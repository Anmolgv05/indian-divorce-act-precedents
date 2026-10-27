"""Taxonomy + rule-based labeling for Section 10 Indian Divorce Act judgments (v2).

All rules are heuristics. Anything ambiguous returns 'unclear' (never guess).
Validate on a manual sample (Task 5) and tune the patterns below.
"""
import re
from collections import Counter

# ---------------------------------------------------------------- grounds
GROUND_PATTERNS = {
    "adultery": r"\badulter(?:y|ous)\b",
    "conversion": r"ceased to be (?:a )?christian|conver(?:ted|sion) (?:to|into)",
    "unsound_mind": r"unsound mind|incurably of unsound",
    "venereal_disease": r"venereal",
    "leprosy": r"\blepro(?:sy|us)\b",
    "presumed_dead_7_years": r"not been heard of as being alive|heard of as being alive",
    "non_consummation": r"refus\w* to consummate|non-?consummation|not (?:been )?consummated",
    "restitution_noncompliance": r"(?:fail\w*|not|non-?) ?(?:to )?compl\w* (?:with )?(?:a |the )?decree for restitution",
    "desertion": r"\bdesert(?:ed|ion|ing)\b",
    "cruelty": r"\bcruel(?:ty)?\b",
    # needs 'husband' nearby: otherwise quoted statute text inflates it
    "wife_specific": r"husband[^.]{0,120}\b(?:rape|sodomy|bestiality)\b|\b(?:rape|sodomy|bestiality)\b[^.]{0,120}husband",
    # mutual_consent_10A is NOT keyword-scored: it is assigned only by _is_consent_decree() on the operative tail
    "nullity_sec19": r"decree of nullity|section 19\b|impoten(?:t|ce|cy)",
    "constitutional_validity": r"article\s*(?:14|15|21)\b|ultra vires|constitutional(?:ity)? validity|violative of",
    "procedural": r"section 1[67]\b|section 55\b|confirm(?:ation)? of (?:the )?decree|decree nisi|jurisdiction",
}
GROUND_RE = {k: re.compile(v, re.I) for k, v in GROUND_PATTERNS.items()}
GROUND_MIN = {"constitutional_validity": 6}   # others use MIN_SCORE
MIN_SCORE = 4
PER_PARA_CAP = 2   # a paragraph quoting statute text can't dominate

# Clause hint only. VERIFY against the Act on India Code. Numbering differs before/after 2001.
CLAUSE_RE = re.compile(r"clause\s*\(?([ivx]+)\)?\s*of\s*(?:sub-?section\s*\(?1\)?\s*of\s*)?section\s*10\b", re.I)
POST_2001_CLAUSE_HINT = {  # UNVERIFIED, tie-breaker only
    "i": "adultery", "ii": "conversion", "vii": "non_consummation",
    "viii": "restitution_noncompliance", "ix": "desertion", "x": "cruelty",
}


_CONSENT_LINK = re.compile(
    r"(?:mutual consent|joint petition|section 10 ?a\b)[^.;]{0,200}(?:dissol|decree|divorce)|(?:dissol|decree|divorce)[^.;]{0,200}(?:mutual consent|joint petition|section 10 ?a\b)", re.I)
_CONSENT_NEG = re.compile(r"\b(?:not|no|without|neither)\b[^.;]{0,40}(?:mutual consent|joint petition|section 10 ?a)", re.I)


def _is_consent_decree(paragraphs):
    """True only if the operative tail itself ties mutual consent / a joint petition to a
    dissolution or decree. A passing discussion of Section 10A elsewhere does not count."""
    tail = _norm_abbr(clean_tail(paragraphs, min_chars=1500, frac=0.0))
    for sent in re.split(r"(?<=[.;])\s+", tail):
        if _CONSENT_LINK.search(sent) and not _CONSENT_NEG.search(sent):
            return True
    return False


