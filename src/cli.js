#!/usr/bin/env node
const { addKnowledge, query, getRecent, listTopics } = require('./dragon-mind');

const [,, cmd, ...args] = process.argv;

switch(cmd) {
  case 'add':
    const [topic, content, source, contributor] = args;
    const entry = addKnowledge(topic, content, source || 'cli', contributor || 'unknown');
    console.log('Added:', entry);
    break;
  case 'query':
    console.log(query(args[0]));
    break;
  case 'recent':
    console.log(getRecent(parseInt(args[0]) || 10));
    break;
  case 'topics':
    console.log(listTopics());
    break;
  default:
    console.log('Usage: node cli.js <add|query|recent|topics> [args]');
}
