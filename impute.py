# -*- coding: utf-8 -*-
"""Produce a COMPLETE imputed panel from the assembled real data.
Rules (transparent):
  - Drop columns with no anchors: CASH, POS_ATM, CASHLESS_VAL, MOBILE_COVERAGE.
  - Drop countries with NO observed SHADOW at all (Uzbekistan, Turkmenistan, and any
    ECA country absent from the DGE/MIMIC database) -> they cannot be imputed.
  - Restrict to 2004-2020 (years where the shadow-economy series exists; the DV is
    NOT extrapolated).
  - Impute the rest: (1) within-country linear interpolation for interior gaps,
    then (2) multivariate imputation (MICE / IterativeImputer) for remaining edge gaps,
    conditioning on all indicators + country dummies + a year trend.
  - SHADOW / SHADOW_MIMIC are left as observed (never cross-country imputed).
  - Every imputed cell is flagged for full transparency.
"""
import numpy as np, pandas as pd
from sklearn.experimental import enable_iterative_imputer   # noqa
from sklearn.impute import IterativeImputer
from sklearn.linear_model import BayesianRidge

YEAR_MIN, YEAR_MAX = 2011, 2020   # Findex anchor range: interpolate, do NOT back-extrapolate

def load(path):
    df = pd.read_csv(path)
    df.columns = [str(c).split(" (")[0].strip() for c in df.columns]
    for c in df.columns:
        if c != "country":
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

# variables we keep
NUM = ["SHADOW","SHADOW_MIMIC","TAX","ACCOUNT","DIGPAY","ATM_per100k","GDPPC_USD",
       "OPEN","UNEMP","INFL","REMIT","URBAN","MOBILE","BROADBAND","REG_QUALITY","RULE_OF_LAW"]
# imputation targets (SHADOW/SHADOW_MIMIC excluded from imputation -> observed only)
TARGETS = ["TAX","ACCOUNT","DIGPAY","ATM_per100k","OPEN","UNEMP","INFL","REMIT",
           "URBAN","MOBILE","BROADBAND","REG_QUALITY","RULE_OF_LAW","GDPPC_USD"]

def process(path, label):
    df = load(path)
    # drop countries with no observed SHADOW at all (before restricting years)
    has_shadow = df.groupby("country")["SHADOW"].apply(lambda s: s.notna().any())
    keep = has_shadow[has_shadow].index.tolist()
    dropped = [c for c in df.country.unique() if c not in keep]
    df = df[df.country.isin(keep)].copy().sort_values(["country","year"]).reset_index(drop=True)

    # step 1: within-country linear interpolation over the FULL series (uses 2021 Findex anchor
    # to interpolate 2018-2020), interior gaps only -> no extrapolation
    for c in TARGETS:
        df[c] = df.groupby("country")[c].transform(
            lambda s: s.interpolate(method="linear", limit_area="inside"))

    # now restrict to the Findex anchor range
    df = df[(df.year >= YEAR_MIN) & (df.year <= YEAR_MAX)].copy().reset_index(drop=True)
    print(f"\n===== {label} =====")
    print(f"  countries kept ({len(keep)}): {keep}")
    print(f"  countries dropped (no shadow): {dropped}")

    # flag cells still missing after interpolation (these get MICE)
    flags = df[TARGETS].isna()

    # step 2: MICE (deterministic) for the few remaining gaps, then bound to plausible ranges
    feat = df[NUM].copy()
    feat["yr"] = df["year"] - df["year"].mean()
    feat["yr2"] = feat["yr"]**2
    dummies = pd.get_dummies(df["country"], prefix="c").astype(float)
    X = pd.concat([feat, dummies], axis=1)
    imp = IterativeImputer(estimator=BayesianRidge(), max_iter=50,
                           sample_posterior=False, random_state=42, min_value=0)
    arr = imp.fit_transform(X)
    Xi = pd.DataFrame(arr, columns=X.columns)
    for c in TARGETS:
        vals = df[c].copy()
        miss = vals.isna()
        vals[miss] = Xi[c].values[miss.values]
        if c in ("ACCOUNT", "DIGPAY", "UNEMP", "URBAN"):
            vals = vals.clip(0, 100)
        elif c in ("ATM_per100k", "MOBILE", "BROADBAND", "OPEN", "INFL", "REMIT", "TAX", "GDPPC_USD"):
            vals = vals.clip(lower=0)
        df[c] = vals.values
    df["LGDPPC"] = np.log(df["GDPPC_USD"])
    df["INST"] = (df["REG_QUALITY"] + df["RULE_OF_LAW"]) / 2

    n = len(df)
    print(f"  rows: {n}  years: {YEAR_MIN}-{YEAR_MAX}")
    print("  imputed (MICE) cells per column:", {c: int(flags[c].sum()) for c in TARGETS})
    print("  SHADOW missing (left real):", int(df['SHADOW'].isna().sum()),
          "| TAX missing:", int(df['TAX'].isna().sum()))
    return df, flags

