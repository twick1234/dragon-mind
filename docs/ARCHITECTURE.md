# Dragon Mind - Architecture Document

**Version:** 0.1.0  
**Author:** ChuMemory 🧠  
**Date:** 2026-02-04  
**Status:** Draft

---

## 1. Overview

Dragon Mind uses a **file-based coordination architecture** where agents communicate through shared markdown files and group chat messages. This approach leverages Clawdbot's existing infrastructure while enabling rich multi-agent collaboration.

```
┌─────────────────────────────────────────────────────────────┐
│                     DRAGON MIND SYSTEM                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐   │
│  │ CustomerChu │     │  ChuMemory  │     │  ChuCoder   │   │
│  │ Coordinator │     │   Docs 🧠   │     │  Code 🐒    │   │
│  └──────┬──────┘     └──────┬──────┘     └──────┬──────┘   │
│         │                   │                   │           │
│  ┌──────┴───────────────────┴───────────────────┴──────┐   │
│  │              SHARED WORKSPACE (dragon-mind/)         │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │   │
│  │  │STATUS.md │  │ INBOX.md │  │ docs/, src/, etc │   │   │
│  │  └──────────┘  └──────────┘  └──────────────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
│         │                   │                   │           │
│  ┌──────┴──────┐     ┌──────┴──────┐     ┌──────┴──────┐   │
│  │  ChuScout   │     │   ChuOps    │     │   Human     │   │
│  │ Research 🔍 │     │  DevOps 👹  │     │  Overseer   │   │
│  └─────────────┘     └─────────────┘     └─────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
           │                                      │
           ▼                                      ▼
    ┌─────────────┐                      ┌─────────────┐
    │  Telegram   │◄────────────────────►│  Clawdbot   │
    │ Group Chat  │                      │   Gateway   │
    └─────────────┘                      └─────────────┘
```

## 2. Core Components

### 2.1 Agent Workspaces

Each Chu agent has a dedicated workspace with standard files:

```
/home/hacker8/chu-<name>/
├── SOUL.md          # Agent personality & role
├── AGENTS.md        # Team instructions
├── HEARTBEAT.md     # Polling behavior
├── INBOX.md         # Incoming tasks
├── MEMORY.md        # Persistent context
└── memory/          # Daily notes
    └── YYYY-MM-DD.md
```

### 2.2 Shared Project Workspace

The `dragon-mind/` workspace is shared across all agents:

```
/home/hacker8/dragon-mind/
├── STATUS.md        # Live progress board
├── docs/            # Documentation (ChuMemory)
│   ├── PRD.md
│   ├── BRD.md
│   └── ARCHITECTURE.md
├── src/             # Source code (ChuCoder)
├── research/        # Findings (ChuScout)
└── infra/           # DevOps configs (ChuOps)
```

### 2.3 Communication Channels

| Channel | Purpose | Direction |
|---------|---------|-----------|
| INBOX.md | Task dispatch | CustomerChu → Agents |
| STATUS.md | Progress sync | All agents (read/write) |
| Telegram Group | Real-time updates | All agents ↔ Human |
| Clawdbot Gateway | Message routing | System ↔ Agents |

## 3. Data Flow

### 3.1 Task Lifecycle

```
1. Human Request (Telegram)
        │
        ▼
2. CustomerChu Receives
        │
        ▼
3. Task Breakdown
        │
        ├──► INBOX.md (ChuMemory)
        ├──► INBOX.md (ChuCoder)
        ├──► INBOX.md (ChuScout)
        └──► INBOX.md (ChuOps)
        │
        ▼
4. Heartbeat Triggers
        │
        ▼
5. Agents Execute
        │
        ├──► STATUS.md updates
        └──► Telegram updates
        │
        ▼
6. Completion → Human Review
```

### 3.2 Inter-Agent Communication

Agents communicate through:

1. **Direct mentions** in Telegram (`@ChuCoder_bot`)
2. **STATUS.md** updates (read by all agents)
3. **Shared files** in dragon-mind workspace
4. **sessions_send** for urgent direct messages

## 4. Technical Decisions

### 4.1 Why File-Based Coordination?

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| File-based | Simple, debuggable, works now | Polling latency | ✅ MVP |
| Database | Faster queries | Infrastructure needed | Future |
| Message queue | Real-time | Complexity | Future |

### 4.2 Why Heartbeat Polling?

- Agents check INBOX.md on heartbeat intervals
- Simple, reliable, no additional infrastructure
- Latency acceptable for async collaboration

### 4.3 Why Telegram?

- Already integrated with Clawdbot
- Supports group chats with multiple bots
- Human can easily participate
- Message history preserved

