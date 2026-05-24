# Postmortem Template — ML Pipeline Incidents

> **Use this template for any incident that affects the customer-churn ML pipeline**: training
> failures, serving outages, drift-triggered retrains that fired in error, data-quality breaks,
> feature-skew bugs, model regressions in production, or infra-level outages of Postgres / Redis
> / MLflow / Kafka that the pipeline depends on.
>
> **Blameless.** This is about systems, not people. If a sentence in your postmortem could be
> rewritten as "the system made it easy to do the wrong thing," rewrite it that way.
>
> **Copy this file** to `docs/postmortems/YYYY-MM-DD-short-slug.md` and fill in the sections.
> Open the PR within **5 business days** of incident resolution.

---

## Header (fill before sharing the draft)

| Field                        | Value                                                                 |
|------------------------------|-----------------------------------------------------------------------|
| Incident ID                  | `INC-YYYY-NNNN`                                                       |
| Title                        | `<one-line summary, e.g. "Churn model AUC dropped 8 pp after retrain">`|
| Severity                     | SEV1 / SEV2 / SEV3 / SEV4 (see §Appendix A)                           |
| Status                       | Draft / Under review / Final                                          |
| Author                       | `@github-handle`                                                      |
| Reviewers                    | `@github-handle`, `@github-handle`                                    |
| Incident commander           | `@github-handle`                                                      |
| Detected at (UTC)            | `YYYY-MM-DD HH:MM`                                                    |
| Mitigated at (UTC)           | `YYYY-MM-DD HH:MM`                                                    |
| Resolved at (UTC)            | `YYYY-MM-DD HH:MM`                                                    |
| Total user-visible duration  | `Xh Ym`                                                               |
| Affected components          | `src/api/server.py`, `src/monitoring/drift_detection.py`, …           |
| Affected stakeholders        | API consumers / batch-prediction users / internal dashboards / …      |

---

## 1. TL;DR

Two-to-four sentences. A peer who knows nothing about the incident should be able to read
**only this section** and answer:

1. What broke?
2. Who/what was impacted, and how badly?
3. What fixed it?
4. What is the single most important follow-up?

> **Example:**
> Between 14:02 and 15:47 UTC on 2026-04-12, the `/predict` endpoint returned cached predictions
> from a model artifact that had been silently rolled back two hours earlier. Approximately
> 38,000 churn scores served during the window were 1.5 pp below the current production model's
> calibration target, leading the downstream retention-offer service to under-flag at-risk
> customers. We mitigated by flushing the Redis cache and pinning the API to the correct
> MLflow run ID. The top follow-up is to make the model-version-in-use a labeled Prometheus
> metric so the rollback would have been visible in Grafana.

---

## 2. Timeline

All times **UTC**. Include observation timestamps from the actual logs/metrics where possible,
not memory.

| Time (UTC)        | Event                                                                                  | Source           |
|-------------------|----------------------------------------------------------------------------------------|------------------|
| `YYYY-MM-DD 14:02`| Drift report flagged 12 features above PSI=0.25 threshold.                             | Evidently report |
| `14:05`           | Auto-retrain job started in MLflow (run `abc123…`).                                    | MLflow UI        |
| `14:31`           | New model artifact written to `s3://…/models/churn/2026-04-12T14-31/`.                 | S3 access log    |
| `14:33`           | API container restarted by Kubernetes liveness probe (OOM during model load).          | kubectl events   |
| `14:33`           | API came back up loading the **previous** artifact from local volume.                  | API startup log  |
| `15:21`           | First customer-success ticket: "retention offers stopped firing".                      | Zendesk #4821    |
| `15:30`           | On-call paged.                                                                         | PagerDuty        |
| `15:35`           | Hypothesis 1 (cache poisoning) discarded after checking Redis TTLs.                    | Slack thread     |
| `15:41`           | Root cause identified: API loaded stale local artifact after restart.                  | -                |
| `15:42`           | Mitigation: redeploy API pinned to MLflow run `abc123…`, flush Redis.                  | -                |
| `15:47`           | `/predict` calibration back within target. Tickets stopped.                            | Grafana          |
| `YYYY-MM-DD 17:10`| Comms sent to affected internal teams.                                                 | Slack `#mlops`   |

Conventions:

- One row per **observable** event.
- Prefer `kubectl events`, MLflow run IDs, Grafana panel links, and Slack permalinks over prose.
- Include **what was tried and discarded**, not just what worked.

---

## 3. Impact

Be quantitative. If you cannot quantify, say so explicitly — "no estimate available" is better
than a guess that calcifies into a number people cite later.

### 3.1 User-facing

- **Endpoint(s) affected:** `/predict`, `/predict/batch`
- **Request volume in window:** 38,412 predictions (Prometheus `predict_requests_total` delta).
- **Error rate:** 0% (predictions returned 200s — the failure was *semantic*, not HTTP).
- **Latency impact:** p99 unchanged.
- **Downstream effect:** Retention-offer service under-flagged ~480 high-risk customers
  (estimated from offline replay against the correct model).

