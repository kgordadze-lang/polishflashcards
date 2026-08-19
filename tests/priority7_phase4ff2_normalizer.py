"""Phase 4F-F2 normalisation, shared by every historical Priority 7 suite.

Phase 4F-F2 advanced all 45 patterns from ``editorial-reviewed`` to
``approved`` by appending exactly one human ``product-approval``
acceptance to each pattern and registering exactly one human product
owner, ``product-owner-001``.  Nothing else in the corpus or the context
moved: no learner-facing field, no example, no provenance record, no
nonhuman actor, none of the 47 reference acceptances and none of the 45
editorial acceptances.

Every historical suite states its claims over the corpus and context with
that approved governance work reverted, exactly as Phase 4F-E1's editorial
review, Phase 4F-D3.1's wording corrections, Phase 4F-C2's examples and
Phase 4F-B3B's corrections already are.  Compose it *outside* the Phase
4F-E1 normaliser, which is pinned to ``editorial-reviewed`` and therefore
sees nothing until this layer is removed first::

    E1.without_phase_4fe1_editorial_review(
        F2.without_phase_4ff2_product_approval(live_corpus))

The revert is keyed on an explicit 45-identity allowlist and the complete
approved event object, including a statically pinned tier-3 digest for each
identity.  Nothing is derived from the corpus being normalised.  An event
that differs anywhere -- including one repinned to mutated live wording --
is not recognised, stays visible, and still breaks the historical guard it
was hidden behind.  An event on a 46th identity is outside the allowlist and
is likewise untouched.  The same holds for the context: only the exact
approved reviewer record and the exact appended notice paragraph are
removed.

This module is phase-owned and additive.  It imports nothing from the
suites that use it, so it can be imported from any of them without a
cycle, and it never writes to any file.
"""

from __future__ import annotations

import copy
import json

#: The date every Phase 4F-F2 acceptance carries.
F2_REVIEWED_AT = "2026-08-17"

#: The one human product owner Phase 4F-F2 registered, and nothing else.
F2_OWNER = "product-owner-001"

F2_DECISION = "accept"
F2_SCOPE_VERSION = 1
F2_PRIOR_REVIEW_STATE = "editorial-reviewed"
F2_FINAL_REVIEW_STATE = "approved"

#: The single note every acceptance carries: one blanket product decision.
F2_NOTE = (
('Product owner approval after visual inspection of all 45 patterns in '
 'the Priority 7 learner interface: APPROVE ALL. Inclusion and '
 'usefulness decision on the recorded treatment; no new language review '
 'was performed.')
)

#: The exact reviewer record Phase 4F-F2 added to ``reviewerRegistry``.
F2_REVIEWER_RECORD = (
{'acknowledgedReleaseModes': ['solo-maintainer-reference-backed'],
 'human': True,
 'namedInPhase': 'Priority 7 Phase 4F-F2',
 'note': 'Real identified human product owner. Product-approval '
         'authority ONLY: holds no external-verification, '
         'native-linguistic, correction or reopen role, is not an '
         'example author, and ownerAllowsMultipleRoles is deliberately '
         'absent because the owner performs exactly one release stage. '
         'Named in Phase 4F-F2 to record the product decision returned '
         'after visual inspection of all 45 patterns in the Priority 7 '
         'learner interface on 2026-08-17: APPROVE ALL. '
         "acknowledgedReleaseModes records the owner's explicit "
         'acceptance of the solo-maintainer-reference-backed chain, in '
         'the stated knowledge that tier 1 and tier 2 were performed by '
         'nonhuman project workflows and that no human external '
         'verification and no formal native-speaker review advanced '
         'either tier. Product approval is a usefulness and inclusion '
         'decision about learner-facing product content; it is not a '
         'language judgement and claims none.',
 'roles': ['product-approval']}
)

