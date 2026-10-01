"""Exact paired statistics for Transformer-only vs Transformer+GNN.

By default this script uses the compact reaction-level paired outcomes stored in
results/reviewer1_major4_paired_outcomes.json, so the reported significance
test and bootstrap CI can be reproduced without large candidate tables.
"""

import argparse, base64, json
from pathlib import Path
import numpy as np
from scipy.stats import binomtest

def unpack(b64,n):
    raw=base64.b64decode(b64)
    return np.unpackbits(np.frombuffer(raw,dtype=np.uint8))[:n].astype(bool)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--paired",default="results/reviewer1_major4_paired_outcomes.json")
    p.add_argument("--bootstrap",type=int,default=10000)
    p.add_argument("--seed",type=int,default=42)
    p.add_argument("--out",default="results/reviewer1_major4_summary_recomputed.json")
    a=p.parse_args()

    d=json.loads(Path(a.paired).read_text(encoding="utf-8"))
    n=int(d["n"])
    t=unpack(d["transformer_only_correct_b64"],n)
    c=unpack(d["combined_correct_b64"],n)

    recovered=int((~t & c).sum())
    harmed=int((t & ~c).sum())
    pval=binomtest(min(recovered,harmed),recovered+harmed,0.5,alternative="two-sided").pvalue

    rng=np.random.default_rng(a.seed)
    gains=np.empty(a.bootstrap)
    tf=t.astype(float); cf=c.astype(float)
    for i in range(a.bootstrap):
        idx=rng.integers(0,n,size=n)
        gains[i]=cf[idx].mean()-tf[idx].mean()
    lo,hi=np.percentile(gains,[2.5,97.5])

    out={
        "test_reactions":n,
        "transformer_only_correct":int(t.sum()),
        "transformer_only_top1_pct":float(100*t.mean()),
        "combined_correct":int(c.sum()),
        "combined_top1_pct":float(100*c.mean()),
        "absolute_gain_pp":float(100*(c.mean()-t.mean())),
        "recovered":recovered,
        "harmed":harmed,
        "net_gain":recovered-harmed,
        "discordant_pairs":recovered+harmed,
        "mcnemar_exact_p":float(pval),
        "bootstrap_iterations":a.bootstrap,
        "gain_95ci_lower_pp":float(100*lo),
        "gain_95ci_upper_pp":float(100*hi),
        "random_seed":a.seed
    }
    Path(a.out).write_text(json.dumps(out,indent=2),encoding="utf-8")
    print(json.dumps(out,indent=2))

if __name__=="__main__":
    main()
