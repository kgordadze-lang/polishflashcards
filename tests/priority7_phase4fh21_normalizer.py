"""Phase 4F-H2.1 normalisation, shared by every historical Priority 7 suite.

Phase 4F-H2.1 recorded the product owner's decision on the corrected content
Phase 4F-H2 produced.  On 2026-08-18, after reviewing the H2 learner-facing
preview, the owner said "H2 approved".  On that authority H2.1 appended
**exactly one** ``product-approval`` acceptance to each of the 44 patterns H2
changed, each bound to that pattern's freshly recomputed *current* tier-3
scope digest, and moved those 44 rows from ``editorial-reviewed`` to
``approved``.

It did nothing else.  No learner-facing field, no example, no provenance
record, no ``contentRefs`` entry, no evidence record, no reviewer identity, no
nonhuman actor, none of the 47 reference acceptances, none of the 89 editorial
acceptances, none of the 44 editorial change requests and none of the 42
corrections moved.  ``vp-p-zajmowac-sie-look-after-person-instrumental-object-6f93facbd939``
was not touched by H2, its Phase 4F-F2 approval still covers its current
tier-3 scope, and H2.1 deliberately gave it **no** second approval.

Every historical suite states its claims over the corpus and context with that
re-approval reverted.  H2.1 is the newest layer, so compose it *innermost* --
it must come off before Phase 4F-H2's content completion, which must come off
before Phase 4F-F2's approvals, which must come off before Phase 4F-E1's
editorial review::

    E1.without_phase_4fe1_editorial_review(
        F2.without_phase_4ff2_product_approval(
            H2.without_phase_4fh2_content_completion(
                H21.without_phase_4fh21_product_reapproval(live_corpus))))

    E1.without_phase_4fe1_actors(
        F2.without_phase_4ff2_reviewer(
            H2.without_phase_4fh2_context(
                H21.without_phase_4fh21_context(live_context))))

The revert is keyed on an explicit 44-identity allowlist and, for each
identity, the complete pinned acceptance object including a statically pinned
tier-3 digest.  **Nothing is derived from the corpus being normalised.**  A row
is reverted only when it is at exactly ``approved``, the pinned event is
present exactly once, and it is the *last* event in the history.  So each of
the following stays wholly visible and still breaks the guard it would
otherwise hide behind: an approval on the untouched pattern (outside the
allowlist), a duplicated approval, a wrong ``reviewerRef``, an ``actorRef``
in place of a ``reviewerRef``, a wrong date, a stale or repinned digest, a
changed note, an extra reference-verification, editorial-review, correction or
reopen event appended after the approval, and any future product approval.

A *missing* approval is the one mutation a per-row pin cannot expose, because
removing an H2.1 event returns that row to a state Phase 4F-H2 legitimately
described.  It is therefore refused at the layer, not the row:
:func:`without_phase_4fh21_product_reapproval` raises when the corpus carries
the H2.1 layer on *some but not all* of the allowlisted identities it actually
contains.  Every historical suite runs this normaliser, so a partial H2.1
layer cannot pass anywhere.

This module is phase-owned and additive.  It imports nothing from the suites
that use it, so it can be imported from any of them without a cycle, it opens
no file, runs no subprocess and writes nothing.
"""

from __future__ import annotations

import copy
import json

#: The date every Phase 4F-H2.1 acceptance carries.
H21_REVIEWED_AT = "2026-08-18"

#: The existing human product owner.  H2.1 registered nobody new.
H21_OWNER = "product-owner-001"

H21_KIND = "product-approval"
H21_DECISION = "accept"
H21_SCOPE_VERSION = 1
H21_PRIOR_REVIEW_STATE = "editorial-reviewed"
H21_FINAL_REVIEW_STATE = "approved"

#: The one pattern H2 did not touch and H2.1 therefore did not re-approve.
H21_UNTOUCHED_PATTERN_ID = (
    "vp-p-zajmowac-sie-look-after-person-instrumental-object-6f93facbd939"
)

#: The single note every H2.1 acceptance carries.
H21_NOTE = (
('Product owner visually reviewed the corrected H2 learner content - '
 'completed examples, translated Polish illustrations - approved it '
 '2026-08-18. Not a new linguistic, reference or native-speaker review. '
 'Audio deferred; UI wording separate.')
)

