"""Compute REAL Table 3 (correlation matrix) and Table 4 (PCA diagnostics)
from the assembled open-source dataset. No fabricated numbers.
DFS_INDEX built from the 3 available components (ACCOUNT, DIGPAY, ATM_per100k);
POS terminals and cashless value are unavailable (see READ_ME), so they are omitted.
"""
import numpy as np, pandas as pd
from numpy.linalg import inv, det
from scipy import stats

def load(path):
    df = pd.read_csv(path)
    # strip header suffixes like "SHADOW (author: ...)" -> "SHADOW"
    df.columns = [str(c).split(" (")[0].strip() for c in df.columns]
    return df

core = load("DFS_data_FILLED_core.csv")
eca  = load("DFS_data_FILLED_ECA.csv")

def prep(df):
    df = df.copy()
    for c in df.columns:
        if c != "country":
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df["LGDPPC"] = np.log(df["GDPPC_USD"])
    return df

core, eca = prep(core), prep(eca)

# ---------- Table 4: PCA on the 3 available DFS components ----------
def kmo(corr):
    inv_corr = inv(corr)
    n = corr.shape[0]
    partial = np.zeros_like(corr)
    for i in range(n):
        for j in range(n):
            partial[i, j] = -inv_corr[i, j] / np.sqrt(inv_corr[i, i] * inv_corr[j, j])
    r2 = np.sum(corr**2) - n            # off-diagonal sum of squared corr
    p2 = np.sum(partial**2) - n
    kmo_all = r2 / (r2 + p2)
    return kmo_all

def bartlett(X):
    n, p = X.shape
    R = np.corrcoef(X, rowvar=False)
    chi2 = -((n - 1) - (2 * p + 5) / 6) * np.log(det(R))
    df = p * (p - 1) / 2
    pval = stats.chi2.sf(chi2, df)
    return chi2, int(df), pval, R

def pca_report(df, comps, label):
    sub = df[comps].dropna()
    n = len(sub)
    print(f"\n===== PCA ({label}) : components={comps}  N={n} =====")
    if n < 10:
        print("  Too few complete observations for a meaningful PCA.")
        return None
    X = sub.values.astype(float)
    Xz = (X - X.mean(0)) / X.std(0, ddof=1)
    chi2, dfree, pval, R = bartlett(Xz)
    kmo_all = kmo(R)
    eigval, eigvec = np.linalg.eigh(R)
    order = np.argsort(eigval)[::-1]
    eigval = eigval[order]; eigvec = eigvec[:, order]
    var_expl = eigval / eigval.sum() * 100
    pc1 = eigvec[:, 0]
    if pc1.sum() < 0:  # sign convention: positive loadings
        pc1 = -pc1
    loadings = pc1 * np.sqrt(eigval[0])
    print(f"  KMO = {kmo_all:.3f}")
    print(f"  Bartlett chi2 = {chi2:.2f}, df = {dfree}, p = {pval:.4g}")
    print(f"  Eigenvalue PC1 = {eigval[0]:.3f}  (all: {np.round(eigval,3)})")
    print(f"  Variance explained PC1 = {var_expl[0]:.1f}%")
    for c, l in zip(comps, loadings):
        print(f"    loading {c:14s} = {l:.3f}")
    # DFS index (rescaled 0-100) merged back
    scores = Xz @ pc1
    idx = (scores - scores.min()) / (scores.max() - scores.min()) * 100
    sub = sub.assign(DFS_INDEX=idx)
    return {"N": n, "KMO": kmo_all, "chi2": chi2, "df": dfree, "p": pval,
            "eig": eigval[0], "var": var_expl[0],
            "loadings": dict(zip(comps, loadings)),
            "index_rows": sub.index, "DFS_INDEX": idx}

COMPS = ["ACCOUNT", "DIGPAY", "ATM_per100k"]
pca_core = pca_report(core, COMPS, "core CA panel")
pca_eca  = pca_report(eca,  COMPS, "wider ECA panel")

# ---------- build DFS_INDEX on ECA panel and merge ----------
def attach_index(df, comps):
    sub = df[comps].dropna()
    if len(sub) < 10: return df
    X = sub.values.astype(float)
    Xz = (X - X.mean(0)) / X.std(0, ddof=1)
    R = np.corrcoef(Xz, rowvar=False)
    ev, evec = np.linalg.eigh(R)
    pc1 = evec[:, np.argmax(ev)]
    if pc1.sum() < 0: pc1 = -pc1
    scores = Xz @ pc1
    idx = (scores - scores.min()) / (scores.max() - scores.min()) * 100
    df = df.copy(); df.loc[sub.index, "DFS_INDEX"] = idx
    return df

# ---------- Table 3: correlation matrix with significance stars ----------
def star(p):
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""

def corr_table(df, vars_, label):
    df = attach_index(df, COMPS)
    print(f"\n===== Table 3 correlation matrix ({label}) =====")
    print("var pairs: lower triangle = r (stars), N")
    present = [v for v in vars_ if v in df.columns]
    for i, a in enumerate(present):
        row = []
        for j, b in enumerate(present):
            if j > i:
                row.append("        .   ")
                continue
            if a == b:
                row.append("  1.00      ")
                continue
            d = df[[a, b]].dropna()
            if len(d) < 4:
                row.append(f"  n/a(N={len(d)})")
                continue
            r, p = stats.pearsonr(d[a], d[b])
            row.append(f"{r:+.2f}{star(p):<3s}(N={len(d)})")
        print(f"  {a:10s} " + " ".join(row))
    return df

VARS = ["SHADOW", "TAX", "DFS_INDEX", "LGDPPC", "INST"]
corr_table(eca,  VARS, "wider ECA panel")
corr_table(core, VARS, "core CA panel")

# ---------- #9 standardized beta & elasticity from author's reported numbers ----------
print("\n===== #9 Standardized coefficients & elasticities (from reported Table 2 & Table 5) =====")
# reported values from the manuscript
sd = {"DFS_INDEX": 22.3, "SHADOW": 6.4, "TAX": 4.1}
mean = {"DFS_INDEX": 37.6, "SHADOW": 33.1, "TAX": 18.2}
b = {"SHADOW": -0.121, "TAX": 0.083}   # full-model FE coefficients (Table 5 cols 2 & 4)
for y in ["SHADOW", "TAX"]:
    beta = b[y] * sd["DFS_INDEX"] / sd[y]
    elas = b[y] * mean["DFS_INDEX"] / mean[y]
    print(f"  {y}: standardized beta = {beta:+.3f} ; elasticity at mean = {elas:+.3f}")
