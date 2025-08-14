#!/usr/bin/env bash

# Monitor the server and print statistics.
# Also alert if server health-checks are failing for too long.

set -e          # Exit in case of error
set -o pipefail # Exit if piped command returns non-zero

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
# How often to poll and print server stats
STATS_INTERVAL=${STATS_INTERVAL:-5}
# How often to poll server health
HEALTH_INTERVAL=${HEALTH_INTERVAL:-1}
# After how long without a successfull health-check to raise an alert
# N.B. set this higher than pause-fault MAX_ON to avoid false positives
HEALTH_ALERT_INTERVAL=${HEALTH_ALERT_INTERVAL:-30}

echo "Loading virtual environment..."
. .venv/bin/activate

echo "Starting monitor"
echo "Target: ${SERVER_ADDRESS}:${SERVER_PORT_NUMBER}"
echo "Stats: ${STATS_INTERVAL}s, Health: ${HEALTH_INTERVAL}s, Alert: ${HEALTH_ALERT_INTERVAL}s"

python3 -u -m src.monitor \
  --host ${SERVER_ADDRESS} \
  --port ${SERVER_PORT_NUMBER} \
  --stats-interval ${STATS_INTERVAL} \
  --health-interval ${HEALTH_INTERVAL} \
  --alert-interval ${HEALTH_ALERT_INTERVAL} \
  ;
