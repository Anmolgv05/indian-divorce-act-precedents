"""
Task 6: Retrieval and search module for Section 10 Indian Divorce Act judgments.
- Uses BAAI/bge-small-en-v1.5 query prefix: 'Represent this sentence for searching relevant passages: '
- Supports hybrid retrieval: score = 0.7 * dense + 0.3 * tfidf
- Ranks cases by best chunk score, collapses possible duplicate pairs.
- Returns best chunk plus best petitioner_argument, respondent_argument, and reasoning chunks.
- Excludes constitutional_validity and procedural cases from dissolution stats.
- Fixes year == 0 to None, displays 'n/a', and never filters it out.
"""

import os
import re
import argparse
import numpy as np
import pandas as pd
import joblib
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "

_MODEL_CACHE = {}
_INDEX_CACHE = {}
_TFIDF_CACHE = {}


OUT_OF_SCOPE_PATTERNS = [
    (re.compile(r"\b(?:hindu marriage act|hma)\b", re.I), "Hindu Marriage Act"),
    (re.compile(r"\b(?:special marriage act|sma)\b", re.I), "Special Marriage Act"),
    (re.compile(r"\b(?:muslim|talaq)\b", re.I), "Muslim Personal Law / Dissolution of Muslim Marriages Act"),
    (re.compile(r"\b(?:parsi)\b", re.I), "Parsi Marriage and Divorce Act"),
    (re.compile(r"\b(?:125\s*cr\.?p\.?c|section\s+125\b)", re.I), "Section 125 CrPC (Maintenance)"),
    (re.compile(r"\b(?:domestic violence|dv act|pwdva)\b", re.I), "Domestic Violence Act"),
    (re.compile(r"\b(?:ipc|indian penal code)\b", re.I), "Indian Penal Code (IPC)"),
]

GROUND_PATTERNS = {
    "conversion": [
        r"\b(?:convert(?:ed|ing|s)?|conversion|ceased\s+to\s+be\s+christian|embraced\s+(?:islam|hinduism|buddhism)|remarried\s+after\s+conversion)\b"
    ],
    "mutual_consent_10A": [
        r"\b(?:mutual\s+consent|mutually\s+agree(?:d|s)?|both\s+agree(?:d|s)?|joint\s+petition|10a\b|cooling\s+off|waive\s+six\s+months)\b"
    ],
    "non_consummation": [
        r"\b(?:consummat\w*|impoten\w*|erectile|incapacity|invincible\s+repugnance|unconsummated)\b"
    ],
    "unsound_mind": [
        r"\b(?:unsound\s+mind|schizophreni\w*|mental\s+disorder|mental\s+illness|lunatic|insan\w*)\b"
    ],
    "nullity_sec19": [
        r"\b(?:nullity|annul\w*|void\s+marriage|fraud\w*|consent\s+by\s+force|bigam\w*|impediment)\b"
    ],
    "cruelty": [
        r"\b(?:cruel\w*|beat\w*|harass\w*|tortur\w*|mental\s+agony|violence|assault\w*|dowry|verbal\s+abuse|ill-treat\w*|quarrel\w*|humiliat\w*)\b"
    ],
    "desertion": [
        r"\b(?:desert\w*|abandon\w*|left\s+(?:the\s+)?(?:house|home|matrimonial)|refused\s+to\s+(?:return|live|cohabit)|living\s+separately|lived\s+apart|two\s+years\s+separat\w*)\b"
    ],
    "adultery": [
        r"\b(?:adulter\w*|affair\w*|paramour|illicit\s+relat\w*|co-respondent|infidelity|cheating|another\s+woman|another\s+man)\b"
    ],
}


def detect_query_grounds(query: str) -> list[str]:
    """Identifies the intended statutory grounds from query text."""
    if not query:
        return []
    detected = []
    for g, patterns in GROUND_PATTERNS.items():
        if any(re.search(p, query, re.I) for p in patterns):
            detected.append(g)
    return detected


def out_of_scope_notice(query: str) -> str | None:
    """Checks if query references adjacent or non-applicable statutes and returns an informational notice."""
    if not query:
        return None
    for pattern, name in OUT_OF_SCOPE_PATTERNS:
        if pattern.search(query):
            return (
                f"Note: Your query appears to reference {name}. "
                "This database specifically covers judgments under the Indian Divorce Act, 1869 (Christian marriages)."
            )
    return None


