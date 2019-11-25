#!/bin/bash
set -e

pip3 install -r requirements.txt

python3 -c 'import nltk; nltk.download("punkt"); nltk.download("stopwords")'

mkdir -p logs
