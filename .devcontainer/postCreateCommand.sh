#! /usr/bin/env bash

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Dependencies
uv sync

# Initialize git repo if not already one (needed for pre-commit)
if [ ! -d ".git" ]; then
    git init
fi

# Install pre-commit hooks
uv run pre-commit install --install-hooks
