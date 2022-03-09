#!/bin/sh
set -e

if [ ! -d $1 ]
then
  echo "$1 not exist or not directory"
  exit 1
fi

NOW=$(date "+%Y%m%d-%H%M")

tar -zcf $NOW.tar.gz $1
sshpass -p$3 scp -o StrictHostKeyChecking=no $NOW.tar.gz $2
rm -rf $NOW.tar.gz