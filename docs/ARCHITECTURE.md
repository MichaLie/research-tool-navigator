# Architecture

## Design rationale

The simplest test of the product idea is an expert-mediated agent workspace,
not a new multi-agent platform. One assistant preserves conversational context;
small instruction contracts separate responsibilities; deterministic code
makes catalogue retrieval inspectable and repeatable.

```text
researcher question
        |
        v
short interview + visible interpretation
        |
        v
confirmed metadata-only query profile
        |
        v
deterministic read-only catalogue retrieval
        |
        v
current-evidence comparison, criterion by criterion
        |
        +----> refine or stop
        |
 researcher selects candidate(s)
        |
        v
optional readiness mapping ----> stop before acquisition or execution
```

## Instruction hierarchy

There are not separate autonomous personalities for Layer 1 and Layer 2.

| Contract | Responsibility | Authority |
|---|---|---|
| `AGENTS.md` | Overall mission, evidence policy, artifacts, and hard boundaries | Governs the whole workspace |
| `instructions/RESEARCH_INTERVIEW.md` | Translate ordinary language into a researcher-confirmed query profile | Conversation and interpretation only |
| `instructions/CANDIDATE_DISCOVERY.md` | Retrieve, verify, and compare candidates | Layer 1; no winner selection or execution |
| `instructions/TRIAL_READINESS.md` | Triage trial routes, then map researcher-selected routes and their blockers | Layer 2; planning only |

This arrangement is easier to audit than multiple nested `AGENTS.md` files and
avoids implying that independent agents are acting on the researcher's behalf.

## Deterministic retrieval component

`scripts/navigator.py` uses only the Python standard library. It:

- validates the closed query-profile contract;
- rejects real-data, secret, sequence-like, and opaque payload indicators;
- validates catalogue record IDs and duplicate keys;
- searches selected fields using visible query-term and field weights;
- applies required and excluded terms as hard filters;
- reports the matched fields and contribution of each term;
- returns a bounded list per index; and
- records catalogue counts, file paths, and SHA-256 hashes.

The score exists only to order retrieval results. It does not combine
scientific fit, evidence quality, cost, governance, or feasibility and is never
presented as a recommendation.

## Catalogue boundary

The navigator reads three catalogue files and never writes to them:
`models_final.json` (Foundation Models), `agents_final.json` (Autonomous
Agents), and `tools.json` (Coding Agents). They come from sibling repository
checkouts or, in a standalone clone, from the published distributions fetched
by `scripts/fetch_catalogues.py` (see the README section on standalone use).

Catalogue metadata establishes discovery context. Candidate comparison must
check current primary documentation, papers, artifacts, licences, and relevant
independent evidence. A public lead absent from the catalogues may be discussed
but must remain visibly provisional.

## State and reproducibility

Each research need receives a new `runs/<request-id>/` directory. The confirmed
profile, retrieval output, comparison, readiness plan, and provenance are kept
together. Query-profile hashes and catalogue hashes allow later reconstruction
of what the retrieval engine actually saw.

## Authority boundary

The pilot stops after comparison or planning. It cannot acquire a
candidate, install dependencies, call authenticated services, upload data, run
code, approve scientific use, or make an institutional decision. Adding any of
those capabilities would be a separate product and governance decision.
