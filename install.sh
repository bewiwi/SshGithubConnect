#!/bin/bash

BinFile=/usr/bin/sshgithub
ConfFile=/etc/sshgit.ini

if [ "$(id -u)" != "0" ]; then
    echo "This script must be run as root" 1>&2
    exit 1
fi

cd $(dirname $0)

cp sshgithub.py $BinFile
chown root:root $BinFile
chmod 500 $BinFile

[ -e $ConfFile ] || cp sshgit.ini $ConfFile
chown root:root $ConfFile
chmod 600 $ConfFile