---
annotations_creators:
- machine-generated
- curated
language:
- en
license: cc-by-4.0
size_categories:
- n<1K
task_categories:
- text-classification
- feature-extraction
- sentence-similarity
pretty_name: Indian Divorce Act (Section 10) Case Corpus & Legal Taxonomy
tags:
- legal
- indian-law
- divorce-act
- case-law
- judgment-analysis
- precedents
- section-10
---

# Indian Divorce Act, 1869 — Section 10 Case Corpus

A curated and structured corpus of judicial opinions and rulings from the Supreme Court of India and High Courts concerning **Section 10 (Grounds for Dissolution of Marriage)** of the **Divorce Act, 1869** (governing Christian matrimonial causes in India).

## Corpus Overview

- **Corpus Size**: 175 retained judgments spanning from pre-independence through modern rulings (post-2001 Act 51 amendment).
- **Format**:
  - `labeled/cases.jsonl`: Structured metadata, outcome taxonomy, statutory grounds, relief, court, year, and judgment tail text.
  - `parsed/`: Clean extracted paragraphs and sentences with rhetorical role annotations (Facts, Issue, Reasoning, Ruling, Procedural, Citation).
  - `raw/`: Raw judgment HTML documents.
  - `index/`: Pre-computed hybrid search index (TF-IDF sparse vectorizer & matrix, sentence-transformer dense embeddings, and parquet metadata).

## Legal Taxonomy & Tags

Every case in `labeled/cases.jsonl` is classified under standardized statutory and procedural dimensions:

### 1. Grounds (`ground`)
- `adultery`: Section 10(1)(i)
- `conversion`: Section 10(1)(ii)
- `unsound_mind`: Section 10(1)(iii)
- `leprosy`: Section 10(1)(iv)
- `venereal_disease`: Section 10(1)(v)
- `not_heard_alive`: Section 10(1)(vi)
- `restitution_non_compliance`: Section 10(1)(vii)
- `desertion`: Section 10(1)(viii) (willful desertion for 2+ years)
- `cruelty`: Section 10(1)(ix) (mental or physical cruelty)
- `rape_bestiality`: Section 10(2)
- `nullity`: Section 19 grounds (impotency, consanguinity, lunacy, force/fraud)
- `mutual_consent`: Section 10A (introduced by Act 51 of 2001)
- `constitutional_validity`: High Court & Supreme Court challenges (e.g., Ammini E.J., Mary Sonia Zachariah)
- `procedural`: Maintenance, transfer, condonation, delays, Section 17 confirmation.

### 2. Outcomes (`outcome`)
- `allowed`: Petition or appeal granted in favour of petitioner.
- `dismissed`: Petition or appeal rejected.
- `decree_absolute`: Decree confirmed under Section 17.
- `decree_refused`: Confirmation refused or decree nisi discharged.
- `remanded`: Remitted to trial court for fresh evidence or findings.
- `partly_allowed`: Relief granted in part (e.g. maintenance allowed, divorce declined).
- `unclear`: Ambiguous final order or interim procedural order.

### 3. Marriage Dissolved (`marriage_ended`)
- `yes`: Legal dissolution, decree absolute, or marriage annulled.
- `no`: Marriage preserved, petition dismissed, or restitution ordered.
- `unclear`: Procedural order or interim matter.

### 4. Rhetorical Paragraph Roles
- `Facts`: Factual background, marriage solemnization, living arrangements.
- `Issue`: Substantive questions of law or statutory interpretation.
- `Reasoning`: Evidentiary evaluation, burden of proof analysis, legal doctrine.
- `Ruling`: Operative decree, dissolution order, costs, or disposal.
- `Procedural`: Interim applications, service of summons, condonation.
- `Citation`: Precedents, statutory provisions, and external authorities cited.

## Usage

```python
import json

with open("data/labeled/cases.jsonl", "r", encoding="utf-8") as f:
    cases = [json.loads(line) for line in f]

print(f"Loaded {len(cases)} cases.")
```

## Disclaimer

This dataset is compiled for legal research, NLP analysis, and educational purposes. Judicial records are public domain documents in India. It does not constitute legal advice.