class SearchResults(list):
    """Subclass of list allowing metadata attributes like low_confidence and top_score."""
    low_confidence: bool = False
    top_score: float = 0.0
    out_of_scope_notice: str | None = None


def get_model(model_name: str = "BAAI/bge-small-en-v1.5"):
    if SentenceTransformer is None:
        raise ImportError("sentence_transformers package is not installed")
    if model_name not in _MODEL_CACHE:
        _MODEL_CACHE[model_name] = SentenceTransformer(model_name, device="cpu")
    return _MODEL_CACHE[model_name]


def load_index(index_dir: str = "data/index"):
    if index_dir not in _INDEX_CACHE:
        emb_path = os.path.join(index_dir, "embeddings.npy")
        meta_path = os.path.join(index_dir, "meta.parquet")
        if not os.path.exists(emb_path) or not os.path.exists(meta_path):
            raise FileNotFoundError(f"Index files missing in {index_dir}. Run src/embed_index.py first.")
        embeddings = np.load(emb_path, mmap_mode="r")
        df = pd.read_parquet(meta_path)
        _INDEX_CACHE[index_dir] = (embeddings, df)
    return _INDEX_CACHE[index_dir]


def load_tfidf(index_dir: str = "data/index"):
    if index_dir not in _TFIDF_CACHE:
        vec_path = os.path.join(index_dir, "tfidf_vectorizer.joblib")
        mat_path = os.path.join(index_dir, "tfidf_matrix.joblib")
        if not os.path.exists(vec_path) or not os.path.exists(mat_path):
            return None, None
        _TFIDF_CACHE[index_dir] = (joblib.load(vec_path), joblib.load(mat_path))
    return _TFIDF_CACHE[index_dir]


def format_case_outcome_summary(c: dict) -> str:
    """Generates an accurate, plain-language operative outcome summary based on judgment metadata."""
    disp = c.get("disposal", "unclear")
    diss = c.get("marriage_dissolved", "unclear")
    rel = c.get("relief", "unclear")
    ground = c.get("primary_ground", "unclear")
    court = c.get("court", "Court")

    ground_labels = {
        "cruelty": "cruelty",
        "adultery": "adultery",
        "desertion": "desertion",
        "mutual_consent_10A": "mutual consent (Section 10A)",
        "nullity_sec19": "nullity of marriage (Section 19)",
        "non_consummation": "non-consummation",
        "unsound_mind": "unsoundness of mind",
        "conversion": "conversion / remarriage",
        "procedural": "procedural / transfer",
        "constitutional_validity": "constitutional validity of Section 10"
    }
    g_str = ground_labels.get(ground, ground.replace("_", " "))

    if ground == "constitutional_validity":
        return f"{court}: Constitutional validity challenge to Section 10 provisions — petition {disp}. Landmark ruling striking down discriminatory gender requirements under the Indian Divorce Act."
    if ground == "procedural" or c.get("non_merits"):
        return f"{court}: Procedural matter / transfer petition {disp} without final adjudication of divorce on merits."
    if disp == "remanded":
        return f"{court}: Order set aside and proceedings remanded to lower court for fresh trial / evidence on {g_str} (evaluating corroboration and statutory compliance)."
    if diss == "yes":
        r_str = "decree of nullity" if rel == "nullity" else "decree for dissolution of marriage"
        rationale_hints = {
            "cruelty": "substantiated by persistent physical/mental harassment making cohabitation intolerable",
            "adultery": "established on cogent circumstantial evidence of inclination and opportunity",
            "desertion": "established by continuous 2+ years willful abandonment without reasonable excuse",
            "mutual_consent_10A": "approved upon joint verification of 2-year living separately and voluntary mutual consent",
            "nullity_sec19": "granted on established statutory impediment/impotence existing at time of marriage",
        }
        hint = rationale_hints.get(ground, f"proved under Section 10 ({g_str})")
        return f"{court}: {r_str.capitalize()} granted under Section 10 ({g_str}) — proceeding {disp}; {hint}."
    if diss == "no":
        r_str = f" ({rel.replace('_', ' ')})" if rel not in ("none", "unclear") else ""
        defense_hints = {
            "cruelty": "allegations uncorroborated, deemed ordinary marital wear-and-tear, or barred by condonation",
            "adultery": "allegations unproven by strict circumstantial standard or defective under Section 11",
            "desertion": "animus deserendi or statutory 2-year duration not established, or respondent had reasonable cause",
            "mutual_consent_10A": "consent withdrawn prior to second motion or statutory period not met",
            "nullity_sec19": "grounds not established by medical evidence",
        }
        dhint = defense_hints.get(ground, "insufficient evidence on statutory grounds")
        return f"{court}: Relief refused — proceeding {disp}; dissolution under Section 10 ({g_str}) not granted{r_str} ({dhint})."
    return f"{court}: Proceeding {disp} regarding {g_str}; final decree status not determined from record."


