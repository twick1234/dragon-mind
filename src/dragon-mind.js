const fs = require('fs');
const path = require('path');
const os = require('os');

const KNOWLEDGE_FILE = path.join(__dirname, '..', 'knowledge.json');
const MAX_TOPIC_LEN = 200;
const MAX_CONTENT_LEN = 10000;

function loadKnowledge() {
  if (!fs.existsSync(KNOWLEDGE_FILE)) {
    return { entries: [], meta: { created: new Date().toISOString(), contributors: [] } };
  }
  try {
    return JSON.parse(fs.readFileSync(KNOWLEDGE_FILE, 'utf8'));
  } catch (e) {
    console.error('Warning: knowledge.json is corrupt, starting fresh:', e.message);
    return { entries: [], meta: { created: new Date().toISOString(), contributors: [] } };
  }
}

function saveKnowledge(data) {
  const tmp = path.join(os.tmpdir(), `knowledge-${Date.now()}.json.tmp`);
  fs.writeFileSync(tmp, JSON.stringify(data, null, 2));
  fs.renameSync(tmp, KNOWLEDGE_FILE);
}

function addKnowledge(topic, content, source, contributor) {
  if (typeof topic !== 'string' || typeof content !== 'string') {
    throw new Error('topic and content must be strings');
  }
  if (topic.length > MAX_TOPIC_LEN || content.length > MAX_CONTENT_LEN) {
    throw new Error(`Input exceeds size limit (topic: ${MAX_TOPIC_LEN}, content: ${MAX_CONTENT_LEN})`);
  }
  const data = loadKnowledge();
  const entry = {
    id: Date.now().toString(36),
    topic,
    content,
    source: typeof source === 'string' ? source : 'cli',
    contributor: typeof contributor === 'string' ? contributor : 'unknown',
    timestamp: new Date().toISOString()
  };
  data.entries.push(entry);
  if (!data.meta.contributors.includes(entry.contributor)) {
    data.meta.contributors.push(entry.contributor);
  }
  saveKnowledge(data);
  return entry;
}

function query(searchTerm) {
  if (!searchTerm) return [];
  const data = loadKnowledge();
  const term = String(searchTerm).toLowerCase();
  return data.entries.filter(e =>
    (typeof e.topic === 'string' && e.topic.toLowerCase().includes(term)) ||
    (typeof e.content === 'string' && e.content.toLowerCase().includes(term))
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
