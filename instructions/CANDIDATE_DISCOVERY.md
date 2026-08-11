# Candidate discovery and comparison contract

## Objective

Use the confirmed query profile, the three read-only catalogues, and current
public evidence to produce a defensible candidate set. Explain why every
compared candidate remains relevant and what is not known.

## Retrieval sequence

1. Validate the confirmed query profile.
2. Run `scripts/navigator.py search` against the bound catalogue snapshots.
3. Inspect matched fields and terms. A high retrieval score means only that the
   catalogue record matched the confirmed vocabulary strongly.
4. Check whether expected roles or obvious terminology were missed. If needed,
   propose visible synonym changes and ask the researcher before rerunning.
5. Select a manageable set for evidence review, preserving more than one
   pathway when the roles are not interchangeable.
6. Investigate current public evidence. Do not rely on catalogue prose alone
   for consequential suitability claims.

## Candidate comparison

Compare each candidate on separate dimensions rather than one composite score:

| Dimension | Question |
| --- | --- |
| Scientific-task fit | Does the documented operation and output match the confirmed need? |
| Evidence strength | What primary and independent evidence directly supports this use? |
| Artifact clarity | Is the exact usable artifact, version and provenance identifiable? |
| Access and licence | Can it lawfully and practically be obtained or accessed? |
| Operational fit | Do interface, dependencies, compute and support match the constraints? |
| Data and governance fit | Are data location, telemetry, account and institutional implications clear? |

Use states such as `supportive`, `mixed`, `insufficient`, `conflicting`, or
`not_applicable`, each with a short rationale and sources. Do not sum these
states into a hidden total.

## Result language

- Distinguish “catalogue match” from “evidence-supported candidate.”
- Say “stronger evidence for criterion X,” not “best overall,” unless the
  researcher has explicitly defined and accepted an aggregation rule.
- Treat popularity and search order as discovery signals only.
- Preserve zero-result and evidence-insufficient outcomes.
- A public web lead absent from the catalogues may be reported as provisional,
  but not silently treated as a catalogue candidate.

## Required output

Create `candidate-comparison.md` with:

1. confirmed need and constraints;
2. catalogue snapshots and retrieval limitations;
3. candidates grouped by role/pathway;
4. the criterion-wise comparison table;
5. exclusions and provisional leads;
6. unresolved evidence and questions;
7. options available to the researcher: change criteria, request more evidence,
   select candidates for readiness mapping, or stop.
