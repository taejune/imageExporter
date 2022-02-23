#!/bin/sh

if [ ! -d $1 ]
then
  echo "$1 not exist or not directory"
  exit 1
fi

if [ ! -d $2 ]
then
  echo "$1 not exist or not directory"
  exit 1
fi

NOW=$(date "+%Y%m%d-%H%M")

tar -zcf $NOW.tar.gz $1
mv $NOW.tar.gz $2
