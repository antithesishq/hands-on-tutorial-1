#!/usr/bin/env bash

# Start the echo server

set -e          # Exit in case of error
set -o pipefail # Exit if piped command returns non-zero

# Uncomment to make the server verbose
# VERBOSE='--verbose'

if ! test "${BIND_ADDRESS}"; then
  echo "BIND_ADDRESS not set"
fi

if ! test "${BIND_PORT_NUMBER}"; then
  echo "BIND_PORT_NUMBER not set"
fi

echo "Loading virtual environment..."
. .venv/bin/activate

echo "Starting server"
echo "Bind address: ${BIND_ADDRESS}:${BIND_PORT_NUMBER}"

# Invoke this function on exit
function exit_trap() {
  echo "Server exited with code ${?}"
}
trap exit_trap EXIT

python3 -u -m src.server --host ${BIND_ADDRESS} --port ${BIND_PORT_NUMBER} ${VERBOSE}
