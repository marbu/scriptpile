#!/usr/bin/env python3
# -*- coding: utf8 -*-


import argparse
import hashlib
import json
import logging
import os.path
import subprocess
import sys
import urllib.request


# based on info from https://signal.org/android/apk/
LATEST_JSON_URL = "https://updates.signal.org/android/latest.json"
SIGNAL_CERT_DIGEST = (
    '29:F3:4E:5F:27:F2:11:B4:24:BC:5B:F9:D6:71:62:C0:'
    'EA:FB:A2:DA:35:AF:35:C1:64:16:FC:44:62:76:BA:26')


logger = logging.getLogger()


def set_logger(verbose_level):
    if verbose_level > 0:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    if verbose_level > 1:
        logger.setLevel(logging.DEBUG)


def get_latest_dict(latest_json_url):
    logger.info("fetching %s", latest_json_url)
    try:
        with urllib.request.urlopen(latest_json_url) as res:
            latest = json.loads(res.read())
            logger.debug("http headers:\n%s", res.info())
    except Exception as ex:
        logger.error(f"Failed to get '{latest_json_url}': %s", ex)
        return None
    return latest


def get_cert_fingerprint(apk_filename):
    """
    Check SHA256 fingerprint of APK signing certificate.
    See also: https://security.stackexchange.com/questions/178936/
    """
    keytool_cmd = ['keytool', '-printcert', '-jarfile', apk_filename]
    proc = subprocess.run(keytool_cmd, capture_output=True, check=True)
    stderr = proc.stderr.decode('utf-8').strip()
    stdout = proc.stdout.decode('utf-8')
    logger.warning("stderr from keytool:\n%s", stderr)
    checksums = []
    for line in stdout.splitlines():
        if line.startswith('\t SHA256: '):
            checksums.append(line[10:])
    logger.debug("checksums identified: %s", checksums)
    if len(checksums) != 1:
        logger.error("SHA256 fingerprint of apk cert can't be identified")
        logger.debug(stdout)
        return None
    return checksums[0]


def main():
    ap = argparse.ArgumentParser(description="Fetch latest signal apk file.")
    ap.add_argument(
        "-v",
        dest="verbose_level",
        action="count",
        default=0,
        help="increase output verbosity")
    ap.add_argument(
        "-s",
        dest="skip_cert_check",
        action="store_true",
        help="skip cert validation via keytool")
    args = ap.parse_args()

    set_logger(args.verbose_level)

    latest = get_latest_dict(LATEST_JSON_URL)
    if latest is None:
        return 1

    apk_filename = os.path.basename(latest['url'])
    checksum_filename = apk_filename + ".sha256"

    if not os.path.exists(apk_filename):
        apk_url = latest['url']
        try:
            logger.info("fetching %s", apk_url)
            _, headers = urllib.request.urlretrieve(apk_url, apk_filename)
            logger.debug("http headers:\n%s", headers)
        except Exception as ex:
            logger.error(f"Failed to get '{apk_url}': %s", ex)
            return 1
        with open(checksum_filename, "w") as checksum_file:
            checksum_file.write(latest['sha256sum'] + "  " + apk_filename)

    checksum_fail = False
    with open(apk_filename, "rb") as apk_file:
        logger.info("computing sha256 digest for %s", apk_filename)
        digest = hashlib.sha256(apk_file.read()).hexdigest()
        if digest == latest['sha256sum']:
            print(f"{apk_filename}: OK")
        else:
            print(f"{apk_filename}: FAILED")
            checksum_fail = True
    with open(checksum_filename, "r") as checksum_file:
        logger.info("comparing sha256 digest with checksum file")
        stored_digest, _ = checksum_file.readline().split("  ")
        if digest == stored_digest:
            logger.info("sha256 digest matches checksum file")
        else:
            logger.error("sha256 digest doesn't match with checksum file")
            print(digest + " from latest.json", file=sys.stderr)
            print(stored_digest + " from the checksum file", file=sys.stderr)
            checksum_fail = True
    if checksum_fail:
        return 1

    if args.skip_cert_check:
        return 0

    cert_digest = get_cert_fingerprint(apk_filename)
    if cert_digest == SIGNAL_CERT_DIGEST:
        logger.info("apk certificate fingerprint looks ok")
    else:
        logger.error("apk certificate fingerprint doesn't match")
        return 1


if __name__ == '__main__':
    sys.exit(main())
