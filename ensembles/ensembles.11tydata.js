const path = require("path");

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
  },
};
