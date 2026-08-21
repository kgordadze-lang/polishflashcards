# Priority 8 Phase 4B0 - Risk Review

## Overall assessment

Phase 4B0 is safe to submit for independent review as private staging
infrastructure. It begins no linguistic batch and makes no canonical, runtime,
schema, audio, activity, deployment, or integration change.

## 1. Staging accidentally becomes canonical

Risk: The private JSON could be treated as a convenient alternate canonical or
runtime source.

Control: It is not wired into any application or generator. The validator
imports no canonical tooling and writes nothing. Protected-file hash tests and
the five-path scope gate prove that canonical/runtime projection does not
occur. Phase 4C promotion remains mandatory.

## 2. Production-ID leakage

Risk: Draft or candidate identity could prematurely freeze as a production
Verb Patterns identity.

Control: Recursive validation rejects every string containing any of the five
production prefixes and rejects production-ID field names at every nesting
depth. Dedicated mutations cover all five prefixes plus a production-ID field.
The real skeleton contains zero candidate keys and zero production IDs.

## 3. Constraint drift

Risk: The 21 narrowing/representation boundaries or 12 global constraints
could be omitted, paraphrased, reordered, or attached to the wrong lemma.

Control: Per-lemma constraints are derived from the frozen CSV selection rule,
copied exactly, and validated against exact text/source objects. Global text is
an exact frozen constant with item-level handoff pointers. Missing and moved
constraint mutations fail.

## 4. Metadata-only aspect leakage

Risk: `zaczynać` or `przeczytać` could become a 69th/70th record, receive an ID,
carry syntax, or leak into current public aspect relationships.

Control: Exact membership excludes both identities. Exactly two private
objects are allowed only on `zacząć` and `czytać`, with two fields each. The
record shape rejects syntax/content/ID additions, and `aspectPartnerIds` is not
created. Missing, wrong, moved, and full-record mutations fail.

## 5. Required `udział` is lost

Risk: Later work could reduce `brać/wziąć udział w + Locative` to generic object
syntax.

Control: The skeleton requires `requiredLexicalItems: ["udział"]` exactly on
`brać` and `wziąć`, nowhere else. Three dedicated mutations prove both omission
cases and unrelated placement fail. Batch review must carry this guard into the
candidate construction review.

## 6. Linguistic authoring accidentally begins in B0

Risk: A meaning, pattern, example, learner explanation, complement, CEFR/status
decision, or candidate key could enter under cover of infrastructure work.

Control: Every record has three explicit empty candidate collections. Phase
4B0 validation requires all three to equal empty arrays, rejects candidate key
fields, and rejects unexpected record fields. The measured aggregate content
counts are all zero.

## 7. Staging and canonical governance are confused

Risk: A private review status could be interpreted as the canonical
`reviewState` or product release approval.

Control: The envelope declares the private vocabulary separately. Phase 4B0
requires every record to be `draft`; neither `reviewState` nor canonical
governance fields are present. Later `human-approved` means only that the
ID-less staging record may proceed to Phase 4C reconciliation.

## 8. Frozen membership or source identity drifts

Risk: A reserve, revised source, wrong aspect, or reordered lemma could enter
without reopening governance.

Control: The validator derives exact membership, order, aspects, dispositions,
evidence pointers, and the 21-row selection from the frozen CSV reports. The
envelope pins source hashes and starting HEAD/tree. Count, reserve, order,
duplicate, source, and baseline mutations fail.

## 9. Future key freeze is premature or unstable

Risk: Candidate keys may be malformed, duplicated, or treated as durable before
human staging approval.

Control: No candidate key exists in valid Phase 4B0 staging. Future field names
are explicit, and the validator already applies the current lowercase-kebab
syntax. Sibling-scoped uniqueness is deliberately deferred until the candidate
ownership hierarchy is defined before candidate authoring begins. Global
uniqueness must never be imposed because the stable-ID seed model scopes meaning
keys under lemma identity, pattern keys under meaning identity, and example keys
under pattern identity. Candidate keys remain editable until human staging
approval and must not include verification order as an identity seed.

## 10. Future direct-speech schema dependency

Risk: Later authoring may need direct speech before the canonical model supports
the approved `clauseKind: direct-speech` shape.

Control: Phase 4B remains private and may not implement schema support. Phase
4B0 authors no clause or other candidate content. Phase 4C must implement and
mechanically synchronize the Python/JavaScript clause-kind contract before any
direct-speech candidate is canonically promoted. No fifth complement type is
authorized.

## 11. Version, audio, or activity side effects

Risk: Infrastructure work could accidentally trigger release machinery.

Control: The allowed-path gate excludes UI/runtime/service-worker/audio files.
No version or revision value is changed, no audio is generated, and no activity
is activated. The validator has no generation path.

## Residual risk and gate

The main residual risk begins with Phase 4B Batch 1, when sourced linguistic
content and candidate semantic keys first become possible. Independent review
of this Phase 4B0 commit is required before that batch. Direct-speech canonical
support, key freeze, production-ID allocation, and canonical promotion remain
deferred to Phase 4C.
