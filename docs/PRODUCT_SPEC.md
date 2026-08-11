# Product specification — local pilot v0.1

## Product decision

The initial product is a **Research Tool Navigator**, not an autonomous trial
executor. Its first obligation is to understand a researcher's need and expose
a defensible candidate set. Readiness analysis is optional and downstream of a
researcher-owned choice.

## User and job

Primary user: a researcher who knows the scientific task but may not know which
AI-enabled research tools, models, or agents exist or how their practical
constraints differ.

Job to be done:

> Given my intended scientific operation, outputs, environment, and
> constraints, help me find and compare plausible tools without disguising
> catalogue matches as recommendations.

## Product promise

The pilot accepts any ordinary-language, metadata-only research-tool need. It
returns one of the following:

1. an evidence-supported comparison of relevant catalogue candidates;
2. provisional public leads clearly separated from catalogue records; or
3. an explicit zero-result conclusion with coverage limitations.

It cannot promise that a suitable tool exists or that the catalogues cover the
research domain.

## Experience

1. The researcher states a need in normal language.
2. The assistant asks only the questions needed to make the task operational.
3. The assistant shows the interpreted search contract and terms.
4. The researcher confirms or corrects the contract.
5. Deterministic retrieval searches the selected catalogue indexes.
6. The assistant verifies consequential claims using current public evidence.
7. Candidates are compared criterion by criterion; no hidden winner is chosen.
8. The researcher may refine, select candidates, request the optional Layer 2
   readiness analysis (see `ARCHITECTURE.md`), or stop.

## Required outputs

- confirmed query profile;
- reproducible retrieval results with source hashes;
- evidence-backed candidate comparison;
- explicit uncertainties and exclusions; and
- optional readiness plan after researcher selection.

## Non-goals for v0.1

- accepting research datasets or identifiers;
- automatic scientific validation;
- composite suitability scoring;
- autonomous candidate choice;
- installation, acquisition, external submission, or execution;
- authenticated or paid service access;
- institutional authorization; and
- public deployment.

## Acceptance criteria for continuing beyond v0.1

On a small set of unseen, researcher-supplied questions:

- the researcher confirms that the interpreted need is materially accurate;
- retrieval explanations are understandable and reproducible;
- relevant known candidates are not systematically missed;
- evidence and uncertainty are distinguishable from catalogue claims;
- the comparison helps the researcher decide what to inspect next; and
- all data, authority, and execution boundaries are preserved.

Any safety-boundary failure blocks progression. Retrieval improvements should
be driven by observed evaluation failures rather than feature speculation.
