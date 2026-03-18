const fs = require('fs');
const path = require('path');

const INPUT_PATH = './apex/canon/legacy-order-map.json';
const ARTIFACTS_DIR = './artifacts/threads';
const OUTPUT_PATH = './legacy-content-timed.json';

const TIME_PATTERN = /\d{1,2}:\d{2}\s+hours,\s+\w+,\s+\w+\s+\d{1,2}(?:st|nd|rd|th)(?:,\s+\d{4})?/i;

function extractContentTime(text) {
  const match = text.match(TIME_PATTERN);
  return match ? match[0] : null;
}

function main() {
  const raw = fs.readFileSync(INPUT_PATH, 'utf8');
  const entries = JSON.parse(raw);
  console.log('Processing ' + entries.length + ' entries...');
  const results = [];
  for (const entry of entries) {
    const artifactFile = path.join(ARTIFACTS_DIR, entry.temp_id + '.json');
    console.log('  Reading: ' + artifactFile);
    let contentTime = null;
    try {
      const artifact = JSON.parse(fs.readFileSync(artifactFile, 'utf8'));
      contentTime = extractContentTime(artifact.text || '');
    } catch (err) {
      console.error('  ERROR: ' + err.message);
    }
    results.push({
      filename: entry.filename,
      path: entry.path,
      created: entry.created,
      modified: entry.modified,
      primaryTime: entry.primaryTime,
      contentTime: contentTime
    });
  }
  fs.writeFileSync(OUTPUT_PATH, JSON.stringify(results, null, 2), 'utf8');
  console.log('Wrote ' + results.length + ' entries to ' + OUTPUT_PATH);
}

main();