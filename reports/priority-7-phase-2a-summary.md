# Priority 7 — Phase 2A Tooling Summary

**Phase:** 2A fictional schema / ID / validation / projection tooling only  
**Status:** focused independent-review safety corrections complete; Phase 2B remains **NO-GO**

## 1. Safety boundary and baseline

Work was performed only in the approved Phase 2A worktree on branch
`priority-7-phase-2a-tooling`.

- approved HEAD: `d30e43aacf9e6654007ba8277ae0664ab1ab0387`
- approved tree: `f195b784a62ab93005d572cec3e2991e600757a1`
- Git remotes: none
- `push.default`: `nothing`
- starting worktree: clean

No application, learner-content, generated-page, audio, service-worker, progress,
migration, or version file was changed. No real Priority 7 record was created.

## 2. Files

Phase 2A adds:

- `priority7_tooling.py` — isolated Python implementation and CLI;
- `tests/test_priority7_phase2a.py` — in-memory fictional fixtures and dedicated
  regression tests;
- `reports/priority-7-phase-2a-summary.md` — this implementation record.

The focused pre-release safety correction also amends only the directly affected
Phase 1 contracts:

- `reports/priority-7-provenance-and-review-specification.md`;
- `reports/priority-7-content-authoring-specification.md`;
- `reports/priority-7-frozen-data-and-persistence-specification.md`;
- `reports/priority-7-phase-2-readiness-checklist.md`;
- `reports/priority-7-pattern-data-specification.md` (direct release-boundary
  contradiction only);
- `reports/priority-7-phase-1-summary.md` (direct evidence/release summary
  contradiction only).

There is no editorial candidate JSON, public runtime JSON, `data-*.js` file,
browser loader, audio asset, or learner page. The only authored linguistic-looking
fixture is mechanically marked nonproduction and uses the Phase 1 fictional
`fikcjonować` family.

## 3. Implemented contracts

The module keeps three closed contracts separate:

1. the committed Phase 1 report-only specification fixture;
2. the complete private editorial envelope
   `artifactStatus` + `formatVersion` + `lemmas`;
3. the public runtime envelope
   `formatVersion` + `patternDataRevision` + projected `lemmas`.

Private source, reviewer, author, repository, and released-allocation registries
are explicit `ValidationContext` inputs. They are not placed in the editorial
envelope or runtime output.

The editorial validator covers the complete hierarchy, global ID uniqueness,
ownership, closed enums and unions, relation/complement constraints, CEFR and
teaching policy, usage, activity/audio eligibility, provenance, evidence,
content references, examples, aspect/reflexive links, and review history. Bad
container/scalar types return deterministic issues rather than Python errors.

The runtime validator is independent and recursively rejects private/editorial
keys. When supplied with a repository index and/or retained frozen allocation
registry it additionally resolves runtime content references and verifies every
runtime entity's allocated kind and parent ownership. This is shape/referential
validation, not active-release proof: allocation history deliberately retains
tombstoned IDs. Complete release verification validates the whole frozen envelope.

## 4. Stable IDs

All five locked families are implemented:

- `vp-l-*`, `vp-m-*`, `vp-p-*`, `vp-e-*`, and future `vp-x-*`;
- NFC plus canonical whitespace/lowercase normalization;
- the exact Polish-to-ASCII transliteration table;
- punctuation folding, 32-character lemma-slug truncation, and trailing-hyphen
  removal;
- exact versioned seeds, SHA-256, and the first 12 lowercase hexadecimal digits;
- example/exercise readable stems derived only from the stable owning pattern ID;
- distinct exercise item keys for multiple items of one activity type.

The tests reproduce every fictional ID in the Phase 1 example and cover
diacritics, lexical `się`, whitespace, punctuation, truncation, slug collisions,
empty slugs, and malformed owners.

Released allocations retain the original seed and allocation-time readable
inputs. Validators recompute the complete ID, including the readable portion,
and bind active records to frozen kind, parent, key, and original/current
canonical lineage.

## 5. Canonical digests and review state

`canonicalize_rfc8785` is a small RFC 8785 implementation restricted to the
Phase 1 value domain: null, Boolean, NFC Unicode strings, arrays, string-keyed
objects, and safe integers. It uses UTF-16 property ordering, UTF-8 output, and
compact JSON. Floats, non-JSON values, unsafe integers, lone surrogates, and
non-NFC reviewed strings fail explicitly.

Evidence digests cover the complete evidence record, including `note`. Review
scope digests use full `sha256:<64 lowercase hex>` values for all three cumulative
stages. Tests lock exact golden answers and prove invalidation for parent,
meaning, structure, policy, wording, example, origin, audio, and content-reference
changes.

