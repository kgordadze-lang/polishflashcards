# Priority 8 Phase 0 — runtime revision options

Current `patternDataRevision` is 1.

## Option comparison

| Criterion | A — staged: 1 → 2 audio, 2 → 3 expansion | B — combined: 1 → 2 audio + expansion |
|---|---|---|
| Release risk | bounded first release over 45 approved examples | one large change across policy, UI, 70 lemmas and audio |
| Testing | audio semantics/player/discovery isolated first | failures span corpus, governance, UI and media |
| Governance | one re-review/reapproval for audio, later full new-corpus chain | very large simultaneous approval surface |
| Audio QA | exact 45, 20 reuse + 25 new | current 45 plus unapproved expansion text |
| Rollback | revision 2 can be reverted independently; expansion has its own boundary | all-or-nothing rollback |
| User value | pronunciation arrives earlier | value delayed until full corpus completion |
| Failure isolation | strong | weak |
| Implementation speed | small first increment, longer overall sequence | superficially fewer releases but higher integration/review cost |

## Recommendation

Choose **Option A**.

- Revision 2: the same 30 lemmas/34 meanings/45 patterns/45 examples, with approved pronunciation eligibility and control behavior only.
- Revision 3: the separately approved expansion to approximately 100 lemmas.
- Expanded-corpus audio may ship with revision 3 only after exact text freeze, or as a tightly coupled subsequent revision if its eligibility changes runtime bytes. Do not claim revision 3 content is audio-ready before QA.

The revision is a content/projection revision, not learner persistence. It changes only through the official approval-gated frozen transition. A runtime revision must never be hand-edited or treated as release authority by itself.

## Rollback boundaries

Revision 2 rollback restores the revision-1 runtime/control projection and removes only new manifest references; shared pre-existing clips remain. Revision 3 rollback returns to the complete revision-2 30-lemma corpus. Stable IDs allocated in a released revision remain reserved/tombstoned as applicable; rollback never recycles them.

## Release precondition

Do not increment a revision until the current private editorial state, retained frozen baseline, review events, runtime projection, manifest/audio parity and scope-specific tests all pass. Phase 0 changes no revision.
