#!/bin/bash

for pkg in $(pwd)/*.pkg
do
echo "Installation of ${pkg}"
qicli call PackageManager.install ${pkg} users
done