Review validation derives current state from append-only events rather than
trusting `reviewState`. It enforces stage order, exact integer `scopeVersion: 1`,
literal `YYYY-MM-DD` dates, current scope hashes, current evidence pins,
contemporary external evidence, identified-human registry roles, explicit
multi-role owner allowance, deferred/rejected reopen rules, and fresh correction
authority. Reciprocal aspect links require reviewed records on both sides.

Complete duplicate evidence records are rejected so deleting one copy cannot
leave an indistinguishable pin. Editorial error references remain numeric, but
native/product scope construction resolves each reference to the complete
evidence-record digest and preserves reference order. Raw array positions are not
claim-bearing fingerprint values. Reordering two externally pinned records under
an unchanged index now stales native/product approval; moving the same evidence
and updating its index preserves the fingerprint; end-appended unrelated evidence
does not invalidate it. Editing referenced evidence changes both the external pin
and the native/product error-claim fingerprint. A currently reviewed documented
common error still resolves only to current externally pinned evidence.

## 6. Repository reuse

`RepositoryIndex` consumes the same strict source-corpus shape produced by the
existing content loader. It fails closed on upstream parse issues, duplicate IDs,
malformed sources, kind mismatches, missing fields, and non-string fields.

Per-example reuse permits only the locked combinations: card `pl`/`ex` and drill
`prompt`/`answer`. It requires raw parsed string equality with no trimming,
Unicode normalization, markup/audio normalization, joining, coercion, or fallback
to another field. Tests inject a nonproduction in-memory corpus and also exercise
the real repository adapter without copying an existing Polish string into a
fixture.

The inspected repository contains 285 scalar-answer drills, which are eligible
for exact `drill.answer` reuse, and 68 build drills whose `answer` is a token
array and whose `prompt` is absent. Those 68 answers fail explicitly as
non-string. Joining is not a safe adapter: it differs from the repository's
authored completed `full` string in 62 of 68 cases, while `full` is outside the
locked provenance-field enum. Supporting those records requires a Phase 1
contract clarification; Phase 2A does not invent a join or `full` mapping.

## 7. Frozen and tombstone safeguards

`freeze_editorial` creates an independent nonproduction artifact with:

- append-only allocation records;
- closed identity, structure, wording, and policy dimensions;
- retained evidence/review history and current ordered example origins;
- active identities plus immutable tombstones;
- an exactly derivable public runtime projection.

Every frozen dimension has a closed per-kind schema and exact active-identity
coverage. Scope digests are recomputed from the frozen dimensions and origins;
policy cannot self-declare approval. Runtime bytes must be exactly derivable from
the frozen dimensions. Review events and evidence order are prefix-append-only,
and retired pattern evidence/history remain in the private audit artifact.

Released ownership/key/relation identity cannot drift. Relation/complement
identity changes and lexical addition/removal of `się` require replacement.
Wording or retained-origin changes require a fresh owner-authorized correction.
A newly approved entity needs fresh staged approvals but is not mislabeled as a
correction. A narrowly explicit legacy-Boolean repair can correct only a redundant
`reflexive` mismatch while canonical bytes, ownership, ID, and allocation remain
unchanged.

Tombstones prevent disappearance, reuse, and resurrection; preserve former
ownership and retirement revision; and validate same-kind replacement links.
Historical replacement chains resolve through retained allocations even after an
intermediate replacement is later retired.

The frozen transition is the sole Phase 2A release authority. Its returned
`runtimeProjection` is available only after prior frozen state, allocations,
active identity, tombstones, replacement rules, private history, current approval,
runtime parity, and revision transition validate. `validate_frozen_release` and
`verified_runtime_from_frozen` provide the same complete-envelope verification for
an already constructed frozen artifact.

`patternDataRevision` begins at 1 only in the fictional runtime/frozen release.
It increments exactly when the public runtime payload changes, not for private
audit-only changes.

## 8. Projector and privacy boundary

`project_runtime_nonrelease` first validates the entire private editorial record.
It admits only current-digest-valid `approved` patterns whose teaching status is
`active-production` or `recognition-only`, then prunes empty ancestors and sorts
set-like/sibling collections deterministically. Ordered complements, glosses,
examples, and error notes remain ordered. Links to filtered aspect entities are
removed.

The projection contains only runtime consumer fields. It excludes internal scope
and keys, evidence/source material, review state/events/reviewers/digests, example
origins/authors/repository source, editorial evidence references, registries, and
all deferred, rejected, research, or stale candidates. Optional runtime arrays
are omitted when empty.

