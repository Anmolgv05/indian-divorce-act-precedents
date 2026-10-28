import { useEffect, useState } from "react";
import SiteNav from "./SiteNav.jsx";
import "./knowledge_graph.css";

const LANDMARK_CASES = [
  { id: "1401518", name: "Mrs. Pragati Varghese v. Cyril George Varghese (Bombay HC FB 1997)" },
  { id: "191479048", name: "Alphonsa v. Rajathasammal (Madras HC 2002)" },
  { id: "1264372", name: "Mary Browne v. A.N. Browne (Madras HC)" },
  { id: "504250", name: "Bipinchandra Jaisinghbhai Shah v. Prabhavati (Supreme Court 1956)" },
];

export default function KnowledgeGraph() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("sections");
  const [selectedCaseId, setSelectedCaseId] = useState("1401518");
  const [caseNeighborhood, setCaseNeighborhood] = useState(null);
  const [neighborhoodLoading, setNeighborhoodLoading] = useState(false);
  const [testQuery, setTestQuery] = useState("wife condoned adultery after 2 years desertion under Section 14 in Madras High Court");
  const [resolvedEntities, setResolvedEntities] = useState(null);
  const [resolving, setResolving] = useState(false);

  useEffect(() => {
    fetch("/api/graph/stats")
      .then((r) => r.json())
      .then((data) => {
        setStats(data);
        setLoading(false);
      })
      .catch((e) => {
        console.error("Failed to load graph stats:", e);
        setLoading(false);
      });
  }, []);

  const loadCaseNeighborhood = (docId) => {
    setSelectedCaseId(docId);
    setNeighborhoodLoading(true);
    fetch(`/api/graph/case/${docId}`)
      .then((r) => r.json())
      .then((data) => {
        setCaseNeighborhood(data);
        setNeighborhoodLoading(false);
      })
      .catch((e) => {
        console.error("Failed to load case neighborhood:", e);
        setNeighborhoodLoading(false);
      });
  };

  useEffect(() => {
    if (selectedCaseId) {
      loadCaseNeighborhood(selectedCaseId);
    }
  }, []);

  const handleResolveText = () => {
    if (!testQuery.trim()) return;
    setResolving(true);
    fetch(`/api/graph/entities?query=${encodeURIComponent(testQuery)}`)
      .then((r) => r.json())
      .then((data) => {
        setResolvedEntities(data);
        setResolving(false);
      })
      .catch((e) => {
        console.error("Failed to resolve text entities:", e);
        setResolving(false);
      });
  };

  return (
    <>
      <SiteNav />
      <main id="main" className="kg-container">
        <header className="kg-header">
          <h1>🕸️ Section 10 Legal Knowledge Graph &amp; Entity Resolution</h1>
          <p className="kg-subtitle">
            A bidirectional legal property graph indexing 429 Indian Divorce Act precedents across High Courts,
            judges, statutory provisions, fault grounds, legal eras, and operative judicial outcomes.
          </p>
        </header>

        {loading ? (
          <div className="skeletons"><div className="sk" /><div className="sk" /></div>
        ) : stats ? (
          <>
            <div className="kg-stats-grid">
              <div className="kg-stat-card">
                <div className="kg-stat-val">{stats.total_nodes}</div>
                <div className="kg-stat-lbl">Graph Entities (Nodes)</div>
              </div>
              <div className="kg-stat-card">
                <div className="kg-stat-val">{stats.total_edges}</div>
                <div className="kg-stat-lbl">Jurisprudential Relations (Edges)</div>
              </div>
              <div className="kg-stat-card">
                <div className="kg-stat-val">{stats.node_types?.case || 429}</div>
                <div className="kg-stat-lbl">Adjudicated Judgments</div>
              </div>
              <div className="kg-stat-card">
                <div className="kg-stat-val">{stats.node_types?.court || 21}</div>
                <div className="kg-stat-lbl">High Courts &amp; Supreme Court</div>
              </div>
              <div className="kg-stat-card">
                <div className="kg-stat-val">{stats.node_types?.judge || 195}</div>
                <div className="kg-stat-lbl">Canonical Judges</div>
              </div>
              <div className="kg-stat-card">
                <div className="kg-stat-val">{stats.node_types?.section || 247}</div>
                <div className="kg-stat-lbl">Statutory Sections Cited</div>
              </div>
            </div>

            <div className="kg-tabs" role="tablist">
              <button
                type="button"
                className={`kg-tab-btn ${activeTab === "sections" ? "active" : ""}`}
                onClick={() => setActiveTab("sections")}
              >
                📜 Statutory Sections
              </button>
              <button
                type="button"
                className={`kg-tab-btn ${activeTab === "courts" ? "active" : ""}`}
                onClick={() => setActiveTab("courts")}
              >
                🏛️ High Courts
              </button>
              <button
                type="button"
                className={`kg-tab-btn ${activeTab === "judges" ? "active" : ""}`}
                onClick={() => setActiveTab("judges")}
              >
                ⚖️ Canonical Judges
              </button>
              <button
                type="button"
                className={`kg-tab-btn ${activeTab === "similarity" ? "active" : ""}`}
                onClick={() => setActiveTab("similarity")}
              >
                🔗 Case Neighborhoods &amp; Graph Similarity
              </button>
              <button
                type="button"
                className={`kg-tab-btn ${activeTab === "resolver" ? "active" : ""}`}
                onClick={() => setActiveTab("resolver")}
              >
                🔍 Live Entity Resolution Tester
              </button>
            </div>

            {activeTab === "sections" && (
              <section>
                <h3>Most Cited Statutory Provisions Across the 429 Precedents</h3>
                <p style={{ color: "var(--muted)", marginBottom: "1rem" }}>
                  Judgments cite specific procedural and substantive provisions that dictate evidentiary burdens and statutory bars.
                </p>
                <div className="kg-hubs-grid">
                  {(stats.top_sections || []).map((s) => (
                    <div key={s.name} className="kg-hub-item">
                      <span className="kg-hub-name">{s.name}</span>
                      <span className="kg-hub-badge">{s.cases_citing} citing cases</span>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {activeTab === "courts" && (
              <section>
                <h3>Jurisdictional Distribution of Precedents</h3>
                <p style={{ color: "var(--muted)", marginBottom: "1rem" }}>
                  Christian matrimonial disputes historically cluster in coastal High Courts (Madras, Kerala, Bombay, Calcutta) alongside Supreme Court appeals.
                </p>
                <div className="kg-hubs-grid">
                  {(stats.top_courts || []).map((c) => (
                    <div key={c.name} className="kg-hub-item">
                      <span className="kg-hub-name">{c.name}</span>
                      <span className="kg-hub-badge">{c.cases_decided} judgments</span>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {activeTab === "judges" && (
              <section>
                <h3>Canonical Judges with Multiple Reported Section 10 Decisions</h3>
                <p style={{ color: "var(--muted)", marginBottom: "1rem" }}>
                  Entity resolution extracted and unified judge names from court docket headers, removing honorifics and bench suffixes.
                </p>
                <div className="kg-hubs-grid">
                  {(stats.top_judges || []).map((j) => (
                    <div key={j.name} className="kg-hub-item">
                      <span className="kg-hub-name">{j.name}</span>
                      <span className="kg-hub-badge">{j.cases_heard} cases</span>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {activeTab === "similarity" && (
              <section>
                <h3>Explore a Case’s Graph Neighborhood &amp; Structural Similarity</h3>
                <p style={{ color: "var(--muted)", marginBottom: "1rem" }}>
                  Pick a landmark judgment to inspect its 1-hop connections and find structurally related precedents sharing the same statutory sections, grounds, and courts:
                </p>

                <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginBottom: "1.25rem" }}>
                  {LANDMARK_CASES.map((lc) => (
                    <button
                      key={lc.id}
                      type="button"
                      className={`rd-btn ${selectedCaseId === lc.id ? "strong" : ""}`}
                      onClick={() => loadCaseNeighborhood(lc.id)}
                    >
                      {lc.name}
                    </button>
                  ))}
                </div>

                {neighborhoodLoading && <p>Loading graph neighborhood…</p>}

                {caseNeighborhood && !neighborhoodLoading && (
                  <div className="kg-neighborhood-box">
                    <h4>{caseNeighborhood.case?.title} ({caseNeighborhood.case?.year || "n/a"})</h4>
                    <p style={{ color: "var(--muted)", fontSize: "0.9rem", margin: "0.25rem 0 1rem" }}>
                      {caseNeighborhood.case?.court} · Ground: <b>{caseNeighborhood.case?.ground}</b> · Outcome: <b>{caseNeighborhood.case?.disposal}</b>
                    </p>

                    <div>
                      <h5 style={{ margin: "0.75rem 0 0.5rem" }}>Direct Connected Entities in Graph:</h5>
                      <div>
                        {Object.entries(caseNeighborhood.connected_entities || {}).map(([type, list]) => (
                          <div key={type} style={{ margin: "0.4rem 0" }}>
                            <strong style={{ textTransform: "capitalize", fontSize: "0.85rem", color: "var(--muted)" }}>{type}: </strong>
                            {list.map((item) => (
                              <span key={item} className="kg-conn-pill">{item}</span>
                            ))}
                          </div>
                        ))}
                      </div>
                    </div>

                    <div style={{ marginTop: "1.5rem" }}>
                      <h5>Structurally Related Cases (via 2-hop Shared Graph Connections):</h5>
                      <div className="kg-similar-list">
                        {(caseNeighborhood.similar_cases_via_graph || []).map((sc) => (
                          <div key={sc.doc_id} className="kg-similar-card">
                            <div>
                              <a href={`#/read/${sc.doc_id}`} style={{ fontWeight: 600, color: "var(--accent)" }}>
                                {sc.title} ({sc.year || "n/a"})
                              </a>
                              <div className="kg-similar-meta">
                                {sc.court} · Ground: {sc.ground} · Outcome: {sc.disposal}
                              </div>
                            </div>
                            <span className="kg-hub-badge">{sc.shared_graph_connections} shared entities</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </section>
            )}

            {activeTab === "resolver" && (
              <section>
                <h3>Live Entity Resolution (ER) Engine</h3>
                <p style={{ color: "var(--muted)", marginBottom: "1rem" }}>
                  Test how the Entity Resolution engine extracts statutory sections, matrimonial fault grounds, statutory bars, and canonical High Courts from arbitrary text:
                </p>

                <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
                  <input
                    type="text"
                    value={testQuery}
                    onChange={(e) => setTestQuery(e.target.value)}
                    style={{ flex: 1, padding: "0.6rem 0.8rem", borderRadius: "8px", border: "1px solid var(--border)" }}
                    placeholder="Enter legal scenario or clause..."
                  />
                  <button type="button" className="rd-btn strong" onClick={handleResolveText}>
                    {resolving ? "Resolving…" : "Resolve Entities"}
                  </button>
                </div>

                {resolvedEntities && (
                  <div className="kg-neighborhood-box">
                    <h4>Resolved Legal Entities:</h4>
                    <div style={{ marginTop: "0.75rem" }}>
                      <p><b>🏛️ Courts Identified:</b> {resolvedEntities.courts?.length ? resolvedEntities.courts.join(", ") : "None"}</p>
                      <p><b>⚖️ Grounds Identified:</b> {resolvedEntities.grounds?.length ? resolvedEntities.grounds.join(", ") : "None"}</p>
                      <p><b>📜 Statutory Sections:</b> {resolvedEntities.sections?.length ? resolvedEntities.sections.join(", ") : "None"}</p>
                      <p><b>⚠️ Statutory Bars:</b> {resolvedEntities.statutory_bars?.length ? resolvedEntities.statutory_bars.join(", ") : "None"}</p>
                    </div>
                  </div>
                )}
              </section>
            )}
          </>
        ) : (
          <p>Failed to load Knowledge Graph data.</p>
        )}
      </main>
    </>
  );
}
