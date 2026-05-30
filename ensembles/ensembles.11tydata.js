const path = require("path");
const fs = require("fs");

function slugify(name) {
  return name
    .toLowerCase()
    .replace(/\s*-\s*/g, "-")
    .replace(/&/g, "and")
    .replace(/'/g, "-")
    .replace(/\./g, "-")
    .replace(/\s+/g, "-")
    .replace(/[^a-z0-9-]/g, "")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "");
}

module.exports = {
  layout: "ensemble",
  tags: ["ensemble"],
  eleventyComputed: {
    ensembleName: (data) => path.basename(path.dirname(data.page.inputPath)),
    permalink: (data) => {
      const dir = path.basename(path.dirname(data.page.inputPath));
      return `ensembles/${slugify(dir)}.html`;
    },
    players: (data) => {
      const md = fs.readFileSync(data.page.inputPath, "utf-8");
      const system = new Set(["context", "players", "references"]);
      return (md.match(/^## (.+)$/gm) || [])
        .map((m) => m.replace(/^## /, "").trim())
        .filter((n) => !system.has(n.toLowerCase()));
    },
  },
};
