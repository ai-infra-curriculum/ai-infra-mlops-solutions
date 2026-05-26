"""Gateway: assigns variant, routes, logs exposure."""
from __future__ import annotations

import time

import httpx
from fastapi import FastAPI
from pydantic import BaseModel

import sys
sys.path.insert(0, "../exercise-01")
from ab import assign


EXPERIMENT = "recs-v6-vs-v5-2026-05"
VARIANTS = {"control": 0.5, "treatment": 0.5}
ENDPOINTS = {
    "control":   "http://recs-v5:8000/predict",
    "treatment": "http://recs-v6:8000/predict",
}

app = FastAPI()


class Req(BaseModel):
    user_id: int
    features: list[float]


@app.post("/predict")
async def predict(req: Req):
    variant = assign(req.user_id, EXPERIMENT, VARIANTS)
    async with httpx.AsyncClient(timeout=10) as c:
        r = await c.post(ENDPOINTS[variant], json=req.dict())
    log_exposure(req.user_id, variant, r.json())
    return {"variant": variant, **r.json()}


def log_exposure(user_id: int, variant: str, response: dict):
    print({"ts": time.time(), "experiment": EXPERIMENT,
            "user_id": user_id, "variant": variant, "response": response})
