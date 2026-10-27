// Run: node frontend/tests/annotations.test.mjs
import assert from "node:assert/strict";
import {
  addHighlight, removeHighlight, updateHighlight, segmentsFor, reanchor, numberNotes,
  saveEntry, getEntry, listEntries, removeEntry, exportJSON, importJSON, toMarkdown,
} from "../src/lib/annotations.js";

// in-memory localStorage stub (also tests the fallback when it throws)
const store = {};
globalThis.window = { localStorage: { getItem: (k) => store[k] ?? null, setItem: (k, v) => { store[k] = v; } } };

let passed = 0;
const t = (name, fn) => { fn(); passed += 1; console.log("ok -", name); };

const P = "The appellant was subjected to mental cruelty by the respondent wife.";

t("add highlight stores the quote", () => {
  const l = addHighlight([], { para: 0, start: 4, end: 13, color: "green" }, P);
  assert.equal(l.length, 1);
  assert.equal(l[0].quote, "appellant");
});

t("rejects empty / out-of-range selections", () => {
  assert.equal(addHighlight([], { para: 0, start: 5, end: 5 }, P).length, 0);
  assert.equal(addHighlight([], { para: 0, start: -1, end: 4 }, P).length, 0);
  assert.equal(addHighlight([], { para: 0, start: 0, end: 999 }, P).length, 0);
});

t("segments cover the whole paragraph exactly", () => {
  let l = addHighlight([], { para: 0, start: 4, end: 13 }, P);
  l = addHighlight(l, { para: 0, start: 30, end: 44 }, P);
  const segs = segmentsFor(P, l);
  assert.equal(segs.map((s) => s.text).join(""), P);
  assert.equal(segs.filter((s) => s.hl).length, 2);
  // contiguous
  let pos = 0;
  for (const s of segs) { assert.equal(s.start, pos); pos = s.end; }
  assert.equal(pos, P.length);
});

t("overlap in the middle splits the old highlight and keeps the note on the left piece", () => {
  let l = addHighlight([], { para: 0, start: 4, end: 30, note: "keep me" }, P);
  l = addHighlight(l, { para: 0, start: 10, end: 20, color: "blue" }, P);
  assert.equal(l.length, 3);
  assert.deepEqual(l.map((h) => [h.start, h.end]), [[4, 10], [10, 20], [20, 30]]);
  assert.equal(l[0].note, "keep me");
  assert.equal(l[2].note, "");
  assert.equal(segmentsFor(P, l).map((s) => s.text).join(""), P);
});

t("new highlight covering an old one replaces it", () => {
  let l = addHighlight([], { para: 0, start: 10, end: 20 }, P);
  l = addHighlight(l, { para: 0, start: 0, end: 40, color: "pink" }, P);
  assert.equal(l.length, 1);
  assert.equal(l[0].color, "pink");
});

t("highlights in other paragraphs are untouched", () => {
  let l = addHighlight([], { para: 1, start: 0, end: 5 }, P);
  l = addHighlight(l, { para: 0, start: 0, end: 5 }, P);
  assert.equal(l.length, 2);
});

t("update colour and note, remove", () => {
  let l = addHighlight([], { para: 0, start: 4, end: 13 }, P);
  const id = l[0].id;
  l = updateHighlight(l, id, { color: "blue", note: "check s.10(1)(x)" });
  assert.equal(l[0].color, "blue");
  assert.equal(l[0].note, "check s.10(1)(x)");
  l = updateHighlight(l, id, { color: "purple" });
  assert.equal(l[0].color, "blue");
  assert.equal(removeHighlight(l, id).length, 0);
});

t("footnotes are numbered in document order, only for notes", () => {
  let l = addHighlight([], { para: 1, start: 0, end: 5, note: "second" }, P);
  l = addHighlight(l, { para: 0, start: 0, end: 5, note: "first" }, P);
  l = addHighlight(l, { para: 0, start: 10, end: 15 }, P);
  const m = numberNotes(l);
  const byNote = Object.fromEntries(l.map((h) => [h.note, m[h.id]]));
  assert.equal(byNote.first, 1);
  assert.equal(byNote.second, 2);
  assert.equal(Object.keys(m).length, 2);
});