def label_grounds(paragraphs, year=None, title=None):
    """Returns (grounds, primary, scores)."""
    n = len(paragraphs)
    if not n:
        return ["unclear"], "unclear", {}
    head_end, tail_start = max(1, int(n * 0.2)), int(n * 0.8)
    scores = Counter()
    for i, p in enumerate(paragraphs):
        for g, rx in GROUND_RE.items():
            hits = min(len(rx.findall(p["text"])), PER_PARA_CAP)
            if not hits:
                continue
            scores[g] += hits
            if i < head_end or i >= tail_start:
                scores[g] += 2 * hits
    if year is None or year >= 2001:
        full = " ".join(p["text"] for p in paragraphs)
        for m in CLAUSE_RE.finditer(full):
            g = POST_2001_CLAUSE_HINT.get(m.group(1).lower())
            if g:
                scores[g] += 3
    mins = dict(GROUND_MIN)
    if title and re.search(r"union of india|state of", title, re.I):
        mins["constitutional_validity"] = 3   # 'X vs Union of India' is usually a validity challenge
    kept = [g for g, s in scores.most_common() if s >= mins.get(g, MIN_SCORE)]
    if year is not None and year < 2001:   # Section 10A was inserted by the 2001 amendment
        kept = [g for g in kept if g != "mutual_consent_10A"]
    substantive = [g for g in kept if g != "procedural"]
    grounds = substantive or (["procedural"] if "procedural" in kept else ["unclear"])

    # Constitutional validity wins primary ground when constitutional signals are at least half of top score
    top_score = scores.most_common(1)[0][1] if scores else 0
    const_score = scores.get("constitutional_validity", 0)
    if const_score >= mins.get("constitutional_validity", MIN_SCORE) and const_score >= (top_score / 2.0):
        grounds = ["constitutional_validity"] + [g for g in grounds if g != "constitutional_validity"]

    # Procedural questions in opening paragraphs: whether decree is decree nisi / confirmation under S.16/17
    head_text = " ".join(p["text"] for p in paragraphs[:5])
    if re.search(r"whether\b[^.;]{0,350}\bdecree nisi\b[^.;]{0,100}(?:to)?sections?\s*1[67]|whether\b[^.;]{0,200}confirmation of (?:a )?decree nisi", head_text, re.I):
        grounds = ["procedural"] + [g for g in grounds if g != "procedural"]

    # mutual-consent petitions: the operative order is a consent decree, whatever was pleaded earlier.
    is_validity_case = bool(title and re.search(r"union of india|state of", title, re.I)) \
        or scores.get("constitutional_validity", 0) >= 3
    if (year is None or year >= 2001) and not is_validity_case and _is_consent_decree(paragraphs):
        grounds = ["mutual_consent_10A"] + [g for g in grounds if g != "mutual_consent_10A"]
    return grounds, grounds[0], dict(scores)


# ---------------------------------------------------------- non-merits flag
NON_MERITS_RE = re.compile(
    r"transfer (?:petition|application)|transfer of (?:the )?(?:case|petition)|section 24 (?:of )?(?:the )?c\.?p\.?c"
    r"|\b(?:testamentary(?:\s+suit)?|probate\s+(?:op|suit|petition|application|of|order)|(?:grant(?:ing|ed)?|obtain(?:ing)?)\s+(?:of\s+)?probate|in the absence of probate)\b",
    re.I
)

TRANSFER_ORDER_RE = re.compile(r"stands? transferred to the court|transfer (?:petition|application) (?:is |stands )?(?:allowed|disposed)", re.I)


def is_non_merits(title, paragraphs, look=6):
    """True for transfer applications, testamentary/probate suits etc. that carry no reasoning on Section 10 grounds.
    Keep them out of outcome statistics."""
    head = (title or "") + " " + " ".join(p["text"] for p in paragraphs[:look])
    tail = " ".join(p["text"] for p in paragraphs[-3:])
    return bool(NON_MERITS_RE.search(head) or TRANSFER_ORDER_RE.search(tail))


