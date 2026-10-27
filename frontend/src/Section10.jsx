import SiteNav from "./SiteNav.jsx";
import "./about.css";
import "./section10.css";

// Update LAST_CHECKED whenever the text below is re-checked against the statute.
const LAST_CHECKED = "22 October 2026";
const ACT_URL = "https://indiankanoon.org/doc/1387951/";

const GROUNDS = [
  ["10(1)(i)", "Adultery", "The other spouse has committed adultery.", "adultery"],
  ["10(1)(ii)", "Conversion", "The other spouse has stopped being Christian by converting to another religion.", ""],
  ["10(1)(iii)", "Unsound mind", "The other spouse has been incurably of unsound mind for at least two continuous years immediately before the petition.", "unsound mind"],
  ["10(1)(iv)", "Removed in 2019", "This clause (a ground based on leprosy) was omitted by the Personal Laws (Amendment) Act, 2019.", ""],
  ["10(1)(v)", "Venereal disease", "The other spouse has had a venereal disease in a communicable form for at least two years immediately before the petition.", ""],
  ["10(1)(vi)", "Not heard of", "The other spouse has not been heard of as alive for seven years or more by those who would naturally have heard from them.", ""],
  ["10(1)(vii)", "Non-consummation", "The other spouse has wilfully refused to consummate the marriage, and it has not been consummated.", "non-consummation"],
  ["10(1)(viii)", "Restitution decree ignored", "The other spouse has not complied, for two years or more, with a decree for restitution of conjugal rights.", ""],
  ["10(1)(ix)", "Desertion", "The other spouse has deserted the petitioner for at least two years immediately before the petition.", "desertion"],
  ["10(1)(x)", "Cruelty", "The other spouse has treated the petitioner with cruelty.", "cruelty"],
  ["10(2)", "Wife only", "A wife may also petition on the ground that her husband has, since the marriage, been guilty of rape, sodomy or bestiality.", ""],
];

