# CI/CD Documentation — GitHub Actions

## 1. Overview

The repository uses **GitHub Actions** for continuous integration, model quality
gating, containerised deployment, and scheduled drift-triggered retraining.
Workflow file: `.github/workflows/ci_cd.yml`.

## 2. Pipeline Topology

```
push / PR (master, develop)          schedule: Mon 02:00 UTC
          │                                   │
          ▼                                   ▼
┌────────────────────────────────┐   ┌──────────────────┐
│  1. test (lint + unit tests)   │   │ 5. drift-check   │
└──────────────┬─────────────────┘   │    monitor.py    │
               ▼                     │    PSI analysis  │
┌────────────────────────────────┐   │    retraining?   │
│  2. validate-model             │   └───────┬──────────┘
│    preprocess → train → gate   │           │ if drift:
│    (R² ≥ 0.85, MAE ≤ 20)       │           ▼
└──────────────┬─────────────────┘   (re)run train job
               ▼
┌────────────────────────────────┐
│  3. docker-build + smoke test  │   curl /health in container
└──────────────┬─────────────────┘
               ▼
┌────────────────────────────────┐
│  4. deploy (master only)       │
└────────────────────────────────┘
```

## 3. Jobs

### 3.1 `test` — Lint & Unit Tests
Runs on every push/PR.
- Setup Python 3.11, install `config/requirements.txt`.
- `flake8` lint over `src/` (max-line-length 100, ignores E501/W503).
- `pytest src/test_pipeline.py` — 17 tests: preprocessing, training, prediction
  helper, API endpoints, batch API, drift computation.

### 3.2 `validate-model` — Quality Gate
Runs after `test`.
- Executes the real pipeline: `python src/preprocess.py`, `python src/train.py`.
- Reads `data/model_results.csv` and enforces the production gate:
  - **R² ≥ 0.85** — else FAIL, build stops.
  - **MAE ≤ 20** — else FAIL, build stops.
- Current model passes easily (R² 0.9196, MAE 14.68). A regression in model
  quality blocks the pipeline automatically.

### 3.3 `docker-build` — Image Build + Smoke Test
- Builds image from `config/Dockerfile`, tagged with commit SHA.
- Launches container, waits, `curl http://localhost:8000/health` must succeed.
- Fails the build if the API does not come up healthy.

### 3.4 `deploy` — Deployment (master only)
- `if: github.ref == 'refs/heads/master'`.
- Production deploy hook (push image to registry + restart service). The actual
  target environment is wired at deployment time; the CI already validates the
  artifact end-to-end.

### 3.5 `drift-check` — Scheduled Monitoring & Retraining
- Triggered only by the weekly `schedule` cron (Mon 02:00 UTC).
- Runs `src/monitor.py`, which computes PSI for 4 lag features over the last 30
  days vs. the training baseline.
- If `retraining_needed` is true (any feature PSI ≥ 0.2), the job reports drift
  and the retraining job is triggered — completing the monitor → retrain
  automation loop.

## 4. Automation Summary

| Automation | Mechanism |
|------------|-----------|
| Automated testing | `test` job on every push/PR |
| Model quality gate | `validate-model` (R²/MAE thresholds) |
| Container build check | `docker-build` smoke test |
| Automated deployment | `deploy` on master |
| Automated retraining | weekly `drift-check` + retrain trigger |
| Drift detection | PSI via `src/monitor.py` |