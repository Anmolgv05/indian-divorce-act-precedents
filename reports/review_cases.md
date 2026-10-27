# Task 5: 20-Case Manual Validation Dossier

Review instructions for reviewers B and C:
- For each case, read the excerpt and verify the model's extracted labels.
- Mark `1` (or `yes`) in `reports/review_sheet.csv` if the label is accurate, or `0` (or `no`) if incorrect.
- If incorrect, record the true legal outcome in `correct_value_if_wrong`.
- Run `python src/validate.py --score reports/review_sheet.csv` to compute validation metrics.

---

## [1] Case 850953: N. Sarada Mani vs G. Alexander And Anr. on 21 October, 1997

- **URL:** [https://indiankanoon.org/doc/850953/](https://indiankanoon.org/doc/850953/)
- **Court & Date:** Andhra HC (Pre-Telangana) (1997-10-21)
- **Model Ground:** `adultery` (All detected: ['adultery', 'desertion', 'cruelty'])
- **Model Disposal:** `confirmed`
- **Model Dissolution:** `yes` (Relief: `dissolution`)
- **Model Petitioner:** `wife`

### Head Excerpt (First 600 chars):
> JUDGMENT
 

P. Ramakrishnam Raju, J. 1. This is an application filed by the wife underSection 10of the Indian Divorce Act (hereinafter referred to as 'Act') seeking divorce on the ground that her husband, the first respondent, is living in adultery with the second respondent and that he treated her with cruelty, beating her and threatening to kill her. The first respondent-husband, while admitting his marriage with the petitioner on 28-6-1989, denied that he received any dowry nor treated the petitioner with any cruelty. He also further denied that he had any illicit intimacy with the second r

### Cleaned Tail (Last 800 chars):
> ccupy the field, the grounds available to the wife for divorce shall be, available to husband as well. Wedo so, as unquestionably that construction which is inconsonance with the common law and in our country with the Constitution of India has to be accepted which would promote the intentions of the Constitution and the common law and not one which would conflict with the same. Suffice it for the present that the wife, who is the petitioner herein, has established that there is desertion by her husband without reasonable excuse for two years or upwards. On this basis, we are inclined to affirm the decree for divorce gran ted by the learned District Judge although not on the ground that there is irretrievable incompatibility between the spouses. The decree is accordingly affirmed. No costs.

### Segments Preview:
- **[facts]** (`pre_1`): JUDGMENT    P. Ramakrishnam Raju, J....
- **[law]** (`p_1, p_2, p_3, p_4, p_5, blockquote_1, blockquote_2, blockquote_3, p_6`): 1. This is an application filed by the wife underSection 10of the Indian Divorce Act (hereinafter referred to as 'Act') seeking divorce on the ground ...
- **[reasoning]** (`p_7, blockquote_5, p_8, blockquote_6, p_9, blockquote_7, p_10`): 7. We are aware that it is well settled principle of law that while resorting to interpreting some of the provisions of a statute, Courts should be lo...
- **[law]** (`p_11, p_12, p_13`): 9. A reading ofSection 10of the Act, 1869 shows that the Act remained on the Statute book without undergoing slightest change for all these years. The...
- **[issue]** (`p_14, p_15, p_16`): 12. Argumentum inconvenienti, principle of hardship, absurdity, have no application, while interpreting the statutes. But, however the cardinal princi...
- **[conclusion]** (`p_17`): 15. Therefore, we are of the opinion that the grounds which are available to the wife underSection 10should also be made available to the husband in a...

---

## [2] Case 1600938: Grace Jayamani vs E.P. Peter on 17 July, 1981

- **URL:** [https://indiankanoon.org/doc/1600938/](https://indiankanoon.org/doc/1600938/)
- **Court & Date:** Karnataka High Court (1981-07-17)
- **Model Ground:** `wife_specific` (All detected: ['wife_specific', 'cruelty'])
- **Model Disposal:** `confirmed`
- **Model Dissolution:** `yes` (Relief: `dissolution`)
- **Model Petitioner:** `unclear`

### Head Excerpt (First 600 chars):
> JUDGMENT


 

Sabhahit, J. 1. This reference underS. 17of the Indian Divorce Act. 1869 is by the District Judge. Dakshina Kannada, Mangalore in Matrimonial Case No. 3 of 1979 on his file. 2. Smt. Grace Jayamani presented a petition to the District Judge. Dakshina Kannada. Mangalore. underS. 10of the Indian Divorce Act for dissolution of the marriage of the petitioner with the respondent, Sri E. P. Peter and for grant of a decree of divorce. She averred in the petition thus: The petitioner and the respondent belong to Protestant Christian community and profess the said religion. They were marri

### Cleaned Tail (Last 800 chars):
> no hesitation to hold on the facts of the case that the learned District Judge was justified in coming to the conclusion that the husband in the case Committed sodomy on his wife by forcing her for carnal copulation per anus and per os. 14. The conduct of the husband during the trial and the fact that the husband remained absent, though he filed objections, would make it clear that there is no collusion between the parties. We are satisfied with the finding of the learned District Judge that there is no collusion between the parties and we are further satisfied that the parties are Protestant Christians and reside in the jurisdiction of the Court. 15. In the result, the decree for dissolution of the marriage of the petitioner with the respondent is hereby confirmed. 16. Order accordingly.

### Segments Preview:
- **[facts]** (`pre_1, p_1, p_2, blockquote_1, blockquote_2, p_3, p_4`): JUDGMENT      Sabhahit, J. 1. This reference underS. 17of the Indian Divorce Act. 1869 is by the District Judge. Dakshina Kannada, Mangalore in Matrim...
- **[issue]** (`blockquote_3, blockquote_4`): (i) Whether the provisions of the Act apply to the petitioner and the respondent? (ii) Whether the petitioner and the respondent reside or last reside...
- **[law]** (`blockquote_5`): (iii) Whether the petitioner has made out grounds underSection 10of the Act for dissolution of her marriage with respondent?...
- **[issue]** (`blockquote_6, blockquote_7, p_5, p_6, p_7, p_8, p_9, p_10, p_11, blockquote_8, p_12, blockquote_9, p_13, blockquote_10, p_14, blockquote_11, p_15, blockquote_12, blockquote_13`): (iv) Whether there is no collusion between the petitioner and respondent? (v) Whether the petitioner is entitled to the decree of dissolution of her m...
- **[reasoning]** (`p_16`): Thus it is evident that the term 'Sodomy', as it is understood currently in the Court for Divorce and Matrimonial cases in England, to which this Cour...
- **[issue]** (`blockquote_14, p_17, p_18, p_19, blockquote_15, p_20, blockquote_16, p_21, blockquote_17, p_22, p_23`): "Sodomv: It is a felony by the Sexual Offences Act. 1956 (Sect. 12) for a person to commit buggery with another person, which means the action of a ma...
- **[conclusion]** (`p_24, p_25`): 15. In the result, the decree for dissolution of the marriage of the petitioner with the respondent is hereby confirmed. 16. Order accordingly....

---

## [3] Case 1815443: Raphael Damacious vs Mrs. Teresa Raphael And Anr. on 8 September, 1989

- **URL:** [https://indiankanoon.org/doc/1815443/](https://indiankanoon.org/doc/1815443/)
- **Court & Date:** Patna High Court (1989-09-08)
- **Model Ground:** `adultery` (All detected: ['adultery'])
- **Model Disposal:** `not_confirmed`
- **Model Dissolution:** `no` (Relief: `none`)
- **Model Petitioner:** `unclear`

### Head Excerpt (First 600 chars):
> JUDGMENT N.P. Singh, U.P. Singh and B.N. Agrawal, JJ. 1. A decree for dissolution of the marriage between the applicant and respondent No. 1 has been forwarded to this Court by the District Judge, Dumka for confirmation in accordance with the provisions ofSection 17of the Indian Divorce Act, 1869 (hereinafter referred to as 'the Act'). 2. In appears that the applicant filed an application underSection 10of the Act levelling a charge of adultery against his wife, respondent No. 1, and sought a decree for divorce on that ground. I, may be mentioned that Undersection 10any husband may present a p

### Cleaned Tail (Last 800 chars):
> school. In that view of the matter, under changed circumstances, there could be nothing unusual in respondent No. 2 at time visiting the residence of the applicant or even meeting the wife of the applicant respondent No. 1. In our opinion, on the materials on record, it is not possible to record a categorical finding that the applicant has been able to prove to the satisfaction of the Court that his wife, respondent No. 1, has been guilty of adultery because of which a decree for divorce should have been passed. 10. For the reasons mentioned above, we are of the opinion that it is not possible to confirm the decree for divorce passed by the District Judge, Dumka. Accordingly, the judgment of the District Judge, Dumka is set aside, the decree is not confirmed and the reference is discharge.

### Segments Preview:
- **[facts]** (`pre_1, p_1`): JUDGMENT N.P. Singh, U.P. Singh and B.N. Agrawal, JJ....
- **[law]** (`p_2, p_3`): 1. A decree for dissolution of the marriage between the applicant and respondent No. 1 has been forwarded to this Court by the District Judge, Dumka f...
- **[conclusion]** (`p_4`): 3. The learned Counsel appearing for the applicant and respondent No. 1, the wife, at the outset, informed the Court that, after the decree for divorc...
- **[law]** (`p_5, p_6`): 4. The learned Counsel appearing for respondent no. 1, the wife, pointed out they from a bare reference to the application underSection 10itself it sh...
- **[conclusion]** (`p_7, blockquote_1, p_8`): 6.Section 10enables any husband to present a petition for dissolution of his marriage only on the ground that since the solemnization of the marriage ...
- **[law]** (`p_9`): 8. In the instant case, as already pointed out, in the petition underSection 10itself, only some vague allegations have been made. It has been said by...
- **[reasoning]** (`blockquote_2`): "Having regard to the standard or society, of which the petitioner and his wife are members, it is difficult to suggest that the respondent was not ex...
- **[conclusion]** (`p_10, p_11`): 9. There is no dispute, in the present case, that respondent No. 2 during the relevant time was an Administrator of the School in question in which th...

---

## [4] Case 672495: Amarthala Hemalatha vs Dasari Balu Rajendra Varaprasad on 5 March, 1990

- **URL:** [https://indiankanoon.org/doc/672495/](https://indiankanoon.org/doc/672495/)
- **Court & Date:** Andhra HC (Pre-Telangana) (1990-03-05)
- **Model Ground:** `desertion` (All detected: ['desertion', 'adultery', 'cruelty'])
- **Model Disposal:** `not_confirmed`
- **Model Dissolution:** `no` (Relief: `judicial_separation`)
- **Model Petitioner:** `wife`

### Head Excerpt (First 600 chars):
> ORDER
 

Jagannadha Rao, J. This reference application has come before us underSection 17of the Indian Divorce Act 1869 (hereinafter called the Act) for confirmation of the order of lower Court in regard to the dissolution of marriage between the petitioner and the respondent. 2. The petitioner before the learned District Judge was the wife and she filed the application underSec. 14of the Act for dissolution of the marriage between her and the respondent. It is averred in the petition that the petitioner and the respondent are Christians and have been married on 6-1-1975 at Eluru, that the hus

### Cleaned Tail (Last 800 chars):
> e passing of the decree for judicial separation. We are, therefore, unable to confirm the decree for dissolution as granted by the lower Court. We hold that it will be necessary for the wife to file a fresh petition and seek divorce only on the specified grounds mentioned inS. 10of the Act. She may, therefore, pursue her remedies in accordance with law. 21. We thank Sri C. Sadasiva Reddi, Advocate, for helping the court in this matter at our request. 22. For the aforesaid reasons, we refuse to confirm the decree for dissolution of the marriage on the grounds mentioned in the O.P. but we however pass only a decree of Judicial separation. The petitioner may however pursue her remedies for divorce in accordance withS. 10of the Act. The reference is disposed of accordingly. Answer accordingly.

### Segments Preview:
- **[facts]** (`pre_1`): ORDER    Jagannadha Rao, J....
- **[law]** (`p_1`): This reference application has come before us underSection 17of the Indian Divorce Act 1869 (hereinafter called the Act) for confirmation of the order...
- **[conclusion]** (`p_2`): 2. The petitioner before the learned District Judge was the wife and she filed the application underSec. 14of the Act for dissolution of the marriage ...
- **[law]** (`p_3`): 3. It is true that underSection 13(1)(A)of the Hindu Marriage Act 1955 as well as underSec.27(1)(i)of the Special Marriage Act 1954 parties to the mar...
- **[issue]** (`p_4, p_5`): 4. The point therefore arises whether the matter arising under theIndian Divorce Act1869 the District Court could pass a decree for divorce, subject t...
- **[law]** (`p_6`): 6. It will be noticed that under theIndian Divorce Act1869 the grounds for divorce at the instance of the wife are not the same as the grounds for div...
- **[reasoning]** (`p_7, blockquote_1`): 7. In a case where the wife does not allege change of religion and remarriage by the  husband and is also unable to prove adultery in the manner menti...
- **[conclusion]** (`p_8`): 8. In the sections immediately followingSec. 22we find the following consequences after judicial separation.Section 24says that in every case of judic...
- **[reasoning]** (`p_9, p_10, p_11, p_12`): 9. The question arises as to what is meant by a divorce a mensa et toro mentioned in one of the sub-clauses inSection 10and also inSection 22of the Ac...
- **[law]** (`p_13, p_14, p_15, p_16`): 13. However, the Indian Law of Divorce so far as Christians are concerned has remained stagnant since 1869. No provision has been introduced for permi...
- **[reasoning]** (`p_17, blockquote_2, blockquote_3`): 16.Section 7of the Act states that the Courts in India have to act upon principles of English Divorce Court. The question arises whether this is refer...
- **[law]** (`p_18, p_19, p_20`): 17. The abovesaid provision had been interpreted by different High Courts differently. A Division Bench of the Bombay High Court consisting of Chagla,...
- **[reasoning]** (`p_21, p_22`): 20.In view ofthe said decisionof the Supreme Court, it is not permissible for the parties to seek dissolution of the marriage on  grounds presently co...
- **[conclusion]** (`p_23, p_24`): 22. For the aforesaid reasons, we refuse to confirm the decree for dissolution of the marriage on the grounds mentioned in the O.P. but we however pas...

---

## [5] Case 40579: Jose vs Ali Joseph on 29 June, 1990

- **URL:** [https://indiankanoon.org/doc/40579/](https://indiankanoon.org/doc/40579/)
- **Court & Date:** Kerala High Court (1990-06-29)
- **Model Ground:** `adultery` (All detected: ['adultery'])
- **Model Disposal:** `remanded`
- **Model Dissolution:** `unclear` (Relief: `unclear`)
- **Model Petitioner:** `husband`

### Head Excerpt (First 600 chars):
> JUDGMENT
 

Varghese Kalliath, J. 1. A well educated young couple with two children are before us. The husband filed a petition underSection 10of the Indian Divorce Act, for short, the Act, to shap the marriage tie by a decree of the court dissolving the marriage with his wife, the counter petitioner Their marriage was on 21-5-1979. Parties belong to Roman Catholic Community and their marriage was solemnised at the Bishop's House, Kottayam. After the marriage, the counter petitioner gave birth to two children, 2.Section 10of the Act provides that a husband may present a petition to the Distric

### Cleaned Tail (Last 800 chars):
> the appellant herein should not stand in the way of proper disposal of the case. So, we feel that the judgment now challenged has to be set aside and the matter has to be remitted back to the court below so as to enable the appellant to file an application as contemplated underSection 11of the Act for excusing the appellant from not making the adulterer a co-respondent in the petition. We do so. This application has to be tried first and if the court is satisfied that there are sufficient grounds for allowing the application, the court can try the main application on merits. It will be a trial de novo. With the above observations, appeal is disposed of. Case is remitted back to the court below. No order as to costs. Parties are directed to appear before the lower court on 30th July, 1990.

### Segments Preview:
- **[facts]** (`pre_1`): JUDGMENT    Varghese Kalliath, J....
- **[law]** (`p_1, p_2, p_3, p_4, p_5, p_6, blockquote_1, blockquote_2`): 1. A well educated young couple with two children are before us. The husband filed a petition underSection 10of the Indian Divorce Act, for short, the...
- **[petitioner_argument]** (`p_7, p_8`): 6. In the petition, the petitioner has stated thus :--(Matter ommitted as in Vernakular) 7. Further, in paragraph 9 of the petition, he has stated tha...
- **[law]** (`p_9, p_10, p_11`): 8. There is a serious controversy as regards the question whether before proceeding to try a petition for divorce on the ground of adultery and if tha...
- **[reasoning]** (`p_12`): 11. In this case, the court below found that the husband was not able to establish the ground that since the solemnization of the marriage, the wife h...
- **[law]** (`p_13, p_14, p_15, p_16, p_17`): 12.Section 11of the Act enjoins a responsibility on the part of the husband to make the alleged adulterer a co-respondent in the petition. In this cas...
- **[conclusion]** (`p_18`): With the above observations, appeal is disposed of. Case is remitted back to the court below. No order as to costs. Parties are directed to appear bef...

---

## [6] Case 18226488: Dr. G.M. Pradeep Kumar, Kadapa District vs Smt. Uma Maheswari, Proddatur on 2 January, 2025

- **URL:** [https://indiankanoon.org/doc/18226488/](https://indiankanoon.org/doc/18226488/)
- **Court & Date:** Andhra Pradesh High Court - Amravati (2025-01-02)
- **Model Ground:** `desertion` (All detected: ['desertion', 'cruelty', 'adultery'])
- **Model Disposal:** `remanded`
- **Model Dissolution:** `unclear` (Relief: `unclear`)
- **Model Petitioner:** `husband`

### Head Excerpt (First 600 chars):
> 1
 (RNT,J & CGR,J
 C.M.A.NO.650 OF 2008)

 * THE HONOURABLE SRI JUSTICE RAVI NATH TILHARI

 *THE HONOURABLE SRI JUSTICE CHALLA GUNARANJAN

 + CIVIL MISCELLANEOUS APPEAL NO: 650 OF 2008

 % 02.01.2025



# Dr. G.M. Pradeep Kumar,
 Kadapa District
 ......Petitioner

And:

$ Smt Uma Maheswari
 Proddatur
 ....Respondent.

!Counsel for the petitioner : Sri S.Lakshminarayana Reddy

^Counsel for the respondent : Sri Nagaraju Naguru



<Gist:

>Head Note:

? Cases referred: NIL
 2
 (RNT,J & CGR,J
 C.M.A.NO.650 OF 2008)




 HIGH COURT OF ANDHRA PRADESH AT AMARAVATI

 ****

 CIVIL MISCELLANEOUS APPEAL

### Cleaned Tail (Last 800 chars):
> rary to the statutory provisions. 12. The Civil Miscellaneous Appeal is allowed. The order, dated 17.04.2008 passed in D.O.P.No.349 of 2004 on the file of the Principal District Judge, Kadapa is hereby set aside. The matter is remitted to the learned Court for fresh consideration of the petition for divorce, with due notice to the respondent/wife, in accordance with law, within a period of one (01) year from the date of the receipt of a copy of this judgment. No order as to costs. As a sequel thereto, miscellaneous petitions, if any pending, shall also stand closed. RAVI NATH TILHARI, J CHALLA GUNARANJAN,J (RNT,J & CGR,J C.M.A.NO.650 OF 2008)220THE HONOURABLE SRI JUSTICE RAVI NATH TILHARI THE HONOURABLE SRI JUSTICE CHALLA GUNARANJAN (ALLOWED) CIVIL MISCELLANEOUS APPEAL NO: 650 of 2008 RPD.

### Segments Preview:
- **[respondent_argument]** (`pre_1, p_1`): 1  (RNT,J & CGR,J  C.M.A.NO.650 OF 2008)   * THE HONOURABLE SRI JUSTICE RAVI NATH TILHARI   *THE HONOURABLE SRI JUSTICE CHALLA GUNARANJAN   + CIVIL MI...
- **[law]** (`p_2, p_4, p_5, p_6, p_8, p_10`): 2. This appeal has been filed by the appellant/husband,  challenging the dismissal of the petition for divorce under Section 104(RNT,J & CGR,J  C.M.A....
- **[issue]** (`p_12`): 8. Now the point that arises for determination is :-...
- **[law]** (`blockquote_1, p_13, blockquote_2, blockquote_3, blockquote_4, blockquote_5, blockquote_6, blockquote_7, blockquote_8, blockquote_9, blockquote_10, blockquote_11, p_14, p_15, p_16, p_17`): "Whether divorce can be sought on the   ground of 'cruelty' or/and 'desertion' underSection 10of the Indian Divorce Act or only   on the ground of adu...
- **[conclusion]** (`p_18, p_19, p_20, p_22, p_23, p_25`): 12. The Civil Miscellaneous Appeal is allowed. The order,  dated 17.04.2008 passed in D.O.P.No.349 of 2004 on the file of the  Principal District Judg...

---

## [7] Case 1660230: Dennis Lall vs Smt. Amita Lall on 3 March, 1997

- **URL:** [https://indiankanoon.org/doc/1660230/](https://indiankanoon.org/doc/1660230/)
- **Court & Date:** Allahabad High Court (1997-03-03)
- **Model Ground:** `procedural` (All detected: ['procedural'])
- **Model Disposal:** `dismissed`
- **Model Dissolution:** `unclear` (Relief: `unclear`)
- **Model Petitioner:** `unclear`

### Head Excerpt (First 600 chars):
> JUDGMENT
 

 G.P. Mathur, J. 1. The two appeals have been placed before this Special Bench, on a reference made by Judge, Family Court, Jhansi. The appeals are being disposed of by a common order as the controversy raised is identical. 2. Dennis Lal filed a petition underSection 22of Divorce Act, 1869 (hereinafter referred to as the Act) against his wife Smt. Amita Lall, which was registered as suit No. 270 of 1994, praying that a decree of judicial separation be passed on the ground of adultery and cruelty. The Judge, Family Court, Jhansi passed a decree for judicial separation on 21-5-96 but

### Cleaned Tail (Last 800 chars):
> r the Central Act. The Central Act has been drastically amended by the U. P. Act andSection 17has been amended in the following manner: "1. Paragraph one to five shall be omitted. 2. In paragraph six words "or special" occurring between the words "general" and "or" shall be omitted." 6. In view of the U. P. Amendment, a decree for dissolution of marriage made by a District Judge does not require confirmation by the High Court and is effective by itself. Therefore the reference made by the Judge, Family Court for confirmation of decree for dissolution of marriage passed by him in suit No. 321 of 1993 is incompetent. 7. For the reasons mentioned above, both the references are rejected. The Judge, Family Court, Jhansi, is directed to pass final orders in accordance with law in both the suits.

### Segments Preview:
- **[facts]** (`pre_1, p_1`): JUDGMENT     G.P. Mathur, J. 1. The two appeals have been placed before this Special Bench, on a reference made by Judge, Family Court, Jhansi. The ap...
- **[conclusion]** (`p_2, p_3, p_4`): 2. Dennis Lal filed a petition underSection 22of Divorce Act, 1869 (hereinafter referred to as the Act) against his wife Smt. Amita Lall, which was re...
- **[law]** (`p_5, blockquote_1, blockquote_3`): 5. Section 17 of the Principal Act which provides that every decree for dissolution of marriage made by a District Judge shall be subject to confirmat...
- **[conclusion]** (`p_6, p_7`): 6. In view of the U. P. Amendment, a decree for dissolution of marriage made by a District Judge does not require confirmation by the High Court and i...

---

## [8] Case 1353346: P.E. Mathew vs Union Of India (Uoi) on 3 May, 1999

- **URL:** [https://indiankanoon.org/doc/1353346/](https://indiankanoon.org/doc/1353346/)
- **Court & Date:** Kerala High Court (1999-05-03)
- **Model Ground:** `constitutional_validity` (All detected: ['constitutional_validity'])
- **Model Disposal:** `dismissed`
- **Model Dissolution:** `yes` (Relief: `dissolution`)
- **Model Petitioner:** `unclear`

### Head Excerpt (First 600 chars):
> JUDGMENT
 

 Ar. Lakshmanan, J. 1. These two Original Petitions raise the same question with regard to the validity ofSection 17of the Indian Divorce Act, 1986 (hereinafter referred to as 'the Act') which says that a decree for dissolution of marriage passed by a District Judge has to be confirmed by a three-Judge Bench of the High Court. According to the petitioners, this confirmation is required only for Christians and so it is discriminatory, arbitrary and violative ofArticles 13(1), 14, 15(1)and21of the Constitution of India. It is further submitted that since this section is to consistent

### Cleaned Tail (Last 800 chars):
> en though none of the parties is desir-ous of preferring an appeal. In our opinion, there is no justification for continuation of this procedure especially when no such procedure is prescribed by other Acts dealing with dissolution of marriages, namely,Special Marriage Act, 1954andHindu Marriage Act, 1955. In our view, there is an urgent need for making suitable amendments in the Act. In this light, we direct the Government of Kerala to bring in an amendment on the lines of Uttar Pradesh amendment as we feel that such an amendment is necessary and expedient. 15. Subject to the above directions, we hold that the provisions ofSection 17of the Act are intra vires the Constitution of India and are legally valid. The Original Petitions have no merit and they are accordingly dismissed. No costs.

### Segments Preview:
- **[facts]** (`pre_1`): JUDGMENT     Ar. Lakshmanan, J....
- **[conclusion]** (`p_1, blockquote_1, blockquote_2, blockquote_3`): 1. These two Original Petitions raise the same question with regard to the validity ofSection 17of the Indian Divorce Act, 1986 (hereinafter referred ...
- **[law]** (`p_2, p_3, blockquote_4, blockquote_5`): 2. It is further submitted that a decree for dissolution of marriage among Hindus, Budhists, Sikhs and Jains under theHindu Marriage Act, 1955, among ...
- **[reasoning]** (`blockquote_6`): (c) It is clearly for the Legislature to lay down its policies,State of Bombay v. Narasu Appa Mali, AIR 1952 Bombay 84 : (1952 Cri LJ 354)....
- **[law]** (`blockquote_7, blockquote_8, blockquote_9, blockquote_10, p_4, p_5, blockquote_11, blockquote_12, blockquote_13, blockquote_14, blockquote_15, p_6, p_7, p_8, p_9, blockquote_16, blockquote_17, p_10`): (d)Section 17of the Act embodies a procedure in accordance with the Legislative policy and the said provision of Law has withstood the test of time an...
- **[conclusion]** (`blockquote_18`): "We feel that it is high time that the provision regarding confirmation underSections 17and20of the Indian Divorce Act, 1869 are deleted from the Stat...
- **[law]** (`p_11, p_12, p_13`): Before the Full Bench, the judgment of the Supreme Court reported in,Ahmedabad Women Action Group v. Union of India, 1997 (3) JT (SC) 171 : (AIR 1997 ...
- **[reasoning]** (`blockquote_19`): "It must not be forgotten that in a democracy the Legislature is constituted by the chosen representatives of the people. They are responsible for the...
- **[issue]** (`p_14, blockquote_20, p_15`): Coming to Articles Hand 15(1) of the Constitution, the Bench has emphasized that both the Articles stress the equality before law.Article 14confers th...
- **[law]** (`p_16, p_17`): 10. Mr. Ramakumar then cited a Special Bench decision of the Madras High Court in,T.M. Bashiam v. M. Victor, ALR1970 Mad 12). The above case was a ref...
- **[reasoning]** (`p_18, p_19`): 12. In view of the Supreme Court decision, we are of the opinion that personal laws do not fall withinArticle 13(1)of the Constitution and that they a...
- **[conclusion]** (`blockquote_21`): "79.Section 17of the Indian Divorce Act provides for a decreeifor dissolution passed by a District Judge being confirmed by a Special Bench of the Hig...
- **[law]** (`p_20`): The Law Commission had explained the importance of the proposal and the recommendations relating to the subject. The report also discussed in detail t...
- **[reasoning]** (`p_21, p_22`): 14. We would, therefore, like to observe that the procedure prescribed bySection 17of the Act requiring confirmation by the High Court of a decree for...
- **[conclusion]** (`p_23`): The Original Petitions have no merit and they are accordingly dismissed. No costs....

---

## [9] Case 1208421: Kanku D/O Dhulabhai Dahyabhai vs Khristi Shanabhai Fulabhai on 3 May, 1963

- **URL:** [https://indiankanoon.org/doc/1208421/](https://indiankanoon.org/doc/1208421/)
- **Court & Date:** Gujarat High Court (1963-05-03)
- **Model Ground:** `nullity_sec19` (All detected: ['nullity_sec19'])
- **Model Disposal:** `dismissed`
- **Model Dissolution:** `yes` (Relief: `nullity`)
- **Model Petitioner:** `wife`

### Head Excerpt (First 600 chars):
> JUDGMENT
 

 N.M. Miabhoy, J. 1. A decree has been passed by the learned District Judge, Kaira at Nadiad, in Divorce Suit No. 1 of 1961 on 1st September 1961, by which the learned Judge has declared the marriage between the petitioner Kanku and the respondent Shanabhai null and void, subject to the declaration being confirmed by this Court underSection 20of the Divorce Act, 1869 (hereafter called 'the Act'). The learned District Judge by his letter, dated 1st March 1962, has sent the proceedings in the suit to this Court for confirmation. The petition, which was numbered in the District Court

### Cleaned Tail (Last 800 chars):
> ble and the learned trial Judge had no power to pass a decree under the Act. There is, therefore, no valid decree before us which can be confirmed underSection 20of the Act. In my view therefore the rule issued in this reference should be discharged. MODY, J. 55. I had the advantage of reading the judgments of my learned brothers Miabhoy J. and Bakshi J. With respect, I agree with the view taken by brother Bakshi J. in his judgment for the reasons set out therein. 56. I am also of the opinion that the petition in the reference before us in not sustainable under the provisions ofSections 18and19of the Indian Divorce Act and the rule issued is liable to be discharged. P.C. No orders are passed on these proceedings in accordance with the view of the majority. Each party to bear its own costs.

### Segments Preview:
- **[facts]** (`pre_1`): JUDGMENT     N.M. Miabhoy, J....
- **[conclusion]** (`p_1`): 1. A decree has been passed by the learned District Judge, Kaira at Nadiad, in Divorce Suit No. 1 of 1961 on 1st September 1961, by which the learned ...
- **[reasoning]** (`p_2`): 2. The main question which Mr. Shah raised was one about the jurisdiction of the District Court to grant under the Act the relief for nullity of marri...
- **[law]** (`p_3, p_4`): 3. The question which has got to be decided is whether the District Court has jurisdiction to entertain a petition and grant a decree for a declaratio...
- **[reasoning]** (`p_5`): 5. From the above resume, it is clear that the Act has been conceived and enacted as a comprehensive measure and provides for both substantive and adj...
- **[law]** (`p_6, p_7, blockquote_1, blockquote_2, blockquote_3, p_8, p_9, p_10`): 6.Section 2of the Act prescribes general conditions which require to be satisfied in order to enable the Court to exercise jurisdiction in matters mat...
- **[conclusion]** (`p_11, p_12, p_13, blockquote_4, blockquote_5, p_14`): 11. That, at once, raises the question as to what jurisdiction the High Court itself possessed in respect of nullity of marriage at the date when the ...
- **[law]** (`p_15, blockquote_6, blockquote_7, blockquote_8, blockquote_9, blockquote_10`): 15. The next question for consideration is whether the Act itself confers any express jurisdiction upon the Court to pass decrees for nullity of marri...
- **[issue]** (`blockquote_11, blockquote_12, blockquote_13, p_16`): (2) that the parties are within the prohibited degrees of consanguinity (whether natural or legal) or affinity; (3) that either party was a lunatic or...
- **[law]** (`p_17, p_18, blockquote_14, blockquote_15, blockquote_16, p_19, blockquote_17, p_20, blockquote_18, blockquote_19, p_21, p_22, p_23, blockquote_20, blockquote_21`): 16. None of these two sections contains a specific provision conferring jurisdiction upon the Court to grant a decree for nullity on the ground that t...
- **[conclusion]** (`p_24`): 22. Thereafter, the section mentions four grounds on the basis of which a decree for nullity can be passed. Therefore,Section 8provides in express ter...
- **[law]** (`p_25, p_26, blockquote_22, blockquote_23, blockquote_24, blockquote_25, blockquote_26, p_27, blockquote_27`): 23. Now, the expression "principles and rules" used inSection 7of the Act has not been restricted only to me principles and rules enunciated and appli...
- **[conclusion]** (`p_28, p_29`): 26. In this connection, it is important to notice that if the Court gets jurisdiction to grant a relief for nullity of marriage, on the ground that it...
- **[law]** (`p_30, p_31, p_32, blockquote_28, p_33, blockquote_29`): 28. Mr. Shah, the Learned Counsel for the respondent, argued that whatever jurisdiction the High Court might have exercised on this subject previously...
- **[reasoning]** (`p_34, p_35`): 32. Perhaps, in 1934, when the case was decided, there was no provision in the English law conferring jurisdiction to grant a decree for nullity of ma...
- **[law]** (`blockquote_30, p_36, blockquote_31`): The Learned Counsel urged that at that date it was probable that there existed in that High Court an unrestricted matrimonial jurisdiction and that at...
- **[reasoning]** (`blockquote_32`): as used in clause 27, may be construed as contemplating a larger jurisdiction than that to which at any rate High Courts existing prior to theIndian D...
- **[law]** (`p_37, p_38, p_39, blockquote_33, p_40, p_41`): 35. With great respect, we cannot agree with the observation thatSection 7cannot deal with the question of jurisdiction and that the meaning of the ex...
- **[reasoning]** (`p_42, blockquote_34, p_43, p_44`): 40. Having regard to our aforesaid conclusion, in our judgment, the matter must be remanded to the District Court for affording a chance to the partie...
- **[conclusion]** (`p_45`): 42. This is a reference underSection 20of the Indian Divorce Act, 1869 (hereinafter referred to as the Act) for confirmation of the decree of nullity ...
- **[law]** (`p_46, blockquote_35, p_47, p_48, p_49, p_50, blockquote_36, p_51, blockquote_37, blockquote_38`): 43. This would lead us to an examination of the relevant provisions of the Act. The preamble of the Act mentions two objects for the enactment, namely...
- **[issue]** (`blockquote_39, blockquote_40, p_52`): (2) that the parties are within the prohibited degrees of consangunity (whether natural or legal) or affinity,    (3) that either party was a lunatic ...
- **[conclusion]** (`p_53`): 48.Section 20requires every decree of nullity of marriage to be confirmed by the High Court andSection 21relates to children of an annulled marriage. ...
- **[law]** (`p_54, p_55, p_56, p_57`): 49. If the grounds for nullity of marriage permissible under the English law but not enumerated inSection 19were permitted to be availed of in a petit...
- **[conclusion]** (`blockquote_41`): A decree for dissolution is the relief which a Court grants on certain grounds. The grounds are mentioned inSection 10of the Divorce Act. It may be I ...
- **[law]** (`p_58, blockquote_42, p_59, p_60, p_61, p_62, p_63, p_64`): 52. The observations of Chaga C.J. quoted above show that the question whether it was open to the grounds for dissolution of a marriage by virtue ofSe...
- **[conclusion]** (`p_65`): P.C. No orders are passed on these proceedings in accordance with the view of the majority. Each party to bear its own costs....

---

## [10] Case 527509: Joseph vs Mary on 21 July, 1999

- **URL:** [https://indiankanoon.org/doc/527509/](https://indiankanoon.org/doc/527509/)
- **Court & Date:** Kerala High Court (1999-07-21)
- **Model Ground:** `adultery` (All detected: ['adultery', 'cruelty'])
- **Model Disposal:** `remanded`
- **Model Dissolution:** `no` (Relief: `none`)
- **Model Petitioner:** `husband`

### Head Excerpt (First 600 chars):
> JUDGMENT AR. Lakshmanan, Atg. C.J. 1. Petitioner, who is the husband of the respondent Mary, filed the petition for divorce underSection 10of the Indian Divorce Act on the ground of adultery. According to the petitioner, the marriage between him and the respondent was solemnised on 17.6.1974 in accordance with their customary rites and that he and the respondent were residing together from the date of marriage and in that wedlock five children were born to them. It is stated that since his father was taking treatment in the hospital at Manipal, he stayed in the hospital to help his father and

### Cleaned Tail (Last 800 chars):
> beyond any reasonable doubt as to the commission of any matrimonial offence, which is the clear requirement ofSection 14of the Act. 12. We are of the opinion that in the case on hand the quantity and quality of the evidence on record does not justify the grant of a decree for divorce in favour of the petitioner. This apart, the mandatory requirement underSection 11has also been given a go-bye. We, therefore, decline to confirm the decree granted by the District Judge and remit the matter to the District Court, Thalassery. The District Judge shall re-hear the case after observing the formalities underSection 11of the Act and dispose of the same in accordance with law as expeditiously as possible. The Registry is directed to dispatch the records to the District Court, Thalassery, forthwith.

### Segments Preview:
- **[facts]** (`pre_1, p_1`): JUDGMENT AR. Lakshmanan, Atg. C.J....
- **[law]** (`p_2`): 1. Petitioner, who is the husband of the respondent Mary, filed the petition for divorce underSection 10of the Indian Divorce Act on the ground of adu...
- **[petitioner_argument]** (`p_3`): 2. The respondent filed a counter affidavit denying the allegations as baseless. It is submitted that she does not know any person by name Joseph Kizh...
- **[issue]** (`p_4, blockquote_1, blockquote_2, blockquote_3, blockquote_4`): 3. The Principal District Judge, Thalassery formulated the following points for consideration in the petition : "(1) Whether the respondent committed ...
- **[conclusion]** (`p_5`): The petitioner examined himself as P.W. 1 and his eldest daughter Sheena as P.W. 2. Exts. A1 and A2 were also marked on his side. The respondent exami...
- **[reasoning]** (`p_6, blockquote_5, blockquote_6, blockquote_7`): 4. When the matter came up for hearing before us, the Bench felt that the non-impleadment of the adulterer is vital to the case and is against the man...
- **[law]** (`p_7, p_8, blockquote_8, p_9, blockquote_9, blockquote_10, p_10, p_11, blockquote_11, p_12, p_13, blockquote_12, blockquote_13, blockquote_14, blockquote_15, p_14, p_15, blockquote_16`): 5.Section 12also provides that Courts should be satisfied of absence of collusion. The standard of proof required in divorce cases under the Act is th...
- **[conclusion]** (`p_16, blockquote_17, blockquote_18, blockquote_19, blockquote_20, blockquote_21`): The object ofSection 17of the Act is to guard against any infringement of public policy and public morality. The said section deals with confirmation ...
- **[law]** (`blockquote_22`): During the progress of the suit in the Court of the District Judge, any person suspecting that any parties to the suit are or have been acting in coll...
- **[reasoning]** (`p_17, p_18`): 11. The procedure underSection 17does not call for any application by either party or personal appearance before the High Court. The High Court is als...
- **[conclusion]** (`p_19`): The Registry is directed to dispatch the records to the District Court, Thalassery, forthwith....

---

## [11] Case 71126: Miss Shireen Mall vs John James Taylor on 21 December, 1951

- **URL:** [https://indiankanoon.org/doc/71126/](https://indiankanoon.org/doc/71126/)
- **Court & Date:** Punjab-Haryana High Court (1951-12-21)
- **Model Ground:** `desertion` (All detected: ['desertion', 'adultery'])
- **Model Disposal:** `unclear`
- **Model Dissolution:** `yes` (Relief: `nullity`)
- **Model Petitioner:** `unclear`

### Head Excerpt (First 600 chars):
> ORDER 
 

Soni, J. 1. This is an application by Shireen Mall under the provisions ofSections 18and19of the Indian Divorce Act, 1869, read withSections 3and4of the Indian Matrimonial Causes (War Marriages) Act XL of 1948, praying that this Court may declare the marriage between her and the respondent to be null and void. 2. The facts as deposed to by the petitioner are that she was employed as a Sergeant in the Women's Auxiliary Corps (India) and was stationed at Meerut. In June 1943 she came to know the respondent John James Taylor, then a Lieutenant in the British Army. They fell in love with

### Cleaned Tail (Last 800 chars):
> ere with her as husband and wife. In my opinion there is no doubt that fraud was practised on her. In these circumstances I consider that the petitioner and the respondent went through a ceremony without any intention on the part of the husband to regard it as a real marriage. I hold that the consent of the petitioner was obtained by fraud land that this marriage was a mere pretence and is null and void. I would, therefore, pass a decree declaring this marriage null and void. 14. Notice was sent to the respondent, by regis tered post in England. There is a postal acknow ledgment receipt in the records of this Court. This creates a presumption that the respondent was properly apprised of the proceedings in this Court. He has not cared to defend this petition which has been heard 'ex parte.'

### Segments Preview:
- **[facts]** (`pre_1, p_1`): ORDER     Soni, J. 1. This is an application by Shireen Mall under the provisions ofSections 18and19of the Indian Divorce Act, 1869, read withSections...
- **[petitioner_argument]** (`p_2, blockquote_1, blockquote_2, blockquote_3`): 2. The facts as deposed to by the petitioner are that she was employed as a Sergeant in the Women's Auxiliary Corps (India) and was stationed at Meeru...
- **[law]** (`p_3, p_4, p_5, p_6`): The petitioner's case is that the respondent's oral as well as written representations were such that the respondent appeared to her to be genuine in ...
- **[reasoning]** (`blockquote_4, blockquote_5, p_7, p_8, p_9`): "Surely my last letter made that quite clear, as far as I am concerned we are finished. And I have no desire to see or hear from you again. I do not t...
- **[law]** (`p_10, p_11, p_12, blockquote_6, p_13, p_14, p_15, p_16, p_17, blockquote_7, p_18, p_19`): 7. The present petition has been brought in this Court under the provisions of theIndian Divorce Actread with theIndian Matrimonial Causes (War Marria...
- **[issue]** (`p_20`): 12. I would, however, go further than this in the present case. The petitioner was undoubtedly a minor as understood in theIndian Christian Marriage A...
- **[law]** (`p_21, blockquote_8`): 13. In this case I am prepared to go still further. In my opinion the respondent went through the ceremony of marriage without any intention of gettin...
- **[conclusion]** (`pre_2`): * * * *    (3) a promise made without any intention of performing it; * * *     The respondent lured her into the belief that he was deeply interested...

---

## [12] Case 905650: Kallu Daniel vs G.D. Hemalatha on 31 May, 2005

- **URL:** [https://indiankanoon.org/doc/905650/](https://indiankanoon.org/doc/905650/)
- **Court & Date:** Karnataka High Court (2005-05-31)
- **Model Ground:** `procedural` (All detected: ['procedural'])
- **Model Disposal:** `remanded`
- **Model Dissolution:** `unclear` (Relief: `unclear`)
- **Model Petitioner:** `unclear`

### Head Excerpt (First 600 chars):
> JUDGMENT

 

Anand Byrareddy, J. 1. The present Appeal is filed against the order of the Addl. Civil Judge (Sr. Dn.), Hubli, returning the petition of the appellant, seeking a decree of divorce filed underSection 12of the Indian Divorce Act, 1869, to present it before the proper Court. 2. The respondent has been served, she remains unrepresented. The only question to be considered in this Appeal is; 'Whether the Addl. Civil Judge (Sr. Dn.) Hubli, did not have jurisdiction to entertain the petition seeking divorce under theDivorce Act, 1869?'
 

The reasoning of the Court in returning the petit

### Cleaned Tail (Last 800 chars):
> ion dated 31.11.1978 the High Court has conferred power of a District Court or District Judge on all the officers presiding over the Civil Judge's Courts in the State under the following Acts viz., (1)The Divorce Act, 1869, (2)The Lunacy Act, 1912and; (3)The Special Marriage Act, 1954. This position of law has been stated in a Full Bench decision of this Court in the case ofChandramohan Kumar v. Mrs. Florence Indravathi and Anr., AIR 1982 KAR 242. 4. In the light of the above, this Appeal is allowed. The order returning the petition is set aside. The matter is remitted for fresh consideration. In so far as the application seeking a direction in respect of a certain amount in deposit before the Trial Court, it is open for the appellant to approach the Trial Court for appropriate directions.

### Segments Preview:
- **[facts]** (`pre_1`): JUDGMENT     Anand Byrareddy, J....
- **[law]** (`p_1, p_2, p_3, p_4`): 1. The present Appeal is filed against the order of the Addl. Civil Judge (Sr. Dn.), Hubli, returning the petition of the appellant, seeking a decree ...
- **[conclusion]** (`p_5, p_6`): 4. In the light of the above, this Appeal is allowed. The order returning the petition is set aside. The matter is remitted for fresh consideration. I...

---

## [13] Case 332665: Susan Samuel vs Oommen Mathew on 26 February, 2009

- **URL:** [https://indiankanoon.org/doc/332665/](https://indiankanoon.org/doc/332665/)
- **Court & Date:** Kerala High Court (2009-02-26)
- **Model Ground:** `procedural` (All detected: ['procedural'])
- **Model Disposal:** `dismissed`
- **Model Dissolution:** `unclear` (Relief: `unclear`)
- **Model Petitioner:** `unclear`

### Head Excerpt (First 600 chars):
> IN THE HIGH COURT OF KERALA AT ERNAKULAM

WP(C).No. 1913 of 2009(S)


1. SUSAN SAMUEL, D/O.MR. P.S. SAMUEL,
 ... Petitioner

 Vs



1. OOMMEN MATHEW, S/O.MR. A.M. MATHEW
 ... Respondent

 For Petitioner :SRI.V.V.NANDAGOPAL NAMBIAR

 For Respondent :SRI.S.SUBHASH CHAND

The Hon'ble MR. Justice P.R.RAMAN
The Hon'ble MR. Justice P.S.GOPINATHAN

 Dated :26/02/2009

 O R D E R
 P.R.RAMAN & P.S.GOPINATHAN, JJ.

 -------------------------------

 W.P.(C) No.1913 of 2009

 -------------------------------

 Dated this the 26th February, 2009

 J U D G M E N T Raman, J. Petitioner who is the wife has in

### Cleaned Tail (Last 800 chars):
> tion in the matter. 5. In order to stay the latter proceedings underSection 10of the Divorce Act, the earlier proceedings must be pending before a court having jurisdiction. Necessarily, when an application is made to the latter court, where the subsequent proceedings are filed, it will have to consider whether the earlier proceedings are under the court of competent jurisdiction. Therefore, there is nothing wrong in the order of the Family Court, Thiruvalla, dismissing the application for stay, having found that the Bangalore Court, where the earlier proceedings are initiated by the petitioner herein, has no jurisdiction. In suchW.P.(C) No.1913 of 20095circumstances, we find no merit in the writ petition. Accordingly, the writ petition is dismissed. P.R.RAMAN, JUDGE P.S.GOPINATHAN, JUDGE.

### Segments Preview:
- **[facts]** (`pre_1, p_1`): IN THE HIGH COURT OF KERALA AT ERNAKULAM  WP(C).No. 1913 of 2009(S)   1. SUSAN SAMUEL, D/O.MR. P.S. SAMUEL,  ... Petitioner   Vs    1. OOMMEN MATHEW, ...
- **[law]** (`p_3, p_5, p_6, p_8`): Petitioner who is the wife has initiated proceedings  for getting a decree of divorce under theDivorce Actbefore the  Principal Family Court, Bangalor...
- **[reasoning]** (`p_10, p_12`): 5. In order to stay the latter proceedings underSection 10of the Divorce Act, the earlier proceedings must be  pending before a court having jurisdict...
- **[conclusion]** (`p_13`): nj....

---

## [14] Case 1194173: George Joseph vs Alphonsa Alias Lovely Mathew And Anr. on 15 October, 1998

- **URL:** [https://indiankanoon.org/doc/1194173/](https://indiankanoon.org/doc/1194173/)
- **Court & Date:** Kerala High Court (1998-10-15)
- **Model Ground:** `nullity_sec19` (All detected: ['nullity_sec19', 'unsound_mind', 'adultery', 'cruelty'])
- **Model Disposal:** `dismissed`
- **Model Dissolution:** `yes` (Relief: `dissolution`)
- **Model Petitioner:** `unclear`

### Head Excerpt (First 600 chars):
> JUDGMENT
 

 Usha, J. 1. This appeal is at the instance of a Christian husband whose prayer for a decree of nullity of his marriage with the 1 st respondent has failed. The appellant contended that the 1st respondent was a lunatic at the time of the marriage and therefore he is entitled to a decree for nullity of his marriage underSection 18of the Indian Divorce Act, 1869 read withSection 19. He had also alleged fraud on the part of the respondent in obtaining his consent for the marriage. The petition was dismissed by the learned single Judge holding that the petitioner husband has failed to

### Cleaned Tail (Last 800 chars):
> e. In 1995 (1) KLT 644 this Court had not added a new ground for dissolution of marriage underSection 10. Secondly the evidence in this case does not go to show that the 1st respondent is incurably of unsound mind. 18. There may be cases where one of the spouses becomes incurably unsound in mind which would have been sufficient forgetting a decree for divorce under theHindu Marriage Actor other enactments. But as far as the Christians in Kerala are concerned they are still governed by the provisions of theDivorce Act, 1869. Therefore, even in such cases of incurable mental illness of a spouse after the marriage no decree for dissolution of the marriage could be obtained. This anomaly can be cured only at the instance of the Legislature by bringing in appropriate amendments, to the Statute.

### Segments Preview:
- **[facts]** (`pre_1`): JUDGMENT     Usha, J....
- **[law]** (`p_1`): 1. This appeal is at the instance of a Christian husband whose prayer for a decree of nullity of his marriage with the 1 st respondent has failed. The...
- **[petitioner_argument]** (`p_2, p_3`): 2. The marriage between the petitioner and the 1 st respondent was solemnised on 4-9-1995 at St. Thomas Forane Church, Thomapuram as per the rites and...
- **[law]** (`p_4`): 4. The petitioner would further allege that on enquiry it was understood that besides the 1st respondent, her mother, uncle, brother and younger siste...
- **[respondent_argument]** (`p_5, p_6`): 5. Even though the petitioner has impleaded the 2nd respondent to represent the 1 st respondent as guardian, no order is seen sought or passed for app...
- **[law]** (`p_7`): 7. The learned single Judge on appreciation of the entire evidence in the case came to the conclusion that after marriage the 1st respondent was treat...
- **[petitioner_argument]** (`p_8`): 8. The above finding of the learned Judge is under severe attack by the appellant. It is contended by the learned counsel for the appellant that there...
- **[law]** (`p_9, p_10`): 9. What has to be established to get a decree for nullity underSection 18read withSection 19(3)is that the 1st respondent was a lunatic at the time of...
- **[reasoning]** (`p_11, p_12`): 11. The evidence of the petitioner would in no way prove the allegation that the 2nd respondent was a lunatic at the time of her marriage, on the othe...
- **[issue]** (`p_13, p_14`): 13. We will now consider the medical evidence in this case given by PWs 3 and 4, two doctors. PW 4 Dr. K. Sivaramakrishnan have a Master degree in Psy...
- **[reasoning]** (`p_15, p_16`): 14.1. Now we will come to the evidence of PW 5 on which much reliance was sought to be placed by the learned counsel for the appellant. In chief exami...
- **[law]** (`p_17, p_18`): 16. The learned counsel appearing on behalf of the appellant contended that the appellant is a young person and that after 16 days of marital life he ...
- **[conclusion]** (`p_19`): 18. There may be cases where one of the spouses becomes incurably unsound in mind which would have been sufficient forgetting a decree for divorce und...

---

## [15] Case 442538: Arokia Raj Morais vs Mabia Bibia Rani Morais And Ors. on 24 March, 2006

- **URL:** [https://indiankanoon.org/doc/442538/](https://indiankanoon.org/doc/442538/)
- **Court & Date:** Madras High Court (2006-03-24)
- **Model Ground:** `adultery` (All detected: ['adultery'])
- **Model Disposal:** `dismissed`
- **Model Dissolution:** `unclear` (Relief: `unclear`)
- **Model Petitioner:** `husband`

### Head Excerpt (First 600 chars):
> ORDER
 

M. Thanikachalam, J. 1. This is a suit filed by the husband to dissolve the marriage between himself and the first respondent on the ground of adultery, underSection 10of the Divorce Act, 1869, hereinafter called 'the Act'. 2. The marriage between the petitioner and the first respondent was solemnised on 3.5.1995 in accordance with the Christian Rites and Customs, at St. Andrews Church, Madras-600 112. After the marriage, both were living happily in the matrimonial home. At the time of the marriage, the first respondent was working as a teacher and obtaining permission from the petiti

### Cleaned Tail (Last 800 chars):
> an the second and the third respondents resulting the birth of a male child, then that person also should have been impleaded as a party, as mandated under law, which is not the case in the petition. Therefore, relying upon Ex.P-5, which might have come into existence, under mysterious circumstances, it is not possible to dissolve the marriage between the petitioner and the first respondent. Except these documents, and the uncorroborated oral testimony of P.W. 1, to substantiate the adultery alleged, no other acceptable evidence has been let in, and because of these reasons, the petition should fail. Hence the two issues are answered accordingly. In the result, the petition is dismissed, but under the facts and circumstances of the case, ordering the parties to bear their respective costs.

### Segments Preview:
- **[facts]** (`pre_1`): ORDER    M. Thanikachalam, J....
- **[law]** (`p_1, p_2, p_3, p_4, p_5, p_6, blockquote_1, blockquote_2, blockquote_3, blockquote_4`): 1. This is a suit filed by the husband to dissolve the marriage between himself and the first respondent on the ground of adultery, underSection 10of ...
- **[issue]** (`p_7, blockquote_5, blockquote_6, p_8, p_9, p_10`): 7. On the above pleadings, the following issues were framed on 10.4.2002 for decision: (1) Whether the respondent is guilty of adultery ? (2) Whether ...
- **[law]** (`p_11`): 10. According to the petitioner, the first respondent is living in adultery or she is having immoral activities with the second respondent and that is...
- **[petitioner_argument]** (`p_12`): 11. In this case, by going through the entire petition, I am unable to find any specific instances of adultery said to have been committed by the firs...
- **[law]** (`p_13, p_14, p_15`): 12. In the counter, the first respondent has stated in paragraph-3, which is repeated in paragraph-9 that the second respondent had resigned from the ...
- **[reasoning]** (`p_16`): 15. The sheet anchors of the petitioner's case, to prove the adultery are Exs.P-2 to P5. Ex.P-2 is an anonymous letter, which cannot be the basis to p...
- **[issue]** (`p_17, p_18, p_19`): 16. Law will not presume that a girl, who was compelled to have sexual activities with another man by force or otherwise, should have continued the sa...
- **[respondent_argument]** (`p_20`): 18. The specific case of the petitioner that the first respondent continued her adulterous life with the second respondent must be incorrect, which co...
- **[conclusion]** (`p_21`): In the result, the petition is dismissed, but under the facts and circumstances of the case, ordering the parties to bear their respective costs....

---

## [16] Case 190233259: Mary Latha Regini vs Maria James on 9 January, 2026

- **URL:** [https://indiankanoon.org/doc/190233259/](https://indiankanoon.org/doc/190233259/)
- **Court & Date:** Madras High Court (2026-01-09)
- **Model Ground:** `cruelty` (All detected: ['cruelty', 'desertion'])
- **Model Disposal:** `allowed`
- **Model Dissolution:** `no` (Relief: `none`)
- **Model Petitioner:** `unclear`

### Head Excerpt (First 600 chars):
> C.M.A.(MD)No.606 of 2021


 BEFORE THE MADURAI BENCH OF MADRAS HIGH COURT

 Reserved on : 05.11.2025

 Pronounced on : 09.01.2026

 CORAM:

 THE HONOURABLE MR. JUSTICE P.VELMURUGAN

 and

 THE HONOURABLE MRS.JUSTICE L.VICTORIA GOWRI

 C.M.A.(MD)No.606 of 2021
 and
 CMP(MD)No.5884 of 2021

 Mary Latha Regini ... Appellant / Respondent


 Vs.

 Maria James ... Respondent / Petitioner



 PRAYER: Civil Miscellaneous Appeal filed underSection 19(1)of the
 Family Court Act, 1984, to call for the records pertaining to the fair and
 decreetal order in I.D.O.P.No.86 of 2018 passed by the learned Famil

### Cleaned Tail (Last 800 chars):
> h either party may approach the learned Family Court for appropriate directions. The appellant shall not, in any manner, obstruct or prevent the respondent from making additional voluntary contributions for the welfare, education and future settlement of the children. There shall be no order as to costs in this appeal. Consequently, connected miscellaneous petition is closed. 47. In fine, this Civil Miscellaneous Appeal is allowed. [P.V.,J.] [L.V.G.,J.] 09.01.2026 NCC : Yes / No Index : Yes / No Internet : Yes Sml22/24 C.M.A.(MD)No.606 of 2021To The Family Court, Kannyakumari at Nagercoil Copy to The Section Officer, Vernacular Records, Madurai Bench of Madras High Court, Madurai.23/24 C.M.A.(MD)No.606 of 2021P.VELMURUGAN, J., AND L.VICTORIA GOWRI, J., SmlC.M.A.(MD)No.606 of 2021.202624/24

### Segments Preview:
- **[law]** (`pre_1, p_1, p_3, blockquote_1, blockquote_2, p_5`): C.M.A.(MD)No.606 of 2021    BEFORE THE MADURAI BENCH OF MADRAS HIGH COURT   Reserved on : 05.11.2025   Pronounced on : 09.01.2026   CORAM:   THE HONOU...
- **[issue]** (`p_6, p_7`): 3. The appeal raises, in essence, the recurring question as to   when a spouse’s protest, suspicion and complaint regarding the   conduct and associat...
- **[law]** (`p_8, p_9`): 4. The respondent-husband laid I.D.O.P. No.86 of 2018 underSection 10(ix)(x)of the Indian Divorce Act, 1869, seeking dissolution of   his marriage wit...
- **[petitioner_argument]** (`p_10, p_11, p_12, p_14, p_16, p_17, p_18, p_20, p_21, p_22, p_23`): 5. According to the husband, though the marriage subsisted in   form, the appellant-wife never showed compassion, understanding, true   love or affect...
- **[issue]** (`p_25, p_27, p_28, p_30, p_31, blockquote_3, p_32, p_34, p_36, blockquote_5`): 13. Before the learned Family Court, the husband examined   himself as P.W.1 and produced Exs.P1 to P5. The wife examined herself   as R.W.1 and produ...
- **[law]** (`p_38`): wife within the meaning ofSection 10(ix)(x)of the Indian Divorce Act,   1869?...
- **[issue]** (`p_40, p_41, p_42, p_44`): (ii) Whether the decree of divorce granted by the learned Family   Court is sustainable in law on the evidence on record? (iii) What order is required...
- **[law]** (`p_46`): 19. The learned Family Court has extracted and relied on the   principles laid down by the Hon’ble Supreme Court inShobha Rani v.   Madhukar Reddi1,V....
- **[issue]** (`p_48`): 20. There can be no quarrel with the propositions emerging   therefrom, namely, cruelty may be physical or mental, intentional or   unintentional. Men...
- **[law]** (`p_49, p_51, p_52, p_53`): 21. The pivot of the learned Family Court’s finding on cruelty is   that the wife allegedly levelled baseless imputations of   immoral/unnatural condu...
- **[petitioner_argument]** (`p_54`): 25. The law on cruelty does not intend to punish a spouse merely   for reacting to unusual or unexplained conduct of the other spouse.   When one spou...
- **[issue]** (`p_55`): 26. The learned Family Court has, in paragraphs 20 and 21 of its   judgment, itself recorded that the parties had trivial disputes and   misunderstand...
- **[law]** (`p_57, p_58, p_59, p_60, p_61, p_63, p_65, p_67, p_68, p_69, p_71, p_73, p_75, p_77, p_78`): 27. Further, the learned Family Court has not adverted to the   settled principle that to constitute cruelty, the conduct must be “grave   and weighty...
- **[conclusion]** (`p_80, p_81`): 42. In the result, the Civil Miscellaneous Appeal is allowed. 43. The judgment and decree dated 27.03.2019 passed in I.D.O.P.   No.86 of 2018 on the f...
- **[law]** (`p_82, p_84, p_86`): 44. Consequently, I.D.O.P. No.86 of 2018 filed by the respondent-   husband underSection 10(ix)(x)of the Indian Divorce Act, 1869, shall   stand dismi...
- **[conclusion]** (`p_88, pre_2, p_89`): 47. In fine, this Civil Miscellaneous Appeal is allowed. [P.V.,J.] [L.V.G.,J.]   09.01.2026    NCC : Yes / No  Index : Yes / No  Internet : Yes  Sml22...

---

## [17] Case 105078: Christinamary Stella vs Vijay Siddharaj And Anr. on 7 September, 1978

- **URL:** [https://indiankanoon.org/doc/105078/](https://indiankanoon.org/doc/105078/)
- **Court & Date:** Madras High Court (1978-09-07)
- **Model Ground:** `procedural` (All detected: ['procedural'])
- **Model Disposal:** `dismissed`
- **Model Dissolution:** `unclear` (Relief: `unclear`)
- **Model Petitioner:** `unclear`

### Head Excerpt (First 600 chars):
> JUDGMENT
 

 Ramaprasada Rao, C.J. 1. This case comes up before us for confirmation of the order passed by the District Judge, Pudukottai, who allowed the petition filed by the first wife and dissolved the marriage as between the petitioner and the first respondent on the ground that the first respondent contracted a second marriage with the second respondent after the solemnisation of the first marriage and that the first respondent deserted the petitioner and is permanently living with the second respondent and had a child through her also. The facts, as disclosed in the petition, are that t

### Cleaned Tail (Last 800 chars):
> n 47shall not be the sole criteria for the dismissal of a petition by a wife who is faced with a circumstance where her husband has openly violated the matrimonial bondage and taken a second wife and has deserted her since 1974. We are satisfied that the petitioner is entitled to a decree for dissolution of marriage underSection 10, she having proved substantially all the relevant facts which are necessary to enable her to obtain an order of dissolution of marriage. In these circumstances, the order of the court below is confirmed. 6. We place on record our appreciation of the assistance rendered by Mrs. Hemsala Rajendran as amicus curiae for the first respondent, who brought to out notice certain lacuna appearing on record, which had to be rectified only in this court. 7. Order confirmed.

### Segments Preview:
- **[facts]** (`pre_1`): JUDGMENT     Ramaprasada Rao, C.J....
- **[reasoning]** (`p_1, p_2, p_3, p_4, p_5, p_6`): 1. This case comes up before us for confirmation of the order passed by the District Judge, Pudukottai, who allowed the petition filed by the first wi...
- **[conclusion]** (`p_7`): 7. Order confirmed....

---

## [18] Case 103985033: Johnsi Amalarani vs S.Arul Prakash on 19 July, 2016

- **URL:** [https://indiankanoon.org/doc/103985033/](https://indiankanoon.org/doc/103985033/)
- **Court & Date:** Madras High Court (2016-07-19)
- **Model Ground:** `unclear` (All detected: ['unclear'])
- **Model Disposal:** `allowed`
- **Model Dissolution:** `unclear` (Relief: `unclear`)
- **Model Petitioner:** `unclear`

### Head Excerpt (First 600 chars):
> BEFORE THE MADURAI BENCH OF MADRAS HIGH COURT 

DATED : 19.07.2016 

CORAM 
THE HONOURABLE MR.JUSTICE K.KALYANASUNDARAM 

TR.C.M.P.(MD).No.333 of 2016 
and 
C.M.P.(MD)No.6334 of 2016 


Johnsi Amalarani ... Petitioner/Respondent

 Vs.

S.Arul Prakash ... Respondent/Petitioner


PRAYER : Transfer Civil Miscellaneous Petition is filed under Section 24
of Civil Procedure Code, to withdraw and transfer the I.D.O.P.No.25 of 2016
from the file of the learned District and Sessions Judge, Tiruchirappalli and
transfer the same to the District and Sessions Court, Sivagangai be tried
along with I.D.O.P.N

### Cleaned Tail (Last 800 chars):
> essions Judge, Thiruchirappalli and transferred to the file of the District and Sessions Court, Sivagangai for joint trial along with I.D.O.P.No.23 of 2015. 8. The learned District and Sessions Judge, Thiruchirappalli is directed to transmit the entire records to the file of the learned District and Sessions Judge, Sivagangai for joint trial along with I.D.O.P.No.23 of 2015, within a period of two weeks from the date of receipt of a copy of this order and the learned District and Sessions Judge, Sivagangai, after obtaining the records on transfer, is directed to dispose the matter as expeditiously as possible. No order as to costs. Consequently, connected Miscellaneous Petition is closed. 1. The District and Sessions Court, Tiruchirappalli. 2. The District and Sessions Court, Sivagangai. .

### Segments Preview:
- **[law]** (`pre_1, p_1`): BEFORE THE MADURAI BENCH OF MADRAS HIGH COURT   DATED : 19.07.2016   CORAM  THE HONOURABLE MR.JUSTICE K.KALYANASUNDARAM   TR.C.M.P.(MD).No.333 of 2016...
- **[petitioner_argument]** (`p_2`): 2. Mr.P.Mahendran, learned counsel for the petitioner would submit that the petitioner is the wife of the respondent and she is a permanent resident o...
- **[law]** (`p_3`): 3. It is further submitted that earlier, the respondent filed I.D.O.P.No.103 of 2013 before the III Additional District and Sessions Court, Thiruchira...
- **[petitioner_argument]** (`p_4, p_5, p_6, p_7, p_8, p_9, p_10`): 4. The learned counsel for the petitioner would further submit that the petitioner has been blessed with twins and both of them are in the custody of ...
- **[conclusion]** (`p_11`): 2. The District and Sessions Court, Sivagangai. ....

---

## [19] Case 1401518: Mrs. Pragati Varghese And Etc. vs Cyril George Varghese And Etc. on 6 May, 1997

- **URL:** [https://indiankanoon.org/doc/1401518/](https://indiankanoon.org/doc/1401518/)
- **Court & Date:** Bombay High Court (1997-05-06)
- **Model Ground:** `adultery` (All detected: ['adultery', 'constitutional_validity', 'desertion', 'cruelty', 'wife_specific'])
- **Model Disposal:** `dismissed`
- **Model Dissolution:** `yes` (Relief: `dissolution`)
- **Model Petitioner:** `wife`

### Head Excerpt (First 600 chars):
> ORDER
 

 Agarwal, J. 1. Present suits arc filed by Christian wives for dissolution of their marriages underSection 10of the Indian Divorce Act, 1869 (hereinafter referred as 'the Act'). Each of them impugn the vires of the provisions ofSection 10of the Act which provides for the grounds on which a husband and wife can sue for dissolution of marriage. It is contended that the provisions are archaic and adversely discriminate wives as against husbands merely on ground of sex and are, therefore, violative ofarticle 15of the Constitution. It is further contended that the

aforesaid provisions adv

### Cleaned Tail (Last 800 chars):
> own the provisions ofSection 10of the Act. The said matter was not carried to the Supreme Court. Even in the present suits, even though notices were served upon the learned Attorney General, no affidavit-in-reply has been filed in any of the mailers. Mr. Shah, at the commencement of the arguments, had frankly staled that, despite several letters and reminders, he has received no instructions whatsoever in the matter. In the circumstances, we find that no useful purpose will be served in granting stay. In any event. Union of India will have sufficient time at its disposal to impugn our order, if so advised, as all that has been done in the instant case is to remit the present suits for trial to the learned single Judge. Prayer, in this behalf, is accordingly rejected. 59. Order accordingly.

### Segments Preview:
- **[facts]** (`pre_1`): ORDER     Agarwal, J....
- **[law]** (`p_1, p_2, p_3, p_4, blockquote_1, blockquote_2, blockquote_3, blockquote_4, p_5, p_6, p_7, p_8, p_9, p_10, p_11, p_12, p_13, p_14, p_15, p_16, p_17, blockquote_5, p_18, blockquote_6`): 1. Present suits arc filed by Christian wives for dissolution of their marriages underSection 10of the Indian Divorce Act, 1869 (hereinafter referred ...
- **[reasoning]** (`blockquote_7`): (Provided that nothing in this section shall deprive the said Courts of jurisdiction in a case where the parties to a marriage professed the Christian...
- **[law]** (`p_19, blockquote_8`): 16.Section 7of 'the Act' has come up for consideration in various decisions. The principle of incorporating the developments under English Matrimonial...
- **[issue]** (`p_20`): 17. After independence, in 1955, the issue whether the statute of sovereign Republic could be made subordinate to the laws of a foreign power, was exa...
- **[law]** (`blockquote_9, p_21, blockquote_10, p_22, p_23, p_24, p_25, p_26, blockquote_11, p_27, blockquote_12, p_28, p_29`): "SinceSection 7of IDA has been preserved by Adaptation of Laws Order, 1950, English law and practice could be applied to and should be applied. Courts...
- **[issue]** (`p_30, p_31, p_32`): 11. .. ... Time has also come for a reappraisal and reconsideration of the other anachronistic incongruities fundamental and discriminatory in nature ...
- **[law]** (`p_33, p_34`): 24.In the case of, "Ramish Francis Toppo v. Violet Francis Toppo", (SB), the Court again expressed its opinion that-- "desertion of one spouse by the ...
- **[reasoning]** (`p_35, p_36`): 26.In the case ofShri Srinivasa Theatre v. Government of Tamil Nadu," , the Supreme Court observed that,Article 14of the Constitution enjoins upon the...
- **[law]** (`blockquote_13, p_37, blockquote_14, blockquote_15, blockquote_16, blockquote_17, blockquote_18, blockquote_19, p_38, p_39`): "As the aforesaid provision (Section 125Code of Criminal Procedure) granted maintenance to all women irrespective of castes, including woman belonging...
- **[reasoning]** (`p_40, p_41, p_42, blockquote_20, blockquote_21, p_43, blockquote_22, blockquote_23, p_44, blockquote_24`): 31. Denial of right of divorce, in our view, also constitutes violation of right to life underArticle 21of the Constitution. In recent years, various ...
- **[law]** (`p_45, p_46, p_47, blockquote_25, p_48, blockquote_26, blockquote_27, blockquote_28, p_49, blockquote_29, blockquote_30, blockquote_31`): 35. Let us now examine the impugned provisions ofSection 10of the Indian Divorce Act in the light of the observations contained in the various Judgmen...
- **[reasoning]** (`blockquote_32, p_50, p_51, blockquote_33, blockquote_34, blockquote_35, blockquote_36, blockquote_37, p_52, blockquote_38, p_53, blockquote_39, p_54, p_55, blockquote_40, p_56, p_57, p_58, blockquote_41, p_59`): "The reason why we attach the highest importance to amendingSection 10as above may be stated. We regard such an amendment as a constitutional imperati...
- **[conclusion]** (`p_60`): 24. Learned counsel for the Central Government has however tried to support the constitutionality of the provision relying strongly upon the reasoning...
- **[law]** (`p_61, p_62, p_63, p_64, p_65, p_66, p_67`): Union of India AIR 1979 SC 1868 and other cases. 25. The more important challenge levelled againstS. 10of the Act was that it is violative of the fund...
- **[petitioner_argument]** (`p_68`): 41. In the light of our findings that the impugned provisions are violative of the provisions in Arts. 14, 15 and 21 of the Constitution of India, nor...
- **[law]** (`p_69, blockquote_42, blockquote_43, blockquote_44, blockquote_45, blockquote_46, p_70`): 42. Elucidating the point further, the learned counsel has submitted that the words and phrases 'incestuous' and 'adultery coupled with' used in the i...
- **[reasoning]** (`p_71, p_72`): 43.Section 10being the only provision allowing dissolution of marriage among Christians governed by the Act, striking down of the provisions as a whol...
- **[law]** (`p_73`): 45. Applying the tests indicated inR.M.D.C.'s case, , if we are now, to ask ourselves the question as Venkataramd Iyyer, J. has donein that case, woul...
- **[reasoning]** (`p_74`): 46. For all the above reasons we would hold that the offending portions of the provisions as already indicated are severable and they are liable to be...
- **[law]** (`p_75, blockquote_47, blockquote_48, blockquote_49, blockquote_50, blockquote_51, p_76, blockquote_52`): "47. We would accordingly severe and quash the words "incestuous" and "adultery coupled with" from the provisions inSection 10of the Act and would dec...
- **[issue]** (`blockquote_53, p_77, p_78, blockquote_54`): (a) that the husband has exchanged his profession of Christianity for the profession of some other religion and gone through a form of marriage with a...
- **[law]** (`p_79, blockquote_55, blockquote_56, blockquote_57, p_80, p_81, p_82, p_83, blockquote_58, blockquote_59, blockquote_60, blockquote_61, p_84, blockquote_62, p_85, p_86, blockquote_63, p_87`): Shorter Oxford English Dictionary defines the word 'sodomy' to mean "An unnatural form of sexual intercourse, esp. that of one male with another."Sect...
- **[issue]** (`blockquote_64, p_88, blockquote_65, p_89`): "(30) But it is argued that even as to this social reform, the Stale Legislature should have made it all pervasive and should not have left the Mahome...
- **[petitioner_argument]** (`blockquote_66`): "10. Learned Counsel for the appellants then points out that a Christian marriage can be registered under theSpecial Marriage Act. 1954 and that there...
- **[law]** (`p_90, p_91, blockquote_67, p_92, blockquote_68, p_93, blockquote_69, p_94, blockquote_70`): Placing reliance on the above observations. Mr. Shah has contended that provisions to be found inSection 10of 'the Act' are a result of a legislation ...
- **[reasoning]** (`p_95`): 49. We have considered the aforesaid submissions advanced by Mr. Shah, in the light of the decisions relied upon by him and we find that what we are d...
- **[law]** (`p_96, p_97, p_98`): 50. The Supreme Court in the case of Anil Kumar Mahsi. (supra), was concerned with an altogether different and distinct challenge toSection 10of the A...
- **[reasoning]** (`p_99, blockquote_71`): 53. As far as the provisions ofSections 17and20are concerned, they provide for confirmation by High Court of decrees for dissolution of marriages and ...
- **[law]** (`p_100, p_101, p_102, p_103`): In the case ofSwapna Ghosh v. Sadananda Ghosh, (SB), it has been observed' - under theSpecial Marriage Act.providing the general matrimonial law of th...
- **[conclusion]** (`p_104, p_105`): 56. In the result, we hold that the indicaled portions ofSection 10of the Act are ultra viresArticles 14, 15and21of the Constitution and the same are ...
- **[reasoning]** (`p_106`): 58. At this stage, the counsel appearing for the Union of India, applies for slay of this order in order to enable the Union of India to carry the  ma...
- **[conclusion]** (`p_107`): 59. Order accordingly....

---

## [20] Case 14646681: S.Rinu vs Nil on 18 June, 2026

- **URL:** [https://indiankanoon.org/doc/14646681/](https://indiankanoon.org/doc/14646681/)
- **Court & Date:** Madras High Court (2026-06-18)
- **Model Ground:** `unclear` (All detected: ['unclear'])
- **Model Disposal:** `allowed`
- **Model Dissolution:** `unclear` (Relief: `unclear`)
- **Model Petitioner:** `unclear`

### Head Excerpt (First 600 chars):
> CMA No. 1213 of 2026


 IN THE HIGH COURT OF JUDICATURE AT MADRAS
 DATED: 18-06-2026
 CORAM
 THE HON'BLE MR JUSTICE C.V. KARTHIKEYAN
 AND
 THE HON'BLE MR.JUSTICE K.RAJASEKAR
 CMA No. 1213 of 2026
 1. S.Rinu
 D/o Suresh Kumar,
 No 4/2, 3rd Street,
 Narayanasami Thottam,
 Kodungaiyur, Chennai 600 118.

 2. R.Shyam Solomon
 S/o Raja David,
 P.No 3A, ZLMJ Avenue,
 Sivashakthi Nagar Extn,
 Kurinji Street,
 New Perungalathur, Srinivasanagar,
 Kancheepuram, Chennai 600 063

 ..Appellant(s)
 Vs
 Nil
 Nil
 ..Respondent(s)

 PRAYER :Appeal filed underSection 19(1)of the Family Court Act, to set
 aside t

### Cleaned Tail (Last 800 chars):
> note that, as on date, the mandatory period of two years has expired from the date of separation. The appellants have taken a conscious decision to dissolve their marriage. We are also satisfied that there is no possibility for re-union and every attempt of reunion has failed. The parties are firm that they will not rejoin in the marital life. Hence, we would allow this Appeal and direct dissolution of marriage solemnised between the appellants on 12.06.2024 at CSI Christ Church, Kodungaiyur, Chennai. Page3 of 4 No. 1213 of 2026C.V.KARTHIKEYAN, J. AND K.RAJASEKAR, J. 6. Accordingly, this Civil Miscellaneous Appeal stands allowed. No costs. 18-06-2026 Index: Yes/No Speaking/Non-speaking order Neutral Citation: Yes/No GSK To V Additional Family Court, Chennai. CMA No. 1213 of 2026 Page4 of 4

### Segments Preview:
- **[law]** (`pre_1, p_1, p_2, p_3, p_4, blockquote_1, blockquote_2, blockquote_3, blockquote_4`): CMA No. 1213 of 2026    IN THE HIGH COURT OF JUDICATURE AT MADRAS  DATED: 18-06-2026  CORAM  THE HON'BLE MR JUSTICE C.V. KARTHIKEYAN  AND  THE HON'BLE...
- **[petitioner_argument]** (`p_5, p_6, p_7, p_8, p_9, p_10, p_12, p_13`): 4. The learned counsel for the appellants also affirmed the said fact. 5. Even otherwise, we note that, as on date, the mandatory period of two   year...
- **[conclusion]** (`p_14`): __________  Page4 of 4 https://www.mhc.tn.gov.in/judis...

---

