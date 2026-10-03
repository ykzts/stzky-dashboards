#!/bin/bash

set -euo pipefail

# Download the whole installer before running it, so a truncated download is
# never partially executed.
installer="$(mktemp)"
trap 'rm -f "${installer}"' EXIT
curl -fsSL -o "${installer}" https://claude.ai/install.sh
bash "${installer}"