# ------------------------------------------------------ tail cleaning/outcome
_BOILER = [
    re.compile(r"\(\s*uploaded on[^)]*\)", re.I),
    re.compile(r"uploaded on:?\s*[\d/ :apm]+", re.I),
    re.compile(r"https?://\S+"),
    re.compile(r"\bdate\s*:\s*[\d/.\-]+", re.I),
    re.compile(r"\ba\.f\.r\.?", re.I),
    re.compile(r"\(\s*[A-Z][\w .,'-]{2,50},?\s*(?:J\.|JJ\.|C\.J\.)\s*\)"),
    re.compile(r"\bjustice\s+[A-Z][A-Z .]{2,40}"),
    re.compile(r"_{3,}"),
]

def clean_tail(paragraphs, min_chars=2500, frac=0.15):
    parts = []
    for p in paragraphs:
        t = p["text"]
        for rx in _BOILER:
            t = rx.sub(" ", t)
        t = re.sub(r"\s+", " ", t).strip()
        if len(t) >= 8:   # keep short operative orders like 'Appeal dismissed.'
            parts.append(t)
    full = " ".join(parts)
    k = max(min_chars, int(len(full) * frac))
    return full[-k:]

_APPEAL_SUBJ = r"(?:appeals?|revisions?|references?|c\.?m\.?a\.?)"
_PET_SUBJ = r"(?:petitions?|applications?|o\.?p\.?|c\.?m\.?p\.?|suit|prayer)"

_ABBR_DOTS = re.compile(r"\b(?:[A-Za-z]\.){2,}")
_ABBR_WORDS = re.compile(r"\b(No|Nos|Mat|Rs|Dr|Mr|Mrs|Smt|Sri|Shri|St|Ors|Anr)\.", re.I)

def _norm_abbr(t):
    """'C.M.P. 5/2001' -> 'CMP 5/2001', 'No. 76' -> 'No 76' so sentence splitting and
    [^.] windows don't break inside abbreviations."""
    t = _ABBR_DOTS.sub(lambda m: m.group().replace(".", ""), t)
    return _ABBR_WORDS.sub(r"\1", t)


def _verbs(subj):
    d = re.compile(rf"\b{subj}\b[^.;]{{0,100}}\b(?:dismiss\w*|rejected|fails|discharged?)\b|\b(?:dismiss\w*|reject\w*)\b[^.;]{{0,60}}\b{subj}\b", re.I)
    a = re.compile(rf"\b{subj}\b[^.;]{{0,100}}(?<!dis)\ballow(?:ed|s)?\b(?! to\b)|(?<!dis)\ballow(?:ed|s)?\b(?! to\b)[^.;]{{0,60}}\b{subj}\b|\bappeal succeeds\b|\breference[^.;]{{0,30}}\b(?:is|be) accepted\b", re.I)
    return d, a

