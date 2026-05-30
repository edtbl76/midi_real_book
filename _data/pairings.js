const fs = require("fs");
const path = require("path");

const PAIRINGS = path.resolve(__dirname, "../Work/etude_pairings.md");

module.exports = function () {
  const text = fs.readFileSync(PAIRINGS, "utf-8");
  const map = {};

  for (const m of text.matchAll(/^\|\s*\d+\s*\|(.+)$/gm)) {
    const fields = m[1].split("|").map((f) => f.trim());
    if (fields.length < 11) continue;

    const bassist = fields[0];
    const guitarists = [fields[1], fields[2], fields[3], fields[4]].filter(
      (g) => g && g !== "—"
    );
    const bandInfluence = fields[10] || "";

    for (const guitarist of guitarists) {
      map[`${bassist}|${guitarist}`] = bandInfluence;
    }
  }

  return map;
};