### 3.2 Business

- **Revenue at risk:** ~$X (retention-offer ARPU × under-flagged count).
- **SLA / SLO impact:** Availability SLO not breached. **Prediction-quality SLO breached**
  (AUC dropped from 0.84 → 0.76 in the window; SLO is "rolling 1h AUC ≥ 0.82").
- **Customer trust:** 3 tickets, 1 escalation.

### 3.3 Internal

- **On-call hours burned:** 2.1 hours across 2 responders.
- **Data backfill required:** Yes — re-score the 38k predictions and replay into the
  retention-offer queue. Tracked as `AI-1042`.

---

## 4. Root cause analysis — 5 Whys

The 5 Whys is a forcing function to keep asking "why" past the first technical answer until
you reach a process or design root. Stop when the next "why" would be "because humans are
fallible," which is never the root cause.

> **Example walk-through:**
>
> 1. **Why** did `/predict` return stale scores?
>    Because the API loaded a previous model artifact from its local volume after a restart.
> 2. **Why** did the API load a previous artifact instead of the latest MLflow Production model?
>    Because the startup code falls back to the local cached artifact if MLflow is unreachable
>    within a 5 s timeout, and MLflow was slow during the restart.
> 3. **Why** is "silently fall back to an older model" the default behavior?
>    Because the original author optimized for API availability over correctness and did not
>    surface the chosen model version anywhere observable.
> 4. **Why** was there no observability on the chosen model version?
>    Because `src/utils/metrics.py` exposes prediction counters but not a `model_version_info`
>    gauge, and the `/model/info` endpoint is not scraped by Prometheus.
> 5. **Why** did nobody notice this gap before the incident?
>    Because the model-promotion runbook does not require a "verify the live model version
>    matches the registry" check, and our drift-detection assumes the live model is the
>    registry-Production model.

**Root cause statement** (one sentence, blameless):

> The API silently falls back to a locally cached model artifact when MLflow is slow at startup,
> and the live model version is not exposed as a metric, so a fallback is undetectable until
> downstream metrics drift.

---

## 5. Contributing factors

Things that made the incident **more likely** or **worse** but are not the root cause. List
each with a one-line description.

- **Latent bug:** The startup fallback path was added in PR #214 with a TODO to "make this a
  metric"; the TODO was never filed as an issue.
- **Process gap:** Model promotions are a single human click in MLflow; there is no required
  post-promotion verification.
- **Tooling gap:** Redis cache key does not include the model version, so cached predictions
  from any model version look identical.
- **Alerting gap:** Prediction-quality SLO is computed but the alert threshold was set to
  "AUC < 0.70" — far below the SLO target of 0.82 — so the alert never fired.
- **Documentation gap:** The on-call runbook (`docs/runbooks/api-rollback.md`) did not exist
  at the time of the incident.

---

## 6. Action items

Every action item gets an **owner**, a **due date**, an **issue link**, and a **priority**.
Action items without an owner and a date do not exist.

| #   | Priority | Action                                                                              | Owner            | Due (UTC) | Issue   |
|-----|----------|-------------------------------------------------------------------------------------|------------------|-----------|---------|
| AI-1 | P0       | Expose `model_version_info{run_id, stage}` Prometheus gauge from API at startup.    | `@alice`         | 2026-04-19| `#312`  |
| AI-2 | P0       | Include model version in Redis cache key (`predict:{model_version}:{payload_hash}`).| `@bob`           | 2026-04-19| `#313`  |
| AI-3 | P1       | Tighten prediction-quality SLO alert from AUC<0.70 to AUC<0.80.                     | `@carol`         | 2026-04-26| `#314`  |
| AI-4 | P1       | Replace silent MLflow fallback with **fail-closed** behavior (refuse to start).     | `@alice`         | 2026-05-03| `#315`  |
| AI-5 | P2       | Backfill 38k corrected scores into retention-offer queue.                           | `@dan`           | 2026-04-15| `#316`  |
| AI-6 | P2       | Write `docs/runbooks/api-rollback.md` runbook.                                      | `@erin`          | 2026-04-26| `#317`  |
| AI-7 | P3       | Add a chaos test that pauses MLflow for 30 s during API startup in CI.              | `@frank`         | 2026-05-17| `#318`  |

**Priority definitions:**

- **P0** — Prevents recurrence of this exact incident. Must ship within one week.
- **P1** — Reduces severity or detection time for the same class of incident. Within two weeks.
- **P2** — Cleanup, backfill, runbook work. Within one month.
- **P3** — Hardening or testing improvements. Within one quarter.

**Tracking discipline:** A new issue is opened for each action item *before* this postmortem
is merged. The postmortem links to the issues; the issues link back to the postmortem. A
quarterly review checks that P0/P1 items shipped on time.

