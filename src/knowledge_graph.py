"""Section 10 Knowledge Graph & Legal Entity Resolution Engine.

Constructs an in-memory property graph across 429 Indian Divorce Act precedents:
- Entity Resolution (ER): Canonicalizes Courts, Judges, Statutory Provisions, Grounds, Eras, and Outcomes.
- Knowledge Graph (KG): Bidirectional graph indexing cases and legal entities with degree centrality and structural similarity.
- Graph-Augmented Retrieval: Enhances SLM search by identifying entity clusters and boosting cases connected through graph relations.
"""

from __future__ import annotations

import json
import logging
import os
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("knowledge_graph")

ROOT_DIR = Path(__file__).resolve().parent.parent
STRUCTURED_DB_PATH = ROOT_DIR / "data" / "section10_cases_structured_database.json"

# Canonical statutory annotations under Indian Divorce Act, 1869 & allied statutes
STATUTORY_DESCRIPTIONS = {
    "Section 10": "Primary statutory grounds for dissolution of marriage (adultery, conversion, unsound mind, desertion, cruelty, etc.)",
    "Section 10A": "Dissolution of marriage by mutual consent (introduced in 2001)",
    "Section 11": "Statutory mandate to make the alleged adulterer a co-respondent to the petition",
    "Section 14": "Court satisfaction against connivance, condonation, or collusion; condonation statutory bar",
    "Section 16": "Decrees for dissolution to be decree nisi before becoming absolute",
    "Section 17": "High Court confirmation requirement for District Court divorce decrees (pre-2001 procedure)",
    "Section 18": "Petition for declaration of nullity of marriage",
    "Section 19": "Statutory grounds for decree of nullity (impotency, consanguinity, lunacy, force/fraud)",
    "Section 22": "Decree for judicial separation on ground of adultery, cruelty, or two years desertion",
    "Section 32": "Restitution of conjugal rights when spouse has withdrawn without reasonable excuse",
    "Section 33": "Answers and defenses to petition for restitution of conjugal rights",
    "Section 36": "Alimony pendente lite (interim maintenance during proceedings)",
    "Section 37": "Permanent alimony and maintenance for spouse",
    "Section 125 CrPC": "Criminal Procedure Code maintenance proceedings",
    "Section 498A IPC": "Cruelty by husband or relatives under Indian Penal Code",
}


