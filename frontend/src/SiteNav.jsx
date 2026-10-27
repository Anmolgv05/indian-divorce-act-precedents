import { useEffect, useState } from "react";
import "./nav.css";

const route = () => (typeof window === "undefined" ? "" : window.location.hash.replace(/^#\/?/, "").split("?")[0]);

export default function SiteNav() {
  const [r, setR] = useState(route());
  const [theme, setTheme] = useState(() => (typeof document !== "undefined" ? document.documentElement.dataset.theme || "" : ""));

  useEffect(() => {
    const on = () => setR(route());
    window.addEventListener("hashchange", on);
    return () => window.removeEventListener("hashchange", on);
  }, []);

  const toggleTheme = () => {
    const dark = theme ? theme === "dark" : window.matchMedia("(prefers-color-scheme: dark)").matches;
    const next = dark ? "light" : "dark";
    setTheme(next);
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem("s10-theme", next); } catch { /* private mode */ }
  };

  const skip = (e) => {
    const m = document.getElementById("main");
    if (!m) return;
    e.preventDefault();
    m.setAttribute("tabindex", "-1");
    m.focus();
  };

  const isCurrent = (name) => (r === name ? "page" : undefined);

  return (
    <>
      <a className="skip-link" href="#main" onClick={skip}>Skip to main content</a>
      <header className="site-header no-print">
        <div className="site-header-inner">
          <div className="site-brand-wrap">
            <a className="site-brand" href="#/" aria-label="Section 10 Precedent Search, home">
              <span className="brand-mark">§</span>
              <span className="brand-title">Section 10</span>
            </a>
            <span className="site-scope-badge">Divorce Act, 1869</span>
          </div>

          <nav aria-label="Site Navigation" className="site-nav">
            <a className="nav-item" href="#/" aria-current={isCurrent("")}>Search</a>
            <a className="nav-item" href="#/section-10" aria-current={isCurrent("section-10")}>Section 10 Explained</a>
            <a className="nav-item" href="#/cases" aria-current={isCurrent("cases")}>Browse Cases</a>
            <a className="nav-item" href="#/library" aria-current={isCurrent("library")}>My Library</a>
            <a className="nav-item" href="#/about" aria-current={isCurrent("about")}>About &amp; Tags</a>
          </nav>

          <div className="site-header-actions">
            <button
              type="button"
              className="theme-toggle-btn"
              onClick={toggleTheme}
              aria-label="Toggle light and dark theme"
              title="Toggle theme"
            >
              <i className="theme-toggle-icon" aria-hidden="true" />
            </button>
          </div>
        </div>
      </header>
    </>
  );
}
