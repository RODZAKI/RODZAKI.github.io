// extract-legacy-dates.js

const fs = require('fs');
const path = require('path');
const pdf = require('pdf-parse');

const LEGACY_DIR = path.join(__dirname, '../threads-legacy');
const OUTPUT_FILE = path.join(__dirname, '../apex/canon/legacy-content-map.json');

function getPdfFiles(dir) {
  return fs.readdirSync(dir)
    .filter(file => file.toLowerCase().endsWith('.pdf'));
}

function extractDate(text) {
  // basic patterns (we will refine later)
  const patterns = [
    /\b\d{4}-\d{2}-\d{2}\b/,                // 2026-03-17
    /\b\d{1,2}\/\d{1,2}\/\d{2,4}\b/,        // 3/17/2026
    /\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b/i,
    /\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b/i
  ];

  for (let pattern of patterns) {
    const match = text.match(pattern);
    if (match) return match[0];
  }

  return null;
}

async function processFile(file) {
  const fullPath = path.join(LEGACY_DIR, file);
  const dataBuffer = fs.readFileSync(fullPath);

  try {
    const data = await pdf(dataBuffer);
    const text = data.text;

    const extractedDate = extractDate(text);

    return {
      filename: file,
      path: `/threads-legacy/${file}`,
      extractedDate,
      preview: text.slice(0, 200).replace(/\s+/g, ' ')
    };

  } catch (err) {
    return {
      filename: file,
      error: true,
      message: err.message
    };
  }
}

async function main() {
  const files = getPdfFiles(LEGACY_DIR);

  const results = [];

  for (let file of files) {
    console.log(`Processing: ${file}`);
    const result = await processFile(file);
    results.push(result);
  }

  fs.writeFileSync(
    OUTPUT_FILE,
    JSON.stringify(results, null, 2)
  );

  console.log(`\n✅ Extracted content data for ${files.length} files`);
}

main();