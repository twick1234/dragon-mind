#!/bin/bash
echo "{"
echo "  \"timestamp\": \"$(date -Iseconds)\","
echo "  \"bots\": {"

for bot in clawdbot chu-coder chu-scout chu-ops chu-memory; do
  status=$(pm2 jlist | jq -r ".[] | select(.name==\"$bot\") | .pm2_env.status" 2>/dev/null || echo "unknown")
  echo "    \"$bot\": \"$status\","
done

echo "  },"
echo "  \"disk\": \"$(df -h / | awk 'NR==2 {print $5}')\","
echo "  \"memory\": \"$(free -m | awk 'NR==2 {printf \"%.1f%%\", $3*100/$2}')\""
echo "}"
