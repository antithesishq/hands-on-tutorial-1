#!/usr/bin/env bash

# Start the workload

set -e          # Exit in case of error
set -o pipefail # Exit if piped command returns non-zero

# Uncomment to make the workload verbose
# VERBOSE='--verbose'

if ! test "${SERVER_ADDRESS}"; then
  echo "SERVER_ADDRESS not set"
  exit 1
fi

if ! test "${SERVER_PORT_NUMBER}"; then
  echo "SERVER_PORT_NUMBER not set"
  exit 1
fi

#
# These default/fallback values can be altered via
# `environment` in docker-compose.yaml
#
# After how long without a successfull request to raise an alert
# N.B. set this higher than pause-fault MAX_ON to avoid false positives
ALERT_INTERVAL=${ALERT_INTERVAL:-30}

echo "Loading virtual environment..."
. .venv/bin/activate

echo "Starting workload"
echo "Target: ${SERVER_ADDRESS}:${SERVER_PORT_NUMBER}"
echo "Alert: ${ALERT_INTERVAL}s"

# Invoke this function on exit
function exit_trap() {
  echo "Workload exited with code ${?}"
}
trap exit_trap EXIT

python3 -u -m src.workload --host ${SERVER_ADDRESS} --port ${SERVER_PORT_NUMBER} --alert-interval ${ALERT_INTERVAL} ${VERBOSE}
