#!/bin/bash
# quick (read as "quickly hacked together") ffmpeg based conversion script for
# me to be able play audio files on my old and  crappy nokia phone which
# doesn't support ogg vorbis

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

# this works in few special cases only
guess_metadata()
{
  mp3_dir=$1/nokia
  expected_artist=$2
  cd "${mp3_dir}"
  for file in *.mp3; do
    if [[ "$file" =~ ^([^-]*)\ ?-\ ?([^-\(]*)\ ?-.*\.mp3$ ]]; then
      artist=${BASH_REMATCH[1]}
      song=${BASH_REMATCH[2]}
      # swap fields if needed
      if [[ "${artist}" != "${expected_artist}" ]]; then
        song=${artist}
        artist=${expected_artist}
      fi
      ${DEBUG} id3v2 --artist "${artist}" --song "${song}" "${file}"
    else
      echo "failed to guess metadata for: $file" >&2
      if [[ $expected_artist ]]; then
        ${DEBUG} id3v2 --artist "${expected_artist}" "${file}"
      fi
    fi
  done
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
  id3)     guess_metadata "$2" "$3";;
  mp3)     bulk_run "$2";;
  all)     bulk_run "$2"; guess_metadata "$2" "$3";;
  *)       show_help;;
esac
