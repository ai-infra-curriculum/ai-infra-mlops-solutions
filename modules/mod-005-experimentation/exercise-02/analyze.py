"""Statistical significance + effect size for A/B results."""
from __future__ import annotations

import argparse
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats


@dataclass(frozen=True)
class Verdict:
    lift_pct: float
    welch_p: float
    mann_whitney_p: float
    cohens_d: float
    significant: bool
    direction: str


def cohen_d(a: np.ndarray, b: np.ndarray) -> float:
    return float((a.mean() - b.mean()) / np.sqrt((a.std(ddof=1)**2 + b.std(ddof=1)**2) / 2))


def analyze(control: np.ndarray, treatment: np.ndarray, alpha: float = 0.05) -> Verdict:
    t_stat, t_p = stats.ttest_ind(treatment, control, equal_var=False)
    _, u_p = stats.mannwhitneyu(treatment, control, alternative="two-sided")
    d = cohen_d(treatment, control)
    lift = (treatment.mean() - control.mean()) / control.mean() * 100 if control.mean() != 0 else 0.0
    sig = t_p < alpha
    direction = "positive" if treatment.mean() > control.mean() else "negative"
    return Verdict(lift, float(t_p), float(u_p), d, sig, direction)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--exposures", required=True, help="JSONL with {variant, metric}")
    p.add_argument("--metric", default="conversion")
    args = p.parse_args()

    df = pd.read_json(args.exposures, lines=True)
    c = df[df.variant == "control"][args.metric].dropna().to_numpy()
    t = df[df.variant == "treatment"][args.metric].dropna().to_numpy()
    v = analyze(c, t)
    print(f"control n={len(c)} mean={c.mean():.4f}")
    print(f"treatment n={len(t)} mean={t.mean():.4f}")
    print(f"lift {v.lift_pct:+.2f}%  Welch p={v.welch_p:.4f}  MW p={v.mann_whitney_p:.4f}  d={v.cohens_d:.3f}")
    print(f"{'SIGNIFICANT' if v.significant else 'not significant'} ({v.direction})")


if __name__ == "__main__":
    main()
