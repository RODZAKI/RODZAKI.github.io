const fs = require("fs");
const path = require("path");
const Ajv = require("ajv");

const ajv = new Ajv({ allErrors: true, strict: false });

const schemaPath = path.join(__dirname, "../canon/thread.schema.json");
const dataPath = path.join(__dirname, "../canon/threads.json");

const schema = JSON.parse(fs.readFileSync(schemaPath, "utf8"));
const data = JSON.parse(fs.readFileSync(dataPath, "utf8"));

const validate = ajv.compile(schema);
const valid = validate(data);

if (!valid) {
  console.error("❌ Schema validation failed:");
  console.error(validate.errors);
  process.exit(1);
}

console.log("✅ Validation passed.");