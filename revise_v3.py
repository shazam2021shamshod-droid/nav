# -*- coding: utf-8 -*-
"""Build Manuscript_Revised_GBR_v3.docx from the ORIGINAL manuscript, filling every table
with REAL numbers estimated on the final 8-country transition panel (N=80) and integrating
reviewer points 1-11. Results/abstract rewritten to reflect the ACTUAL (honest) findings."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from docx import Document
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph
from linearmodels.panel import PanelOLS

# ---- compute overall R2 for Table 5 models ----
d = pd.read_csv("DFS_panel_final.csv"); P = d.set_index(["country","year"])
def r2(dv, regs):
    dd = P[[dv]+regs].dropna()
    r = PanelOLS(dd[dv], dd[regs], entity_effects=True, time_effects=True).fit()
    return max(r.rsquared, 0)
CTRL=["LGDPPC","OPEN","INFL","REMIT","INST"]
R2 = {"s1":r2("SHADOW",["DFS_INDEX"]), "s2":r2("SHADOW",["DFS_INDEX"]+CTRL),
      "t1":r2("TAX",["DFS_INDEX"]), "t2":r2("TAX",["DFS_INDEX"]+CTRL)}

doc = Document("Manuscript_Revised_GBR.docx")
def setc(t,r,c,v): t.cell(r,c).text=v
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
    np_=OxmlElement("w:p"); p._p.addnext(np_); q=Paragraph(np_,p._parent); q.add_run(text); return q
def block(anchor,texts):
    cur=anchor
    for t in texts: cur=after(cur,t)
    return cur

# ================== TABLE 2 (tables[1]) descriptives N=80 ==================
t2=doc.tables[1]
desc=[("SHADOW (% of GDP)","41.9","7.7","33.2","61.6"),
      ("TAX (% of GDP)","15.8","4.2","8.3","23.1"),
      ("DFS_INDEX (0–100)","49.6","25.2","0.0","100.0"),
      ("DIGPAY (%)","34.9","20.8","0.0","78.7"),
      ("SELFEMP (% of employment)","41.5","18.0","7.6","68.3"),
      ("LGDPPC (log)","8.13","0.80","6.70","9.30"),
      ("OPEN (% of GDP)","89.5","25.0","49.9","158.0"),
      ("REMIT (% of GDP)","14.1","12.3","0.1","43.8"),
      ("MOBILE (per 100)","119.7","18.8","62.3","174.7"),
      ("INST (index)","-0.40","0.50","-1.20","0.70")]
for i,(lab,m,sd,mn,mx) in enumerate(desc, start=1):
    setc(t2,i,0,lab); setc(t2,i,1,m); setc(t2,i,2,sd); setc(t2,i,3,mn); setc(t2,i,4,mx); setc(t2,i,5,"80")

# ================== TABLE 3 (tables[2]) correlations, N=80 ==================
t3=doc.tables[2]
setc(t3,2,1,"+0.44***")
setc(t3,3,1,"+0.04"); setc(t3,3,2,"+0.12")
setc(t3,4,1,"n.a."); setc(t3,4,2,"n.a."); setc(t3,4,3,"n.a.")
setc(t3,5,1,"+0.04"); setc(t3,5,2,"+0.08"); setc(t3,5,3,"+0.68***"); setc(t3,5,4,"n.a.")
setc(t3,6,1,"+0.57***"); setc(t3,6,2,"+0.78***"); setc(t3,6,3,"+0.31***"); setc(t3,6,4,"n.a."); setc(t3,6,5,"+0.37***")

# ================== TABLE 4 (tables[3]) PCA ==================
t4=doc.tables[3]
setc(t4,1,1,"0.519")
setc(t4,2,1,"346.47, df = 3, p < .001")
setc(t4,3,1,"2.514")
setc(t4,4,1,"83.8")
setc(t4,5,1,"0.977"); setc(t4,6,1,"0.953"); setc(t4,7,1,"0.807 (ATM density; POS unavailable)"); setc(t4,8,1,"n.a. (data unavailable)")

# ================== TABLE 5 (tables[4]) baseline FE, real ==================
t5=doc.tables[4]
cells={(2,1):"+0.054\n(0.042)",(2,2):"-0.056**\n(0.028)",(2,3):"+0.038\n(0.030)",(2,4):"+0.020\n(0.020)",
       (3,2):"+13.574***\n(4.448)",(3,4):"+0.935\n(5.241)",
       (4,2):"-0.031\n(0.019)",(4,4):"+0.032\n(0.022)",
       (5,2):"-0.092**\n(0.041)",(5,4):"-0.075\n(0.093)",
       (6,2):"-0.015\n(0.017)",(6,4):"-0.024\n(0.043)",
       (7,2):"+0.099\n(1.794)",(7,4):"-6.467*\n(3.819)",
       (10,1):"80",(10,2):"80",(10,3):"80",(10,4):"80",
       (11,1):f"{R2['s1']:.2f}",(11,2):f"{R2['s2']:.2f}",(11,3):f"{R2['t1']:.2f}",(11,4):f"{R2['t2']:.2f}"}
for (r,c),v in cells.items(): setc(t5,r,c,v)

# ================== TABLE 6 (tables[5]) robustness, real ==================
t6=doc.tables[5]
rows=[("FE (baseline, full panel)","-0.056**","+0.020","N = 80; within-country FE"),
      ("FE, Driscoll–Kraay SE","-0.056*","+0.020","CSD-robust standard errors"),
      ("System GMM (exploratory — see 4.4)","+0.027","—","Hansen p = 1.00 (instrument proliferation, 57 instr./8 groups → unreliable); AR(2) p = .60"),
      ("IV (2SLS: mobile/broadband)","-0.018","+0.081","Effect insignificant under IV"),
      ("Excl. Kazakhstan","-0.084***","+0.011","Drop largest economy"),
      ("Central Asia subsample (N = 30)","-0.026**","+0.027","Focus region")]
for i,(lab,sh,tx,dg) in enumerate(rows, start=1):
    setc(t6,i,0,lab); setc(t6,i,1,sh); setc(t6,i,2,tx); setc(t6,i,3,dg)

# ================== HIGHLIGHTS (paras) — honest ==================
settext("Digital financial services (DFS) are associated with a smaller shadow economy",
 "Across eight post-Soviet transition economies (2004–2022), deeper digital-financial-services (DFS) penetration is robustly associated with a smaller shadow economy in two-way fixed-effects models, conditional on income level.")
settext("The formalization effect strengthens where regulatory quality and the rule of law are stronger",
 "The association with tax revenue is positive but statistically insignificant, and we find no significant DFS × institutions interaction, so we do not claim an institutional-complementarity effect.")
settext("Reduced cash intensity is a key transmission channel",
 "A cash-intensity (currency/broad-money) series was not available for the sample, so the cash channel is set out as a hypothesis to be tested rather than an established result.")
settext("Results hold under Driscoll–Kraay errors, system-GMM, instrumental-variable, and wider-panel estimation.",
 "The negative shadow-economy association is stable under Driscoll–Kraay errors and across subsamples, but is weaker and statistically insignificant under instrumental-variable and system-GMM estimation, so we interpret it as robust in association but only suggestive as to causation.")
settext("The study extends institutional-voids theory to digital finance and offers guidance",
 "The study applies institutional-voids logic to digital finance and offers cautious guidance for tax authorities, banks, and fintech providers.")

# ================== ABSTRACT (#2,#8,#11 + honest) ==================
settext("Central Asia's five republics carry some of the largest informal economies",
 "Central Asia's economies carry some of the largest informal sectors among transition regions, "
 "constraining public revenue even as digital financial services (DFS)—mobile money, cards, and "
 "instant payments—rapidly diffuse. Drawing on institutional theory and the economics of tax evasion, "
 "we ask whether DFS diffusion is associated with a smaller shadow economy and a broader tax base. "
 "For statistical power we assemble an annual panel of eight post-Soviet transition economies "
 "(2011–2020; N = 80) as the primary empirical setting, within which the Central Asian republics are "
 "the focal region and are examined as a subsample. The shadow economy is measured with dynamic "
 "general-equilibrium (DGE) estimates and the DFS index by principal-component analysis of account "
 "ownership, digital-payment use, and ATM density. In two-way fixed-effects models, deeper DFS "
 "penetration is significantly associated with a smaller shadow economy once income is controlled "
 "(a one-standard-deviation rise in DFS corresponds to about −0.18 SD of informality), and this "
 "association is stable under Driscoll–Kraay errors and across subsamples. However, the association "
 "with tax revenue is positive but insignificant, the DFS × institutions interaction is insignificant, "
 "and the effect is weaker and insignificant under instrumental-variable and system-GMM estimation. "
 "We therefore read the evidence as a robust conditional association rather than clean causal proof, "
 "and we apply—rather than claim to extend—institutional-voids logic to the digital-finance context. "
 "Implications for tax administrations and financial-sector strategy are drawn cautiously.")

# ================== 4.1 sample (#2) ==================
settext("The core sample is an annual panel of the five Central Asian republics",
 "The primary estimation sample is an annual panel of eight post-Soviet transition economies with "
 "the most complete data—Kazakhstan, the Kyrgyz Republic, Tajikistan (the Central Asian focus), "
 "together with Armenia, Azerbaijan, Georgia, Belarus, and Moldova—over 2011–2020 (N = 80). The three "
 "Central Asian republics are analysed as a focused subsample (N = 30). Because the cross-sectional "
 "dimension is modest, dynamic system-GMM is reported only as an exploratory cross-check. Uzbekistan "
 "and Turkmenistan are omitted from the DGE-based analysis because model-based shadow-economy estimates "
 "are not available for them in the World Bank informal-economy database; a self-employment-based "
 "informality proxy that does cover them is used in a robustness check. Data are drawn from public "
 "sources: World Bank World Development Indicators and the Global Findex database; the World Bank "
 "informal-economy database (Elgin et al., 2021) for the DGE shadow-economy series; the IMF Financial "
 "Access Survey for payment infrastructure; and the Worldwide Governance Indicators for institutional quality.")

# ================== 4.5 software (#10, truthful — Python) ==================
settext("[AUTHOR ACTION REQUIRED: state the statistical software",
 "All estimation and construction were carried out in Python 3.11: the composite DFS index and its "
 "PCA diagnostics (Table 4) with numpy/scipy/factor_analyzer; correlations (Table 3) with scipy; "
 "two-way fixed-effects and Driscoll–Kraay (kernel) models with the linearmodels package (PanelOLS); "
 "instrumental-variable 2SLS with linearmodels (IV2SLS); and system-GMM with pydynpd. Missing Global "
 "Findex values between survey years were linearly interpolated within country and residual gaps "
 "imputed by multivariate imputation (scikit-learn IterativeImputer); all imputed cells are flagged in "
 "the replication dataset. The compiled dataset and code are available from the corresponding author on request.")

doc.save("Manuscript_Revised_GBR_v3.docx")
print("Saved v3 (tables + core text). R2:", {k:round(v,2) for k,v in R2.items()})
