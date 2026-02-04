# 🐉 Dragon Mind Operations Runbook

## Overview

This runbook documents operational procedures for the Chu Collective bot infrastructure.

---

## Bot Management (PM2)

### Start/Stop/Restart Bots

```bash
# List all bots
pm2 list

# Start a bot
pm2 start <bot-name>

# Stop a bot
pm2 stop <bot-name>

# Restart a bot
pm2 restart <bot-name>

# Restart all bots
pm2 restart all
```

### Bot Names
- `clawdbot` - Main Clawdbot instance
- `chu-coder` - ChuCoder agent
- `chu-scout` - ChuScout agent
- `chu-ops` - ChuOps agent (that's me! 👹)
- `chu-memory` - ChuMemory agent

### View Status
```bash
# Simple status
pm2 status

# Detailed JSON output
pm2 jlist

# Monitor in real-time
pm2 monit
```

---

## Log Locations

All PM2 logs are stored in: `~/.pm2/logs/`

### Log Files
- `<bot-name>-out.log` - Standard output
- `<bot-name>-error.log` - Error output

### Viewing Logs
```bash
# Tail logs for a specific bot
pm2 logs <bot-name>

# Tail all logs
pm2 logs

# Last 100 lines
pm2 logs --lines 100

# Direct file access
tail -f ~/.pm2/logs/clawdbot-out.log
```

### Log Rotation
```bash
# Install log rotate module
pm2 install pm2-logrotate

# Configure max size (default 10MB)
pm2 set pm2-logrotate:max_size 10M

# Configure retention (default 30 files)
pm2 set pm2-logrotate:retain 30
```

---

## Common Issues & Fixes

### Bot Not Responding

1. **Check if running:**
   ```bash
   pm2 status <bot-name>
   ```

2. **Check logs for errors:**
   ```bash
   pm2 logs <bot-name> --lines 50
   ```

3. **Restart the bot:**
   ```bash
   pm2 restart <bot-name>
   ```

### High Memory Usage

1. **Check memory:**
   ```bash
   pm2 monit
   # or
   free -h
   ```

2. **Restart offending bot:**
   ```bash
   pm2 restart <bot-name>
   ```

3. **If persists, check for memory leaks in logs**

### Disk Space Full

1. **Check disk usage:**
   ```bash
   df -h
   ```

2. **Clear old logs:**
   ```bash
   pm2 flush  # Clears all logs
   ```

3. **Check large files:**
   ```bash
   du -sh ~/.pm2/logs/*
   ```

### Bot Stuck in "errored" State

1. **Check error logs:**
   ```bash
   pm2 logs <bot-name> --err --lines 100
   ```

2. **Delete and restart:**
   ```bash
   pm2 delete <bot-name>
   pm2 start <ecosystem-file> --only <bot-name>
   ```

### Connection Issues

1. **Check network:**
   ```bash
   ping api.telegram.org
   curl -I https://api.anthropic.com
   ```

2. **Check API keys in config**

3. **Restart affected bot**

---

## Emergency Procedures

### 🚨 All Bots Down

```bash
# Quick recovery
pm2 resurrect

# If that fails, restart all
pm2 restart all

# Nuclear option - kill and reload
pm2 kill
pm2 start ecosystem.config.js  # or your config file
```

### 🚨 System Unresponsive

1. Check system resources:
   ```bash
   top
   htop
   ```

2. Kill runaway processes if needed

3. Restart PM2 daemon:
   ```bash
   pm2 kill
   pm2 start all
   ```

### 🚨 Need to Roll Back

1. Check git history:
   ```bash
   git log --oneline -10
   ```

2. Revert to previous commit:
   ```bash
   git checkout <commit-hash>
   pm2 restart all
   ```

---

## Health Check

Run the health check script:
```bash
./ops/health-check.sh
```

This outputs JSON with:
- Timestamp
- All bot statuses
- Disk usage
- Memory usage

---

## Useful Commands Cheatsheet

| Task | Command |
|------|---------|
| List bots | `pm2 list` |
| Restart bot | `pm2 restart <name>` |
| View logs | `pm2 logs <name>` |
| Monitor | `pm2 monit` |
| Clear logs | `pm2 flush` |
| Save state | `pm2 save` |
| Load saved | `pm2 resurrect` |
| Health check | `./ops/health-check.sh` |

---

## Contact

- **ChuOps** 👹 - Infrastructure guardian
- **CustomerChu** 🐉 - Team lead
- **Bot World Group** - Team coordination

---

*Last updated: Dragon Mind v1.0*
