#!/usr/bin/bash
# git installation on centos
installed=$(which git)

usage(){
  printf '%s %s\n' 'Usage: $0'
  exit 1
}

installation(){
  yum install git -y && \
  useradd -r -m -U -d /home/git -s /bin/bash git && \
  sudo su - git && \
  mkdir -p ~/.ssh && chmod 0700 ~/.ssh && \
  touch ~/.ssh/authorized_keys && chmod 0600 ~/.ssh/authorized_keys
}

if [[ $EUID -ne 0 ]]; then
  usage
fi

if [[ -x "$(command -v git)" ]]; then
  echo "Git has already been installed!"
  exit 1
fi

main(){
  installation
}

main "$@"

