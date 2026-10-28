import { useState, useEffect } from "react";
import SiteNav from "./SiteNav.jsx";
import "./about.css";

// Audited corpus count across 24 High Courts and Supreme Court
const DEFAULT_CASE_COUNT = 363;

export default function About() {
  const [caseCount, setCaseCount] = useState(DEFAULT_CASE_COUNT);

  useEffect(() => {
    fetch("/api/stats")
      .then((r) => r.json())
      .then((data) => {
        if (data && data.total_cases) {
          setCaseCount(data.total_cases);
        }
      })
      .catch(() => {});
  }, []);
  return (
    <>
      <SiteNav />
      <main id="main" className="about">
        <a className="about-back" href="#/">← Back to search</a>
        <p className="about-kicker">SYSTEM & ARCHITECTURE GUIDE</p>
        <h1>Section 10 Divorce Search</h1>
        <p className="about-lede">

        An intelligent precedent research and case law intelligence tool for reported decisions
        under Section 10 of the Indian Divorce Act, 1869 (Christian matrimonial law).
        Designed specifically for advocates, legal practitioners, and researchers to assess factual scenarios,
        evidentiary burdens, and judicial likelihood.
        </p>
      <section>
        <h2>What it covers</h2>
        <p>
          Reported decisions under Section 10 of the Divorce Act, 1869 (Christian matrimonial law) from the Supreme Court of India and High Courts.
        </p>
        <p>
          <a href="#/section-10">New to Section 10? Read the plain-words explainer.</a>
        </p>
        <p>
          <a href="#/cases">Browse all cases in the audited corpus.</a>
        </p>
      </section>

      <section className="about-highlight-box">
        <h2>At a glance</h2>
        <div className="about-grid">
          <div className="about-card">
            <h3>{caseCount}+ Substantive Judgments</h3>
            <p>Curated Supreme Court and High Court judgments from 1869 to present, filtered to exclude irrelevant revisions.</p>
          </div>
          <div className="about-card">
            <h3>Zero Hallucinations</h3>
            <p>Grounded strictly in verbatim text and deterministic legal rules. No fabricated citations or bench quotes.</p>
          </div>
          <div className="about-card">
            <h3>Complete Client Privacy</h3>
            <p>100% local CPU-based processing. Confidential client facts and matrimonial allegations never touch cloud servers.</p>
          </div>
          <div className="about-card">
            <h3>Dual Search SLM Engine</h3>
            <p>Combines deep semantic understanding of human stories with razor-sharp statutory keyword precision.</p>
          </div>
          <div className="about-card">
            <h3>Multilingual Indian Law Support</h3>
            <p>Query in Hindi, Malayalam, Tamil, Telugu, Marathi, Bengali, or English. Vernacular statutory terms are seamlessly translated to relevant precedents with canonical links.</p>
          </div>
        </div>
      </section>

      <section>
        <h2>Why Small Language Models (SLMs) Instead of Generic Chatbots?</h2>
        <p>
          Large generative chatbots (like ChatGPT or general cloud LLMs) are designed for creative text generation,
          which makes them hazardous for legal practice. In law, a slightly altered quote or an invented citation is not a minor bug—it is professional misconduct.
        </p>
        <p>
          Rather than relying on closed, unpredictable cloud models, this system is built on a specialized <b>Compound Small Language Model (SLM) & Legal NLP Pipeline</b>:
        </p>
        <div className="about-comparison">
          <div className="about-comparison-col col-bad">
            <h4>Traditional Generative AI / Cloud Chatbots</h4>
            <ul>
              <li><b>Hallucinations:</b> Often invents non-existent Supreme Court rulings, fictional bench names, and fake section clauses.</li>
              <li><b>Privacy Risks:</b> Sensitive marital disputes and client facts are transmitted to commercial cloud servers and may train public models.</li>
              <li><b>Black-Box Guesses:</b> Unverifiable reasoning that cannot be cross-examined or checked against primary sources.</li>
            </ul>
          </div>
          <div className="about-comparison-col col-good">
            <h4>Our Specialized Local SLM Architecture</h4>
            <ul>
              <li><b>100% Verbatim Fidelity:</b> Every retrieved snippet and precedent citation links directly to the original judgment record.</li>
              <li><b>Absolute Confidentiality:</b> Runs entirely on local infrastructure; search queries and client scenarios never leave your device.</li>
              <li><b>Deterministic Legal Taxonomies:</b> Grounds, disposals, and decrees are classified with rigorous, rule-based legal logic.</li>
            </ul>
          </div>
        </div>
      </section>

      <section>
        <h2>How the Search Engine Works (in Plain English)</h2>
        <p>
          When you enter a search query, multiple specialized local models and indexers collaborate in real time:
        </p>
        <ol className="about-steps">
          <li>
            <b>1. Understanding the Narrative (Semantic SLM):</b>
            <p>
              We run <code>BAAI/bge-small-en-v1.5</code>, a compact 33-million parameter transformer embedding model.
              It reads your natural-language factual description (e.g. <i>"husband falsely accused wife of unchastity and expelled her from the house"</i>)
              and projects the core meaning into a 384-dimensional conceptual space, matching similar judicial stories even when different words were used.
            </p>
          </li>
          <li>
            <b>2. Precision Statutory Matching (Lexical TF-IDF Index):</b>
            <p>
              Simultaneously, a high-speed term-frequency index scans the judgments for exact statutory sections
              (e.g. <code>Section 10(1)(x)</code>, <code>Section 10A</code>, <code>Section 11</code>, <code>Section 14</code>, <code>Section 19</code>)
              and legal terms of art (such as <i>animus deserendi</i>, <i>condonation</i>, or <i>decree nisi</i>).
            </p>
          </li>
          <li>
            <b>3. Hybrid Score Combination (70% Semantic + 30% Exact):</b>
            <p>
              The engine fuses the broad conceptual score (70%) with the precise statutory match (30%).
              This ensures you get cases that match the human factual situation while respecting statutory precision.
            </p>
          </li>
          <li>
            <b>4. Precedent Intelligence & Strategic Advocate Synthesis:</b>
            <p>
              The retrieved cases are analyzed to extract actionable legal intelligence: the operative grant rate among merits rulings,
              key evidentiary standards required by judges, statutory defenses to anticipate (such as Section 14 condonation), and a practical litigation checklist.
            </p>
          </li>
        </ol>
      </section>

      <section>
        <h2>The Curated Judgment Corpus ({caseCount}+ Cases)</h2>
        <p>
          Legal databases are frequently polluted with procedural noise. We conducted a strict audit of the corpus to ensure high relevance:
        </p>
        <ul>
          <li><b>Scope:</b> Only reported judgments of the Supreme Court of India and High Courts adjudicating Section 10 grounds (cruelty, desertion, adultery), Section 10A mutual consent petitions, Section 18/19 nullity suits, or Section 16/17 confirmation references.</li>
          <li><b>Filtered Out:</b> Unrelated criminal maintenance revisions under CrPC Section 125, Hindu Marriage Act petitions, Special Marriage Act petitions, and government administrative circulars have been rigorously removed.</li>
          <li><b>Historical Ground Reforms:</b> Includes landmark constitutional decisions (such as <i>Ammini E.J.</i>, <i>Mary Sonia Zachariah</i>, and <i>Pragati Varghese</i>) that struck down gender-discriminatory provisions of Section 10, leading to the landmark 2001 Indian Divorce Amendment Act.</li>
        </ul>
      </section>

      <section>
        <h2>How Advocates Can Use This System Effectively</h2>
        <div className="about-tips">
          <div className="about-tip">
            <h4>Pleadings & Fact Matching</h4>
            <p>Paste the core factual narrative from your draft petition or client conference. The semantic model will find judgments with closely matching domestic facts.</p>
          </div>
          <div className="about-tip">
            <h4>Anticipating Defenses</h4>
            <p>Search for statutory bars like <code>condonation under section 14</code> or <code>failure to implead co-respondent under section 11</code> to evaluate respondent defenses before filing.</p>
          </div>
          <div className="about-tip">
            <h4>Evidentiary Roadmaps</h4>
            <p>Inspect the Advocate's Precedent Intelligence panel to see what documentary evidence (MLCs, complaints, letters) persuaded the bench in similar cases.</p>
          </div>
        </div>
      </section>

      <section>
        <h2>Taxonomy &amp; Legal Tags Overview</h2>
        <p>
          Every judgment in the corpus is indexed with structured classification tags generated by deterministic legal NLP rules.
          Click any tag below to inspect matching decisions in the Case Explorer:
        </p>

        <h3>1. Statutory Grounds Tags (Click to browse)</h3>
        <div className="about-tag-cloud">
          <a className="about-tag-pill" href="#/cases?ground=cruelty"><span>Cruelty §10(1)(x)</span><span className="count">80</span></a>
          <a className="about-tag-pill" href="#/cases?ground=adultery"><span>Adultery §10(1)(i)</span><span className="count">75</span></a>
          <a className="about-tag-pill" href="#/cases?ground=desertion"><span>Desertion §10(1)(ix)</span><span className="count">30</span></a>
          <a className="about-tag-pill" href="#/cases?ground=constitutional_validity"><span>Constitutional Validity</span><span className="count">27</span></a>
          <a className="about-tag-pill" href="#/cases?ground=mutual_consent_10A"><span>Mutual Consent §10A</span><span className="count">21</span></a>
          <a className="about-tag-pill" href="#/cases?ground=nullity_sec19"><span>Nullity &amp; Impotency §19</span><span className="count">15</span></a>
          <a className="about-tag-pill" href="#/cases?ground=procedural"><span>Procedural &amp; §17 Confirmation</span><span className="count">31</span></a>
          <a className="about-tag-pill" href="#/cases?ground=unsound_mind"><span>Unsound Mind §10(1)(iii)</span><span className="count">4</span></a>
          <a className="about-tag-pill" href="#/cases?ground=non_consummation"><span>Non-Consummation §10(1)(vii)</span><span className="count">3</span></a>
          <a className="about-tag-pill" href="#/cases?ground=conversion"><span>Religious Conversion §10(1)(ii)</span><span className="count">2</span></a>
          <a className="about-tag-pill" href="#/cases?ground=wife_specific"><span>Wife-Specific §10(2)</span><span className="count">1</span></a>
          <a className="about-tag-pill" href="#/cases?ground=venereal_disease"><span>Venereal Disease §10(1)(v)</span><span className="count">1</span></a>
          <a className="about-tag-pill" href="#/cases?ground=leprosy"><span>Leprosy §10(1)(iv)</span><span className="count">1</span></a>
        </div>

        <h3>2. Regional High Courts &amp; Apex Court (24 Jurisdictions)</h3>
        <div className="about-tag-cloud">
          <a className="about-tag-pill" href="#/cases"><span>Kerala High Court</span><span className="count">54</span></a>
          <a className="about-tag-pill" href="#/cases"><span>Madras High Court</span><span className="count">50</span></a>
          <a className="about-tag-pill" href="#/cases"><span>Bombay High Court</span><span className="count">29</span></a>
          <a className="about-tag-pill" href="#/cases"><span>Delhi High Court</span><span className="count">23</span></a>
          <a className="about-tag-pill" href="#/cases"><span>Calcutta High Court</span><span className="count">22</span></a>
          <a className="about-tag-pill" href="#/cases"><span>Allahabad High Court</span><span className="count">21</span></a>
          <a className="about-tag-pill" href="#/cases"><span>Supreme Court of India</span><span className="count">21</span></a>
          <a className="about-tag-pill" href="#/cases"><span>Jharkhand High Court</span><span className="count">20</span></a>
          <a className="about-tag-pill" href="#/cases"><span>Karnataka High Court</span><span className="count">20</span></a>
          <a className="about-tag-pill" href="#/cases"><span>Orissa High Court</span><span className="count">18</span></a>
          <a className="about-tag-pill" href="#/cases"><span>Rajasthan High Court</span><span className="count">16</span></a>
          <a className="about-tag-pill" href="#/cases"><span>Punjab &amp; Haryana High Court</span><span className="count">13</span></a>
          <a className="about-tag-pill" href="#/cases"><span>Gauhati High Court</span><span className="count">12</span></a>
          <a className="about-tag-pill" href="#/cases"><span>Patna High Court</span><span className="count">11</span></a>
          <a className="about-tag-pill" href="#/cases"><span>Himachal Pradesh High Court</span><span className="count">11</span></a>
          <a className="about-tag-pill" href="#/cases"><span>Andhra High Court</span><span className="count">8</span></a>
          <a className="about-tag-pill" href="#/cases"><span>Madhya Pradesh High Court</span><span className="count">6</span></a>
          <a className="about-tag-pill" href="#/cases"><span>Gujarat High Court</span><span className="count">4</span></a>
          <a className="about-tag-pill" href="#/cases"><span>Telangana High Court</span><span className="count">3</span></a>
          <a className="about-tag-pill" href="#/cases"><span>Tripura High Court</span><span className="count">1</span></a>
        </div>

        <h3>3. Disposal Tags (<code>disposal</code>)</h3>
        <p>The formal procedural disposition recorded in the judgment’s operative order:</p>
        <ul>
          <li><b><code>allowed</code> (110 cases):</b> Appeal or original petition accepted; prayer granted.</li>
          <li><b><code>dismissed</code> (115 cases):</b> Appeal or petition rejected; judgment affirmed.</li>
          <li><b><code>partly_allowed</code> (23 cases):</b> Relief granted in part (e.g. divorce refused, but maintenance or property return allowed).</li>
          <li><b><code>confirmed</code> (22 cases):</b> High Court Full Bench confirmed District Court decree nisi under historic Section 17.</li>
          <li><b><code>disposed_of</code> (19 cases):</b> Closed without merits determination (e.g. joint memo settlement or transfer).</li>
          <li><b><code>remanded</code> (16 cases):</b> Sent back to trial court or Family Court for fresh adjudication or evidence.</li>
          <li><b><code>not_confirmed</code> (10 cases):</b> High Court declined to confirm decree nisi under historic Section 17.</li>
        </ul>

        <h3>4. Marital Status Decree (<code>marriage_dissolved</code>)</h3>
        <ul>
          <li><b><code>yes</code> (96 cases):</b> The operative decree severed the marital tie (dissolution under Section 10/10A or nullity under Section 18/19).</li>
          <li><b><code>no</code> (52 cases):</b> Divorce petition dismissed, decree set aside, or marriage kept legally intact.</li>
          <li><b><code>unclear</code> (215 cases):</b> Interlocutory orders, remands, transfer petitions, or where marital status was not determined.</li>
        </ul>

        <h3>5. Paragraph Structural Segments (<code>role</code>)</h3>
        <p>Every paragraph in a judgment is automatically segmented into functional rhetorical roles:</p>
        <ul>
          <li><b>Facts:</b> Marital history, cohabitation, and domestic background.</li>
          <li><b>Issue:</b> Points of law and questions framed for adjudication.</li>
          <li><b>Petitioner's Argument:</b> Submissions and factual contentions raised by the moving spouse.</li>
          <li><b>Respondent's Argument:</b> Rebuttals, denials, and counter-claims by the answering spouse.</li>
          <li><b>Law:</b> Relevant statutory sections and precedent authorities discussed.</li>
          <li><b>Court's Reasoning:</b> Substantive judicial analysis and evidentiary evaluation.</li>
          <li><b>Conclusion:</b> Operative ruling and cost orders.</li>
        </ul>
      </section>

      <section className="about-note">
        <h2>Important Research Notice</h2>
        <ul>
          <li><b>Judicial Trends, Not Predictions:</b> Retrieved cases reflect historical court rulings across diverse Benches; they indicate judicial trends and evidentiary thresholds, not a mathematical guarantee of outcome.</li>
          <li><b>Verify Citations:</b> Built as an intelligent research aid. Always verify citations in primary law reports (SCC, AIR, ILR) before submitting pleadings.</li>
          <li><b>Source Records:</b> Public court decisions are indexed from Indian Kanoon for academic and legal research.</li>
        </ul>
      </section>

      <section>
        <h2>Grounded Result Summaries</h2>
        <p>
          The summary above the results is compiled only from the cases shown. By default it is assembled from the case labels and matched passages. If the site operator turns on AI summaries, a language model writes it from those same cases and the result is checked for citations; the cards underneath are always the original text.
        </p>
      </section>

      <section>
        <h2>Project Repositories &amp; Data Assets</h2>
        <ul>
          <li>
            <b>GitHub Repository:</b>{" "}
            <a href="https://github.com/Anmolgv05/indian-divorce-act-precedents" target="_blank" rel="noopener noreferrer">
              Anmolgv05/indian-divorce-act-precedents
            </a>
          </li>
          <li>
            <b>Hugging Face Dataset:</b>{" "}
            <a href="https://huggingface.co/datasets/AnmolGV/section10-divorce-corpus" target="_blank" rel="noopener noreferrer">
              AnmolGV/section10-divorce-corpus
            </a>
          </li>
          <li>
            <b>Production Web App:</b>{" "}
            <a href="https://section10-divorce-search.onrender.com" target="_blank" rel="noopener noreferrer">
              section10-divorce-search.onrender.com
            </a>
          </li>
        </ul>
      </section>
    </main>
    </>
  );
}

