# -*- coding: utf-8 -*-
"""v8: final title; reconcile Introduction contributions with actual findings (fix the
complementarity/tax contradictions flagged by the reviewer); deepen managerial implications."""
from docx import Document
doc = Document("Manuscript_Revised_GBR_v7.docx")
DASH="\u2013"
def st(sub,new):
    for p in doc.paragraphs:
        if sub in p.text:
            for r in p.runs: r.text=""
            if p.runs: p.runs[0].text=new
            else: p.add_run(new)
            return True
    raise ValueError("not found: "+sub[:45])

# ---- FINAL TITLE ----
st("From Cash to Compliance: Digital Financial Services, Institutional Voids",
 "Can Digital Payments Formalize the Shadow Economy? Evidence from Eight Post-Soviet Transition Economies")

# ---- Reconcile Introduction contributions (fix contradiction #1; tax; CA overclaim) ----
st("The study makes four contributions, three empirical and one theoretical.",
 f"The study makes three contributions. First, it provides one of the first focused, multi-country "
 f"panel assessments of the DFS{DASH}informality nexus for post-Soviet transition economies, with the "
 f"Central Asian republics\u2014highly informal and rapidly digitalizing, yet under-represented in the "
 f"empirical literature\u2014as the focal region. Second, it examines formalization on two margins, "
 f"modelling both the shadow economy and tax revenue; we find a robust conditional association for the "
 f"former but no significant association for the latter, and report this asymmetry transparently rather "
 f"than assuming a uniform fiscal dividend. Third, and most directly relevant to management "
 f"scholarship, it applies institutional-voids theory (Khanna & Palepu, 2010) to a technology-mediated "
 f"account of formalization, positioning shared digital-payment infrastructure as a market-supporting "
 f"institution that lowers the cost of overcoming informational voids for all market participants "
 f"simultaneously\u2014thereby reshaping the addressable market that banks, fintech entrants, and "
 f"multinationals face in emerging and transition economies. We treat the moderating role of "
 f"institutions as an empirical question and, in these data, find no significant interaction between "
 f"DFS and institutional quality; we therefore do not claim institutional complementarity. The "
 f"remainder of the article proceeds as follows. Section 2 reviews the literature, develops the "
 f"conceptual framework, and states the hypotheses. Section 3 describes the Central Asian context and "
 f"the wider sample. Section 4 sets out the data and methodology, Section 5 presents the results, and "
 f"Section 6 discusses them. Section 7 draws out the theoretical contribution, Section 8 develops "
 f"policy and managerial implications, and Sections 9 and 10 conclude with limitations and future "
 f"directions.")

# ---- Deepen managerial implications (#7) ----
st("The findings also carry implications for banks, fintech firms, and payment-network operators. Although we find no evidence of institutional complementarity",
 f"The findings also carry concrete implications for banks, fintech firms, payment-network operators, "
 f"and multinational enterprises. First, the mechanism the data are consistent with\u2014rising "
 f"digital-payment usage making previously cash-based microenterprises and households more visible"
 f"\u2014implies a specific commercial opportunity: the transaction records generated as a by-product of "
 f"payments can be used to build credit scores for thin-file customers, so firms that invest early in "
 f"payment acceptance and data infrastructure can convert formalization into a proprietary underwriting "
 f"advantage. Second, because the association is strongest in the early, extensive-margin phase of "
 f"digitalization (2011{DASH}2015), first-mover investment in merchant acquisition and digital "
 f"onboarding in markets at an early adoption stage is likely to compound, whereas entrants to "
 f"already-digitalized markets should compete on intensive-margin services\u2014credit, savings, "
 f"insurance\u2014rather than basic account provision. Third, the remittance-digitization opportunity in "
 f"migrant-sending economies (the Kyrgyz Republic, Tajikistan, Armenia, Moldova) is a specific product "
 f"strategy: regulated digital corridors convert informal, hawala-type transfers into recorded flows "
 f"that both formalize the flow and create the transaction history needed to cross-sell savings and "
 f"micro-insurance to recipient households. Fourth, because we find no evidence that institutions "
 f"amplify the DFS effect, firms should not condition entry on institutional quality expecting a larger "
 f"DFS payoff; instead, thin institutions matter for payment-system reliability, settlement risk, and "
 f"contract enforcement independently, and interoperable, open standards\u2014which enlarge the "
 f"addressable network rather than fragmenting it into walled gardens\u2014are a shared interest of "
 f"entrants, incumbents, and the state. Finally, because the aggregate association does not survive "
 f"instrumental-variable and dynamic-panel estimation, managers should treat DFS-driven formalization "
 f"as a plausible but unproven driver of market expansion and pair it with their own market "
 f"intelligence rather than assuming a mechanical effect.")

doc.save("Manuscript_Revised_GBR_v8.docx")
print("Saved v8.")
