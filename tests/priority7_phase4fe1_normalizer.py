"""Phase 4F-E1 normalisation, shared by every historical Priority 7 suite.

Phase 4F-E1 advanced all 45 patterns from ``reference-verified`` to
``editorial-reviewed`` by appending exactly one ``editorial-review``
acceptance to each pattern and registering exactly two nonhuman
``editorial-review`` actors.  Nothing else in the corpus or the context
moved: no learner-facing field, no example, no provenance record, no
identity, and none of the 47 existing reference acceptances.

Every historical suite states its claims over the corpus and context with
that approved governance work reverted, exactly as Phase 4F-B3B's
corrections, Phase 4F-C2's examples and Phase 4F-D3.1's wording
corrections already are.

The revert is keyed on an explicit 45-identity allowlist and the complete
approved event object, including a statically pinned post-D3.1 digest for
each identity.  Nothing is derived from the corpus being normalised.  An
event that differs anywhere -- including one repinned to mutated live
wording -- is not recognised, stays visible, and still breaks the historical
guard it was hidden behind.  An event on a 46th identity is outside the
allowlist and is likewise untouched.  The same holds for the context: only
the two exact approved actor records and the exact appended notice paragraph
are removed.

This module is phase-owned and additive.  It imports nothing from the
suites that use it, so it can be imported from any of them without a
cycle, and it never writes to any file.
"""

from __future__ import annotations

import copy
import json

#: The date every Phase 4F-E1 acceptance carries.
E1_REVIEWED_AT = "2026-08-17"

#: The two nonhuman actors Phase 4F-E1 registered, and nothing else.
E1_EDITORIAL_ACTOR = "priority7-editorial-review"
E1_CORROBORATING_ACTOR = "priority7-editorial-corroboration"

E1_CONTEXT_NOTICE_SUFFIX = (' Phase 4F-E1 is the first phase to record tier-2 editorial review, and '
 'it supersedes exactly two statements in the Phase 4F-A paragraph above '
 '- that no editorial-review actor is registered and that no '
 'editorial-review event exists - while leaving every other statement in '
 'this notice standing. It registered exactly two further nonhuman '
 'actors, priority7-editorial-review and '
 'priority7-editorial-corroboration, each holding the editorial-review '
 'role and nothing else and each deliberately distinct from the other, '
 'from priority7-reference-analysis and from '
 'priority7-example-generation; and it recorded exactly one '
 'editorial-review acceptance on each of the 45 patterns, bound to that '
 "pattern's CURRENT post-D3.1 tier-2 scope digest and naming "
 'priority7-editorial-corroboration as the independent corroborator the '
 'solo chain requires at this tier. All 45 patterns are now '
 'editorial-reviewed. The substantive basis is the completed '
 'D1/D2/D3/D3.1 review chain already persisted in reports: D1 '
 'recommended acceptance on 45/45, blind D2 returned 41 ACCEPT and 4 '
 'CHANGES NEEDED, D3 overturned the P7-NR-011 blocker and upheld those '
 'on P7-NR-018, P7-NR-028 and P7-NR-037, and D3.1 implemented the three '
 'approved canonical corrections. Those three rows are the only ones '
 'whose tier-2 digest moved; tier-1 is unchanged on all 45, so no '
 'reference-verification event was created, altered or invalidated and '
 'the 47 existing reference acceptances stand. editorial-reviewed means '
 'two independent nonhuman editorial passes agreed on the learner-facing '
 'treatment against the current tier-2 scope; it never means '
 'native-speaker review, professional linguistic review or any human '
 'review. releaseMode stays solo-maintainer-reference-backed. No '
 'external-verification, product-approval, correction or reopen '
 'authority has been named, no product-approval event exists, no pattern '
 'is approved, and nothing was frozen, released or projected to runtime.')


