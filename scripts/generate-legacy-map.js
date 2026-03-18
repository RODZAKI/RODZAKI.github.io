// generate-legacy-map.js

const fs = require('fs');
const path = require('path');

const LEGACY_DIR = path.join(__dirname, '../threads-legacy');
const OUTPUT_DIR = path.join(__dirname, '../apex/canon');
const OUTPUT_FILE = path.join(OUTPUT_DIR, 'legacy-order-map.json');

function getPdfFiles(dir) {
  return fs.readdirSync(dir)
    .filter(file => file.toLowerCase().endsWith('.pdf'));
}

function buildMap(files) {
  return files.map((file, index) => {
    return {
      temp_id: `legacy-${String(index + 1).padStart(3, '0')}`,
      filename: file,
      path: `/threads-legacy/${file}`
    };
  });
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

  console.log(`✅ Generated legacy-order-map.json with ${files.length} entries`);
}

main();