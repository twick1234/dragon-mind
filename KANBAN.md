# 🐉 Dragon Mind - Kanban Board

**Last Updated:** 2026-02-04 21:53 SGT by CustomerChu

---

## 📦 Package: @chu-collective/knowledge-graph
*Portable, reusable, npm-installable*

---

## 🔄 IN PROGRESS - Incremental Steps

### Step 1: Minimal Core ⬅️ START HERE
**Owner:** 🐒 ChuCoder
- [ ] `packages/knowledge-graph/src/store.js`
- [ ] SQLite + better-sqlite3
- [ ] Agents, Tasks, Memories, Standards CRUD
- [ ] **Measure:** Can agents share state?

### Step 2: CLI Tool
**Owner:** 🐒 ChuCoder
- [ ] `packages/knowledge-graph/bin/kg-cli.js`
- [ ] `kg agents list`, `kg tasks add`, etc.
- [ ] **Measure:** Can interact from command line?

### Step 3: Full-Text Search
**Owner:** 🐒 ChuCoder
- [ ] `packages/knowledge-graph/src/search.js`
- [ ] SQLite FTS5
- [ ] **Measure:** Find memories by keyword <100ms?

### Step 4: MCP Server
**Owner:** 🐒 ChuCoder
- [ ] `packages/knowledge-graph/src/mcp-server.js`
- [ ] Tools: kg_agent_status, kg_memory_search, etc.
- [ ] **Measure:** Can Claude connect via MCP?

### Step 5: Human Dashboard
**Owner:** 🐒 ChuCoder
- [ ] `packages/knowledge-graph/demo/explorer.html`
- [ ] Browse agents, tasks, memories
- [ ] Search UI
- [ ] **Measure:** Humans can see agent state?

---

## 🔍 Research (Parallel)

### 🔍 ChuScout
- [ ] KNOWLEDGE-GRAPH-COMPARISON.md
- [ ] Neo4j vs Postgres vs SQLite analysis
- [ ] Recommendation for future scaling

### 🧠 ChuMemory
- [ ] ADR-001-KNOWLEDGE-GRAPH.md
- [ ] Document each step's learnings

### 👹 ChuOps
- [ ] Backup scripts
- [ ] Health monitoring integration

---

## ✅ DONE
- [x] Project setup (CustomerChu)
- [x] PRD, BRD, ARCHITECTURE (ChuMemory)
- [x] Package structure scaffolded
- [x] Incremental plan defined
- [x] Vercel deployment (37 pages)

---

## 📊 Sprint Goal
Build `@chu-collective/knowledge-graph`:
- ✅ Portable npm package
- ✅ Works anywhere (no server required)
- ✅ Incremental: step, measure, iterate
- ✅ MCP integration for agents
- ✅ Human dashboard for visibility

---

*The Chu Collective builds incrementally* 🐉
