import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from labels import label_grounds, label_outcome, label_petitioner, segment_paragraphs


def P(*texts):
    return [{"p_id": f"p_{i+1}", "text": t} for i, t in enumerate(texts)]


KERALA = P(
    "1. The questions involved in this Matrimonial Appeal are : (1) Whether a petition for dissolution of marriage filed by the husband on the ground that the wife wilfully refused to consummate the marriage and the marriage therefore has not been consummated is maintainable.",
    "2. The parties are Indian Christians. Their marriage was solemnized on 29-8-1991.",
    "3. The respondent-wife in her counter stated that she hails from a highly educated family.",
    "24. We are of the view that the respondent was not justified in denying sex to the appellant. The wilful refusal to consummate is established.",
    "For the aforesaid reasons, we allow the Appeal, set aside the judgment of the Court below and allow the petition for dissolution of marriage under Clause (vii) of Sub-section (1) of Section 10 of the Divorce Act, 1869. A decree of dissolution of marriage is passed.",
)

MONIKA = P(
    "1. This is an appeal by the wife under Section 55 of the Indian Divorce Act directed against the order denying her a decree of divorce.",
    "3. The first respondent-husband remained absent and was set ex parte. The second respondent with whom it was alleged that the husband was having an adulterous relationship was also set ex parte.",
    "12. In this view of the matter we hold that the requirement of Section 16 is not applicable to the decree passed dissolving the marriage; the decree is made absolute.",
)


def test_non_consummation():
    grounds, primary, _ = label_grounds(KERALA, year=2007)
    assert primary == "non_consummation"


def test_adultery_beats_procedural_in_full_length_doc():
    # Stub of a longer judgment: adultery alleged in facts and decided in the holding,
    # while Sections 55/16 appear throughout (procedural noise).
    paras = MONIKA[:2] + P(*["The wife alleged adultery by the husband with the second respondent." if i % 3 == 0
                             else "Section 16 and Section 55 were considered." for i in range(12)]) + MONIKA[2:]
    grounds, primary, _ = label_grounds(paras, year=2002)
    assert primary == "adultery" and "procedural" not in grounds


def test_procedural_only_doc():
    paras = P("This appeal under Section 55 concerns confirmation of the decree nisi under Section 16 and Section 17.",
              "The jurisdiction of the court was questioned.", "Confirmation of decree is granted.")
    grounds, primary, _ = label_grounds(paras, year=2002)
    assert primary == "procedural"


def test_outcome_granted_and_dissolved():
    disposal, dissolved = label_outcome(KERALA)
    assert disposal == "allowed" and dissolved == "yes"


def test_outcome_dismissed():
    paras = P("x", "y", "For these reasons the appeal is dismissed. The petition for dissolution of marriage stands dismissed.")
    disposal, dissolved = label_outcome(paras)
    assert disposal == "dismissed" and dissolved == "no"


def test_outcome_unclear():
    assert label_outcome(P("a", "b", "c")) == ("unclear", "unclear")


def test_petitioner():
    assert label_petitioner(KERALA) == "husband"
    assert label_petitioner(MONIKA) == "wife"


def test_segments_cover_all_paragraphs_and_end_with_conclusion():
    segs = segment_paragraphs(KERALA)
    assert sum(len(s["p_ids"]) for s in segs) == len(KERALA)
    assert segs[-1]["type"] == "conclusion"


# ---------------- regression tests from the first 150-case run (v2 fixes) ----------------
from labels import label_disposal, label_dissolved, is_non_merits, clean_tail


def test_case5_respondent_granted_dissolution():
    paras = P("x", "In the result, the prayer of the petitioner for nullity of marriage is rejected and the respondent is granted a decree for dissolution of marriage on the grounds of cruelty simpliciter. The petition is dismissed.")
    assert label_dissolved(paras)[0] == "yes"
    assert label_disposal(paras) in ("dismissed", "partly_allowed")


def test_case9_refuse_to_confirm_gives_judicial_separation():
    paras = P("x", "7. In the result, we are not in a position to confirm the decree of dissolution passed by the learned District Judge. However, we pass a decree on the facts as noticed above for judicial separation.")
    assert label_dissolved(paras) == ("no", "judicial_separation")


def test_case2_signature_boilerplate_is_stripped():
    paras = P("The appeal lacks merit and is dismissed. The decree of the Family Court is affirmed.",
              "(Pradeep Kumar Srivastava, J.) (Pradeep Kumar Srivastava, J.)   Date : 14/07/2026  Birendra / A.F.R. Uploaded on 15/07/202659")
    assert label_disposal(paras) == "dismissed"
    assert "Uploaded" not in clean_tail(paras)


def test_case4_miscellaneous_petitions_ignored():
    paras = P("18. In view of the above discussion, this appeal is dismissed. Consequently, miscellaneous petitions, if any, pending in this appeal shall stand closed. ________________________ JUSTICE K. LAKSHMAN")
    assert label_disposal(paras) == "dismissed"


def test_case10_in_fine_allowed_with_url_boilerplate():
    paras = P("47. In fine, this Civil Miscellaneous Appeal is allowed. https://www.mhc.tn.gov.in/judis ( Uploaded on: 02/02/2026 06:05:06 pm )")
    assert label_disposal(paras) == "allowed"


def test_case3_remitted():
    paras = P("With the above observations, appeal is disposed of. Case is remitted back to the court below. No order as to costs.")
    assert label_disposal(paras) == "remanded"


