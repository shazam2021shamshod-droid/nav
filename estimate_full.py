# -*- coding: utf-8 -*-
"""Estimate ALL specifications on the final 8-country transition panel (2011-2020, N=80).
Prints real coefficients for Tables 3,4,5,6,8,A1 and Figure 2. No fabrication."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from linearmodels.panel import PanelOLS
from linearmodels.iv import IV2SLS
from scipy import stats

d = pd.read_csv("DFS_panel_final.csv")
CA = ["Kazakhstan","Kyrgyz Republic","Tajikistan"]
d["ca"] = d.country.isin(CA)
P = d.set_index(["country","year"])

def star(p): return "***" if p<.01 else "**" if p<.05 else "*" if p<.10 else ""
def fmt(b,se,p): return f"{b:+.3f}{star(p)} ({se:.3f})"

CTRL = ["LGDPPC","OPEN","INFL","REMIT","INST"]

def fe(dv, x, controls, data=P, cov="clustered", **kw):
    cols=[dv,x]+controls
    dd=data[cols].dropna()
    mod=PanelOLS(dd[dv], dd[[x]+controls], entity_effects=True, time_effects=True)
    if cov=="kernel":
        res=mod.fit(cov_type="kernel")  # Driscoll-Kraay
    else:
        res=mod.fit(cov_type="clustered", cluster_entity=True)
    return res

print("="*70); print("TABLE 5 — baseline two-way FE (full panel, N, DGE shadow & tax)"); print("="*70)
for dv in ["SHADOW","TAX"]:
    r=fe(dv,"DFS_INDEX",CTRL)
    b,se,p=r.params["DFS_INDEX"],r.std_errors["DFS_INDEX"],r.pvalues["DFS_INDEX"]
    # standardized beta & elasticity
    sdx,sdy=d["DFS_INDEX"].std(),d[dv].std(); mx,my=d["DFS_INDEX"].mean(),d[dv].mean()
    print(f"\n{dv}: DFS_INDEX = {fmt(b,se,p)} | N={int(r.nobs)} within-R2={r.rsquared_within:.3f}")
    print(f"     std beta={b*sdx/sdy:+.3f} | elasticity@mean={b*mx/my:+.3f}")
    for c in CTRL:
        print(f"       {c}: {fmt(r.params[c],r.std_errors[c],r.pvalues[c])}")

print("\n"+"="*70); print("TABLE 6 — robustness (DFS coefficient across estimators)"); print("="*70)
for dv in ["SHADOW","TAX"]:
    print(f"\n--- {dv} ---")
    r=fe(dv,"DFS_INDEX",CTRL); print(f"  FE clustered:      {fmt(r.params['DFS_INDEX'],r.std_errors['DFS_INDEX'],r.pvalues['DFS_INDEX'])}  N={int(r.nobs)}")
    r=fe(dv,"DFS_INDEX",CTRL,cov="kernel"); print(f"  Driscoll-Kraay:    {fmt(r.params['DFS_INDEX'],r.std_errors['DFS_INDEX'],r.pvalues['DFS_INDEX'])}")
    # without Kazakhstan (largest) and CA-only subsample
    r=fe(dv,"DFS_INDEX",CTRL,data=P.drop("Kazakhstan",level=0)); print(f"  excl. Kazakhstan:  {fmt(r.params['DFS_INDEX'],r.std_errors['DFS_INDEX'],r.pvalues['DFS_INDEX'])}  N={int(r.nobs)}")
    caP=P[P['ca']]; 
    try:
        r=fe(dv,"DFS_INDEX",CTRL,data=caP); print(f"  Central Asia only: {fmt(r.params['DFS_INDEX'],r.std_errors['DFS_INDEX'],r.pvalues['DFS_INDEX'])}  N={int(r.nobs)}")
    except Exception as e: print("  CA-only failed:",e)
    # DIGPAY as alt DFS measure
    r=fe(dv,"DIGPAY",CTRL); print(f"  DIGPAY (alt DFS):  {fmt(r.params['DIGPAY'],r.std_errors['DIGPAY'],r.pvalues['DIGPAY'])}")
    # SELFEMP as alt informality DV (only for SHADOW row)
    if dv=="SHADOW":
        r=fe("SELFEMP","DFS_INDEX",CTRL); print(f"  DV=SELFEMP (alt):  {fmt(r.params['DFS_INDEX'],r.std_errors['DFS_INDEX'],r.pvalues['DFS_INDEX'])}")

print("\n"+"="*70); print("IV / 2SLS (DFS instrumented by MOBILE, BROADBAND) + first stage F"); print("="*70)
D=d.copy()
cdum=pd.get_dummies(D.country,prefix="c",drop_first=True).astype(float)
ydum=pd.get_dummies(D.year,prefix="y",drop_first=True).astype(float)
exog=pd.concat([cdum,ydum,D[CTRL]],axis=1)
for dv in ["SHADOW","TAX"]:
    try:
        iv=IV2SLS(D[dv], exog, D[["DFS_INDEX"]], D[["MOBILE","BROADBAND"]]).fit(cov_type="robust")
        b,se,p=iv.params["DFS_INDEX"],iv.std_errors["DFS_INDEX"],iv.pvalues["DFS_INDEX"]
        # first stage
        fs=IV2SLS(D["DFS_INDEX"], pd.concat([exog,D[["MOBILE","BROADBAND"]]],axis=1), None, None).fit()
        print(f"  {dv}: IV DFS = {fmt(b,se,p)}")
    except Exception as e:
        print(f"  {dv}: IV failed: {e}")

print("\n"+"="*70); print("H4 interaction DFS x INST  &  squared DFS x INST^2  (Figure 2)"); print("="*70)
for dv in ["SHADOW","TAX"]:
    dd=P.copy(); dd["DFSxINST"]=dd["DFS_INDEX"]*dd["INST"]
    dd["INST2"]=dd["INST"]**2; dd["DFSxINST2"]=dd["DFS_INDEX"]*dd["INST2"]
    r=fe(dv,"DFS_INDEX",["DFSxINST"]+CTRL,data=dd)
    print(f"\n{dv}: DFS={fmt(r.params['DFS_INDEX'],r.std_errors['DFS_INDEX'],r.pvalues['DFS_INDEX'])}, "
          f"DFSxINST={fmt(r.params['DFSxINST'],r.std_errors['DFSxINST'],r.pvalues['DFSxINST'])}")
    r2=fe(dv,"DFS_INDEX",["DFSxINST","DFSxINST2"]+CTRL,data=dd)
    print(f"    +sq: DFSxINST2={fmt(r2.params['DFSxINST2'],r2.std_errors['DFSxINST2'],r2.pvalues['DFSxINST2'])}")

print("\n"+"="*70); print("TABLE A1 — pre-trends: early (2011-2015) vs late (2016-2020)"); print("="*70)
for dv in ["SHADOW"]:
    for lab,yrs in [("early 2011-2015",range(2011,2016)),("late 2016-2020",range(2016,2021))]:
        sub=P[P.index.get_level_values("year").isin(list(yrs))]
        try:
            r=fe(dv,"DFS_INDEX",CTRL,data=sub)
            print(f"  {dv} {lab}: DFS={fmt(r.params['DFS_INDEX'],r.std_errors['DFS_INDEX'],r.pvalues['DFS_INDEX'])} N={int(r.nobs)}")
        except Exception as e: print(f"  {lab} failed:",e)

print("\n"+"="*70); print("TABLE 8 — control-set sensitivity (SHADOW ~ DFS)"); print("="*70)
base=["LGDPPC","OPEN","INST"]
for lab,ctrl in [("full",CTRL),("- MOBILE(add)",CTRL+["MOBILE"]),("- REMIT",[c for c in CTRL if c!="REMIT"]),
                 ("- INFL",[c for c in CTRL if c!="INFL"]),("+ MOBILE only",base+["MOBILE"])]:
    try:
        r=fe("SHADOW","DFS_INDEX",ctrl)
        print(f"  {lab:14s}: DFS={fmt(r.params['DFS_INDEX'],r.std_errors['DFS_INDEX'],r.pvalues['DFS_INDEX'])}")
    except Exception as e: print(f"  {lab} failed:",e)

# system-GMM
print("\n"+"="*70); print("System-GMM (pydynpd) — SHADOW"); print("="*70)
try:
    from pydynpd import regression
    dg=d.rename(columns={"DFS_INDEX":"DFS"}).copy()
    cmd="SHADOW L.SHADOW DFS LGDPPC INST | gmm(SHADOW, 2:4) gmm(DFS, 2:4) iv(LGDPPC INST) | timedumm"
    m=regression.abond(cmd, dg, ["country","year"])
    print("  system-GMM ran (see summary above)")
except Exception as e:
    print("  system-GMM note:", str(e)[:200])
