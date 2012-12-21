#!/bin/bash
xrandr | grep "*" | awk '{print $1}'