E1_ACTORS = {'priority7-editorial-review': {'human': False,
                                'kind': 'editorial-review-workflow',
                                'roles': ['editorial-review'],
                                'namedInPhase': 'Priority 7 Phase 4F-E1',
                                'note': 'Nonhuman editorial-review '
                                        'workflow. Not a person, not a '
                                        'native speaker, not a linguist '
                                        'and not a reviewer identity: it '
                                        'is the identity under which the '
                                        "project's own tier-2 editorial "
                                        'review of the learner-facing '
                                        'treatment was performed. It '
                                        'records only that that workflow '
                                        'ran against the final post-D3.1 '
                                        'corpus; it supplies no '
                                        'native-speaker judgement and no '
                                        'professional linguistic '
                                        'authority. Holds the '
                                        'editorial-review role only, so '
                                        'it can neither reference-verify '
                                        'nor generate examples, and it '
                                        'is deliberately distinct from '
                                        'priority7-reference-analysis '
                                        'and '
                                        'priority7-example-generation. '
                                        'editorial-reviewed therefore '
                                        'means the recorded '
                                        'learner-facing treatment passed '
                                        'two independent nonhuman '
                                        'editorial passes against the '
                                        'current tier-2 scope digest; it '
                                        'never means human review, and '
                                        'product approval remains human, '
                                        'mandatory and unperformed.',
                                'auditMetadata': {'runNote': 'Private '
                                                             'audit '
                                                             'trail for '
                                                             'the '
                                                             'maintainer. '
                                                             'The '
                                                             'substantive '
                                                             'review '
                                                             'this actor '
                                                             'records is '
                                                             'the Phase '
                                                             '4F-D1 '
                                                             'primary '
                                                             'editorial '
                                                             'pass over '
                                                             'all 45 '
                                                             'rows, '
                                                             'which '
                                                             'returned '
                                                             '45/45 '
                                                             'acceptance '
                                                             'recommendations '
                                                             'with 23 '
                                                             'ACCEPT and '
                                                             '22 ACCEPT '
                                                             'WITH NOTE. '
                                                             'Blind '
                                                             'corroboration '
                                                             'is Phase '
                                                             '4F-D2, '
                                                             'recorded '
                                                             'separately '
                                                             'as '
                                                             'priority7-editorial-corroboration. '
                                                             'The four '
                                                             'rows the '
                                                             'two passes '
                                                             'disagreed '
                                                             'on were '
                                                             'resolved '
                                                             'by the '
                                                             'Phase '
                                                             '4F-D3 '
                                                             'adjudication '
                                                             'and, where '
                                                             'upheld, '
                                                             'implemented '
                                                             'by Phase '
                                                             '4F-D3.1. '
                                                             'Nothing in '
                                                             'this '
                                                             'object is '
                                                             'part of '
                                                             'the stable '
                                                             'actor '
                                                             'identity '
                                                             'and no '
                                                             'release '
                                                             'validity '
                                                             'depends on '
                                                             'it.'}},
 'priority7-editorial-corroboration': {'human': False,
                                       'kind': 'editorial-review-workflow',
                                       'roles': ['editorial-review'],
                                       'namedInPhase': 'Priority 7 Phase '
                                                       '4F-E1',
                                       'note': 'Nonhuman '
                                               'editorial-review '
                                               'workflow, registered as '
                                               'the independent '
                                               'corroborator required by '
                                               "the solo chain's tier-2 "
                                               'acceptance rule. Not a '
                                               'person, not a native '
                                               'speaker, not a linguist '
                                               'and not a reviewer '
                                               'identity. It is the '
                                               'identity of the blind '
                                               'second editorial pass '
                                               'run in Phase 4F-D2, '
                                               'which reviewed the same '
                                               '45 rows without sight of '
                                               'the Phase 4F-D1 pass and '
                                               'returned 41 ACCEPT and 4 '
                                               'CHANGES NEEDED. Holds '
                                               'the editorial-review '
                                               'role only, so it can '
                                               'neither reference-verify '
                                               'nor generate examples, '
                                               'and it is deliberately '
                                               'distinct from '
                                               'priority7-editorial-review, '
                                               'priority7-reference-analysis '
                                               'and '
                                               'priority7-example-generation. '
                                               'Corroboration by this '
                                               'actor means one further '
                                               'independent nonhuman '
                                               'pass agreed; it is never '
                                               'native-speaker review, '
                                               'professional linguistic '
                                               'review or human '
                                               'editorial review.'}}


E1_GENERIC_NOTE = ('Final editorial review round: D1 recommended acceptance, blind D2 '
 'corroborated independently, D3 adjudicated. Accepted against the '
 'post-D3.1 tier-2 scope.')


