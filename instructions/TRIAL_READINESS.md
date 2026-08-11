# Trial-readiness contract

## Objective

After the researcher selects one or more candidates, determine what would be
required to design a bounded evaluation. This stage plans; it does not acquire
or execute anything.

Assess each selected candidate separately. Do not assume that two tools sharing
a scientific role share an artifact, adapter, licence, environment, oracle, or
governance route.

## Required readiness dimensions

- exact candidate and artifact/service identity;
- version, release, commit or endpoint identity;
- access route and licence terms;
- input and output semantics;
- adapter or integration requirements;
- dependencies and environment;
- local, container, notebook, API, browser, HPC or institutional route;
- CPU, RAM, storage, walltime, GPU and network needs;
- account, telemetry, data location, cost and institutional ownership;
- procedural synthetic fixture design;
- independent scientific and technical oracle;
- evidence to capture, stop conditions and unresolved blockers.

## Readiness states

- `mapped_no_known_blocker` — the present evidence exposes no blocker, but this
  is not acquisition or execution approval;
- `mapped_with_open_requirements` — a route is plausible but material fields
  remain unresolved;
- `blocked` — current evidence identifies a hard conflict or missing authority;
- `not_assessed` — insufficient evidence to map the dimension honestly.

Unknown is not equivalent to acceptable.

## Required output

Create `readiness-plan.md` containing:

1. selected candidate and source-bound identity;
2. proposed route or alternative routes;
3. dimension-by-dimension readiness table with owners and evidence;
4. blockers, open requirements and assumptions;
5. a procedural synthetic evaluation concept;
6. the oracle and success/failure criteria;
7. decisions that remain with the researcher or institution; and
8. an explicit statement that acquisition and execution remain outside this
   pilot.

Do not download, install, import, run, submit, authenticate, spend, schedule an
institutional job, or ask for real data while producing this plan.
