import { useEffect, useRef, useState } from "react";
import SiteNav from "./SiteNav.jsx";
import "./about.css";
import "./explorer.css";

const GROUND = {
  adultery: "Adultery", cruelty: "Cruelty", desertion: "Desertion", procedural: "Procedural question",
  nullity_sec19: "Nullity (Section 19)", mutual_consent_10A: "Mutual consent (Section 10A)",
  constitutional_validity: "Constitutional validity", non_consummation: "Non-consummation",
  unsound_mind: "Unsound mind", wife_specific: "Wife-specific ground", unclear: "Not determined",
};
const DISPOSAL = {
  allowed: "Allowed", dismissed: "Dismissed", confirmed: "Decree confirmed", not_confirmed: "Decree not confirmed",
  partly_allowed: "Partly allowed", remanded: "Sent back", disposed_of: "Disposed of", modified: "Modified",
  interim: "Interim order", unclear: "Not determined",
};
const ENDED = { yes: "Marriage ended", no: "Marriage not ended", unclear: "Not determined" };
const label = (map, k) => map[k] || k;
const PAGE_SIZE = 20;

let _readerEnabled = null;
let _readerPromise = null;
function checkReaderEnabled(callback) {
  if (_readerEnabled !== null) {
    callback(_readerEnabled);
    return;
  }
  if (!_readerPromise) {
    _readerPromise = fetch("/api/reader/status")
      .then((r) => (r.ok ? r.json() : { enabled: false }))
      .then((d) => {
        _readerEnabled = Boolean(d?.enabled);
        return _readerEnabled;
      })
      .catch(() => {
        _readerEnabled = false;
        return false;
      });
  }
  _readerPromise.then(callback);
}

function CaseItem({ c }) {
  const [open, setOpen] = useState(false);
  const [excerpt, setExcerpt] = useState(null);
  const [canRead, setCanRead] = useState(_readerEnabled ?? false);

  useEffect(() => {
    checkReaderEnabled(setCanRead);
  }, []);

  useEffect(() => {
    if (!open || excerpt !== null) return;
    fetch(`/api/cases/${c.doc_id}`).then((r) => r.json()).then((d) => setExcerpt(d.excerpt || "")).catch(() => setExcerpt(""));
  }, [open]); // eslint-disable-line react-hooks/exhaustive-deps
  const title = c.title.replace(/\s+on\s+\d{1,2}\s+\w+,\s*\d{4}\s*$/, "");
  return (
    <li className="ex-case">
      <h3>{title}</h3>
      <p className="ex-meta">{[c.year, c.court].filter(Boolean).join(" · ")}</p>
      <ul className="ex-chips" aria-label="Labels">
        <li>Ground: {label(GROUND, c.ground)}</li>
        <li>Outcome: {label(DISPOSAL, c.disposal)}</li>
        <li>{label(ENDED, c.ended)}</li>
        {c.non_merits && <li>Procedural or non-merits matter</li>}
      </ul>
      <div className="ex-actions">
        <button type="button" className="ex-link" aria-expanded={open} onClick={() => setOpen(!open)}>
          {open ? "Hide" : "Show"} the end of the judgment<span className="sr-only"> for {title}</span>
        </button>
        {canRead && (
          <a href={`#/read/${c.doc_id}`}>Read in site</a>
        )}
        <a href={`https://huggingface.co/datasets/anabaena/section10-divorce-corpus/blob/main/parsed/${c.doc_id}.json`} target="_blank" rel="noopener noreferrer">HF Data<span className="sr-only"> (opens in a new tab)</span></a>
        <a href={c.url} target="_blank" rel="noopener noreferrer">Indian Kanoon<span className="sr-only"> (opens in a new tab)</span></a>
      </div>
      {open && (
        <blockquote className="ex-excerpt">
          {excerpt === null ? "Loading…" : excerpt || "No excerpt available."}
          {excerpt ? <footer>Last part of the judgment, shown so you can see what the labels were read from.</footer> : null}
        </blockquote>
      )}
    </li>
  );
}

