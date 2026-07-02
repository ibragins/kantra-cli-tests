#!/bin/bash
export HUB_TOKEN=$(curl -sSf -k --resolve "tackle.local:8443:127.0.0.1" \
  -u admin:admin \
  -X POST "https://tackle.local:8443/hub/auth/tokens" \
  -H 'Content-Type:application/x-yaml' \
  -H 'Accept:application/x-yaml' \
  -d 'lifespan: 168' \
  | awk '/^token:/{print $2}')
echo $HUB_TOKEN
