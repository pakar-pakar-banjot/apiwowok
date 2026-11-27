#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CQL_FILE="${SCRIPT_DIR}/../docker/init-dev-keyspace.cql"
CASSANDRA_CONTAINER="${CASSANDRA_CONTAINER:-nusafire-cassandra-dev}"

"${SCRIPT_DIR}/wait-for-cassandra.sh"

echo "Applying dev keyspace from ${CQL_FILE}..."
docker exec -i "${CASSANDRA_CONTAINER}" cqlsh < "${CQL_FILE}"

echo "Current keyspaces:"
docker exec "${CASSANDRA_CONTAINER}" cqlsh -e "describe keyspaces"
