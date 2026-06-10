#!/usr/bin/env bun
// Audit intra-file anchors + per-file TOC completeness for the course repo.
// Usage: bun tools/md_audit.js <repo-root>
import { readdirSync, readFileSync, statSync } from "fs";
import { join } from "path";

const root = process.argv[2] || ".";
const SKIP = new Set(["QA-REPORT.md", "AGENTS.md", "LICENSE.md"]);

function* mdFiles(dir) {
  for (const e of readdirSync(dir)) {
    if (e === ".git" || e === "slides" || e === "__pycache__") continue;
    const p = join(dir, e);
    const st = statSync(p);
    if (st.isDirectory()) yield* mdFiles(p);
    else if (e.endsWith(".md") && !SKIP.has(e)) yield p;
  }
}

// GitHub slugger: strip md formatting, lowercase, keep [letters numbers space - _], spaces->hyphens, dedup with -n
function headingText(raw) {
  let t = raw.replace(/`/g, "");                 // inline code markers
  t = t.replace(/\[([^\]]*)\]\([^)]*\)/g, "$1"); // links -> text
  t = t.replace(/\*\*([^*]*)\*\*/g, "$1").replace(/\*([^*]*)\*/g, "$1");
  return t.trim();
}
function slugify(text, seen) {
  let s = text.toLowerCase();
  s = Array.from(s).filter(ch => /[\p{L}\p{N} _-]/u.test(ch)).join("");
  s = s.replace(/ /g, "-");
  if (seen.has(s)) {
    const n = seen.get(s);
    seen.set(s, n + 1);
    s = `${s}-${n}`;
  } else {
    seen.set(s, 1);
  }
  return s;
}

let brokenTotal = 0, tocMissingTotal = 0, filesWithIssues = 0;
for (const file of mdFiles(root)) {
  const lines = readFileSync(file, "utf8").split("\n");
  const seen = new Map();
  const slugs = new Set();
  const h2s = [];          // {text, slug, line} outside fences
  const anchors = new Set(); // explicit <a name="...">
  let fence = false;

  lines.forEach((line, i) => {
    if (/^```/.test(line)) { fence = !fence; return; }
    if (fence) return;
    const m = line.match(/^(#{1,6})\s+(.*)$/);
    if (m) {
      const text = headingText(m[2]);
      const slug = slugify(text, seen);
      slugs.add(slug);
      if (m[1].length === 2) h2s.push({ text, slug, line: i + 1 });
    }
    for (const a of line.matchAll(/<a\s+name="([^"]+)"/g)) anchors.add(a[1]);
  });

  // pass 2: links
  fence = false;
  const broken = [];
  lines.forEach((line, i) => {
    if (/^```/.test(line)) { fence = !fence; return; }
    if (fence) return;
    for (const m of line.matchAll(/\]\(#([^)]+)\)/g)) {
      const target = m[1];
      if (!slugs.has(target) && !anchors.has(target)) broken.push({ line: i + 1, target });
    }
  });

  // TOC completeness: H2s (except "Table of contents") whose slug is never referenced
  const refd = new Set();
  for (const line of lines) for (const m of line.matchAll(/\]\(#([^)]+)\)/g)) refd.add(m[1]);
  const missing = h2s.filter(h => h.text.toLowerCase() !== "table of contents" && !refd.has(h.slug));

  if (broken.length || missing.length) {
    filesWithIssues++;
    console.log(`\n== ${file.replace(root + "/", "")}`);
    for (const b of broken) { console.log(`  BROKEN  L${b.line}: #${b.target}`); brokenTotal++; }
    for (const h of missing) { console.log(`  NO-TOC  L${h.line}: ## ${h.text}  ->  #${h.slug}`); tocMissingTotal++; }
  }
}
console.log(`\nTOTAL: ${brokenTotal} broken links, ${tocMissingTotal} H2s missing from TOC, ${filesWithIssues} files with issues`);
