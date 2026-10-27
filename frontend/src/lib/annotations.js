// Pure annotation logic for the case reader. No DOM, no React, so it can be tested in Node.
//
// A highlight is { id, para, start, end, quote, color, note }
//   para  : paragraph index in the judgment
//   start/end : character offsets inside that paragraph's text (end exclusive)
//   quote : the highlighted text, kept so we can re-anchor if the corpus text is rebuilt
//   color : one of COLORS
//   note  : optional free text

export const COLORS = ["yellow", "green", "blue", "pink"];
export const COLOR_LABELS = {
  yellow: "Yellow: key holding",
  green: "Green: facts / evidence",
  blue: "Blue: law / provision",
  pink: "Pink: doubt / to check",
};

let counter = 0;
export function newId() {
  counter += 1;
  return "h" + Date.now().toString(36) + counter.toString(36) + Math.random().toString(36).slice(2, 5);
}

/**
 * Add a highlight. Any existing highlight in the same paragraph that overlaps is trimmed
 * so highlights never overlap. Remnants keep colour; the note stays with the left remnant
 * (or the right one if there is no left remnant).
 */
export function addHighlight(list, h, paraText) {
  if (!(h.end > h.start) || h.start < 0 || h.end > paraText.length) return list;
  const fresh = {
    id: h.id || newId(),
    para: h.para,
    start: h.start,
    end: h.end,
    quote: paraText.slice(h.start, h.end),
    color: COLORS.includes(h.color) ? h.color : "yellow",
    note: h.note || "",
  };
  const out = [];
  for (const x of list) {
    if (x.para !== fresh.para || x.end <= fresh.start || x.start >= fresh.end) {
      out.push(x);
      continue;
    }
    const left = x.start < fresh.start ? mk(x, x.start, fresh.start, paraText, x.note) : null;
    const right = x.end > fresh.end ? mk(x, fresh.end, x.end, paraText, left ? "" : x.note) : null;
    if (left) out.push(left);
    if (right) out.push(right);
  }
  out.push(fresh);
  return sortHighlights(out);
}

function mk(x, start, end, text, note) {
  return { ...x, id: newId(), start, end, quote: text.slice(start, end), note: note || "" };
}

export function removeHighlight(list, id) {
  return list.filter((h) => h.id !== id);
}

export function updateHighlight(list, id, patch) {
  return list.map((h) => {
    if (h.id !== id) return h;
    const next = { ...h };
    if ("color" in patch && COLORS.includes(patch.color)) next.color = patch.color;
    if ("note" in patch) next.note = String(patch.note || "");
    return next;
  });
}

export function sortHighlights(list) {
  return [...list].sort((a, b) => a.para - b.para || a.start - b.start);
}

/**
 * Split one paragraph into consecutive segments that cover the whole text.
 * Each segment: { text, start, end, hl } where hl is the highlight or null.
 */
export function segmentsFor(text, hls) {
  const mine = [...hls].filter((h) => !h.orphan).sort((a, b) => a.start - b.start);
  const segs = [];
  let pos = 0;
  for (const h of mine) {
    const s = Math.max(h.start, pos);
    const e = Math.min(h.end, text.length);
    if (e <= s) continue;
    if (s > pos) segs.push({ text: text.slice(pos, s), start: pos, end: s, hl: null });
    segs.push({ text: text.slice(s, e), start: s, end: e, hl: h });
    pos = e;
  }
  if (pos < text.length) segs.push({ text: text.slice(pos), start: pos, end: text.length, hl: null });
  if (!segs.length) segs.push({ text: "", start: 0, end: 0, hl: null });
  return segs;
}

/**
 * Check saved highlights against the current paragraph texts. If the text has changed
 * (for example after the corpus was rebuilt), try to find the quote again. If it cannot
 * be found, the highlight is kept but flagged orphan so the user's notes are never lost.
 */
export function reanchor(list, paras) {
  return list.map((h) => {
    const t = paras[h.para];
    if (t !== undefined && t.slice(h.start, h.end) === h.quote) {
      return h.orphan ? { ...h, orphan: false } : h;
    }
    if (t !== undefined) {
      const i = t.indexOf(h.quote);
      if (i >= 0) return { ...h, start: i, end: i + h.quote.length, orphan: false };
    }
    for (let p = 0; p < paras.length; p++) {
      const i = paras[p].indexOf(h.quote);
      if (i >= 0 && h.quote.length >= 12) {
        return { ...h, para: p, start: i, end: i + h.quote.length, orphan: false };
      }
    }
    return { ...h, orphan: true };
  });
}