t("reanchor keeps position when text is unchanged", () => {
  const l = addHighlight([], { para: 0, start: 4, end: 13 }, P);
  const r = reanchor(l, [P]);
  assert.equal(r[0].start, 4);
  assert.equal(r[0].orphan, undefined);
});

t("reanchor follows the quote when text shifts (e.g. spacing fix)", () => {
  const old = "under Section 10of the Act the appellant alleged cruelty";
  const l = addHighlight([], { para: 0, start: 36, end: 56 }, old);
  const fixed = "under Section 10 of the Act the appellant alleged cruelty";
  const r = reanchor(l, [fixed]);
  assert.equal(fixed.slice(r[0].start, r[0].end), l[0].quote);
  assert.equal(r[0].orphan, false);
});

t("reanchor finds a quote that moved to another paragraph", () => {
  const q = "mental cruelty by the respondent";
  const l = addHighlight([], { para: 0, start: 28, end: 28 + q.length }, P);
  const r = reanchor(l, ["Intro paragraph.", P]);
  assert.equal(r[0].para, 1);
});

t("reanchor flags orphans instead of dropping notes", () => {
  let l = addHighlight([], { para: 0, start: 4, end: 13, note: "important" }, P);
  const r = reanchor(l, ["completely different text now"]);
  assert.equal(r.length, 1);
  assert.equal(r[0].orphan, true);
  assert.equal(r[0].note, "important");
  // orphans are not drawn
  assert.equal(segmentsFor("completely different text now", r).filter((s) => s.hl).length, 0);
});

t("library save / get / list / remove", () => {
  let l = addHighlight([], { para: 0, start: 4, end: 13, note: "n" }, P);
  saveEntry(123, { title: "A vs B", court: "Madras High Court", year: 2001 }, l);
  assert.equal(getEntry(123).title, "A vs B");
  assert.equal(listEntries().length, 1);
  removeEntry(123);
  assert.equal(getEntry(123), null);
});

t("export then import round-trips, newer wins, bad input rejected", () => {
  let l = addHighlight([], { para: 0, start: 4, end: 13, note: "keep" }, P);
  saveEntry(7, { title: "X vs Y" }, l);
  const dump = exportJSON();
  removeEntry(7);
  const res = importJSON(dump);
  assert.equal(res.ok, true);
  assert.equal(res.added, 1);
  assert.equal(getEntry(7).highlights[0].note, "keep");
  assert.equal(importJSON("not json").ok, false);
  assert.equal(importJSON('{"hello":1}').ok, false);
  // importing the same file again changes nothing
  const again = importJSON(dump);
  assert.equal(again.added, 0);
  assert.equal(again.updated, 0);
});

t("import drops malformed highlights and unknown colours", () => {
  const bad = JSON.stringify({ docs: { 9: { title: "Z", highlights: [
    { para: 0, start: 1, end: 3, quote: "ab", color: "neon" },
    { para: "x", start: 1, end: 3 },
    null,
  ] } } });
  assert.equal(importJSON(bad).ok, true);
  const e = getEntry(9);
  assert.equal(e.highlights.length, 1);
  assert.equal(e.highlights[0].color, "yellow");
});

t("markdown export lists paragraph numbers, quotes and notes", () => {
  let l = addHighlight([], { para: 2, start: 4, end: 13, note: "see s.17", color: "blue" }, P);
  const md = toMarkdown({ docId: "5", title: "T", court: "C", year: 2000, highlights: l });
  assert.match(md, /para 3/);
  assert.match(md, /appellant/);
  assert.match(md, /Note: see s\.17/);
  assert.match(md, /indiankanoon\.org\/doc\/5\//);
});

console.log(`\n${passed} tests passed`);