## 5. Agent Specifications

### 5.1 CustomerChu (Coordinator)
- **Triggers:** Human messages in group
- **Actions:** Task breakdown, dispatch to INBOXes
- **Outputs:** STATUS.md coordination

### 5.2 ChuMemory (Documentation) 🧠
- **Triggers:** INBOX.md tasks, mentions
- **Actions:** Create docs, research summaries
- **Outputs:** PRD, BRD, Architecture, specs

### 5.3 ChuCoder (Engineering) 🐒
- **Triggers:** INBOX.md tasks, architecture docs
- **Actions:** Write code, create demos
- **Outputs:** src/, tests/, working software

### 5.4 ChuScout (Research) 🔍
- **Triggers:** INBOX.md tasks, mentions
- **Actions:** Web search, analysis
- **Outputs:** research/, competitive intel

### 5.5 ChuOps (Operations) 👹
- **Triggers:** INBOX.md tasks, deployment needs
- **Actions:** Monitor, deploy, maintain
- **Outputs:** infra/, dashboards

## 6. Operational Infrastructure (Human-AI Partnership)

### 6.1 The Coordination Problem

**Challenge:** Only CustomerChu can read the Telegram group chat. The other Chu bots (ChuCoder, ChuScout, ChuOps, ChuMemory) run as separate Clawdbot instances and cannot see group messages unless directly @mentioned.

**Solution:** CustomerChu acts as the **coordinator/dispatcher**, translating group conversations into INBOX.md task files that other agents process during their heartbeat cycles.

```
┌─────────────────────────────────────────────────────────────┐
│                 COMMUNICATION ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              TELEGRAM GROUP (Bot World)              │   │
│  │                                                      │   │
│  │   Human (Mark) ←──────────────→ CustomerChu          │   │
│  │        │                              │               │   │
│  │        │  @mentions trigger           │               │   │
│  │        ▼  individual bots             ▼               │   │
│  │   [ChuCoder] [ChuScout] [ChuOps] [ChuMemory]         │   │
│  │   (respond when                  (I dispatch         │   │
│  │    directly tagged)               tasks to them)     │   │
│  └──────────────────────────────────────────────────────┘   │
│                              │                               │
│                              ▼                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           FILE-BASED TASK DISPATCH                   │   │
│  │                                                      │   │
│  │  CustomerChu writes to:                              │   │
│  │    /home/hacker8/chu-coder/INBOX.md                  │   │
│  │    /home/hacker8/chu-scout/INBOX.md                  │   │
│  │    /home/hacker8/chu-ops/INBOX.md                    │   │
│  │    /home/hacker8/chu-memory/INBOX.md                 │   │
│  │                                                      │   │
│  │  Each agent checks INBOX.md on heartbeat (~30 min)   │   │
│  │  and processes pending tasks                         │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Bot Health & Recovery System

Mark designed a robust monitoring system to keep all bots alive:

```
┌─────────────────────────────────────────────────────────────┐
│              BOT HEALTH MONITORING SYSTEM                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌─────────────────────────────────────────┐               │
│   │  clawdbot-health-monitor.sh (systemd)   │               │
│   │  Runs every 60 seconds                  │               │
│   └─────────────────┬───────────────────────┘               │
│                     │                                        │
│                     ▼                                        │
│   ┌─────────────────────────────────────────┐               │
│   │  PM2 Process Manager                    │               │
│   │  ┌─────────┐ ┌─────────┐ ┌─────────┐   │               │
│   │  │chu-coder│ │chu-scout│ │chu-ops  │   │               │
│   │  │  (20)   │ │  (21)   │ │  (22)   │   │               │
│   │  └─────────┘ └─────────┘ └─────────┘   │               │
│   │  ┌──────────┐ ┌────────────────────┐   │               │
│   │  │chu-memory│ │customerchu (main)  │   │               │
│   │  │  (23)    │ │  (via systemd)     │   │               │
│   │  └──────────┘ └────────────────────┘   │               │
│   └─────────────────────────────────────────┘               │
│                     │                                        │
│                     ▼                                        │
│   ┌─────────────────────────────────────────┐               │
│   │  Auto-Recovery Actions                  │               │
│   │  • Detect crashed process               │               │
│   │  • Automatic restart via PM2            │               │
│   │  • Alert to Telegram on failure         │               │
│   │  • Log to /tmp/clawdbot/ for debugging  │               │
│   └─────────────────────────────────────────┘               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Key Files:**
- `/home/hacker8/clawdbot-health-monitor.sh` - Health check script
- `/home/hacker8/.config/systemd/user/clawdbot-health-monitor.service` - Systemd service
- PM2 ecosystem managed via `pm2 startup` and `pm2 save`

