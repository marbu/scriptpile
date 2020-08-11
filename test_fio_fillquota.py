#!/usr/bin/env python3
# -*- coding: utf8 -*-


import os.path
import subprocess
import textwrap

import pytest


FS_SIZE = 100*2**20
QUOTA_SIZE = 80*2**20


@pytest.fixture(
    params=["/usr/bin", os.path.expanduser("~/projects/fio")],
    ids=['system', 'local'])
def fio_build(request):
    return os.path.join(request.param, "fio")


@pytest.fixture(params=[True, False], ids=["quota", ""])
def quota(request):
    """Returns true if quota is (expected to be) enabled."""
    return request.param


@pytest.fixture(params=["xfs", "btrfs"])
def fio_directory(request, quota):
    """Rerenrence to test directory on given fs prepared in advance."""
    mountpoint = f"/mnt/test_{request.param}"
    if quota:
        mountpoint += "_quota"
    assert os.path.ismount(mountpoint)
    target_dir = os.path.join(mountpoint, "target")
    assert os.path.isdir(target_dir)
    yield target_dir
    # make sure files created during test are deleted
    for f in os.listdir(target_dir):
        os.remove(os.path.join(target_dir, f))


@pytest.fixture
def fio_config(fio_directory):
    """Fio config with a minimal write job, using given directory."""
    conf = textwrap.dedent(f"""
        [write]
        readwrite=write
        ioengine=libaio
        directory={fio_directory}
        nrfiles=4
        """)
    return conf


@pytest.mark.parametrize("fill_fs", [True, False], ids=['fill_fs', ''])
@pytest.mark.parametrize("fill_quota", [True, False], ids=['fill_quota', ''])
def test_fio_write(tmpdir, fio_build, fio_config, fio_directory, fill_fs, fill_quota, quota):
    if fill_fs:
        fio_config += "fill_fs=1\n"
    if fill_quota:
        fio_config += "fill_quota=1\n"
    if not fill_fs and not fill_quota:
        pytest.skip("out of scope")

    # create fio config file in test temp. directory
    fio_config_file = tmpdir.join("write.fio")
    fio_config_file.write(fio_config)

    # run the fio job
    cp = subprocess.run([fio_build, "-f", fio_config_file], capture_output=True)

    # write fio report to temporary files in pytest tmp dir
    fio_stdout = tmpdir.join("fio.stdout")
    fio_stdout.write(cp.stdout.decode('utf8'))
    fio_stderr = tmpdir.join("fio.stderr")
    fio_stderr.write(cp.stderr.decode('utf8'))

    # skip (as expected failure) cases when stable build uses the new feature
    if fio_build.startswith("/usr") and fill_quota:
        assert cp.returncode != 0
        pytest.xfail("expected, system build lacks fill_quota feature")

    # expectations
    if quota:
        assert "Disk quota exceeded" in cp.stderr.decode('utf8')
    else:
        assert "No space left on device" in cp.stderr.decode('utf8')
    if not fill_quota and quota:
        # if fill_quota option is not used when space is constrained by quota,
        # fio run is expected to fail
        assert cp.returncode == 1
    elif fill_quota and not fill_fs and not quota:
        # if sheer fill_quota option is used when quota is not enabled, fio
        # will run out of free space and fail (which is expected)
        assert cp.returncode == 1
    else:
        assert cp.returncode == 0

    # check that fio wrote expected amount of data
    space_used = 0
    for f in os.listdir(fio_directory):
        file_path = os.path.join(fio_directory, f)
        if not os.path.isfile(file_path):
            continue
        space_used += os.path.getsize(file_path)
    if quota:
        expected_min = QUOTA_SIZE*0.90
        expected_max = QUOTA_SIZE
    else:
        expected_min = FS_SIZE*0.85
        expected_max = FS_SIZE
    assert expected_min <= space_used <= expected_max
