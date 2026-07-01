# -*- coding: utf-8 -*-
"""v4: second-round reviewer fixes. DIGPAY primary; drop H2(tax)/H3(cash) & Table 7;
no causal claim; prominent pre-trends; remove complementarity & ECA overclaims; CA subsample;
simplify DAG; polish. Operates on v3 -> v4."""
from docx import Document
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph

doc = Document("Manuscript_Revised_GBR_v3.docx")
def find(sub):
    for p in doc.paragraphs:
        if sub in p.text: return p
    raise ValueError("not found: "+sub[:45])
def st(sub,new):
    p=find(sub); rs=p.runs
    if rs:
        rs[0].text=new
        for r in rs[1:]: r.text=""
    else: p.add_run(new)
    return p
def clear(sub):
    p=find(sub)
    for r in p.runs: r.text=""
    return p
def after(p,text):
    e=OxmlElement("w:p"); p._p.addnext(e); q=Paragraph(e,p._parent); q.add_run(text); return q
def setc(t,r,c,v): t.cell(r,c).text=v

DASH="\u2013"; TIMES="\u00d7"

# ============ TABLE 5 -> DIGPAY primary ============
t5=doc.tables[4]
setc(t5,2,0,"DIGPAY")
for (r,c),v in {(2,1):"+0.063\n(0.042)",(2,2):"-0.051**\n(0.023)",(2,3):"+0.040\n(0.028)",(2,4):"+0.013\n(0.032)",
                (3,2):"+12.285***\n(3.967)",(3,4):"+1.765\n(5.813)",
                (4,2):"-0.028\n(0.019)",(4,4):"+0.030\n(0.023)",
                (5,2):"-0.103**\n(0.042)",(5,4):"-0.071\n(0.095)",
                (6,2):"-0.014\n(0.018)",(6,4):"-0.024\n(0.043)",
                (7,2):"+0.195\n(1.789)",(7,4):"-6.492*\n(3.783)",
                (11,1):"0.11",(11,2):"0.59",(11,3):"0.02",(11,4):"0.20"}.items():
    setc(t5,r,c,v)

# ============ HIGHLIGHTS ============
st("Across eight post-Soviet transition economies (2004",
 f"Across eight post-Soviet transition economies (2011{DASH}2020), deeper digital-payment usage\u2014our "
 "primary measure of DFS penetration\u2014is associated with a smaller shadow economy in two-way "
 "fixed-effects models, conditional on income.")
st("The association with tax revenue is positive but statistically insignificant, and we find no significant DFS",
 "The association with tax revenue is statistically insignificant, and the DFS \u00d7 institutions "
 "interaction is insignificant, so we advance neither a tax-base nor an institutional-complementarity claim.")
st("A cash-intensity (currency/broad-money) series was not available for the sample",
 f"The negative shadow-economy association is concentrated in the earlier part of the sample "
 f"(2011{DASH}2015) and is not detectable in 2016{DASH}2020.")
st("The negative shadow-economy association is stable under Driscoll",
 f"The association is stable in fixed-effects and Driscoll{DASH}Kraay models but is statistically "
 "insignificant under instrumental-variable and system-GMM estimation; we therefore interpret it as a "
 "robust conditional association without causal content.")

# ============ ABSTRACT ============
st("For statistical power we assemble an annual panel of eight post-Soviet",
 f"Central Asia's economies carry some of the largest informal sectors among transition regions, "
 f"constraining public revenue even as digital financial services (DFS){DASH}mobile money, cards, and "
 f"instant payments{DASH}rapidly diffuse. Drawing on institutional theory and the economics of tax "
 f"evasion, we ask whether DFS diffusion is associated with a smaller shadow economy. For statistical "
 f"power we assemble an annual panel of eight post-Soviet transition economies (2011{DASH}2020; N = 80), "
 f"within which the Central Asian republics are the focal region and are examined as a subsample. The "
 f"shadow economy is measured with dynamic general-equilibrium (DGE) estimates, and DFS penetration "
 f"primarily by the directly observed Global Findex indicator of digital-payment usage (DIGPAY), with a "
 f"principal-component composite retained only as a robustness check. In two-way fixed-effects models, "
 f"deeper digital-payment usage is significantly associated with a smaller shadow economy once income is "
 f"controlled (a one-standard-deviation rise corresponds to about {chr(0x2212)}0.14 SD of informality). "
 f"However, this association is concentrated in the earlier part of the sample (2011{DASH}2015) and "
 f"disappears in later years, is insignificant under instrumental-variable and system-GMM estimation, "
 f"and does not extend to tax revenue; the DFS {TIMES} institutions interaction is also insignificant. "
 f"We therefore interpret the evidence as a conditional association that is robust in fixed-effects "
 f"specifications but does not withstand estimators that more directly address endogeneity, and we "
 f"advance no causal claim. We apply{DASH}rather than claim to extend{DASH}institutional-voids logic to "
 f"the digital-finance context, and draw implications for tax administrations and financial-sector "
 f"strategy cautiously.")

