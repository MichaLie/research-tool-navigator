# Trial-readiness contract

## Objective

After the researcher selects one or more candidates, determine what would be
required to design a bounded evaluation. This stage plans; it does not acquire
or execute anything.

Assess each selected candidate separately. Do not assume that two tools sharing
a scientific role share an artifact, adapter, licence, environment, oracle, or
governance route.

## Trial route triage

Open the readiness plan by classifying how a bounded synthetic evaluation of
the candidate could be carried out. Assign every plausible route one of five
classes:

| Route class | Meaning |
|---|---|
| `hosted_free` | a public service or free tier could accept a synthetic fixture from the researcher |
| `hosted_paid` | a hosted service could accept one only under a paid plan or metered account |
| `local_workstation` | a pinned artifact could run on a researcher-controlled computer |
| `institutional_compute` | requirements exceed a workstation; an institutional route (e-INFRA CZ / MetaCentrum class) would be required |
| `not_currently_runnable` | no route exists today: paper-only, artifact unavailable, access-gated without an open request path, or deprecated |

Rules:

- List every route the evidence supports, ordered by increasing requirement
  burden. Do not collapse to a single route by preference; a candidate may be
  both `hosted_free` and `local_workstation`.
- For each route record the exact artifact or endpoint identity; account and
  licence conditions for evaluation use; the compute floor (CPU, GPU, RAM,
  disk) and network needs; and, for hosted routes, unresolved governance
  items such as data retention, telemetry, and deployed-version identity.
- Mark every requirement value with its basis: `stated_by_author`,
  `derived_from_artifacts`, `reported_by_users`, or `unknown`. Never replace
  a missing value with a plausible number; `unknown` is the honest value.
- For `hosted_paid`, record an observed price basis with source and date.
  Prices are observations, not guarantees.
- Name a delegation owner for each route's next non-executing step:
  `researcher`, `group_developer`, `e_infra_contact`, `institution`, or
  `author_contact`.
- Compare each route's data destination with the confirmed profile's intended
  data classification and record a production-fit note: a synthetic trial may
  be feasible on a route that the researcher's real data could never use.
- A triage verdict describes; it authorizes nothing. "The researcher could
  submit a synthetic fixture to this service" is a statement this contract
  may make; the assistant submitting anything is outside this pilot.

## Required readiness dimensions

The triage surveys every plausible route. The dimensions below are then
mapped in depth for the route or routes the researcher asks to examine.

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
2. the trial route triage across all plausible routes;
3. dimension-by-dimension readiness table with owners and evidence;
4. blockers, open requirements and assumptions;
5. a procedural synthetic evaluation concept;
6. the oracle and success/failure criteria;
7. decisions that remain with the researcher or institution; and
8. an explicit statement that acquisition and execution remain outside this
   pilot.

Do not download, install, import, run, submit, authenticate, spend, schedule an
institutional job, or ask for real data while producing this plan.
