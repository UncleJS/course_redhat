#!/usr/bin/env bun
// Fix broken intra-file anchors, then insert missing H2 TOC entries in doc order.
// Usage: bun tools/md_fix.js <repo-root> [--write]
import { readdirSync, readFileSync, writeFileSync, statSync } from "fs";
import { join } from "path";

const root = process.argv[2] || ".";
const WRITE = process.argv.includes("--write");
const SKIP = new Set(["QA-REPORT.md", "AGENTS.md", "LICENSE.md"]);

function* mdFiles(dir) {
  for (const e of readdirSync(dir)) {
    if (e === ".git" || e === "slides" || e === "__pycache__") continue;
    const p = join(dir, e);
    if (statSync(p).isDirectory()) yield* mdFiles(p);
    else if (e.endsWith(".md") && !SKIP.has(e)) yield p;
  }
}
function headingText(raw) {
  let t = raw.replace(/`/g, "");
  t = t.replace(/\[([^\]]*)\]\([^)]*\)/g, "$1");
  t = t.replace(/\*\*([^*]*)\*\*/g, "$1").replace(/\*([^*]*)\*/g, "$1");
  return t.trim();
}
function slugify(text, seen) {
  let s = Array.from(text.toLowerCase()).filter(ch => /[\p{L}\p{N} _-]/u.test(ch)).join("").replace(/ /g, "-");
  if (seen.has(s)) { const n = seen.get(s); seen.set(s, n + 1); s = `${s}-${n}`; }
  else seen.set(s, 1);
  return s;
}
const collapse = s => s.replace(/-+/g, "-");

let relinked = 0, inserted = 0, unmatched = 0;
for (const file of mdFiles(root)) {
  let lines = readFileSync(file, "utf8").split("\n");
  const rel = file.replace(root + "/", "");

  // --- collect headings outside fences ---
  function collectHeadings() {
    const seen = new Map(); const hs = []; const anchors = new Set();
    let fence = false;
    lines.forEach((line, i) => {
      if (/^```/.test(line)) { fence = !fence; return; }
      if (fence) return;
      const m = line.match(/^(#{1,6})\s+(.*)$/);
      if (m) hs.push({ level: m[1].length, raw: m[2].trim(), text: headingText(m[2]), slug: slugify(headingText(m[2]), seen), line: i });
      for (const a of line.matchAll(/<a\s+name="([^"]+)"/g)) anchors.add(a[1]);
    });
    return { hs, anchors };
  }

  // --- pass 1: rewrite broken link targets ---
  let { hs, anchors } = collectHeadings();
  const slugSet = new Set(hs.map(h => h.slug));
  let fence = false;
  lines = lines.map((line, i) => {
    if (/^```/.test(line)) { fence = !fence; return line; }
    if (fence) return line;
    return line.replace(/\]\(#([^)]+)\)/g, (whole, target) => {
      if (slugSet.has(target) || anchors.has(target)) return whole;
      const cands = hs.filter(h => collapse(h.slug) === collapse(target));
      if (cands.length === 1) { relinked++; return `](#${cands[0].slug})`; }
      console.log(`  UNMATCHED ${rel}:${i + 1} #${target} (${cands.length} candidates)`);
      unmatched++;
      return whole;
    });
  });

  // --- pass 2: insert missing H2 entries into the TOC ---
  ({ hs, anchors } = collectHeadings());
  const refd = new Set();
  for (const line of lines) for (const m of line.matchAll(/\]\(#([^)]+)\)/g)) refd.add(m[1]);
  const tocHead = hs.find(h => h.level === 2 && h.text.toLowerCase() === "table of contents");
  const missing = hs.filter(h => h.level === 2 && h.text.toLowerCase() !== "table of contents" && !refd.has(h.slug));
  if (missing.length && tocHead) {
    // TOC block: bullet lines following the TOC heading until first non-bullet/non-blank
    let tocStart = tocHead.line + 1;
    while (tocStart < lines.length && lines[tocStart].trim() === "") tocStart++;
    let tocEnd = tocStart;
    while (tocEnd < lines.length && /^\s*-\s+\[/.test(lines[tocEnd])) tocEnd++;
    // map existing TOC lines by slug target
    const tocLineOf = new Map();
    for (let i = tocStart; i < tocEnd; i++) {
      const m = lines[i].match(/\]\(#([^)]+)\)/);
      if (m) tocLineOf.set(m[1], i);
    }
    // insert in reverse doc order so indices stay valid
    const h2sInDoc = hs.filter(h => h.level === 2 && h.text.toLowerCase() !== "table of contents");
    for (const h of [...missing].sort((a, b) => b.line - a.line)) {
      // find previous H2 in doc order that has a TOC line
      const idx = h2sInDoc.findIndex(x => x.slug === h.slug);
      let insertAt = null;
      for (let j = idx - 1; j >= 0; j--) {
        const prev = tocLineOf.get(h2sInDoc[j].slug);
        if (prev !== undefined) {
          // skip that entry's indented sub-entries
          let k = prev + 1;
          while (k < tocEnd && /^\s+-\s+\[/.test(lines[k])) k++;
          insertAt = k; break;
        }
      }
      if (insertAt === null) insertAt = tocStart; // no prior entry -> top of TOC
      lines.splice(insertAt, 0, `- [${h.raw}](#${h.slug})`);
      tocEnd++;
      for (const [s, ln] of tocLineOf) if (ln >= insertAt) tocLineOf.set(s, ln + 1);
      tocLineOf.set(h.slug, insertAt);
      inserted++;
    }
  } else if (missing.length && !tocHead) {
    console.log(`  NO-TOC-SECTION ${rel}: ${missing.length} entries cannot be inserted`);
  }

  if (WRITE) writeFileSync(file, lines.join("\n"));
}
console.log(`\n${WRITE ? "APPLIED" : "DRY-RUN"}: ${relinked} links rewritten, ${inserted} TOC entries inserted, ${unmatched} unmatched`);