#: The 44 literal identities Phase 4F-H2.1 re-approved.
H21_EXPECTED_PATTERN_IDS = frozenset(
['vp-p-bac-sie-be-afraid-of-genitive-stimulus-4f1d684a5144',
'vp-p-bac-sie-worry-about-o-accusative-concern-c4b9b8d6811b',
'vp-p-byc-predicate-role-instrumental-predicate-3b90a83fbb30',
'vp-p-czekac-wait-for-na-accusative-target-3c9ac823ecde',
'vp-p-dbac-take-care-of-o-accusative-target-d3e3eb63129c',
'vp-p-dziekowac-thank-dative-recipient-za-accusative-057197dd300f',
'vp-p-dziekowac-thank-za-accusative-reason-fd31baa1b1ad',
'vp-p-interesowac-sie-be-interested-in-instrumental-topic-1ab788e84e01',
'vp-p-lubic-enjoy-thing-or-activity-accusative-object-7e585a50878f',
'vp-p-lubic-enjoy-thing-or-activity-infinitive-activity-be3742b7ce45',
'vp-p-miec-possess-accusative-object-7181f802bd57',
'vp-p-mowic-tell-content-dative-recipient-accusative-content-2f2b1add1960',
'vp-p-mowic-tell-content-dative-recipient-ze-clause-a01ddc4a4736',
'vp-p-myslec-think-about-o-locative-topic-edf0461e0dd2',
'vp-p-opiekowac-sie-care-for-instrumental-object-8aa6f0a91e5b',
'vp-p-placic-pay-instrumental-method-ef4313d0d5ce',
'vp-p-placic-pay-za-accusative-goods-73c6760c091d',
'vp-p-podobac-sie-appeal-to-nominative-stimulus-dative-experiencer-ef199e675ee9',
'vp-p-pomagac-assist-dative-recipient-9f0a375c5e81',
'vp-p-pomagac-assist-dative-recipient-w-locative-area-1e507dcdb869',
'vp-p-potrzebowac-need-genitive-object-437fafad17d2',
'vp-p-prosic-request-accusative-person-o-accusative-thing-b7a8d9ce1a99',
'vp-p-prosic-request-o-accusative-request-06d776fbfd20',
'vp-p-pytac-ask-for-information-accusative-person-o-accusative-topic-841b41ed735a',
'vp-p-pytac-ask-for-information-o-accusative-topic-c89674d989d8',
'vp-p-rozmawiac-talk-with-o-locative-topic-b1c59475ac05',
'vp-p-rozmawiac-talk-with-z-instrumental-interlocutor-8398fa7449ca',
'vp-p-rozmawiac-talk-with-z-instrumental-o-locative-4e586b18cf98',
'vp-p-sluchac-listen-to-genitive-target-a274f84c8d93',
'vp-p-sluchac-obey-genitive-object-674adae2dec3',
'vp-p-szukac-seek-genitive-target-71dc6eff512c',
'vp-p-tesknic-miss-za-instrumental-target-f866502502c7',
'vp-p-uczyc-sie-study-genitive-subject-matter-44c5fdb95dd7',
'vp-p-uczyc-sie-study-infinitive-skill-ab708776387e',
'vp-p-ufac-trust-dative-object-10988adac8cd',
'vp-p-uzywac-use-genitive-object-2c5cb44fe85d',
'vp-p-widziec-perceive-visually-accusative-object-80b697e51432',
'vp-p-wierzyc-have-trust-dative-object-f38bb3e72123',
'vp-p-wierzyc-have-trust-w-accusative-target-6561408ea8d1',
'vp-p-zajmowac-sie-occupation-activity-instrumental-topic-3321df3f989e',
'vp-p-zalezec-depend-on-od-genitive-source-1ad29f7a1318',
'vp-p-zalezec-matter-to-someone-dative-experiencer-na-locative-1fc4131471cc',
'vp-p-znac-be-acquainted-with-accusative-object-379e19b36299',
'vp-p-znalezc-find-accusative-object-d80c52211462']
)