E1_SPECIAL_ROWS = {'vp-p-dziekowac-thank-dative-recipient-za-accusative-057197dd300f': {'note': 'Final '
                                                                              'editorial '
                                                                              'review '
                                                                              'round: '
                                                                              'blind '
                                                                              'D2 '
                                                                              'raised '
                                                                              'a '
                                                                              'blocking '
                                                                              'objection '
                                                                              'to '
                                                                              'the '
                                                                              'canonical '
                                                                              'English '
                                                                              'example; '
                                                                              'D3 '
                                                                              'did '
                                                                              'not '
                                                                              'sustain '
                                                                              'it. '
                                                                              'Accepted '
                                                                              'as '
                                                                              'authored, '
                                                                              'unchanged.',
                                                                      'findings': [{'severity': 'high',
                                                                                    'summary': 'Blind '
                                                                                               'D2 '
                                                                                               'review '
                                                                                               'blocked '
                                                                                               'the '
                                                                                               'canonical '
                                                                                               'English '
                                                                                               'example '
                                                                                               'as '
                                                                                               'a '
                                                                                               'literal '
                                                                                               'case-teaching '
                                                                                               'gloss '
                                                                                               'rather '
                                                                                               'than '
                                                                                               'a '
                                                                                               'natural '
                                                                                               'standalone '
                                                                                               'translation.',
                                                                                    'resolved': True,
                                                                                    'resolutionNote': 'D3 '
                                                                                                      'adjudication '
                                                                                                      'overturned '
                                                                                                      'the '
                                                                                                      'blocker. '
                                                                                                      'The '
                                                                                                      'row '
                                                                                                      'stands '
                                                                                                      'exactly '
                                                                                                      'as '
                                                                                                      'authored '
                                                                                                      'and '
                                                                                                      'is '
                                                                                                      'byte-identical '
                                                                                                      'to '
                                                                                                      'its '
                                                                                                      'pre-D3.1 '
                                                                                                      'state '
                                                                                                      'at '
                                                                                                      'every '
                                                                                                      'scope '
                                                                                                      'tier.'}]},
 'vp-p-dbac-take-care-of-o-accusative-target-d3e3eb63129c': {'note': 'Final '
                                                                     'editorial '
                                                                     'review '
                                                                     'round: '
                                                                     'blind '
                                                                     'D2 '
                                                                     'blocked '
                                                                     'the '
                                                                     'English '
                                                                     'example '
                                                                     'collocation; '
                                                                     'D3 '
                                                                     'upheld '
                                                                     'it '
                                                                     'and '
                                                                     'D3.1 '
                                                                     'implemented '
                                                                     'the '
                                                                     'approved '
                                                                     'repair. '
                                                                     'Accepted '
                                                                     'as '
                                                                     'repaired.',
                                                             'findings': [{'severity': 'high',
                                                                           'summary': 'Blind '
                                                                                      'D2 '
                                                                                      'review '
                                                                                      'blocked '
                                                                                      'the '
                                                                                      'English '
                                                                                      'example '
                                                                                      'for '
                                                                                      'the '
                                                                                      'non-idiomatic '
                                                                                      'collocation '
                                                                                      "'look "
                                                                                      'after '
                                                                                      'my '
                                                                                      "fitness'.",
                                                                           'resolved': True,
                                                                           'resolutionNote': 'D3 '
                                                                                             'upheld '
                                                                                             'the '
                                                                                             'blocker; '
                                                                                             'D3.1 '
                                                                                             'set '
                                                                                             'examples[0].en '
                                                                                             'to '
                                                                                             "'I "
                                                                                             'work '
                                                                                             'on '
                                                                                             'my '
                                                                                             'fitness '
                                                                                             'every '
                                                                                             "day.' "
                                                                                             'The '
                                                                                             'Polish, '
                                                                                             'origin, '
                                                                                             'key '
                                                                                             'and '
                                                                                             'ID '
                                                                                             'are '
                                                                                             'unchanged.'}]},
 'vp-p-lubic-enjoy-thing-or-activity-infinitive-activity-be3742b7ce45': {'note': 'Final '
                                                                                 'editorial '
                                                                                 'review '
                                                                                 'round: '
                                                                                 'blind '
                                                                                 'D2 '
                                                                                 'blocked '
                                                                                 'the '
                                                                                 'reused '
                                                                                 'English '
                                                                                 'example; '
                                                                                 'D3 '
                                                                                 'upheld '
                                                                                 'it '
                                                                                 'canonical-only '
                                                                                 'and '
                                                                                 'D3.1 '
                                                                                 'implemented '
                                                                                 'the '
                                                                                 'approved '
                                                                                 'repair. '
                                                                                 'Accepted '
                                                                                 'as '
                                                                                 'repaired.',
                                                                         'findings': [{'severity': 'high',
                                                                                       'summary': 'Blind '
                                                                                                  'D2 '
                                                                                                  'review '
                                                                                                  'blocked '
                                                                                                  'the '
                                                                                                  'repository-reused '
                                                                                                  'English '
                                                                                                  'example '
                                                                                                  "'before "
                                                                                                  "sleep' "
                                                                                                  'as '
                                                                                                  'non-idiomatic '
                                                                                                  'and '
                                                                                                  'out '
                                                                                                  'of '
                                                                                                  'sync '
                                                                                                  'with '
                                                                                                  'its '
                                                                                                  'declared '
                                                                                                  'source '
                                                                                                  'card.',
                                                                                       'resolved': True,
                                                                                       'resolutionNote': 'D3 '
                                                                                                         'upheld '
                                                                                                         'the '
                                                                                                         'blocker '
                                                                                                         'but '
                                                                                                         'rejected '
                                                                                                         "D2's "
                                                                                                         'shipping-card '
                                                                                                         'edit; '
                                                                                                         'D3.1 '
                                                                                                         'corrected '
                                                                                                         'examples[0].en '
                                                                                                         'to '
                                                                                                         'agree '
                                                                                                         'with '
                                                                                                         'card '
                                                                                                         'a1-free-time-003, '
                                                                                                         'which '
                                                                                                         'was '
                                                                                                         'not '
                                                                                                         'modified.'}]},
 'vp-p-podobac-sie-appeal-to-nominative-stimulus-dative-experiencer-ef199e675ee9': {'note': 'Final '
                                                                                            'editorial '
                                                                                            'review '
                                                                                            'round: '
                                                                                            'blind '
                                                                                            'D2 '
                                                                                            'blocked '
                                                                                            'the '
                                                                                            'positive '
                                                                                            'Polish '
                                                                                            'learner '
                                                                                            'model; '
                                                                                            'D3 '
                                                                                            'upheld '
                                                                                            'it '
                                                                                            'and '
                                                                                            'D3.1 '
                                                                                            'implemented '
                                                                                            'the '
                                                                                            'approved '
                                                                                            'repair. '
                                                                                            'Accepted '
                                                                                            'as '
                                                                                            'repaired.',
                                                                                    'findings': [{'severity': 'high',
                                                                                                  'summary': 'Blind '
                                                                                                             'D2 '
                                                                                                             'review '
                                                                                                             'blocked '
                                                                                                             'the '
                                                                                                             'only '
                                                                                                             'positive '
                                                                                                             'Polish '
                                                                                                             'learner '
                                                                                                             'model '
                                                                                                             'for '
                                                                                                             'using '
                                                                                                             'contextually '
                                                                                                             'marked '
                                                                                                             'clitic '
                                                                                                             'order '
                                                                                                             'in '
                                                                                                             'both '
                                                                                                             'fields '
                                                                                                             'that '
                                                                                                             'carried '
                                                                                                             'it.',
                                                                                                  'resolved': True,
                                                                                                  'resolutionNote': 'D3 '
                                                                                                                    'upheld '
                                                                                                                    'the '
                                                                                                                    'blocker; '
                                                                                                                    'D3.1 '
                                                                                                                    'replaced '
                                                                                                                    'the '
                                                                                                                    'model '
                                                                                                                    'with '
                                                                                                                    "'ten "
                                                                                                                    'film '
                                                                                                                    'mi '
                                                                                                                    'się '
                                                                                                                    "podoba' "
                                                                                                                    'in '
                                                                                                                    'learnerExplanationEn '
                                                                                                                    'and '
                                                                                                                    'errorNotes[0].guidanceEn '
                                                                                                                    'only.'}]}}

