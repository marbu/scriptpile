#!/bin/bash
rpm -qa | xargs rpm -qi | awk -f rpm-license-filter.awk
