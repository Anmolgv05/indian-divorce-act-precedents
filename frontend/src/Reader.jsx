import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import SiteNav from "./SiteNav.jsx";
import {
  COLORS, COLOR_LABELS, newId, addHighlight, removeHighlight, updateHighlight,
  segmentsFor, reanchor, numberNotes, sortHighlights, getEntry, saveEntry, removeEntry, toMarkdown,
} from "./lib/annotations.js";
import { download, safeName, printWithTitle } from "./lib/download.js";
import "./reader.css";

// Where in the paragraph a DOM selection boundary sits.
function locate(node, offset) {
  const base = node.nodeType === 3 ? node.parentElement : node;
  const el = base && base.closest ? base.closest("[data-start]") : null;
  if (!el) return null;
  const p = el.closest("[data-para]");
  if (!p) return null;
  const within = node.nodeType === 3 ? offset : offset > 0 ? el.textContent.length : 0;
  return { para: Number(p.dataset.para), pos: Number(el.dataset.start) + within };
}

export default function Reader({ docId }) {
  const [load, setLoad] = useState({ status: "loading" });
  const [hls, setHls] = useState([]);
  const [saved, setSaved] = useState(false);
  const [color, setColor] = useState("yellow");
  const [sel, setSel] = useState(null);
  const [focusId, setFocusId] = useState(null);
  const [notice, setNotice] = useState("");
  const articleRef = useRef(null);

  // ----- load text + saved annotations -----
  useEffect(() => {
    let live = true;
    setLoad({ status: "loading" });
    fetch(`/api/cases/${encodeURIComponent(docId)}/text`)
      .then(async (r) => {
        if (r.status === 404) throw new Error("off");
        if (!r.ok) throw new Error("fail");
        return r.json();
      })
      .then((d) => {
        if (!live) return;
        const entry = getEntry(docId);
        setHls(entry ? reanchor(entry.highlights, d.paragraphs) : []);
        setSaved(!!entry);
        setLoad({ status: "ok", data: d });
      })
      .catch((e) => {
        // Fallback directly to Hugging Face Hub dataset if server is off or file is un-cached
        fetch(`https://huggingface.co/datasets/AnmolGV/section10-divorce-corpus/raw/main/parsed/${encodeURIComponent(docId)}.json`)
          .then(async (r) => {
            if (!r.ok) throw new Error("hf_fail");
            return r.json();
          })
          .then((hfData) => {
            if (!live) return;
            const paras = (hfData.paragraphs || []).map((p) => String(p.text || "").trim()).filter(Boolean);
            const formatted = {
              doc_id: docId,
              title: hfData.title || "Untitled",
              court: hfData.court || "",
              year: hfData.year,
              source_url: `https://indiankanoon.org/doc/${docId}/`,
              hf_url: `https://huggingface.co/datasets/AnmolGV/section10-divorce-corpus/blob/main/parsed/${docId}.json`,
              source: "huggingface",
              paragraphs: paras,
            };
            const entry = getEntry(docId);
            setHls(entry ? reanchor(entry.highlights, formatted.paragraphs) : []);
            setSaved(!!entry);
            setLoad({ status: "ok", data: formatted });
          })
          .catch(() => {
            if (live) setLoad({ status: e.message === "off" ? "off" : "error" });
          });
      });
    return () => { live = false; };
  }, [docId]);

  const data = load.data;
  const paras = data ? data.paragraphs : [];

  const persist = useCallback((next) => {
    setHls(next);
    if (!data) return;
    const ok = saveEntry(docId, { title: data.title, court: data.court, year: data.year }, next);
    setSaved(true);
    setNotice(ok ? "" : "Your browser is blocking storage, so these notes will be lost when you close the tab. Use Export notes to keep them.");
  }, [data, docId]);

  // ----- track the text selection -----
  useEffect(() => {
    const onSel = () => {
      const s = window.getSelection();
      const root = articleRef.current;
      if (!s || s.isCollapsed || s.rangeCount === 0 || !root || !root.contains(s.anchorNode)) {
        setSel(null);
        return;
      }
      const r = s.getRangeAt(0);
      const a = locate(r.startContainer, r.startOffset);
      const b = locate(r.endContainer, r.endOffset);
      if (!a || !b) { setSel(null); return; }
      if (a.para !== b.para) { setSel({ multi: true }); return; }
      if (b.pos <= a.pos) { setSel(null); return; }
      setSel({ para: a.para, start: a.pos, end: b.pos, multi: false });
    };
    document.addEventListener("selectionchange", onSel);
    return () => document.removeEventListener("selectionchange", onSel);
  }, []);

  const byPara = useMemo(() => {
    const m = {};
    for (const h of hls) (m[h.para] = m[h.para] || []).push(h);
    return m;
  }, [hls]);
  const fnMap = useMemo(() => numberNotes(hls), [hls]);
  const ordered = useMemo(() => sortHighlights(hls), [hls]);
  const notes = ordered.filter((h) => fnMap[h.id]);

  // ----- actions -----
  const highlight = (withNote) => {
    if (!sel || sel.multi) return;
    const id = newId();
    const next = addHighlight(hls, { id, para: sel.para, start: sel.start, end: sel.end, color }, paras[sel.para]);
    if (next === hls) return;
    persist(next);
    window.getSelection().removeAllRanges();
    setSel(null);
    if (withNote) setFocusId(id);
  };

  const jump = (id) => {
    const el = articleRef.current && articleRef.current.querySelector(`[data-hid="${id}"]`);
    if (el) {
      el.scrollIntoView({ block: "center", behavior: "smooth" });
      el.classList.add("flash");
      setTimeout(() => el.classList.remove("flash"), 1400);
    }
  };

  const onArticleActivate = (e) => {
    if (e.type === "keydown" && e.key !== "Enter") return;
    const m = e.target.closest && e.target.closest("[data-hid]");
    if (m) setFocusId(m.dataset.hid);
  };

  useEffect(() => {
    if (!focusId) return;
    const li = document.getElementById(`ann-${focusId}`);
    if (li) {
      li.scrollIntoView({ block: "nearest" });
      const ta = li.querySelector("textarea");
      if (ta) ta.focus();
    }
  }, [focusId]);

  const toggleSaved = () => {
    if (saved) {
      if (hls.length && !window.confirm("Remove this case and its highlights and notes from your library?")) return;
      removeEntry(docId);
      setHls([]);
      setSaved(false);
    } else {
      persist(hls);
    }
  };

  const entryForExport = () => ({
    docId, title: data.title, court: data.court, year: data.year, highlights: hls,
  });

  // ----- states without text -----
  if (load.status !== "ok") {
    return (
      <>
        <div className="no-print"><SiteNav /></div>
        <main id="main" className="rd-state">
          {load.status === "loading" && <p role="status">Loading the judgment…</p>}
          {load.status === "off" && (
            <>
              <h1>Reading in the site is switched off</h1>
              <p>This server is not showing full judgment text. You can read the original on Indian Kanoon.</p>
              <p><a href={`https://indiankanoon.org/doc/${encodeURIComponent(docId)}/`} target="_blank" rel="noopener noreferrer">Open on Indian Kanoon</a> · <a href="#/cases">Back to all cases</a></p>
            </>
          )}
          {load.status === "error" && (
            <>
              <h1>Could not load this case</h1>
              <p>Something went wrong while fetching the text. <a href="#/cases">Back to all cases</a></p>
            </>
          )}
        </main>
      </>
    );
  }

  const today = new Date().toLocaleDateString("en-IN", { day: "numeric", month: "long", year: "numeric" });

  return (
    <>
      <div className="no-print"><SiteNav /></div>
      <main id="main" className="rd">
        <div className="rd-toolbar no-print" role="toolbar" aria-label="Highlight and note tools">
          <div className="rd-colors" role="group" aria-label="Highlight colour">
            {COLORS.map((c) => (
              <button
                key={c}
                type="button"
                className={`rd-swatch hl-${c}`}
                aria-pressed={color === c}
                aria-label={COLOR_LABELS[c]}
                title={COLOR_LABELS[c]}
                onMouseDown={(e) => e.preventDefault()}
                onClick={() => setColor(c)}
              />
            ))}
          </div>
          <button type="button" className="rd-btn rd-primary" disabled={!sel || sel.multi}
            onMouseDown={(e) => e.preventDefault()} onClick={() => highlight(false)}>Highlight</button>
          <button type="button" className="rd-btn" disabled={!sel || sel.multi}
            onMouseDown={(e) => e.preventDefault()} onClick={() => highlight(true)}>Highlight + note</button>
          <span className="rd-hint" role="status">
            {sel && sel.multi ? "Select within one paragraph." : sel ? "Passage selected." : "Select text in the judgment to mark it."}
          </span>
          <span className="rd-spacer" />
          <button type="button" className="rd-btn" onClick={toggleSaved}>{saved ? "Saved in library ✓" : "Save to library"}</button>
          <button type="button" className="rd-btn" onClick={() => download(`${safeName(data.title)}-notes.md`, toMarkdown(entryForExport()), "text/markdown")}>Export notes</button>
          <button type="button" className="rd-btn" onClick={() => printWithTitle(data.title)}>Save as PDF</button>
          <a className="rd-btn rd-link" href="#/library">My library</a>
        </div>

        {notice && <p className="rd-notice no-print" role="alert">{notice}</p>}

        <div className="rd-wrap">
          <article className="rd-paper" ref={articleRef} onClick={onArticleActivate} onKeyDown={onArticleActivate}>
            <header className="rd-title">
              {data.court && <p className="rd-court">{data.court}</p>}
              <h1>{data.title}</h1>
              <p className="rd-meta">{[data.year, `Indian Kanoon doc ${data.doc_id}`].filter(Boolean).join("  ·  ")}</p>
              <div className="rd-rule" aria-hidden="true" />
            </header>

            {paras.map((t, i) => (
              <p key={i} data-para={i} className={i === 0 ? "rd-p first" : "rd-p"}>
                <span className="rd-num" aria-hidden="true">{i + 1}</span>
                {segmentsFor(t, byPara[i] || []).map((s, j) =>
                  s.hl ? (
                    <span key={j}>
                      <mark
                        data-start={s.start}
                        data-hid={s.hl.id}
                        className={`hl hl-${s.hl.color}`}
                        tabIndex={0}
                        title={s.hl.note || COLOR_LABELS[s.hl.color]}
                      >{s.text}</mark>
                      {fnMap[s.hl.id] && s.end === s.hl.end && <sup className="fn">{fnMap[s.hl.id]}</sup>}
                    </span>
                  ) : (
                    <span key={j} data-start={s.start}>{s.text}</span>
                  )
                )}
              </p>
            ))}

            <footer className="rd-foot">
              <p>
                Text reproduced from Indian Kanoon for reading and research. It is not an authenticated copy of the
                judgment. Check the certified copy before citing.{" "}
                <a href={data.source_url} target="_blank" rel="noopener noreferrer">View original on Indian Kanoon</a>
                {" · "}
                <a href={data.hf_url || `https://huggingface.co/datasets/AnmolGV/section10-divorce-corpus/blob/main/parsed/${docId}.json`} target="_blank" rel="noopener noreferrer">Hugging Face Dataset JSON</a>
              </p>
            </footer>

            {notes.length > 0 && (
              <section className="print-only rd-endnotes" aria-label="Notes">
                <h2>Notes</h2>
                <ol>
                  {notes.map((h) => (
                    <li key={h.id} value={fnMap[h.id]}>
                      <span className="q">“{h.quote.length > 140 ? h.quote.slice(0, 140) + "…" : h.quote}”</span> {h.note}
                    </li>
                  ))}
                </ol>
              </section>
            )}
            <p className="print-only rd-printed">Printed {today} from {window.location.origin}. Reader's own highlights and notes; not part of the judgment.</p>
          </article>

          <aside className="rd-panel no-print" aria-label="Your highlights and notes">
            <h2>Your highlights <span className="rd-count">{ordered.length}</span></h2>
            {ordered.length === 0 && <p className="rd-empty">Nothing marked yet. Select a passage, pick a colour and press Highlight. Everything is saved in this browser.</p>}
            <ul>
              {ordered.map((h) => (
                <li key={h.id} id={`ann-${h.id}`} className={`rd-ann${focusId === h.id ? " active" : ""}${h.orphan ? " orphan" : ""}`}>
                  <div className="rd-ann-top">
                    <span className={`rd-dot hl-${h.color}`} aria-hidden="true" />
                    <span className="rd-ann-meta">¶ {h.para + 1}{fnMap[h.id] ? ` · note ${fnMap[h.id]}` : ""}</span>
                  </div>
                  <blockquote>{h.quote.length > 200 ? h.quote.slice(0, 200) + "…" : h.quote}</blockquote>
                  {h.orphan && <p className="rd-warn">This passage is no longer found in the current text, so it is not shown in the judgment. Your note is kept.</p>}
                  <label className="rd-sr" htmlFor={`note-${h.id}`}>Note for this passage</label>
                  <textarea
                    id={`note-${h.id}`}
                    defaultValue={h.note}
                    placeholder="Add a note…"
                    rows={2}
                    onBlur={(e) => e.target.value !== h.note && persist(updateHighlight(hls, h.id, { note: e.target.value }))}
                  />
                  <div className="rd-ann-actions">
                    {COLORS.map((c) => (
                      <button key={c} type="button" className={`rd-swatch sm hl-${c}`} aria-pressed={h.color === c}
                        aria-label={`Change to ${COLOR_LABELS[c]}`} onClick={() => persist(updateHighlight(hls, h.id, { color: c }))} />
                    ))}
                    <span className="rd-spacer" />
                    {!h.orphan && <button type="button" className="rd-mini" onClick={() => jump(h.id)}>Go to text</button>}
                    <button type="button" className="rd-mini danger" onClick={() => persist(removeHighlight(hls, h.id))}>Delete</button>
                  </div>
                </li>
              ))}
            </ul>
          </aside>
        </div>
      </main>
    </>
  );
}
