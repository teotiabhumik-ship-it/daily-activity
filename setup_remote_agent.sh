#!/usr/bin/env bash
# ==============================================================================
# Setup script for Auto Issue Solver on Antigravity Remote Agent (Cloud Linux VM)
# ==============================================================================
set -e

echo "=== [1/3] Updating system packages & verifying tools ==="
sudo apt-get update -y
sudo apt-get install -y git curl python3 python3-pip python3-venv

echo "=== [2/3] Installing GitHub CLI (gh) if missing ==="
if ! command -v gh &> /dev/null; then
    type -p curl >/dev/null || (sudo apt update && sudo apt install curl -y)
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && sudo apt update \
    && sudo apt install gh -y
fi

echo "GitHub CLI version: $(gh --version | head -n 1)"

echo "=== [3/3] Setting up Python dependencies & workspaces ==="
mkdir -p repos
pip install --upgrade pip pytest requests

echo "Auto Issue Solver Cloud Environment is ready!"