def test_case6_petition_dismissed():
    paras = P("In the result, the petition is dismissed, but under the facts and circumstances of the case, ordering the parties to bear their respective costs.")
    assert label_disposal(paras) == "dismissed"


def test_case7_quashed_and_allowed():
    paras = P("31. Under the circumstances and in view of discussion (supra) the Appeal is allowed. The impugned judgment and order dated 17th July, 2008 is hereby quashed and set aside.")
    assert label_disposal(paras) == "allowed"


def test_case8_transfer_application_flagged():
    paras = P("This transfer application has been filed under Section 24 CPC seeking transfer of the matrimonial case.")
    assert is_non_merits("Anju Masih vs Prince Procha", paras)


def test_not_allowed_is_not_allowed():
    paras = P("The prayer is not allowed.")
    assert label_disposal(paras) != "allowed"


def test_wife_specific_needs_husband_context():
    quoted = P("Section 10 provides that a wife may petition if her husband has been guilty of rape, sodomy or bestiality.",
               *["The statute was quoted in the earlier judgment." for _ in range(10)])
    # a single quoted mention in the middle must not become the primary ground
    _, primary, _ = label_grounds(quoted[:1] + quoted[3:], year=1998)
    assert primary != "wife_specific"


def test_petitioner_cause_title_patterns():
    assert label_petitioner(P("X ... Appellant-husband   Vs   Y ... Respondent")) == "husband"
    assert label_petitioner(P("The wife filed the petition for divorce under Section 10.")) == "wife"
    assert label_petitioner(P("Smt X, petitioner (wife) approached this Court.")) == "wife"


# ---------------- v3 regression tests (second 150-case run) ----------------
from labels import petitioner_from_title
from dedupe import find_duplicates


def test_short_operative_paragraph_survives_tail_cleaning():
    paras = P("Long discussion " * 40, "Appeal dismissed.")
    assert "Appeal dismissed." in clean_tail(paras)
    assert label_disposal(paras) == "dismissed"


def test_case15_cannot_confirm_is_no_and_not_confirmed():
    paras = P("x", "In the circumstances, we regret, we cannot confirm the decree and set aside the decree for divorce passed by the learned District Judge in utter ignorance of the law.")
    assert label_dissolved(paras)[0] == "no"
    assert label_disposal(paras) == "not_confirmed"


def test_case13_incompetent_reference_is_unclear_not_yes():
    paras = P("x", "The reference by the Family Court for confirmation of decree for dissolution of marriage passed by him in suit No. 321 of 1993 is incompetent. For the reasons mentioned above, both the references are rejected.")
    assert label_dissolved(paras)[0] == "unclear"
    assert label_disposal(paras) == "dismissed"


def test_cases2_3_decree_confirmed():
    paras = P("The wife is entitled to a decree of divorce and the view of the District Judge is justified. Hence, the decree passed by the District Judge is confirmed.")
    assert label_disposal(paras) == "confirmed"
    assert label_dissolved(paras)[0] == "yes"


def test_case4_reference_accepted_decree_confirmed():
    paras = P("15. Hence, the reference is accepted. The decree for dissolution of marriage passed under section 10 of the Indian Divorce Act, 1869, by the learned Judge of the Family Court, is confirmed. No order as to costs.")
    assert label_dissolved(paras)[0] == "yes"
    assert label_disposal(paras) in ("allowed", "confirmed")


def test_case5_original_side_decree_nisi():
    paras = P("52. I, therefore, grant a decree nisi for dissolution of marriage as prayed by the petitioner wife in prayer (1) of the petition and I also order that the respondent husband shall pay the costs.")
    assert label_dissolved(paras) == ("yes", "dissolution")
    assert label_disposal(paras) == "allowed"


def test_case6_reference_discharged():
    paras = P("10. we are of the opinion that it is not possible to confirm the decree for divorce passed by the District Judge. Accordingly, the judgment is set aside, the decree is not confirmed and the reference is discharged.")
    assert label_disposal(paras) == "not_confirmed" and label_dissolved(paras)[0] == "no"


def test_case10_rehear_is_remand():
    paras = P("The District Judge shall re-hear the case after observing the formalities under Section 11 of the Act and dispose of the same in accordance with law.")
    assert label_disposal(paras) == "remanded"


def test_case1_modified_and_case8_interim():
    assert label_disposal(P("To this extent our earlier order/judgment dated 17-12-2002 stands modified.")) == "modified"
    assert label_disposal(P("Preliminary issue is found accordingly.")) == "interim"


def test_petitioner_title_fallback():
    assert petitioner_from_title("Saroj W/O Maical @ Babasaheb Patole vs Maical @ Babasaheb Sadanana Patole on 7 December, 1999") == "wife"
    assert petitioner_from_title("A vs B on 18 January, 1996") is None
    assert label_petitioner(P("nothing useful"), title="Smt. X vs Y") == "wife"


def test_dedupe_same_judgment_two_doc_ids():
    body = "The view taken by the District Judge that the wife is entitled to a decree of divorce is fully justified " * 6
    a = {"doc_id": "1316952", "title": "M.T. Carunya vs S. Joseph Chellappa on 15 September, 1995", "date": "1995-09-15", "paragraphs": [{"text": body}]}
    b = {"doc_id": "1858140", "title": "M.T. Carunya vs S. Joseph Chellappa on 15 September, 1995", "date": "1995-09-15", "paragraphs": [{"text": body + " extra"}]}
    c = {"doc_id": "9", "title": "Other vs Case on 1 January, 2000", "date": "2000-01-01", "paragraphs": [{"text": "completely different text about cruelty " * 20}]}
    dups = find_duplicates([a, b, c])
    assert len(dups) == 1 and dups[0][0] == "1858140" and dups[0][1] == "1316952"


