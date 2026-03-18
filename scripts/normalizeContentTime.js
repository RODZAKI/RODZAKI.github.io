const fs = require("fs");

const INPUT = "./legacy-content-timed.json";
const OUTPUT = "./legacy-content-normalized.json";

const MONTHS = {
  January: "01",
  February: "02",
  March: "03",
  April: "04",
  May: "05",
  June: "06",
  July: "07",
  August: "08",
  September: "09",
  October: "10",
  November: "11",
  December: "12"
};

function normalize(contentTime) {
  if (!contentTime) return null;

  const match = contentTime.match(
    /(\d{1,2}):(\d{2}).*?(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2})(?:st|nd|rd|th)(?:,\s*(\d{4}))?/i
  );

  if (!match) return null;

  let [_, hour, minute, month, day, year] = match;

  if (!year) year = "2026"; // fallback — adjust later if needed

  const mm = MONTHS[month];
  const dd = String(day).padStart(2, "0");
  const hh = String(hour).padStart(2, "0");

  return `${year}-${mm}-${dd}T${hh}:${minute}:00`;
}

function main() {
  const data = JSON.parse(fs.readFileSync(INPUT, "utf-8"));

  const enriched = data.map(entry => ({
    ...entry,
    contentTimeISO: normalize(entry.contentTime)
  }));

  fs.writeFileSync(OUTPUT, JSON.stringify(enriched, null, 2));

  console.log("✅ Normalization complete → legacy-content-normalized.json");
}

main();