#: Statically pinned CURRENT tier-3 scope digest per identity.
H21_EXPECTED_SCOPE_DIGESTS = (
{'vp-p-bac-sie-be-afraid-of-genitive-stimulus-4f1d684a5144': 'sha256:94d608261c88168ebe30c08b028fce5bafcfb3dd225eb32e3982902b7b84fe58',
'vp-p-bac-sie-worry-about-o-accusative-concern-c4b9b8d6811b': 'sha256:ba58c5f82966f80e23c59ba46bc7eade12d875fe241b52095cb9a188f1eba8d0',
'vp-p-byc-predicate-role-instrumental-predicate-3b90a83fbb30': 'sha256:c8adbe8db5636e2e0736e886d17250fd1cafd7f073fb07ba84008e3689345e92',
'vp-p-czekac-wait-for-na-accusative-target-3c9ac823ecde': 'sha256:9a27b8759c484a73c8ced5ffcf5987dc69b4bd3a3e6159dd07526219858d1f6e',
'vp-p-dbac-take-care-of-o-accusative-target-d3e3eb63129c': 'sha256:0600cbc63b87ec9ecb40e93e5cb03c0d0c21537702237280e5f770ee62411c3e',
'vp-p-dziekowac-thank-dative-recipient-za-accusative-057197dd300f': 'sha256:8e5d111e269ab5021f25e1580a5fc82e32cd705f3e14c2cd2499a37a3607fc31',
'vp-p-dziekowac-thank-za-accusative-reason-fd31baa1b1ad': 'sha256:62664768342b3c0436314d16814da7897a576e00a11f4501ee84d2a856d138dd',
'vp-p-interesowac-sie-be-interested-in-instrumental-topic-1ab788e84e01': 'sha256:dd531be3aa11274048d25f2d2f6caf1cb675b390e312a586741980fee1ced940',
'vp-p-lubic-enjoy-thing-or-activity-accusative-object-7e585a50878f': 'sha256:e3db5179fe5a230e56c1439c738fc4b3690b6d2c93e53ed5b219525234ad6d50',
'vp-p-lubic-enjoy-thing-or-activity-infinitive-activity-be3742b7ce45': 'sha256:d2a8300e30c14b32452eee17f00d826322e102c7f07d5644049a2102a5c3f7a8',
'vp-p-miec-possess-accusative-object-7181f802bd57': 'sha256:c0511d930f936124ffdaac2bcd74b2e2f84d5f2613c40006305365b8242181e3',
'vp-p-mowic-tell-content-dative-recipient-accusative-content-2f2b1add1960': 'sha256:8a1e38583a1e4d2e74f544c1664bf35df7546000fab93fbe97a80965d23a513f',
'vp-p-mowic-tell-content-dative-recipient-ze-clause-a01ddc4a4736': 'sha256:4cbae9363bbf497b4618b30716b90722f6166d39cf2c28bf09a9c0fb5ae71d41',
'vp-p-myslec-think-about-o-locative-topic-edf0461e0dd2': 'sha256:a7f44ca64aaf37059092e52e780acca06fdb61ab23e4062389cd83cfab8253b3',
'vp-p-opiekowac-sie-care-for-instrumental-object-8aa6f0a91e5b': 'sha256:d88db8cd82a6ac17a51ce1a4689e3648db5c15ea07c52b4a924e1e73356246db',
'vp-p-placic-pay-instrumental-method-ef4313d0d5ce': 'sha256:0f5a91b7d14414957e3d66756e3fdb829aaa7941a23146f43a36ef650970e1bb',
'vp-p-placic-pay-za-accusative-goods-73c6760c091d': 'sha256:ad740bee93176d65e5bf531fdeceec1fa2e9dd93cbaf94998a13500d00bf5691',
'vp-p-podobac-sie-appeal-to-nominative-stimulus-dative-experiencer-ef199e675ee9': 'sha256:6968668d63136cdce1af2b72f18b005d46c3ad3550e58d7b89bc2e94edcbe2c2',
'vp-p-pomagac-assist-dative-recipient-9f0a375c5e81': 'sha256:55c47b9c41b525c0084825b5d32742ad2f561de502d2681a5dea338b679c8717',
'vp-p-pomagac-assist-dative-recipient-w-locative-area-1e507dcdb869': 'sha256:444c5599f784b03e99e3ad62a24b335838b8231f2629ef3e2d8fc7faa0149440',
'vp-p-potrzebowac-need-genitive-object-437fafad17d2': 'sha256:fbe7df00f4970510ea9750b8fc65bb2185fae4747f8fc27bcd36c050ea2ac8c9',
'vp-p-prosic-request-accusative-person-o-accusative-thing-b7a8d9ce1a99': 'sha256:d65de8e66247b3a0cd88159aecc7d0fe381420ce91f5720633376aaef5246232',
'vp-p-prosic-request-o-accusative-request-06d776fbfd20': 'sha256:6defb789f3d948b78cb56d671c8514de315dc1188ebdbb8c5eb0715830e1d37d',
'vp-p-pytac-ask-for-information-accusative-person-o-accusative-topic-841b41ed735a': 'sha256:1c87e8ab48c6e30b81af986d50901747d464bf5e80fdeed065c3d0fecde7fb9b',
'vp-p-pytac-ask-for-information-o-accusative-topic-c89674d989d8': 'sha256:0cad580360cd7cc676796b055c737a89fb34d317c5eec1cf03ed38a5ccda96c1',
'vp-p-rozmawiac-talk-with-o-locative-topic-b1c59475ac05': 'sha256:e5e4d6a88ad646926139715d119ce68fce1edeb0992086ba0618fa1d09989490',
'vp-p-rozmawiac-talk-with-z-instrumental-interlocutor-8398fa7449ca': 'sha256:80063bbc73fa99ac80f5724f692594b356ed0334ef5a813860f1d33e974c66e6',
'vp-p-rozmawiac-talk-with-z-instrumental-o-locative-4e586b18cf98': 'sha256:196259c091bec738bc68e790fd61d30499abe4adb97d70e0342505c147c5dd06',
'vp-p-sluchac-listen-to-genitive-target-a274f84c8d93': 'sha256:b6af0c7dff15e195cc8cadb110b5e3b38aa1b1cb48350c10b03cf63662079ca6',
'vp-p-sluchac-obey-genitive-object-674adae2dec3': 'sha256:9d2f2898321c3dbbb8569105a13040f6fa9b058aec72bb5574a43287cf22e092',
'vp-p-szukac-seek-genitive-target-71dc6eff512c': 'sha256:d1f2c661160acaa717f4fe9e7f0c01fd18208e1aa62138e63fe34fb7acc2b970',
'vp-p-tesknic-miss-za-instrumental-target-f866502502c7': 'sha256:41a31b3a295660387c2d08a2488b36cc9bf3f8947b1d91500e5819d1167e0e92',
'vp-p-uczyc-sie-study-genitive-subject-matter-44c5fdb95dd7': 'sha256:45773301f3764fd2c1160901210ebdcc715ec6242059dab211d35be30e0c2544',
'vp-p-uczyc-sie-study-infinitive-skill-ab708776387e': 'sha256:af2dcfd0088ff2c9ea05df3a9e3b6abb454d3690c35e39080bbb8b501a1af858',
'vp-p-ufac-trust-dative-object-10988adac8cd': 'sha256:45195955f24b35064fea249eee3b8262ed7f434cebfce1dcbd7ae666312c6258',
'vp-p-uzywac-use-genitive-object-2c5cb44fe85d': 'sha256:a74cb0058a51b20f31a8a449f47fe328de8800a83fb7dbd59583d20b5c5b4a6a',
'vp-p-widziec-perceive-visually-accusative-object-80b697e51432': 'sha256:d1a067b778dd61badcca0f68f4fc782f4d42584988d5134d17fe16f72da5d0f6',
'vp-p-wierzyc-have-trust-dative-object-f38bb3e72123': 'sha256:e1574564b89fd3adb9e052c7d2b21c0e8798e3ad014263331464b737d5c8638c',
'vp-p-wierzyc-have-trust-w-accusative-target-6561408ea8d1': 'sha256:2852c0883199fdca98c2398f729a5d187f27debe5b5b3e908e63bd32523178eb',
'vp-p-zajmowac-sie-occupation-activity-instrumental-topic-3321df3f989e': 'sha256:9f5c0105cd951cf7a6645c4de4903320935fe62085fd93da989681ff78cc81fe',
'vp-p-zalezec-depend-on-od-genitive-source-1ad29f7a1318': 'sha256:16281abeda74d4588ef26cc4c0de3458c1555a4f3332f3f4170ac37b14111e6f',
'vp-p-zalezec-matter-to-someone-dative-experiencer-na-locative-1fc4131471cc': 'sha256:ba575f3e28d89a552526e023f5881503d2534f7dcabaad5aa2852113a719b6dd',
'vp-p-znac-be-acquainted-with-accusative-object-379e19b36299': 'sha256:29a82711a7bfef3bc63672f8d6dbf2576c038aa8c28802132e60b7882c302fe5',
'vp-p-znalezc-find-accusative-object-d80c52211462': 'sha256:fddd4b01dc3340abc593e004f69923891f308dcb365b26e51837417767a1e52c'}
)