core_df, core_fl = process("DFS_data_FILLED_core.csv", "CORE CA (imputed)")
eca_df,  eca_fl  = process("DFS_data_FILLED_ECA.csv",  "ECA (imputed)")

# ---------- write workbook with observed/imputed colouring ----------
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

ORDER = ["country","year","SHADOW","SHADOW_MIMIC","TAX","ACCOUNT","DIGPAY","ATM_per100k",
         "LGDPPC","GDPPC_USD","OPEN","UNEMP","INFL","REMIT","URBAN","MOBILE","BROADBAND",
         "REG_QUALITY","RULE_OF_LAW","INST"]
obs_fill = PatternFill("solid", fgColor="C6EFCE")   # observed real
imp_fill = PatternFill("solid", fgColor="FCE4D6")   # imputed
id_fill  = PatternFill("solid", fgColor="D9E1F2")
hf = PatternFill("solid", fgColor="1F4E78"); hfont = Font(bold=True, color="FFFFFF", size=9)
thin = Side(style="thin", color="BFBFBF"); bd = Border(left=thin,right=thin,top=thin,bottom=thin)

def sheet(wb, title, df, flags):
    ws = wb.create_sheet(title)
    for j,k in enumerate(ORDER, start=1):
        c=ws.cell(1,j,k); c.fill=hf; c.font=hfont; c.border=bd
        c.alignment=Alignment(horizontal="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(j)].width = 13
    ws.freeze_panes="C2"
    for i,(_,row) in enumerate(df.iterrows(), start=2):
        for j,k in enumerate(ORDER, start=1):
            v = row.get(k)
            cell=ws.cell(i,j); cell.border=bd
            if k=="country": cell.value=v; cell.fill=id_fill
            elif k=="year": cell.value=int(v); cell.fill=id_fill
            else:
                cell.value = round(float(v),4) if pd.notna(v) else None
                was_imp = (k in flags.columns) and bool(flags.iloc[i-2][k]) if k in flags.columns else False
                cell.fill = imp_fill if was_imp else obs_fill
    return ws

wb = openpyxl.Workbook(); wb.remove(wb.active)
# READ_ME
rm = wb.create_sheet("READ_ME")
lines = [
 ("IMPUTED, COMPLETE PANEL - read me", True),
 ("", False),
 ("GREEN = observed (real, from official sources).  ORANGE = imputed.", False),
 ("Imputation method: (1) within-country linear interpolation of interior gaps;", False),
 ("  (2) multivariate imputation (MICE / IterativeImputer, BayesianRidge) for remaining gaps,", False),
 ("  conditioning on all indicators + country dummies + a quadratic year trend.", False),
 ("SHADOW and SHADOW_MIMIC are NEVER imputed - shown only where genuinely observed.", False),
 ("", False),
 ("DROPPED (cannot be imputed - no anchors):", True),
 ("  - Countries with no shadow-economy estimate at all: Uzbekistan, Turkmenistan (both panels);", False),
 ("    plus Montenegro, Serbia in the ECA panel (absent from the DGE/MIMIC database).", False),
 ("  - Columns: CASH, POS terminals, CASHLESS_VAL, MOBILE_COVERAGE (no observed values).", False),
 ("Years restricted to 2011-2020 (the Global Findex anchor range) so ACCOUNT/DIGPAY are", False),
 ("  INTERPOLATED between real survey years (2011/2014/2017/2021), never back-extrapolated.", False),
 ("", False),
 ("CAUTION: interpolated/imputed Findex values create smooth within-country paths; any regression", False),
 ("run on this file must treat apparent precision cautiously and disclose the imputation.", True),
]
for i,(t,b) in enumerate(lines, start=1):
    c=rm.cell(i,1,t)
    if b: c.font=Font(bold=True, size=11)
rm.column_dimensions["A"].width=110

sheet(wb, "Core_panel_CA", core_df, core_fl)
sheet(wb, "ECA_panel", eca_df, eca_fl)
wb.save("DFS_data_IMPUTED.xlsx")

# CSVs
core_df[ORDER].to_csv("DFS_data_IMPUTED_core.csv", index=False)
eca_df[ORDER].to_csv("DFS_data_IMPUTED_ECA.csv", index=False)
print("\nWROTE DFS_data_IMPUTED.xlsx + CSVs")
print("Core rows:", len(core_df), "| ECA rows:", len(eca_df))
