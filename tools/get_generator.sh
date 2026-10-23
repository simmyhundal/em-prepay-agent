#!/bin/sh
# Fetch the postpay repository (data generators) at the commit in GENERATOR_PIN into external/em-upcoding-agent.
set -e
cd "$(dirname "$0")/.."
PIN=$(cat GENERATOR_PIN)
if [ ! -d external/em-upcoding-agent/.git ]; then
  mkdir -p external
  git clone -q https://github.com/simmyhundal/em-upcoding-agent.git external/em-upcoding-agent
fi
git -C external/em-upcoding-agent fetch -q origin
git -C external/em-upcoding-agent checkout -q "$PIN"
echo "generator at $PIN"
echo "build D4.2: python3 external/em-upcoding-agent/src/generate_v2.py data/OUT --seed N --data-version 4.2 --answer-key eval/answer_key/NAME.json"
