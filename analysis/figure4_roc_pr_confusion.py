"""Create the manuscript ROC, precision-recall, and confusion-matrix figure.

Provide a CSV containing binary labels and reaction-center probabilities.
The threshold must be the validation-selected frozen threshold.
"""

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--label-col", default="y_true")
    p.add_argument("--prob-col", default="y_prob")
    p.add_argument("--threshold", type=float, default=0.957427)
    p.add_argument("--output", default="results/Figure4_ROC_PR_CM.png")
    args = p.parse_args()

    df = pd.read_csv(args.input)
    y_true = df[args.label_col].astype(int).to_numpy()
    y_prob = df[args.prob_col].astype(float).to_numpy()
    y_pred = (y_prob >= args.threshold).astype(int)

    fpr, tpr, _ = roc_curve(y_true, y_prob)
    pr_p, pr_r, _ = precision_recall_curve(y_true, y_prob)
    auc = roc_auc_score(y_true, y_prob)
    ap = average_precision_score(y_true, y_prob)
    precision = precision_score(y_true, y_pred, zero_division=0)
    recall = recall_score(y_true, y_pred, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)

    tn, fp, fn, tp = cm.ravel()
    fpr_thr = fp / (fp + tn)
    tpr_thr = tp / (tp + fn)
    prevalence = y_true.mean()

    fig, axes = plt.subplots(1, 3, figsize=(16.5, 5.2))

    ax = axes[0]
    ax.plot(fpr, tpr, linewidth=2.2, label=f"ROC curve (AUC = {auc:.4f})")
    ax.plot([0, 1], [0, 1], "--", linewidth=1.2, label="Random classifier")
    ax.scatter([fpr_thr], [tpr_thr], s=55, label=f"Frozen threshold = {args.threshold:.4f}")
    ax.set(xlabel="False positive rate", ylabel="True positive rate", title="(a) ROC curve")
    ax.grid(alpha=0.2)
    ax.legend(loc="lower right")

    ax = axes[1]
    ax.plot(pr_r, pr_p, linewidth=2.2, label=f"PR curve (AP = {ap:.4f})")
    ax.axhline(prevalence, linestyle="--", linewidth=1.2, label=f"Positive prevalence = {prevalence:.4f}")
    ax.scatter([recall], [precision], s=55, label=f"Frozen threshold = {args.threshold:.4f}")
    ax.set(xlabel="Recall", ylabel="Precision", title="(b) Precision–recall curve")
    ax.grid(alpha=0.2)
    ax.legend(loc="lower left")

    ax = axes[2]
    im = ax.imshow(cm, interpolation="nearest")
    ax.set_title("(c) Confusion matrix")
    ax.set_xlabel("Predicted class")
    ax.set_ylabel("True class")
    ax.set_xticks([0, 1], ["Non-RC", "RC"])
    ax.set_yticks([0, 1], ["Non-RC", "RC"])
    pct = cm / cm.sum() * 100
    for i in range(2):
        for j in range(2):
            ax.text(j, i, f"{int(cm[i,j]):,}\n({pct[i,j]:.2f}%)", ha="center", va="center", fontweight="bold")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="Number of atoms")

    fig.subplots_adjust(left=0.055, right=0.985, bottom=0.16, top=0.90, wspace=0.30)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=600, bbox_inches="tight", facecolor="white")
    print(f"saved: {out}")


if __name__ == "__main__":
    main()