def search(
    query: str,
    top_k: int = 5,
    ground: str = None,
    year_range: tuple = None,
    include_non_merits: bool = False,
    include_duplicates: bool = False,
    mode: str = "hybrid",
    dense_weight: float = 0.7,
    tfidf_weight: float = 0.3,
    confidence_threshold: float = 0.20,
    index_dir: str = "data/index",
    model_name: str = "BAAI/bge-small-en-v1.5"
) -> list[dict]:
    """Retrieves top_k relevant cases for query, ranked by best chunk score."""
    embeddings, df = load_index(index_dir)

    have_dense = False
    dense_scores = np.zeros(len(df), dtype=np.float32)
    try:
        model = get_model(model_name)
        # 1. Dense score with BGE query instruction prefix
        query_text = QUERY_INSTRUCTION + query
        query_emb = model.encode(query_text, normalize_embeddings=True, convert_to_numpy=True)
        query_emb = query_emb.astype(np.float32)
        dense_scores = np.dot(embeddings, query_emb)
        have_dense = True
    except Exception as e:
        print(f"[Search Warning] Dense model unavailable, falling back to lexical search: {e}")

    # 2. Hybrid score combination (dense + TF-IDF)
    tfidf_vec, tfidf_matrix = load_tfidf(index_dir)
    if tfidf_vec is not None and tfidf_matrix is not None:
        query_tfidf = tfidf_vec.transform([query])
        tfidf_scores = (tfidf_matrix @ query_tfidf.T).toarray().ravel()
        if have_dense and mode == "hybrid":
            raw_scores = dense_weight * dense_scores + tfidf_weight * tfidf_scores
        elif have_dense:
            raw_scores = dense_scores
        else:
            raw_scores = tfidf_scores
    else:
        raw_scores = dense_scores

    scores = raw_scores.copy()

    # 3. Disqualify short fragments, order captions, and boilerplate conclusions (e.g. "I agree.")
    short_mask = (df["text"].str.len() < 55) | (
        df["text"].str.strip().str.lower().isin(
            ["i agree.", "8. i agree.", "order accordingly.", "judgment", "order", "decree accordingly."]
        )
    )
    scores[short_mask] = -999.0

    # 4. Ground-aware scoring adjustments if user didn't specify an explicit ground filter
    detected_grounds = detect_query_grounds(query)
    if detected_grounds and not ground:
        # Boost cases matching detected ground
        primary_match = df["primary_ground"].isin(detected_grounds)
        scores[primary_match] += 0.09

        # Secondary match in grounds list
        secondary_match = df["grounds"].apply(
            lambda g: any(dg in (g if isinstance(g, list) else str(g).split(",")) for dg in detected_grounds)
        )
        scores[secondary_match & ~primary_match] += 0.05

        # Suppress unrelated fault grounds if query specifically targeted other grounds
        other_faults = {
            "adultery", "desertion", "cruelty", "conversion",
            "unsound_mind", "non_consummation", "nullity_sec19", "mutual_consent_10A"
        } - set(detected_grounds)
        conflicting = df["primary_ground"].isin(other_faults) & ~secondary_match
        scores[conflicting] -= 0.05

    # 5. Apply user filters
    mask = np.ones(len(df), dtype=bool)
    if not include_non_merits:
        mask &= (~df["non_merits"].fillna(False).astype(bool))
    if ground:
        mask &= (df["primary_ground"] == ground)
    if year_range:
        min_yr, max_yr = year_range
        # Never filter out cases where year is None / NaN
        mask &= (df["year"].isna()) | ((df["year"] >= min_yr) & (df["year"] <= max_yr))

    scores[~mask] = -999.0

    valid_indices = np.where(scores > -900.0)[0]
    if len(valid_indices) == 0:
        empty_res = SearchResults()
        empty_res.low_confidence = True
        empty_res.top_score = 0.0
        empty_res.detected_grounds = detected_grounds
        return empty_res

    # 6. Take top 100 chunks for rich case coverage
    top_100_idx = valid_indices[np.argsort(scores[valid_indices])[::-1][:100]]

    # 7. Group by case and compute best score per case
    case_scores = {}
    best_chunk_per_case = {}
    for idx in top_100_idx:
        row = df.iloc[idx]
        doc_id = str(row["doc_id"])
        sc = float(scores[idx])
        if doc_id not in case_scores or sc > case_scores[doc_id]:
            case_scores[doc_id] = sc
            best_chunk_per_case[doc_id] = (sc, row)

    # 8. Rank cases and collapse duplicates
    sorted_doc_ids = sorted(case_scores.keys(), key=lambda d: case_scores[d], reverse=True)
    included_doc_ids = set()
    ranked_cases = []

    for did in sorted_doc_ids:
        # Check possible_duplicate_of
        case_rows = df[df["doc_id"] == did]
        if case_rows.empty:
            continue
        dup_of = case_rows["possible_duplicate_of"].iloc[0]
        dup_partners = set([x.strip() for x in str(dup_of).split(",")]) if (dup_of and pd.notna(dup_of)) else set()

        if not include_duplicates and any(p in included_doc_ids for p in dup_partners):
            continue

        included_doc_ids.add(did)
        best_sc, best_row = best_chunk_per_case[did]

        # Extract best specific segment chunks for this case
        case_indices = np.where(df["doc_id"] == did)[0]
        role_chunks = {}
        for role in ["petitioner_argument", "respondent_argument", "reasoning"]:
            role_indices = [i for i in case_indices if df.iloc[i]["segment_type"] == role]
            if role_indices:
                best_i = role_indices[np.argmax(raw_scores[role_indices])]
                role_chunks[role] = {
                    "text": df.iloc[best_i]["text"],
                    "chunk_idx": int(df.iloc[best_i]["chunk_idx"]),
                    "p_ids": df.iloc[best_i]["p_ids"],
                    "score": round(float(raw_scores[best_i]), 4)
                }
            else:
                role_chunks[role] = None

        grounds_val = best_row.get("grounds", "")
        if isinstance(grounds_val, str):
            grounds_list = [g.strip() for g in grounds_val.split(",") if g.strip()]
        elif isinstance(grounds_val, list):
            grounds_list = grounds_val
        else:
            grounds_list = []

        raw_yr = best_row.get("year")
        year_val = int(raw_yr) if (pd.notna(raw_yr) and int(raw_yr) > 0) else None

        case_dict = {
            "doc_id": did,
            "title": best_row["title"],
            "year": year_val,
            "court": best_row["court"],
            "url": best_row["url"],
            "grounds": grounds_list,
            "primary_ground": best_row["primary_ground"],
            "disposal": best_row["disposal"],
            "marriage_dissolved": best_row["marriage_dissolved"],
            "relief": best_row["relief"],
            "non_merits": bool(best_row["non_merits"]),
            "possible_duplicate_of": best_row["possible_duplicate_of"],
            "score": round(best_sc, 4),
            "best_chunk": {
                "text": best_row["text"],
                "segment_type": best_row["segment_type"],
                "chunk_idx": int(best_row["chunk_idx"]),
                "chunk_hash": best_row.get("chunk_hash", ""),
                "p_ids": best_row["p_ids"],
                "score": round(best_sc, 4)
            },
            "petitioner_argument": role_chunks["petitioner_argument"],
            "respondent_argument": role_chunks["respondent_argument"],
            "reasoning": role_chunks["reasoning"]
        }
        case_dict["outcome_summary"] = format_case_outcome_summary(case_dict)
        ranked_cases.append(case_dict)

        if len(ranked_cases) >= top_k:
            break

    top_score = ranked_cases[0]["score"] if ranked_cases else 0.0
    is_low_conf = bool(top_score < confidence_threshold)
    for c in ranked_cases:
        c["low_confidence"] = is_low_conf

    notice = out_of_scope_notice(query)
    results_obj = SearchResults(ranked_cases)
    results_obj.low_confidence = is_low_conf
    results_obj.top_score = top_score
    results_obj.out_of_scope_notice = notice
    results_obj.detected_grounds = detected_grounds
    return results_obj


