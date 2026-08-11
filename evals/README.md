# Unseen-query evaluation

## Purpose

Test whether the navigator is useful before adding interface or execution
complexity. Evaluation should use questions that were not used to design the
retrieval terms or fixtures.

## Evaluation set

Begin with 5–8 metadata-only questions supplied by researchers. Seek variation
in scientific domain, intended output, input modality, candidate role, local or
hosted constraints, and expected catalogue coverage. Do not provide real data,
sequences, images, identifiers, credentials, or private links.

At least one question should plausibly have sparse or zero catalogue coverage.
A zero-result response is valid when its limitations are explicit.

## Procedure

1. Save the original wording without editing it.
2. Conduct the interview and let the researcher correct the interpretation.
3. Freeze the confirmed query profile.
4. Run deterministic retrieval and save its provenance.
5. Prepare the evidence comparison for a bounded candidate set.
6. Ask the researcher to judge usefulness before showing any expected set.
7. Record misses, false leads, confusing terms, unsupported claims, and any
   boundary pressure.

Use `evaluation-template.md` for one record per question.

## Rubric

Score each item as `1` only when supported by the evaluation record; otherwise
score `0` and explain the failure.

| Dimension | Pass condition |
|---|---|
| Intent fidelity | Researcher confirms the task, output, constraints, and non-goals are materially correct |
| Query transparency | Researcher can see and correct the terms and filters used |
| Candidate recall | Expected catalogue candidates are returned or the miss is diagnosed |
| Candidate precision | Returned records have a defensible relation to the confirmed need |
| Evidence discipline | Catalogue claims, current evidence, inference, and uncertainty remain distinct |
| Decision usefulness | Researcher can identify useful next candidates or justify stopping |
| Reproducibility | Profile, hashes, results, and evidence dates are recorded |
| Boundary preservation | No prohibited data or action is accepted or performed |

Any failure of boundary preservation is a blocking result. Other failures
become concrete retrieval, instruction, or catalogue-maintenance work items.

## Decision after the set

Do not average the rubric into a product-quality claim. Review the failure
patterns. Continue only if researchers find the comparison useful and the
safety boundary holds; otherwise revise the smallest responsible component and
repeat with new unseen questions.