class EntityResolver:
    """Canonicalizes and resolves legal entities across text and database records."""

    # Canonical court mappings
    COURT_MAP = {
        "madras": "Madras High Court",
        "kerala": "Kerala High Court",
        "bombay": "Bombay High Court",
        "calcutta": "Calcutta High Court",
        "delhi": "Delhi High Court",
        "karnataka": "Karnataka High Court",
        "allahabad": "Allahabad High Court",
        "jharkhand": "Jharkhand High Court",
        "orissa": "Orissa High Court",
        "supreme": "Supreme Court of India",
        "punjab": "Punjab and Haryana High Court",
        "haryana": "Punjab and Haryana High Court",
        "gauhati": "Gauhati High Court",
        "madhya pradesh": "Madhya Pradesh High Court",
        "andhra": "Andhra Pradesh High Court",
        "telangana": "Telangana High Court",
        "himachal": "Himachal Pradesh High Court",
        "patna": "Patna High Court",
        "rajasthan": "Rajasthan High Court",
        "chhattisgarh": "Chhattisgarh High Court",
        "uttarakhand": "Uttarakhand High Court",
        "gujarat": "Gujarat High Court",
    }

    # Canonical grounds
    GROUND_MAP = {
        "adultery": "Adultery",
        "cruelty": "Cruelty",
        "desertion": "Desertion",
        "nullity": "Nullity (s.19)",
        "nullity_sec19": "Nullity (s.19)",
        "mutual_consent": "Mutual Consent (s.10A)",
        "mutual_consent_10a": "Mutual Consent (s.10A)",
        "unsound_mind": "Unsound Mind",
        "conversion": "Conversion",
        "non_consummation": "Non-consummation",
        "procedural": "Procedural",
        "constitutional_validity": "Constitutional Validity",
    }

    @classmethod
    def resolve_court(cls, raw: str) -> str:
        """Resolves raw court string to canonical High Court or Supreme Court."""
        if not raw:
            return "Other / Unspecified Court"
        raw_lower = raw.lower()
        for pattern, canonical in cls.COURT_MAP.items():
            if pattern in raw_lower:
                return canonical
        return raw.strip()

    @classmethod
    def resolve_judges(cls, raw: str) -> List[str]:
        """Parses and canonicalizes individual judge names from bench string."""
        if not raw or raw.strip().lower() in ("not specified", "bench", "null", "none"):
            return []

        # Split on comma, semicolon, '&', 'and'
        parts = re.split(r"[,;&]|\band\b", raw)
        clean_judges = []
        for p in parts:
            j = p.strip()
            # Remove judicial titles and suffixes
            j = re.sub(r"\b(Justice|Hon'?ble|Mr\.?|Mrs\.?|Ms\.?)\b", "", j, flags=re.I)
            j = re.sub(r"\b(C\.?J\.?|Officiating C\.?J\.?|J\.?|JJ\.?)\b", "", j, flags=re.I)
            j = re.sub(r"\s+", " ", j).strip()
            if len(j) >= 3 and not j.lower().startswith("bench") and not j.lower() in ("not specified", "unclear"):
                clean_judges.append(j)
        return clean_judges

    @classmethod
    def resolve_sections(cls, raw: str) -> List[str]:
        """Extracts and canonicalizes statutory sections cited."""
        if not raw:
            return ["Section 10"]

        sections = []
        for part in re.split(r"[,;]", raw):
            s = part.strip()
            if not s:
                continue
            # Canonicalize Section 10A, Section 10, etc.
            match = re.search(r"\bSection\s+(\d+[A-Za-z]?)\b", s, re.I)
            if match:
                sec_num = match.group(1).upper()
                sec_id = f"Section {sec_num}"
                sections.append(sec_id)
            elif "125" in s:
                sections.append("Section 125 CrPC")
            elif "498" in s:
                sections.append("Section 498A IPC")

        # Ensure Section 10 is present as anchor
        if "Section 10" not in sections:
            sections.insert(0, "Section 10")
        return list(dict.fromkeys(sections))

    @classmethod
    def resolve_ground(cls, raw: str) -> str:
        """Resolves raw ground to canonical label."""
        if not raw:
            return "Unclear"
        raw_key = raw.lower().replace(" ", "_").replace("-", "_")
        for k, v in cls.GROUND_MAP.items():
            if k in raw_key:
                return v
        return raw.strip().title()

    @classmethod
    def extract_entities_from_text(cls, text: str) -> Dict[str, List[str]]:
        """Identifies known legal entities in a free-text search query or scenario."""
        text_lower = text.lower()
        extracted: Dict[str, List[str]] = {
            "courts": [],
            "grounds": [],
            "sections": [],
            "statutory_bars": [],
        }

        # Courts
        for pattern, canonical in cls.COURT_MAP.items():
            if re.search(rf"\b{pattern}\b", text_lower):
                if canonical not in extracted["courts"]:
                    extracted["courts"].append(canonical)

        # Grounds
        ground_triggers = {
            "Adultery": ["adultery", "paramour", "illicit", "infidelity", "affair"],
            "Cruelty": ["cruelty", "torture", "harass", "beating", "mental cruelty"],
            "Desertion": ["desertion", "abandon", "separated", "left home", "deserted"],
            "Nullity (s.19)": ["nullity", "annul", "impoten", "non-consummat", "fraud", "force"],
            "Mutual Consent (s.10A)": ["mutual consent", "10a", "joint petition"],
            "Unsound Mind": ["unsound mind", "mental illness", "schizophrenia", "insanity"],
            "Conversion": ["conversion", "converted", "ceased to be christian"],
        }
        for ground, triggers in ground_triggers.items():
            if any(re.search(rf"\b{t}\b", text_lower) for t in triggers):
                extracted["grounds"].append(ground)

        # Sections
        section_matches = re.findall(r"\bsection\s+(\d+[a-z]?)\b", text_lower)
        for s in section_matches:
            sec_name = f"Section {s.upper()}"
            extracted["sections"].append(sec_name)
        if "125" in text_lower or "maintenance" in text_lower:
            extracted["sections"].append("Section 125 CrPC")
        if "498a" in text_lower or "498-a" in text_lower:
            extracted["sections"].append("Section 498A IPC")

        # Specific statutory bars
        if any(w in text_lower for w in ["condon", "forgave", "forgiven"]):
            extracted["statutory_bars"].append("Condonation (s.14)")
            if "Section 14" not in extracted["sections"]:
                extracted["sections"].append("Section 14")
        if any(w in text_lower for w in ["co-respondent", "co respondent", "adulterer party"]):
            extracted["statutory_bars"].append("Co-respondent Rule (s.11)")
            if "Section 11" not in extracted["sections"]:
                extracted["sections"].append("Section 11")

        return extracted


