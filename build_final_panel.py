# -*- coding: utf-8 -*-
"""Final clean panel: 8 post-Soviet transition economies with the most COMPLETE data,
consistent honest sources (SHADOW = DGE for all). Central Asia (KAZ,KGZ,TJK) is the focus;
Armenia, Azerbaijan, Georgia, Belarus, Moldova provide the wider transition comparison.
Findex (ACCOUNT/DIGPAY) interpolated between real survey years; tiny residual gaps via MICE.
No fabrication."""
import numpy as np, pandas as pd
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import IterativeImputer
from sklearn.linear_model import BayesianRidge

SEL = ["Kazakhstan","Kyrgyz Republic","Tajikistan","Armenia","Azerbaijan","Georgia","Belarus","Moldova"]
Y0, Y1 = 2011, 2020

df = pd.read_csv("DFS_data_FILLED_ECA.csv")
df.columns = [str(c).split(" (")[0].strip() for c in df.columns]
for c in df.columns:
    if c != "country": df[c] = pd.to_numeric(df[c], errors="coerce")

TARGETS = ["TAX","ACCOUNT","DIGPAY","ATM_per100k","OPEN","UNEMP","INFL","REMIT",
           "URBAN","MOBILE","BROADBAND","REG_QUALITY","RULE_OF_LAW","GDPPC_USD"]
# interpolate within country over full range (uses 2021 Findex anchor for 2018-2020)
dfull = df[df.country.isin(SEL)].sort_values(["country","year"]).copy()
for c in TARGETS:
    dfull[c] = dfull.groupby("country")[c].transform(lambda s: s.interpolate(method="linear", limit_area="inside"))
d = dfull[(dfull.year>=Y0)&(dfull.year<=Y1)].copy().reset_index(drop=True)
flags = d[TARGETS].isna()

# MICE for residual gaps
feat = d[["SHADOW","SHADOW_MIMIC"]+TARGETS].copy()
feat["yr"]=d.year-d.year.mean(); feat["yr2"]=feat["yr"]**2
X = pd.concat([feat, pd.get_dummies(d.country, prefix="c").astype(float)], axis=1)
imp = IterativeImputer(estimator=BayesianRidge(), max_iter=50, sample_posterior=False, random_state=42, min_value=0)
Xi = pd.DataFrame(imp.fit_transform(X), columns=X.columns)
for c in TARGETS:
    v=d[c].copy(); m=v.isna(); v[m]=Xi[c].values[m.values]
    if c in ("ACCOUNT","DIGPAY","UNEMP","URBAN"): v=v.clip(0,100)
    elif c in ("ATM_per100k","MOBILE","BROADBAND","OPEN","INFL","REMIT","TAX","GDPPC_USD"): v=v.clip(lower=0)
    d[c]=v.values

d["LGDPPC"]=np.log(d["GDPPC_USD"])
d["INST"]=(d["REG_QUALITY"]+d["RULE_OF_LAW"])/2

# DFS_INDEX = first PC of ACCOUNT, DIGPAY, ATM (rescaled 0-100)
comps=["ACCOUNT","DIGPAY","ATM_per100k"]
Z=(d[comps]-d[comps].mean())/d[comps].std(ddof=1)
R=np.corrcoef(Z.values,rowvar=False); ev,evec=np.linalg.eigh(R)
pc1=evec[:,np.argmax(ev)]; pc1=pc1 if pc1.sum()>0 else -pc1
sc=Z.values@pc1; d["DFS_INDEX"]=((sc-sc.min())/(sc.max()-sc.min())*100).round(2)

OUT=["country","year","SHADOW","SELFEMP","DFS_INDEX","ACCOUNT","DIGPAY","ATM_per100k",
     "TAX","LGDPPC","OPEN","UNEMP","INFL","REMIT","URBAN","MOBILE","BROADBAND","INST"]
# SELFEMP may not be in this file's columns; ensure present
if "SELFEMP" not in d.columns: OUT.remove("SELFEMP")
d=d.round(3)
d[OUT].to_csv("DFS_panel_final.csv", index=False)
print("countries:", d.country.nunique(), "| rows:", len(d), "(8 x 10 = 80)")
print("missing cells (excl SHADOW_MIMIC):", int(d[OUT].isna().sum().sum()))
print("SHADOW real for all:", int(d['SHADOW'].notna().sum()), "/", len(d))
print("Findex cells interpolated (ACCOUNT/DIGPAY):", int(flags['ACCOUNT'].sum()+flags['DIGPAY'].sum()))
print("\nPCA loadings:", dict(zip(comps, (pc1*np.sqrt(ev.max())).round(3))))
