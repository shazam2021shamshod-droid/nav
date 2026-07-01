# -*- coding: utf-8 -*-
"""Run REAL panel regressions on the assembled open-source data.
Reports actual estimates (no fabrication). Prints diagnostics so we can see
what is estimable given data coverage before writing numbers into the manuscript.
"""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from linearmodels.panel import PanelOLS
from linearmodels.iv import IV2SLS
from scipy import stats

def load(path):
    df = pd.read_csv(path)
    df.columns = [str(c).split(" (")[0].strip() for c in df.columns]
    for c in df.columns:
        if c != "country":
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df["LGDPPC"] = np.log(df["GDPPC_USD"])
    return df

def build_dfs(df, comps=("ACCOUNT","DIGPAY","ATM_per100k")):
    comps=list(comps); sub=df[comps].dropna()
    if len(sub)>=10:
        X=sub.values.astype(float); Xz=(X-X.mean(0))/X.std(0,ddof=1)
        R=np.corrcoef(Xz,rowvar=False); ev,evec=np.linalg.eigh(R)
        pc1=evec[:,np.argmax(ev)]; pc1=pc1 if pc1.sum()>0 else -pc1
        s=Xz@pc1; idx=(s-s.min())/(s.max()-s.min())*100
        df.loc[sub.index,"DFS_INDEX"]=idx
    # annual single-indicator proxy (rescaled ATM density 0-100)
    a=df["ATM_per100k"]; df["DFS_ATM"]=(a-a.min())/(a.max()-a.min())*100
    return df

def coverage(df, cols, label):
    print(f"\n[{label}] non-missing counts:")
    for c in cols:
        if c in df: print(f"   {c:12s}: {df[c].notna().sum()}")

def fe(df, dv, dfs, controls, label):
    cols=["country","year",dv,dfs]+controls
    d=df[cols].dropna().copy()
    if d["country"].nunique()<2 or len(d)<15:
        print(f"   {label}: not estimable (N={len(d)}, groups={d['country'].nunique()})"); return None
    d=d.set_index(["country","year"])
    try:
        mod=PanelOLS(d[dv], d[[dfs]+controls], entity_effects=True, time_effects=True)
        res=mod.fit(cov_type="clustered", cluster_entity=True)
        b=res.params[dfs]; se=res.std_errors[dfs]; p=res.pvalues[dfs]
        print(f"   {label}: {dfs}={b:+.4f} (se={se:.4f}, p={p:.3f}), N={int(res.nobs)}, within R2={res.rsquared_within:.3f}")
        return res
    except Exception as e:
        print(f"   {label}: FAILED {e}"); return None

CTRLS=["LGDPPC","OPEN","REMIT","INFL","INST"]

for path,label in [("DFS_data_FILLED_ECA.csv","ECA PANEL"),("DFS_data_FILLED_core.csv","CORE CA PANEL")]:
    df=build_dfs(load(path))
    print("="*60); print(label); print("="*60)
    coverage(df,["SHADOW","TAX","DFS_INDEX","DFS_ATM"]+CTRLS,label)
    print(" -- SHADOW equation --")
    fe(df,"SHADOW","DFS_INDEX",CTRLS,"FE Findex-composite")
    fe(df,"SHADOW","DFS_ATM",CTRLS,"FE ATM-density (annual)")
    print(" -- TAX equation --")
    fe(df,"TAX","DFS_INDEX",CTRLS,"FE Findex-composite")
    fe(df,"TAX","DFS_ATM",CTRLS,"FE ATM-density (annual)")
