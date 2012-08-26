#!/bin/bash
# by marbu, 2012
# initialize my home directory

init_subdir()
{
  DIRNAME=$1
  BASEDIR=$2
  SIMLINK=$3
  NEWNAME=$(echo $DIRNAME | tr [:upper:] [:lower:] | sed 's/^\.//')
  if [[ -d ~/$DIRNAME ]]; then
    mv ~/$DIRNAME $BASEDIR/$NEWNAME
  else
    mkdir $BASEDIR/$NEWNAME
  fi
  if [[ $SIMLINK ]]; then
    ln -s $BASEDIR/$NEWNAME ~/$DIRNAME
  fi
}

create_skeleton()
{
  cd
  # mostly version controlled
  mkdir ~/projects # foreign/public projects (repos only)
  mkdir ~/packages # foreign/public packages (repos only)
  mkdir ~/tvorba   # my projects
  mkdir ~/school   # school related
  # annexizable
  mkdir ~/data   # mostly work of sb. else (data collections)
  mkdir ~/texty  # all texts (textbooks, articles, ebooks, magazines)
  # and the rest
  mkdir ~/tmp     # temporary files
  mkdir ~/tmp/pub # publicly shareable (because of xdg sth.)
  # local directory (scripts, var files)
  mkdir ~/local           # local directory for my scripts
  mkdir ~/local/var       # temp files of my scripts
  mkdir ~/local/javalib   # place for simlinks (mentioned in bashrc)
  mkdir ~/local/pylib     # place for weird python modules
  init_subdir bin     ~/local ln # classic user bin directory
  init_subdir texmf   ~/local ln # texlive files
  init_subdir .cabal  ~/local ln # haskell's cabal
  init_subdir Desktop ~/local    # classic desktop dir
  init_subdir Documents ~/tvorba # classic desktop dir
  # change xdg dir configuration (don't care about others)
  CONF_FILE=$HOME/.config/user-dirs.dirs
  sed -i 's!^\(XDG_DESKTOP_DIR\).*!\1="$HOME/local/desktop"!'      $CONF_FILE
  sed -i 's!^\(XDG_DOCUMENTS_DIR\).*!\1="$HOME/tvorba/documents"!' $CONF_FILE
  sed -i 's!^\(XDG_PUBLICSHARE_DIR\).*!\1="$HOME/tmp/pub"!'        $CONF_FILE
  # remove empty predefined directories
  for DIR in $(ls ~ | grep ^[[:upper:]] | grep -v ^Downloads); do
    rmdir $DIR || echo "error, not empty: $DIR" >&2
  done
}

setup_ssh_keys()
{
  echo "ssh setup"
  cd
  mkdir .ssh
  chmod 0700 .ssh
  restorecon -f .ssh
  cd .ssh
  echo "key for: default rsa key"
  ssh-keygen -f id_kari_rsa
  # id_kari_{github,skoll,fi ...} doesn't make sense
}

checkout_projects()
{
  # projects of others
  cd ~/projects
  git clone https://github.com/vogo/vok.git
  # my projects (rw requires key setup)
  cd ~/tvorba
}

#
# main
#

if [[ $# = 0 ]]; then
  echo "homedir init script, run with --force"
  exit
fi

create_skeleton
setup_ssh_keys
checkout_projects