_A_DISMISS, _A_ALLOW = _verbs(_APPEAL_SUBJ)
_P_DISMISS, _P_ALLOW = _verbs(_PET_SUBJ)
_NEG_ALLOW = re.compile(r"\bnot\b[^.;]{0,20}\ballow", re.I)
_GRANT = re.compile(r"\b(?:i|we)\b[^.;]{0,20}\b(?:grant|pronounce)\b[^.;]{0,60}\bdecree\b", re.I)   # original-side: 'I grant a decree nisi'
_NEG_GRANT = re.compile(r"\b(?:not|refus\w*|declin\w*|unable)\b[^.;]{0,30}\bgrant", re.I)
_REMAND_VERB = re.compile(
    r"\bremand\w*"
    r"|\bremit(?:s|ted|ting)?\b(?!\s+(?:the\s+)?records?\b)"
    r"|\bsent back\b"
    r"|\bde nov[oa]\b"
    r"|\bfresh (?:trial|disposal|consideration)\b"
    r"|\bre-?hear\w*[^.;]{0,40}\b(?:petition|case|matter|suit)\b"
    r"|\b(?:petition|case|matter|suit)\b[^.;]{0,40}\bre-?hear\w*",
    re.I
)
_REMAND = _REMAND_VERB
_PART = re.compile(r"allowed in part|partly allowed|partially allowed|allowed to the extent", re.I)
_DISPOSED = re.compile(r"\bdisposed of\b|reference (?:is )?answered|answer(?:ed)? the reference", re.I)
_NOTCONF = re.compile(r"(?:cannot|can not|not possible to|not in a position to|unable to|refus\w+ to|declin\w+ to)\s+confirm|(?:decree|reference)[^.;]{0,40}\bnot\b[^.;]{0,15}confirmed", re.I)
_CONF = re.compile(r"\b(?:decree|reference|judgment)\b[^.;]{0,80}\b(?:is|stands|are|be)\s+(?:hereby\s+|accordingly\s+|therefore\s+)?(?:confirmed|upheld|affirmed)\b|\bwe confirm\b|\bconfirm(?:ed|s)? the (?:decree|judgment)|\bwe (?:are inclined to )?affirm\b", re.I)
_MODIFIED = re.compile(r"stands modified|is modified|modified accordingly", re.I)
_INTERIM = re.compile(r"preliminary issue|interim (?:order|maintenance)", re.I)
_SETASIDE = re.compile(r"\b(?:judgment|decree|order)\b[^.;]{0,120}\b(?:is|are|stands?)\s+(?:hereby\s+)?(?:set aside|quashed)\b", re.I)
_SKIP_SENT = re.compile(r"miscellaneous (?:petitions?|applications?)|interlocutory", re.I)


def _decide(found):
    if "allowed" in found and "dismissed" in found: return "partly_allowed"
    return "allowed" if "allowed" in found else "dismissed" if "dismissed" in found else None


def label_disposal(paragraphs):
    """disposal in: remanded, not_confirmed, confirmed, partly_allowed, allowed, dismissed,
    modified, interim, disposed_of, unclear.
    If a sentence gives an appeal/revision/reference-level verdict, that beats petition-level
    wording ('Appeal allowed ... original petition shall stand dismissed' -> allowed).
    A remand signal only counts if operative (sentence starts within final 1200 chars of cleaned tail);
    otherwise falls through to the explicit appeal/petition verdict."""
    tail = _norm_abbr(clean_tail(paragraphs))
    tail_len = len(tail)
    appeal, pet, other = set(), set(), set()
    for m in re.finditer(r"(?:^|(?<=[.;])\s+)(.*?)(?=$|(?<=[.;])\s+)", tail, re.S):
        sent = m.group(1).strip()
        if not sent or _SKIP_SENT.search(sent):
            continue
        start_pos = m.start(1)
        dist_from_end = tail_len - start_pos

        a_hit = False
        if _A_DISMISS.search(sent): appeal.add("dismissed"); a_hit = True
        if _A_ALLOW.search(sent) and not _NEG_ALLOW.search(sent): appeal.add("allowed"); a_hit = True
        if not a_hit and _SETASIDE.search(sent): appeal.add("allowed"); a_hit = True
        if not a_hit:
            if _P_DISMISS.search(sent): pet.add("dismissed")
            if _P_ALLOW.search(sent) and not _NEG_ALLOW.search(sent): pet.add("allowed")
        if _GRANT.search(sent) and not _NEG_GRANT.search(sent): pet.add("allowed")

        is_op_remand = bool(_REMAND_VERB.search(sent) and dist_from_end <= 1200)
        if is_op_remand:
            other.add("remanded")

        if _PART.search(sent): other.add("partly_allowed")
        if _NOTCONF.search(sent): other.add("not_confirmed")
        elif _CONF.search(sent): other.add("confirmed")
        if _MODIFIED.search(sent): other.add("modified")
        if _INTERIM.search(sent): other.add("interim")
        if _DISPOSED.search(sent): other.add("disposed_of")
    verdict = _decide(appeal) or _decide(pet)
    if "remanded" in other: return "remanded"
    if "not_confirmed" in other: return "not_confirmed"
    if "partly_allowed" in other: return "partly_allowed"
    if verdict: return verdict
    for k in ("confirmed", "modified", "interim", "disposed_of"):
        if k in other: return k
    return "unclear"


