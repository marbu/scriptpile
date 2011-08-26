#!/bin/bash

ORIGIN=$(pwd)
cd $HOME/local/bin

for i; do
  TARGET="${i%.sh}"
  if [[ ! -h $TARGET ]]; then
    ln -s "${ORIGIN}/${i}" $TARGET
  fi
done
