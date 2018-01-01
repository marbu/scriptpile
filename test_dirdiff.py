#!/usr/bin/env python3
# -*- coding: utf8 -*-

import pytest

from dirdiff import dirdiff


@pytest.fixture
def dd_flat1():
    return {
        '1': {'foo': 'b8073268d2b91a20597db9ba777331c989b74690'},
        'a': {'one': '1f4a5722bbcba22eea575fe7a904c8f8980cbbbf'},
        'b/1': {'foo': 'b8073268d2b91a20597db9ba777331c989b74690'},
        }


@pytest.fixture
def dd_flat2():
    return {
        '2': {'foo': 'b8073268d2b91a20597db9ba777331c989b74690'},
        'a': {'one': '000a5722bbcba22eea575fe7a904c8f8980cbbbf'},
        'b/2': {'foo': 'b8073268d2b91a20597db9ba777331c989b74690'},
        }


def test_dirdiff_empty():
    assert list(dirdiff({}, {})) == []


def test_dirdiff_same(dd_flat1):
    "comparing the same directory yields no differences"
    assert list(dirdiff(dd_flat1, dd_flat1)) == []


def test_dirdiff_directories(dd_flat1, dd_flat2):
    "checking that directories present only in 1st or 2nd dir are detected"
    diff_list = list(dirdiff(dd_flat1, dd_flat2))
    assert ('D1', '1') in diff_list
    assert ('D1', 'b/1') in diff_list
    assert ('D2', '2') in diff_list
    assert ('D2', 'b/2') in diff_list
    assert len([x for x in diff_list if x[0].startswith("D")]) == 4
