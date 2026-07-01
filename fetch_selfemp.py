# -*- coding: utf-8 -*-
"""Fetch self-employment & vulnerable-employment (ILO modelled, via WB API) for all
ECA+CA countries and merge into the FILLED CSVs so Uzbekistan & Turkmenistan can be
included via a relative informality proxy. Real data only."""
import json, time, urllib.request
import pandas as pd

ISO = ["ALB","ARM","AZE","BLR","BIH","BGR","HRV","GEO","KAZ","KGZ","MDA","MNE",
       "MKD","ROU","RUS","SRB","TJK","TKM","UKR","UZB"]
NAME = {"ALB":"Albania","ARM":"Armenia","AZE":"Azerbaijan","BLR":"Belarus",
 "BIH":"Bosnia and Herzegovina","BGR":"Bulgaria","HRV":"Croatia","GEO":"Georgia",
 "KAZ":"Kazakhstan","KGZ":"Kyrgyz Republic","MDA":"Moldova","MNE":"Montenegro",
 "MKD":"North Macedonia","ROU":"Romania","RUS":"Russian Federation","SRB":"Serbia",
 "TJK":"Tajikistan","TKM":"Turkmenistan","UKR":"Ukraine","UZB":"Uzbekistan"}
CODES = {"SELFEMP":"SL.EMP.SELF.ZS", "VULN":"SL.EMP.VULN.ZS"}

def fetch(code):
    url=(f"https://api.worldbank.org/v2/country/{';'.join(ISO)}/indicator/{code}"
         f"?format=json&date=2004:2022&per_page=20000")
    for _ in range(3):
        try:
            d=json.load(urllib.request.urlopen(url,timeout=40))
            out={}
            if isinstance(d,list) and len(d)>1 and d[1]:
                for x in d[1]:
                    iso=x.get("countryiso3code") or x["country"]["id"]
                    if x["value"] is not None:
                        out[(iso,int(x["date"]))]=round(float(x["value"]),4)
            return out
        except Exception as e:
            print("retry:",e); time.sleep(3)
    return {}

data={k:fetch(v) for k,v in CODES.items()}
for k,v in data.items():
    print(f"{k}: {len(v)} values")
    for iso in ["UZB","TKM"]:
        ys=sorted(y for (i,y) in v if i==iso)
        print(f"   {iso}: n={len(ys)} range={ys[:1]}..{ys[-1:]}")

# merge into FILLED csvs
for panel,fn in [("core","DFS_data_FILLED_core.csv"),("ECA","DFS_data_FILLED_ECA.csv")]:
    df=pd.read_csv(fn)
    df.columns=[str(c).split(" (")[0].strip() for c in df.columns]
    iso_of={v:k for k,v in NAME.items()}
    df["_iso"]=df["country"].map(iso_of)
    for k,v in data.items():
        df[k]=[v.get((r._iso, int(r.year))) for r in df.itertuples()]
    df=df.drop(columns=["_iso"])
    df.to_csv(fn, index=False)
    print(f"merged into {fn}: SELFEMP non-null={df['SELFEMP'].notna().sum()}, VULN={df['VULN'].notna().sum()}")
