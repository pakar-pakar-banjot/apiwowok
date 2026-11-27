#!/usr/bin/env bash
set -euo pipefail

CASSANDRA_CONTAINER="${CASSANDRA_CONTAINER:-nusafire-cassandra-dev}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-180}"
POLL_INTERVAL="${POLL_INTERVAL:-5}"

start_ts=$(date +%s)
deadline=$((start_ts + TIMEOUT_SECONDS))

echo "Waiting for Cassandra container '${CASSANDRA_CONTAINER}' (timeout: ${TIMEOUT_SECONDS}s)..."

while true; do
  if output=$(docker exec "${CASSANDRA_CONTAINER}" cqlsh -e "describe keyspaces" 2>/dev/null); then
    elapsed=$(( $(date +%s) - start_ts ))
    echo "Cassandra is ready in ${elapsed}s."
    echo "${output}"
    exit 0
  fi

  now=$(date +%s)
  if [ "${now}" -ge "${deadline}" ]; then
    echo "ERROR: Cassandra did not become ready within ${TIMEOUT_SECONDS}s." >&2
    exit 1
  fi

  sleep "${POLL_INTERVAL}"
done
