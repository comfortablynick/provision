#!/usr/bin/env sh
# Install python package

pip3 install --upgrade pip
pip3 install -r requirements.txt
pip3 install -e .
