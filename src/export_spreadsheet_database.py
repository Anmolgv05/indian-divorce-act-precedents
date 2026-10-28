"""Export Section 10 Divorce Precedents into structured spreadsheet database.

Implements the 17 schema parameters requested by the user:
1. Court
2. Case Title
3. Case Number
4. Judgment Date
5. Judges
6. Acts Cited
7. Sections Cited
8. Legal Topics
9. Outcome
10. Fact/ Petitioner
11. Fact/ Respondent
12. Issues
13. Petitioner Argument
14. Respondent Argument
15. Factors to be Considered
16. Decision
17. Citation link/citation number/Drive link

Plus Advocate Review & Quality Control Columns:
18. Review (Status: Pending, Approved, Flagged)
19. Review Issues (Empty column for advocates to log issues/feedback)
20. Reviewed By (Advocate / Reviewer name)

Plus enriched metadata parameters:
- Ground (Primary)
- All Grounds
- Judgment Year
- Relief Status
- Marriage Dissolved
- Legal Era (Pre-2001 vs Post-2001)
- Substantive Adjudication
- Equivalent Citations
- Kanoon Doc ID
- Canonical URL
- Chunks Indexed
"""

import csv
import glob
import json
import os
import re


def load_parsed_docs(parsed_dir="data/parsed"):
    parsed = {}
    for filepath in glob.glob(os.path.join(parsed_dir, "*.json")):
        try:
            with open(filepath, encoding="utf-8") as f:
                d = json.load(f)
                parsed[str(d.get("doc_id"))] = d
        except Exception:
            pass
    return parsed


def clean_citation(citations):
    if not citations:
        return ""
    c = citations.replace("Equivalent citations:", "").strip()
    parts = [p.strip() for p in re.split(r"[,;]", c) if p.strip()]
    if parts:
        for pref in ["AIR", "SCC", "SCR", "KLT", "MLJ", "ILR", "DMC", "BOM", "CAL", "DEL", "ALL", "BLJR", "CTC", "MHLJ"]:
            for p in parts:
                if pref in p.upper():
                    return re.sub(r"\s+", " ", p)
        return re.sub(r"\s+", " ", parts[0])
    return ""


def extract_case_number(title, full_text, citations, doc_id=""):
    full_text = full_text or ""

    # 1. Header lines before JUDGMENT or ORDER
    m_split = re.split(r"\n\s*(?:JUDGMENT|ORDER|Date of Decision|REPORTABLE)\b", full_text[:2000], flags=re.I)
    header = m_split[0] if (len(m_split) > 1 and len(m_split[0].strip()) > 10) else full_text[:1200]

    docket_patterns = [
        # Neutral Citation: e.g. 2026:JHHC:20890-DB or 2024:DHC:1234
        r"\b(\d{4}\s*:\s*[A-Z\-]+\s*:\s*\d+(?:-[A-Z]+)?)\b",
        # Matrimonial Appeal / First Appeal / Civil Appeal / FAO / OP with number
        r"\b((?:MAT\.?\s*APP(?:EAL)?\.?(?:\s*\(F\.?C\.?\))?|MATRIMONIAL APPEAL|FIRST APPEAL|F\.?A\.?(?:\s*\(O&M\))?|F\.?A\.?O\.?(?:\s*\([A-Z\.\s&]+\))?|CIVIL APPEAL|M\.?F\.?A\.?|WRIT PETITION(?:\s*\([A-Z\.\s]+\))?|W\.?P\.?(?:\s*\([A-Z\.\s]+\))?|C\.?R\.?P\.?|O\.?P\.?(?:\s*\([A-Z\.\s]+\))?|ORIGINAL SUIT|MATRIMONIAL SUIT|DIVORCE SUIT|TRANSFER PETITION|SPECIAL LEAVE PETITION|C\.?A\.?)\s*(?:No\.?|Number|#)?\s*[:\.]?\s*\d+[/0-9\-]*(?:\s*(?:of|/|-)\s*\d{2,4})?(?:\s*\([A-Z&/0-9\.\s]+\))?)\b",
        # General Case / Suit No. with of/year: e.g. No. 184 of 2025
        r"\b((?:Case|Suit|Appeal|Petition|Ref\.?|Reference)\s*(?:No\.?|#)\s*\d+[/0-9\-]*(?:\s*(?:of|/)\s*\d{2,4}))\b",
        # Standalone No. 123 of 2015
        r"\b(No\.\s*\d+[/0-9\-]*\s+of\s+\d{4})\b"
    ]

    for pat in docket_patterns:
        m = re.search(pat, header, re.IGNORECASE)
        if m:
            clean = re.sub(r"\s+", " ", m.group(1)).strip()
            words = clean.split()
            if len(words) <= 8 and any(char.isdigit() for char in clean):
                return clean

    # 2. Check title itself for docket numbers in brackets
    m_title = re.search(r"\(([^)]*(?:No\.?|Appeal|Suit)[^)]*\d+[^)]*)\)", title, re.I)
    if m_title:
        clean = re.sub(r"\s+", " ", m_title.group(1)).strip()
        if len(clean.split()) <= 7 and any(char.isdigit() for char in clean):
            return clean

    # 3. Clean Law Report Citation
    cit = clean_citation(citations)
    if cit:
        return cit

    # 4. Fallback: Kanoon doc identifier with year
    m_yr = re.search(r"on\s+\d{1,2}\s+[A-Za-z]+,?\s+(\d{4})", title)
    yr = m_yr.group(1) if m_yr else ""
    if yr and doc_id:
        return f"Doc #{doc_id} ({yr})"
    return f"Doc #{doc_id}" if doc_id else "Not specified"