#: Closed Phase 4F-E1 identity allowlist.  These are literal accepted E1
#: facts; they are never derived from the corpus being normalised.
E1_EXPECTED_PATTERN_IDS = frozenset({
    'vp-p-szukac-seek-genitive-target-71dc6eff512c',
    'vp-p-pomagac-assist-dative-recipient-9f0a375c5e81',
    'vp-p-pomagac-assist-dative-recipient-w-locative-area-1e507dcdb869',
    'vp-p-sluchac-listen-to-genitive-target-a274f84c8d93',
    'vp-p-sluchac-obey-genitive-object-674adae2dec3',
    'vp-p-czekac-wait-for-na-accusative-target-3c9ac823ecde',
    'vp-p-potrzebowac-need-genitive-object-437fafad17d2',
    'vp-p-uczyc-sie-study-genitive-subject-matter-44c5fdb95dd7',
    'vp-p-uczyc-sie-study-infinitive-skill-ab708776387e',
    'vp-p-dziekowac-thank-za-accusative-reason-fd31baa1b1ad',
    'vp-p-dziekowac-thank-dative-recipient-za-accusative-057197dd300f',
    'vp-p-placic-pay-za-accusative-goods-73c6760c091d',
    'vp-p-placic-pay-instrumental-method-ef4313d0d5ce',
    'vp-p-uzywac-use-genitive-object-2c5cb44fe85d',
    'vp-p-prosic-request-o-accusative-request-06d776fbfd20',
    'vp-p-prosic-request-accusative-person-o-accusative-thing-b7a8d9ce1a99',
    'vp-p-interesowac-sie-be-interested-in-instrumental-topic-1ab788e84e01',
    'vp-p-dbac-take-care-of-o-accusative-target-d3e3eb63129c',
    'vp-p-tesknic-miss-za-instrumental-target-f866502502c7',
    'vp-p-rozmawiac-talk-with-z-instrumental-interlocutor-8398fa7449ca',
    'vp-p-rozmawiac-talk-with-o-locative-topic-b1c59475ac05',
    'vp-p-rozmawiac-talk-with-z-instrumental-o-locative-4e586b18cf98',
    'vp-p-bac-sie-be-afraid-of-genitive-stimulus-4f1d684a5144',
    'vp-p-bac-sie-worry-about-o-accusative-concern-c4b9b8d6811b',
    'vp-p-byc-predicate-role-instrumental-predicate-3b90a83fbb30',
    'vp-p-znac-be-acquainted-with-accusative-object-379e19b36299',
    'vp-p-lubic-enjoy-thing-or-activity-accusative-object-7e585a50878f',
    'vp-p-lubic-enjoy-thing-or-activity-infinitive-activity-be3742b7ce45',
    'vp-p-mowic-tell-content-dative-recipient-accusative-content-2f2b1add1960',
    'vp-p-mowic-tell-content-dative-recipient-ze-clause-a01ddc4a4736',
    'vp-p-pytac-ask-for-information-o-accusative-topic-c89674d989d8',
    'vp-p-pytac-ask-for-information-accusative-person-o-accusative-topic-841b41ed735a',
    'vp-p-widziec-perceive-visually-accusative-object-80b697e51432',
    'vp-p-miec-possess-accusative-object-7181f802bd57',
    'vp-p-myslec-think-about-o-locative-topic-edf0461e0dd2',
    'vp-p-znalezc-find-accusative-object-d80c52211462',
    'vp-p-podobac-sie-appeal-to-nominative-stimulus-dative-experiencer-ef199e675ee9',
    'vp-p-ufac-trust-dative-object-10988adac8cd',
    'vp-p-wierzyc-have-trust-dative-object-f38bb3e72123',
    'vp-p-wierzyc-have-trust-w-accusative-target-6561408ea8d1',
    'vp-p-zajmowac-sie-occupation-activity-instrumental-topic-3321df3f989e',
    'vp-p-zajmowac-sie-look-after-person-instrumental-object-6f93facbd939',
    'vp-p-opiekowac-sie-care-for-instrumental-object-8aa6f0a91e5b',
    'vp-p-zalezec-depend-on-od-genitive-source-1ad29f7a1318',
    'vp-p-zalezec-matter-to-someone-dative-experiencer-na-locative-1fc4131471cc',
})

