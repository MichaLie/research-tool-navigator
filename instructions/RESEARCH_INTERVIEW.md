# Research interview contract

## Objective

Turn an ordinary-language research-tool need into a concise, confirmed,
metadata-only query profile. The interview should reduce ambiguity without
requiring the researcher to understand the catalogues or implementation.

## Conversation pattern

1. Reflect the interpreted scientific operation and intended outcome in one or
   two sentences.
2. Ask only questions that change retrieval or comparison. Ask no more than
   three at once.
3. Prefer ordinary scientific language. Explain technical constraints only
   when they affect the candidate set.
4. Show the resulting interpretation before catalogue search and invite a
   correction.

## Minimum information

- the scientific or research-support operation;
- the intended output or decision;
- a coarse description of the input modality and scale, without actual data;
- candidate-role scope: models, autonomous scientific agents, coding/data
  agents, or any combination;
- material constraints such as local-only use, openness, cost, accounts,
  compute, data classification intent, or institutional environment;
- what success would look like; and
- explicit non-goals when they prevent a misleading match.

If these are already clear, do not ask for them again.

## Safety boundary

Accept descriptions and coarse dimensions only. If the researcher pastes or
offers raw sequences, tables, images, files, identifiers, credentials, private
links, patient narratives, or other sensitive content, stop and ask for a
metadata-only description instead.

The profile fields `contains_real_data` and `contains_secrets` must remain
`false`. `researcher_confirmed` becomes `true` only after the researcher sees
and accepts the interpretation.

## Search-term compilation

Derive and expose rather than hide:

- `domain_terms` — scientific domain, modality and entity vocabulary;
- `outcome_terms` — intended operation and output vocabulary;
- `synonyms` — controlled expansions and common terminology variants;
- `required_terms` — only researcher-confirmed hard lexical requirements;
- `excluded_terms` — explicit exclusions, not guessed dislikes;
- `explicit_candidate_ids` — only candidates the researcher actually names.

Search terms are retrieval aids, not scientific conclusions. Preserve the
researcher's original need verbatim in `research_need`.

## Confirmation view

Before search, show a compact table with:

| Field | Interpreted value |
| --- | --- |
| Research operation | ... |
| Intended output | ... |
| Input description | ... |
| Candidate roles | ... |
| Hard constraints | ... |
| Success criteria | ... |
| Exclusions/non-goals | ... |

Ask: “Is this an accurate search contract?” A correction updates the profile;
it does not count as an error or a new run until the contract is confirmed.