# ---------------- v4 tests: dedupe tiers + gaps from the third run ----------------
from dedupe import classify_pairs


def test_same_title_date_but_different_text_is_review_not_drop():
    a = {"doc_id": "417034", "title": "Monika Sanctis vs Henry Joseph on 17 December, 2002", "date": "2002-12-17",
         "paragraphs": [{"text": "The appeal by the wife concerns a decree of divorce and the statutory waiting period. " * 30}]}
    b = {"doc_id": "447004", "title": "Monika Sanctis vs Henry Joseph on 17 December, 2002", "date": "2002-12-17",
         "paragraphs": [{"text": "We hold that the six months requirement is not a requirement under the statute and our earlier order stands modified. " * 30}]}
    res = classify_pairs([a, b])
    assert len(res) == 1 and res[0]["action"] == "review"
    assert find_duplicates([a, b]) == []          # nothing is dropped


def test_shorter_copy_contained_in_longer_is_dropped():
    long_ = "The wife is entitled to a decree of divorce on the ground of adultery proved by evidence. " * 40
    a = {"doc_id": "1", "title": "A vs B on 1 May, 1990", "date": "1990-05-01", "paragraphs": [{"text": long_}]}
    b = {"doc_id": "2", "title": "A vs B on 1 May, 1990", "date": "1990-05-01", "paragraphs": [{"text": long_[:len(long_)//2]}]}
    res = classify_pairs([a, b])
    assert res[0]["action"] == "drop" and res[0]["keep"] == "1"


def test_appeal_allowed_original_petition_dismissed_is_allowed():
    paras = P("37. Consequently, Matrimonial Appeal is allowed. The impugned judgment passed by the Family Court in O.P. No. 278/1997 is set aside. The Original Petition for dissolution of marriage shall stand dismissed. No order as to costs.")
    assert label_disposal(paras) == "allowed"
    assert label_dissolved(paras)[0] == "no"


def test_revision_petitions_dismissed():
    assert label_disposal(P("49. In the result, both the Civil Revision Petitions are devoid of merits and are accordingly dismissed. No costs.")) == "dismissed"


def test_decree_accordingly_affirmed():
    paras = P("On this basis, we are inclined to affirm the decree for divorce granted by the learned District Judge. The decree is accordingly affirmed. No costs.")
    assert label_disposal(paras) == "confirmed" and label_dissolved(paras)[0] == "yes"


def test_decree_nisi_issued_is_dissolved():
    paras = P("we allow the Appeal and allow the petition for dissolution of marriage under Section 10 of the Divorce Act, 1869. A decree nisi is issued for dissolution of marriage under Section 16 of the Divorce Act.")
    assert label_dissolved(paras) == ("yes", "dissolution")


def test_original_side_pronounce_decree():
    paras = P("32. I accordingly pronounce a decree for dissolution of marriage of the petitioner and respondent. There will be the usual decree nisi with costs.")
    assert label_dissolved(paras) == ("yes", "dissolution")


def test_nullity_declared():
    paras = P("15. We, therefore, allow the appeal and declare the marriage solemnised between the petitioner and the respondent on 18-8-1996 as null and void.")
    assert label_dissolved(paras) == ("yes", "nullity")


def test_restitution_of_conjugal_rights_is_no():
    paras = P("The appeal is allowed, the decree of the trial Court is set aside and a decree for restitution of conjugal rights is passed in favor of the appellant husband.")
    assert label_dissolved(paras) == ("no", "restitution")


def test_reference_answered_is_disposed_of():
    assert label_disposal(P("69. For these reasons, the reference is answered in the manner stated in the first paragraph.")) == "disposed_of"


def test_transfer_order_flagged_from_tail():
    paras = P("The matrimonial case is pending before the Family Court.", "The proceeding shall stand transferred to the Court of competent jurisdiction at Karwar. Accordingly, the petition is allowed.")
    assert is_non_merits("Mrs Olivia D Souza vs Mr Prakash", paras)


# ---------------- v5 tests: abbreviations, set-aside, mutual consent (fourth run) ----------------
def test_cmp_abbreviation_does_not_split_sentence():
    paras = P("11. In the result C.M.P. 53500/2001 is allowed and the marriage between the petitioner and the 1st respondent is dissolved by a decree nisi.")
    assert label_disposal(paras) == "allowed"
    assert label_dissolved(paras) == ("yes", "dissolution")


def test_first_appeal_no_abbreviation():
    paras = P("71. In the result, First Appeal No. 76 of 2020 is allowed. Decree accordingly. 72. Pending interlocutory application(s), if any, also stands disposed of.")
    assert label_disposal(paras) == "allowed"


def test_swamidas_decree_set_aside_is_no_not_yes():
    paras = P("Therefore, the judgment and decree for dissolution of the marriage on the ground of adultery granted by the Additional District Judge, Tirupathi is set aside, and O.P. No. 336 of 1988 is dismissed, but in the circumstances without costs.")
    assert label_dissolved(paras)[0] == "no"
    assert label_disposal(paras) in ("allowed", "dismissed")


def test_bare_set_aside_is_allowed():
    assert label_disposal(P("The impugned judgment and decree of the Family Court is set aside.")) == "allowed"


def test_set_aside_and_remitted_stays_remanded():
    assert label_disposal(P("The order is set aside and the matter is remitted to the Family Court for fresh disposal.")) == "remanded"


def test_mutual_consent_overrides_earlier_pleadings():
    paras = P("The husband alleged adultery and cruelty by the wife in the petition.", "Adultery was denied.",
              *["The allegations of cruelty and adultery were examined." for _ in range(6)],
              "The parties filed a joint petition for dissolution by mutual consent under Section 10A.",
              "In the result the marriage is dissolved on mutual consent by a decree nisi.")
    _, primary, _ = label_grounds(paras, year=2001)
    assert primary == "mutual_consent_10A"


def test_union_of_india_title_lowers_constitutional_threshold():
    paras = P("The petitioners challenge Section 10 as violative of Article 14.",
              "The classification is said to be violative of Article 21.",
              *["Section 10 and the Act were examined in the light of the statute." for _ in range(6)],
              "The policy of the law should protect the wife.")
    _, with_title, _ = label_grounds(paras, year=1982, title="Reynold Rajamani vs Union Of India")
    _, no_title, _ = label_grounds(paras, year=1982)
    assert with_title == "constitutional_validity"


# ---------------- v6 tests: mutual-consent false positives (fifth run) ----------------
def _long_doc_with_consent_discussion(closing):
    return P("The husband filed a petition alleging adultery and cruelty.",
             *["The statute and the Act were examined; Section 10A on mutual consent was referred to in passing." for _ in range(10)],
             closing)


def test_pre_2001_case_can_never_be_mutual_consent():
    # Section 10A did not exist before the 2001 amendment (Hemalatha 1990, Pragati 1997)
    paras = _long_doc_with_consent_discussion("The parties moved a joint petition for dissolution by mutual consent; the decree is not confirmed.")
    for _ in range(3):
        paras.insert(2, {"p_id": "x", "text": "Section 10A and mutual consent were discussed. Section 10A again."})
    _, primary, _ = label_grounds(paras, year=1990)
    assert primary != "mutual_consent_10A"


def test_union_of_india_challenge_is_not_mutual_consent():
    paras = _long_doc_with_consent_discussion("Section 10 is violative of Article 14. The law reform should consider mutual consent divorce and dissolution.")
    _, primary, _ = label_grounds(paras, year=2005, title="Reynold Rajamani vs Union Of India")
    assert primary != "mutual_consent_10A"


def test_contested_case_with_passing_10A_mention_in_middle_is_not_mutual_consent():
    paras = _long_doc_with_consent_discussion("The appeal is allowed and the decree of dissolution on the ground of adultery is confirmed.")
    _, primary, _ = label_grounds(paras, year=2003)
    assert primary != "mutual_consent_10A"


def test_negated_mutual_consent_in_tail_does_not_count():
    paras = _long_doc_with_consent_discussion("The petition for divorce is not by mutual consent and the appeal is dismissed.")
    _, primary, _ = label_grounds(paras, year=2010)
    assert primary != "mutual_consent_10A"


def test_real_consent_decree_after_2001_is_mutual_consent():
    paras = P("The husband alleged adultery and cruelty; the wife denied them.", "Adultery and cruelty were pleaded at length.",
              *["The earlier pleadings alleged adultery and cruelty." for _ in range(6)],
              "11. In the result CMP 53500/2001 is allowed and the marriage between the petitioner and the 1st respondent is dissolved on mutual consent by a decree nisi.")
    _, primary, _ = label_grounds(paras, year=2001)
    assert primary == "mutual_consent_10A"


# ---------------- v7 tests: verbatim false-positive tails and validity rules ----------------
def test_case_suryawanshi_refuse_confirmation():
    tail = ("19. In the result, we refuse to bestow our confirmation on the decree of divorce passed by "
            "the learned Additional District Judge, Ahmednagar. We, therefore, reject the Reference and "
            "dismiss the original Marriage Petition No. 3 of 1997 with no order as to costs.")
    assert label_dissolved(P(tail)) == ("no", "none")


def test_case_rajamani_suit_dismissed():
    tail = ("36. In fine, the suit is dismissed and the respondent-wife is entitled for maintenance of "
            "Rs.5,000/- per month from the petitioner from the date of the petition. She is also entitled "
            "for the right of residence in the petitioner's property till her life time. No cost.")
    assert label_dissolved(P(tail)) == ("no", "none")


def test_case_george_joseph_no_decree_obtainable():
    tail = ("Therefore, even in such cases of incurable mental illness of a spouse after the marriage "
            "no decree for dissolution of the marriage could be obtained. This anomaly can be cured "
            "only at the instance of the Legislature by bringing in appropriate amendments, to the Statute.")
    assert label_dissolved(P(tail)) == ("no", "none")


def test_case_paikas_khaka_no_decree_of_divorce():
    tail = ("practical purposes, there was no Decree of Divorce in favour of the petitioner dissolving his "
            "marriage with Ursulla. 20. For the reasons stated above, this Court holds that no illegality was "
            "committed by the respondents in taking action against the petitioner. Consequently, there is no "
            "merit in this Writ Application. The same is accordingly dismissed.")
    assert label_dissolved(P(tail)) == ("no", "none")


def test_case_kanku_reference_not_sustainable_rule_discharged():
    tail = ("56. I am also of the opinion that the petition in the reference before us in not sustainable "
            "under the provisions ofSections 18and19of the Indian Divorce Act and the rule issued is liable "
            "to be discharged. P.C. No orders are passed on these proceedings in accordance with the view of the majority.")
    assert label_dissolved(P(tail)) == ("unclear", "unclear")


def test_validity_challenge_dissolved_unclear():
    tail = "A decree of dissolution of marriage was passed by the court below. We hold Section 10 is unconstitutional."
    assert label_dissolved(P(tail), ground="constitutional_validity") == ("unclear", "unclear")


def test_validity_ammini_moves_to_constitutional_validity():
    paras = P("The petitioners challenge Section 10 as violative of Article 14 and Article 21.",
              "The wife alleges adultery and desertion and cruelty by the husband.",
              *["Section 10 discriminates against Christian women; equality under Article 14." for _ in range(8)],
              *["Adultery and cruelty were also cited in the petition." for _ in range(8)],
              "Section 10 is struck down in part.")
    _, primary, _ = label_grounds(paras, year=1995, title="Ammini E.J. vs Union Of India")
    assert primary == "constitutional_validity"


def test_validity_pragati_moves_to_constitutional_validity():
    paras = P("The constitutional validity of Section 10 of Indian Divorce Act is questioned.",
              "Article 14 and Article 21 of the Constitution were invoked.",
              *["The constitutional challenge to Section 10 is considered in depth." for _ in range(6)],
              *["Adultery was pleaded by the wife." for _ in range(8)],
              "The matter is remitted to the single Judge.")
    _, primary, _ = label_grounds(paras, year=1997, title="Mrs. Pragati Varghese vs Cyril George Varghese")
    assert primary == "constitutional_validity"


def test_case_vailshery_dismissed_with_affirmance_is_dissolved_yes():
    tail = ("12. There is no merit in this appeal which is dismissed with costs throughout. The order of the "
            "learned single Judge is upheld. The marriage of the parties is directed to be dissolved in terms "
            "of the decree passed in favour of the respondent wife. 13. Appeal dismissed.")
    assert label_dissolved(P(tail)) == ("yes", "dissolution")


def test_recital_without_affirmance_is_unclear():
    tail = "The learned District Judge passed a decree for divorce in favor of the petitioner. The appeal is dismissed."
    assert label_dissolved(P(tail)) == ("unclear", "unclear")


def test_remit_base_form_is_remand_pragati():
    paras = P("In any event, all that has been done in the instant case is to remit the present suits for trial to the learned single Judge. Prayer, in this behalf, is accordingly rejected. 59. Order accordingly.")
    assert label_disposal(paras) == "remanded"


# ---------------- Author v7 tests (restored from /tmp/v7/test_labels.py) ----------------
def test_rajesh_refuse_confirmation_and_dismiss_petition_is_no():
    paras = P("The Additional District Judge passed a decree for divorce which is before us for confirmation.",
              "For these reasons we refuse to bestow our confirmation on the decree of divorce passed by the learned Additional District Judge. We reject the Reference and dismiss the original Marriage Petition.")
    assert label_dissolved(paras)[0] == "no"


def test_rajamani_suit_dismissed_is_no_even_with_recital():
    paras = P("The decree for nullity was granted by the trial court at an earlier stage of the proceedings.",
              "In fine, the suit is dismissed and the respondent-wife is entitled for maintenance of Rs.5,000/- per month from the petitioner from the date of the petition.")
    assert label_dissolved(paras)[0] == "no"


def test_paikas_no_decree_of_divorce_in_favour():
    paras = P("For all practical purposes, there was no Decree of Divorce in favour of the petitioner dissolving his marriage with Ursulla. The Writ Application is accordingly dismissed.")
    assert label_dissolved(paras)[0] == "no"


def test_george_joseph_no_decree_for_dissolution_could_be_obtained():
    paras = P("In such cases of incurable mental illness of a spouse after the marriage no decree for dissolution of the marriage could be obtained. This anomaly can be cured only at the instance of the Legislature.")
    assert label_dissolved(paras)[0] == "no"


def test_kanku_reference_not_sustainable_is_unclear_not_yes():
    paras = P("The trial court had passed a decree for nullity of marriage.",
              "The petition in the reference before us is not sustainable under the provisions of Sections 18 and 19 of the Indian Divorce Act and the rule issued is liable to be discharged.")
    assert label_dissolved(paras)[0] == "unclear"


def test_dismissed_appeal_with_only_a_recital_is_unclear_not_yes():
    paras = P("The Family Court granted a decree for divorce passed in favour of the wife.",
              "We find no merit in the appeal and it is dismissed.")
    assert label_disposal(paras) == "dismissed"
    assert label_dissolved(paras)[0] == "unclear"


def test_dismissed_appeal_with_explicit_affirmation_is_yes():
    paras = P("The appeal is dismissed. The decree of dissolution passed by the Family Court is affirmed.")
    assert label_dissolved(paras)[0] == "yes"


def test_a_vs_b_court_itself_grants_dissolution_stays_yes():
    paras = P("In the result, the prayer of the petitioner for nullity of marriage is rejected and the respondent is granted a decree for dissolution of marriage on the grounds of cruelty simpliciter. The petition is dismissed.")
    assert label_dissolved(paras)[0] == "yes"


def test_constitutional_ground_gives_unclear_outcome():
    paras = P("The decree was discussed.", "Constitutional challenge decided; suits remitted for trial.")
    assert label_dissolved(paras, ground="constitutional_validity") == ("unclear", "unclear")


def test_constitutional_validity_beats_adultery_when_it_is_a_major_signal():
    paras = P("The petitioners challenge Section 10 as violative of Article 14 and Article 21.",
              *["Section 10 is ultra vires; the classification is violative of Article 14." if i % 2 == 0 else "The wife alleged adultery by the husband." for i in range(12)],
              "Section 10 is violative of Article 14 to that extent.")
    _, primary, _ = label_grounds(paras, year=1995, title="Ammini E.J. vs Union Of India")
    assert primary == "constitutional_validity"


# ---------------- v7.1 Regression Tests (15-case report fixes) ----------------
def test_walter_monteiro_writ_petition_dismissed_is_unclear_dissolved():
    paras = P("red opinion, the Court below is justified in converting the petition as the one underSection 10of the Indian Divorce Act, 1869 by transposing the petitioner herein as contesting respondent. 6. It is to be noted here itself that the evidence of the respondent is already recorded by the Court below fully. Now, the matter is posted for recording the evidence of the petitioner herein. Hence, no interference is called for on that ground also. Accordingly, the writ petition stands dismissed. JUDGE PMR")
    assert label_disposal(paras) == "dismissed"
    assert label_dissolved(paras)[0] == "unclear"


def test_henry_fernandes_plural_suits_dismissed_is_no():
    paras = P(" are untenable for they seek relief which is not permissible underSection 10. Hence, they would have to be dismissed. Since the suits themselves have been referred to us in exercise of the powers of the learned Chief Justice, we make the following order : \"M.J, Suit No. 7132 of 1999 and M.J. Suit No. 318 of 1998 are hereby dismissed with no order as to costs.\" Parties to act on an ordinary copy of this order duly authenticated by the Associate of this Court. Issuance of certified copy expedited.")
    assert label_disposal(paras) == "dismissed"
    assert label_dissolved(paras)[0] == "no"


def test_bhagyalaxmi_op_dismissed_wider_window_is_no():
    paras = P("In the result, this civil revision petition filed underArticle 227of the Constitution of India is allowed and the order dated 20.2.2007 made in IA No. 91 of 2006 in O.P. No. 89 of 2005 is hereby set aside. Consequently, in the light of the observations made by this Court that only Christians can maintain a petition for divorce under theDivorce Act, the O.P. filed by the respondent-husband is hereby dismissed. If the respondent-husband so chooses and is advised, he can file a separate O.P. under the provisions of theHindu Marriage Act. No costs.")
    assert label_disposal(paras) == "allowed"
    assert label_dissolved(paras)[0] == "no"


def test_s_rinu_direct_dissolution_of_marriage_is_yes():
    paras = P("appeared before this Honourable Court and agreed to mutually separated with my wife with my full consent.” 4. The learned counsel for the appellants also affirmed the said fact. 5. Even otherwise, we note that, as on date, the mandatory period of two years has expired from the date of separation. The appellants have taken a conscious decision to dissolve their marriage. We are also satisfied that there is no possibility for re-union and every attempt of reunion has failed. The parties are firm that they will not rejoin in the marital life. Hence, we would allow this Appeal and direct dissolution of marriage solemnised between the appellants on 12.06.2024 at CSI Christ Church, Kodungaiyur, Chennai. Page3 of 4 No. 1213 of 2026C.V.KARTHIKEYAN, J. AND K.RAJASEKAR, J. 6. Accordingly, this Civil Miscellaneous Appeal stands allowed. No costs. 18-06-2026 Index: Yes/No Speaking/Non-speaking order Neutral Citation: Yes/No GSK To V Additional Family Court, Chennai. CMA No. 1213 of 2026 Page4 of 4")
    assert label_disposal(paras) == "allowed"
    assert label_dissolved(paras)[0] == "yes"


def test_chitra_remit_record_is_transfer_not_remand():
    paras = P("pal Judge, Family Court, Kanpur Nagar is transferred to the Court of Principal Judge, Family Court, Jalaun at Orai. 7. The Principal Judge, Family Court, Kanpur Nagar is directed to remit the record of Case No.1108 of 2023 (Mohit Kumar (Maisi) Vs. Smt. Chitra Alias Mahima), underSection 10of Indian Divorce Act, 1869 to the Court of Principal Judge, Family Court, Jalaun at Orai for disposal of the same. 8. The Transfer Application is allowed with no order as to costs. Order 29.11.2023 R.S. Tiwari")
    assert label_disposal(paras) == "allowed"
    assert label_dissolved(paras)[0] == "unclear"


def test_ruth_remand_gives_unclear_outcome():
    paras = P(
        "16. The mandatory requirements ofSection 11of the Act not having been fulfilled, it is not possible to grant any relief to the husband in a proceeding initiated by the wife, by relying onSection 15of the Act. Hence, the decree-nisi for dissolution granted by the trial Court cannot be sustained and the same is hereby set aside.",
        "17. At this stage, the learned Counsel for the respondent submits that the matter be remitted back instead of driving the respondent to a fresh proceedings which will be time consuming. We, therefore, remit the matter to the trial Court for disposal in accordance with law. The petitioner and the respondent will be entitled to place such additional material as may be advised and the respondent may also, if he is so advised, seek the impleading of the alleged adulterer a co-respondent to the proceedings.",
        "18. Having regard to the fact that the petition is already three years old, the trial Judge is directed to dispose of the matter within four months from the date of receipt of the papers and copy of this order."
    )
    assert label_disposal(paras) == "remanded"
    assert label_dissolved(paras)[0] == "unclear"


def test_george_raju_singh_affirm_decree_requires_no_interference_is_yes():
    paras = P("89. Accordingly, issue as framed by this court that is decided against the appellant-husband and it is held that the judgment and decree passed by the learned family court, allowing the decree of divorce to the respondent-wife on the ground of cruelty underSection 10(x)of the Divorce Act, requires no interference. 90. Accordingly, the instant appeal fails and is dismissed. 91. Pending interlocutory application(s), if any, also stands disposed of. I agree. Dated : 21/04/2026 Birendra / .04.202640")
    assert label_disposal(paras) == "dismissed"
    assert label_dissolved(paras)[0] == "yes"


# ---------------- Precedence & Operative Remand Tests ----------------
def test_lokhande_790723_rehearing_discussion_is_partly_allowed():
    paras = P(
        "34. Similarly the argument on behalf of the learned Advocate for the respondent that decree nisi has to put for confirmation before the Bench of 2 or 3 High Court Judges would also pale into insignificance if the judgment of the Sind High Court in the case of Wiilliam Knox Hewson v. Mrs. Lilian Mary Hewson AIR 1947 Sind 18, is taken into consideration. According to that ratio, a decree passed by the High Court in its original jurisdiction by Single Bench has to be confirmed by that Judge and not Bench of Judges as mentioned inSection 17. On the other hand, an appeal referred from the decree of the Court of the first instance requires rehearing of the whole suit, as if litigated against the Court of appeal and the final decree in appeal to be the final decree of the suit, even if it is subject to variation. As indicated, the High Court in the above ruling was pleased to set aside the dismissal and ordered the dissolution of marriage.",
        "35. The learned Advocate for the respondent has contended that the observations in the judgment about the final payment of alimony subject to confirmation of decree underSection 37of the Act would mean that the decree passed in appeal was a decree nisi. I am afraid that this observation would not bar the consideration of the provisions ofDivorce Act. The above point about decree in appeal being final was not pressed in that appeal and, therefore, the Court was not required to decide that question. The only deducible ratio is that the High Court in appeal could pass the decree for dissolution of marriage.",
        "36. Even if the problem is reviewed from another angle, it would be found that no deadlock is created by adopting the interpretation as suggested above. The High Court sitting in appeal is duty bound and presumed to have done so on the detailed consideration of the evidence adduced before the trial Court and arrive at a conclusion other than one recorded by the District Judge. There is, therefore, a safeguard provided in appeal for passing the decree of dissolution without the same being required to be confirmed by the same Court.",
        "37. For all those reasons, it will have to be held that the view taken by the Rangoon High Court cannot be accepted and has to be respectfully dissented from. The arguments similar to those advanced here do not seem to have advanced before the Rangoon High Court. The High Court, therefore, was not required to consider all the ramifications ofSections 16and17and hence it will have to be observed that the decree in appeal passed by the High Court is not a decree nisi. It is a final decree which terminates the relationship between husband and wife and in that light of the matter, the appeal shall have to be allowed to that extent. The petitioner, brother of the deceased Virbala, shall not be entitled to the assets of the deceased Sumant Lokhande. Accordingly, the following order.",
        "38. The appeal is partly allowed and it is hereby declared that the assets of the deceased Sumant Lokhande shall be excluded from the probate together with the Will of Virbala and the petitioner Purushottam Sansare shall be entitled only to the assets and effects of the deceased Virbala. In the circumstances, the parties shall bear their own costs."
    )
    assert label_disposal(paras) == "partly_allowed"
    assert label_dissolved(paras, ground="procedural")[0] == "unclear"


def test_joseph_527509_remit_matter_is_remanded():
    paras = P("We, therefore, decline to confirm the decree granted by the District Judge and remit the matter to the District Court, Thalassery. The District Judge shall re-hear the case after observing the formalities underSection 11of the Act and dispose of the same in accordance with law as expeditiously as possible. The Registry is directed to dispatch the records to the District Court, Thalassery, forthwith.")
    assert label_disposal(paras) == "remanded"
    assert label_dissolved(paras)[0] == "unclear"


def test_susanta_mitra_50670_de_novo_is_remanded():
    paras = P("As we are setting aside the decree, we must make it clear that the whole suit must be heard de novo and the leave granted to the petitioner must not be confused as an excuse not to issue all the necessary notices to the respondent or respondents as required for the trial of this suit. Evidence already tendered in these proceedings if intended to be used over again can be tendered but only subject to cross-examination by the respondent or respondents who may appear at such re-hearing of the petition, with liberty to the petitioner to adduce such further or other evidence that he may be advised to produce in the light of the observations made in this judgment. 9. There should not be unnecessary delay in these proceedings and the matter should be expedited. 10. There will be no order as to costs. Laik, J. 11. I agree. R.N. Dutt, J. 12. I agree.")
    assert label_disposal(paras) == "remanded"
    assert label_dissolved(paras)[0] == "unclear"


def test_esther_rani_1342943_remand_matter_is_remanded():
    paras = P("In that view, we would remand the matter to the court below so that the parties may amend the pleadings, if so advised, and adduce further evidence, if any to substantiate their respective contentions. If an application for this purpose is made the learned Judge would look into the matter and pass appropriate orders. If the pleadings are amended and further evidence if any, is adduced, the learned Judge would address himself to the grounds available inS.10of the Act and dispose of the matter in accordance with law after properly considering the pleadings and evidence on record. 6. The reference underS.17of the Act is answered in the above terms. 7. Order accordingly.")
    assert label_disposal(paras) == "remanded"
    assert label_dissolved(paras)[0] == "unclear"


def test_deepika_couto_893002_remand_discussion_is_dismissed():
    paras = P(
        "6. An appeal underSection 55of the Indian Divorce Act, as amended by U. P Amendment of 1957, deleting the first proviso to the section, lies to this Court and consequently the court of the District Judge which passed the decree in the present case is under the supervisory jurisdiction of this Court. Clause (1) ofArticle 227of the Constitution provides that a High Court shall have superintendence over all courts subject to its appellate jurisdiction. The primary object of this supervisory jurisdiction of the High Court, according to the consensus of authorities, is that the courts over which the High Court has such superintendence must be kept within the bounds of law. Whenever such bounds are exceeded the High Court is competent in the exercise of its powers underArticle 227of the Constitution to pass an appropriate order. It is also settled by the authorities that the jurisdiction of the High Court underArticle 227of the Constitution is wider than underArticle 226.As observed by the Supreme Court inHari Vishnu Kamath v Ahmad Ishaque(AIR 1955 SC 233) while in a certiorari underArticle 226the High Court can only annul the decision of the Tribunal, it can, underArticle 227, do that, and also issue further directions in the matter. In other words, in exercise of powers underArticle 227of the Constitu-jtion, the High Court cannot only quash 'an order, as in the present case, as being without jurisdiction, but can also issue further appropriate directions such as for the remand of the case and its decision in accordance with law. We cannot jallow an incompetent order or decree, which has been brought to the notice of this Court, to stand on the ground that it now suits the parties not to prolong the litigation between them but to ring down the curtain.",
        "6-A. Before parting with the case we would, however, like to observe that the learned District Judge passed a manifestly erroneous decree without applying his mind even to the preliminary question as to whether his jurisdiction was invoked on any of the grounds relevant toSection 10of the Act.",
        "7. For these reasons we dismiss the application for reference as incompetent and also quash the ex parte decree dated 18th Dec., 1976 for divorce passed by the District Judge, Gorakhpur. We direct him to decide the application in accordance with law and the observations made by us. It would, however, be open to the petitioner to seek such amendment as she may be advised when the matter goes back and it will be for the court below to deal with such request in accordance with law.",
        "8. In the circumstances of the case we make no order as to costs."
    )
    assert label_disposal(paras) == "dismissed"
    assert label_dissolved(paras)[0] == "unclear"


def test_premchand_hira_1799882_dropped_remand_is_unclear():
    paras = P(
        "28. We think, therefore, that on the evidence now before us there should be a decree absolute for dissolution of the marriage. There remains the question of damages. As pointed out in the previous judgment, the learned Judge originally held that no damages ought to be granted against the co-respondent because they are not mentioned inSection 10of the Act. We, however, pointed out that the relevant section is notSection 10, butSection 34which clearly provides for damages. We, therefore, directed the learned Judge to record a finding as to damages. The learned Judge has not done so having regard to his findings as to condonation. But with great respect to the learned Judge, in my opinion it was his duty to record findings to all the questions sent on remand and not to omit certain answers because of the view he took of the law. The law was for this appellate Court finally to decide. However, under all the circumstances we do not propose to send the case back for a second remand. There is evidence here by the petitioner as to the damages he has sustained by the co-respondent's conduct, and we think we have power to award them. He says his wife was a good wife to him, that they lived happily together, and that this lasted some ten or eleven years. Then the co-respondent formed an improper acquaintance with the wife; he took her away; the husband got the wife back again and gave her another chance for some two or three months, and then the corespondent abducted the wife a second time, and has been living with her ever since. It is clearly, therefore, a case where the co-respondent has deliberately broken up the home. Under those circumstances we think it is a ease where damages should be awarded, and having regard to all the circumstances of the case, and the condition in life of the parties, and in particular to the loss which we think the husband has suffered, we think a sum of Rs. 300 would be a proper sum to award as damages.",
        "29. Therefore, the order I would pass would be to pass a decree absolute for the dissolution of the marriage, and to award a sum of Rs 300 as damages against the co-respondent. He must also pay the costs of the proceedings throughout.",
        "Crump, J.",
        "30. I agree.",
        "Blackwell, J.",
        "31. I agree."
    )
    assert label_disposal(paras) == "unclear"
    assert label_disposal(paras) != "remanded"
    assert label_dissolved(paras)[0] == "yes"


def test_lokhande_790723_flagged_as_non_merits():
    paras = P(
        "JUDGMENT",
        "1. The important question which has been posed for determination in this appeal is whether the decree passed by the High Court in appeal, dissolving the marriage between the husband and wife...",
        "2. In view of the extensive arguments advanced...",
        "3. It is, therefore, necessary to consider the facts giving rise to this appeal...",
        "4. It may be stated that the parties were Indian Christians and were governed by the provisions of the Indian Divorce Act...",
        "5. However, Anilkumar Vasant Lokhande, the nephew of deceased Sumant Madhav Lokhande, filed Misc. Applicant No. 449 of 1976/in the District Court, Pune for obtaining succession certificate... It seems that the same was dismissed because Sansare had no locus standi to file the application in the absence of probate."
    )
    assert is_non_merits("Mr. Anil Kumar Vasant Lokhande vs Mr. Purushottam Vinayak Sansare And ... on 12 January, 1993", paras)