#: Exact accepted post-D3.1 tier-2 digest for every E1 identity.
E1_EXPECTED_SCOPE_DIGESTS = {
    'vp-p-szukac-seek-genitive-target-71dc6eff512c': 'sha256:5e716fa9446cbf4820d46c19918848efb959cca2e01d4ac187019d4864991f2f',
    'vp-p-pomagac-assist-dative-recipient-9f0a375c5e81': 'sha256:bf03e7e0743d3a52a610fc4f28b403f83fd455c44000ada28f9a15e87232f21a',
    'vp-p-pomagac-assist-dative-recipient-w-locative-area-1e507dcdb869': 'sha256:660ea958f2b1c84eaf6e77bfebd8b7bda3b5049587a2a8ece154963c17c28c76',
    'vp-p-sluchac-listen-to-genitive-target-a274f84c8d93': 'sha256:5712ed57f40c3602f7fff60d61ca382ed21cca7a12033b8e69ad2b3bbfa85325',
    'vp-p-sluchac-obey-genitive-object-674adae2dec3': 'sha256:8d0b52e383e19191951e7e691ba31aff7cf55acc72328c0771abb7ebf7b71ebd',
    'vp-p-czekac-wait-for-na-accusative-target-3c9ac823ecde': 'sha256:a7148641f76c36cf87b99ab517d09df83f430b2b9922ee4e3d417c292ebcd130',
    'vp-p-potrzebowac-need-genitive-object-437fafad17d2': 'sha256:3411ceb84a83e77faec756d442456c33eebc8c187ddec6fe0cc0e765c5460ac3',
    'vp-p-uczyc-sie-study-genitive-subject-matter-44c5fdb95dd7': 'sha256:63a6d410e0d2b25b7e042de9d41a16629b2128dc7b542de9d34555287c6ba413',
    'vp-p-uczyc-sie-study-infinitive-skill-ab708776387e': 'sha256:06840919d0bdcfbc53772098958f2c2d8ac6adbbdf7ee9de01198351773f62ad',
    'vp-p-dziekowac-thank-za-accusative-reason-fd31baa1b1ad': 'sha256:1a69d07c0af7435fdf882e050142b4124ded299e461bbed03454180a81b23340',
    'vp-p-dziekowac-thank-dative-recipient-za-accusative-057197dd300f': 'sha256:a08ed8e55e2ab36fe9f80c4f46e66bc60c10355a34b2bf31327c7625c67a0a80',
    'vp-p-placic-pay-za-accusative-goods-73c6760c091d': 'sha256:1afa6474f762eb1f7d1161801827db205c9622f165322be26e1b662b96abba4d',
    'vp-p-placic-pay-instrumental-method-ef4313d0d5ce': 'sha256:59a16c026b9e0950d2c75a3fa14c2edce6df8a19ee9e42dd0c47f63af33b0245',
    'vp-p-uzywac-use-genitive-object-2c5cb44fe85d': 'sha256:a9d5aef1cac74a27bebea0a8446f2eec07b2546a0b30232cd588da73d187e435',
    'vp-p-prosic-request-o-accusative-request-06d776fbfd20': 'sha256:69bd1a0167cd7ac5d213e3fd4e2b9bc2108aa0635b9424bc63490dd03c4590dd',
    'vp-p-prosic-request-accusative-person-o-accusative-thing-b7a8d9ce1a99': 'sha256:71d419a22bff13515b333cc3765f74eeee57a2c5574c363c430a2af21c872823',
    'vp-p-interesowac-sie-be-interested-in-instrumental-topic-1ab788e84e01': 'sha256:cf7887b3bff92d61f42dda307c2030603dae12af9893c7aa3f47fd6a63cac3e9',
    'vp-p-dbac-take-care-of-o-accusative-target-d3e3eb63129c': 'sha256:0a73a863157cefe410c707afa55c9249224eff5a19217788e1b4363a50f65038',
    'vp-p-tesknic-miss-za-instrumental-target-f866502502c7': 'sha256:64524cb299e7f3a2125b8c59da77eefccc51f429e29183e3ca899e35c543e7f5',
    'vp-p-rozmawiac-talk-with-z-instrumental-interlocutor-8398fa7449ca': 'sha256:ca3f46bc7ffd4d223352019d555d91df2e046de553042e57230f4582b42f959b',
    'vp-p-rozmawiac-talk-with-o-locative-topic-b1c59475ac05': 'sha256:e268942eac8dfedde00e5b08dca41da1fa8176e92db5789bd45472d352e6c2ba',
    'vp-p-rozmawiac-talk-with-z-instrumental-o-locative-4e586b18cf98': 'sha256:65816700a113eafe5ba3012d2863af3c85df4b3e7141674426dbaa918fe51f1c',
    'vp-p-bac-sie-be-afraid-of-genitive-stimulus-4f1d684a5144': 'sha256:4481113726c088065a7f0aaeb817216be026cbb9ef9f6fbcb96493875acf5a55',
    'vp-p-bac-sie-worry-about-o-accusative-concern-c4b9b8d6811b': 'sha256:123fc42dcc69d4d997f7d2a64144de8c630105fc1148cb83db73b9ad29fe6c26',
    'vp-p-byc-predicate-role-instrumental-predicate-3b90a83fbb30': 'sha256:5a8c8d36bc1a0031c34e63a7eb3b85f3883cde91936bab66e15a265b01123fe2',
    'vp-p-znac-be-acquainted-with-accusative-object-379e19b36299': 'sha256:edf334b37733d060d1dd54713838e57e783a810cad15297ac96340b7f5d20dc2',
    'vp-p-lubic-enjoy-thing-or-activity-accusative-object-7e585a50878f': 'sha256:7e69ef7fa90872760b9ea1e37fc0ea176f7576246cd9e9f499b7e9330cdd4ede',
    'vp-p-lubic-enjoy-thing-or-activity-infinitive-activity-be3742b7ce45': 'sha256:c3048bd0a53d6c9d079b224769f48d153b90d2f2321ddaf52cf2c4fa348e72ca',
    'vp-p-mowic-tell-content-dative-recipient-accusative-content-2f2b1add1960': 'sha256:be4cecd0d8a46882fe783c4bfb11a3eb1c145d0e947bdb04245f6f7fff332012',
    'vp-p-mowic-tell-content-dative-recipient-ze-clause-a01ddc4a4736': 'sha256:ffd4265d1bb231c05615399b3830307be9a68fc694f5998a6dd237fef8c27c52',
    'vp-p-pytac-ask-for-information-o-accusative-topic-c89674d989d8': 'sha256:ef4b0d243f3fd50041ac2eb850f3641a99797d71331142449675aa94a7c3c7fc',
    'vp-p-pytac-ask-for-information-accusative-person-o-accusative-topic-841b41ed735a': 'sha256:dca644f3a9f2d8899bb17ae98640de5694447f69b03dd24afbc23081a0423dca',
    'vp-p-widziec-perceive-visually-accusative-object-80b697e51432': 'sha256:9c5ab6f466b2e7c1136ce5dd02dd9ea2d4acdb1e5041e496d7d62797cd9fcab1',
    'vp-p-miec-possess-accusative-object-7181f802bd57': 'sha256:181040f8007f772c44b5b81584fbd9d5744f7fdf4c1785e4b953d36a58f2f128',
    'vp-p-myslec-think-about-o-locative-topic-edf0461e0dd2': 'sha256:dcb5046c21990eada062f991521c0d32be745ecec9fb0a91b0d0a7b208f55fc7',
    'vp-p-znalezc-find-accusative-object-d80c52211462': 'sha256:ec1a17385d91e5a7fee8fa6f6f45df96ce6b4a0c32a694eec463a3658546f459',
    'vp-p-podobac-sie-appeal-to-nominative-stimulus-dative-experiencer-ef199e675ee9': 'sha256:1e9bc9735bade2c87d6594a2f96de2d982b69dcfd6c2238697d2a18564e9e06e',
    'vp-p-ufac-trust-dative-object-10988adac8cd': 'sha256:024d43b443215b5fd2fc7c25896bd6fe8f6216b723741ecd9ec6e9b60b6b1b92',
    'vp-p-wierzyc-have-trust-dative-object-f38bb3e72123': 'sha256:b982bc9a16702034af3b284c2499ae10cc2fcb54548b2d893b5b8965e21a2f37',
    'vp-p-wierzyc-have-trust-w-accusative-target-6561408ea8d1': 'sha256:953624e7dbc93f30127aeb511e4852f532a1fa7a0de194bb9cc0ca5425471e06',
    'vp-p-zajmowac-sie-occupation-activity-instrumental-topic-3321df3f989e': 'sha256:441143ff34875fd8c61ddc708a2bff26623991d37618d7eb4993fe522fe68676',
    'vp-p-zajmowac-sie-look-after-person-instrumental-object-6f93facbd939': 'sha256:2d1f19426dcf4b5dcdb57070c968b6ef124ba80ce28f88799ba2c2aaccafa2bd',
    'vp-p-opiekowac-sie-care-for-instrumental-object-8aa6f0a91e5b': 'sha256:e594cbae2316369e805b284ff14aa95f485a2d2769c81a3c9cafb38b55f11dbe',
    'vp-p-zalezec-depend-on-od-genitive-source-1ad29f7a1318': 'sha256:045fea80c132a5055c776ab94e66f531fbf1f7edf1adce1fb12b0304c9e53851',
    'vp-p-zalezec-matter-to-someone-dative-experiencer-na-locative-1fc4131471cc': 'sha256:bf55e1a1ac1c4335a9d2eefcd8503858192c01c9e2cb272d2626e6c79d8cd4b4',
}

