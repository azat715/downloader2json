#!/bin/bash
#
# bakup-gitea.sh
# Copyright (C) 2020 archman <azat715@gmail.com>
#
# Distributed under terms of the MIT license.
#

# some helpers and error handling:
info() { printf "\n%s %s\n\n" "$( date )" "$*" >&2; }

cleanup() {
	echo "$(date +%d-%m-%y-%T) Error >&2; exit 2"
}

trap cleanup INT TERM

info "Starting run"

for i in {1..2}
do 
  docker volume create --name=test_albums
  start=`date +%s.%N`
  docker run --rm -v test_albums:/code downloader2json async_1
  end=`date +%s.%N`
  if [ $? -eq 0 ]
  then
    echo "$i закончилась загрузка"
  else
    echo "ошибка" >&2
    docker volume rm test_albums
    exit 1
  fi
  docker volume rm test_albums
  runtime=$( echo "$end - $start" | bc -l )
  echo "time $runtime"
done 

