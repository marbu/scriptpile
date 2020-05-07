#!/usr/bin/env python3
# -*- coding: utf8 -*-


import argparse
import hashlib
import json
import logging
import os.path
import sys
import urllib.request


LATEST_JSON_URL = "https://updates.signal.org/android/latest.json"


def main():
    ap = argparse.ArgumentParser(description="Fetch latest signal apk file.")
    ap.add_argument(
        "-v",
        dest="verbose",
        action="count",
        default=0,
        help="increase output verbosity")
    args = ap.parse_args()

    logger = logging.getLogger()
    if args.verbose > 0:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    if args.verbose > 1:
        logger.setLevel(logging.DEBUG)

    try:
        logger.info("fetching %s", LATEST_JSON_URL)
        with urllib.request.urlopen(LATEST_JSON_URL) as res:
            latest = json.loads(res.read())
            logger.debug("http headers:\n%s", res.info())
    except Exception as ex:
        logger.error(f"Failed to get '{LATEST_JSON_URL}': %s", ex)
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


if __name__ == '__main__':
    sys.exit(main())