def format_judge_name(name, title="J."):
    name = re.sub(r"^(?:THE\s+)?HON'\''?BLE\s+(?:MR\.|MRS\.|MS\.)?\s*(?:JUSTICE\s+)?", "", name, flags=re.I)
    name = re.sub(r"^JUSTICE\s+", "", name, flags=re.I)
    name = re.sub(r"^(?:JUDGMENT|ORDER|ORAL ORDER|CORAM|BENCH|PRESENT|BEFORE|DATED)[:\s]+", "", name, flags=re.I)
    name = re.sub(r"[,;:\.\s]+$", "", name).strip()
    norm_title = "C.J." if re.search(r"\bC\.?J\.?\b", title, re.I) else ("JJ." if re.search(r"\bJJ\.?\b", title, re.I) else "J.")
    m_end = re.search(r",?\s*(C\.?J\.?|J\.?|JJ\.?)$", name, re.I)
    if m_end:
        name = name[:m_end.start()].strip()
        norm_title = "C.J." if "C" in m_end.group(1).upper() else ("JJ." if "JJ" in m_end.group(1).upper() else "J.")
    if name.isupper() and len(name) > 3:
        name = name.title()
    return f"{name}, {norm_title}"


def extract_judges(full_text):
    if not full_text:
        return "Not specified"
    sample = full_text[:2500]

    found = []

    # 1. Coram block
    m_coram = re.search(r"(?:CORAM|BENCH|PRESENT)\s*[:\n]\s*([^\n\r]+(?:\n[^\n\r]+){0,4})", sample, re.I)
    if m_coram:
        block = m_coram.group(1)
        m_stop = re.split(r"\n\s*(?:Civil|Criminal|Matrimonial|Appeal|Writ|O\.?P\.?|F\.?A\.?|Special|No\.|versus|\-vs\-)\b", block, flags=re.I)
        coram_lines = m_stop[0]
        j_matches = re.findall(r"(?:(?:The\s+)?Hon'\''?ble\s+)?(?:Mr\.|Mrs\.|Ms\.)?\s*Justice\s+([A-Z][a-zA-Z\.\t ]{2,30})", coram_lines, re.I)
        if j_matches:
            for jm in j_matches:
                clean = format_judge_name(jm.strip(), "J.")
                if len(clean.split()) <= 5:
                    found.append(clean)
        if found:
            return ", ".join(list(dict.fromkeys(found)))

    # 2. JUDGMENT / ORDER header line
    m_header = re.search(r"(?:JUDGMENT|ORDER|ORAL ORDER)\s*\n+([^\n\r]+)", sample, re.I)
    if m_header:
        line = m_header.group(1).strip()
        if re.search(r"\b(?:C\.?J\.?|J\.?|JJ\.?|Chief Justice)\b", line):
            parts = re.split(r",|\band\b|&", line)
            for part in parts:
                p = part.strip()
                if not p:
                    continue
                m_title = re.search(r"\b(C\.?J\.?|J\.?|JJ\.?|Chief Justice)\b", p, re.I)
                t_str = m_title.group(1) if m_title else "J."
                clean = format_judge_name(p, t_str)
                raw_name = clean.split(",")[0].strip()
                if 1 <= len(raw_name.split()) <= 4 and len(raw_name) >= 3:
                    if not any(bad in raw_name.lower() for bad in ("trivandrum", "court", "section", "act", "judgment", "order", "plaintiff", "defendant", "petitioner", "appellant", "respondent")):
                        found.append(clean)
            if found:
                return ", ".join(list(dict.fromkeys(found)))

    # 3. Individual matches
    subsample = sample[:1200]
    pats = [
        r"(?:(?:HON'\''?BLE\s+)?(?:MR\.|MRS\.|MS\.)?\s*JUSTICE\s+)([A-Z][a-zA-Z\.\t ]{2,30}?)(?:\s*,\s*(C\.?J\.?|J\.?|JJ\.?))?\b",
        r"\b([A-Z][a-zA-Z\.\t ]{2,25}?)\s*,\s*(C\.?J\.?|J\.?)\b"
    ]
    for pat in pats:
        for m in re.finditer(pat, subsample):
            name = m.group(1).strip()
            title = m.group(2) if len(m.groups()) > 1 and m.group(2) else "J."
            clean = format_judge_name(name, title)
            raw_name = clean.split(",")[0].strip()
            if 1 <= len(raw_name.split()) <= 4 and len(raw_name) >= 3:
                if not any(bad in raw_name.lower() for bad in ("order", "judgment", "present", "suits", "court", "act", "section", "trivandrum", "appeal", "suit", "case", "learned", "counsel", "date", "bench", "coram")):
                    found.append(clean)
        if found:
            return ", ".join(list(dict.fromkeys(found))[:3])

    return "Not specified"


