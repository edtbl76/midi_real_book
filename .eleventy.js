const markdownIt = require("markdown-it");
const markdownItAnchor = require("markdown-it-anchor");
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

module.exports = function (eleventyConfig) {
  const anchorSlugify = (str) =>
    str.toLowerCase()
      .replace(/[:\s]+/g, "-")
      .replace(/[^a-z0-9-]/g, "")
      .replace(/-+/g, "-")
      .replace(/^-|-$/g, "");

  const md = markdownIt({ html: true, linkify: true }).use(markdownItAnchor, {
    slugify: anchorSlugify,
  });
  eleventyConfig.setLibrary("md", md);

  // Extract h1/h2 headings from rendered HTML for sidebar nav
  eleventyConfig.addFilter("navItems", function (content) {
    const items = [];
    const re = /<h([12])[^>]*\bid="([^"]*)"[^>]*>([\s\S]*?)<\/h\1>/g;
    let m;
    while ((m = re.exec(content)) !== null) {
      const level = m[1];
      const id = m[2];
      const text = m[3].replace(/<[^>]+>/g, "").trim();
      items.push(`<li class="level-${level}"><a href="#${id}">${text}</a></li>`);
    }
    return items.join("\n          ");
  });

  // Sort a collection by ensembleName, case-insensitive
  eleventyConfig.addFilter("sortByName", function (collection) {
    return [...collection].sort((a, b) =>
      a.data.ensembleName.localeCompare(b.data.ensembleName, undefined, {
        sensitivity: "base",
      })
    );
  });

  eleventyConfig.addGlobalData("slugify", () => slugify);

  return {
    dir: {
      input: ".",
      output: "public",
      includes: "_includes",
      data: "_data",
    },
    markdownTemplateEngine: false,
    htmlTemplateEngine: "njk",
  };
};
