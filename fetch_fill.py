"""Fetch REAL data from the World Bank API (WDI, Global Findex, WGI) and fill the panel template.
Only genuine, published values are written. Series not available via the API are left BLANK.
Outputs: DFS_data_FILLED.xlsx and DFS_data_FILLED_core.csv / _ECA.csv
"""
import json, time, urllib.request, urllib.error
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

YEARS = list(range(2004, 2023))

# name -> ISO3
CORE = [
    ("Kazakhstan", "KAZ"), ("Kyrgyz Republic", "KGZ"), ("Tajikistan", "TJK"),
    ("Turkmenistan", "TKM"), ("Uzbekistan", "UZB"),
]
ECA = [
    ("Albania","ALB"),("Armenia","ARM"),("Azerbaijan","AZE"),("Belarus","BLR"),
    ("Bosnia and Herzegovina","BIH"),("Bulgaria","BGR"),("Croatia","HRV"),("Georgia","GEO"),
    ("Kazakhstan","KAZ"),("Kyrgyz Republic","KGZ"),("Moldova","MDA"),("Montenegro","MNE"),
    ("North Macedonia","MKD"),("Romania","ROU"),("Russian Federation","RUS"),("Serbia","SRB"),
    ("Tajikistan","TJK"),("Turkmenistan","TKM"),("Ukraine","UKR"),("Uzbekistan","UZB"),
]
ALL_ISO = sorted({iso for _, iso in ECA})  # superset covers core too

# column key -> (WB indicator id, source id). source 2 = WDI default.
FETCH = {
    "TAX":         ("GC.TAX.TOTL.GD.ZS", 2),
    "ACCOUNT":     ("FX.OWN.TOTL.ZS",    2),
    "DIGPAY":      ("g20.any",           28),
    "ATM_per100k": ("FB.ATM.TOTL.P5",    2),
    "GDPPC_USD":   ("NY.GDP.PCAP.KD",    2),
    "OPEN":        ("NE.TRD.GNFS.ZS",    2),
    "UNEMP":       ("SL.UEM.TOTL.ZS",    2),
    "INFL":        ("FP.CPI.TOTL.ZG",    2),
    "REMIT":       ("BX.TRF.PWKR.DT.GD.ZS", 2),
    "URBAN":       ("SP.URB.TOTL.IN.ZS", 2),
    "MOBILE":      ("IT.CEL.SETS.P2",    2),
    "BROADBAND":   ("IT.NET.BBND.P2",    2),
    "REG_QUALITY": ("GOV_WGI_RQ.EST",    3),
    "RULE_OF_LAW": ("GOV_WGI_RL.EST",    3),
}

def api_get(url, tries=3):
    for k in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=40) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            if k == tries - 1:
                print("  ! failed:", e)
                return None
            time.sleep(2)

# data[iso3][year][colkey] = value
data = {iso: {y: {} for y in YEARS} for iso in ALL_ISO}
countries_param = ";".join(ALL_ISO)

def ingest(js, col):
    got = 0
    if js and isinstance(js, list) and len(js) > 1 and js[1]:
        for rec in js[1]:
            iso = rec.get("countryiso3code") or (rec.get("country") or {}).get("id") or ""
            val = rec.get("value")
            try:
                yr = int(rec.get("date"))
            except (TypeError, ValueError):
                continue
            if iso in data and yr in YEARS and val is not None:
                data[iso][yr][col] = round(float(val), 4)
                got += 1
    return got

for col, (code, src) in FETCH.items():
    n = 0
    if src == 28:  # Findex: multi-country not supported -> loop per country
        for iso in ALL_ISO:
            url = (f"https://api.worldbank.org/v2/country/{iso}/indicator/{code}"
                   f"?format=json&date=2004:2022&per_page=100&source=28")
            n += ingest(api_get(url), col)
            time.sleep(0.2)
    else:
        src_q = f"&source={src}" if src != 2 else ""
        url = (f"https://api.worldbank.org/v2/country/{countries_param}/indicator/{code}"
               f"?format=json&date=2004:2022&per_page=20000{src_q}")
        n = ingest(api_get(url), col)
    print(f"{col:12s} <- {code:22s} (src {src}) : {n} values")
    time.sleep(0.4)

# derive INST = mean(REG_QUALITY, RULE_OF_LAW)
for iso in ALL_ISO:
    for y in YEARS:
        rq = data[iso][y].get("REG_QUALITY")
        rl = data[iso][y].get("RULE_OF_LAW")
        if rq is not None and rl is not None:
            data[iso][y]["INST"] = round((rq + rl) / 2, 4)

# ---- build workbook ----
AUTO = ["TAX","ACCOUNT","DIGPAY","ATM_per100k","GDPPC_USD","OPEN","UNEMP","INFL",
        "REMIT","URBAN","MOBILE","REG_QUALITY","RULE_OF_LAW","INST","BROADBAND"]
BLANK = ["SHADOW","SHADOW_MIMIC","POS_ATM_full","CASHLESS_VAL","CASH","MOBILE_COVERAGE"]