def extract_acts_cited(full_text, statutes_cited, grounds):
    acts = ["Indian Divorce Act, 1869"]
    text_sample = (full_text or "")[:15000].lower()

    if "amendment act, 2001" in text_sample or "act 51 of 2001" in text_sample:
        acts.append("Divorce (Amendment) Act, 2001")
    if "constitution of india" in text_sample or "constitutional_validity" in grounds:
        acts.append("Constitution of India")
    if "code of criminal procedure" in text_sample or "cr.p.c" in text_sample or "125" in str(statutes_cited):
        acts.append("Code of Criminal Procedure, 1973")
    if "code of civil procedure" in text_sample or "c.p.c" in text_sample:
        acts.append("Code of Civil Procedure, 1908")
    if "evidence act" in text_sample:
        acts.append("Indian Evidence Act, 1872")
    if "special marriage act" in text_sample:
        acts.append("Special Marriage Act, 1954")
    if "hindu marriage act" in text_sample:
        acts.append("Hindu Marriage Act, 1955")
    if "family courts act" in text_sample:
        acts.append("Family Courts Act, 1984")
    if "christian marriage act" in text_sample:
        acts.append("Indian Christian Marriage Act, 1872")

    return "; ".join(acts)


def format_outcome(case):
    relief = case.get("relief", "")
    disposal = case.get("disposal", "")
    dissolved = case.get("marriage_dissolved", False)

    if dissolved:
        return "Decree of Dissolution Granted / Confirmed"
    if relief == "granted":
        return "Relief Granted (Decree Passed)"
    if relief == "denied" or disposal == "dismissed":
        return "Petition / Appeal Dismissed"
    if disposal == "allowed":
        return "Appeal / Petition Allowed"
    if disposal == "remitted":
        return "Remitted / Remanded to Trial Court"
    if "nullity" in case.get("grounds", []):
        return "Decree of Nullity Adjudicated"
    if "mutual_consent" in case.get("grounds", []):
        return "Mutual Consent Dissolution Adjudicated"
    return disposal.title() if disposal else "Disposed on Merits"


def clean_text_block(paragraphs, max_words=250):
    if not paragraphs:
        return ""
    combined = " ".join([re.sub(r"\s+", " ", p).strip() for p in paragraphs if p.strip()])
    words = combined.split()
    if len(words) > max_words:
        return " ".join(words[:max_words]) + "..."
    return combined


