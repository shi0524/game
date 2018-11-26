#!/bin/bash

# default root dir

_ROOT_PATH='/Users/kaiqigu/my_notebook/game'

CUR_PATH=$(cd "$(dirname "$0")"; pwd)

env=$1

ipython -i $CUR_PATH/shell.py $env $CUR_PATH