export default function Section10() {
  return (
    <>
      <SiteNav />
      <main id="main" className="about s10">
        <p className="about-kicker">EXPLAINER</p>
        <h1>Section 10, in plain words</h1>
        <p className="about-lede">
          Section 10 of the Divorce Act, 1869 says on what grounds a Christian marriage in India can be ended by a court.
          This page explains it so the case results make sense. It is a guide to reading the law, not legal advice.
        </p>

        <nav className="s10-toc" aria-label="On this page">
          <h2>On this page</h2>
          <ul>
            <li><a href="#s10-what">What Section 10 does</a></li>
            <li><a href="#s10-grounds">The grounds</a></li>
            <li><a href="#s10-10a">Divorce by mutual consent (Section 10A)</a></li>
            <li><a href="#s10-changes">What changed in 2001 and 2019</a></li>
            <li><a href="#s10-courts">How courts read the grounds</a></li>
            <li><a href="#s10-related">Related sections you will see in cases</a></li>
            <li><a href="#s10-read">Reading the cases on this site</a></li>
          </ul>
        </nav>

        <section id="s10-what">
          <h2>What Section 10 does</h2>
          <p>
            It lists the reasons a court may dissolve (end) a marriage between persons who profess the Christian religion.
            Since 2001 either the husband or the wife can file, on the same grounds, in the District Court
            (or the Family Court, where one has been set up in that area). A marriage can be dissolved under Section 10 whether it was
            solemnised before or after 2001.
          </p>
          <p>
            Dissolution is a divorce: the marriage ends. It is different from judicial separation (spouses live apart but stay married)
            and from nullity (the marriage is declared void from the start).
          </p>
        </section>

        <section id="s10-grounds">
          <h2>The grounds</h2>
          <p>The wording below is paraphrased. The respondent is the spouse the petition is filed against.</p>
          <div className="s10-table-wrap" role="region" aria-labelledby="s10-cap" tabIndex={0}>
            <table className="s10-table">
              <caption id="s10-cap">Grounds for dissolution of marriage under Section 10</caption>
              <thead>
                <tr><th scope="col">Clause</th><th scope="col">Ground</th><th scope="col">What it means</th><th scope="col">Search</th></tr>
              </thead>
              <tbody>
                {GROUNDS.map(([clause, name, text, q]) => (
                  <tr key={clause}>
                    <th scope="row">{clause}</th>
                    <td>{name}</td>
                    <td>{text}</td>
                    <td>{q ? <a href={`/?q=${encodeURIComponent(q + " section 10")}`}>Find cases<span className="sr-only"> on {name}</span></a> : <span aria-label="No search shortcut">—</span>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="s10-note">
            Read the exact statutory wording before relying on any clause: <a href={ACT_URL}>Section 10 on Indian Kanoon</a>.
          </p>
        </section>

        <section id="s10-10a">
          <h2>Divorce by mutual consent (Section 10A)</h2>
          <p>
            Section 10A, added in 2001, lets both spouses file together. The statute asks for at least two years of living separately,
            that they have not been able to live together, and that they have agreed the marriage should end.
          </p>
          <p>
            The two-year period has been challenged. In 2010 the Kerala High Court held that it should be read as one year,
            and in December 2022 a Kerala High Court Division Bench struck down the one-year minimum as unconstitutional (W.P.(C) 28317/2022).
            These are High Court rulings, so what applies to a particular couple depends on the High Court whose area they are in.
            Cases in this database show the courts working through this question.
          </p>
        </section>

        <section id="s10-changes">
          <h2>What changed in 2001 and 2019</h2>
          <ul className="s10-timeline">
            <li><b>1869</b> The Act is passed. Under the original Section 10, a husband could petition for divorce on his wife’s adultery alone,
              but a wife had to prove adultery together with another fault such as cruelty or desertion.</li>
            <li><b>2001</b> The Indian Divorce (Amendment) Act, 2001 replaced Section 10 with the grounds above, open to both spouses, and added
              Section 10A. The word “Indian” was dropped from the Act’s name.</li>
            <li><b>2019</b> The Personal Laws (Amendment) Act, 2019 omitted clause (iv).</li>
          </ul>
          <p>
            This matters when you read old judgments. A case from before 2001 may discuss rules that no longer exist, such as the
            extra burden on wives, or the High Court’s confirmation of a decree before it took effect. Always check the date.
          </p>
        </section>

        <section id="s10-courts">
          <h2>How courts read the grounds</h2>
          <ul>
            <li><b>Desertion</b> is more than leaving. Courts look for the fact of separation and an intention to end the marriage,
              continuing for at least two years before the petition was filed.</li>
            <li><b>Cruelty</b> is not defined in the Act. Courts decide it case by case and have accepted mental cruelty as well as physical.</li>
            <li><b>Non-consummation</b> needs a wilful refusal. A marriage that was not consummated for other reasons does not meet the clause.</li>
            <li><b>Proof</b> matters. Many cases turn on whether the petitioner’s evidence actually established the ground, not on whether
              the ground exists in the Act.</li>
          </ul>
        </section>

        <section id="s10-related">
          <h2>Related sections you will see in cases</h2>
          <ul>
            <li><b>Section 17</b> — the rule on confirming a decree of dissolution. Heavily discussed in older cases.</li>
            <li><b>Section 19</b> — nullity: a marriage declared void.</li>
            <li><b>Section 22</b> — judicial separation.</li>
            <li><b>Section 32</b> — restitution of conjugal rights: an order that a spouse return to the marriage.</li>
            <li><b>Section 37</b> — alimony and maintenance when a marriage is dissolved.</li>
          </ul>
        </section>

        <section id="s10-read">
          <h2>Reading the cases on this site</h2>
          <p>
            Each result is a real judgment that discusses Section 10. The labels on the cards (ground, outcome, whether the marriage ended)
            are generated by rules, and “Not determined” means the rules could not tell. A case that lost on one ground may have been
            decided on a different one, and a decision from one High Court does not bind another. Use the original judgment, and a
            lawyer, before relying on any of it.
          </p>
          <p><a href="/">Start a search</a> · <a href="#/about">How this site works</a></p>
        </section>

        <p className="s10-checked">Law last checked against published text on {LAST_CHECKED}.</p>
      </main>
    </>
  );
}
