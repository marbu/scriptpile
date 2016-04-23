#!/bin/bash
# quick ffmpeg based conversion script for me to be able play audio files on my
# old and  crappy nokia phone which doesn't support ogg vorbis

show_help()
{
  echo -e "Usage: $(basename $0) <command> [command-options]\n"
  echo "Create mp3 nokia version of audio files in given directory"
}

bulk_run()
{
  source_dir=$1
  cpu_num=$(grep '^processor' /proc/cpuinfo | wc -l)
  # create output directory
  ${DEBUG} mkdir -p "${source_dir}/nokia"
  # go into target directory (audio files are expected to be located there)
  cd "${source_dir}"
  [[ ${DEBUG} = echo ]] && echo cd "${source_dir}"
  # run ffmpeg on all files in parallel to utilize all cpu cores
  find . -maxdepth 1 -mindepth 1 -type f -print0 \
  | xargs --null --max-procs=${cpu_num} --max-args=1 -I '{}' \
  ${DEBUG:+/usr/bin/echo} ffmpeg -i '{}' nokia/'{}'.mp3
}

#
# main
#

if [[ $# = 0 ]]; then
  show_help
  exit
fi

# debug mode
if [[ $1 = "-d" ]]; then
  DEBUG=echo
  shift
fi

case $1 in
  -h|help) show_help;;
  *)       bulk_run $1;;
esac