E1_PRIOR_REVIEW_STATE = "reference-verified"
E1_FINAL_REVIEW_STATE = "editorial-reviewed"
E1_SCOPE_TIER = "native-linguistic"
E1_SCOPE_VERSION = 1
E1_DECISION = "accept"

# Fail at import time if either independently pinned collection drifts.
assert len(E1_EXPECTED_PATTERN_IDS) == 45
assert E1_EXPECTED_PATTERN_IDS == frozenset(E1_EXPECTED_SCOPE_DIGESTS)
assert frozenset(E1_SPECIAL_ROWS) <= E1_EXPECTED_PATTERN_IDS

#: The exact registry text Phase 4F-E1 inserted into the context file,
#: as one contiguous well-formed block of two records.
E1_CONTEXT_ACTOR_BLOCK = ('    "priority7-editorial-corroboration": {\n'
 '      "human": false,\n'
 '      "kind": "editorial-review-workflow",\n'
 '      "roles": ["editorial-review"],\n'
 '      "namedInPhase": "Priority 7 Phase 4F-E1",\n'
 '      "note": "Nonhuman editorial-review workflow, registered as the '
 "independent corroborator required by the solo chain's tier-2 "
 'acceptance rule. Not a person, not a native speaker, not a linguist '
 'and not a reviewer identity. It is the identity of the blind second '
 'editorial pass run in Phase 4F-D2, which reviewed the same 45 rows '
 'without sight of the Phase 4F-D1 pass and returned 41 ACCEPT and 4 '
 'CHANGES NEEDED. Holds the editorial-review role only, so it can '
 'neither reference-verify nor generate examples, and it is deliberately '
 'distinct from priority7-editorial-review, priority7-reference-analysis '
 'and priority7-example-generation. Corroboration by this actor means '
 'one further independent nonhuman pass agreed; it is never '
 'native-speaker review, professional linguistic review or human '
 'editorial review."\n'
 '    },\n'
 '    "priority7-editorial-review": {\n'
 '      "human": false,\n'
 '      "kind": "editorial-review-workflow",\n'
 '      "roles": ["editorial-review"],\n'
 '      "namedInPhase": "Priority 7 Phase 4F-E1",\n'
 '      "note": "Nonhuman editorial-review workflow. Not a person, not a '
 'native speaker, not a linguist and not a reviewer identity: it is the '
 "identity under which the project's own tier-2 editorial review of the "
 'learner-facing treatment was performed. It records only that that '
 'workflow ran against the final post-D3.1 corpus; it supplies no '
 'native-speaker judgement and no professional linguistic authority. '
 'Holds the editorial-review role only, so it can neither '
 'reference-verify nor generate examples, and it is deliberately '
 'distinct from priority7-reference-analysis and '
 'priority7-example-generation. editorial-reviewed therefore means the '
 'recorded learner-facing treatment passed two independent nonhuman '
 'editorial passes against the current tier-2 scope digest; it never '
 'means human review, and product approval remains human, mandatory and '
 'unperformed.",\n'
 '      "auditMetadata": {\n'
 '        "runNote": "Private audit trail for the maintainer. The '
 'substantive review this actor records is the Phase 4F-D1 primary '
 'editorial pass over all 45 rows, which returned 45/45 acceptance '
 'recommendations with 23 ACCEPT and 22 ACCEPT WITH NOTE. Blind '
 'corroboration is Phase 4F-D2, recorded separately as '
 'priority7-editorial-corroboration. The four rows the two passes '
 'disagreed on were resolved by the Phase 4F-D3 adjudication and, where '
 'upheld, implemented by Phase 4F-D3.1. Nothing in this object is part '
 'of the stable actor identity and no release validity depends on it."\n'
 '      }\n'
 '    },\n')


