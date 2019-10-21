#!/bin/bash
# tmux wrapper with systemd integration, see:
# - https://github.com/tmux/tmux/issues/428
# - https://unix.stackexchange.com/questions/490267
exec systemd-run --scope --user /usr/bin/tmux "$@"
