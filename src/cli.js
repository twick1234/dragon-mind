#!/usr/bin/env node
const { addKnowledge, query, getRecent, listTopics } = require('./dragon-mind');

const [,, cmd, ...args] = process.argv;

switch (cmd) {
  case 'add': {
    const [topic, content, source, contributor] = args;
    if (!topic || !content) {
      console.error('Usage: node cli.js add <topic> <content> [source] [contributor]');
      process.exit(1);
    }
    try {
      const entry = addKnowledge(topic, content, source || 'cli', contributor || 'unknown');
      console.log('Added:', entry);
    } catch (err) {
      console.error('Error:', err.message);
      process.exit(1);
    }
    break;
  }
  case 'query': {
    if (!args[0]) {
      console.error('Usage: node cli.js query <searchTerm>');
      process.exit(1);
    }
    try {
      console.log(query(args[0]));
    } catch (err) {
      console.error('Error:', err.message);
      process.exit(1);
    }
    break;
  }
  case 'recent': {
    const limit = args[0] ? parseInt(args[0], 10) : 10;
    if (isNaN(limit) || limit < 1) {
      console.error('limit must be a positive integer');
      process.exit(1);
    }
    try {
      console.log(getRecent(limit));
    } catch (err) {
      console.error('Error:', err.message);
      process.exit(1);
    }
    break;
  }
  case 'topics':
    console.log(listTopics());
    break;
  default:
    console.log('Usage: node cli.js <add|query|recent|topics> [args]');
}
