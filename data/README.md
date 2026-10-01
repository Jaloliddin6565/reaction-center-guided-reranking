# Data and large-file notes

The study starts from the public LocalMapper-remapped USPTO-50K corpus cited in the manuscript.

The study-specific retained set contains 47,517 reactions and uses record-disjoint splits:

- train: 38,013
- validation: 4,751
- test: 4,753

The split source/target SMILES files are included under `data/splits/` to make the exact Transformer split assignment explicit.

Large intermediate files are intentionally not tracked in GitHub, including:

- the ~60 MB mapped master reaction tables,
- PyTorch Geometric tensors (`train.pt`, `val.pt`, `test.pt`),
- temporary candidate-scoring tables,
- large visual audit assets.

These files can be regenerated with the notebook from the public starting corpus. Compact derived results required to verify the manuscript's numerical claims are included in `results/`.
