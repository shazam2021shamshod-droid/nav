# -*- coding: utf-8 -*-
"""Second pass on Manuscript_Revised_GBR_v3.docx: rewrite Results/Discussion/Theory text to
match the REAL findings, add Tables 7/8/A1 + Figure 2 blocks, integrate reviewer points 3,5,6,7,8,9."""
from docx import Document
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph

doc = Document("Manuscript_Revised_GBR_v3.docx")
def find(sub):
    for p in doc.paragraphs:
        if sub in p.text: return p
    raise ValueError("not found: "+sub[:40])
def settext(sub,new):
    p=find(sub); rs=p.runs
    if rs:
        rs[0].text=new
        for r in rs[1:]: r.text=""
    else: p.add_run(new)
    return p
def after(p,text):
    e=OxmlElement("w:p"); p._p.addnext(e); q=Paragraph(e,p._parent); q.add_run(text); return q
def block(anchor,texts):
    cur=anchor
    for t in texts: cur=after(cur,t)
    return cur

# ---- 5.3 baseline results (#9 standardized/elasticity) ----
settext("Table 5 presents the two-way fixed-effects results.",
 "Table 5 presents the two-way fixed-effects estimates. The DFS–shadow association depends on "
 "conditioning: with no controls the within-country DFS coefficient is small and insignificant "
 "(column 1, +0.054), but once log GDP per capita and the remaining controls are included it turns "
 "negative and significant (column 2, −0.056, p < .05). Because DFS and income are highly collinear "
 "(r ≈ 0.68), the formalization association is identified holding development constant rather than "
 "unconditionally. In magnitude, a one-standard-deviation rise in DFS_INDEX corresponds to about "
 "−0.18 standard deviations of the shadow economy (elasticity at the mean ≈ −0.07); a ten-point rise "
 "in the 0–100 index maps to roughly −0.56 percentage points of GDP. For tax revenue (columns 3–4) "
 "the DFS coefficient is positive but small and insignificant throughout (standardized β ≈ +0.12). "
 "These results support H1 conditionally and provide no support for H2.")

# ---- 5.4 robustness ----
settext("Table 6 summarizes the robustness and endogeneity analysis.",
 "Table 6 summarizes the robustness and endogeneity analysis for the DFS coefficient. The negative "
 "shadow-economy association is stable under Driscoll–Kraay standard errors (−0.056, p < .10), larger "
 "when Kazakhstan is excluded (−0.084, p < .01), present in the Central Asian subsample (−0.026, "
 "p < .05), and reproduced when the single DIGPAY indicator replaces the composite (−0.051, p < .05). "
 "It is not, however, robust to estimators that target endogeneity: the instrumental-variables "
 "estimate (mobile-network and broadband rollout) is negative but insignificant (−0.018), and the "
 "system-GMM estimate is small, positive, and insignificant (+0.027). The GMM diagnostics are "
 "themselves unreliable—the Hansen statistic is degenerate (p = 1.00) because the instrument count "
 "(57) far exceeds the eight groups—which is exactly why, per Section 4.4, the dynamic-panel results "
 "are exploratory. Across the tax equations the DFS coefficient is insignificant under every "
 "estimator. The evidence is thus best described as a robust conditional association whose causal "
 "interpretation remains suggestive.")

# insert Table A1, Table 8, Figure 2 after the robustness paragraph
anchorR = find("Table 6. Robustness and endogeneity")
block(anchorR, [
 "Table A1 (pre-trends). Dependent variable: shadow economy (% of GDP). Earlier window 2011–2015: "
 "DFS_INDEX = −0.090 (SE 0.035, p < .05; N = 40). Later window 2016–2020: DFS_INDEX = −0.008 "
 "(SE 0.019, n.s.; N = 40). Two-way fixed effects, full controls. The association is concentrated in "
 "the earlier window and is not stable over time—a caution rather than a clean placebo result.",
 "Table 8 (control-set sensitivity). Dependent variable: shadow economy; DFS_INDEX coefficient. Full "
 "controls −0.056 (p < .05); adding MOBILE −0.055 (p < .10); dropping REMIT −0.063 (p < .05); "
 "dropping INFL −0.056 (p < .05); parsimonious set (LGDPPC, OPEN, INST) plus MOBILE −0.063 (p < .05). "
 "The coefficient is stable across control sets as long as GDP per capita is included; it is the "
 "inclusion of income—not of MOBILE, REMIT, or INFL—that matters. Because MOBILE, REMIT, and INFL may "
 "lie on the causal pathway between DFS and informality, the preferred specification is read with that "
 "caveat, and the assumed causal structure is set out as a directed acyclic graph in Appendix Figure A1.",
 "Figure 2 (marginal effects). The marginal effect of DFS on the shadow economy across the observed "
 "institutional range (INST ≈ −1.2 to +0.7) is negative throughout, but its 95% confidence interval "
 "includes zero over most of the range, consistent with the insignificant DFS × INST interaction; the "
 "marginal effect on tax revenue is indistinguishable from zero. The figure does not support an "
 "institutional-complementarity reading."])

