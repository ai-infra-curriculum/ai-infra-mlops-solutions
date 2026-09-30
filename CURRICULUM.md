# Curriculum Guide

This document defines the expected structure for `ai-infra-mlops-solutions`.

## Repository Type

- Track type: solutions
- Paired learning repo: `ai-infra-mlops-learning`
- Primary content directories: `modules/` + `projects/`

## Top-Level Layout

- `modules/`: per-module reference solutions, mirroring the learning repo's `lessons/`
- `projects/`: full reference implementations for each capstone project
- `guides/`: cross-cutting troubleshooting + implementation notes
- `resources/`: supporting references + shared assets

## Module Minimums

Each module solution directory (`modules/NN-<slug>/`) should include:

- One subdirectory per learning exercise (`exercise-NN-<slug>/`)
- Each exercise directory has a `README.md` linking back to the learning exercise
- Working reference code/configs

## Modules

Reference solutions for the modules live under `modules/`:

- `mod-001-mlops-foundations`
- `mod-002-experiment-tracking`
- `mod-003-model-monitoring`

## Projects

Reference implementations for the capstone projects live under `projects/`:

- `project-01-ml-pipeline`
- `project-02-model-serving`
- `project-03-experimentation`
- `project-04-governance`
- `project-05-llmops`

## Structural Rules

- Module slugs MUST match the paired learning repository.
- Solutions are reference implementations; learners are expected to attempt the exercises first before consulting.
- Operational reports belong in the workspace `_meta/`, not the repo root.

## Shipped (autonomous)

Auto-appended by the AICG runner. One row per verified work item. Edit the rest of the document by hand; this section is additive only.

| Date | Work ID | Scope | Title |
|---|---|---|---|
| 2026-09-28 | `depth-mod-001-mlops-foundations-exercises` | `mod-001-mlops-foundations` | Add exercise-level depth for mod-001-mlops-foundations |