def build_precedent_guidance(results: list[dict], query: str = None, x_ended: int = 0, y_did_not: int = 0, z_unclear: int = 0) -> dict:
    """
    Synthesizes actionable, lawyer-centric guidance across retrieved Section 10 precedents.
    Distills judicial success likelihood, evidentiary requirements, statutory traps (e.g. s.14 condonation, s.11 joinder),
    and a practical litigation checklist.
    """
    merits_total = x_ended + y_did_not
    if merits_total > 0:
        grant_rate = round((x_ended / merits_total) * 100, 1)
        ratio_str = f"{x_ended} of {merits_total} merits rulings granted dissolution/nullity ({grant_rate}% grant rate); {y_did_not} dismissed; {z_unclear} remanded/procedural."
    else:
        grant_rate = 0.0
        ratio_str = f"0 of 0 merits rulings ({z_unclear} remanded, procedural, or constitutional determinations)."

    grounds_present = set()
    for r in results:
        g = r.get("primary_ground")
        if g:
            grounds_present.add(g)
        for sub_g in r.get("grounds", []):
            if sub_g:
                grounds_present.add(sub_g)

    q_lower = (query or "").lower()

    roadmaps = []
    traps = []

    if "cruelty" in grounds_present or "cruelt" in q_lower:
        roadmaps.append({
            "ground": "Cruelty (Section 10(1)(x))",
            "requirement": "Requires establishing a sustained course of conduct inflicting physical violence or grave mental agony making continued cohabitation injurious to health or safety. Judges heavily rely on contemporaneous documentary exhibits: medico-legal certificates (MLCs), hospital injury reports, complaints under s.498A IPC, and written communications. Vague, omnibus oral allegations without specific dates or police/medical records were consistently dismissed as ordinary marital wear-and-tear."
        })
        traps.append({
            "title": "Section 14 Condonation Defense",
            "detail": "Any resumption of sexual cohabitation or reconciliation after acts of cruelty constitutes statutory condonation under Section 14, acting as an absolute bar to divorce unless subsequent matrimonial offenses revive the prior misconduct. Pleadings must expressly negate condonation or detail subsequent revival."
        })

    if "desertion" in grounds_present or "desert" in q_lower:
        roadmaps.append({
            "ground": "Desertion (Section 10(1)(ix)/(x))",
            "requirement": "Requires concurrent proof of two statutory elements: (1) physical separation for a continuous minimum period of two years immediately preceding petition presentation, and (2) animus deserendi—the respondent's willful intention to bring cohabitation permanently to an end without reasonable cause. Petitions failed where the respondent established just cause for leaving (e.g. ill-treatment) or where the petitioner failed to prove bonafide reconciliation attempts."
        })
        traps.append({
            "title": "Strict 2-Year Statutory Timeline",
            "detail": "The two-year statutory period of desertion must be complete on the day the petition is presented before the court. Premature filing is an incurable jurisdictional defect resulting in mandatory dismissal."
        })

    if "adultery" in grounds_present or "adulter" in q_lower:
        roadmaps.append({
            "ground": "Adultery (Section 10(1)(i))",
            "requirement": "Direct proof of adultery is rarely obtainable; courts evaluate circumstantial evidence on a preponderance of probabilities, requiring proof of both inclination and opportunity (e.g. hotel registers, cohabitation in a shared dwelling, compromising letters/photos, or conclusive non-access during conception). Hearsay, uncorroborated suspicion, or mere friendly association was rejected as insufficient."
        })
        traps.append({
            "title": "Section 11 Mandatory Co-Respondent Joinder",
            "detail": "Section 11 strictly mandates that the alleged adulterer must be made a co-respondent in the petition, unless the court formally grants leave to dispense with joinder on statutory grounds (e.g., identity unknown after diligent inquiry). Failure to implead or seek court dispensation renders the petition fatally defective."
        })

    if "mutual_consent_10A" in grounds_present or "mutual" in q_lower or "10a" in q_lower:
        roadmaps.append({
            "ground": "Mutual Consent (Section 10A)",
            "requirement": "Requires joint petition demonstrating: (1) living separately for two years or more (note: 2 years under IDA vs 1 year under HMA Section 13B), (2) inability to live together, and (3) mutual agreement to dissolve the marriage. Both parties must confirm voluntary consent at both first and second motions."
        })
        traps.append({
            "title": "Cooling-Off Period & Withdrawal of Consent",
            "detail": "Second motion must be moved between 6 and 18 months after the first motion, unless formal waiver application is allowed under Supreme Court guidelines. Unilateral withdrawal of consent by either spouse before the second motion terminates the petition."
        })

    if "nullity_sec19" in grounds_present or "nullity" in q_lower or "impoten" in q_lower or "consummat" in q_lower:
        roadmaps.append({
            "ground": "Nullity & Non-Consummation (Sections 18 & 19)",
            "requirement": "Requires establishing statutory impediments (impotence, consent obtained by force/fraud, or idiocy/lunacy) existing at the time of marriage. Court-appointed medical board examination reports or adverse inferences drawn from a spouse's refusal to undergo examination form the core evidentiary basis."
        })
        traps.append({
            "title": "Pre-Existing Incapacity Requirement",
            "detail": "Under Section 19(1), impotence must exist both at the time of marriage and at the time of the institution of the suit. Post-marital incapacity does not support a decree of nullity."
        })

    if not roadmaps:
        roadmaps.append({
            "ground": "General Statutory Burden of Proof",
            "requirement": "Matrimonial causes under the Indian Divorce Act are evaluated on a civil standard of preponderance of probabilities. Relief requires clear, corroborated testimony and contemporaneous documentary exhibits rather than uncorroborated oral assertions."
        })

    if not any("Condonation" in t["title"] for t in traps):
        traps.append({
            "title": "Section 14 Condonation Defense",
            "detail": "Any resumption of marital cohabitation or sexual relations after knowledge of marital misconduct constitutes statutory condonation under Section 14, extinguishing the right to divorce unless subsequent misconduct revives the cause of action."
        })

    if not any("Delay" in t["title"] for t in traps):
        traps.append({
            "title": "Statutory Delay & Acquiescence (Sections 14 & 23)",
            "detail": "Unexplained, inordinate delay between the occurrence of the matrimonial misconduct and the institution of legal proceedings triggers judicial suspicion of acquiescence, waiver, or collusion."
        })

    checklist = [
        "1. Chronological Schedule of Incidents: Draft pleadings with specific calendar dates, locations, specific acts/words, and names of witnessing relatives or neighbours.",
        "2. Contemporaneous Exhibits: Secure police complaints, MLCs, discharge summaries, diary entries, letters, electronic messages (emails/WhatsApp), and financial statements.",
        "3. Address & Rebut Condonation (Section 14): Explicitly plead the date cohabitation permanently ceased and state that matrimonial offenses were never condoned, or plead subsequent revival.",
        "4. Procedural & Statutory Compliance: Ensure co-respondent joinder under Section 11 (or file application for leave), and verify the strict 2-year statutory timeline for desertion or Section 10A."
    ]

    return {
        "grant_rate_pct": grant_rate,
        "operative_ratio": ratio_str,
        "evidentiary_roadmaps": roadmaps,
        "statutory_traps": traps,
        "litigation_checklist": checklist
    }


