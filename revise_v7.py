# -*- coding: utf-8 -*-
"""v7: fix serious NON-thematic internal inconsistencies (descriptives, control set,
table notes, conceptual framework) so text matches the actual 8-country/N=80 estimation."""
from docx import Document
from docx.oxml import OxmlElement
from docx.text.paragraph import Paragraph
doc = Document("Manuscript_Revised_GBR_v6.docx")
DASH="\u2013"
def find(sub):
    for p in doc.paragraphs:
        if sub in p.text: return p
    raise ValueError("not found: "+sub[:45])
def st(sub,new):
    p=find(sub)
    for r in p.runs: r.text=""
    if p.runs: p.runs[0].text=new
    else: p.add_run(new)
    return p
def after(p,text):
    e=OxmlElement("w:p"); p._p.addnext(e); q=Paragraph(e,p._parent); q.add_run(text); return q

# 1) 5.1 descriptives -> real numbers, 8-country panel
st("Table 2 reports summary statistics for the core Central Asian panel.",
 f"Table 2 reports summary statistics for the eight-country transition panel. Two features stand out. "
 f"First, informality is large and dispersed: the mean shadow economy is about 42% of GDP, ranging "
 f"from the low-thirties in the most formalized country-years to roughly 60% in Georgia. Second, "
 f"digital-payment usage varies widely\u2014from near zero in the early Tajik and Kyrgyz observations to "
 f"about 79% in the most digitalized country-years\u2014reflecting the sharp within-country acceleration "
 f"over the sample. Tax revenue averages about 16% of GDP, modest by international standards and "
 f"consistent with a narrow assessable base.")

# 2) Table 2 title + note
st("Table 2. Descriptive statistics, core Central Asian panel (2004",
 f"Table 2. Descriptive statistics, eight-country transition panel (2011{DASH}2020).")
st("Note. Statistics are computed on the estimation sample used in the baseline specification",
 f"Note. Statistics are computed on the estimation sample (N = 80). INST is the average of the WGI "
 f"regulatory-quality and rule-of-law scores (approximate range {chr(0x2212)}2.5 to 2.5). The "
 f"Findex-based indicators (ACCOUNT, DIGPAY) are interpolated between survey years within country; all "
 f"imputed cells are flagged in the replication dataset.")

# 3) 4.2 control set aligned with the estimated model
st("Control variables follow the informality and tax-capacity literatures: the natural logarithm of real GDP per capita (LGDPPC) and its square",
 f"Control variables follow the informality and tax-capacity literatures. The reported specifications "
 f"include the natural logarithm of real GDP per capita (LGDPPC), trade openness (exports plus imports "
 f"over GDP), consumer-price inflation, the ratio of personal remittances to GDP, and institutional "
 f"quality (the average of the WGI regulatory-quality and rule-of-law scores, INST). Mobile-cellular "
 f"subscriptions and fixed-broadband penetration are used as instruments for DFS rather than as "
 f"controls (Section 4.4). Table 1 summarizes the variables and their sources.")

# 4) Table 5 note: correct the control set (no UNEMP/URBAN/MOBILE)
st("Note. Dependent variables as indicated by column headers. Country-clustered standard errors in parentheses.",
 f"Note. Dependent variables as indicated by column headers. Country-clustered standard errors in "
 f"parentheses. *p < .10, **p < .05, ***p < .01. Columns (2) and (4) control for log GDP per capita, "
 f"trade openness, inflation, remittances, and institutional quality; columns (1) and (3) include only "
 f"country and year fixed effects. All specifications include country and year fixed effects.")

# 5) Conceptual framework: soften tax-base outcome
st("Figure 1 summarizes the conceptual model. DFS operate through two proximate channels",
 f"Figure 1 summarizes the conceptual model. DFS operate through two proximate channels\u2014a "
 f"traceability channel that raises the observability of transactions and a financial-access channel "
 f"that expands the availability of formal credit to previously informal actors\u2014both of which feed "
 f"into formalization, measured here primarily as a smaller shadow economy (tax revenue is also "
 f"examined). Institutional quality is modelled as a potential moderator of the DFS{DASH}formalization "
 f"relationship, consistent with the institutional-voids logic that technology and institutions may "
 f"jointly determine formalization outcomes.")

# 6) Section 3: acknowledge the wider comparator sample
sec3 = find("The five republics of Central Asia share a common Soviet institutional inheritance")
after(sec3,
 f"Although Central Asia is the focal region, the estimation panel adds five comparable post-Soviet "
 f"transition economies (Armenia, Azerbaijan, Georgia, Belarus, and Moldova) that share the Soviet "
 f"institutional legacy and for which model-based shadow-economy estimates are available; they provide "
 f"additional cross-sectional variation and a check that the Central Asian pattern is not idiosyncratic.")

doc.save("Manuscript_Revised_GBR_v7.docx")
print("Saved v7.")
