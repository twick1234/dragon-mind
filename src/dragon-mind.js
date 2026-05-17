const fs = require('fs');
const path = require('path');
const os = require('os');
const crypto = require('crypto');

const KNOWLEDGE_FILE = path.join(__dirname, '..', 'knowledge.json');

function emptyStore() {
  return { entries: [], meta: { created: new Date().toISOString(), contributors: [] } };
}

function loadKnowledge() {
  if (!fs.existsSync(KNOWLEDGE_FILE)) {
    return emptyStore();
  }
  try {
    return JSON.parse(fs.readFileSync(KNOWLEDGE_FILE, 'utf8'));
  } catch (err) {
    console.error('[dragon-mind] knowledge.json parse failed, returning empty store:', err.message);
    return emptyStore();
  }
}

function saveKnowledge(data) {
  // Atomic write: write to a temp file beside the target, then rename.
  // rename(2) is atomic on POSIX — concurrent readers never see a partial file.
  const tmp = path.join(
    path.dirname(KNOWLEDGE_FILE),
    `.knowledge-${crypto.randomBytes(6).toString('hex')}.tmp`
  );
  try {
    fs.writeFileSync(tmp, JSON.stringify(data, null, 2));
    fs.renameSync(tmp, KNOWLEDGE_FILE);
  } catch (err) {
    try { fs.unlinkSync(tmp); } catch (_) {}
    throw err;
  }
}

function addKnowledge(topic, content, source, contributor) {
  const data = loadKnowledge();
  const entry = {
    id: crypto.randomUUID(),
    topic,
    content,
    source,
    contributor,
    timestamp: new Date().toISOString()
  };
  data.entries.push(entry);
  if (!data.meta.contributors.includes(contributor)) {
    data.meta.contributors.push(contributor);
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
