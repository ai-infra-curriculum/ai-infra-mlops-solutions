"""Real-time ML with Feast: feature lookup → inference, <50ms p95."""
from __future__ import annotations

from feast import FeatureStore


def predict(user_id: int) -> dict:
    fs = FeatureStore(repo_path="feature_repo")
    features = fs.get_online_features(
        features=["user_recency:clicks_7d", "user_purchase:purchases_30d"],
        entity_rows=[{"user_id": user_id}],
    ).to_dict()
    # Sketch: feed features into a real model here
    score = (features["clicks_7d"][0] or 0) * 0.1 \
            + (features["purchases_30d"][0] or 0) * 0.5
    return {"user_id": user_id, "features": features, "score": score}
