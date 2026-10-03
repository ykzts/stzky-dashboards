FROM mcr.microsoft.com/devcontainers/base:2.1.10-trixie@sha256:b60cd6e70901c42c23dc312b8e0cf2c704cad3acf65c55739ff1ef33a30166d2

# python3 runs .github/scripts/check-dashboards.py
RUN apt-get update && apt-get install -y --no-install-recommends python3 && rm -rf /var/lib/apt/lists/*

# Pre-create the Claude Code and GitHub CLI config directories so the mounted volumes are owned by vscode
RUN install -d -o vscode -g vscode /home/vscode/.claude /home/vscode/.config/gh \
  && chown -R vscode:vscode /home/vscode/.config
