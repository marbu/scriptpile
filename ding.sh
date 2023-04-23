#!/bin/bash
# Run a given command and play a sound based on it's exit code.
# By martinb@marbu.eu
# Based on Jonathan Palardy's ding script from:
# https://github.com/jpalardy/dotfiles/blob/53a26cbb54dd7eb1de599a8e6ba931649452a468/bin/ding
# As presented in the following blog post from Oct 2022:
# https://blog.jpalardy.com/posts/ding/

# Play a short sound based on given exit code.
# See also https://tldp.org/LDP/abs/html/exitcodes.html
play_sound()
{
  if ! type play >/dev/null; then
    echo "$(basename $0): can't play sound" >&2
	return
  fi
  case $1 in
    0)   play -q /usr/share/sounds/Oxygen-Sys-App-Positive.ogg;;
	127) play -q /usr/share/sounds/Oxygen-Sys-File-Open-Foes.ogg;;
    *)   play -q /usr/share/sounds/Oxygen-Sys-App-Error-Serious-Very.ogg;;
  esac
}

wrap_command()
{
  "$@"
  exit_code=$?
  play_sound $exit_code &
  exit $exit_code
}

show_help()
{
  echo -e "Run a given command and play a sound based on it's exit code.\n"
  echo -e "Usage: $(basename "$0") COMMAND\n"
  echo """Options:
  --good    play good sound and exit without running any command
  --fail    play fail sound and exit without running any command
  --help    this message"""
}

#
# main
#

if [[ $# = 0 ]]; then
  play_sound 0 &
  exit
fi

case $1 in
  --good)          play_sound 0;;
  --fail)          play_sound 1;;
  [0-9]*)          play_sound $1;;
  -h|--help|help)  show_help;;
  *)               wrap_command $@;
esac