#: The exact text block Phase 4F-F2 inserted into the context file.
F2_CONTEXT_REVIEWER_BLOCK = (
('    },\n'
 '    "product-owner-001": {\n'
 '      "human": true,\n'
 '      "roles": ["product-approval"],\n'
 '      "acknowledgedReleaseModes": '
 '["solo-maintainer-reference-backed"],\n'
 '      "namedInPhase": "Priority 7 Phase 4F-F2",\n'
 '      "note": "Real identified human product owner. Product-approval '
 'authority ONLY: holds no external-verification, native-linguistic, '
 'correction or reopen role, is not an example author, and '
 'ownerAllowsMultipleRoles is deliberately absent because the owner '
 'performs exactly one release stage. Named in Phase 4F-F2 to record the '
 'product decision returned after visual inspection of all 45 patterns '
 'in the Priority 7 learner interface on 2026-08-17: APPROVE ALL. '
 "acknowledgedReleaseModes records the owner's explicit acceptance of "
 'the solo-maintainer-reference-backed chain, in the stated knowledge '
 'that tier 1 and tier 2 were performed by nonhuman project workflows '
 'and that no human external verification and no formal native-speaker '
 'review advanced either tier. Product approval is a usefulness and '
 'inclusion decision about learner-facing product content; it is not a '
 'language judgement and claims none."\n')
)

#: The exact paragraph Phase 4F-F2 appended to ``contextNotice``.
F2_CONTEXT_NOTICE_SUFFIX = (
(' Phase 4F-F2 is the first phase to record tier-3 human product '
 'approval, and it supersedes exactly three statements made in the '
 'paragraphs above - that no product-approval authority has been named, '
 'that no product-approval event exists, and that no pattern is approved '
 '- while leaving every other statement in this notice standing, '
 'including that no external-verification, correction or reopen '
 'authority has been named and that nothing has been frozen, released or '
 'projected to runtime. It registered exactly one further human '
 'reviewer, product-owner-001, holding the product-approval role and '
 'nothing else, with acknowledgedReleaseModes naming '
 'solo-maintainer-reference-backed and ownerAllowsMultipleRoles '
 'deliberately absent; and it recorded exactly one product-approval '
 'acceptance on each of the 45 patterns, dated 2026-08-17 and bound to '
 "that pattern's CURRENT tier-3 scope digest, which covers the tier-2 "
 'scope plus contentRefs. All 45 patterns are now approved. The '
 "substantive decision is the product owner's own: after visually "
 'inspecting all 45 patterns in the Priority 7 learner interface, the '
 'owner returned APPROVE ALL. That decision is a usefulness and '
 'inclusion judgement about learner-facing product content and is never '
 'a language judgement; the owner performed no new source check and no '
 'new review of the Polish. No content was reviewed, altered or '
 're-scored in this phase: tier 1 and tier 2 are unchanged on all 45, so '
 'no reference-verification and no editorial-review event was created, '
 'altered or invalidated, and the 47 reference acceptances and 45 '
 'editorial acceptances stand. approved means the human product owner '
 'accepted the recorded treatment for product inclusion under a release '
 'mode whose two lower tiers were performed by nonhuman project '
 'workflows; it never means human external verification, professional '
 'linguistic review or native-speaker review. releaseMode stays '
 'solo-maintainer-reference-backed. No external-verification, correction '
 'or reopen authority has been named, activityEligibility stays empty on '
 'all 45, no audio was enabled, and nothing was frozen, released or '
 'projected to runtime.')
)

#: The 45 literal identities Phase 4F-F2 approved.
F2_EXPECTED_PATTERN_IDS = frozenset(
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
 'vp-p-zajmowac-sie-look-after-person-instrumental-object-6f93facbd939',
 'vp-p-zajmowac-sie-occupation-activity-instrumental-topic-3321df3f989e',
 'vp-p-zalezec-depend-on-od-genitive-source-1ad29f7a1318',
 'vp-p-zalezec-matter-to-someone-dative-experiencer-na-locative-1fc4131471cc',
 'vp-p-znac-be-acquainted-with-accusative-object-379e19b36299',
 'vp-p-znalezc-find-accusative-object-d80c52211462']
)

