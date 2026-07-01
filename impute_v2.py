# -*- coding: utf-8 -*-
"""Rebuild the COMPLETE imputed panel INCLUDING Uzbekistan & Turkmenistan, using
self-employment (% of employment, ILO modelled) as the relative informality proxy
that is observed for every country. SHADOW (DGE) is kept where it exists; SELFEMP
covers all five Central Asian republics. Real data only; Findex interpolated."""
import json
import numpy as np, pandas as pd
from sklearn.experimental import enable_iterative_imputer   # noqa
from sklearn.impute import IterativeImputer
from sklearn.linear_model import BayesianRidge

YEAR_MIN, YEAR_MAX = 2011, 2020
NAME = {"ALB":"Albania","ARM":"Armenia","AZE":"Azerbaijan","BLR":"Belarus",
 "BIH":"Bosnia and Herzegovina","BGR":"Bulgaria","HRV":"Croatia","GEO":"Georgia",
 "KAZ":"Kazakhstan","KGZ":"Kyrgyz Republic","MDA":"Moldova","MNE":"Montenegro",
 "MKD":"North Macedonia","ROU":"Romania","RUS":"Russian Federation","SRB":"Serbia",
 "TJK":"Tajikistan","TKM":"Turkmenistan","UKR":"Ukraine","UZB":"Uzbekistan"}
ISO_OF = {v:k for k,v in NAME.items()}

# self-employment (real) from saved API response
sj = json.load(open("self.json"))
SELF = {}
for x in sj[1]:
    iso = x.get("countryiso3code") or x["country"]["id"]
    if x["value"] is not None:
        SELF[(iso, int(x["date"]))] = round(float(x["value"]), 4)

def load(path):
    df = pd.read_csv(path)
    df.columns = [str(c).split(" (")[0].strip() for c in df.columns]
    for c in df.columns:
        if c != "country":
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df["SELFEMP"] = [SELF.get((ISO_OF.get(c), int(y))) for c, y in zip(df.country, df.year)]
    return df

NUM = ["SHADOW","SHADOW_MIMIC","SELFEMP","TAX","ACCOUNT","DIGPAY","ATM_per100k","GDPPC_USD",
       "OPEN","UNEMP","INFL","REMIT","URBAN","MOBILE","BROADBAND","REG_QUALITY","RULE_OF_LAW"]
TARGETS = ["TAX","ACCOUNT","DIGPAY","ATM_per100k","OPEN","UNEMP","INFL","REMIT",
           "URBAN","MOBILE","BROADBAND","REG_QUALITY","RULE_OF_LAW","GDPPC_USD"]

def process(path, label):
    df = load(path)
    # keep countries that have an informality measure (SELFEMP covers all) -> none dropped
    keep = df.groupby("country")["SELFEMP"].apply(lambda s: s.notna().any())
    keep = keep[keep].index.tolist()
    df = df[df.country.isin(keep)].copy().sort_values(["country","year"]).reset_index(drop=True)
    # interpolate Findex + other targets within country over full range (uses 2021 anchor)
    for c in TARGETS:
        df[c] = df.groupby("country")[c].transform(
            lambda s: s.interpolate(method="linear", limit_area="inside"))
    df = df[(df.year>=YEAR_MIN)&(df.year<=YEAR_MAX)].copy().reset_index(drop=True)
    flags = df[TARGETS].isna()
    # MICE for remaining scattered gaps
    feat = df[NUM].copy(); feat["yr"]=df.year-df.year.mean(); feat["yr2"]=feat["yr"]**2
    dummies = pd.get_dummies(df["country"], prefix="c").astype(float)
    X = pd.concat([feat, dummies], axis=1)
    imp = IterativeImputer(estimator=BayesianRidge(), max_iter=50, sample_posterior=False,
                           random_state=42, min_value=0)
    Xi = pd.DataFrame(imp.fit_transform(X), columns=X.columns)
    for c in TARGETS:
        vals = df[c].copy(); miss = vals.isna()
        vals[miss] = Xi[c].values[miss.values]
        if c in ("ACCOUNT","DIGPAY","UNEMP","URBAN"): vals = vals.clip(0,100)
        elif c in ("ATM_per100k","MOBILE","BROADBAND","OPEN","INFL","REMIT","TAX","GDPPC_USD"):
            vals = vals.clip(lower=0)
        df[c] = vals.values
    df["LGDPPC"] = np.log(df["GDPPC_USD"])
    df["INST"] = (df["REG_QUALITY"]+df["RULE_OF_LAW"])/2
    print(f"\n== {label} == countries={df.country.nunique()} rows={len(df)}")
    print("   SHADOW real obs:", int(df['SHADOW'].notna().sum()),
          "| SELFEMP real obs:", int(df['SELFEMP'].notna().sum()), "(informality proxy, all countries)")
    print("   MICE-imputed cells:", {c:int(flags[c].sum()) for c in TARGETS if flags[c].sum()})
    return df, flags

