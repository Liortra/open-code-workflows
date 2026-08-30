# Open Code Workflows

A reusable set of **role-based pipelines** for building web apps with an agentic coding assistant. Given a short seed concept, the workflows drive a staged build with human checkpoints through clearly separated roles: concept (human-supplied), feature decomposition, feature briefs, system engineering, architecture, backend, frontend, verification, and documentation.

Designed and validated in [OpenCode](https://opencode.ai) with DeepSeek V4 Flash, but the workflows are **model- and agent-agnostic**. They should generalize to any agentic coding tool that can spawn and resume sub-agents (see "Generalizability" below).

## Repo layout

```
instructions/
├── build/          build a new app from scratch (stages 01–09)
├── enhancements/   add features to an existing app (stages 01–10)
├── debug/          investigate, fix, verify a bug (stages 01–03)
└── meta/           the Stage Manager orchestrator that runs the pipelines
concept-examples/   seed concepts to copy as a starting point
```

Each pipeline has an authoritative `00-README.md` plus one instruction file per role. The `meta/00-stage-manager.md` role sequences, dispatches, gates, and audits each stage.

## Prerequisites

- A git repo with an `origin` remote (each stage commits and pushes per-stage).
- An agentic-exec platform that can **spawn and resume sub-agents** and offer a writable agent type. See `instructions/meta/00-stage-manager.md` → "Executor model" for the capability requirements and how the workflows degrade gracefully if a capability is missing.

## Steps to get started

1. **Copy a seed concept** to your project root as `concept.md`:
   ```
   cp ./concept-examples/concept-language-tutor.md ./concept.md
   ```
2. **Customize `concept.md`** — make any updates or adjustments to fit your needs.
3. **Create an OpenCode Project** in the root of your project folder.
4. **Start a new Agent session** and select "DeepSeek V4 Flash" (or another capable model).
5. **Bootstrap the Stage Manager** by giving the model this instruction:
   ```
   Read the file instructions/meta/00-stage-manager.md - you will assume the
   Stage Manager role for this session.
   ```
6. **Kick off the build** — have the Stage Manager analyze your `concept.md` and run a `build` workflow, spawning a sub-agent for each stage/role. Build Stage 1 is a human role: it is skipped if `concept.md` already exists (the common case) and otherwise prompts you to brainstorm and produce it.
7. **Answer questions** — the Stage Manager relays any clarifications it needs, along with its own suggestions on how to proceed.
8. **Run the app** once the build completes:
   ```
   bash install.sh && bash run.sh
   ```
   then open a web browser to the port `run.sh` starts (FastAPI defaults to `http://localhost:8000`).

## Bootstrap a new project

1. **Create a project workspace** — a new git repo + branch for the target app.
2. **Bring in the workflows** — copy the `instructions/` tree into the project root (and `.gitignore` as a starting point).
3. **Seed the concept** — place a `concept.md` in the project root. Copy one from `concept-examples/` and edit it, or write your own. If you skip this, build Stage 1 will prompt you to brainstorm and create it.
4. **Run the build pipeline** — have the Stage Manager orchestrate `build` stages 01→09, dispatching a sub-agent per stage. Stage 1 is a human role (skipped when the seed exists). The build progressively produces:

   ```
   concept.md              (stage 1, human-supplied)
   features/*.md            (stage 2)
   features/briefs/*.md     (stage 3)
   requirements.txt, install.sh, run.sh, .gitignore, environment-notes.md  (stage 4)
   docs/architecture.md     (stage 5)
   backend/                 (stage 6)
   frontend/                (stage 7)
   docs/verification-report.md  (stage 8)
   README.md                (stage 9)
   ```

   Each stage writes a summary into its pipeline's `summaries/` folder, then commits (`stage <NN>: <brief summary>`) and pushes to `origin` as its final step. See the pipeline's `00-README.md` for the authoritative conventions.

## Choosing a pipeline

| Pipeline       | Use when                                                          |
|----------------|-------------------------------------------------------------------|
| `build`        | Building a new app from a seed concept (stages 01–09).            |
| `enhancements` | Adding new features to an already-built app (stages 01–10).       |
| `debug`        | Investigating, fixing, and verifying a bug (stages 01–03, gated). |

## Choosing a seed concept

The `concept-examples/` folder provides ready-made starting points. Each follows the same template: product identity, a default baseline stack (Web App / Bootstrap frontend / FastAPI+SQLite backend), app-appropriate basic seed data, and enumerated major capabilities. A concept should **shape the app** without **constraining its development** — enough for downstream roles to build coherently, but no pre-decided data model (no entities, fields, status lists, schemas, or API contracts; those belong to later stages):

- `concept-language-tutor.md` — English/Spanish language tutor
- `concept-job-tracker.md` — job applications, companies, contacts, stages
- `concept-client-project-tracker.md` — clients, projects, time entries, billing
- `concept-sales-inventory-tracker.md` — second-hand sales & inventory
- `concept-plant-nursery.md` — plant nursery / batch inventory / sales
- `concept-capstone-project.md` — thesis/capstone research & document tracker

Copy any of these to `concept.md` and edit to fit your product, or author your own from scratch. You own `concept.md` — edit it directly whenever you like, including substituting a different stack (e.g. MDL + Django + Postgres) or adjusting the seed data.

## Conventions & handoff chain

The build follows a fixed artifact chain — each role's output becomes the next role's input:

```
concept → features → briefs → env scripts → architecture → backend → frontend → verification → README
```

Common conventions across pipelines:

- Each role writes a summary to its pipeline's `summaries/` folder before handing off.
- Each stage commits and pushes as its **final** step (`stage <NN>: ...`, `debug <NN>: ...`).
- Temporary files and logs go in the gitignored `./tmp/` folder, never the OS temp dir.
- Roles do not reach backward or forward past their own stage.

## Generalizability

These workflows were designed and validated in OpenCode with DeepSeek V4 Flash, but they are written as plain markdown instructions and should work with other models and agentic apps. The main caveats are **platform capabilities**, not model choice:

- Whether the platform can spawn and **resume** sub-agents by id (the Stage Manager prefers resuming the same sub-agent per stage).
- Whether it offers a **writable** sub-agent type so a stage can create its artifacts and commit/push.

If a capability is unavailable, the Stage Manager surfaces the limitation and confirms how to proceed rather than guessing — see `instructions/meta/00-stage-manager.md` → "Executor model".