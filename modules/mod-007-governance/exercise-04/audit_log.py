"""Tamper-evident audit log via SHA-256 hash chain."""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class AuditEvent:
    seq: int
    ts: float
    event_type: str
    actor: str
    payload: dict
    prev_hash: str
    this_hash: str


def _hash(event: dict) -> str:
    canonical = json.dumps(event, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(canonical).hexdigest()


class AuditChain:
    def __init__(self):
        self._events: list[AuditEvent] = []

    def append(self, event_type: str, actor: str, payload: dict) -> AuditEvent:
        seq = len(self._events)
        prev = self._events[-1].this_hash if self._events else "0" * 64
        body = {"seq": seq, "ts": time.time(), "event_type": event_type,
                 "actor": actor, "payload": payload, "prev_hash": prev}
        body["this_hash"] = _hash(body)
        ev = AuditEvent(**body)
        self._events.append(ev)
        return ev

    def verify(self) -> tuple[bool, int | None]:
        prev = "0" * 64
        for ev in self._events:
            d = asdict(ev)
            stored = d.pop("this_hash")
            if d["prev_hash"] != prev or _hash(d) != stored:
                return False, ev.seq
            prev = stored
        return True, None
