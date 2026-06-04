"""Thompson sampling bandit for binary-reward variants (conversion, click)."""
from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class Arm:
    name: str
    alpha: int = 1   # successes + 1 (Beta prior)
    beta: int = 1    # failures + 1


class ThompsonBandit:
    def __init__(self, arm_names: list[str]):
        self.arms = {n: Arm(n) for n in arm_names}

    def select(self) -> str:
        """Sample from each arm's Beta posterior; pick the highest."""
        samples = {n: random.betavariate(a.alpha, a.beta) for n, a in self.arms.items()}
        return max(samples, key=samples.get)

    def update(self, arm_name: str, reward: int):
        a = self.arms[arm_name]
        if reward:
            a.alpha += 1
        else:
            a.beta += 1

    def stats(self) -> dict:
        return {n: {"alpha": a.alpha, "beta": a.beta,
                     "estimated_p": a.alpha / (a.alpha + a.beta)}
                for n, a in self.arms.items()}


if __name__ == "__main__":
    random.seed(0)
    # True conversion rates: 0.05, 0.07, 0.04
    truth = {"a": 0.05, "b": 0.07, "c": 0.04}
    b = ThompsonBandit(list(truth))
    for _ in range(10_000):
        arm = b.select()
        b.update(arm, 1 if random.random() < truth[arm] else 0)

    import json
    print(json.dumps(b.stats(), indent=2))
    print("Bandit converged to:", max(b.arms, key=lambda n: b.arms[n].alpha))