### 6.3 Multi-Bot Configuration

Each Chu bot runs as a separate Clawdbot instance with its own:

| Component | Path |
|-----------|------|
| Config | `~/.clawdbot-<name>/clawdbot.json` |
| Sessions | `~/.clawdbot-<name>/agents/` |
| Auth | `~/.clawdbot-<name>/agents/main/agent/auth-profiles.json` |
| Workspace | `/home/hacker8/chu-<name>/` |

**Critical Config Settings:**
```json
{
  "channels": {
    "telegram": {
      "groups": {
        "*": {
          "enabled": true,
          "allowFrom": ["*"],
          "requireMention": false  // Respond to all messages
        }
      }
    }
  }
}
```

### 6.4 Debugging Session (2026-02-04)

Mark and CustomerChu debugged why bots weren't responding:

| Issue | Root Cause | Solution |
|-------|-----------|----------|
| Bots not responding | `activation` key invalid | Use `requireMention: false` |
| getUpdates conflict | Stale processes | Kill all, restart cleanly |
| No API auth | Missing auth-profiles.json | Copy from main bot |
| Config validation | Wrong key names | Consult Clawdbot docs |

**Key Learning:** Telegram bots need:
1. Privacy mode OFF (via @BotFather `/setprivacy`)
2. Correct `requireMention` config
3. No duplicate polling processes
4. Valid API credentials in auth-profiles.json

### 6.5 Startup Sequence

```bash
# 1. Main CustomerChu bot (via systemd)
systemctl --user start clawdbot-gateway

# 2. Chu Collective bots (via PM2)
pm2 start chu-coder chu-scout chu-ops chu-memory

# 3. Health monitor (via systemd)
systemctl --user start clawdbot-health-monitor
```

## 7. Memory Architecture

### 7.1 Memory Hierarchy

Each agent maintains a multi-layered memory system:

```
┌─────────────────────────────────────────────────────────────┐
│                    MEMORY ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              AGENT WORKSPACE MEMORY                  │   │
│  │           /home/hacker8/chu-<name>/                  │   │
│  │                                                      │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │  SOUL.md    │  │  AGENTS.md  │  │   USER.md   │  │   │
│  │  │ (Identity)  │  │ (Behavior)  │  │ (Human ctx) │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  │                                                      │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │ MEMORY.md   │  │HEARTBEAT.md │  │  INBOX.md   │  │   │
│  │  │(Long-term)  │  │ (Tasks)     │  │ (Incoming)  │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  │                                                      │   │
│  │  ┌───────────────────────────────────────────────┐  │   │
│  │  │              memory/ (Daily Logs)             │  │   │
│  │  │  2026-02-03.md  2026-02-04.md  ...           │  │   │
│  │  └───────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           CLAWDBOT SESSION MEMORY                    │   │
│  │        ~/.clawdbot-<name>/agents/main/               │   │
│  │                                                      │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │  sessions/ (Conversation History)           │    │   │
│  │  │  • Telegram group sessions                  │    │   │
│  │  │  • DM sessions                              │    │   │
│  │  │  • Compacted summaries                      │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  │                                                      │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │  agent/auth-profiles.json (API Keys)        │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           SHARED PROJECT MEMORY                      │   │
│  │          /home/hacker8/dragon-mind/                  │   │
│  │                                                      │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │ STATUS.md   │  │ KANBAN.md   │  │ README.md   │  │   │
│  │  │(Live state) │  │ (Tasks)     │  │ (Overview)  │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  │                                                      │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │  docs/ research/ src/ (Shared artifacts)    │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Memory Files Explained

| File | Purpose | Persistence | Who Writes |
|------|---------|-------------|------------|
| `SOUL.md` | Agent identity, personality, role | Permanent | Human/Agent |
| `AGENTS.md` | Behavioral instructions | Permanent | Human |
| `USER.md` | Context about the human | Evolving | Agent |
| `MEMORY.md` | Long-term curated memories | Evolving | Agent |
| `memory/YYYY-MM-DD.md` | Daily raw logs | Daily | Agent |
| `HEARTBEAT.md` | Periodic task checklist | Dynamic | Agent |
| `INBOX.md` | Incoming task queue | Transient | Coordinator |
| `TOOLS.md` | Tool-specific notes | Evolving | Agent |

### 7.3 Memory Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    MEMORY LIFECYCLE                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   1. SESSION START                                          │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  Agent reads: SOUL.md → USER.md → MEMORY.md         │   │
│   │  Agent reads: memory/today.md + memory/yesterday.md │   │
│   │  Agent reads: HEARTBEAT.md (if heartbeat trigger)   │   │
│   └─────────────────────────────────────────────────────┘   │
│                         │                                    │
│                         ▼                                    │
│   2. DURING SESSION                                         │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  Agent accumulates context in conversation          │   │
│   │  Agent may update files as needed                   │   │
│   └─────────────────────────────────────────────────────┘   │
│                         │                                    │
│                         ▼                                    │
│   3. PRE-COMPACTION FLUSH                                   │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  System prompts: "Store durable memories now"       │   │
│   │  Agent writes to: memory/YYYY-MM-DD.md              │   │
│   │  Agent may update: MEMORY.md (significant events)   │   │
│   └─────────────────────────────────────────────────────┘   │
│                         │                                    │
│                         ▼                                    │
│   4. SESSION COMPACTION                                     │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  Clawdbot compresses conversation history           │   │
│   │  Summary preserved, old context discarded           │   │
│   └─────────────────────────────────────────────────────┘   │
│                         │                                    │
│                         ▼                                    │
│   5. NEXT SESSION                                           │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  Agent wakes fresh, reads memory files              │   │
│   │  Continuity restored from files, not conversation   │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 7.4 Cross-Agent Memory Sharing

```
┌─────────────────────────────────────────────────────────────┐
│              SHARED MEMORY COORDINATION                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  CustomerChu (Coordinator)                                  │
│       │                                                      │
│       │ Reads group chat, understands context               │
│       │                                                      │
│       ├──► Writes INBOX.md to each agent workspace          │
│       │    (Task dispatch with context)                     │
│       │                                                      │
│       ├──► Updates dragon-mind/STATUS.md                    │
│       │    (All agents can read current state)              │
│       │                                                      │
│       └──► Updates dragon-mind/KANBAN.md                    │
│            (Project-wide task tracking)                     │
│                                                              │
│  Other Agents                                               │
│       │                                                      │
│       ├──► Read their INBOX.md on heartbeat                 │
│       │                                                      │
│       ├──► Read dragon-mind/STATUS.md for context           │
│       │                                                      │
│       ├──► Write to dragon-mind/ shared folders             │
│       │    (docs/, src/, research/, ops/)                   │
│       │                                                      │
│       └──► Post updates to Telegram when mentioned          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 7.5 GitHub Backup Strategy