#: Statically pinned tier-3 scope digest per identity.
F2_EXPECTED_SCOPE_DIGESTS = (
{'vp-p-bac-sie-be-afraid-of-genitive-stimulus-4f1d684a5144': 'sha256:a7f666441f7ad0bac6f4a26a6e80fe41ea9c635b6ebeaea03e0ab25a25607ac0',
 'vp-p-bac-sie-worry-about-o-accusative-concern-c4b9b8d6811b': 'sha256:001086f30b7487e8d6149d3db165be3ff4c26b0f1bfa8522a68f3b56b423fea6',
 'vp-p-byc-predicate-role-instrumental-predicate-3b90a83fbb30': 'sha256:e661ea4801e087f0781c02a3408fa68e3510e1f0c2374d2c9a629e4a9554e990',
 'vp-p-czekac-wait-for-na-accusative-target-3c9ac823ecde': 'sha256:6db3e8ee2b41aa798f4b6bd0fa8b6819f285a5d7e055a704f4c68c7c8a2c5e6d',
 'vp-p-dbac-take-care-of-o-accusative-target-d3e3eb63129c': 'sha256:695241db94fb86a1a01629a64441a604daf3da762c8c62986895e29fea0beb41',
 'vp-p-dziekowac-thank-dative-recipient-za-accusative-057197dd300f': 'sha256:48bc17f9e48601014aed03484c60c674ec7ddf9b308e7d022e07927c2e815af9',
 'vp-p-dziekowac-thank-za-accusative-reason-fd31baa1b1ad': 'sha256:99d9f515c4ca032062837ced610e2702a04c4290573341008d4608dde4f8462e',
 'vp-p-interesowac-sie-be-interested-in-instrumental-topic-1ab788e84e01': 'sha256:f3680a2819261c5fdce2b5c8edbeb742443b8a3d615ad76d1b44502383a98f65',
 'vp-p-lubic-enjoy-thing-or-activity-accusative-object-7e585a50878f': 'sha256:c54a7cfe7429e84c7394d6ba5670a17e1bebc401090f6a707417fca236151d7f',
 'vp-p-lubic-enjoy-thing-or-activity-infinitive-activity-be3742b7ce45': 'sha256:b64dfc696aec6a0639bf4d9db24daeb475a4c30d60692be4ef0898da6ed208f4',
 'vp-p-miec-possess-accusative-object-7181f802bd57': 'sha256:5bbf5716859eaec828d092c5e47e927a208a262b9047b267e810eeee6974f063',
 'vp-p-mowic-tell-content-dative-recipient-accusative-content-2f2b1add1960': 'sha256:6e435a1762ed9bd59cdb5f75856b45abd3cef4499e4badac7e513962a3b31305',
 'vp-p-mowic-tell-content-dative-recipient-ze-clause-a01ddc4a4736': 'sha256:c34a591c0b0a93540045e98ef97ff93b198e05da098f51e85b5d8a0621ecdd25',
 'vp-p-myslec-think-about-o-locative-topic-edf0461e0dd2': 'sha256:5e5d5049cc9adcc5c7e724ce0735954f39e13c1e12583837631e0b1cb13b200e',
 'vp-p-opiekowac-sie-care-for-instrumental-object-8aa6f0a91e5b': 'sha256:fca3774cddae09c439994c8fbc4fc0f2a4a8602797c24b3c2e78a8d843261b9c',
 'vp-p-placic-pay-instrumental-method-ef4313d0d5ce': 'sha256:30b29bde926cbb98d9e9e15d366cd63081d2157d752cd4f1b932404040d49431',
 'vp-p-placic-pay-za-accusative-goods-73c6760c091d': 'sha256:23261f22a5b3d63a92c5f50e0f1b7a2e90a0dcefcdd1c2086bb6d9c738fa6cef',
 'vp-p-podobac-sie-appeal-to-nominative-stimulus-dative-experiencer-ef199e675ee9': 'sha256:efab9b694b8c5ba244fe023319a76ee9d97767f2e618442188ebe32d7f1c8610',
 'vp-p-pomagac-assist-dative-recipient-9f0a375c5e81': 'sha256:727e97ffe99ff5fa98062a07544f746595aab4eda7402d9d5545e94bbacf7f79',
 'vp-p-pomagac-assist-dative-recipient-w-locative-area-1e507dcdb869': 'sha256:e047e3e99416736206c2a85ce52f6c047c0f3ffc82ac52eced291ee59d012aa7',
 'vp-p-potrzebowac-need-genitive-object-437fafad17d2': 'sha256:9b12fa472a765996d432a0d6c793da02f864106d5ef86e4ddb950fda40d864ed',
 'vp-p-prosic-request-accusative-person-o-accusative-thing-b7a8d9ce1a99': 'sha256:c0f610357cf3818af0ef92afd784f5960b3ae63c6e2a05039ae1f62e81385ff2',
 'vp-p-prosic-request-o-accusative-request-06d776fbfd20': 'sha256:2b4a9b94f8a453386670c76226ce21e21454c97a152bb53962bf19181c9c43c5',
 'vp-p-pytac-ask-for-information-accusative-person-o-accusative-topic-841b41ed735a': 'sha256:bb12b72ca3782911e0f7781c94af3dc8f5330a34ca1ea01eeedae21f4acc0d7d',
 'vp-p-pytac-ask-for-information-o-accusative-topic-c89674d989d8': 'sha256:4a10ef11c4933c7e8dfcec109df6ab8b9d14e7e13becd650900143c5a0bc6514',
 'vp-p-rozmawiac-talk-with-o-locative-topic-b1c59475ac05': 'sha256:63ab2a847cea4ee1f0c1365fad4be6b557921897713b58ea57197ce5e7237c07',
 'vp-p-rozmawiac-talk-with-z-instrumental-interlocutor-8398fa7449ca': 'sha256:5603893c77f77a03244f556f1517f195f76226e03a11180c8a42913c45116b8d',
 'vp-p-rozmawiac-talk-with-z-instrumental-o-locative-4e586b18cf98': 'sha256:e664ac2a00806eda09d4886e9b10a86e492669a767e71d8b514a536de1647762',
 'vp-p-sluchac-listen-to-genitive-target-a274f84c8d93': 'sha256:8cec11d2b3047a29c8f3518178ef5deb2d0ff643274bc0efe8645583c126a09c',
 'vp-p-sluchac-obey-genitive-object-674adae2dec3': 'sha256:d5bc1c16955e2392c3e4f0e18993fc2f78fa8f37b6aec9e733c2822935b0beb0',
 'vp-p-szukac-seek-genitive-target-71dc6eff512c': 'sha256:4792776f3021d9fe40bc378d5b85b54bc40d3642a31c300a32bd0155e45e1884',
 'vp-p-tesknic-miss-za-instrumental-target-f866502502c7': 'sha256:7b900a6bf50ee0ea96984114cefe53de04fe573e6d81125e17f59be3d2dc5db0',
 'vp-p-uczyc-sie-study-genitive-subject-matter-44c5fdb95dd7': 'sha256:7d69f8f0353ec7651617b6bf967dada9411c181ae40bf623ac123a70ea3de471',
 'vp-p-uczyc-sie-study-infinitive-skill-ab708776387e': 'sha256:13ee3d7420a8f9a86b0a7559282fe70330c8f5bf1097a45db1c774e8badcd9ee',
 'vp-p-ufac-trust-dative-object-10988adac8cd': 'sha256:0b1da43bfe1cb1b3a0c67a3ea49ece406e028da1f686ecf5c4ef34beaa92c96c',
 'vp-p-uzywac-use-genitive-object-2c5cb44fe85d': 'sha256:ac7d9f5756a661e03295cc72795613d270b5d84e78c364ad1c8d63e211609f9b',
 'vp-p-widziec-perceive-visually-accusative-object-80b697e51432': 'sha256:d7a426241913e2fd63c5419bb9ded99fbe9814082fcfcbf83eae68234823c6a9',
 'vp-p-wierzyc-have-trust-dative-object-f38bb3e72123': 'sha256:b749444696a140eef0a4adb5f841913944152c47469a09640db817b00d71bc65',
 'vp-p-wierzyc-have-trust-w-accusative-target-6561408ea8d1': 'sha256:8b4098137c3bbc61f18075b37d8a1f9dd7a4b130f2453da73c68d9b579ff3bd7',
 'vp-p-zajmowac-sie-look-after-person-instrumental-object-6f93facbd939': 'sha256:4c0444dbef473a5ef9f757f4724834dc2a3bfb3db6e28db4bbb27a4f3c38bb7b',
 'vp-p-zajmowac-sie-occupation-activity-instrumental-topic-3321df3f989e': 'sha256:e40f3578ea259cdc1a1d69124ab9376ecc19511085f58db5db5e29198e80ad71',
 'vp-p-zalezec-depend-on-od-genitive-source-1ad29f7a1318': 'sha256:770600fe533ff87a9af6e0e4cfae3fe847353ccaac4cde0a9577208600bea520',
 'vp-p-zalezec-matter-to-someone-dative-experiencer-na-locative-1fc4131471cc': 'sha256:5ba0eb15397f5234360d55760fce081732048738fc39d5bfcde4f1a35cb4b911',
 'vp-p-znac-be-acquainted-with-accusative-object-379e19b36299': 'sha256:5b9b4e8826a2ad89f543b80e9663d30ce0ba1caa721884a2b0e168e40a6c624f',
 'vp-p-znalezc-find-accusative-object-d80c52211462': 'sha256:7d237d060db6320cadbe1ef2c562e4493decd1ee71928045b2eea449ff545594'}
)


