// generate-legacy-map.js (v2 — chronology aware)

const fs = require('fs');
const path = require('path');

const LEGACY_DIR = path.join(__dirname, '../threads-legacy');
const OUTPUT_DIR = path.join(__dirname, '../apex/canon');
const OUTPUT_FILE = path.join(OUTPUT_DIR, 'legacy-order-map.json');

function getPdfFiles(dir) {
  return fs.readdirSync(dir)
    .filter(file => file.toLowerCase().endsWith('.pdf'));
}

function getFileTimestamps(filePath) {
  const stats = fs.statSync(filePath);

  const created = stats.birthtimeMs || stats.ctimeMs;
  const modified = stats.mtimeMs;

  const primary = Math.min(created, modified);

  return {
    created,
    modified,
    primary
  };
}

function buildMap(files) {
  const enriched = files.map(file => {
    const fullPath = path.join(LEGACY_DIR, file);
    const time = getFileTimestamps(fullPath);

    return {
      filename: file,
      path: `/threads-legacy/${file}`,
      created: time.created,
      modified: time.modified,
      primaryTime: time.primary
    };
  });

  // SORT: oldest → newest
  enriched.sort((a, b) => a.primaryTime - b.primaryTime);

  // ASSIGN ORDERED IDS
  return enriched.map((entry, index) => ({
    temp_id: `legacy-${String(index + 1).padStart(3, '0')}`,
    ...entry
  }));
}

function main() {
  if (!fs.existsSync(LEGACY_DIR)) {
    console.error('❌ threads-legacy folder not found');
    process.exit(1);
  }

  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  const files = getPdfFiles(LEGACY_DIR);

  if (files.length === 0) {
    console.warn('⚠️ No PDF files found in threads-legacy');
  }

  const map = buildMap(files);

  fs.writeFileSync(
    OUTPUT_FILE,
    JSON.stringify(map, null, 2)
  );

  console.log(`✅ Chronological map generated with ${files.length} entries`);
}

main();