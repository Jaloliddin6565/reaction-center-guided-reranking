"""Reproducible audit of state-only reaction-center labels."""

import argparse, json
from collections import Counter
from pathlib import Path
import pandas as pd
from rdkit import Chem, RDLogger

RDLogger.DisableLog("rdApp.*")
STATE_PROPERTIES=["formal_charge","total_h","degree","hybridization","chiral_tag"]

def atom_states(smiles):
    mol=Chem.MolFromSmiles(smiles)
    if mol is None: return None
    out={}
    for atom in mol.GetAtoms():
        m=atom.GetAtomMapNum()
        if m==0: continue
        out[m]={
            "symbol":atom.GetSymbol(),
            "formal_charge":atom.GetFormalCharge(),
            "total_h":atom.GetTotalNumHs(),
            "degree":atom.GetDegree(),
            "hybridization":int(atom.GetHybridization()),
            "chiral_tag":int(atom.GetChiralTag()),
        }
    return out

def local_env(smiles):
    mol=Chem.MolFromSmiles(smiles)
    if mol is None: return None
    out={}
    for atom in mol.GetAtoms():
        m=atom.GetAtomMapNum()
        if m==0: continue
        sig=[]
        for bond in atom.GetBonds():
            nb=bond.GetOtherAtom(atom); nm=nb.GetAtomMapNum()
            nid=f"M{nm}" if nm>0 else f"U{nb.GetAtomicNum()}:{nb.GetFormalCharge()}"
            sig.append((nid,str(bond.GetBondType())))
        out[m]=sorted(sig)
    return out

def audit_one(reactants,product):
    rs,ps=atom_states(reactants),atom_states(product)
    re,pe=local_env(reactants),local_env(product)
    if any(x is None for x in [rs,ps,re,pe]):
        return {"parse_success":False}
    changed=[]; props=set(); structural=False; heavy=False
    for m in sorted(set(rs)&set(ps)):
        delta={}
        for p in STATE_PROPERTIES:
            if rs[m][p]!=ps[m][p]:
                delta[p]={"reactant":rs[m][p],"product":ps[m][p]}
                props.add(p)
        if not delta: continue
        r,p_=re[m],pe[m]
        lc=r!=p_
        if lc:
            structural=True
            removed=list((Counter(r)-Counter(p_)).elements())
            added=list((Counter(p_)-Counter(r)).elements())
            if any(not item[0].startswith("U1:") for item in removed+added):
                heavy=True
        changed.append({"map_num":int(m),"element":rs[m]["symbol"],"state_changes":delta,
                        "reactant_environment":r,"product_environment":p_,
                        "local_environment_changed":bool(lc)})
    cls="STRUCTURALLY_SUPPORTED" if heavy else ("H_ENVIRONMENT_CHANGE" if structural else "REPRESENTATION_SENSITIVE")
    return {"parse_success":True,"n_changed_atoms":len(changed),
            "changed_map_numbers":[x["map_num"] for x in changed],
            "changed_properties":sorted(props),
            "structural_support":bool(structural),"heavy_atom_support":bool(heavy),
            "audit_class":cls,"changed_atoms_detail":changed}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--master",required=True)
    p.add_argument("--sample-size",type=int,default=100)
    p.add_argument("--seed",type=int,default=42)
    p.add_argument("--outdir",default="results/state_only_audit_recomputed")
    a=p.parse_args()

    df=pd.read_csv(a.master)
    required={"mapped_reactants","mapped_product","old_n_rc","enhanced_n_rc"}
    missing=required-set(df.columns)
    if missing: raise ValueError(f"Missing columns: {sorted(missing)}")

    pool=df[(df.old_n_rc==0)&(df.enhanced_n_rc>0)]
    sample=pool.sample(n=a.sample_size,random_state=a.seed)
    records=[]
    for idx,row in sample.iterrows():
        records.append({"master_index":int(idx),**audit_one(row.mapped_reactants,row.mapped_product)})
    audit=pd.DataFrame(records)

    out=Path(a.outdir); out.mkdir(parents=True,exist_ok=True)
    audit.to_csv(out/"state_only_audit.csv",index=False)

    prop={}
    for xs in audit.loc[audit.parse_success,"changed_properties"]:
        for x in xs: prop[x]=prop.get(x,0)+1
    summary={"state_only_pool":int(len(pool)),"sample_size":int(len(sample)),"seed":a.seed,
             "parse_success":int(audit.parse_success.sum()),
             "heavy_atom_support":int(audit.heavy_atom_support.fillna(False).sum()),
             "structural_support":int(audit.structural_support.fillna(False).sum()),
             "property_counts":prop}
    (out/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))

if __name__=="__main__":
    main()
