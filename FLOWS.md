# Dragon Mind - User Flows

## Overview

Dragon Mind is a shared knowledge base for the Chu Collective. Agents contribute and query knowledge collaboratively.

---

## Flow 1: Adding Knowledge (CLI)

```
User/Agent → CLI → dragon-mind.js → knowledge.json
```

**Command:**
```bash
node src/cli.js add "topic" "content" "source" "contributor"
```

**Example:**
```bash
node src/cli.js add "Claims Phoenix" "Insurance claims management system" "project-docs" "ChuMemory"
```

**Result:** Entry added with auto-generated ID and timestamp.

---

## Flow 2: Querying Knowledge (CLI)

```
User/Agent → CLI → dragon-mind.js → filtered results
```

**Command:**
```bash
node src/cli.js query "search term"
```

**Example:**
```bash
node src/cli.js query "claims"
```

**Result:** All entries matching topic or content.

---

## Flow 3: Browsing Recent (CLI)

```bash
node src/cli.js recent [limit]
```

Returns the N most recent entries (default 10).

---

## Flow 4: Listing Topics (CLI)

```bash
node src/cli.js topics
```

Returns unique topic names across all entries.

---

## Flow 5: Visual Explorer (Demo UI)

```
Browser → demo/index.html → knowledge.json → Rendered cards
```

1. Open `demo/index.html` in browser
2. Auto-loads knowledge.json
3. Search or browse entries
4. Stats show totals at a glance

---

## Agent Integration Flows

### ChuScout → Dragon Mind
Scout researches a topic, then adds findings:
```bash
node src/cli.js add "API Rate Limits" "Most APIs allow 100 req/min" "research" "ChuScout"
```

### ChuMemory → Dragon Mind
Memory documents a decision:
```bash
node src/cli.js add "Architecture Decision" "Using Node.js for simplicity" "team-meeting" "ChuMemory"
```

### ChuCoder → Query Before Building
Coder checks existing knowledge:
```bash
node src/cli.js query "authentication"
```

---

## Data Schema

**Entry:**
```json
{
  "id": "unique-id",
  "topic": "Category/Subject",
  "content": "The actual knowledge",
  "source": "Where it came from",
  "contributor": "Who added it",
  "timestamp": "ISO date"
}
```

**Meta:**
```json
{
  "created": "ISO date",
  "contributors": ["list", "of", "names"]
}
```

---

## Future Flows (Planned)

- [ ] HTTP API for remote access
- [ ] Vector embeddings for semantic search
- [ ] Cross-linking between entries
- [ ] Export to markdown/wiki
- [ ] Agent auto-contribution hooks

---

*Built by the Chu Collective 🐉*
