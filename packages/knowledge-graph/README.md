# @chu-collective/knowledge-graph

Shared knowledge graph for multi-agent coordination.

## Installation

```bash
npm install @chu-collective/knowledge-graph
```

## Quick Start

```javascript
const kg = require('@chu-collective/knowledge-graph');

// Create store
const store = kg.create('./knowledge.db');

// Add agent
store.agents.upsert({ 
  id: 'myagent', 
  name: 'My Agent', 
  role: 'Assistant',
  status: 'online' 
});

// Add memory
store.memories.add({
  agent: 'myagent',
  content: 'Learned something important',
  tags: ['learning']
});

// Search
const results = store.search('important');
```

## CLI

```bash
kg agents list
kg tasks add --agent=myagent --title="Do something"
kg memories search "important"
kg status
```

## MCP Server

```bash
npm run mcp
# Exposes tools: kg_agent_status, kg_task_list, kg_memory_search, etc.
```

## Built by the Chu Collective 🐉
