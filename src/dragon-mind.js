const fs = require('fs');
const path = require('path');

const KNOWLEDGE_FILE = path.join(__dirname, '..', 'knowledge.json');
const MAX_FIELD_LENGTH = 10000;
const MAX_ENTRIES = 10000;

function sanitize(value, fieldName) {
  if (typeof value !== 'string') throw new TypeError(`${fieldName} must be a string`);
  const trimmed = value.slice(0, MAX_FIELD_LENGTH);
  return trimmed;
}

function loadKnowledge() {
  if (!fs.existsSync(KNOWLEDGE_FILE)) {
    return { entries: [], meta: { created: new Date().toISOString(), contributors: [] } };
  }
  const raw = JSON.parse(fs.readFileSync(KNOWLEDGE_FILE, 'utf8'));
  if (!Array.isArray(raw.entries)) raw.entries = [];
  if (!raw.meta || typeof raw.meta !== 'object') raw.meta = { created: new Date().toISOString(), contributors: [] };
  if (!Array.isArray(raw.meta.contributors)) raw.meta.contributors = [];
  return raw;
}

function saveKnowledge(data) {
  fs.writeFileSync(KNOWLEDGE_FILE, JSON.stringify(data, null, 2));
}

function addKnowledge(topic, content, source, contributor) {
  const safeTopic = sanitize(topic, 'topic');
  const safeContent = sanitize(content, 'content');
  const safeSource = sanitize(source || 'cli', 'source');
  const safeContributor = sanitize(contributor || 'unknown', 'contributor');

  const data = loadKnowledge();
  if (data.entries.length >= MAX_ENTRIES) {
    throw new Error(`Knowledge store limit (${MAX_ENTRIES} entries) reached`);
  }

  const entry = {
    id: Date.now().toString(36),
    topic: safeTopic,
    content: safeContent,
    source: safeSource,
    contributor: safeContributor,
    timestamp: new Date().toISOString()
  };
  data.entries.push(entry);
  if (!data.meta.contributors.includes(safeContributor)) {
    data.meta.contributors.push(safeContributor);
  }
  saveKnowledge(data);
  return entry;
}

function query(searchTerm) {
  const safe = sanitize(searchTerm, 'searchTerm');
  const data = loadKnowledge();
  const term = safe.toLowerCase();
  return data.entries.filter(e =>
    e.topic.toLowerCase().includes(term) ||
    e.content.toLowerCase().includes(term)
  );
}

function getRecent(limit = 10) {
  const safeLimit = Math.min(Math.max(1, Math.floor(Number(limit))), 1000);
  if (!Number.isFinite(safeLimit)) throw new RangeError('limit must be a finite number');
  const data = loadKnowledge();
  return data.entries.slice(-safeLimit);
}

function listTopics() {
  const data = loadKnowledge();
  return [...new Set(data.entries.map(e => e.topic))];
}

module.exports = { addKnowledge, query, getRecent, listTopics, loadKnowledge };
