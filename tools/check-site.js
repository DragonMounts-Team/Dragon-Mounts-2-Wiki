const { execFileSync, spawnSync } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const errors = [];
const trackedHtml = execFileSync("git", ["ls-files", "--", "*.html"], {
  cwd: root,
  encoding: "utf8"
}).trim().split(/\r?\n/).filter(Boolean);
const pages = new Map();

function fail(message) {
  errors.push(message);
}

function hasExactPath(relativePath) {
  let current = root;
  for (const part of relativePath.split(/[\\/]/).filter(Boolean)) {
    let entries;
    try {
      entries = fs.readdirSync(current);
    } catch {
      return false;
    }
    if (!entries.includes(part)) return false;
    current = path.join(current, part);
  }
  return fs.existsSync(current);
}

for (const file of trackedHtml) {
  const contents = fs.readFileSync(path.join(root, file), "utf8");
  pages.set(file, contents);
  const ids = [...contents.matchAll(/\b(?:id|name)="([^"]+)"/g)].map(match => match[1]);
  const duplicates = new Set(ids.filter((id, index) => ids.indexOf(id) !== index));
  for (const id of duplicates) fail(`${file}: duplicate anchor "${id}"`);
}

if (!pages.has("index.html")) fail("GitHub Pages root is missing index.html");
else {
  const home = pages.get("index.html");
  if (!/<title>DragonMounts 2 Wiki<\/title>/.test(home)) {
    fail("index.html must be the edition-selection homepage");
  }
  for (const id of ["edition-picker", "select-bedrock", "select-java", "bedrock-content"]) {
    if (!home.includes(`id="${id}"`)) fail(`index.html is missing the edition control "${id}"`);
  }
}
if (!fs.existsSync(path.join(root, ".nojekyll"))) fail("GitHub Pages root is missing .nojekyll");

for (const [file, contents] of pages) {
  for (const match of contents.matchAll(/(?:href|src)="([^"]+)"/g)) {
    const reference = match[1].replaceAll("&amp;", "&");
    if (/^(?:https?:|mailto:|tel:|data:|javascript:|\/\/)/i.test(reference)) continue;
    if (reference.startsWith("/")) {
      fail(`${file}: root-relative path "${reference}" will break under a GitHub project Pages URL`);
      continue;
    }

    let url;
    try {
      url = new URL(reference, `https://pages.invalid/${file}`);
    } catch {
      fail(`${file}: invalid local URL "${reference}"`);
      continue;
    }
    const target = decodeURIComponent(url.pathname.replace(/^\/+/, ""));
    if (!target) continue;
    const absoluteTarget = path.resolve(root, target);
    if (!absoluteTarget.startsWith(root + path.sep) || !hasExactPath(target)) {
      fail(`${file}: missing or case-mismatched local path "${reference}"`);
      continue;
    }
    if (url.hash && pages.has(target)) {
      const destination = pages.get(target);
      const anchors = new Set([...destination.matchAll(/\b(?:id|name)="([^"]+)"/g)].map(item => item[1]));
      const fragment = decodeURIComponent(url.hash.slice(1));
      if (!anchors.has(fragment)) fail(`${file}: missing anchor "${reference}"`);
    }
  }
}

for (const file of ["assets/app.js", "assets/config.js", "assets/data.js"]) {
  const result = spawnSync(process.execPath, ["--check", path.join(root, file)], { encoding: "utf8" });
  if (result.status !== 0) fail(`${file}: JavaScript syntax check failed\n${result.stderr || result.stdout}`);
}

if (errors.length) {
  console.error(errors.map(error => `- ${error}`).join("\n"));
  process.exitCode = 1;
} else {
  console.log(`Site check passed: ${trackedHtml.length} HTML pages, local paths, anchors, and JavaScript syntax.`);
}
