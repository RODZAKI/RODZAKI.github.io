const fs = require('fs');
const path = require('path');

// INPUT: ChatGPT export file
const inputPath = path.join(__dirname, '../chatgpt-export.json');

// OUTPUT DIR
const outputDir = path.join(__dirname, '../artifacts/threads');

if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

const raw = JSON.parse(fs.readFileSync(inputPath, 'utf-8'));

// ChatGPT export is typically an array of conversations
let index = 1;

raw.forEach(thread => {
  const title = thread.title || `Untitled-${index}`;

  // Extract earliest timestamp (thread start)
  let timestamps = [];

  if (thread.mapping) {
    Object.values(thread.mapping).forEach(node => {
      if (node.message && node.message.create_time) {
        timestamps.push(node.message.create_time);
      }
    });
  }

  if (timestamps.length === 0) return;

  const primaryTime = Math.min(...timestamps) * 1000; // convert to ms
  const iso = new Date(primaryTime).toISOString();

  const output = {
    filename: `${title}.json`,
    path: `/threads-thunk/${title}.json`,

    primaryTime: primaryTime,

    contentTime: iso,
    contentTimeISO: iso,

    resolvedTime: iso
  };

  const padded = String(index).padStart(3, '0');
  const outputPath = path.join(outputDir, `thunk-${padded}.json`);

  fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));

  index++;
});

console.log(`THUNK ingestion complete → ${index - 1} threads created`);