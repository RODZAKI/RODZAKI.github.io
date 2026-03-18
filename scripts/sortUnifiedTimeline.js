const fs = require('fs');
const path = require('path');

const inputPath = path.join(__dirname, '../apex/canon/legacy-unified-timeline.json');
const outputPath = path.join(__dirname, '../apex/canon/legacy-timeline-sorted.json');

const data = JSON.parse(fs.readFileSync(inputPath, 'utf-8'));

const sorted = data.sort((a, b) => {
  return new Date(a.resolvedTime) - new Date(b.resolvedTime);
});

fs.writeFileSync(outputPath, JSON.stringify(sorted, null, 2));

console.log('Sorted timeline created → apex/canon/legacy-timeline-sorted.json');