# ---- 5.5 mechanisms (H3 not testable, H4 not supported) ----
settext("Two further specifications examine the mechanisms.",
 "Two mechanism questions—the cash channel (H3) and institutional complementarity (H4)—can be "
 "addressed only partially. A consistent cash-intensity (currency-to-broad-money) series was not "
 "available from open sources for this sample, so the formal mediation analysis specified in "
 "Section 4.3 (decomposition into direct and DFS→CASH→outcome effects with a Sobel–Goodman test and "
 "bootstrapped intervals; Table 7) could not be estimated; we make no cash-channel claim. For H4, the "
 "interaction DFS × INST is negative for the shadow economy but insignificant (−0.012), and a squared "
 "interaction term is also insignificant, as is the interaction in the tax equation. We therefore find "
 "no evidence of institutional complementarity in these data and do not advance that claim. Table 7 is "
 "reported as unfilled pending the cash series; no illustrative numbers are entered in its place.")

# ---- 4.4 IV critical + pre-trends + DiD (#3) ----
p44 = find("Robustness checks include the alternative MIMIC-based shadow-economy series")
block(p44, [
 "We report three further identification checks. First, on pre-trends: splitting the sample into an "
 "earlier (2011–2015) and a later (2016–2020) window shows the negative DFS–shadow association in the "
 "earlier window only, cautioning that it is not stable over time (Appendix Table A1). Second, a "
 "difference-in-differences design exploiting staggered payment-system reforms (e.g., Kazakhstan's "
 "super-app-led expansion; Uzbekistan's 2017 liberalization) is a natural extension but requires "
 "reform-timing coding we leave for future work. Third, the exclusion restriction for the "
 "telecommunications instruments is not beyond question—mobile and broadband rollout could affect "
 "informality through e-commerce or information channels—so the IV estimates are read as suggestive "
 "and, as shown in Section 5.4, are in any case statistically insignificant."])

# ---- Section 6 discussion (honest) + measurement error (#7) ----
settext("The evidence assembled here supports the view that digital financial services function as a formalization technology",
 "The evidence assembled here is consistent with digital financial services acting as a formalization "
 "technology, but it is more qualified than a strong reading would suggest. Deeper DFS penetration is "
 "robustly associated with a smaller shadow economy in fixed-effects and Driscoll–Kraay models and "
 "across subsamples, conditional on income. That association does not survive as a clean causal "
 "estimate: it is insignificant under instrumental-variable and dynamic-panel estimation, is "
 "concentrated in the earlier part of the sample, and does not extend to tax revenue. It is therefore "
 "best summarized as a robust conditional correlation with suggestive rather than conclusive causal content.")
settext("The mechanism analysis is instructive.",
 "The mechanism evidence is limited. The cash channel could not be tested for want of a cash-intensity "
 "series, and the DFS × institutions interaction that would indicate complementarity is statistically "
 "insignificant. We accordingly refrain from the stronger mechanism and complementarity claims and "
 "treat them as open questions. Two data limitations reinforce this caution: the shadow economy is "
 "model-based, so measurement error—if largely classical—attenuates coefficients toward zero and the "
 "true association may be somewhat larger than estimated; and DGE estimates are unavailable for "
 "Uzbekistan and Turkmenistan, so the analysis rests on eight economies with complete data, the three "
 "DGE-covered Central Asian republics being examined as a subsample.")

# ---- Section 7 theory tone-down (#8) ----
settext("This study's principal theoretical contribution is to extend institutional-voids theory",
 "This study's contribution to theory is to apply institutional-voids logic (Khanna & Palepu, 2010; "
 "Meyer et al., 2009) to the digital-finance context rather than to claim a wholesale extension of it. "
 "The pattern we document—deeper shared payment infrastructure accompanying a smaller informal sector, "
 "conditional on income—is consistent with the idea that digital rails can partially substitute for "
 "firm-specific institutional bridging by generating verifiable information as a by-product of "
 "transacting. While our aggregate design cannot directly test this firm-level mechanism, the "
 "aggregate patterns are consistent with the institutional-voids-filling interpretation.")
settext("At the same time, the institutional-complementarity result (H4)",
 "At the same time, we do not find the institutional-complementarity effect that a stronger version of "
 "the argument would predict: the DFS × institutions interaction is statistically insignificant in our "
 "data. Whether complementarity emerges with richer data, longer panels, or firm-level evidence is an "
 "open and testable question, and we flag it as a priority for future international-business research.")

# ---- Conclusion tone-down (#8) ----
settext("Theoretically, the study extends institutional-voids theory to a technology-mediated account of formalization",
 "Theoretically, the study applies institutional-voids logic to a technology-mediated account of "
 "formalization; the evidence is consistent with, but does not establish, digital infrastructure and "
 "institutional capacity acting as complements")

# ---- Appendix (DAG) (#6) ----
lim = find("assess whether the formalization gains from DFS persist or attenuate")
block(lim, [
 "Appendix A. Supplementary analyses.",
 "Figure A1 (directed acyclic graph). Assumed causal structure: DFS affects the shadow economy and tax "
 "revenue directly and (hypothetically) through cash intensity (CASH), with GDP per capita, trade "
 "openness, and institutional quality as common causes that are conditioned on, and telecommunications "
 "infrastructure (MOBILE, BROADBAND) as a driver of DFS used as an instrument. Under this structure "
 "CASH is a mediator (excluded from the baseline conditioning set) and MOBILE may be a partial mediator, "
 "which motivates the sensitivity analysis in Table 8.",
 "Tables 7 (cash-channel mediation) and the difference-in-differences design in Section 4.4 require, "
 "respectively, a currency-to-broad-money series and coded reform dates that are not yet available; "
 "consistent with the position taken for all tables in this revision, no illustrative numbers are "
 "entered in their place."])

doc.save("Manuscript_Revised_GBR_v3.docx")
print("v3 second pass complete.")