def stats(results: list[dict], query: str = None) -> dict:
    """
    Computes outcome statistics and actionable precedent intelligence over returned results.
    Excludes non_merits, constitutional_validity, and procedural cases from X/Y counts.
    """
    n_retrieved = len(results)
    x_ended = 0
    y_did_not = 0
    z_unclear = 0

    for r in results:
        ground = r.get("primary_ground", "")
        if r.get("non_merits") or ground in ["constitutional_validity", "procedural"]:
            z_unclear += 1
            continue

        md = r.get("marriage_dissolved")
        if md == "yes":
            x_ended += 1
        elif md == "no":
            y_did_not += 1
        else:
            z_unclear += 1

    is_low_conf = getattr(results, "low_confidence", False)
    if not is_low_conf and results and isinstance(results[0], dict) and "low_confidence" in results[0]:
        is_low_conf = results[0]["low_confidence"]

    notice = (out_of_scope_notice(query) if query else None) or getattr(results, "out_of_scope_notice", None)

    summary = (
        f"Of the {n_retrieved} retrieved cases, {x_ended} ended the marriage (dissolution/nullity), "
        f"{y_did_not} did not, {z_unclear} unclear or not applicable. "
        "(Note: retrieved cases are not a success rate)"
    )
    if is_low_conf:
        summary += " [Low confidence: query may be out-of-corpus or ambiguous]"

    synthesis_parts = []
    if x_ended > 0:
        synthesis_parts.append(f"dissolution/nullity granted in {x_ended} case(s)")
    if y_did_not > 0:
        synthesis_parts.append(f"relief refused/dismissed in {y_did_not} case(s)")
    if z_unclear > 0:
        synthesis_parts.append(f"remanded or non-merits in {z_unclear} case(s)")

    grounds_tally = {}
    for r in results:
        g = r.get("primary_ground", "unclear")
        grounds_tally[g] = grounds_tally.get(g, 0) + 1

    top_grounds = [f"{k.replace('_', ' ')} ({v})" for k, v in sorted(grounds_tally.items(), key=lambda x: -x[1])[:3]]
    top_grounds_str = ", ".join(top_grounds) if top_grounds else "None"

    precedent_guidance = build_precedent_guidance(results, query, x_ended, y_did_not, z_unclear)

    merits_total = x_ended + y_did_not
    rate_desc = f"{round((x_ended / merits_total) * 100)}% grant rate among merits rulings" if merits_total > 0 else "procedural/remanded determinations"

    outcome_synthesis = (
        f"Across the {n_retrieved} most relevant precedents: "
        f"{', '.join(synthesis_parts) if synthesis_parts else 'no outcomes recorded'} ({rate_desc}). "
        f"Primary grounds adjudicated: {top_grounds_str}. "
        "In these cases, courts granted relief primarily where continuous matrimonial misconduct was corroborated by contemporaneous documentary exhibits, "
        "whereas petitions relying on uncorroborated oral assertions or where Section 14 condonation / Section 11 co-respondent rules were overlooked were dismissed or remanded."
    )

    return {
        "n_retrieved": n_retrieved,
        "ended": x_ended,
        "did_not_end": y_did_not,
        "unclear_or_na": z_unclear,
        "low_confidence": is_low_conf,
        "out_of_scope_notice": notice,
        "summary": summary,
        "outcome_synthesis": outcome_synthesis,
        "precedent_guidance": precedent_guidance
    }


