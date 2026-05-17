#!/bin/bash
# Produces valid JSON health status for all bots.
# Requires: jq, pm2

bots=(clawdbot chu-coder chu-scout chu-ops chu-memory)

# Cache pm2 process list once to avoid TOCTOU inconsistency.
pm2_data=$(pm2 jlist 2>/dev/null)

bots_json="{}"
for bot in "${bots[@]}"; do
  status=$(echo "$pm2_data" | jq -r --arg name "$bot" \
    '.[] | select(.name == $name) | .pm2_env.status' 2>/dev/null)
  # Fallback to "unknown" if pm2 has no entry for this bot.
  [ -z "$status" ] && status="unknown"
  bots_json=$(echo "$bots_json" | jq --arg k "$bot" --arg v "$status" '. + {($k): $v}')
done

disk=$(df -h / | awk 'NR==2 {print $5}')
memory=$(free -m | awk 'NR==2 {printf "%.1f%%", $3*100/$2}')

jq -n \
  --arg ts "$(date -Iseconds)" \
  --argjson bots "$bots_json" \
  --arg disk "$disk" \
  --arg memory "$memory" \
  '{timestamp: $ts, bots: $bots, disk: $disk, memory: $memory}'