# --------------------------------------------------- relief / dissolved
_NO = re.compile(
    r"petition for (?:dissolution|divorce)[^.]{0,40}dismissed"
    r"|decree (?:of|for) (?:dissolution|divorce)[^.]{0,120}set aside|set aside the decree for (?:divorce|dissolution)"
    r"|(?:cannot|can not|not possible to|not in a position to|unable to|refus\w+ to|declin\w+ to)\s+(?:confirm|bestow|grant)"
    r"|refus\w*\s+to\s+bestow\s+(?:our\s+)?confirmation"
    r"|decree (?:is )?not (?:be )?confirmed"
    r"|reject the reference and dismiss the (?:original )?(?:marriage )?petition"
    r"|\b(?:the\s+)?(?:marriage\s+|original\s+)?(?<!writ )(?<!revision )(?<!transfer )(?<!review )petition[^.]{0,40}\b(?:stands?\s+)?dismissed\b"
    r"|\b(?:the\s+)?suit\s+is\s+dismissed\b|dismiss(?:ed)?\s+the\s+suit\b|\bsuits?\b[^;]{0,60}?\b(?:is|are|stands?)\s+(?:hereby\s+)?dismissed\b"
    r"|\b(?:o\.?p\.?|d\.?o\.?p\.?)[^.]{0,60}\b(?:stands?\s+)?dismissed\b"
    r"|\bno\s+decree\s+(?:for|of)\s+(?:dissolution|divorce)\b"
    r"|no decree for dissolution[^.]{0,50}could be obtained",
    re.I
)
_REF_INCOMPETENT = re.compile(
    r"reference[^.]{0,80}(?:incompetent|not maintainable|rejected|not sustainable)"
    r"|confirmation[^.]{0,60}incompetent"
    r"|rule (?:issued is |is )?liable to be discharged"
    r"|rule (?:issued is |is )?discharged"
    r"|no orders are passed on these proceedings",
    re.I
)
_RECITAL = re.compile(
    r"(?:learned\s+)?(?:additional\s+)?(?:district judge|family court|court below|trial court)[^.;]{0,40}(?:passed|granted)\s+(?:a\s+)?decree"
    r"|decree (?:of|for) (?:dissolution|divorce|nullity)[^.;]{0,80}passed by the (?:learned )?(?:additional )?(?:district judge|family court|court below|trial court)"
    r"|after\s+(?:a\s+)?decree\s+(?:for|of)\s+(?:nullity|dissolution|divorce)",
    re.I
)
_NO_GRANT_WORDS = re.compile(
    r"not (?:a )?ground for (?:grant of )?decree|cannot grant decree|refus\w* to grant",
    re.I
)

_YES_A = re.compile(r"\b(?:a\s+)?decree (?:of|for) (?:dissolution|divorce|nullity)(?: of marriage)?[^.]{0,60}\b(?:is\s+|stands\s+)?(?:hereby\s+|accordingly\s+)?(?:passed|granted|confirmed|made absolute|affirmed)\b", re.I)
_YES_B = re.compile(r"\b(?:grant(?:ed)?|passed|allowed|awarded|pronounce\w*)\b[^.]{0,40}decree(?: nisi)? (?:of|for) (?:dissolution|divorce)|decree nisi (?:is |be |shall be )?(?:issued|passed|granted|pronounced)|allow\w*[^.]{0,30}petition for (?:dissolution|divorce)", re.I)
_YES_C = re.compile(r"marriage[^.]{0,80}(?:stands|is|be) (?:directed to be\s+)?dissolved|decree nisi is made absolute|decree\s+absolute\s+for\s+(?:the\s+)?dissolution\s+of\s+(?:the\s+)?marriage|dissolving the marriage", re.I)
_YES_D = re.compile(r"decree[^.]{0,80}\b(?:is|stands)\s+(?:hereby\s+|accordingly\s+)?(?:confirmed|upheld|affirmed)\b|\bconfirm(?:ed|s)? the decree|\bwe (?:are inclined to )?affirm the decree", re.I)  # only if tail talks of divorce
_DIV_WORDS = re.compile(r"divorce|dissolution|dissolv", re.I)
_NULLITY = re.compile(r"declar\w*[^.]{0,200}(?:null and void|void ab initio|a nullity)|decree of nullity (?:is )?(?:passed|granted)", re.I)
_RCR = re.compile(r"decree for restitution of conjugal rights (?:is )?(?:passed|granted)|restitution of conjugal rights[^.]{0,40}(?:allowed|granted|decreed)", re.I)
_JS = re.compile(r"decree (?:of|for) judicial separation|judicial separation is (?:granted|decreed)|pass(?:ed)? a decree[^.]{0,80}judicial separation", re.I)


