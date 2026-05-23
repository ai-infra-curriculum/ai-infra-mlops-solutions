"""Consistent A/B variant assignment via hashing."""
from __future__ import annotations

import hashlib


def assign(user_id: str | int, experiment_id: str, variants: dict[str, float]) -> str:
    """Same (user_id, experiment_id) → same variant. Variants must sum to 1.0."""
    h = hashlib.md5(f"{experiment_id}:{user_id}".encode()).hexdigest()
    pos = int(h[:8], 16) / 0xFFFFFFFF
    cum = 0.0
    for name, weight in variants.items():
        cum += weight
        if pos < cum:
            return name
    return next(iter(variants))


if __name__ == "__main__":
    v = {"control": 0.5, "treatment": 0.5}
    a = [assign(u, "exp1", v) for u in range(10_000)]
    b = [assign(u, "exp1", v) for u in range(10_000)]
    assert a == b                                # stability
    p_treat = sum(1 for x in a if x == "treatment") / len(a)
    assert 0.48 < p_treat < 0.52, p_treat        # split
    print(f"ok — stable + balanced ({p_treat:.3f} treatment)")
