const fs = require('fs');
const path = require('path');

const orderMapPath = path.join(__dirname, '../apex/canon/legacy-order-map.json');
const contentMapPath = path.join(__dirname, '../apex/canon/legacy-content-normalized.json');
const outputPath = path.join(__dirname, '../apex/canon/legacy-unified-timeline.json');

const orderMap = JSON.parse(fs.readFileSync(orderMapPath, 'utf-8'));
const contentMap = JSON.parse(fs.readFileSync(contentMapPath, 'utf-8'));

const contentLookup = {};
contentMap.forEach(item => {
  contentLookup[item.filename] = item;
});

const unified = orderMap.map(entry => {
  const content = contentLookup[entry.filename];

  return {
    filename: entry.filename,
    path: entry.path,
    orderIndex: entry.orderIndex,

    primaryTime: entry.primaryTime,

    contentTime: content ? content.contentTime : null,
    contentTimeISO: content ? content.contentTimeISO : null,

    resolvedTime: content?.contentTimeISO || new Date(entry.primaryTime).toISOString()
  };
});

fs.writeFileSync(outputPath, JSON.stringify(unified, null, 2));

console.log('Unified timeline created → apex/canon/legacy-unified-timeline.json');