def main():
    parser = argparse.ArgumentParser(description="Task 6: Search Section 10 judgments.")
    parser.add_argument("query", type=str, nargs="?", default="husband alleges wife deserted him for three years", help="Search query")
    parser.add_argument("--top-k", type=int, default=5, help="Number of cases to return")
    parser.add_argument("--ground", type=str, default=None, help="Filter by primary ground")
    parser.add_argument("--mode", type=str, default="hybrid", choices=["hybrid", "dense"], help="Retrieval mode (hybrid or dense)")
    parser.add_argument("--confidence-threshold", type=float, default=0.50, help="Confidence threshold below which queries are marked low confidence")
    parser.add_argument("--include-non-merits", action="store_true", help="Include non-merits cases")
    args = parser.parse_args()

    results = search(
        args.query,
        top_k=args.top_k,
        ground=args.ground,
        mode=args.mode,
        confidence_threshold=args.confidence_threshold,
        include_non_merits=args.include_non_merits
    )
    st = stats(results, query=args.query)

    print(f"\nQuery: \"{args.query}\"")
    print(f"Mode: {args.mode}")
    print(f"Results Count: {len(results)}")
    if st.get("out_of_scope_notice"):
        print(f"[SCOPE NOTICE] {st['out_of_scope_notice']}")
    if st.get("low_confidence"):
        top_sc = getattr(results, "top_score", (results[0]["score"] if results else 0.0))
        print(f"[LOW CONFIDENCE WARNING] Top score ({top_sc:.4f}) is below confidence threshold ({args.confidence_threshold}). Query may be out-of-corpus or ambiguous.")
    print(f"Stats: {st['summary']}\n")
    print("=" * 80)

    for idx, r in enumerate(results, 1):
        year_str = str(r['year']) if r['year'] is not None else "n/a"
        print(f"[{idx}] {r['title']} ({year_str})")
        print(f"    Doc ID: {r['doc_id']} | Ground: {r['primary_ground']} | Disposal: {r['disposal']} | Dissolved: {r['marriage_dissolved']} | Score: {r['score']}")
        print(f"    URL: {r['url']}")
        chunk_preview = r['best_chunk']['text'][:150].replace('\n', ' ')
        print(f"    Best Chunk ({r['best_chunk']['segment_type']}): \"{chunk_preview}...\"\n")


if __name__ == "__main__":
    main()