# ordered display columns
ORDER = ["country","year",
         "SHADOW","SHADOW_MIMIC","TAX",
         "ACCOUNT","DIGPAY","ATM_per100k","POS_ATM_full","CASHLESS_VAL",
         "CASH","GDPPC_USD","OPEN","UNEMP","INFL","REMIT","URBAN","MOBILE",
         "REG_QUALITY","RULE_OF_LAW","INST","MOBILE_COVERAGE","BROADBAND"]

LABEL = {
    "SHADOW":"SHADOW (author: WB Informal Economy DB - DGE)",
    "SHADOW_MIMIC":"SHADOW_MIMIC (author: MIMIC series)",
    "ATM_per100k":"ATM_per100k (WB, real)",
    "POS_ATM_full":"POS_ATM (author: add POS from IMF FAS)",
    "CASHLESS_VAL":"CASHLESS_VAL (author: IMF FAS)",
    "CASH":"CASH (author: currency/M2, IFS/central bank)",
    "MOBILE_COVERAGE":"MOBILE_COVERAGE (author: ITU)",
}

green = PatternFill("solid", fgColor="C6EFCE")   # auto-filled real
yellow= PatternFill("solid", fgColor="FFF2CC")   # author to fill
idf   = PatternFill("solid", fgColor="D9E1F2")
hf    = PatternFill("solid", fgColor="1F4E78")
hfont = Font(bold=True, color="FFFFFF", size=9)
thin  = Side(style="thin", color="BFBFBF")
bd    = Border(left=thin,right=thin,top=thin,bottom=thin)

def sheet(wb, title, countries):
    ws = wb.create_sheet(title)
    for j, key in enumerate(ORDER, start=1):
        lab = LABEL.get(key, key)
        c = ws.cell(row=1, column=j, value=lab)
        c.fill = hf; c.font = hfont
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = bd
        ws.column_dimensions[get_column_letter(j)].width = 18 if j > 2 else 15
    ws.row_dimensions[1].height = 46
    ws.freeze_panes = "C2"
    r = 2
    for name, iso in countries:
        for y in YEARS:
            row_vals = data[iso][y]
            for j, key in enumerate(ORDER, start=1):
                cell = ws.cell(row=r, column=j); cell.border = bd
                if key == "country":
                    cell.value = name; cell.fill = idf
                elif key == "year":
                    cell.value = y; cell.fill = idf
                elif key in AUTO:
                    v = row_vals.get(key)
                    if v is not None:
                        cell.value = v
                    cell.fill = green
                else:  # blank author columns
                    cell.fill = yellow
            r += 1
    return ws

wb = openpyxl.Workbook(); wb.remove(wb.active)
sheet(wb, "Core_panel_CA", CORE)
sheet(wb, "ECA_panel", ECA)

# legend sheet
lg = wb.create_sheet("READ_ME", 0)
lines = [
 ("READ ME - how this file was filled", True),
 ("", False),
 ("GREEN columns = REAL values fetched from official APIs on the date below. Verify freely.", False),
 ("   Sources: World Bank WDI; Global Findex (source 28); Worldwide Governance Indicators (source 3).", False),
 ("YELLOW columns = could NOT be pulled from an API. You must fill these from the stated source.", False),
 ("   - SHADOW / SHADOW_MIMIC: World Bank Informal Economy Database (Elgin et al.) / MIMIC series.", False),
 ("   - POS_ATM: ATM_per100k is real (World Bank). Add POS terminals from IMF Financial Access Survey, then combine.", False),
 ("   - CASHLESS_VAL: IMF Financial Access Survey.", False),
 ("   - CASH (currency/M2): IMF IFS or national central banks.", False),
 ("   - MOBILE_COVERAGE (3G/4G): ITU DataHub.", False),
 ("", False),
 ("IMPORTANT: ACCOUNT and DIGPAY (Findex) exist ONLY for survey years (2011, 2014, 2017, 2021).", False),
 ("Blank year cells mean the value is genuinely missing - they were NOT invented. Decide how to handle (interpolate/note).", False),
 ("INST = average of REG_QUALITY and RULE_OF_LAW (computed only where both exist).", False),
 ("A blank cell = missing data. It was left empty on purpose; no numbers were fabricated.", False),
]
for i,(t,b) in enumerate(lines, start=1):
    c = lg.cell(row=i, column=1, value=t)
    if b: c.font = Font(bold=True, size=12)
lg.column_dimensions["A"].width = 120

wb.save("DFS_data_FILLED.xlsx")
print("\nWROTE DFS_data_FILLED.xlsx")

# coverage report
def coverage(countries, label):
    print(f"\n--- coverage: {label} ({len(countries)} countries x {len(YEARS)} yrs) ---")
    for key in AUTO:
        filled = sum(1 for _,iso in countries for y in YEARS if data[iso][y].get(key) is not None)
        tot = len(countries)*len(YEARS)
        print(f"  {key:12s}: {filled:4d}/{tot}")
coverage(CORE, "Core")
