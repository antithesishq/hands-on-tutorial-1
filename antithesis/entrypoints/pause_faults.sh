#!/usr/bin/env bash

# Turn faults ON and OFF at random intervals.
# (The intervals will be different in different multiverse branches)

set -e          # Exit in case of error
set -o pipefail # Exit if piped command returns non-zero

# When not running in Antithesis, ANTITHESIS_STOP_FAULTS is not set
# and this script will terminate here.
#
# Set ANTITHESIS_STOP_FAULTS=echo in docker-compose if you want to test this script locally
if [[ "" == "${ANTITHESIS_STOP_FAULTS}" ]]; then
  echo "ANTITHESIS_STOP_FAULTS not set, exiting"
  exit 0
fi

#
# These default/fallback values can be altered via
# `environment` in docker-compose.yaml
#
# How long to pause before going into intermittent mode.
START_DELAY=${START_DELAY:-10}
# Minimum/Maximum amount of time with faults ON
# N.B. Liveness/progress checks should be larger than MAX_ON to avoid false positives!
MIN_ON=${MIN_ON:-20}
MAX_ON=${MAX_ON:-40}
# Minimum/Maximum amount of time with faults OFF
MIN_OFF=${MIN_OFF:-20}
MAX_OFF=${MAX_OFF:-40}

echo "Intermittent faults: ${MIN_ON}-${MAX_ON}s ON, ${MIN_OFF}-${MAX_OFF}s OFF, "

# Initial faults pause.
# N.B This will may ignored.
echo "Initial faults pause: ${START_DELAY}s"
"${ANTITHESIS_STOP_FAULTS}" ${START_DELAY}
sleep ${START_DELAY};


# Turn faults ON/OFF at random intervals (within bounds)
while true; do
  # Re-seed $RANDOM from /dev/urandom
  # To ensure different values over time.
  RANDOM=$(od -An -N2 -tu2 /dev/urandom | tr -d ' ')
  ON_PERIOD=$((MIN_ON + (RANDOM % (MAX_ON - MIN_ON + 1))))
  OFF_PERIOD=$((MIN_OFF + (RANDOM % (MAX_OFF - MIN_OFF + 1))))

  echo "Faults OFF for ${OFF_PERIOD}s"
  "${ANTITHESIS_STOP_FAULTS}" ${OFF_PERIOD}
  sleep ${OFF_PERIOD};

  echo "Faults ON for ${ON_PERIOD}s"
  sleep ${ON_PERIOD};
done
