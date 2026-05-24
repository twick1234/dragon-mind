const fs = require('fs');
const path = require('path');

const KNOWLEDGE_FILE = path.join(__dirname, '..', 'knowledge.json');

const MAX_FIELD_LENGTH = 10000; // prevent unbounded content DoS

function loadKnowledge() {
  if (!fs.existsSync(KNOWLEDGE_FILE)) {
    return { entries: [], meta: { created: new Date().toISOString(), contributors: [] } };
  }
  let raw;
  try {
    raw = fs.readFileSync(KNOWLEDGE_FILE, 'utf8');
  } catch (err) {
    console.error('Error reading knowledge file:', err.message);
    return { entries: [], meta: { created: new Date().toISOString(), contributors: [] } };
  }
  try {
    return JSON.parse(raw);
  } catch (err) {
    console.error('knowledge.json is malformed — starting with empty store:', err.message);
    return { entries: [], meta: { created: new Date().toISOString(), contributors: [] } };
  }
}

function saveKnowledge(data) {
  try {
    fs.writeFileSync(KNOWLEDGE_FILE, JSON.stringify(data, null, 2));
  } catch (err) {
    console.error('Error saving knowledge file:', err.message);
    throw err;
  }
}

function sanitizeField(value, name) {
  if (typeof value !== 'string') throw new Error(`${name} must be a string`);
  const trimmed = value.trim();
  if (!trimmed) throw new Error(`${name} must not be empty`);
  if (trimmed.length > MAX_FIELD_LENGTH) throw new Error(`${name} exceeds max length of ${MAX_FIELD_LENGTH}`);
  return trimmed;
}

function addKnowledge(topic, content, source, contributor) {
  const safeTopic = sanitizeField(topic, 'topic');
  const safeContent = sanitizeField(content, 'content');
  const safeSource = sanitizeField(source || 'cli', 'source');
  const safeContributor = sanitizeField(contributor || 'unknown', 'contributor');

  const data = loadKnowledge();
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
  const data = loadKnowledge();
  const term = searchTerm.toLowerCase();
  return data.entries.filter(e => 
    e.topic.toLowerCase().includes(term) || 
    e.content.toLowerCase().includes(term)
  );
}

function getRecent(limit = 10) {
  const data = loadKnowledge();
  return data.entries.slice(-limit);
}

function listTopics() {
  const data = loadKnowledge();
  return [...new Set(data.entries.map(e => e.topic))];
}

module.exports = { addKnowledge, query, getRecent, listTopics, loadKnowledge };
