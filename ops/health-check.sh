#!/bin/bash
# Build status JSON safely using jq to avoid bash interpolation and trailing-comma bugs.

bots=("clawdbot" "chu-coder" "chu-scout" "chu-ops" "chu-memory")

bot_json='{}'
for bot in "${bots[@]}"; do
  status=$(pm2 jlist 2>/dev/null | jq -r --arg name "$bot" '.[] | select(.name==$name) | .pm2_env.status' 2>/dev/null || echo "unknown")
  bot_json=$(echo "$bot_json" | jq --arg k "$bot" --arg v "$status" '. + {($k): $v}')
done

jq -n \
  --arg ts "$(date -Iseconds)" \
  --arg disk "$(df -h / | awk 'NR==2 {print $5}')" \
  --arg mem "$(free -m | awk 'NR==2 {printf "%.1f%%", $3*100/$2}')" \
  --argjson bots "$bot_json" \
  '{"timestamp": $ts, "bots": $bots, "disk": $disk, "memory": $mem}'