def iter_patterns(corpus):
    """Yield ``(lemma, meaning, pattern)`` in document order."""
    for lemma in corpus.get("lemmas", []):
        for meaning in lemma.get("meanings", []):
            for pattern in meaning.get("patterns", []):
                yield lemma, meaning, pattern


def approved_f2_event(pattern_id):
    """Return the statically pinned event F2 added to ``pattern_id``.

    ``pattern_id`` must be one of the 45 literal F2 identities.  In
    particular, this function never reads a live lemma, meaning, pattern or
    event to decide what the approved transition was.
    """
    if pattern_id not in F2_EXPECTED_PATTERN_IDS:
        raise KeyError(f"pattern identity is outside Phase 4F-F2: {pattern_id!r}")
    return {
        "kind": "product-approval",
        "decision": F2_DECISION,
        "scopeVersion": F2_SCOPE_VERSION,
        "scopeDigest": F2_EXPECTED_SCOPE_DIGESTS[pattern_id],
        "reviewerRef": F2_OWNER,
        "reviewedAt": F2_REVIEWED_AT,
        "note": F2_NOTE,
    }


def without_phase_4ff2_product_approval(corpus):
    """Return a copy of ``corpus`` with the 45 F2 acceptances reverted.

    A pattern is normalised only when its ID is in the literal 45-identity
    allowlist, its state is exactly F2's final state, and its history
    contains exactly one byte-equal pinned acceptance for that ID.  A later
    state, duplicate event, repinned digest, changed note or non-F2 identity
    is left wholly visible.
    """
    corpus = copy.deepcopy(corpus)
    for _lemma, _meaning, pattern in iter_patterns(corpus):
        pattern_id = pattern.get("id")
        if pattern_id not in F2_EXPECTED_PATTERN_IDS:
            continue
        if pattern.get("reviewState") != F2_FINAL_REVIEW_STATE:
            continue
        events = pattern.get("reviewEvents")
        if not isinstance(events, list):
            continue
        expected = approved_f2_event(pattern_id)
        matches = [index for index, event in enumerate(events)
                   if event == expected]
        if len(matches) != 1:
            # Zero: nothing approved to revert.  More than one: a duplicate
            # acceptance, which this normaliser must never absorb.
            continue
        events.pop(matches[0])
        pattern["reviewState"] = F2_PRIOR_REVIEW_STATE
    return corpus