def _other_relief(tail):
    if _JS.search(tail): return "judicial_separation"
    if _RCR.search(tail): return "restitution"
    return None


_AFFIRM_DECREE = re.compile(
    r"decree[^.;]{0,100}\b(?:allowing|granting)\b[^.;]{0,60}\b(?:divorce|dissolution)\b[^.;]{0,120}"
    r"\b(?:requires?\s+no\s+interference|(?:is|stands)\s+(?:upheld|affirmed))",
    re.I
)
_OWN_GRANT = re.compile(
    r"\brespondent\s+is\s+granted\s+a\s+decree\s+(?:for|of)\s+dissolution\b"
    r"|\b(?:i|we)\s+grant\s+a\s+decree\s+(?:for|of)\s+dissolution\b"
    r"|\bwe\s+pass\s+a\s+decree\s+(?:for|of)\s+dissolution\b"
    r"|(?<!not )\bdirect\s+(?:the\s+)?dissolution\s+of\s+(?:the\s+)?marriage\b",
    re.I
)


def label_dissolved(paragraphs, ground=None):
    """Returns (marriage_dissolved, relief). 'yes' means the marriage is ended by the
    operative order (dissolution OR nullity; see relief). NO-patterns win over YES-patterns
    because judgments quote the lower court's decree before refusing to confirm it. A
    reference rejected as incompetent/unsustainable means no decree was confirmed -> unclear.
    Validity challenges and procedural matters -> unclear."""
    if ground in ("constitutional_validity", "procedural"):
        return "unclear", "unclear"

    tail = _norm_abbr(clean_tail(paragraphs))
    if _OWN_GRANT.search(tail):
        return "yes", "dissolution"
    if label_disposal(paragraphs) == "remanded":
        return "unclear", "unclear"
    if _NO.search(tail):
        return "no", (_other_relief(tail) or "none")
    if _REF_INCOMPETENT.search(tail):
        return "unclear", "unclear"
    if _NULLITY.search(tail):
        return "yes", "nullity"

    if _AFFIRM_DECREE.search(tail):
        return "yes", "dissolution"
    is_recital = bool(_RECITAL.search(tail))
    has_affirmance = bool(_CONF.search(tail) or _YES_C.search(tail) or _GRANT.search(tail)
                          or re.search(r"order of the learned single Judge is upheld|decree of the Family Court is affirmed", tail, re.I))

    if is_recital and not has_affirmance:
        return "unclear", "unclear"

    if _YES_C.search(tail):
        return "yes", "dissolution"
    if _YES_B.search(tail) and not _NEG_GRANT.search(tail) and not _NO_GRANT_WORDS.search(tail):
        return "yes", "dissolution"
    if _YES_A.search(tail):
        return "yes", "dissolution"
    if _YES_D.search(tail) and _DIV_WORDS.search(tail):
        return "yes", "dissolution"

    other = _other_relief(tail)
    if other:
        return "no", other
    return "unclear", "unclear"


def label_outcome(paragraphs, ground=None):
    """Back-compat wrapper: (disposal, marriage_dissolved)."""
    return label_disposal(paragraphs), label_dissolved(paragraphs, ground=ground)[0]