#: The exact paragraph Phase 4F-H2.1 appended to ``contextNotice``.
H21_CONTEXT_NOTICE_SUFFIX = (
(' Phase 4F-H2.1 is governance only and it supersedes exactly two '
 'statements made above - that the corrected content is NOT '
 'product-approved, and that no new product-approval event was '
 'created - while leaving every other statement in this notice '
 'standing. On 2026-08-18, after visually reviewing the H2 '
 'learner-facing preview, the product owner returned H2 approved. On'
 ' that authority H2.1 appended exactly one product-approval '
 'acceptance to each of the 44 patterns H2 changed, dated '
 "2026-08-18, recorded under product-owner-001's existing product "
 "authority and bound to that pattern's freshly recomputed CURRENT "
 'tier-3 scope digest; no stale H2 or F2 digest was reused. '
 'vp-p-zajmowac-sie-look-after-person-instrumental-object-6f93facbd939'
 ' was not touched by H2, its existing product approval still covers'
 ' its current tier-3 scope, and it deliberately received no second '
 "approval. All 45 patterns are now approved. The owner's review "
 'covered the completed examples and the English translations of the'
 ' Polish illustrations; it is a usefulness and inclusion decision '
 'about learner-facing product content and is never a language '
 'judgement, so it is not a new linguistic, reference or '
 'native-speaker review and the Polish was not authored or '
 'externally verified by the owner. No learner content changed: all '
 '45 pattern identities, explanations, error notes, examples, '
 'complements, usage, CEFR, teaching status, contentRefs and '
 'provenance records are byte-identical to the H2 baseline, so '
 'tier-1 and tier-2 digests moved on 0 of 45 and the 47 reference '
 'acceptances, 89 editorial acceptances and 44 editorial change '
 'requests stand unaltered. No reviewer or nonhuman actor identity '
 'was added or changed, no correction, reopen or '
 'external-verification authority has been named, reopen events '
 'remain 0, releaseMode stays solo-maintainer-reference-backed, '
 'activityEligibility stays empty on all 45, audio remains deferred '
 'and no audio was enabled, the UI wording change remains '
 'outstanding for a later phase, and nothing was frozen, released or'
 ' projected to runtime.')
)


