const fs = require('fs');
const path = require('path');

const KNOWLEDGE_FILE = path.join(__dirname, '..', 'knowledge.json');

function loadKnowledge() {
  if (!fs.existsSync(KNOWLEDGE_FILE)) {
    return { entries: [], meta: { created: new Date().toISOString(), contributors: [] } };
  }
  return JSON.parse(fs.readFileSync(KNOWLEDGE_FILE, 'utf8'));
}

function saveKnowledge(data) {
  fs.writeFileSync(KNOWLEDGE_FILE, JSON.stringify(data, null, 2));
}

function addKnowledge(topic, content, source, contributor) {
  const data = loadKnowledge();
  const entry = {
    id: Date.now().toString(36),
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
