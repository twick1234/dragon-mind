#!/bin/bash
# health-check.sh — outputs system status as valid JSON
# Security: all dynamic values are sanitized before embedding in JSON output

# Helper: escape a string for safe JSON embedding
json_escape() {
  local input="$1"
  # Remove control characters and escape backslashes, quotes
  printf '%s' "$input" | sed 's/\\/\\\\/g; s/"/\\"/g; s/[[:cntrl:]]//g'
}

bots_json=""
for bot in clawdbot chu-coder chu-scout chu-ops chu-memory; do
  raw_status=$(pm2 jlist 2>/dev/null | jq -r ".[] | select(.name==\"${bot}\") | .pm2_env.status" 2>/dev/null || true)
  # Sanitize: only allow known safe status strings; fall back to "unknown"
  case "$raw_status" in
    online|stopped|stopping|launching|errored|one-launch-status) status="$raw_status" ;;
    *) status="unknown" ;;
  esac
  bots_json="${bots_json}    \"$(json_escape "$bot")\": \"$(json_escape "$status")\","$'\n'
done
# Remove trailing comma from last entry
bots_json="${bots_json%,$'\n'}"$'\n'

disk=$(df -h / | awk 'NR==2 {print $5}')
memory=$(free -m | awk 'NR==2 {printf "%.1f%%", $3*100/$2}')

printf '{\n'
printf '  "timestamp": "%s",\n' "$(json_escape "$(date -Iseconds)")"
printf '  "bots": {\n'
printf '%s' "$bots_json"
printf '  },\n'
printf '  "disk": "%s",\n' "$(json_escape "$disk")"
printf '  "memory": "%s"\n' "$(json_escape "$memory")"
printf '}\n'
