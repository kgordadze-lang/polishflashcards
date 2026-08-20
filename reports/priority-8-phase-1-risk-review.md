# Priority 8 Phase 1A — risk review

| Risk | Control | Current disposition |
|---|---|---|
| Audio accidentally enables Listening or production | explicit one-way policy, empty allowlists, negative tests | controlled |
| Unreviewed synthesis described as approved | all 25 CSV rows pending; governance notes disclaim audio quality | controlled; human QA outstanding |
| External disclosure during synthesis | owner-authorized text-only CSV allowlist; generator aborts unless the exact missing set equals those 25 sentences | controlled; 25 authorized sentences sent, no other repository content |
| Existing clip regenerated | incremental pipeline plus baseline byte comparison for all 20 | controlled; all 20 entries/files unchanged |
| Hash collision/manifest drift | generator refuses occupied mismatch; verifier checks key/path/text/duplicates | controlled |
| Stale or overlapping playback | one owner, settled latch, identity guards, surface-exit cleanup | controlled |
| Keyboard/screen-reader/mobile regression | native button, contextual label, Polish language tag, 44px target, wrapping | controlled by deterministic tests; human spot check remains useful |
| Offline/Range/cache regression | unchanged worker bytes after release metadata normalization; 558 applicable current-worker behavior assertions plus Phase 1 checks | controlled |
| Private governance leak | official frozen projection and forbidden-key audit | controlled |
| Content/ID drift | normalized-out whole-document comparison and Polish byte digest | controlled |
| Schema/persistence creep | versions remain 2/2/1; no new state | controlled |
| Expansion or analytics enters scope | diff/test/report inspection | no such work observed |

No production, remote, push, deployment, Listening, Type It, grammar activity, expansion corpus, analytics, or learner-facing review UI is part of this candidate.

## Historical reproducibility discrepancy

The Phase 0 test inventory states that all 1,999 Python tests passed. This disposable repository cannot reproduce the historical portion because tracked phase suites pin Git objects that are absent, including `fe07bd32e0379e6b96c06659063ce30cba8514b3`. The owner explicitly revised the Phase 1A gate to classify source-proven historical/release assertions separately; no historical source or expectation was changed. The exact classification and every absent baseline commit are recorded in the test report. This remains a documentation/reproducibility discrepancy for later adjudication, not a current-head application failure.
