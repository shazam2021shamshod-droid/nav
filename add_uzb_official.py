# -*- coding: utf-8 -*-
"""Add Uzbekistan's OFFICIAL shadow-economy series (% of GDP) computed from the
Uzbekistan National Statistics Committee 'hidden economy' dataset (code 1.01.08.0014,
billion soum) divided by nominal GDP (WB NY.GDP.MKTP.CN). Kept as a SEPARATE column
(SHADOW_OFFICIAL) because it is the official NOE measure, NOT comparable to the DGE series."""
import json, urllib.request
import pandas as pd

# annual totals (Q4 cumulative) from Uzbekistan Statistics Committee, billion soum
JAMI = {2010:6679.5,2011:8757.5,2012:10432.1,2013:13889.6,2014:17126.1,2015:19114.6,
        2016:22226.7,2017:25831.1,2018:34038.2,2019:46048.4,2020:45741.1,2021:62324.5,2022:76824.7}

# nominal GDP current LCU (soum) from WB
url="https://api.worldbank.org/v2/country/UZB/indicator/NY.GDP.MKTP.CN?format=json&date=2010:2022&per_page=100"
d=json.load(urllib.request.urlopen(url,timeout=40))
GDP={int(x['date']):x['value'] for x in d[1] if x['value'] is not None}   # soum

# shadow % of GDP = JAMI(bln soum) / (GDP_soum/1e9)
UZB_SHADOW = {y: round(JAMI[y] / (GDP[y]/1e9) * 100, 2) for y in JAMI if y in GDP}
print("Uzbekistan official shadow (% GDP):", {y:UZB_SHADOW[y] for y in sorted(UZB_SHADOW)})

for fn in ["DFS_data_IMPUTED_core.csv","DFS_data_IMPUTED_ECA.csv"]:
    df=pd.read_csv(fn)
    df["SHADOW_OFFICIAL"] = [UZB_SHADOW.get(int(y)) if c=="Uzbekistan" else None
                             for c,y in zip(df.country, df.year)]
    df.to_csv(fn, index=False)
    print(f"{fn}: SHADOW_OFFICIAL filled for {df['SHADOW_OFFICIAL'].notna().sum()} rows (Uzbekistan)")
