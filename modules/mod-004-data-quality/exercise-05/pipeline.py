"""End-to-end DQ pipeline: schema → GE → stats → profile diff."""
from __future__ import annotations

import sys
sys.path.insert(0, "../exercise-01")
sys.path.insert(0, "../exercise-03")
sys.path.insert(0, "../exercise-04")

import pandas as pd

from schema import UserEvent, validate_batch
from stats_checks import report as stats_report
from profile import profile, diff_profiles


def run(current_rows: list[dict], reference_df: pd.DataFrame) -> dict:
    # 1. Schema (Pydantic)
    valid, errors = validate_batch(current_rows, UserEvent)
    if errors:
        return {"status": "fail", "stage": "schema", "errors": errors[:20]}

    cur_df = pd.DataFrame([v.dict() for v in valid])

    # 2. Statistical checks
    stats = stats_report(cur_df, ref=reference_df)
    if (stats["null_rate"] > 0.1).any():
        return {"status": "fail", "stage": "null_rate", "report": stats.to_dict(orient="records")}

    # 3. Profile diff vs reference
    deltas = diff_profiles(profile(reference_df), profile(cur_df))
    if any("mean_shift_sigma" in d and abs(d["mean_shift_sigma"]) > 3 for d in deltas):
        return {"status": "warn", "stage": "drift", "deltas": deltas}

    return {"status": "ok", "rows_validated": len(valid)}


if __name__ == "__main__":
    import json
    sample = [{"user_id": 1, "event_ts": "2026-05-23T10:00:00", "event_type": "click",
                "item_id": "abc", "price": 10.0,
                "session_id": "a" * 32}]
    ref = pd.DataFrame(sample)
    print(json.dumps(run(sample, ref), indent=2))