/** Highlights with notes get footnote numbers in document order. */
export function numberNotes(list) {
  const map = {};
  let n = 0;
  for (const h of sortHighlights(list)) {
    if (h.note && h.note.trim() && !h.orphan) {
      n += 1;
      map[h.id] = n;
    }
  }
  return map;
}

// ---------- Library (saved cases) ----------

const KEY = "s10.library.v1";
let memory = null;

function read() {
  try {
    const raw = window.localStorage.getItem(KEY);
    if (raw) {
      const v = JSON.parse(raw);
      if (v && typeof v === "object" && v.docs) return v;
    }
  } catch (_) {
    /* storage unavailable or corrupt: fall through */
  }
  return memory || { version: 1, docs: {} };
}

function write(lib) {
  memory = lib;
  try {
    window.localStorage.setItem(KEY, JSON.stringify(lib));
    return true;
  } catch (_) {
    return false;
  }
}

export function loadLibrary() {
  return read();
}

export function getEntry(docId) {
  return read().docs[String(docId)] || null;
}

export function saveEntry(docId, meta, highlights) {
  const lib = read();
  const id = String(docId);
  const prev = lib.docs[id] || {};
  lib.docs[id] = {
    docId: id,
    title: meta.title || prev.title || "Untitled",
    court: meta.court || prev.court || "",
    year: meta.year || prev.year || null,
    savedAt: prev.savedAt || new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    highlights: highlights || prev.highlights || [],
  };
  return write(lib) ? lib : null;
}

export function removeEntry(docId) {
  const lib = read();
  delete lib.docs[String(docId)];
  write(lib);
  return lib;
}

export function listEntries(lib = read()) {
  return Object.values(lib.docs).sort((a, b) => (b.updatedAt || "").localeCompare(a.updatedAt || ""));
}

// ---------- Export / import ----------

export function exportJSON(lib = read()) {
  return JSON.stringify({ ...lib, exportedAt: new Date().toISOString() }, null, 2);
}

/** Merge an exported library into the current one. Newer updatedAt wins per case. */
export function importJSON(text) {
  let incoming;
  try {
    incoming = JSON.parse(text);
  } catch (_) {
    return { ok: false, error: "That file is not valid JSON." };
  }
  if (!incoming || typeof incoming !== "object" || typeof incoming.docs !== "object") {
    return { ok: false, error: "That file does not look like a saved library." };
  }
  const lib = read();
  let added = 0;
  let updated = 0;
  for (const [id, e] of Object.entries(incoming.docs)) {
    if (!e || !Array.isArray(e.highlights)) continue;
    const clean = {
      docId: String(id),
      title: String(e.title || "Untitled"),
      court: String(e.court || ""),
      year: e.year || null,
      savedAt: e.savedAt || new Date().toISOString(),
      updatedAt: e.updatedAt || new Date().toISOString(),
      highlights: e.highlights
        .filter((h) => h && Number.isInteger(h.para) && Number.isInteger(h.start) && Number.isInteger(h.end))
        .map((h) => ({
          id: String(h.id || newId()),
          para: h.para,
          start: h.start,
          end: h.end,
          quote: String(h.quote || ""),
          color: COLORS.includes(h.color) ? h.color : "yellow",
          note: String(h.note || ""),
        })),
    };
    const cur = lib.docs[clean.docId];
    if (!cur) {
      lib.docs[clean.docId] = clean;
      added += 1;
    } else if ((clean.updatedAt || "") > (cur.updatedAt || "")) {
      lib.docs[clean.docId] = clean;
      updated += 1;
    }
  }
  write(lib);
  return { ok: true, added, updated };
}

export function toMarkdown(entry) {
  const lines = [];
  lines.push(`# ${entry.title}`);
  const meta = [entry.court, entry.year].filter(Boolean).join(", ");
  if (meta) lines.push(`*${meta}*`);
  lines.push(`Source: https://indiankanoon.org/doc/${entry.docId}/`, "");
  const hs = sortHighlights(entry.highlights || []);
  if (!hs.length) lines.push("_No highlights or notes._");
  for (const h of hs) {
    const label = COLOR_LABELS[h.color] || h.color;
    lines.push(`- [para ${h.para + 1}] (${label}) > ${h.quote.replace(/\s+/g, " ").trim()}`);
    if (h.note && h.note.trim()) lines.push(`  - Note: ${h.note.trim().replace(/\n+/g, " ")}`);
  }
  return lines.join("\n") + "\n";
}

export function libraryToMarkdown(lib = read()) {
  return listEntries(lib).map(toMarkdown).join("\n---\n\n");
}
