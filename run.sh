#!/bin/bash
script_dir=$(dirname $0)
cd $script_dir
nohup python -u ./main.py &> log.txt &