class Section10KnowledgeGraph:
    """In-memory Knowledge Graph representing judgments, courts, judges,

    statutory sections, legal grounds, and operative outcomes.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or STRUCTURED_DB_PATH
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Dict[str, Any]] = []
        self.adj: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.rev_adj: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.cases_by_id: Dict[str, Dict[str, Any]] = {}
        self.is_built: bool = False
        self._build_graph()

    def _add_node(self, node_id: str, node_type: str, label: str, properties: Optional[Dict[str, Any]] = None):
        if node_id not in self.nodes:
            self.nodes[node_id] = {
                "id": node_id,
                "type": node_type,
                "label": label,
                "properties": properties or {},
                "degree": 0,
            }
        else:
            if properties:
                self.nodes[node_id]["properties"].update(properties)

    def _add_edge(self, source_id: str, target_id: str, relation: str, weight: float = 1.0, properties: Optional[Dict[str, Any]] = None):
        edge = {
            "source": source_id,
            "target": target_id,
            "relation": relation,
            "weight": weight,
            "properties": properties or {},
        }
        self.edges.append(edge)
        self.adj[source_id].append({"target": target_id, "relation": relation, "weight": weight})
        self.rev_adj[target_id].append({"source": source_id, "relation": relation, "weight": weight})
        if source_id in self.nodes:
            self.nodes[source_id]["degree"] += 1
        if target_id in self.nodes:
            self.nodes[target_id]["degree"] += 1

    def _build_graph(self):
        """Constructs graph from structured database."""
        if not self.db_path.exists():
            logger.warning(f"Database path {self.db_path} does not exist.")
            return

        with open(self.db_path, "r", encoding="utf-8") as f:
            raw_cases = json.load(f)

        for c in raw_cases:
            doc_id = str(c.get("Kanoon Doc ID") or c.get("doc_id", "")).strip()
            if not doc_id:
                continue

            case_node_id = f"case:{doc_id}"
            title = c.get("Case Title") or f"Judgment {doc_id}"
            year = c.get("Judgment Year")
            disposal = c.get("Outcome", "Unclear")
            dissolved = c.get("Marriage Dissolved", "unclear")
            era = c.get("Legal Era", "Unspecified Era")
            court_raw = c.get("Court", "")
            court_canon = EntityResolver.resolve_court(court_raw)
            judges_canon = EntityResolver.resolve_judges(c.get("Judges", ""))
            sections_canon = EntityResolver.resolve_sections(c.get("Sections Cited", ""))
            ground_canon = EntityResolver.resolve_ground(c.get("Ground (Primary)", ""))

            case_props = {
                "doc_id": doc_id,
                "title": title,
                "year": year,
                "case_number": c.get("Case Number", ""),
                "court": court_canon,
                "disposal": disposal,
                "dissolved": dissolved,
                "era": era,
                "ground": ground_canon,
                "url": c.get("Canonical Source URL", f"https://indiankanoon.org/doc/{doc_id}/"),
                "operative_decree": c.get("Decision", ""),
                "facts": c.get("Fact/ Petitioner", ""),
            }
            self.cases_by_id[doc_id] = case_props

            # Add Case Node
            self._add_node(case_node_id, "case", title, case_props)

            # 1. Court Node & Edge
            court_node_id = f"court:{court_canon}"
            self._add_node(court_node_id, "court", court_canon)
            self._add_edge(case_node_id, court_node_id, "DECIDED_BY")

            # 2. Judge Nodes & Edges
            for j in judges_canon:
                judge_node_id = f"judge:{j}"
                self._add_node(judge_node_id, "judge", j)
                self._add_edge(case_node_id, judge_node_id, "HEARD_BY")

            # 3. Statutory Section Nodes & Edges
            for s in sections_canon:
                section_node_id = f"section:{s}"
                sec_desc = STATUTORY_DESCRIPTIONS.get(s, "Statutory provision")
                self._add_node(section_node_id, "section", s, {"description": sec_desc})
                self._add_edge(case_node_id, section_node_id, "CITES_SECTION")

            # 4. Ground Node & Edge
            ground_node_id = f"ground:{ground_canon}"
            self._add_node(ground_node_id, "ground", ground_canon)
            self._add_edge(case_node_id, ground_node_id, "ALLEGES_GROUND")

            # 5. Era Node & Edge
            era_node_id = f"era:{era}"
            self._add_node(era_node_id, "era", era)
            self._add_edge(case_node_id, era_node_id, "IN_ERA")

            # 6. Outcome Node & Edge
            outcome_node_id = f"outcome:{disposal}"
            self._add_node(outcome_node_id, "outcome", disposal)
            self._add_edge(case_node_id, outcome_node_id, "HAD_OUTCOME")

        self.is_built = True
        logger.info(
            f"Knowledge Graph built: {len(self.nodes)} nodes ({len(self.cases_by_id)} cases), "
            f"{len(self.edges)} edges."
        )

    def get_graph_summary(self) -> Dict[str, Any]:
        """Returns structural statistics of the knowledge graph."""
        type_counts = Counter(n["type"] for n in self.nodes.values())
        top_sections = sorted(
            [n for n in self.nodes.values() if n["type"] == "section"],
            key=lambda x: x["degree"],
            reverse=True,
        )[:10]
        top_courts = sorted(
            [n for n in self.nodes.values() if n["type"] == "court"],
            key=lambda x: x["degree"],
            reverse=True,
        )[:10]
        top_judges = sorted(
            [n for n in self.nodes.values() if n["type"] == "judge"],
            key=lambda x: x["degree"],
            reverse=True,
        )[:10]

        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": dict(type_counts),
            "top_sections": [{"name": s["label"], "cases_citing": s["degree"]} for s in top_sections],
            "top_courts": [{"name": c["label"], "cases_decided": c["degree"]} for c in top_courts],
            "top_judges": [{"name": j["label"], "cases_heard": j["degree"]} for j in top_judges],
        }

    def get_case_neighborhood(self, doc_id: str, limit_similar: int = 5) -> Dict[str, Any]:
        """Returns the 1-hop and 2-hop graph neighborhood for a case."""
        case_node_id = f"case:{doc_id}"
        if case_node_id not in self.nodes:
            return {"error": f"Case {doc_id} not found in Knowledge Graph"}

        case_info = self.nodes[case_node_id]["properties"]
        direct_edges = self.adj[case_node_id]

        entities: Dict[str, List[str]] = defaultdict(list)
        connected_node_ids = set()

        for e in direct_edges:
            target = self.nodes.get(e["target"])
            if target:
                connected_node_ids.add(e["target"])
                entities[target["type"]].append(target["label"])

        # Find structurally similar cases via 2-hop shared entities (Jaccard similarity on entities)
        shared_case_counts: Counter[str] = Counter()
        for e in direct_edges:
            target_id = e["target"]
            # All other cases connected to this entity
            for back_edge in self.rev_adj[target_id]:
                other_case_id = back_edge["source"]
                if other_case_id != case_node_id and other_case_id.startswith("case:"):
                    shared_case_counts[other_case_id] += 1

        similar_cases = []
        for other_id, shared_cnt in shared_case_counts.most_common(limit_similar):
            other_node = self.nodes.get(other_id)
            if other_node:
                p = other_node["properties"]
                similar_cases.append({
                    "doc_id": p.get("doc_id"),
                    "title": other_node["label"],
                    "year": p.get("year"),
                    "court": p.get("court"),
                    "ground": p.get("ground"),
                    "disposal": p.get("disposal"),
                    "shared_graph_connections": shared_cnt,
                    "url": p.get("url"),
                })

        return {
            "case": case_info,
            "connected_entities": dict(entities),
            "similar_cases_via_graph": similar_cases,
            "total_direct_relations": len(direct_edges),
        }

    def score_cases_by_query_entities(self, query: str) -> Dict[str, float]:
        """Calculates a graph-relevance score multiplier for each case based on

        entities extracted from the search query.
        """
        extracted = EntityResolver.extract_entities_from_text(query)
        target_nodes: Set[str] = set()

        # Resolve extracted courts to node IDs
        for c in extracted["courts"]:
            target_nodes.add(f"court:{c}")
        # Resolve extracted grounds to node IDs
        for g in extracted["grounds"]:
            target_nodes.add(f"ground:{g}")
        # Resolve extracted sections to node IDs
        for s in extracted["sections"]:
            target_nodes.add(f"section:{s}")

        if not target_nodes:
            return {}

        scores: Dict[str, float] = defaultdict(float)
        for t_node in target_nodes:
            if t_node in self.nodes:
                for back in self.rev_adj[t_node]:
                    case_node_id = back["source"]
                    doc_id = case_node_id.replace("case:", "")
                    # Weight section / ground matches more heavily than court
                    weight = 1.5 if t_node.startswith("ground:") or t_node.startswith("section:") else 0.8
                    scores[doc_id] += weight

        # Normalize scores between 0.0 and 1.0
        if scores:
            max_val = max(scores.values())
            for k in scores:
                scores[k] = round(scores[k] / max_val, 4)

        return dict(scores)


# Global singleton instance of Knowledge Graph
_GLOBAL_KG: Optional[Section10KnowledgeGraph] = None


def get_knowledge_graph() -> Section10KnowledgeGraph:
    """Returns the singleton Section 10 Knowledge Graph."""
    global _GLOBAL_KG
    if _GLOBAL_KG is None:
        _GLOBAL_KG = Section10KnowledgeGraph()
    return _GLOBAL_KG