# ============ HYPOTHESES: drop H2 & H3, relabel H4 -> H2 ============
st("The preceding discussion yields four testable hypotheses",
 "The preceding discussion yields the following testable hypotheses:")
clear("H2: Higher DFS penetration is associated with higher tax revenue")
clear("H3: The reduction of cash intensity is a channel")
st("H4: The formalization effect of DFS is stronger where regulatory quality",
 f"H2: The formalization association of DFS is stronger where regulatory quality and the rule of law "
 f"are stronger (institutional complementarity).")

# ============ 5.2 construct validity (#1) ============
st("Because DFS_INDEX is derived from principal-component analysis rather than observed directly",
 "Because the composite index is constrained by data availability (only three indicators, "
 "KMO = 0.519), our primary specification uses the directly observed Global Findex indicator DIGPAY "
 "(percentage of adults using digital payments). This measure captures the behavioural dimension of "
 "DFS most closely tied to transaction traceability, and avoids the construct-validity limitations of "
 "the composite. The composite DFS_INDEX is retained as a robustness check (Table 6), where it yields "
 "results of the same sign and significance. Table 4 reports the PCA diagnostics for the composite.")

# ============ 5.3 baseline with DIGPAY + elasticity (#1,#12) ============
st("Table 5 presents the two-way fixed-effects estimates. The DFS",
 f"Table 5 presents the two-way fixed-effects estimates with DIGPAY as the primary regressor. The "
 f"association depends on conditioning: with no controls the within-country DIGPAY coefficient is small "
 f"and insignificant (column 1, +0.063), but once log GDP per capita and the remaining controls are "
 f"included it turns negative and significant (column 2, {chr(0x2212)}0.051, p < .05). Because "
 f"digital-payment usage and income are correlated, the association is identified holding development "
 f"constant rather than unconditionally. A one-standard-deviation rise in DIGPAY corresponds to about "
 f"{chr(0x2212)}0.14 standard deviations of the shadow economy. At the sample mean, the implied "
 f"elasticity is {chr(0x2212)}0.04: a 1% increase in digital-payment usage is associated with roughly a "
 f"0.04% decrease in the shadow economy. This modest elasticity underscores that, while the association "
 f"is statistically significant, its economic magnitude is small. For tax revenue (columns 3{DASH}4) the "
 f"DIGPAY coefficient is positive but insignificant in every specification; the tax hypothesis is "
 f"therefore rejected. Estimates using the composite DFS_INDEX are of the same sign and significance "
 f"(Table 6).")

# ============ 5.5 mechanisms: drop mediation/Table 7; H4->H2; no complementarity (#5,#6) ============
st("Two mechanism questions\u2014the cash channel (H3) and institutional complementarity (H4)",
 f"We originally hypothesised that reduced cash intensity mediates the DFS{DASH}informality association. "
 f"However, a consistent currency-to-broad-money series was unavailable for this sample, so we do not "
 f"test the mediation channel; it remains an important avenue for future research when data become "
 f"available. For institutional complementarity (H2), the interaction DIGPAY {TIMES} INST is negative "
 f"for the shadow economy but statistically insignificant, and a squared interaction term is also "
 f"insignificant, as is the interaction in the tax equation. We therefore find no evidence that stronger "
 f"institutions amplify the association and advance no complementarity claim; Figure 2 confirms that the "
 f"marginal effect of DFS is not distinguishable from zero over most of the observed institutional range.")