def iter_patterns(corpus):
    """Yield ``(lemma, meaning, pattern)`` in document order."""
    for lemma in corpus.get("lemmas", []):
        for meaning in lemma.get("meanings", []):
            for pattern in meaning.get("patterns", []):
                yield lemma, meaning, pattern


def approved_e1_event(pattern_id):
    """Return the statically pinned event E1 added to ``pattern_id``.

    ``pattern_id`` must be one of the 45 literal E1 identities.  In
    particular, this function never reads a live lemma, meaning, pattern or
    event to decide what the approved transition was.
    """
    if pattern_id not in E1_EXPECTED_PATTERN_IDS:
        raise KeyError(f"pattern identity is outside Phase 4F-E1: {pattern_id!r}")
    row = E1_SPECIAL_ROWS.get(pattern_id)
    event = {
        "kind": "editorial-review",
        "decision": E1_DECISION,
        "scopeVersion": E1_SCOPE_VERSION,
        "scopeDigest": E1_EXPECTED_SCOPE_DIGESTS[pattern_id],
        "actorRef": E1_EDITORIAL_ACTOR,
        "corroboratingActorRefs": [E1_CORROBORATING_ACTOR],
        "reviewedAt": E1_REVIEWED_AT,
        "note": row["note"] if row else E1_GENERIC_NOTE,
    }
    if row and row.get("findings"):
        event["findings"] = copy.deepcopy(row["findings"])
    return event