def iter_patterns(corpus):
    """Yield ``(lemma, meaning, pattern)`` in document order."""
    for lemma in corpus.get("lemmas", []):
        for meaning in lemma.get("meanings", []):
            for pattern in meaning.get("patterns", []):
                yield lemma, meaning, pattern


def approved_h21_event(pattern_id):
    """Return the statically pinned event H2.1 appended to ``pattern_id``.

    ``pattern_id`` must be one of the 44 literal H2.1 identities.  In
    particular, this function never reads a live lemma, meaning, pattern or
    event to decide what the re-approval was, and it refuses the untouched
    pattern outright.
    """
    if pattern_id not in H21_EXPECTED_PATTERN_IDS:
        raise KeyError(
            f"pattern identity is outside Phase 4F-H2.1: {pattern_id!r}")
    return {
        "kind": H21_KIND,
        "decision": H21_DECISION,
        "scopeVersion": H21_SCOPE_VERSION,
        "scopeDigest": H21_EXPECTED_SCOPE_DIGESTS[pattern_id],
        "reviewerRef": H21_OWNER,
        "reviewedAt": H21_REVIEWED_AT,
        "note": H21_NOTE,
    }


def _h21_layer_present(pattern):
    """True when ``pattern`` still carries the exact pinned H2.1 acceptance.

    The acceptance must be the *last* event, so anything appended after it --
    a further approval, a correction, a reopen, a new reference verification
    or editorial review -- leaves the row unnormalised and fully visible.
    """
    pattern_id = pattern.get("id")
    if pattern_id not in H21_EXPECTED_PATTERN_IDS:
        return False
    if pattern.get("reviewState") != H21_FINAL_REVIEW_STATE:
        return False
    events = pattern.get("reviewEvents")
    if not isinstance(events, list) or not events:
        return False
    expected = approved_h21_event(pattern_id)
    if events.count(expected) != 1:
        # Zero: nothing to revert.  More than one: a duplicated acceptance,
        # which this normaliser must never absorb.
        return False
    return events[-1] == expected


