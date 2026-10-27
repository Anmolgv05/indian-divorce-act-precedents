"""Near-duplicate detection (v2: two tiers).

Indian Kanoon sometimes holds two copies of one judgment under different doc IDs.
But the same title+date can also be two DIFFERENT documents (a judgment and a later
clarifying order, separate opinions...), so metadata alone must never drop a document.

  drop   : text is essentially the same  (jaccard >= 0.8, or same title/date AND one text
           is >= 0.9 contained in the other)
  review : same title/date (or high containment) but texts differ -> KEEP BOTH, flag for a human
"""
import re


def norm_title(title):
    t = re.sub(r"\bon\s+\d{1,2}\s+\w+,?\s+\d{4}\s*$", "", title or "", flags=re.I)
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def shingles(text, k=8, limit=4000):
    words = re.findall(r"[a-z0-9]+", (text or "").lower())[:limit]
    return {" ".join(words[i:i + k]) for i in range(max(0, len(words) - k + 1))}


def jaccard(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0


def containment(a, b):
    """share of the smaller text's shingles that appear in the other"""
    return len(a & b) / min(len(a), len(b)) if a and b else 0.0


def classify_pairs(cases, jaccard_drop=0.8, contain_drop=0.9):
    """Returns list of dicts: keep, other, action ('drop'|'review'), jaccard, containment,
    same_meta. For 'drop', `other` is the shorter copy to remove."""
    info = []
    for c in cases:
        text = " ".join(p["text"] for p in c.get("paragraphs", []))
        info.append((c["doc_id"], norm_title(c.get("title")), c.get("date"), text, shingles(text)))
    dropped, out = set(), []
    for i in range(len(info)):
        for j in range(i + 1, len(info)):
            a, b = info[i], info[j]
            if a[0] in dropped or b[0] in dropped:
                continue
            same_meta = bool(a[1]) and a[1] == b[1] and a[2] == b[2]
            jac, con = jaccard(a[4], b[4]), containment(a[4], b[4])
            if jac >= jaccard_drop or (same_meta and con >= contain_drop):
                keep, other = (a, b) if len(a[3]) >= len(b[3]) else (b, a)
                dropped.add(other[0])
                action = "drop"
            elif same_meta or con >= contain_drop:
                keep, other, action = a, b, "review"
            else:
                continue
            out.append({"keep": keep[0], "other": other[0], "action": action,
                        "jaccard": round(jac, 2), "containment": round(con, 2), "same_meta": same_meta})
    return out


def find_duplicates(cases, threshold=0.8):
    """Back-compat: (keep_id, drop_id, reason) for pairs that are safe to drop."""
    return [(d["keep"], d["other"], f"same_title_date={d['same_meta']} jaccard={d['jaccard']} containment={d['containment']}")
            for d in classify_pairs(cases, jaccard_drop=threshold) if d["action"] == "drop"]
