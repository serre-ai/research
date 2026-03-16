#!/bin/bash
set -e
cd "$(dirname "$0")"
tectonic main.tex
echo "Built: $(date)"
echo "Output: $(pwd)/main.pdf"
