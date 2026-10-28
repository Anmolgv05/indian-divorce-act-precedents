import { useEffect, useState } from "react";
import App from "./App.jsx";
import About from "./About.jsx";
import Section10 from "./Section10.jsx";
import Explorer from "./Explorer.jsx";
import Reader from "./Reader.jsx";
import Library from "./Library.jsx";
import KnowledgeGraph from "./KnowledgeGraph.jsx";

const getHash = () => (typeof window === "undefined" ? "" : window.location.hash);

export default function Root() {
  const [hash, setHash] = useState(getHash());
  useEffect(() => {
    const on = () => setHash(getHash());
    window.addEventListener("hashchange", on);
    return () => window.removeEventListener("hashchange", on);
  }, []);

  const clean = hash.replace(/^#\/?/, "").split("?")[0];
  if (clean === "about") return <About />;
  if (clean === "section-10") return <Section10 />;
  if (clean === "cases") return <Explorer />;
  if (clean === "graph") return <KnowledgeGraph />;
  if (clean === "library") return <Library />;

  const readMatch = hash.match(/^#\/?read\/(\d+)/);
  if (readMatch) {
    return <Reader docId={readMatch[1]} />;
  }

  return <App />;
}