# ------------------------------------------------------- petitioner gender
_ROLE = r"(?:appellant|petitioner)"
PET_RE = [
    re.compile(rf"(?:appeal|petition|filed|preferred|instituted)\s+(?:is\s+)?by\s+(?:the\s+)?(wife|husband)", re.I),
    re.compile(rf"\b(wife|husband)\s*[-,/(]\s*(?:the\s+)?{_ROLE}\b", re.I),
    re.compile(rf"\b{_ROLE}\s*[-,/(]\s*(?:the\s+)?(wife|husband)\b", re.I),
    re.compile(r"\bthe\s+(wife|husband)\s+(?:has\s+|had\s+)?(?:filed|preferred|instituted|approached|sought|petitioned|moved)\b", re.I),
]

_TITLE_FEMALE = re.compile(r"\b(?:w/o|wife of|d/o|daughter of|smt\.?|mrs\.?|ms\.?)\b", re.I)
_TITLE_MALE = re.compile(r"\b(?:s/o|son of|shri|mr\.?)\b", re.I)

def petitioner_from_title(title):
    """Low-confidence fallback: first-named party in 'X vs Y' is usually appellant/petitioner;
    'W/o', 'D/o', 'Smt' mark a woman, 'S/o', 'Shri' a man. Returns None if no marker."""
    first = re.split(r"\bvs?\.?\b|\bversus\b", title or "", maxsplit=1, flags=re.I)[0]
    f, m = bool(_TITLE_FEMALE.search(first)), bool(_TITLE_MALE.search(first))
    return "wife" if f and not m else "husband" if m and not f else None


def label_petitioner(paragraphs, look=12, title=None):
    c = Counter()
    for p in paragraphs[:look]:
        for rx in PET_RE:
            for m in rx.finditer(p["text"]):
                c[m.group(1).lower()] += 1
    if not c or (len(c) == 2 and c["wife"] == c["husband"]):
        return petitioner_from_title(title) or "unclear"
    return c.most_common(1)[0][0]


# -------------------------------------------------------------- segments
CUES = [
    ("conclusion", re.compile(r"in the result|for the (?:aforesaid|foregoing|above) reasons|appeal is (?:allowed|dismissed)|we allow|we dismiss|decree .* passed|no costs", re.I)),
    ("reasoning", re.compile(r"we are of the (?:view|opinion)|in our (?:view|opinion)|we hold|it is (?:clear|evident)|having regard to|we find|the question (?:that )?arises", re.I)),
    ("law", re.compile(r"section\s+\d+|the act provides|sub-?section|as held in|(?:AIR|SCC|ILR)\s*\d{4}", re.I)),
    ("respondent_argument", re.compile(r"(?:learned )?counsel for the respondent|respondent[- ]\w+ (?:contended|submitted|stated|denied)|the respondent (?:in (?:his|her) (?:counter|written statement)|denied)", re.I)),
    ("petitioner_argument", re.compile(r"(?:learned )?counsel for the (?:appellant|petitioner)|(?:appellant|petitioner)[- ]\w+ (?:contended|submitted|alleged|stated)|it is (?:contended|submitted|alleged) (?:by|that)", re.I)),
    ("issue", re.compile(r"(?:question|point)s? (?:for|that) (?:consideration|arise)|the questions? involved|following (?:question|issue)|whether\b", re.I)),
]

def segment_paragraphs(paragraphs):
    n = len(paragraphs)
    types, current = [], "facts"
    for i, p in enumerate(paragraphs):
        found = next((t for t, rx in CUES if rx.search(p["text"])), None)
        if i == n - 1:
            found = "conclusion"
        current = found or current
        types.append(current)
    segs = []
    for p, t in zip(paragraphs, types):
        if segs and segs[-1]["type"] == t:
            segs[-1]["p_ids"].append(p["p_id"])
            segs[-1]["text"] += "\n" + p["text"]
        else:
            segs.append({"type": t, "p_ids": [p["p_id"]], "text": p["text"]})
    return segs
