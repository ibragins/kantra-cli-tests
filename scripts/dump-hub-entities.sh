#!/bin/bash
# Dump hub entities (targets, analysis profiles, applications, archetypes)
# as JSON so you can copy the output and use it to update create-entities.sh.
#
# Usage: ./dump-hub-entities.sh [OPTIONS] [> hub-entities-dump.json]
#   --exclude TYPE[,TYPE...]   Omit entity types from output (e.g. --exclude targets)
#   Types: targets, analysisProfiles, applications, archetypes
#
#   HUB_BASE_URL=localhost:8080/hub ./dump-hub-entities.sh
set -e

EXCLUDE=""
while [ $# -gt 0 ]; do
    case "$1" in
        --exclude|-x)
            shift
            if [ $# -eq 0 ] || [[ "$1" == -* ]]; then
                echo "Missing value for --exclude (expected comma-separated types)" >&2
                exit 1
            fi
            EXCLUDE="$1"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo "  --exclude, -x TYPE[,TYPE...]  Omit from output: targets, analysisProfiles, applications, archetypes"
            echo "  --help, -h                    Show this help"
            echo "Example: $0 --exclude targets"
            exit 0
            ;;
        *)
            echo "Unknown option: $1 (use --help)" >&2
            exit 1
            ;;
    esac
done

HUB_URL="${HUB_BASE_URL:-localhost:8080}"
if [[ "$HUB_URL" != http* ]]; then
    BASE_URL="http://${HUB_URL}"
else
    BASE_URL="${HUB_URL}"
fi

CURL_OPTS=(--silent --show-error --max-time 15)

# Fetch one endpoint and normalize to JSON array
fetch_json() {
    curl "${CURL_OPTS[@]}" "$1" 2>/dev/null | jq -c 'if type == "array" then . else [] end' 2>/dev/null || echo "[]"
}

# Try root first
echo "Fetching entities from $BASE_URL ..." >&2
TARGETS=$(fetch_json "${BASE_URL}/targets")
PROFILES=$(fetch_json "${BASE_URL}/analysis/profiles")
APPLICATIONS=$(fetch_json "${BASE_URL}/applications")
ARCHETYPES=$(fetch_json "${BASE_URL}/archetypes")

# If all empty and we haven't tried /hub yet, retry with /hub (API often under /hub)
if [[ "$BASE_URL" != */hub ]] && \
   [ "$(echo "$TARGETS" | jq 'length')" -eq 0 ] && \
   [ "$(echo "$PROFILES" | jq 'length')" -eq 0 ] && \
   [ "$(echo "$APPLICATIONS" | jq 'length')" -eq 0 ]; then
   [ "$(echo "$ARCHETYPES" | jq 'length')" -eq 0 ] && \
    echo "Root returned no data, trying ${BASE_URL}/hub ..." >&2
    BASE_URL="${BASE_URL}/hub"
    TARGETS=$(fetch_json "${BASE_URL}/targets")
    PROFILES=$(fetch_json "${BASE_URL}/analysis/profiles")
    APPLICATIONS=$(fetch_json "${BASE_URL}/applications")
    ARCHETYPES=$(fetch_json "${BASE_URL}/archetypes")
fi

# Build output object and optionally remove excluded keys
OUTPUT=$(jq -n \
    --argjson targets "$TARGETS" \
    --argjson analysisProfiles "$PROFILES" \
    --argjson applications "$APPLICATIONS" \
    --argjson archetypes "$ARCHETYPES" \
    '{
      targets: $targets,
      analysisProfiles: $analysisProfiles,
      applications: $applications,
      archetypes: $archetypes
    }')

if [ -n "$EXCLUDE" ]; then
    # e.g. EXCLUDE=targets or targets,applications -> del(.targets) or del(.targets, .applications)
    DEL_ARGS=""
    for t in $(echo "$EXCLUDE" | tr ',' ' '); do
        t=$(echo "$t" | tr -d ' ')
        [ -z "$t" ] && continue
        DEL_ARGS="${DEL_ARGS} .${t},"
    done
    DEL_ARGS="${DEL_ARGS%,}"
    if [ -n "$DEL_ARGS" ]; then
        OUTPUT=$(echo "$OUTPUT" | jq "del(${DEL_ARGS})")
    fi
fi

echo "$OUTPUT" | jq '.'