def without_phase_4fe1_editorial_review(corpus):
    """Return a copy of ``corpus`` with the 45 E1 acceptances reverted.

    A pattern is normalised only when its ID is in the literal 45-identity
    allowlist, its state is exactly E1's final state, and its history contains
    exactly one byte-equal pinned acceptance for that ID.  A later state,
    duplicate event, changed finding, repinned digest or non-E1 identity is
    left wholly visible.
    """
    corpus = copy.deepcopy(corpus)
    for _lemma, _meaning, pattern in iter_patterns(corpus):
        pattern_id = pattern.get("id")
        if pattern_id not in E1_EXPECTED_PATTERN_IDS:
            continue
        if pattern.get("reviewState") != E1_FINAL_REVIEW_STATE:
            continue
        events = pattern.get("reviewEvents")
        if not isinstance(events, list):
            continue
        expected = approved_e1_event(pattern_id)
        matches = [index for index, event in enumerate(events)
                   if event == expected]
        if len(matches) != 1:
            # Zero: nothing approved to revert.  More than one: a duplicate
            # acceptance, which this normaliser must never absorb.
            continue
        events.pop(matches[0])
        pattern["reviewState"] = E1_PRIOR_REVIEW_STATE
    return corpus


def without_phase_4fe1_actors(context):
    """Return a copy of ``context`` with the E1 registry work reverted.

    Each actor record is removed only when it is byte-equal to the approved
    record, and the notice paragraph only when it is still the exact
    approved suffix.  Any edit to either survives.
    """
    context = copy.deepcopy(context)
    registry = context.get("editorialActorRegistry")
    if isinstance(registry, dict):
        for key, record in E1_ACTORS.items():
            if registry.get(key) == record:
                del registry[key]
    notice = context.get("contextNotice")
    if (isinstance(notice, str) and
            notice.endswith(E1_CONTEXT_NOTICE_SUFFIX)):
        context["contextNotice"] = notice[:-len(E1_CONTEXT_NOTICE_SUFFIX)]
    return context


def without_phase_4fe1_corpus_text(text):
    """Reconstruct the corpus file text as it stood before Phase 4F-E1.

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
            "4F-E1 text normaliser cannot reconstruct it safely")
    return json.dumps(
        without_phase_4fe1_editorial_review(document),
        indent=2, ensure_ascii=False) + "\n"


def without_phase_4fe1_context_text(text):
    """Reconstruct the context file text as it stood before Phase 4F-E1.

    Byte surgery on the two exact blocks Phase 4F-E1 inserted -- the actor
    records and the appended notice paragraph -- so the result keeps the
    file's hand-maintained formatting exactly.  Each block must appear
    exactly once; an edit to either leaves it unrecognised and the caller's
    byte comparison then fails, which is the intent.
    """
    for block in (E1_CONTEXT_ACTOR_BLOCK, E1_CONTEXT_NOTICE_SUFFIX):
        if text.count(block) == 1:
            text = text.replace(block, "", 1)
    return text
