#!/bin/bash
# This script is sourced by the custom terminal profile

# Get the workspace folder. In Codespaces, it's usually /workspaces/<repo-name>
# The devcontainer.json uses ${localWorkspaceFolderBasename} which resolves to the repo name.
# So, we assume the .venv is at /workspaces/<repo-name>/.venv
WORKSPACE_ROOT="/workspaces/$(basename $PWD)" # Or more reliably if $PWD is correct
if [ -z "${CODESPACE_NAME}" ]; then # Local dev container
    WORKSPACE_ROOT="/workspaces/$(basename "${localWorkspaceFolder}")"
else # GitHub Codespaces
    WORKSPACE_ROOT="/workspaces/${CODESPACE_NAME}"
fi


VENV_ACTIVATE_SCRIPT="${WORKSPACE_ROOT}/.venv/bin/activate"

if [ -f "$VENV_ACTIVATE_SCRIPT" ]; then
    echo "Activating virtual environment: $VENV_ACTIVATE_SCRIPT"
    source "$VENV_ACTIVATE_SCRIPT"
else
    echo "Warning: Virtual environment activation script not found at $VENV_ACTIVATE_SCRIPT"
fi
