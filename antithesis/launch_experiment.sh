#!/usr/bin/env bash

# Exit on error
set -e
# Exit on reference to undefined variable
set -u

WEBHOOK_ENDPOINT=basic_test

# This script triggers a single experiment by invoking the webhook endpoint.
# See: https://antithesis.com/docs/getting_started/webhook.html
#
# This script takes 4 arguments:
#  1. Duration (exploration minutes)
#  2. Configuration image:tag
#  3. Experiment description (empty string is ok)
#  4. Email recipients (empty string is ok)

################################################################################

REQUIRED="
    jq
    curl
"

################################################################################

# Ensure required commands are available
for cmd in ${REQUIRED}; do
    if ! command -v "${cmd}" >/dev/null 2>&1; then
        echo "Missing required command: ${cmd}"
        exit 1
    fi
done

# Ensure token is set in environment
if [ -z "$WEBHOOK_CREDENTIALS" ]; then
    echo "Environment variable WEBHOOK_CREDENTIALS is not set."
    exit 1
fi

# Ensure tenant domain is set in environment
if [ -z "$TENANT_DOMAIN" ]; then
    echo "Environment variable TENANT_DOMAIN is not set."
    exit 1
fi
webhook_url="https://${TENANT_DOMAIN}.antithesis.com/api/v1/launch_experiment/${WEBHOOK_ENDPOINT}"

# Ensure the right number of arguments
if [ "$#" -ne 4 ]; then
    echo "Expecting 4 arguments, got $#: ${*}"
    exit 1
fi

# Put arguments into variables for readability
duration="${1}"
config_image="${2}"
experiment_description="${3}"
report_recipients="${4}"

if [ "${experiment_description}" == "" ]; then
    experiment_description="Run by ${GITHUB_ACTOR:-$USER} on `date` (${duration}m)"
fi

# Ephemeral marks the run as a one-off, not to be used for future comparisons
# All runs should be marked epemeral except for the ones that always run against
# the same branch (e.g. `main`) for which we want to track changes over time.
ephemeral="${EPHEMERAL:-true}"
# Track which other runs to compare against
lineage="tutorial-1-${GITHUB_ACTOR:-$USER}"

echo "Triggering ${duration} minutes experiment using image: '${config_image}'"

################################################################################

# VCS Info: https://docs.github.com/en/actions/reference/workflows-and-actions/variables
branch="${GITHUB_REF_NAME:-unknown}"
user="${GITHUB_ACTOR:-unknown}"
org="${GITHUB_REPOSITORY_OWNER:-unknown}"
repo="${GITHUB_REPOSITORY:-unknown}"
sha="${GITHUB_SHA:-unknown}"
link="${GITHUB_SERVER_URL:-unknown}/${repo}/commit/${sha}"
caller=${GITHUB_WORKFLOW_REF:-unknown}

# Don't ignore mid-pipeline errors
set -o pipefail

# Invoke endpoint
jq -n \
    --arg duration "${duration}" \
    --arg cfg "${config_image}" \
    --arg description "${experiment_description}" \
    --arg recipients "${report_recipients}" \
    --arg ephemeral "${ephemeral}" \
    --arg lineage "${lineage}" \
    '{
      params: {
        "antithesis.duration": $duration,
        "antithesis.config_image": $cfg,
        "antithesis.description": $description,
        "antithesis.is_ephemeral": $ephemeral,
        "antithesis.source": $lineage,
        "run.caller_type": "github_action",
        "run.creator_name": "'${user}'",
        "vcs.repo_name": "'${repo}'",
        "vcs.repo_owner": "'${org}'",
        "vcs.repo_branch": "'${branch}'",
        "vcs.version_id": "'${sha}'",
        "vcs.version_link": "'${link}'",
        "vcs.caller_name": "'${caller}'",
        "antithesis.report.recipients": $recipients
      }
    }' \
| tee /dev/fd/2 \
| curl \
    --fail \
    --silent \
    --show-error \
    -u "${WEBHOOK_CREDENTIALS}" \
    -X POST \
    --data @- \
    -H "content-type: application/json" \
    "${webhook_url}"

if [ $? -ne 0 ]; then
    echo "Error launching experiment"
    exit 1
fi