That pure helper is deliberately not release-authoritative: its caller-provided
revision and allocation lookup cannot detect active-versus-tombstoned membership.
The former `project` CLI surface was removed. The remaining `project-fixture`
command emits an outer
`priority-7-runtime-projection-nonrelease-fixture` wrapper with
`releaseAuthorized: false`; it cannot be mistaken for the raw deployable runtime
envelope. No deployment/release CLI exists in Phase 2A.

Deployment tests inspect the actual loader scripts, `index.html`, service worker,
sitemap, generated outputs, data/audio discovery globs, and protected application
surface. The repository has no single full-transfer deployment manifest, so the
test proves non-reachability across every concrete public/build surface present;
it does not claim an inventory that the repository does not have.

## 9. Implementation conventions and remaining limitations

Phase 1 names every field in each review scope but does not provide a literal JSON
container example or golden digest vector. Phase 2A uses direct nested `lemma`,
`meaning`, and `pattern` objects; the dedicated tests now lock all three exact
fictional digests. A different container would require `scopeVersion` to change,
not silent reinterpretation.

Phase 1 leaves private registry and frozen-artifact machine envelopes conceptual.
Phase 2A defines the smallest closed `ValidationContext`, allocation, snapshot,
review-history, runtime-parity, and tombstone records needed for verification.
Registry storage, access control, and durable private hosting remain Phase 2B
operational decisions.

The specification explicitly preserves ordered `examples` in review scopes even
though a later exclusion mentions sibling placement. Phase 2A treats example
order as semantic and sorts only lemma/meaning/pattern sibling entities.

Editorial error evidence retains numeric authoring indexes, but review scope binds
their resolved complete evidence digests. Released current evidence order also
remains append-only in private frozen history. This preserves stable historical
interpretation while allowing positional movement before release to be harmless
when the resolved digest stays identical.

Post-correction child allocations can prove the lemma canonical form captured at
allocation against the active lemma's original or current form. Proving an
arbitrary chain of multiple intermediate canonical spellings would require a
richer signed allocation/correction history and is not inferred.

The frozen artifact performs closed-schema, cross-dimension, digest, history, and
runtime parity checks, but it is not a digital signature. Preventing an attacker
from replacing every mutually consistent private record still depends on the
future private store's access control/authentication.

The runtime validator can operate as a closed shape/privacy validator with an
empty context and can add repository/allocation referential checks with context.
Neither mode proves active release membership. Only complete frozen-envelope
validation authorizes its exactly derived `runtimeProjection`; an allocation-only
projection may mechanically contain a historical tombstoned ID and remains
explicitly nonrelease.

## 10. Verification

Commands run from the repository root:

```text
python3 priority7_tooling.py validate-specification reports/priority-7-pattern-schema.example.json
python3 -m py_compile priority7_tooling.py tests/test_priority7_phase2a.py
python3 -m unittest tests.test_priority7_phase2a -q
python3 validate_content.py
python3 verify_audio.py
python3 build_pages.py --check
python3 -m unittest discover -s tests -p 'test_*.py'
for test_file in tests/*.js; do osascript -l JavaScript "$test_file" || exit 1; done
```

Results:

- committed Phase 1 specification fixture: valid;
- dedicated Priority 7 suite: 76 tests passed, including the exact two-pinned
  evidence reorder, same-resolved-evidence position move, tombstone release
  bypass, and nonrelease CLI wrapper regressions;
- systematic editorial/runtime/frozen malformed-value sweep: 2,820 mutations,
  zero raw exceptions;
- content: 10 levels, 97 topics, 1,215 cards, 353 drills, 1,675 unique IDs;
- audio: 3,377 required phrases = 3,377 manifest entries = 3,377 MP3 files,
  with no missing or orphaned audio;
- generated pages: current; 23 grammar + 6 vocabulary + guide hub, 32 sitemap
  URLs, 380 pronunciation-bearing strings;
- complete Python discovery: 251 tests passed;
- JavaScript/JXA: 32 suites, 9,670 assertions passed, 0 failed.

The Python runs emitted existing unclosed-file `ResourceWarning`s from shared
repository helpers. JXA emitted macOS service-connection diagnostics. Neither
changed an exit code or represented a failed assertion.

## 11. Readiness decision

Phase 2A is technically ready for independent review. It proves the generic
architecture with fictional data and remains isolated from the application.

Phase 2B remains **NO-GO**. No real authoring, linguistic/source population,
runtime asset, browser integration, offline change, audio generation, persistence,
deployment, or release revision is authorized by this work.