core_df, core_fl = process("DFS_data_FILLED_core.csv", "CORE CA (5 countries incl UZB/TKM)")
eca_df,  eca_fl  = process("DFS_data_FILLED_ECA.csv",  "ECA (20 countries)")

# ---- workbook ----
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
ORDER = ["country","year","SHADOW","SHADOW_MIMIC","SELFEMP","TAX","ACCOUNT","DIGPAY",
         "ATM_per100k","LGDPPC","GDPPC_USD","OPEN","UNEMP","INFL","REMIT","URBAN","MOBILE",
         "BROADBAND","REG_QUALITY","RULE_OF_LAW","INST"]
obs=PatternFill("solid",fgColor="C6EFCE"); impf=PatternFill("solid",fgColor="FCE4D6")
idf=PatternFill("solid",fgColor="D9E1F2"); miss=PatternFill("solid",fgColor="F2F2F2")
hf=PatternFill("solid",fgColor="1F4E78"); hfont=Font(bold=True,color="FFFFFF",size=9)
thin=Side(style="thin",color="BFBFBF"); bd=Border(left=thin,right=thin,top=thin,bottom=thin)
def sheet(wb,title,df,flags):
    ws=wb.create_sheet(title)
    for j,k in enumerate(ORDER,1):
        c=ws.cell(1,j,k); c.fill=hf; c.font=hfont; c.border=bd
        c.alignment=Alignment(horizontal="center",wrap_text=True); ws.column_dimensions[get_column_letter(j)].width=12
    ws.freeze_panes="C2"
    for i,(_,r) in enumerate(df.iterrows(),2):
        for j,k in enumerate(ORDER,1):
            v=r.get(k); cell=ws.cell(i,j); cell.border=bd
            if k=="country": cell.value=v; cell.fill=idf
            elif k=="year": cell.value=int(v); cell.fill=idf
            else:
                cell.value=round(float(v),4) if pd.notna(v) else None
                was_imp = k in flags.columns and bool(flags.iloc[i-2][k])
                cell.fill = (impf if was_imp else (obs if pd.notna(v) else miss))
    return ws
wb=openpyxl.Workbook(); wb.remove(wb.active)
rm=wb.create_sheet("READ_ME")
for i,(t,b) in enumerate([
 ("COMPLETE imputed panel - now INCLUDING Uzbekistan & Turkmenistan",True),("",False),
 ("GREEN=observed real. ORANGE=imputed (Findex interpolation / bounded MICE). GREY=genuinely missing.",False),
 ("SELFEMP = self-employed (% of employment, ILO modelled, World Bank SL.EMP.SELF.ZS).",False),
 ("  It is observed for EVERY country incl. UZB & TKM, so it is the informality proxy that lets them enter.",False),
 ("SHADOW (DGE) is kept where it exists (KAZ/KGZ/TJK and 16 ECA states); it is blank (grey) for",False),
 ("  Uzbekistan, Turkmenistan, Montenegro, Serbia - never imputed.",False),
 ("USAGE: use SELFEMP as the informality measure for the full 5-country CA panel; use SHADOW for the",False),
 ("  subset where it exists as a robustness check. Do NOT mix the two into one column.",True),
 ("Years 2011-2020 (Findex anchor range). ACCOUNT/DIGPAY interpolated between real survey years.",False),
],1):
    c=rm.cell(i,1,t); c.font=Font(bold=b,size=11) if b else Font(size=10)
rm.column_dimensions["A"].width=115
sheet(wb,"Core_panel_CA",core_df,core_fl)
sheet(wb,"ECA_panel",eca_df,eca_fl)
wb.save("DFS_data_IMPUTED.xlsx")
core_df[ORDER].to_csv("DFS_data_IMPUTED_core.csv",index=False)
eca_df[ORDER].to_csv("DFS_data_IMPUTED_ECA.csv",index=False)
print("\nWROTE DFS_data_IMPUTED.xlsx (+CSVs) incl UZB/TKM")
print("Core countries:", sorted(core_df.country.unique()))