# ============ 4.4 remove ECA (#8) ============
st("DFS penetration is potentially endogenous: reverse causality is possible",
 f"DFS penetration is potentially endogenous: reverse causality is possible if a shrinking informal "
 f"sector encourages digital adoption, and omitted variables may influence both DFS and the outcomes. "
 f"We address this in three ways. First, all regressors enter with a one-year lag to mitigate "
 f"simultaneity. Second, we estimate two-step system GMM (Blundell & Bond, 1998) with "
 f"Windmeijer-corrected standard errors; because the panel has only eight cross-sectional units, the "
 f"number of credible moment conditions is severely limited, so the system-GMM specification is reported "
 f"only as an exploratory cross-check rather than a primary identification strategy, with instrument "
 f"validity assessed by the Hansen and Arellano{DASH}Bond AR(2) tests. Third, as external instruments we "
 f"use the rollout of mobile-network (3G/4G) coverage and fixed-broadband penetration, which plausibly "
 f"drive DFS adoption, and report two-stage least-squares estimates with first-stage diagnostics. "
 f"Robustness checks include the single DIGPAY indicator and the composite DFS_INDEX, the exclusion of "
 f"Kazakhstan, and the Central Asian subsample.")

# ============ intro remove ECA (#8) ============
st("This article addresses that gap. It assembles an annual panel for the five Central Asian republics",
 f"This article addresses that gap. It assembles an annual panel of eight post-Soviet transition "
 f"economies over 2011{DASH}2020\u2014the three Central Asian republics with model-based shadow-economy "
 f"estimates (Kazakhstan, the Kyrgyz Republic, Tajikistan) together with five comparable transition "
 f"economies (Armenia, Azerbaijan, Georgia, Belarus, Moldova)\u2014and measures DFS penetration primarily "
 f"by digital-payment usage, with a principal-component composite as a robustness check. It relates this "
 f"to the estimated size of the shadow economy and to tax revenue using two-way fixed-effects, "
 f"Driscoll{DASH}Kraay, instrumental-variable, and (exploratory) dynamic system-GMM estimators, with the "
 f"Central Asian republics examined as a focused subsample.")

# ============ limitations remove ECA (#8) ============
st("Several limitations qualify these conclusions and point to future work.",
 f"Several limitations qualify these conclusions and point to future work. The modest cross-sectional "
 f"dimension (eight economies) limits statistical power and, as discussed in Section 4.4, makes the "
 f"system-GMM results illustrative rather than definitive; the addition of subnational or firm-level "
 f"data, or longer panels, would materially strengthen inference. Shadow-economy figures are themselves "
 f"model-based estimates subject to measurement error, and DGE estimates are unavailable for Uzbekistan "
 f"and Turkmenistan. While our identification strategy addresses the leading endogeneity concerns, "
 f"definitive causal claims would benefit from policy experiments or the staggered rollout of "
 f"instant-payment systems as natural experiments. Future research could exploit administrative tax and "
 f"payment micro-data, examine distributional consequences, test the institutional-voids mechanism "
 f"directly with firm-level survey data (Polese et al., 2023), and assess whether the early-period "
 f"association is replicated in longer panels.")

# ============ 8.1 policy (#4 no tax, #6 no complementarity) ============
st("Several implications follow for policymakers in Central Asia and comparable transition economies.",
 f"Our results do not support the hypothesis that stronger institutions amplify the DFS{DASH}"
 f"formalization association, and we find no evidence that DFS raises tax revenue. Consequently, "
 f"policymakers should not assume that investments in DFS will automatically yield larger returns where "
 f"institutions are better, or that they will mechanically broaden the tax base. The primary "
 f"implications are narrower: (i) interoperability and merchant digitization are prerequisites for "
 f"transaction traceability; (ii) consumer protection, data privacy, and reliable connectivity build "
 f"the trust that sustains digital adoption; and (iii) remittance digitalization in migrant-sending "
 f"economies offers a promising route to increase the financial visibility of previously cash-based "
 f"flows. Because we do not find a tax-revenue effect, DFS is best treated as a source of information "
 f"that tax administrations must independently pair with enforcement capacity to convert visibility "
 f"into compliance.")

# ============ 8.2 managerial (#6) ============
st("The findings also carry direct implications for the managers of banks",
 f"The findings also carry implications for banks, fintech firms, and payment-network operators. "
 f"Although we find no evidence of institutional complementarity, firms should still calibrate market "
 f"entry to local institutional conditions\u2014not because institutions amplify the DFS effect, but "
 f"because thin institutions affect overall business risk and payment-system reliability independently "
 f"of DFS penetration. As DFS adoption reduces cash intensity, previously invisible microenterprises and "
 f"households become more identifiable, which can expand the addressable market for formal financial "
 f"services over time, and interoperable, open payment standards enlarge that market rather than "
 f"fragmenting it. The remittance-digitization opportunity in the migrant-sending economies is a "
 f"concrete product-strategy implication, converting informal transfers into recorded flows that can "
 f"support household credit histories.")

