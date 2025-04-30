#!/bin/bash
# Entrypoint script for dev container

# Source the Python environment if using a venv (customize if needed)
if [ -f "/workspaces/raga/.venv/bin/activate" ]; then
    source /workspaces/raga/.venv/bin/activate
fi

# Ensure uv and pytest are available
which uv || export PATH="$HOME/.local/bin:$PATH"
which pytest || echo "pytest not found in PATH"

exec "$@"