def phase_4fh21_layer_state(corpus):
    """Report the H2.1 layer as ``absent``, ``complete`` or ``partial``.

    Completeness is judged only over the allowlisted identities the corpus
    actually contains, so a fixture holding a subset of the corpus is
    described honestly rather than accused of being partial.
    """
    present = 0
    total = 0
    for _lemma, _meaning, pattern in iter_patterns(corpus):
        if pattern.get("id") not in H21_EXPECTED_PATTERN_IDS:
            continue
        total += 1
        present += _h21_layer_present(pattern)
    if present == 0:
        return "absent"
    if present == total:
        return "complete"
    return "partial"


def without_phase_4fh21_product_reapproval(corpus):
    """Return a copy of ``corpus`` with the 44 H2.1 acceptances reverted.

    A row is normalised only when its ID is in the literal 44-identity
    allowlist, its state is exactly ``approved``, and the pinned acceptance is
    present exactly once as the final event.  Anything else -- an approval on
    the untouched pattern, a duplicate, a repinned digest, a wrong reviewer,
    an ``actorRef`` instead of a ``reviewerRef``, a wrong date, a changed note
    or a later event -- is left wholly visible.

    A corpus carrying the layer on some but not all of the allowlisted
    identities it contains is refused rather than half-reverted: a missing
    re-approval is the one defect a per-row pin cannot expose, because
    removing an H2.1 event returns that row to a state Phase 4F-H2
    legitimately described.
    """
    state = phase_4fh21_layer_state(corpus)
    if state == "partial":
        raise AssertionError(
            "Phase 4F-H2.1 is present on some but not all of the 44 patterns "
            "it re-approved; the layer is incomplete and must not be "
            "normalised away")
    corpus = copy.deepcopy(corpus)
    if state == "absent":
        return corpus
    for _lemma, _meaning, pattern in iter_patterns(corpus):
        if not _h21_layer_present(pattern):
            continue
        pattern["reviewEvents"].pop()
        pattern["reviewState"] = H21_PRIOR_REVIEW_STATE
    return corpus


def without_phase_4fh21_context(context):
    """Return a copy of ``context`` with the H2.1 notice paragraph reverted.

    Phase 4F-H2.1 registered no reviewer and no nonhuman actor and changed no
    existing registry record, so the appended notice is the only context
    change there is to revert, and it is removed only when it is still the
    exact appended suffix.
    """
    context = copy.deepcopy(context)
    notice = context.get("contextNotice")
    if isinstance(notice, str) and notice.endswith(H21_CONTEXT_NOTICE_SUFFIX):
        context["contextNotice"] = notice[:-len(H21_CONTEXT_NOTICE_SUFFIX)]
    return context


def without_phase_4fh21_corpus_text(text):
    """Reconstruct the corpus file text as it stood before Phase 4F-H2.1.

    The corpus is stored in exactly ``json.dumps(indent=2,
    ensure_ascii=False)`` form plus a trailing newline.  That storage form is
    asserted here rather than assumed, so if it ever changes this raises
    instead of returning something that merely looks reverted.
    """
    document = json.loads(text)
    canonical = json.dumps(document, indent=2, ensure_ascii=False) + "\n"
    if canonical != text:
        raise AssertionError(
            "corpus file is not in its canonical stored form; the Phase "
            "4F-H2.1 text normaliser cannot reconstruct it safely")
    return json.dumps(
        without_phase_4fh21_product_reapproval(document),
        indent=2, ensure_ascii=False) + "\n"


def without_phase_4fh21_context_text(text):
    """Reconstruct the context file text as it stood before Phase 4F-H2.1.

    Byte surgery on the one block Phase 4F-H2.1 inserted -- the appended
    notice paragraph -- so the result keeps the file's hand-maintained
    formatting exactly.  The block must appear exactly once; an edit to it
    leaves it unrecognised and the caller's byte comparison then fails, which
    is the intent.
    """
    if text.count(H21_CONTEXT_NOTICE_SUFFIX) == 1:
        text = text.replace(H21_CONTEXT_NOTICE_SUFFIX, "", 1)
    return text
