# Research Tool Navigator

Local, expert-mediated pilot for turning a researcher's ordinary-language tool
need into an evidence-backed candidate comparison and, when requested, a
trial-readiness plan.

The scope is narrow by design:

> Describe a research task; receive a transparent set of relevant candidate
> tools, the evidence and uncertainty attached to each, and a clear account of
> what would be required to evaluate the candidates you choose.

## What the pilot provides

The pilot provides:

1. a workspace instruction contract for the researcher conversation;
2. a concise research-interview protocol;
3. a confirmed metadata-only query profile;
4. deterministic read-only retrieval across the three sibling catalogues;
5. transparent retrieval explanations and catalogue provenance;
6. a criterion-wise candidate-comparison protocol; and
7. an optional trial-readiness protocol after researcher selection.

It does **not** acquire, install, run, rank a winner, submit data, use private
accounts, or authorize scientific or institutional use. No API key or deployed
service is required for this pilot.

## Use it with an agentic assistant

Requirements: any agentic coding assistant that reads `AGENTS.md`, plus local
Python 3. No API keys, no installs, no network beyond optionally fetching the
published catalogues.

Open this folder as the workspace and start with a normal request such as:

> I need a research tool that can perform [scientific operation] and produce
> [intended output] under [important constraints].

The assistant reads `AGENTS.md` (`CLAUDE.md` points there for tools that use
it), conducts the short interview, shows the interpreted query profile for
confirmation, calls the deterministic catalogue search, and then prepares the
comparison. The front door accepts any **metadata-only research-tool need**;
it may legitimately return no catalogue candidates.

The pilot was developed and exercised with one assistant (OpenAI Codex) and
audited with another (Claude Code); the contracts themselves are plain
Markdown and deterministic Python with no tool-specific dependency.

## Local commands

Show the bound live catalogue snapshots:

```bash
python3 scripts/navigator.py stats
```

Validate a confirmed query profile:

```bash
python3 scripts/navigator.py validate-profile path/to/query-profile.json
```

Search the three sibling catalogues:

```bash
python3 scripts/navigator.py search \
  --profile path/to/query-profile.json \
  --output runs/<request-id>/retrieval-results.json
```

Run the install-free regression suite:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

## Standalone use

The navigator normally reads the three catalogues from sibling checkouts. A
standalone clone can instead download the published FAIR distributions and
pass explicit paths:

```bash
python3 scripts/fetch_catalogues.py
```

The script stores the files under `catalogues/` (gitignored), prints their
SHA-256 hashes, and shows the matching `navigator.py search` command. The
published distributions may differ from any local sibling checkout; the hashes
recorded in every result package identify exactly what was searched.

The numeric `retrieval_score` orders search results only. It is not a
suitability score, scientific assessment, or recommendation.

## Project map

```text
AGENTS.md                         the governing workspace contract
CLAUDE.md                         pointer to AGENTS.md for tools that read it
instructions/RESEARCH_INTERVIEW.md
instructions/CANDIDATE_DISCOVERY.md
instructions/TRIAL_READINESS.md
schemas/query-profile.schema.json
scripts/navigator.py              read-only deterministic catalogue search
scripts/fetch_catalogues.py       fetch published catalogues for standalone use
tests/                            synthetic regression fixtures and tests
docs/PRODUCT_SPEC.md              pilot scope and boundaries
docs/ARCHITECTURE.md              one-assistant architecture
evals/                            unseen-query evaluation protocol
templates/                        comparison and readiness output contracts
runs/                             gitignored per-query working packages
```

The three source catalogues remain read-only siblings:

- `../Foundation_models/models_final.json`
- `../Autonomous_Agents/agents_final.json`
- `../Coding_Agents/tools.json`

## Status

This is a local prototype for supervised evaluation, not an ELIXIR-endorsed
service or production system. Evaluation with unseen researcher questions
(protocol in `evals/`) will determine whether the candidate comparison is
useful.

## Submitting a question

The evaluation depends on real research-tool questions phrased in
researchers' own words. Submit one through the
[structured issue form](../../issues/new?template=submit-question.yml)
(metadata only — no data, identifiers, or private links). If your research
need itself cannot be public, email the steward instead.

Design discussion, catalogue-coverage observations, and retrieval findings are
also welcome as ordinary issues.

## Stewardship and licences

Curated and published by **Michaela Liegertová**
([michaela.liegertova@img.cas.cz](mailto:michaela.liegertova@img.cas.cz)),
affiliated with the [Institute of Molecular Genetics of the Czech Academy of
Sciences](https://www.img.cas.cz/en/). Dedicated to the
[ELIXIR-CZ](https://www.elixir-czech.cz/) community.

IMG affiliation and the ELIXIR-CZ dedication provide context; they do not
imply institutional publication authority or endorsement.

Instruction contracts, schemas, templates, and documentation are licensed
under [CC BY 4.0](LICENSE-CONTENT.md). Retrieval and maintenance software are
licensed under the [MIT License](LICENSE-CODE). The three source catalogues
carry their own licences in their own repositories.
