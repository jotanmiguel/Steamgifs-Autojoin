#!/bin/bash
# wait-for-fsr.sh
set -e

echo "Waiting for FlareSolverr..."
until curl -s http://flaresolverr:8191/v1 > /dev/null; do
    echo "FlareSolverr not ready, retrying in 2s..."
    sleep 2
done

echo "FlareSolverr is up!"
exec "$@"