---

## 7. What went well

Resist the urge to skip this section. Incidents are also a learning opportunity *about what
already works*.

- Drift detection flagged the underlying data shift before customers complained.
- The on-call rotation paged within 9 minutes of the first ticket.
- Mitigation was a config change, not a code change — rollback path worked as designed.

---

## 8. What went poorly

- The incident commander and the responder were the same person; no scribe.
- Slack thread had 4 hypotheses being debugged in parallel without a coordinating doc.
- The retention-offer team learned about the incident from this postmortem, not during the
  incident itself — comms breakdown.

---

## 9. Where we got lucky

The single most uncomfortable section, and the most valuable one. Things that *could* have
made this worse and didn't, **by luck rather than design**.

- The OOM that triggered the restart could have happened during the daily batch-prediction
  job instead of API serving; the batch job has no fallback path at all and would have failed
  silently for hours.
- The drift detector happened to run 14 minutes before the incident window opened; if it had
  run 2 hours earlier, we would have retrained against pre-drift data and the regression
  would have been even worse.
- The on-call engineer happened to have shipped PR #214 four months ago and remembered the
  fallback path. A different on-call would have spent another 30+ minutes finding it.

---

## 10. Lessons learned

Two or three sentences. Not action items — *insights*. Should be true even after every
action item in §6 has shipped.

> **Example:**
>
> Silent fallbacks are a category of bug that is invisible until it hurts. Any code path
> labeled "fall back to" deserves a metric, an alert, and a runbook before it ships. More
> broadly, "the live model version" is a first-class piece of state for an ML system and
> deserves the same observability we give to "the live database connection pool size."

---

## 11. Prevention — design changes vs process changes

Distinguish the two. Process changes (runbooks, checklists, training) decay; design changes
(metrics, fail-closed defaults, schema constraints) persist.

| Type     | Change                                                                                       | Tracked in   |
|----------|----------------------------------------------------------------------------------------------|--------------|
| Design   | Fail-closed model loading (AI-4).                                                            | `#315`       |
| Design   | Model version in cache key (AI-2) and in metrics (AI-1).                                     | `#312`, `#313` |
| Design   | Tighter SLO alert threshold (AI-3).                                                          | `#314`       |
| Design   | Chaos test for MLflow slowness (AI-7).                                                       | `#318`       |
| Process  | API rollback runbook (AI-6).                                                                 | `#317`       |
| Process  | Incident-commander/scribe split for any SEV2+ going forward.                                 | Team norms doc |

If your "Prevention" table is mostly process changes, you have probably stopped one level
short in the 5 Whys. Push for a design change.

---

## Appendix A — Severity definitions

| Sev   | Definition                                                                                    | Page on-call? | Postmortem required? |
|-------|-----------------------------------------------------------------------------------------------|---------------|----------------------|
| SEV1  | Pipeline-wide outage **or** model serving wrong answers to >1% of requests for >5 min.        | Yes, 24/7     | Yes, within 5 days   |
| SEV2  | Single component down (e.g. drift detection) **or** silent correctness degradation.           | Yes, business hours | Yes, within 5 days |
| SEV3  | Self-healed degradation, no customer impact, but worth understanding (e.g. flaky retrain).    | No            | Yes, within 10 days  |
| SEV4  | Near-miss caught by automation; documented for the trend.                                     | No            | Optional, encouraged |

## Appendix B — Concrete-example sidebar

Throughout this template, the **boxed examples** are drawn from a single illustrative incident:
the **stale-model-after-restart** incident in §1, §2, §4, and §6. Read those sections together
to see how a complete postmortem hangs together. The other sections (§3, §5, §7–§11) reference
the same incident so the cross-section feel of a real postmortem is preserved.

When you fill in your own postmortem, **delete the example boxes** but keep the section
headings and the prompts. A postmortem with empty sections is more useful than one with the
example text left in.

## Appendix C — Anti-patterns to avoid

- **"Root cause: human error."** Almost never true. Push for the system change that made the
  error easy.
- **Action items without owners.** They will not happen.
- **Action items without dates.** They will not happen on time.
- **"We will be more careful."** Not an action item.
- **Re-litigating the on-call decisions.** This is a blameless review. Discuss the system,
  not the responder.
- **Skipping the timeline.** A postmortem without a timeline is a vibe, not an artifact.
- **Skipping "Where we got lucky."** The luck is where the next incident lives.

## Appendix D — Cross-references

- Project state: [`../PROJECT_STATUS.md`](../PROJECT_STATUS.md)
- Build narrative: [`../STEP_BY_STEP.md`](../STEP_BY_STEP.md)
- Runbooks: `docs/runbooks/` (create as needed)
- Architecture (in learning repo):
  https://github.com/ai-infra-curriculum/ai-infra-mlops-learning/blob/main/projects/project-1-ml-pipeline/ARCHITECTURE.md