All memory is backed up to GitHub for persistence:

| Repository | Content | Backup Frequency |
|------------|---------|------------------|
| Claims-Phoenix | CustomerChu workspace, MEMORY.md, daily logs | On significant changes |
| dragon-mind | Shared project files, docs, architecture | After major updates |
| chu-* workspaces | Individual agent memories | Periodic |

**Backup Command:**
```bash
cd /home/hacker8/Claims-Phoenix && git add -A && git commit -m "Memory backup" && git push
cd /home/hacker8/dragon-mind && git add -A && git commit -m "Project backup" && git push
```

### 7.6 Memory Search (Semantic Recall)

Agents use `memory_search` tool to find relevant past context:

```
User: "What did we decide about the API?"
       │
       ▼
memory_search(query="API decision")
       │
       ▼
Returns snippets from:
  • MEMORY.md (long-term)
  • memory/*.md (daily logs)
  • With file paths and line numbers
       │
       ▼
memory_get(path="memory/2026-02-03.md", from=45, lines=10)
       │
       ▼
Agent retrieves specific context
```

## 8. Security Considerations

- Agents operate within their Clawdbot sandbox
- No direct internet access except through tools
- Human approval required for destructive operations
- Sensitive data stays in private workspace files

## 7. Scalability Path

### Current (v0.1)
- 5 specialized agents
- Single workspace
- Telegram group

### Future
- Dynamic agent spawning
- Multiple project workspaces
- Cross-project coordination
- Cost optimization layer

## 8. Integration Points

```
┌─────────────────┐
│   External      │
│   Services      │
├─────────────────┤
│ • GitHub        │──► ChuCoder
│ • Web Search    │──► ChuScout  
│ • Notion        │──► ChuMemory
│ • Monitoring    │──► ChuOps
└─────────────────┘
```

## 9. For ChuCoder

**When building the core engine:**

1. Read STATUS.md first to avoid conflicts
2. Code goes in `/home/hacker8/dragon-mind/src/`
3. Consider heartbeat coordination in design
4. File-based state is the current pattern
5. Keep it simple—we're proving the concept

**Questions for you:**
- What's the minimum viable engine?
- Can we start with a CLI demo?
- How should we handle agent failures?

---

*This architecture supports the PRD and BRD*  
*Created by ChuMemory 🧠 for the Chu Collective*
