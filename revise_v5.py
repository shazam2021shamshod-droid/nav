# -*- coding: utf-8 -*-
"""v5: five final minor consistency fixes. Operates on v4 -> v5."""
from docx import Document

doc = Document("Manuscript_Revised_GBR_v4.docx")

def repl_para(locator, old, new):
    for p in doc.paragraphs:
        if locator in p.text:
            newtext = p.text.replace(old, new)
            for r in p.runs: r.text = ""
            if p.runs: p.runs[0].text = newtext
            else: p.add_run(newtext)
            return True
    raise ValueError("locator not found: "+locator[:40])

def setpara(locator, new):
    for p in doc.paragraphs:
        if locator in p.text:
            for r in p.runs: r.text=""
            if p.runs: p.runs[0].text=new
            else: p.add_run(new)
            return True
    raise ValueError("not found: "+locator[:40])

# ---- #1 Table 1: remove CASH row; update DFS_INDEX definition to 3 indicators ----
t1 = doc.tables[0]
# update DFS_INDEX definition (row 3)
t1.cell(3,1).text = ("PCA composite of account ownership, digital-payment use, and ATM density "
                     "(rescaled 0\u2013100); used as a robustness check")
# remove CASH row (row 5)
for row in list(t1.rows):
    if row.cells[0].text.strip() == "CASH":
        row._tr.getparent().remove(row._tr)
        break

# ---- #1 delete the cash-channel sentence in Section 4.2 ----
repl_para("To test the cash channel (H3), we use currency in circulation",
 "To test the cash channel (H3), we use currency in circulation relative to broad money (CASH) as a proxy for cash intensity. ",
 "")

# ---- #2 Section 4.3: H4->H2; delete cash-channel sentence ----
setpara("The institutional complementarity in H4 is tested by adding an interaction term",
 "The institutional complementarity in H2 is tested by adding an interaction term DFSit \u00d7 INSTit; "
 "a positive coefficient in the TAX equation (and a negative one in the SHADOW equation) would "
 "indicate that stronger institutions amplify the formalization association of DFS.")

# ---- #3 Section 4.4: 'suggestive' -> 'exploratory' ----
repl_para("so the IV estimates are read as suggestive",
 "so the IV estimates are read as suggestive", "so the IV estimates are treated as exploratory")

# ---- #4 Section 8.1: soften untested policy claim ----
repl_para("(i) interoperability and merchant digitization are prerequisites for transaction traceability",
 "(i) interoperability and merchant digitization are prerequisites for transaction traceability",
 "(i) interoperability and merchant digitization may be important prerequisites for transaction "
 "traceability, though neither is directly tested in our data")

doc.save("Manuscript_Revised_GBR_v5.docx")
print("Saved v5.")
