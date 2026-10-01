# Reaction-Center-Guided Reranking of Transformer Product Predictions

Reproducibility materials for the manuscript **“Reaction-Center-Guided Reranking of Transformer Product Predictions with a Product-Conditioned Graph Neural Network.”**

## Overview

This repository contains study-specific code, compact reproducibility materials, reviewer-requested statistical analyses, and derived results used in the manuscript.

The workflow combines:

1. a SMILES Transformer for product generation,
2. a product-conditioned reaction-center GNN,
3. candidate-level reaction-center consistency descriptors,
4. a logistic reranker that fuses Transformer and GNN-derived features.

The starting corpus is the public LocalMapper-remapped USPTO-50K release. After study-specific filtering and reconciliation, **47,517 reactions** were retained in record-disjoint splits:

- Train: **38,013**
- Validation: **4,751**
- Test: **4,753**

## Final reported results

### Reaction-center GNN on held-out test atoms

- ROC-AUC: **0.997116**
- Average precision: **0.955620**
- Precision at frozen validation threshold: **0.908414**
- Recall at frozen validation threshold: **0.874455**
- F1: **0.891111**
- Confusion matrix: TN=192,767; FP=849; FN=1,209; TP=8,421

### Product prediction / reranking on 4,753 held-out reactions

| Method | Top-1 (%) | Top-3 (%) |
|---|---:|---:|
| Original Transformer beam | 32.99 | 45.34 |
| Transformer-only learned reranker | 33.75 | 45.97 |
| GNN-only learned reranker | 17.86 | 41.93 |
| Transformer + GNN | **35.37** | **46.52** |

Direct paired comparison of Transformer-only vs Transformer+GNN:

- absolute Top-1 gain: **+1.62 percentage points**
- recovered reactions: **91**
- harmed reactions: **14**
- exact two-sided McNemar p-value: **5.32 × 10⁻15**
- 10,000-resample paired-bootstrap 95% CI: **+1.20 to +2.04 percentage points**

The compact reaction-level paired outcomes required to reproduce these statistics are included in
`results/reviewer1_major4_paired_outcomes.json`.

## Reviewer-requested state-only reaction-center audit

The original bond-only definition yielded 7,503 reactions without a bond-defined reaction center. A reproducible random sample of 100 reactions (seed=42) was audited with the enhanced atom-state definition.

- Parse success: 100/100
- Heavy-atom/local structural support: 100/100
- Degree change: 100/100
- Total-H change: 100/100
- Hybridization change: 44/100
- Formal-charge change: 22/100
- Chirality change: 1/100

The reaction-level audit is included in
`results/Supplementary_Table_S1_State_Only_Reaction_Audit.csv`.

## Repository structure

- `notebooks/reaction_center_guided_reranking.ipynb` — compact reproducibility notebook
- `analysis/figure4_roc_pr_confusion.py` — ROC, precision-recall, and confusion-matrix figure utility
- `analysis/reviewer1_major2_state_only_audit.py` — state-only reaction-center audit
- `analysis/reviewer1_major4_paired_statistics.py` — exact McNemar and paired-bootstrap analysis
- `models/final_rerankers_validation_trained.joblib` — frozen validation-trained rerankers
- `results/` — final tables, summaries, reviewer analyses, and supplementary audit data
- `data/README.md` — data-source and large-file notes
- `requirements.txt` — main Python dependencies

## Reproducibility notes

Large source/intermediate datasets and PyTorch graph tensors are intentionally not duplicated in GitHub. The public starting corpus is cited in the manuscript, and the repository provides the code, compact retained results, and reviewer-requested reaction-level audit/statistical material needed to verify the principal reported numerical claims.

The final GNN classification threshold was selected on validation data and frozen before held-out test evaluation. Test results were not used for threshold tuning or reranker fitting.

## Environment

The study was executed in Google Colab using Python, RDKit, PyTorch, PyTorch Geometric, NumPy, pandas, SciPy, scikit-learn, matplotlib, joblib, tqdm, and Pillow.

Install the main dependencies with:

    pip install -r requirements.txt

## Data availability

The starting reaction corpus is the public LocalMapper-remapped USPTO-50K release cited in the manuscript. Large source and processed datasets are not redistributed here.

## Repository URL

https://github.com/Jaloliddin6565/reaction-center-guided-reranking

## Citation

If this repository is used, please cite the associated manuscript:

> Reaction-Center-Guided Reranking of Transformer Product Predictions with a Product-Conditioned Graph Neural Network.
