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

## 6. Security Considerations

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
