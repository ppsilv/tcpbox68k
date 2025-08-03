#!/bin/bash

# Find if one file ever had into repository
    git log --pretty=format: --name-status --all -M -B | sort -u | grep $1
# The same as above but showing copied files
tt=`git log --pretty=format: --name-status --all -C -M -B | sort -u | grep $1`

echo $ff

echo $tt

