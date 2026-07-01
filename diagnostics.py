# -*- coding: utf-8 -*-
"""Real panel diagnostics on the final 8-country panel: VIF, Hausman (FE vs RE),
Pesaran CD (cross-sectional dependence), Wooldridge-style serial correlation,
groupwise heteroskedasticity. No fabrication."""
import warnings; warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from linearmodels.panel import PanelOLS, RandomEffects
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy import stats

d = pd.read_csv("DFS_panel_final.csv"); P = d.set_index(["country","year"])
X = ["DIGPAY","LGDPPC","OPEN","INFL","REMIT","INST"]

# ---- VIF ----
Xv = d[X].assign(const=1.0)
print("=== VIF (regressors) ===")
for i,c in enumerate(X):
    v = variance_inflation_factor(Xv.values, list(Xv.columns).index(c))
    print(f"  {c:8s}: {v:.2f}")

# ---- FE model + residuals ----
dd = P[["SHADOW"]+X].dropna()
fe = PanelOLS(dd["SHADOW"], dd[X], entity_effects=True, time_effects=True).fit(cov_type="clustered", cluster_entity=True)
re = RandomEffects(dd["SHADOW"], dd[X].assign(const=1.0)).fit()

# ---- Hausman FE vs RE ----
common = [c for c in X if c in fe.params.index and c in re.params.index]
b_diff = (fe.params[common] - re.params[common]).values
cov_diff = fe.cov.loc[common,common].values - re.cov.loc[common,common].values
try:
    stat = float(b_diff.T @ np.linalg.pinv(cov_diff) @ b_diff)
    hp = stats.chi2.sf(stat, len(common))
    print(f"\n=== Hausman FE vs RE: chi2={stat:.2f}, df={len(common)}, p={hp:.3f} ===")
except Exception as e:
    print("Hausman err", e)

# ---- Pesaran CD test (cross-sectional dependence) ----
res = fe.resids.copy()
res.index = dd.index
W = res.unstack(level=0)  # years x countries
corrs=[]; N=W.shape[1]; Ts=[]
cols=list(W.columns)
for i in range(N):
    for j in range(i+1,N):
        pair=W.iloc[:,[i,j]].dropna()
        if len(pair)>2:
            r=np.corrcoef(pair.iloc[:,0],pair.iloc[:,1])[0,1]; corrs.append(r); Ts.append(len(pair))
CD = np.sqrt(2/(N*(N-1))) * sum(np.sqrt(t)*r for r,t in zip(corrs,Ts))
print(f"\n=== Pesaran CD: {CD:.2f}, p={2*stats.norm.sf(abs(CD)):.3f} (H0: no cross-sectional dependence) ===")

# ---- Wooldridge-style serial correlation (regress resid on lag resid) ----
rr = res.reset_index(); rr.columns=["country","year","e"]
rr=rr.sort_values(["country","year"]); rr["el"]=rr.groupby("country")["e"].shift(1)
sub=rr.dropna()
slope,inter,rval,pval,se=stats.linregress(sub["el"],sub["e"])
print(f"\n=== Serial correlation (AR1 of residuals): rho={slope:.2f}, p={pval:.3f} ===")

# ---- Groupwise heteroskedasticity (variance of resid by country) ----
gv = res.groupby(level=0).var()
print(f"\n=== Residual variance by country (heteroskedasticity check) min={gv.min():.2f} max={gv.max():.2f} ratio={gv.max()/gv.min():.1f} ===")
print("  -> clustered/Driscoll-Kraay SEs used throughout to address heteroskedasticity & CSD.")