export default function Explorer() {
  const [f, setF] = useState({ q: "", ground: "", disposal: "", ended: "", court: "", year_min: "", year_max: "", hide: false, sort: "year_desc" });
  const [debouncedQ, setDebouncedQ] = useState("");
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null);
  const [facets, setFacets] = useState(null);
  const [err, setErr] = useState(false);
  const headRef = useRef(null);

  useEffect(() => { const t = setTimeout(() => setDebouncedQ(f.q), 300); return () => clearTimeout(t); }, [f.q]);
  useEffect(() => { setPage(1); }, [debouncedQ, f.ground, f.disposal, f.ended, f.court, f.year_min, f.year_max, f.hide, f.sort]);

  useEffect(() => {
    const p = new URLSearchParams({ page, page_size: PAGE_SIZE, sort: f.sort, include_non_merits: String(!f.hide) });
    if (debouncedQ) p.set("q", debouncedQ);
    ["ground", "disposal", "ended", "court", "year_min", "year_max"].forEach((k) => f[k] !== "" && p.set(k, f[k]));
    const ctl = new AbortController();
    setErr(false);
    fetch(`/api/cases?${p}`, { signal: ctl.signal })
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) => { setData(d); setFacets((old) => old || d.facets); })
      .catch((e) => { if (e?.name !== "AbortError") setErr(true); });
    return () => ctl.abort();
  }, [debouncedQ, f.ground, f.disposal, f.ended, f.court, f.year_min, f.year_max, f.hide, f.sort, page]); // eslint-disable-line react-hooks/exhaustive-deps

  const set = (k) => (e) => setF({ ...f, [k]: e.target.type === "checkbox" ? e.target.checked : e.target.value });
  const reset = () => setF({ q: "", ground: "", disposal: "", ended: "", court: "", year_min: "", year_max: "", hide: false, sort: "year_desc" });
  const go = (n) => { setPage(n); headRef.current?.focus(); headRef.current?.scrollIntoView({ block: "start" }); };
  const opts = (obj, map) => Object.entries(obj || {}).map(([k, n]) => <option key={k} value={k}>{label(map, k)} ({n})</option>);
  const from = data && data.total ? (data.page - 1) * data.page_size + 1 : 0;
  const to = data ? Math.min(data.total, data.page * data.page_size) : 0;

  return (
    <>
      <SiteNav />
      <main id="main" className="about ex">
        <p className="about-kicker">BROWSE</p>
        <h1>All cases in the database</h1>
        <p className="about-lede">
          Every judgment this site searches, with the labels our rules gave it. Filter, sort and open any case.
          Labels are machine-generated and can be wrong; “Not determined” means the rules could not tell.
        </p>

        <form className="ex-filters" role="search" aria-label="Filter cases" onSubmit={(e) => e.preventDefault()}>
          <div className="ex-field ex-wide">
            <label htmlFor="ex-q">Case name or ID</label>
            <input id="ex-q" type="search" value={f.q} onChange={set("q")} autoComplete="off" />
          </div>
          <div className="ex-field"><label htmlFor="ex-g">Ground</label>
            <select id="ex-g" value={f.ground} onChange={set("ground")}><option value="">All grounds</option>{opts(facets?.ground, GROUND)}</select></div>
          <div className="ex-field"><label htmlFor="ex-d">Outcome</label>
            <select id="ex-d" value={f.disposal} onChange={set("disposal")}><option value="">All outcomes</option>{opts(facets?.disposal, DISPOSAL)}</select></div>
          <div className="ex-field"><label htmlFor="ex-e">Did the marriage end?</label>
            <select id="ex-e" value={f.ended} onChange={set("ended")}><option value="">Any</option>{opts(facets?.ended, ENDED)}</select></div>
          <div className="ex-field"><label htmlFor="ex-c">Court</label>
            <select id="ex-c" value={f.court} onChange={set("court")}><option value="">All courts</option>{Object.entries(facets?.court || {}).map(([k, n]) => <option key={k} value={k}>{k} ({n})</option>)}</select></div>
          <div className="ex-field"><label htmlFor="ex-y1">Year from</label>
            <input id="ex-y1" type="number" inputMode="numeric" min={facets?.year_min} max={facets?.year_max} value={f.year_min} onChange={set("year_min")} /></div>
          <div className="ex-field"><label htmlFor="ex-y2">Year to</label>
            <input id="ex-y2" type="number" inputMode="numeric" min={facets?.year_min} max={facets?.year_max} value={f.year_max} onChange={set("year_max")} /></div>
          <div className="ex-field"><label htmlFor="ex-s">Sort by</label>
            <select id="ex-s" value={f.sort} onChange={set("sort")}>
              <option value="year_desc">Newest first</option><option value="year_asc">Oldest first</option><option value="title">Case name A–Z</option></select></div>
          <div className="ex-field ex-check">
            <input id="ex-h" type="checkbox" checked={f.hide} onChange={set("hide")} />
            <label htmlFor="ex-h">Hide procedural and non-merits matters</label></div>
          <div className="ex-field"><button type="button" className="ex-reset" onClick={reset}>Clear all filters</button></div>
        </form>

        <h2 id="cases-h" tabIndex={-1} ref={headRef} className="ex-count" aria-live="polite">
          {err ? "Could not load cases." : data ? (data.total ? `Showing ${from}–${to} of ${data.total} cases` : "No cases match these filters") : "Loading cases…"}
        </h2>

        {data && data.total > 0 && <ol className="ex-list" aria-labelledby="cases-h">{data.items.map((c) => <CaseItem key={c.doc_id} c={c} />)}</ol>}

        {data && data.pages > 1 && (
          <nav className="ex-pager" aria-label="Pages of results">
            <button type="button" disabled={data.page <= 1} onClick={() => go(data.page - 1)}>Previous</button>
            <span>Page {data.page} of {data.pages}</span>
            <button type="button" disabled={data.page >= data.pages} onClick={() => go(data.page + 1)}>Next</button>
          </nav>
        )}
        <p className="ex-note">Judgments are public court records from Indian Kanoon. This page shows only labels and a short excerpt; always read the original judgment. <a href="#/about">How the labels are made</a></p>
      </main>
    </>
  );
}
