#!/usr/bin/env bash

cd python

python3 -m venv env
source env/bin/activate

pip install --upgrade pip
pip install -r requirements.txt