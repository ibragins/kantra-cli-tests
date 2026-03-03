#!/bin/bash
# Remove all hub entities: archetypes, applications, analysis profiles.
# Targets are not deleted (built-in or custom).
#
# Usage: ./cleanup-hub-entities.sh
#        HUB_BASE_URL=localhost:8080/hub ./cleanup-hub-entities.sh
set -e

HUB_URL="${HUB_BASE_URL:-localhost:8080}"
if [[ "$HUB_URL" != http* ]]; then
    BASE_URL="http://${HUB_URL}"
else
    BASE_URL="${HUB_URL}"
fi

CURL_OPTS=(--silent --show-error --max-time 15)

# Discover /hub if root returns no data
fetch_json() {
    curl "${CURL_OPTS[@]}" "$1" 2>/dev/null | jq -c 'if type == "array" then . else [] end' 2>/dev/null || echo "[]"
}

echo "============================================"
echo "Cleaning up Hub Entities"
echo "============================================"
echo "Hub URL: $BASE_URL"
echo ""

APPS_JSON=$(fetch_json "${BASE_URL}/applications")
APPS_LEN=$(echo "$APPS_JSON" | jq -r 'length' 2>/dev/null || echo "0")
[ -z "$APPS_LEN" ] || [ "$APPS_LEN" = "null" ] && APPS_LEN="0"
if [ "${APPS_LEN:-0}" -eq 0 ] && [[ "$BASE_URL" != */hub ]]; then
    echo "No data at root, using ${BASE_URL}/hub ..."
    BASE_URL="${BASE_URL}/hub"
fi

# Delete in reverse dependency order: archetypes -> applications -> analysis profiles
echo "----------------------------------------"
echo "1. Deleting Archetypes"
echo "----------------------------------------"
ARCHETYPES_JSON=$(fetch_json "${BASE_URL}/archetypes")
COUNT=0
for id in $(echo "$ARCHETYPES_JSON" | jq -r '.[].id' 2>/dev/null); do
    [ -z "$id" ] || [ "$id" = "null" ] && continue
    if curl "${CURL_OPTS[@]}" -X DELETE "${BASE_URL}/archetypes/${id}" 2>/dev/null; then
        echo "  Deleted archetype ID: $id"
        COUNT=$((COUNT + 1))
    else
        echo "  Failed or already gone: archetype $id" >&2
    fi
done
echo "  Archetypes removed: $COUNT"

echo ""
echo "----------------------------------------"
echo "2. Deleting Applications"
echo "----------------------------------------"
APPS_JSON=$(fetch_json "${BASE_URL}/applications")
COUNT=0
for id in $(echo "$APPS_JSON" | jq -r '.[].id' 2>/dev/null); do
    [ -z "$id" ] || [ "$id" = "null" ] && continue
    if curl "${CURL_OPTS[@]}" -X DELETE "${BASE_URL}/applications/${id}" 2>/dev/null; then
        echo "  Deleted application ID: $id"
        COUNT=$((COUNT + 1))
    else
        echo "  Failed or already gone: application $id" >&2
    fi
done
echo "  Applications removed: $COUNT"

echo ""
echo "----------------------------------------"
echo "3. Deleting Analysis Profiles"
echo "----------------------------------------"
PROFILES_JSON=$(fetch_json "${BASE_URL}/analysis/profiles")
COUNT=0
for id in $(echo "$PROFILES_JSON" | jq -r '.[].id' 2>/dev/null); do
    [ -z "$id" ] || [ "$id" = "null" ] && continue
    if curl "${CURL_OPTS[@]}" -X DELETE "${BASE_URL}/analysis/profiles/${id}" 2>/dev/null; then
        echo "  Deleted analysis profile ID: $id"
        COUNT=$((COUNT + 1))
    else
        echo "  Failed or already gone: profile $id" >&2
    fi
done
echo "  Analysis profiles removed: $COUNT"

echo ""
echo "============================================"
echo "✓ Cleanup finished"
echo "============================================"