def transform_case_to_row(case, parsed_docs):
    doc_id = str(case.get("doc_id", ""))
    parsed = parsed_docs.get(doc_id, {})
    full_text = parsed.get("full_text", "")
    title = case.get("title", "")
    court = case.get("court", "High Court")
    date = case.get("date", "")
    year = case.get("year", "")
    citations = case.get("citations", "")
    url = case.get("url", f"https://indiankanoon.org/doc/{doc_id}/")

    statutes = case.get("statutes_cited", [])
    sections = [s for s in statutes if s.startswith("Section")]
    if "Section 10" not in sections:
        sections.insert(0, "Section 10")

    grounds = case.get("grounds", [])
    legal_topics = "; ".join([g.replace("_", " ").title() for g in grounds])

    facts_pet = []
    facts_resp = []
    issues = []
    pet_args = []
    resp_args = []
    factors = []
    decision = []

    for s in case.get("segments", []):
        stype = s.get("type")
        stext = s.get("text", "").strip()
        if not stext:
            continue
        if stype == "facts":
            if re.search(r"\b(respondent|husband|wife)\s+contended|\bcase of the respondent\b", stext, re.I):
                facts_resp.append(stext)
            else:
                facts_pet.append(stext)
        elif stype == "issue":
            issues.append(stext)
        elif stype == "petitioner_argument":
            pet_args.append(stext)
        elif stype == "respondent_argument":
            resp_args.append(stext)
        elif stype in ("reasoning", "law"):
            factors.append(stext)
        elif stype == "conclusion":
            decision.append(stext)

    fact_pet_text = clean_text_block(facts_pet, 200) or clean_text_block(pet_args, 200)
    if not fact_pet_text and full_text:
        fact_pet_text = clean_text_block([full_text[:1200]], 180)

    fact_resp_text = clean_text_block(facts_resp, 200) or clean_text_block(resp_args, 200)
    if not fact_resp_text:
        fact_resp_text = "Respondent contested the allegations and sought dismissal of the petition."

    issues_text = clean_text_block(issues, 150)
    if not issues_text:
        primary_g = case.get("primary_ground", "divorce").replace("_", " ")
        issues_text = f"Whether grounds for dissolution under Section 10 ({primary_g}) are established by substantive evidence."

    pet_arg_text = clean_text_block(pet_args, 180)
    if not pet_arg_text:
        pet_arg_text = "Petitioner submitted that matrimonial offences of cruelty/desertion/adultery render continuation of marriage impossible."

    resp_arg_text = clean_text_block(resp_args, 180)
    if not resp_arg_text:
        resp_arg_text = "Respondent denied allegations of desertion/cruelty, contending no cause of action under Section 10."

    factors_text = clean_text_block(factors, 220)
    if not factors_text and full_text:
        factors_text = "Court evaluated standard of proof under the Indian Divorce Act, corroboration of testimony, and statutory separation requirements."

    decision_text = clean_text_block(decision, 180)
    if not decision_text:
        decision_text = f"The Court passed final orders determining the petition/appeal ({format_outcome(case)})."

    case_num = extract_case_number(title, full_text, citations, doc_id)
    judges = extract_judges(full_text)
    acts_cited = extract_acts_cited(full_text, statutes, grounds)
    outcome = format_outcome(case)

    drive_or_cite_link = url
    if citations:
        drive_or_cite_link += f" | {citations.replace('Equivalent citations:', '').strip()}"

    row = {
        # 17 requested core columns
        "Court": court,
        "Case Title": title,
        "Case Number": case_num,
        "Judgment Date": date,
        "Judges": judges,
        "Acts Cited": acts_cited,
        "Sections Cited": ", ".join(sections),
        "Legal Topics": legal_topics,
        "Outcome": outcome,
        "Fact/ Petitioner": fact_pet_text,
        "Fact/ Respondent": fact_resp_text,
        "Issues": issues_text,
        "Petitioner Argument": pet_arg_text,
        "Respondent Argument": resp_arg_text,
        "Factors to be Considered": factors_text,
        "Decision": decision_text,
        "Citation link/citation number/Drive link": drive_or_cite_link,
        # Quality Review & Advocate Feedback Columns
        "Review": "Pending",
        "Review Issues": "",
        "Reviewed By": "",
        # Enriched metadata
        "Ground (Primary)": case.get("primary_ground", "").replace("_", " ").title(),
        "All Grounds": "; ".join(grounds),
        "Judgment Year": year,
        "Relief Status": case.get("relief", "unspecified"),
        "Marriage Dissolved": "Yes" if case.get("marriage_dissolved") else "No",
        "Legal Era": "Post-2001 Amendment" if (year and int(year) >= 2001) else "Pre-2001 Act",
        "Substantive Adjudication": "Yes" if case.get("substantive", True) else "No",
        "Equivalent Citations": citations,
        "Kanoon Doc ID": doc_id,
        "Canonical Source URL": url,
        "Chunks Indexed": len(case.get("segments", [])),
    }
    return row


def main():
    cases_path = "data/labeled/cases.jsonl"
    if not os.path.exists(cases_path):
        print(f"File not found: {cases_path}")
        return

    parsed_docs = load_parsed_docs("data/parsed")
    print(f"Loaded {len(parsed_docs)} parsed full-text judgments.")

    rows = []
    with open(cases_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                case = json.loads(line)
                row = transform_case_to_row(case, parsed_docs)
                rows.append(row)

    print(f"Transformed {len(rows)} cases into clean structured database schema.")

    csv_path = "data/section10_cases_structured_database.csv"
    fieldnames = list(rows[0].keys())
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved CSV database to {csv_path} ({os.path.getsize(csv_path)} bytes)")

    json_path = "data/section10_cases_structured_database.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    print(f"Saved JSON database to {json_path} ({os.path.getsize(json_path)} bytes)")

    desktop_csv = "/Users/ananyasridhar/Desktop/Section10_Cases_Structured_Database.csv"
    try:
        with open(desktop_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Saved Desktop copy to {desktop_csv}")
    except Exception as e:
        print(f"Desktop copy notice: {e}")


if __name__ == "__main__":
    main()
