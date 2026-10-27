import { useRef, useState } from "react";
import SiteNav from "./SiteNav.jsx";
import {
  COLOR_LABELS, loadLibrary, listEntries, removeEntry, exportJSON, importJSON,
  toMarkdown, libraryToMarkdown, sortHighlights,
} from "./lib/annotations.js";
import { download, safeName, printWithTitle } from "./lib/download.js";
import "./reader.css";

export default function Library() {
  const [lib, setLib] = useState(() => loadLibrary());
  const [msg, setMsg] = useState("");
  const fileRef = useRef(null);
  const entries = listEntries(lib);

  const remove = (e) => {
    if (!window.confirm(`Remove "${e.title}" and its ${e.highlights.length} highlight(s) from your library?`)) return;
    setLib(removeEntry(e.docId));
  };

  const onImport = async (ev) => {
    const f = ev.target.files && ev.target.files[0];
    if (!f) return;
    const res = importJSON(await f.text());
    setMsg(res.ok ? `Imported: ${res.added} new, ${res.updated} updated.` : res.error);
    setLib(loadLibrary());
    ev.target.value = "";
  };

  return (
    <>
      <div className="no-print"><SiteNav /></div>
      <main id="main" className="lib">
        <h1>My library</h1>
        <p className="lib-note no-print">
          Cases you saved, with your highlights and notes. They are stored in this browser only. Clearing site data or
          switching device removes them, so export a backup now and then.
        </p>

        <div className="lib-actions no-print">
          <button type="button" className="rd-btn" disabled={!entries.length}
            onClick={() => download("section10-library-backup.json", exportJSON(lib), "application/json")}>Back up (JSON)</button>
          <button type="button" className="rd-btn" disabled={!entries.length}
            onClick={() => download("section10-library-notes.md", libraryToMarkdown(lib), "text/markdown")}>Export all notes (.md)</button>
          <button type="button" className="rd-btn" disabled={!entries.length}
            onClick={() => printWithTitle("Section 10 library notes")}>Save all as PDF</button>
          <button type="button" className="rd-btn" onClick={() => fileRef.current && fileRef.current.click()}>Restore from backup</button>
          <input ref={fileRef} type="file" accept="application/json,.json" hidden onChange={onImport} />
        </div>
        {msg && <p className="rd-notice no-print" role="status">{msg}</p>}

        {entries.length === 0 && (
          <p className="rd-empty">
            Nothing saved yet. Open a case from <a href="#/cases">Browse all cases</a> and press “Save to library”, or just
            highlight a passage and it saves itself.
          </p>
        )}

        <ul className="lib-list">
          {entries.map((e) => {
            const withNotes = e.highlights.filter((h) => h.note && h.note.trim()).length;
            return (
              <li key={e.docId} className="lib-card">
                <h2><a href={`#/read/${e.docId}`}>{e.title}</a></h2>
                <p className="lib-meta">
                  {[e.court, e.year].filter(Boolean).join(" · ")}
                  {" · "}{e.highlights.length} highlight{e.highlights.length === 1 ? "" : "s"}, {withNotes} note{withNotes === 1 ? "" : "s"}
                  {e.updatedAt ? ` · updated ${new Date(e.updatedAt).toLocaleDateString("en-IN")}` : ""}
                </p>
                <div className="lib-card-actions no-print">
                  <a className="rd-btn rd-link" href={`#/read/${e.docId}`}>Open</a>
                  <button type="button" className="rd-btn" onClick={() => download(`${safeName(e.title)}-notes.md`, toMarkdown(e), "text/markdown")}>Export notes</button>
                  <button type="button" className="rd-btn danger" onClick={() => remove(e)}>Remove</button>
                </div>
                <ul className="lib-ann print-only">
                  {sortHighlights(e.highlights).map((h) => (
                    <li key={h.id}>
                      <span className="rd-ann-meta">¶ {h.para + 1} · {COLOR_LABELS[h.color]}</span>
                      <blockquote>{h.quote}</blockquote>
                      {h.note && <p>{h.note}</p>}
                    </li>
                  ))}
                </ul>
              </li>
            );
          })}
        </ul>
      </main>
    </>
  );
}
