#!/bin/bash
rpm -qa | xargs rpm -qi | awk -f rpm-license-filter.awk -v license_id=GPLv2
