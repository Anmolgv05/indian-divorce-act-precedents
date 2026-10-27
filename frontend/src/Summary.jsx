import { useEffect, useMemo, useState } from "react";
import "./summary.css";

// Props: query (string), results (array exactly as returned by /api/search, best match first).
// Requires each result card to have id={`case-${rank}`} (rank starting at 1) so [n] links can jump to it.
export default function Summary({ query, results }) {
  const [state, setState] = useState({ status: "idle", data: null });
  const key = useMemo(
    () => query + "|" + (results || []).slice(0, 8).map((r) => r.doc_id ?? r.id).join(","),
    [query, results]
  );

  useEffect(() => {
    if (!results || results.length === 0) { setState({ status: "idle", data: null }); return; }
    const ctl = new AbortController();
    setState({ status: "loading", data: null });
    fetch("/api/summary", {
      method: "POST", headers: { "Content-Type": "application/json" }, signal: ctl.signal,
      body: JSON.stringify({ query, results: results.slice(0, 8) }),
    })
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((data) => setState({ status: "done", data }))
      .catch((e) => { if (e?.name !== "AbortError") setState({ status: "error", data: null }); });
    return () => ctl.abort();
  }, [key]); // eslint-disable-line react-hooks/exhaustive-deps

  if (state.status === "idle" || state.status === "error") return null;

  const jump = (n) => (e) => {
    const el = document.getElementById(`case-${n}`);
    if (!el) return;
    e.preventDefault();
    el.scrollIntoView({ behavior: "smooth", block: "start" });
    el.setAttribute("tabindex", "-1");
    el.focus({ preventScroll: true });
  };

  const render = (text) =>
    text.split(/(\[\d+\])/g).map((part, i) => {
      const m = part.match(/^\[(\d+)\]$/);
      return m ? (
        <a key={i} className="sum-cite" href={`#case-${m[1]}`} onClick={jump(m[1])} aria-label={`Go to result ${m[1]}`}>{m[1]}</a>
      ) : (part);
    });

  const d = state.data;
  return (
    <section className="sum" aria-labelledby="sum-h" aria-busy={state.status === "loading"}>
      <div className="sum-head">
        <h2 id="sum-h">Summary of these results</h2>
        {d && <span className="sum-badge">{d.mode === "llm" ? "AI-written, checked against the cases" : "Compiled from the case labels"}</span>}
      </div>
      <div aria-live="polite">
        {state.status === "loading" && <p className="sum-wait">Reading the results…</p>}
        {d && d.text.split("\n\n").map((p, i) => <p key={i}>{render(p)}</p>)}
      </div>
      {d && (
        <p className="sum-caveat">
          {d.caveat} <a href="#/about">How this is made</a>
        </p>
      )}
    </section>
  );
}