def without_phase_4ff2_reviewer(context):
    """Return a copy of ``context`` with the F2 registry work reverted.

    The reviewer record is removed only when it is byte-equal to the
    approved record, and the notice paragraph only when it is still the
    exact approved suffix.  Any edit to either survives.
    """
    context = copy.deepcopy(context)
    registry = context.get("reviewerRegistry")
    if isinstance(registry, dict) and registry.get(F2_OWNER) == F2_REVIEWER_RECORD:
        del registry[F2_OWNER]
    notice = context.get("contextNotice")
    if isinstance(notice, str) and notice.endswith(F2_CONTEXT_NOTICE_SUFFIX):
        context["contextNotice"] = notice[:-len(F2_CONTEXT_NOTICE_SUFFIX)]
    return context


def without_phase_4ff2_corpus_text(text):
    """Reconstruct the corpus file text as it stood before Phase 4F-F2.

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
            "4F-F2 text normaliser cannot reconstruct it safely")
    return json.dumps(
        without_phase_4ff2_product_approval(document),
        indent=2, ensure_ascii=False) + "\n"


def without_phase_4ff2_context_text(text):
    """Reconstruct the context file text as it stood before Phase 4F-F2.

    Byte surgery on the two exact blocks Phase 4F-F2 inserted -- the reviewer
    record and the appended notice paragraph -- so the result keeps the
    file's hand-maintained formatting exactly.  Each block must appear
    exactly once; an edit to either leaves it unrecognised and the caller's
    byte comparison then fails, which is the intent.
    """
    for block in (F2_CONTEXT_REVIEWER_BLOCK, F2_CONTEXT_NOTICE_SUFFIX):
        if text.count(block) == 1:
            text = text.replace(block, "", 1)
    return text
