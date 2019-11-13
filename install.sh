#!/bin/bash
set -e

pip install -r requirements.txt

python -c 'import nltk; nltk.download("punkt"); nltk.download("stopwords")'

mkdir -p Logs