# ============ Table 6 note: no causal claim (#3) ============
st("Note. Each cell reports the DFS coefficient",
 f"Note. Each cell reports the DFS coefficient from a separate regression with the full control set and "
 f"country and year effects, unless otherwise noted. *p < .10, **p < .05, ***p < .01. Because the IV and "
 f"system-GMM estimates are statistically insignificant, the fixed-effects results should be read as "
 f"descriptive associations, not causal effects; the paper does not claim that DFS causes formalization.")

# ============ Discussion: prominent pre-trends + CA subsample (#2,#9) ============
disc=find("The evidence assembled here is consistent with digital financial services acting as a form")
p1=after(disc,
 f"A notable caveat is the temporal instability of the association. The negative DFS{DASH}shadow "
 f"coefficient is present only in the 2011{DASH}2015 window and vanishes in 2016{DASH}2020. This "
 f"suggests the effect may be period-specific\u2014possibly reflecting early-stage digitalization, when "
 f"the marginal informal-to-formal transition was largest, or confounding shocks such as commodity-price "
 f"volatility. The absence of an effect in 2016{DASH}2020 cautions against interpreting DFS as a "
 f"permanent or structural formalization driver, and longer panels are needed to test whether the "
 f"pattern is replicated.")
after(p1,
 f"When the sample is restricted to the three Central Asian republics with DGE estimates (Kazakhstan, "
 f"the Kyrgyz Republic, Tajikistan), the negative DFS{DASH}shadow association remains statistically "
 f"significant ({chr(0x2212)}0.026, p < .05), though smaller than in the full eight-country panel. The "
 f"association therefore holds within the focal region, but its economic size is modest\u2014plausibly "
 f"reflecting narrower cross-country variation or the region's specific institutional and economic "
 f"characteristics.")

# ============ Conclusion (#3 no causal, #4 no tax) ============
st("Theoretically, the study applies institutional-voids logic to a technology-mediated account of formalization; the evidence is consistent with, but does not establish",
 f"This study asked whether the diffusion of digital financial services has accompanied a smaller shadow "
 f"economy across post-Soviet transition economies, with Central Asia as the focal region. Using an "
 f"annual panel of eight economies (2011{DASH}2020), digital-payment usage is robustly associated with a "
 f"smaller informal sector in fixed-effects and Driscoll{DASH}Kraay models, conditional on income, but "
 f"the association is concentrated in the earlier part of the sample, does not extend to tax revenue, "
 f"and is statistically insignificant under instrumental-variable and system-GMM estimation. The "
 f"evidence is consistent with a correlation, but the absence of robust IV/GMM results means we cannot "
 f"rule out omitted-variable or reverse-causality explanations; no causal claim is advanced, and the "
 f"formalization hypothesis remains to be tested with stronger identification. Theoretically, the study "
 f"applies institutional-voids logic to a technology-mediated account of formalization; the evidence is "
 f"consistent with, but does not establish, digital infrastructure and institutional capacity acting as "
 f"complements\u2014indeed we find no significant interaction between them.")

# ============ DAG simplify (#7) ============
st("Figure A1 (directed acyclic graph). Assumed causal structure: DFS affects the shadow economy and tax revenue directly",
 f"Figure A1 (directed acyclic graph). Simplified causal diagram for the baseline specification: "
 f"DFS \u2192 SHADOW; GDP per capita \u2192 DFS and GDP per capita \u2192 SHADOW; INST \u2192 SHADOW; "
 f"OPEN \u2192 SHADOW. MOBILE, REMIT, and INFL are included as additional controls but are not assumed "
 f"to lie on the primary causal pathway; consistent with this, Table 8 shows the DFS coefficient is "
 f"essentially unchanged when they are added or removed.")

# ============ remove Table 7 reference in appendix (#5) ============
st("Tables 7 (cash-channel mediation) and the difference-in-differences design",
 f"The difference-in-differences design outlined in Section 4.4 requires coded reform dates that are "
 f"not yet available; consistent with the position taken throughout this revision, no illustrative "
 f"numbers are reported in its place.")

doc.save("Manuscript_Revised_GBR_v4.docx")
print("Saved v4.")
