# Model Card: iris-rf v6 (sample, auto-generated)

## Owners
- Engineering: alice@example.com
- Product:     bob@example.com
- DS lead:     carol@example.com

## Intended use
Classify iris flower species from 4 morphometric features.

## Out of scope
Any species not in {setosa, versicolor, virginica}; non-flower images.

## Training data
- Source: sklearn.datasets.load_iris (canonical 1936 dataset)
- Window: static
- Row count: 150
- Known biases: small dataset; geographically biased to Pacific Northwest

## Architecture
- Algorithm: RandomForestClassifier
- Hyperparameters: n_estimators=200, max_depth=12, random_state=0
- Training compute: CPU; <1 second

## Performance
- accuracy: 0.967
- per-class accuracy:
  - setosa: 1.000
  - versicolor: 0.933
  - virginica: 0.967

## Fairness
- N/A — no protected attributes in this dataset.

## Approvals
- Eng:        ✓ 2026-05-23 (alice)
- Compliance: ✓ 2026-05-23 (legal-bot via low-risk path)
- DS:         ✓ 2026-05-23 (carol)

## Change log
- 2026-05-23: v6 — bumped n_estimators from 100 to 200; +0.4pp accuracy
- 2026-04-01: v5 — initial production version
