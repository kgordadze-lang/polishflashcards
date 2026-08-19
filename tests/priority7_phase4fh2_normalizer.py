"""Phase 4F-H2 normalisation, shared by every historical Priority 7 suite.

Phase 4F-H2 completed the learner-facing content of the Priority 7 corpus
under a correction plan the product owner authorized on 2026-08-18.  It did
three things and nothing else:

*   it added an English gloss to every Polish illustration quoted inside a
    learner-facing English prose field -- 55 illustrations across 54 fields on
    42 patterns;
*   it gave the 16 patterns that had no example exactly one example each, 2
    resolved from the repository index and 14 drafted by
    ``priority7-example-generation``, taking the corpus to 45 examples on 45
    patterns; and
*   it re-entered the editorial chain on the 44 patterns whose content moved,
    appending one owner-authorized ``correction`` on the 42 whose existing
    prose changed, then an ``editorial-review`` change request and a fresh
    ``editorial-review`` acceptance bound to the recomputed tier-2 digest.

Those 44 patterns therefore stand at ``editorial-reviewed`` and their 45
historical product approvals, preserved untouched, no longer cover their
current tier-3 scope.  No reference verification and no product approval was
created, altered or removed, no existing example was edited, no registry
changed, and ``vp-p-zajmowac-sie-look-after-person-instrumental-object-6f93facbd939``
was not touched at all and remains ``approved``.

Every historical suite states its claims over the corpus and context with
that content work reverted.  H2 is the newest layer, so compose it *innermost*
-- it must come off before Phase 4F-F2's approvals, which must come off before
Phase 4F-E1's editorial review::

    E1.without_phase_4fe1_editorial_review(
        F2.without_phase_4ff2_product_approval(
            H2.without_phase_4fh2_content_completion(live_corpus)))

    E1.without_phase_4fe1_actors(
        F2.without_phase_4ff2_reviewer(
            H2.without_phase_4fh2_context(live_context)))

The revert is keyed on an explicit 44-identity allowlist and, for each
identity, the complete pinned H2 transition: the exact appended event
objects including their statically pinned tier-2 digests, the exact before
and after text of every rewritten prose field, and the exact new example
object.  **Nothing is derived from the corpus being normalised.**  A pattern
is reverted only when every one of those pinned facts matches exactly, so an
arbitrary wording mutation, a wrong translation, a missing or extra example,
an altered existing example, wrong example provenance, a stale or repinned
tier-2 digest, a missing correction, a correction on an unauthorised pattern,
a new reference verification, a new product approval or a wrong review state
each leaves the row wholly visible and still breaks the historical guard it
would otherwise have hidden behind.  An event on a 45th identity is outside
the allowlist and is likewise untouched.

This module is phase-owned and additive.  It imports nothing from the suites
that use it, so it can be imported from any of them without a cycle, and it
never writes to any file.
"""

from __future__ import annotations

import copy
import json

#: The date every Phase 4F-H2 event carries.
H2_REVIEWED_AT = "2026-08-18"

H2_PRIOR_REVIEW_STATE = "approved"
H2_FINAL_REVIEW_STATE = "editorial-reviewed"

#: The one pattern Phase 4F-H2 did not touch at all.
H2_UNTOUCHED_PATTERN_ID = (
    "vp-p-zajmowac-sie-look-after-person-instrumental-object-6f93facbd939"
)

#: The 44 literal identities Phase 4F-H2 changed.
H2_EXPECTED_PATTERN_IDS = frozenset(
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

#: The 42 whose existing learner-facing prose changed, and so carry a
#: correction event.
H2_TRANSLATION_PATTERN_IDS = frozenset(
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
 'vp-p-znac-be-acquainted-with-accusative-object-379e19b36299',
 'vp-p-znalezc-find-accusative-object-d80c52211462']
)

#: The 16 that gained a first example.
H2_EXAMPLE_PATTERN_IDS = frozenset(
['vp-p-bac-sie-worry-about-o-accusative-concern-c4b9b8d6811b',
 'vp-p-mowic-tell-content-dative-recipient-accusative-content-2f2b1add1960',
 'vp-p-mowic-tell-content-dative-recipient-ze-clause-a01ddc4a4736',
 'vp-p-podobac-sie-appeal-to-nominative-stimulus-dative-experiencer-ef199e675ee9',
 'vp-p-pomagac-assist-dative-recipient-9f0a375c5e81',
 'vp-p-pomagac-assist-dative-recipient-w-locative-area-1e507dcdb869',
 'vp-p-prosic-request-accusative-person-o-accusative-thing-b7a8d9ce1a99',
 'vp-p-rozmawiac-talk-with-o-locative-topic-b1c59475ac05',
 'vp-p-rozmawiac-talk-with-z-instrumental-interlocutor-8398fa7449ca',
 'vp-p-rozmawiac-talk-with-z-instrumental-o-locative-4e586b18cf98',
 'vp-p-sluchac-obey-genitive-object-674adae2dec3',
 'vp-p-ufac-trust-dative-object-10988adac8cd',
 'vp-p-wierzyc-have-trust-dative-object-f38bb3e72123',
 'vp-p-wierzyc-have-trust-w-accusative-target-6561408ea8d1',
 'vp-p-zajmowac-sie-occupation-activity-instrumental-topic-3321df3f989e',
 'vp-p-zalezec-matter-to-someone-dative-experiencer-na-locative-1fc4131471cc']
)

#: Per identity, the exact prose rewrites: path -> (before, after).
H2_FIELD_REWRITES = (
{'vp-p-bac-sie-be-afraid-of-genitive-stimulus-4f1d684a5144': {'errorNotes[0].guidanceEn': ('Bać '
                                                                                           'się '
                                                                                           'takes '
                                                                                           'the '
                                                                                           'Genitive: '
                                                                                           'boję '
                                                                                           'się '
                                                                                           'pająków.',
                                                                                           'Bać '
                                                                                           'się '
                                                                                           'takes '
                                                                                           'the '
                                                                                           'Genitive: '
                                                                                           'boję '
                                                                                           'się '
                                                                                           'pająków '
                                                                                           "(I'm "
                                                                                           'afraid '
                                                                                           'of '
                                                                                           'spiders).'),
                                                              'learnerExplanationEn': ('What '
                                                                                       'you '
                                                                                       'are '
                                                                                       'afraid '
                                                                                       'of '
                                                                                       'goes '
                                                                                       'in '
                                                                                       'the '
                                                                                       'Genitive: '
                                                                                       'boję '
                                                                                       'się '
                                                                                       'burzy.',
                                                                                       'What '
                                                                                       'you '
                                                                                       'are '
                                                                                       'afraid '
                                                                                       'of '
                                                                                       'goes '
                                                                                       'in '
                                                                                       'the '
                                                                                       'Genitive: '
                                                                                       'boję '
                                                                                       'się '
                                                                                       'burzy '
                                                                                       "(I'm "
                                                                                       'afraid '
                                                                                       'of '
                                                                                       'the '
                                                                                       'storm).')},
 'vp-p-bac-sie-worry-about-o-accusative-concern-c4b9b8d6811b': {'learnerExplanationEn': ('To '
                                                                                         'say '
                                                                                         'who '
                                                                                         'you '
                                                                                         'worry '
                                                                                         'about, '
                                                                                         'use '
                                                                                         'o '
                                                                                         '+ '
                                                                                         'Accusative: '
                                                                                         'boję '
                                                                                         'się '
                                                                                         'o '
                                                                                         'dzieci.',
                                                                                         'To '
                                                                                         'say '
                                                                                         'who '
                                                                                         'you '
                                                                                         'worry '
                                                                                         'about, '
                                                                                         'use '
                                                                                         'o '
                                                                                         '+ '
                                                                                         'Accusative: '
                                                                                         'boję '
                                                                                         'się '
                                                                                         'o '
                                                                                         'dzieci '
                                                                                         "(I'm "
                                                                                         'worried '
                                                                                         'about '
                                                                                         'the '
                                                                                         'children).')},
 'vp-p-byc-predicate-role-instrumental-predicate-3b90a83fbb30': {'errorNotes[0].guidanceEn': ('After '
                                                                                              'być '
                                                                                              'a '
                                                                                              'role '
                                                                                              'or '
                                                                                              'profession '
                                                                                              'takes '
                                                                                              'the '
                                                                                              'Instrumental: '
                                                                                              'jestem '
                                                                                              'studentem.',
                                                                                              'After '
                                                                                              'być '
                                                                                              'a '
                                                                                              'role '
                                                                                              'or '
                                                                                              'profession '
                                                                                              'takes '
                                                                                              'the '
                                                                                              'Instrumental: '
                                                                                              'jestem '
                                                                                              'studentem '
                                                                                              "(I'm "
                                                                                              'a '
                                                                                              'student).'),
                                                                 'learnerExplanationEn': ('For '
                                                                                          'a '
                                                                                          'role '
                                                                                          'or '
                                                                                          'profession '
                                                                                          'after '
                                                                                          'być, '
                                                                                          'use '
                                                                                          'the '
                                                                                          'Instrumental: '
                                                                                          'jestem '
                                                                                          'studentem.',
                                                                                          'For '
                                                                                          'a '
                                                                                          'role '
                                                                                          'or '
                                                                                          'profession '
                                                                                          'after '
                                                                                          'być, '
                                                                                          'use '
                                                                                          'the '
                                                                                          'Instrumental: '
                                                                                          'jestem '
                                                                                          'studentem '
                                                                                          "(I'm "
                                                                                          'a '
                                                                                          'student).')},
 'vp-p-czekac-wait-for-na-accusative-target-3c9ac823ecde': {'errorNotes[0].guidanceEn': ('Czekać '
                                                                                         'needs '
                                                                                         'the '
                                                                                         'preposition '
                                                                                         'na '
                                                                                         'with '
                                                                                         'the '
                                                                                         'Accusative: '
                                                                                         'czekam '
                                                                                         'na '
                                                                                         'autobus.',
                                                                                         'Czekać '
                                                                                         'needs '
                                                                                         'the '
                                                                                         'preposition '
                                                                                         'na '
                                                                                         'with '
                                                                                         'the '
                                                                                         'Accusative: '
                                                                                         'czekam '
                                                                                         'na '
                                                                                         'autobus '
                                                                                         "(I'm "
                                                                                         'waiting '
                                                                                         'for '
                                                                                         'the '
                                                                                         'bus).')},
 'vp-p-dbac-take-care-of-o-accusative-target-d3e3eb63129c': {'learnerExplanationEn': ('Use '
                                                                                      'o '
                                                                                      '+ '
                                                                                      'Accusative '
                                                                                      'for '
                                                                                      'what '
                                                                                      'you '
                                                                                      'take '
                                                                                      'care '
                                                                                      'of: '
                                                                                      'dbam '
                                                                                      'o '
                                                                                      'zdrowie.',
                                                                                      'Use '
                                                                                      'o '
                                                                                      '+ '
                                                                                      'Accusative '
                                                                                      'for '
                                                                                      'what '
                                                                                      'you '
                                                                                      'take '
                                                                                      'care '
                                                                                      'of: '
                                                                                      'dbam '
                                                                                      'o '
                                                                                      'zdrowie '
                                                                                      '(I '
                                                                                      'take '
                                                                                      'care '
                                                                                      'of '
                                                                                      'my '
                                                                                      'health).')},
 'vp-p-dziekowac-thank-dative-recipient-za-accusative-057197dd300f': {'errorNotes[0].guidanceEn': ('The '
                                                                                                   'person '
                                                                                                   'thanked '
                                                                                                   'is '
                                                                                                   'Dative: '
                                                                                                   'dziękuję '
                                                                                                   'mamie '
                                                                                                   'za '
                                                                                                   'pomoc.',
                                                                                                   'The '
                                                                                                   'person '
                                                                                                   'thanked '
                                                                                                   'is '
                                                                                                   'Dative: '
                                                                                                   'dziękuję '
                                                                                                   'mamie '
                                                                                                   'za '
                                                                                                   'pomoc '
                                                                                                   '(I '
                                                                                                   'thank '
                                                                                                   'my '
                                                                                                   'mum '
                                                                                                   'for '
                                                                                                   'the '
                                                                                                   'help).'),
                                                                      'learnerExplanationEn': ('Name '
                                                                                               'the '
                                                                                               'person '
                                                                                               'in '
                                                                                               'the '
                                                                                               'Dative '
                                                                                               'and '
                                                                                               'the '
                                                                                               'reason '
                                                                                               'with '
                                                                                               'za '
                                                                                               '+ '
                                                                                               'Accusative: '
                                                                                               'dziękuję '
                                                                                               'komuś '
                                                                                               'za '
                                                                                               'coś.',
                                                                                               'Name '
                                                                                               'the '
                                                                                               'person '
                                                                                               'in '
                                                                                               'the '
                                                                                               'Dative '
                                                                                               'and '
                                                                                               'the '
                                                                                               'reason '
                                                                                               'with '
                                                                                               'za '
                                                                                               '+ '
                                                                                               'Accusative: '
                                                                                               'dziękuję '
                                                                                               'komuś '
                                                                                               'za '
                                                                                               'coś '
                                                                                               '(I '
                                                                                               'thank '
                                                                                               'someone '
                                                                                               'for '
                                                                                               'something).')},
 'vp-p-dziekowac-thank-za-accusative-reason-fd31baa1b1ad': {'learnerExplanationEn': ('Use '
                                                                                     'za '
                                                                                     '+ '
                                                                                     'Accusative '
                                                                                     'for '
                                                                                     'what '
                                                                                     'you '
                                                                                     'are '
                                                                                     'thanking '
                                                                                     'for: '
                                                                                     'dziękuję '
                                                                                     'za '
                                                                                     'pomoc.',
                                                                                     'Use '
                                                                                     'za '
                                                                                     '+ '
                                                                                     'Accusative '
                                                                                     'for '
                                                                                     'what '
                                                                                     'you '
                                                                                     'are '
                                                                                     'thanking '
                                                                                     'for: '
                                                                                     'dziękuję '
                                                                                     'za '
                                                                                     'pomoc '
                                                                                     '(thank '
                                                                                     'you '
                                                                                     'for '
                                                                                     'the '
                                                                                     'help).')},
 'vp-p-interesowac-sie-be-interested-in-instrumental-topic-1ab788e84e01': {'errorNotes[0].guidanceEn': ('No '
                                                                                                        'preposition: '
                                                                                                        'use '
                                                                                                        'the '
                                                                                                        'bare '
                                                                                                        'Instrumental, '
                                                                                                        'interesuję '
                                                                                                        'się '
                                                                                                        'sportem.',
                                                                                                        'No '
                                                                                                        'preposition: '
                                                                                                        'use '
                                                                                                        'the '
                                                                                                        'bare '
                                                                                                        'Instrumental, '
                                                                                                        'interesuję '
                                                                                                        'się '
                                                                                                        'sportem '
                                                                                                        "(I'm "
                                                                                                        'interested '
                                                                                                        'in '
                                                                                                        'sport).')},
 'vp-p-lubic-enjoy-thing-or-activity-accusative-object-7e585a50878f': {'learnerExplanationEn': ('For '
                                                                                                'a '
                                                                                                'thing '
                                                                                                'you '
                                                                                                'enjoy, '
                                                                                                'lubić '
                                                                                                'takes '
                                                                                                'a '
                                                                                                'plain '
                                                                                                'Accusative '
                                                                                                'object: '
                                                                                                'lubię '
                                                                                                'kawę.',
                                                                                                'For '
                                                                                                'a '
                                                                                                'thing '
                                                                                                'you '
                                                                                                'enjoy, '
                                                                                                'lubić '
                                                                                                'takes '
                                                                                                'a '
                                                                                                'plain '
                                                                                                'Accusative '
                                                                                                'object: '
                                                                                                'lubię '
                                                                                                'kawę '
                                                                                                '(I '
                                                                                                'like '
                                                                                                'coffee).')},
 'vp-p-lubic-enjoy-thing-or-activity-infinitive-activity-be3742b7ce45': {'learnerExplanationEn': ('To '
                                                                                                  'say '
                                                                                                  'which '
                                                                                                  'activity '
                                                                                                  'you '
                                                                                                  'enjoy, '
                                                                                                  'use '
                                                                                                  'an '
                                                                                                  'infinitive: '
                                                                                                  'lubię '
                                                                                                  'czytać.',
                                                                                                  'To '
                                                                                                  'say '
                                                                                                  'which '
                                                                                                  'activity '
                                                                                                  'you '
                                                                                                  'enjoy, '
                                                                                                  'use '
                                                                                                  'an '
                                                                                                  'infinitive: '
                                                                                                  'lubię '
                                                                                                  'czytać '
                                                                                                  '(I '
                                                                                                  'like '
                                                                                                  'reading).')},
 'vp-p-miec-possess-accusative-object-7181f802bd57': {'learnerExplanationEn': ('Mieć '
                                                                               'takes '
                                                                               'a '
                                                                               'plain '
                                                                               'Accusative '
                                                                               'object: '
                                                                               'mam '
                                                                               'psa.',
                                                                               'Mieć '
                                                                               'takes '
                                                                               'a '
                                                                               'plain '
                                                                               'Accusative '
                                                                               'object: '
                                                                               'mam '
                                                                               'psa '
                                                                               '(I '
                                                                               'have '
                                                                               'a '
                                                                               'dog).')},
 'vp-p-mowic-tell-content-dative-recipient-accusative-content-2f2b1add1960': {'learnerExplanationEn': ('The '
                                                                                                       'thing '
                                                                                                       'told '
                                                                                                       'is '
                                                                                                       'Accusative '
                                                                                                       'and '
                                                                                                       'the '
                                                                                                       'person '
                                                                                                       'told '
                                                                                                       'is '
                                                                                                       'Dative; '
                                                                                                       'the '
                                                                                                       'person '
                                                                                                       'can '
                                                                                                       'be '
                                                                                                       'left '
                                                                                                       'out: '
                                                                                                       'mówię '
                                                                                                       'prawdę.',
                                                                                                       'The '
                                                                                                       'thing '
                                                                                                       'told '
                                                                                                       'is '
                                                                                                       'Accusative '
                                                                                                       'and '
                                                                                                       'the '
                                                                                                       'person '
                                                                                                       'told '
                                                                                                       'is '
                                                                                                       'Dative; '
                                                                                                       'the '
                                                                                                       'person '
                                                                                                       'can '
                                                                                                       'be '
                                                                                                       'left '
                                                                                                       'out: '
                                                                                                       'mówię '
                                                                                                       'prawdę '
                                                                                                       "(I'm "
                                                                                                       'telling '
                                                                                                       'the '
                                                                                                       'truth).')},
 'vp-p-mowic-tell-content-dative-recipient-ze-clause-a01ddc4a4736': {'learnerExplanationEn': ('The '
                                                                                              'same '
                                                                                              'meaning '
                                                                                              'with '
                                                                                              'clause '
                                                                                              'content: '
                                                                                              'że '
                                                                                              'introduces '
                                                                                              'what '
                                                                                              'is '
                                                                                              'said, '
                                                                                              'and '
                                                                                              'the '
                                                                                              'person, '
                                                                                              'if '
                                                                                              'named, '
                                                                                              'is '
                                                                                              'Dative: '
                                                                                              'mówię, '
                                                                                              'że '
                                                                                              'to '
                                                                                              'prawda.',
                                                                                              'The '
                                                                                              'same '
                                                                                              'meaning '
                                                                                              'with '
                                                                                              'clause '
                                                                                              'content: '
                                                                                              'że '
                                                                                              'introduces '
                                                                                              'what '
                                                                                              'is '
                                                                                              'said, '
                                                                                              'and '
                                                                                              'the '
                                                                                              'person, '
                                                                                              'if '
                                                                                              'named, '
                                                                                              'is '
                                                                                              'Dative: '
                                                                                              'mówię, '
                                                                                              'że '
                                                                                              'to '
                                                                                              'prawda '
                                                                                              '(I '
                                                                                              'say '
                                                                                              'that '
                                                                                              "it's "
                                                                                              'true).')},
 'vp-p-myslec-think-about-o-locative-topic-edf0461e0dd2': {'errorNotes[0].guidanceEn': ('After '
                                                                                        'o '
                                                                                        'in '
                                                                                        'this '
                                                                                        'meaning '
                                                                                        'use '
                                                                                        'the '
                                                                                        'Locative: '
                                                                                        'myślę '
                                                                                        'o '
                                                                                        'wakacjach.',
                                                                                        'After '
                                                                                        'o '
                                                                                        'in '
                                                                                        'this '
                                                                                        'meaning '
                                                                                        'use '
                                                                                        'the '
                                                                                        'Locative: '
                                                                                        'myślę '
                                                                                        'o '
                                                                                        'wakacjach '
                                                                                        "(I'm "
                                                                                        'thinking '
                                                                                        'about '
                                                                                        'the '
                                                                                        'holidays).'),
                                                           'learnerExplanationEn': ('Use '
                                                                                    'o '
                                                                                    '+ '
                                                                                    'Locative '
                                                                                    'for '
                                                                                    'what '
                                                                                    'you '
                                                                                    'think '
                                                                                    'about: '
                                                                                    'myślę '
                                                                                    'o '
                                                                                    'wakacjach.',
                                                                                    'Use '
                                                                                    'o '
                                                                                    '+ '
                                                                                    'Locative '
                                                                                    'for '
                                                                                    'what '
                                                                                    'you '
                                                                                    'think '
                                                                                    'about: '
                                                                                    'myślę '
                                                                                    'o '
                                                                                    'wakacjach '
                                                                                    "(I'm "
                                                                                    'thinking '
                                                                                    'about '
                                                                                    'the '
                                                                                    'holidays).')},
 'vp-p-opiekowac-sie-care-for-instrumental-object-8aa6f0a91e5b': {'errorNotes[0].guidanceEn': ('No '
                                                                                               'preposition: '
                                                                                               'use '
                                                                                               'the '
                                                                                               'bare '
                                                                                               'Instrumental, '
                                                                                               'opiekuję '
                                                                                               'się '
                                                                                               'babcią.',
                                                                                               'No '
                                                                                               'preposition: '
                                                                                               'use '
                                                                                               'the '
                                                                                               'bare '
                                                                                               'Instrumental, '
                                                                                               'opiekuję '
                                                                                               'się '
                                                                                               'babcią '
                                                                                               '(I '
                                                                                               'look '
                                                                                               'after '
                                                                                               'my '
                                                                                               'grandmother).'),
                                                                  'learnerExplanationEn': ('Who '
                                                                                           'or '
                                                                                           'what '
                                                                                           'you '
                                                                                           'look '
                                                                                           'after '
                                                                                           'takes '
                                                                                           'the '
                                                                                           'bare '
                                                                                           'Instrumental: '
                                                                                           'opiekuję '
                                                                                           'się '
                                                                                           'babcią.',
                                                                                           'Who '
                                                                                           'or '
                                                                                           'what '
                                                                                           'you '
                                                                                           'look '
                                                                                           'after '
                                                                                           'takes '
                                                                                           'the '
                                                                                           'bare '
                                                                                           'Instrumental: '
                                                                                           'opiekuję '
                                                                                           'się '
                                                                                           'babcią '
                                                                                           '(I '
                                                                                           'look '
                                                                                           'after '
                                                                                           'my '
                                                                                           'grandmother).')},
 'vp-p-placic-pay-instrumental-method-ef4313d0d5ce': {'errorNotes[0].guidanceEn': ('No '
                                                                                   'preposition '
                                                                                   'here: '
                                                                                   'the '
                                                                                   'means '
                                                                                   'of '
                                                                                   'payment '
                                                                                   'is '
                                                                                   'a '
                                                                                   'bare '
                                                                                   'Instrumental, '
                                                                                   'płacę '
                                                                                   'kartą.',
                                                                                   'No '
                                                                                   'preposition '
                                                                                   'here: '
                                                                                   'the '
                                                                                   'means '
                                                                                   'of '
                                                                                   'payment '
                                                                                   'is '
                                                                                   'a '
                                                                                   'bare '
                                                                                   'Instrumental, '
                                                                                   'płacę '
                                                                                   'kartą '
                                                                                   "(I'm "
                                                                                   'paying '
                                                                                   'by '
                                                                                   'card).'),
                                                      'learnerExplanationEn': ('To '
                                                                               'say '
                                                                               'how '
                                                                               'you '
                                                                               'pay, '
                                                                               'use '
                                                                               'the '
                                                                               'bare '
                                                                               'Instrumental: '
                                                                               'płacę '
                                                                               'kartą, '
                                                                               'płacę '
                                                                               'gotówką.',
                                                                               'To '
                                                                               'say '
                                                                               'how '
                                                                               'you '
                                                                               'pay, '
                                                                               'use '
                                                                               'the '
                                                                               'bare '
                                                                               'Instrumental: '
                                                                               'płacę '
                                                                               'kartą '
                                                                               "(I'm "
                                                                               'paying '
                                                                               'by '
                                                                               'card), '
                                                                               'płacę '
                                                                               'gotówką '
                                                                               "(I'm "
                                                                               'paying '
                                                                               'in '
                                                                               'cash).')},
 'vp-p-placic-pay-za-accusative-goods-73c6760c091d': {'learnerExplanationEn': ('Use '
                                                                               'za '
                                                                               '+ '
                                                                               'Accusative '
                                                                               'for '
                                                                               'what '
                                                                               'you '
                                                                               'are '
                                                                               'paying '
                                                                               'for: '
                                                                               'płacę '
                                                                               'za '
                                                                               'bilet.',
                                                                               'Use '
                                                                               'za '
                                                                               '+ '
                                                                               'Accusative '
                                                                               'for '
                                                                               'what '
                                                                               'you '
                                                                               'are '
                                                                               'paying '
                                                                               'for: '
                                                                               'płacę '
                                                                               'za '
                                                                               'bilet '
                                                                               "(I'm "
                                                                               'paying '
                                                                               'for '
                                                                               'a '
                                                                               'ticket).')},
 'vp-p-podobac-sie-appeal-to-nominative-stimulus-dative-experiencer-ef199e675ee9': {'errorNotes[0].guidanceEn': ('The '
                                                                                                                 'thing '
                                                                                                                 'liked '
                                                                                                                 'is '
                                                                                                                 'the '
                                                                                                                 'subject '
                                                                                                                 'and '
                                                                                                                 'the '
                                                                                                                 'person '
                                                                                                                 'is '
                                                                                                                 'Dative: '
                                                                                                                 'ten '
                                                                                                                 'film '
                                                                                                                 'mi '
                                                                                                                 'się '
                                                                                                                 'podoba.',
                                                                                                                 'The '
                                                                                                                 'thing '
                                                                                                                 'liked '
                                                                                                                 'is '
                                                                                                                 'the '
                                                                                                                 'subject '
                                                                                                                 'and '
                                                                                                                 'the '
                                                                                                                 'person '
                                                                                                                 'is '
                                                                                                                 'Dative: '
                                                                                                                 'ten '
                                                                                                                 'film '
                                                                                                                 'mi '
                                                                                                                 'się '
                                                                                                                 'podoba '
                                                                                                                 '(I '
                                                                                                                 'like '
                                                                                                                 'this '
                                                                                                                 'film).'),
                                                                                    'learnerExplanationEn': ('The '
                                                                                                             'thing '
                                                                                                             'liked '
                                                                                                             'is '
                                                                                                             'the '
                                                                                                             'subject '
                                                                                                             'and '
                                                                                                             'the '
                                                                                                             'person '
                                                                                                             'is '
                                                                                                             'Dative: '
                                                                                                             'ten '
                                                                                                             'film '
                                                                                                             'mi '
                                                                                                             'się '
                                                                                                             'podoba.',
                                                                                                             'The '
                                                                                                             'thing '
                                                                                                             'liked '
                                                                                                             'is '
                                                                                                             'the '
                                                                                                             'subject '
                                                                                                             'and '
                                                                                                             'the '
                                                                                                             'person '
                                                                                                             'is '
                                                                                                             'Dative: '
                                                                                                             'ten '
                                                                                                             'film '
                                                                                                             'mi '
                                                                                                             'się '
                                                                                                             'podoba '
                                                                                                             '(I '
                                                                                                             'like '
                                                                                                             'this '
                                                                                                             'film).')},
 'vp-p-pomagac-assist-dative-recipient-9f0a375c5e81': {'errorNotes[0].guidanceEn': ('The '
                                                                                    'person '
                                                                                    'helped '
                                                                                    'is '
                                                                                    'Dative, '
                                                                                    'not '
                                                                                    'Accusative: '
                                                                                    'pomagam '
                                                                                    'mamie.',
                                                                                    'The '
                                                                                    'person '
                                                                                    'helped '
                                                                                    'is '
                                                                                    'Dative, '
                                                                                    'not '
                                                                                    'Accusative: '
                                                                                    'pomagam '
                                                                                    'mamie '
                                                                                    '(I '
                                                                                    'help '
                                                                                    'my '
                                                                                    'mum).')},
 'vp-p-pomagac-assist-dative-recipient-w-locative-area-1e507dcdb869': {'learnerExplanationEn': ('To '
                                                                                                'say '
                                                                                                'what '
                                                                                                'you '
                                                                                                'help '
                                                                                                'with, '
                                                                                                'add '
                                                                                                'w '
                                                                                                '+ '
                                                                                                'Locative: '
                                                                                                'pomagać '
                                                                                                'komuś '
                                                                                                'w '
                                                                                                'czymś.',
                                                                                                'To '
                                                                                                'say '
                                                                                                'what '
                                                                                                'you '
                                                                                                'help '
                                                                                                'with, '
                                                                                                'add '
                                                                                                'w '
                                                                                                '+ '
                                                                                                'Locative: '
                                                                                                'pomagać '
                                                                                                'komuś '
                                                                                                'w '
                                                                                                'czymś '
                                                                                                '(to '
                                                                                                'help '
                                                                                                'someone '
                                                                                                'with '
                                                                                                'something).')},
 'vp-p-potrzebowac-need-genitive-object-437fafad17d2': {'errorNotes[0].guidanceEn': ('Potrzebować '
                                                                                     'takes '
                                                                                     'the '
                                                                                     'Genitive: '
                                                                                     'potrzebuję '
                                                                                     'zaświadczenia.',
                                                                                     'Potrzebować '
                                                                                     'takes '
                                                                                     'the '
                                                                                     'Genitive: '
                                                                                     'potrzebuję '
                                                                                     'zaświadczenia '
                                                                                     '(I '
                                                                                     'need '
                                                                                     'a '
                                                                                     'certificate).')},
 'vp-p-prosic-request-accusative-person-o-accusative-thing-b7a8d9ce1a99': {'errorNotes[0].guidanceEn': ('The '
                                                                                                        'person '
                                                                                                        'asked '
                                                                                                        'is '
                                                                                                        'Accusative, '
                                                                                                        'not '
                                                                                                        'Dative: '
                                                                                                        'proszę '
                                                                                                        'mamę '
                                                                                                        'o '
                                                                                                        'pomoc.',
                                                                                                        'The '
                                                                                                        'person '
                                                                                                        'asked '
                                                                                                        'is '
                                                                                                        'Accusative, '
                                                                                                        'not '
                                                                                                        'Dative: '
                                                                                                        'proszę '
                                                                                                        'mamę '
                                                                                                        'o '
                                                                                                        'pomoc '
                                                                                                        '(I '
                                                                                                        'ask '
                                                                                                        'my '
                                                                                                        'mum '
                                                                                                        'for '
                                                                                                        'help).')},
 'vp-p-prosic-request-o-accusative-request-06d776fbfd20': {'learnerExplanationEn': ('Use '
                                                                                    'o '
                                                                                    '+ '
                                                                                    'Accusative '
                                                                                    'for '
                                                                                    'what '
                                                                                    'you '
                                                                                    'ask '
                                                                                    'for: '
                                                                                    'proszę '
                                                                                    'o '
                                                                                    'rachunek.',
                                                                                    'Use '
                                                                                    'o '
                                                                                    '+ '
                                                                                    'Accusative '
                                                                                    'for '
                                                                                    'what '
                                                                                    'you '
                                                                                    'ask '
                                                                                    'for: '
                                                                                    'proszę '
                                                                                    'o '
                                                                                    'rachunek '
                                                                                    '(the '
                                                                                    'bill, '
                                                                                    'please).')},
 'vp-p-pytac-ask-for-information-accusative-person-o-accusative-topic-841b41ed735a': {'errorNotes[0].guidanceEn': ('The '
                                                                                                                   'person '
                                                                                                                   'asked '
                                                                                                                   'is '
                                                                                                                   'Accusative: '
                                                                                                                   'pytam '
                                                                                                                   'mamę '
                                                                                                                   'o '
                                                                                                                   'adres.',
                                                                                                                   'The '
                                                                                                                   'person '
                                                                                                                   'asked '
                                                                                                                   'is '
                                                                                                                   'Accusative: '
                                                                                                                   'pytam '
                                                                                                                   'mamę '
                                                                                                                   'o '
                                                                                                                   'adres '
                                                                                                                   '(I '
                                                                                                                   'ask '
                                                                                                                   'my '
                                                                                                                   'mum '
                                                                                                                   'for '
                                                                                                                   'the '
                                                                                                                   'address).')},
 'vp-p-pytac-ask-for-information-o-accusative-topic-c89674d989d8': {'learnerExplanationEn': ('Use '
                                                                                             'o '
                                                                                             '+ '
                                                                                             'Accusative '
                                                                                             'for '
                                                                                             'what '
                                                                                             'you '
                                                                                             'ask '
                                                                                             'about: '
                                                                                             'pytam '
                                                                                             'o '
                                                                                             'cenę.',
                                                                                             'Use '
                                                                                             'o '
                                                                                             '+ '
                                                                                             'Accusative '
                                                                                             'for '
                                                                                             'what '
                                                                                             'you '
                                                                                             'ask '
                                                                                             'about: '
                                                                                             'pytam '
                                                                                             'o '
                                                                                             'cenę '
                                                                                             '(I '
                                                                                             'ask '
                                                                                             'about '
                                                                                             'the '
                                                                                             'price).')},
 'vp-p-rozmawiac-talk-with-o-locative-topic-b1c59475ac05': {'learnerExplanationEn': ('Use '
                                                                                     'o '
                                                                                     '+ '
                                                                                     'Locative '
                                                                                     'for '
                                                                                     'the '
                                                                                     'topic '
                                                                                     'you '
                                                                                     'talk '
                                                                                     'about: '
                                                                                     'rozmawiamy '
                                                                                     'o '
                                                                                     'pracy.',
                                                                                     'Use '
                                                                                     'o '
                                                                                     '+ '
                                                                                     'Locative '
                                                                                     'for '
                                                                                     'the '
                                                                                     'topic '
                                                                                     'you '
                                                                                     'talk '
                                                                                     'about: '
                                                                                     'rozmawiamy '
                                                                                     'o '
                                                                                     'pracy '
                                                                                     "(we're "
                                                                                     'talking '
                                                                                     'about '
                                                                                     'work).')},
 'vp-p-rozmawiac-talk-with-z-instrumental-interlocutor-8398fa7449ca': {'learnerExplanationEn': ('Use '
                                                                                                'z '
                                                                                                '+ '
                                                                                                'Instrumental '
                                                                                                'for '
                                                                                                'the '
                                                                                                'person '
                                                                                                'you '
                                                                                                'talk '
                                                                                                'to: '
                                                                                                'rozmawiam '
                                                                                                'z '
                                                                                                'koleżanką.',
                                                                                                'Use '
                                                                                                'z '
                                                                                                '+ '
                                                                                                'Instrumental '
                                                                                                'for '
                                                                                                'the '
                                                                                                'person '
                                                                                                'you '
                                                                                                'talk '
                                                                                                'to: '
                                                                                                'rozmawiam '
                                                                                                'z '
                                                                                                'koleżanką '
                                                                                                "(I'm "
                                                                                                'talking '
                                                                                                'to '
                                                                                                'a '
                                                                                                'friend).')},
 'vp-p-sluchac-listen-to-genitive-target-a274f84c8d93': {'errorNotes[0].guidanceEn': ('Słuchać '
                                                                                      'takes '
                                                                                      'the '
                                                                                      'Genitive: '
                                                                                      'słucham '
                                                                                      'muzyki.',
                                                                                      'Słuchać '
                                                                                      'takes '
                                                                                      'the '
                                                                                      'Genitive: '
                                                                                      'słucham '
                                                                                      'muzyki '
                                                                                      '(I '
                                                                                      'listen '
                                                                                      'to '
                                                                                      'music).')},
 'vp-p-sluchac-obey-genitive-object-674adae2dec3': {'learnerExplanationEn': ('In '
                                                                             'the '
                                                                             'obey '
                                                                             'sense '
                                                                             'słuchać '
                                                                             'still '
                                                                             'takes '
                                                                             'the '
                                                                             'Genitive: '
                                                                             'dziecko '
                                                                             'słucha '
                                                                             'mamy.',
                                                                             'In '
                                                                             'the '
                                                                             'obey '
                                                                             'sense '
                                                                             'słuchać '
                                                                             'still '
                                                                             'takes '
                                                                             'the '
                                                                             'Genitive: '
                                                                             'dziecko '
                                                                             'słucha '
                                                                             'mamy '
                                                                             '(the '
                                                                             'child '
                                                                             'obeys '
                                                                             'their '
                                                                             'mum).')},
 'vp-p-szukac-seek-genitive-target-71dc6eff512c': {'errorNotes[0].guidanceEn': ('Szukać '
                                                                                'takes '
                                                                                'the '
                                                                                'Genitive, '
                                                                                'not '
                                                                                'the '
                                                                                'Accusative: '
                                                                                'szukam '
                                                                                'kawiarni.',
                                                                                'Szukać '
                                                                                'takes '
                                                                                'the '
                                                                                'Genitive, '
                                                                                'not '
                                                                                'the '
                                                                                'Accusative: '
                                                                                'szukam '
                                                                                'kawiarni '
                                                                                "(I'm "
                                                                                'looking '
                                                                                'for '
                                                                                'a '
                                                                                'café).')},
 'vp-p-tesknic-miss-za-instrumental-target-f866502502c7': {'errorNotes[0].guidanceEn': ('Tęsknić '
                                                                                        'needs '
                                                                                        'za '
                                                                                        'with '
                                                                                        'the '
                                                                                        'Instrumental: '
                                                                                        'tęsknię '
                                                                                        'za '
                                                                                        'tobą.',
                                                                                        'Tęsknić '
                                                                                        'needs '
                                                                                        'za '
                                                                                        'with '
                                                                                        'the '
                                                                                        'Instrumental: '
                                                                                        'tęsknię '
                                                                                        'za '
                                                                                        'tobą '
                                                                                        '(I '
                                                                                        'miss '
                                                                                        'you).'),
                                                           'learnerExplanationEn': ('Use '
                                                                                    'za '
                                                                                    '+ '
                                                                                    'Instrumental '
                                                                                    'for '
                                                                                    'whoever '
                                                                                    'or '
                                                                                    'whatever '
                                                                                    'you '
                                                                                    'miss: '
                                                                                    'tęsknię '
                                                                                    'za '
                                                                                    'domem.',
                                                                                    'Use '
                                                                                    'za '
                                                                                    '+ '
                                                                                    'Instrumental '
                                                                                    'for '
                                                                                    'whoever '
                                                                                    'or '
                                                                                    'whatever '
                                                                                    'you '
                                                                                    'miss: '
                                                                                    'tęsknię '
                                                                                    'za '
                                                                                    'domem '
                                                                                    '(I '
                                                                                    'miss '
                                                                                    'home).')},
 'vp-p-uczyc-sie-study-genitive-subject-matter-44c5fdb95dd7': {'errorNotes[0].guidanceEn': ('Use '
                                                                                            'the '
                                                                                            'Genitive: '
                                                                                            'uczę '
                                                                                            'się '
                                                                                            'polskiego.',
                                                                                            'Use '
                                                                                            'the '
                                                                                            'Genitive: '
                                                                                            'uczę '
                                                                                            'się '
                                                                                            'polskiego '
                                                                                            "(I'm "
                                                                                            'learning '
                                                                                            'Polish).'),
                                                               'learnerExplanationEn': ('The '
                                                                                        'subject '
                                                                                        'you '
                                                                                        'study '
                                                                                        'goes '
                                                                                        'in '
                                                                                        'the '
                                                                                        'Genitive '
                                                                                        'after '
                                                                                        'uczyć '
                                                                                        'się: '
                                                                                        'uczę '
                                                                                        'się '
                                                                                        'polskiego.',
                                                                                        'The '
                                                                                        'subject '
                                                                                        'you '
                                                                                        'study '
                                                                                        'goes '
                                                                                        'in '
                                                                                        'the '
                                                                                        'Genitive '
                                                                                        'after '
                                                                                        'uczyć '
                                                                                        'się: '
                                                                                        'uczę '
                                                                                        'się '
                                                                                        'polskiego '
                                                                                        "(I'm "
                                                                                        'learning '
                                                                                        'Polish).')},
 'vp-p-uczyc-sie-study-infinitive-skill-ab708776387e': {'learnerExplanationEn': ('To '
                                                                                 'name '
                                                                                 'a '
                                                                                 'skill '
                                                                                 'you '
                                                                                 'are '
                                                                                 'learning, '
                                                                                 'use '
                                                                                 'an '
                                                                                 'infinitive: '
                                                                                 'uczę '
                                                                                 'się '
                                                                                 'gotować.',
                                                                                 'To '
                                                                                 'name '
                                                                                 'a '
                                                                                 'skill '
                                                                                 'you '
                                                                                 'are '
                                                                                 'learning, '
                                                                                 'use '
                                                                                 'an '
                                                                                 'infinitive: '
                                                                                 'uczę '
                                                                                 'się '
                                                                                 'gotować '
                                                                                 "(I'm "
                                                                                 'learning '
                                                                                 'to '
                                                                                 'cook).')},
 'vp-p-ufac-trust-dative-object-10988adac8cd': {'errorNotes[0].guidanceEn': ('Ufać '
                                                                             'takes '
                                                                             'the '
                                                                             'Dative, '
                                                                             'not '
                                                                             'the '
                                                                             'Accusative: '
                                                                             'ufam '
                                                                             'mojemu '
                                                                             'bratu.',
                                                                             'Ufać '
                                                                             'takes '
                                                                             'the '
                                                                             'Dative, '
                                                                             'not '
                                                                             'the '
                                                                             'Accusative: '
                                                                             'ufam '
                                                                             'mojemu '
                                                                             'bratu '
                                                                             '(I '
                                                                             'trust '
                                                                             'my '
                                                                             'brother).'),
                                                'learnerExplanationEn': ('The '
                                                                         'person '
                                                                         'you '
                                                                         'trust '
                                                                         'goes '
                                                                         'in '
                                                                         'the '
                                                                         'Dative: '
                                                                         'ufam '
                                                                         'bratu.',
                                                                         'The '
                                                                         'person '
                                                                         'you '
                                                                         'trust '
                                                                         'goes '
                                                                         'in '
                                                                         'the '
                                                                         'Dative: '
                                                                         'ufam '
                                                                         'bratu '
                                                                         '(I '
                                                                         'trust '
                                                                         'my '
                                                                         'brother).')},
 'vp-p-uzywac-use-genitive-object-2c5cb44fe85d': {'errorNotes[0].guidanceEn': ('Używać '
                                                                               'takes '
                                                                               'the '
                                                                               'Genitive: '
                                                                               'używam '
                                                                               'tej '
                                                                               'aplikacji.',
                                                                               'Używać '
                                                                               'takes '
                                                                               'the '
                                                                               'Genitive: '
                                                                               'używam '
                                                                               'tej '
                                                                               'aplikacji '
                                                                               '(I '
                                                                               'use '
                                                                               'this '
                                                                               'app).')},
 'vp-p-widziec-perceive-visually-accusative-object-80b697e51432': {'learnerExplanationEn': ('Widzieć '
                                                                                            'takes '
                                                                                            'a '
                                                                                            'plain '
                                                                                            'Accusative '
                                                                                            'object: '
                                                                                            'widzę '
                                                                                            'kota.',
                                                                                            'Widzieć '
                                                                                            'takes '
                                                                                            'a '
                                                                                            'plain '
                                                                                            'Accusative '
                                                                                            'object: '
                                                                                            'widzę '
                                                                                            'kota '
                                                                                            '(I '
                                                                                            'see '
                                                                                            'a '
                                                                                            'cat).')},
 'vp-p-wierzyc-have-trust-dative-object-f38bb3e72123': {'errorNotes[0].guidanceEn': ('Wierzyć '
                                                                                     'takes '
                                                                                     'the '
                                                                                     'Dative: '
                                                                                     'nie '
                                                                                     'wierzę '
                                                                                     'mu.',
                                                                                     'Wierzyć '
                                                                                     'takes '
                                                                                     'the '
                                                                                     'Dative: '
                                                                                     'nie '
                                                                                     'wierzę '
                                                                                     'mu '
                                                                                     '(I '
                                                                                     "don't "
                                                                                     'believe '
                                                                                     'him).'),
                                                        'learnerExplanationEn': ('To '
                                                                                 'believe '
                                                                                 'a '
                                                                                 'person, '
                                                                                 'use '
                                                                                 'the '
                                                                                 'Dative: '
                                                                                 'wierzę '
                                                                                 'ci.',
                                                                                 'To '
                                                                                 'believe '
                                                                                 'a '
                                                                                 'person, '
                                                                                 'use '
                                                                                 'the '
                                                                                 'Dative: '
                                                                                 'wierzę '
                                                                                 'ci '
                                                                                 '(I '
                                                                                 'believe '
                                                                                 'you).')},
 'vp-p-wierzyc-have-trust-w-accusative-target-6561408ea8d1': {'learnerExplanationEn': ('For '
                                                                                       'confidence '
                                                                                       'in '
                                                                                       'a '
                                                                                       'person '
                                                                                       'or '
                                                                                       'thing, '
                                                                                       'use '
                                                                                       'w '
                                                                                       '+ '
                                                                                       'Accusative: '
                                                                                       'wierzę '
                                                                                       'w '
                                                                                       'tego '
                                                                                       'lekarza.',
                                                                                       'For '
                                                                                       'confidence '
                                                                                       'in '
                                                                                       'a '
                                                                                       'person '
                                                                                       'or '
                                                                                       'thing, '
                                                                                       'use '
                                                                                       'w '
                                                                                       '+ '
                                                                                       'Accusative: '
                                                                                       'wierzę '
                                                                                       'w '
                                                                                       'tego '
                                                                                       'lekarza '
                                                                                       '(I '
                                                                                       'believe '
                                                                                       'in '
                                                                                       'this '
                                                                                       'doctor).')},
 'vp-p-zajmowac-sie-occupation-activity-instrumental-topic-3321df3f989e': {'errorNotes[0].guidanceEn': ('No '
                                                                                                        'preposition: '
                                                                                                        'use '
                                                                                                        'the '
                                                                                                        'bare '
                                                                                                        'Instrumental, '
                                                                                                        'zajmuję '
                                                                                                        'się '
                                                                                                        'marketingiem.',
                                                                                                        'No '
                                                                                                        'preposition: '
                                                                                                        'use '
                                                                                                        'the '
                                                                                                        'bare '
                                                                                                        'Instrumental, '
                                                                                                        'zajmuję '
                                                                                                        'się '
                                                                                                        'marketingiem '
                                                                                                        '(I '
                                                                                                        'work '
                                                                                                        'in '
                                                                                                        'marketing).'),
                                                                           'learnerExplanationEn': ('What '
                                                                                                    'you '
                                                                                                    'do '
                                                                                                    'or '
                                                                                                    'deal '
                                                                                                    'with '
                                                                                                    'takes '
                                                                                                    'the '
                                                                                                    'bare '
                                                                                                    'Instrumental: '
                                                                                                    'zajmuję '
                                                                                                    'się '
                                                                                                    'marketingiem.',
                                                                                                    'What '
                                                                                                    'you '
                                                                                                    'do '
                                                                                                    'or '
                                                                                                    'deal '
                                                                                                    'with '
                                                                                                    'takes '
                                                                                                    'the '
                                                                                                    'bare '
                                                                                                    'Instrumental: '
                                                                                                    'zajmuję '
                                                                                                    'się '
                                                                                                    'marketingiem '
                                                                                                    '(I '
                                                                                                    'work '
                                                                                                    'in '
                                                                                                    'marketing).')},
 'vp-p-zalezec-depend-on-od-genitive-source-1ad29f7a1318': {'learnerExplanationEn': ('Use '
                                                                                     'od '
                                                                                     '+ '
                                                                                     'Genitive '
                                                                                     'for '
                                                                                     'what '
                                                                                     'something '
                                                                                     'depends '
                                                                                     'on: '
                                                                                     'to '
                                                                                     'zależy '
                                                                                     'od '
                                                                                     'pogody.',
                                                                                     'Use '
                                                                                     'od '
                                                                                     '+ '
                                                                                     'Genitive '
                                                                                     'for '
                                                                                     'what '
                                                                                     'something '
                                                                                     'depends '
                                                                                     'on: '
                                                                                     'to '
                                                                                     'zależy '
                                                                                     'od '
                                                                                     'pogody '
                                                                                     '(it '
                                                                                     'depends '
                                                                                     'on '
                                                                                     'the '
                                                                                     'weather).')},
 'vp-p-znac-be-acquainted-with-accusative-object-379e19b36299': {'learnerExplanationEn': ('Znać '
                                                                                          'takes '
                                                                                          'a '
                                                                                          'plain '
                                                                                          'Accusative '
                                                                                          'object: '
                                                                                          'znam '
                                                                                          'tę '
                                                                                          'restaurację.',
                                                                                          'Znać '
                                                                                          'takes '
                                                                                          'a '
                                                                                          'plain '
                                                                                          'Accusative '
                                                                                          'object: '
                                                                                          'znam '
                                                                                          'tę '
                                                                                          'restaurację '
                                                                                          '(I '
                                                                                          'know '
                                                                                          'this '
                                                                                          'restaurant).')},
 'vp-p-znalezc-find-accusative-object-d80c52211462': {'errorNotes[0].guidanceEn': ('Znaleźć '
                                                                                   'takes '
                                                                                   'the '
                                                                                   'Accusative: '
                                                                                   'znaleźć '
                                                                                   'mieszkanie. '
                                                                                   'Only '
                                                                                   'szukać '
                                                                                   'uses '
                                                                                   'the '
                                                                                   'Genitive.',
                                                                                   'Znaleźć '
                                                                                   'takes '
                                                                                   'the '
                                                                                   'Accusative: '
                                                                                   'znaleźć '
                                                                                   'mieszkanie '
                                                                                   '(to '
                                                                                   'find '
                                                                                   'a '
                                                                                   'flat). '
                                                                                   'Only '
                                                                                   'szukać '
                                                                                   'uses '
                                                                                   'the '
                                                                                   'Genitive.')}}
)

#: Per identity, the exact example object Phase 4F-H2 created.
H2_NEW_EXAMPLES = (
{'vp-p-bac-sie-worry-about-o-accusative-concern-c4b9b8d6811b': {'audioEligible': False,
                                                                'en': "We're "
                                                                      'worried '
                                                                      'about '
                                                                      'our '
                                                                      'grandad '
                                                                      'because '
                                                                      'he '
                                                                      'lives '
                                                                      'alone.',
                                                                'id': 'vp-e-bac-sie-worry-about-o-accusative-concern-worried-about-grandad-6d3fcb1cfed8',
                                                                'key': 'worried-about-grandad',
                                                                'origin': {'adoptedAt': '2026-08-18',
                                                                           'generatorRef': 'priority7-example-generation',
                                                                           'kind': 'editorial-generated'},
                                                                'pl': 'Boimy '
                                                                      'się '
                                                                      'o '
                                                                      'dziadka, '
                                                                      'bo '
                                                                      'mieszka '
                                                                      'sam.'},
 'vp-p-mowic-tell-content-dative-recipient-accusative-content-2f2b1add1960': {'audioEligible': False,
                                                                              'en': 'I '
                                                                                    'always '
                                                                                    'tell '
                                                                                    'my '
                                                                                    'parents '
                                                                                    'the '
                                                                                    'truth.',
                                                                              'id': 'vp-e-mowic-tell-content-dative-recipient-accusative-content-telling-parents-the-truth-cc31a97d5386',
                                                                              'key': 'telling-parents-the-truth',
                                                                              'origin': {'adoptedAt': '2026-08-18',
                                                                                         'generatorRef': 'priority7-example-generation',
                                                                                         'kind': 'editorial-generated'},
                                                                              'pl': 'Zawsze '
                                                                                    'mówię '
                                                                                    'rodzicom '
                                                                                    'prawdę.'},
 'vp-p-mowic-tell-content-dative-recipient-ze-clause-a01ddc4a4736': {'audioEligible': False,
                                                                     'en': "I'm "
                                                                           'telling '
                                                                           'you '
                                                                           'that '
                                                                           "it's "
                                                                           'a '
                                                                           'good '
                                                                           'idea.',
                                                                     'id': 'vp-e-mowic-tell-content-dative-recipient-ze-clause-telling-you-its-a-good-idea-ed20965f4251',
                                                                     'key': 'telling-you-its-a-good-idea',
                                                                     'origin': {'adoptedAt': '2026-08-18',
                                                                                'generatorRef': 'priority7-example-generation',
                                                                                'kind': 'editorial-generated'},
                                                                     'pl': 'Mówię '
                                                                           'ci, '
                                                                           'że '
                                                                           'to '
                                                                           'dobry '
                                                                           'pomysł.'},
 'vp-p-podobac-sie-appeal-to-nominative-stimulus-dative-experiencer-ef199e675ee9': {'audioEligible': False,
                                                                                    'en': 'To '
                                                                                          'be '
                                                                                          'honest, '
                                                                                          'I '
                                                                                          "don't "
                                                                                          'like '
                                                                                          'this '
                                                                                          'movie.',
                                                                                    'id': 'vp-e-podobac-sie-appeal-to-nominative-stimulus-dative-experiencer-honest-opinion-about-the-film-c11dccc4e223',
                                                                                    'key': 'honest-opinion-about-the-film',
                                                                                    'origin': {'kind': 'repository-reuse',
                                                                                               'repositorySource': {'field': 'ex',
                                                                                                                    'id': 'b1-expressing-opinions-004',
                                                                                                                    'kind': 'card'}},
                                                                                    'pl': 'Szczerze '
                                                                                          'mówiąc, '
                                                                                          'nie '
                                                                                          'podoba '
                                                                                          'mi '
                                                                                          'się '
                                                                                          'ten '
                                                                                          'film.'},
 'vp-p-pomagac-assist-dative-recipient-9f0a375c5e81': {'audioEligible': False,
                                                       'en': 'I often help '
                                                             'my '
                                                             'neighbour.',
                                                       'id': 'vp-e-pomagac-assist-dative-recipient-helping-a-neighbour-da22c7a69e27',
                                                       'key': 'helping-a-neighbour',
                                                       'origin': {'adoptedAt': '2026-08-18',
                                                                  'generatorRef': 'priority7-example-generation',
                                                                  'kind': 'editorial-generated'},
                                                       'pl': 'Często '
                                                             'pomagam '
                                                             'sąsiadce.'},
 'vp-p-pomagac-assist-dative-recipient-w-locative-area-1e507dcdb869': {'audioEligible': False,
                                                                       'en': 'I '
                                                                             'help '
                                                                             'my '
                                                                             'brother '
                                                                             'with '
                                                                             'maths.',
                                                                       'id': 'vp-e-pomagac-assist-dative-recipient-w-locative-area-helping-with-maths-adfee546f29a',
                                                                       'key': 'helping-with-maths',
                                                                       'origin': {'adoptedAt': '2026-08-18',
                                                                                  'generatorRef': 'priority7-example-generation',
                                                                                  'kind': 'editorial-generated'},
                                                                       'pl': 'Pomagam '
                                                                             'bratu '
                                                                             'w '
                                                                             'matematyce.'},
 'vp-p-prosic-request-accusative-person-o-accusative-thing-b7a8d9ce1a99': {'audioEligible': False,
                                                                           'en': 'I '
                                                                                 'will '
                                                                                 'ask '
                                                                                 'my '
                                                                                 'boss '
                                                                                 'for '
                                                                                 'a '
                                                                                 'raise.',
                                                                           'id': 'vp-e-prosic-request-accusative-person-o-accusative-thing-asking-the-boss-for-a-raise-edec4ed77571',
                                                                           'key': 'asking-the-boss-for-a-raise',
                                                                           'origin': {'kind': 'repository-reuse',
                                                                                      'repositorySource': {'field': 'ex',
                                                                                                           'id': 'b1-career-006',
                                                                                                           'kind': 'card'}},
                                                                           'pl': 'Będę '
                                                                                 'prosić '
                                                                                 'szefa '
                                                                                 'o '
                                                                                 'podwyżkę.'},
 'vp-p-rozmawiac-talk-with-o-locative-topic-b1c59475ac05': {'audioEligible': False,
                                                            'en': 'We '
                                                                  'always '
                                                                  'talk '
                                                                  'about '
                                                                  'music.',
                                                            'id': 'vp-e-rozmawiac-talk-with-o-locative-topic-talking-about-music-94c6280fa290',
                                                            'key': 'talking-about-music',
                                                            'origin': {'adoptedAt': '2026-08-18',
                                                                       'generatorRef': 'priority7-example-generation',
                                                                       'kind': 'editorial-generated'},
                                                            'pl': 'Zawsze '
                                                                  'rozmawiamy '
                                                                  'o '
                                                                  'muzyce.'},
 'vp-p-rozmawiac-talk-with-z-instrumental-interlocutor-8398fa7449ca': {'audioEligible': False,
                                                                       'en': 'I '
                                                                             'talk '
                                                                             'to '
                                                                             'my '
                                                                             'mum '
                                                                             'every '
                                                                             'day.',
                                                                       'id': 'vp-e-rozmawiac-talk-with-z-instrumental-interlocutor-talking-to-mum-every-day-e0d2b75493db',
                                                                       'key': 'talking-to-mum-every-day',
                                                                       'origin': {'adoptedAt': '2026-08-18',
                                                                                  'generatorRef': 'priority7-example-generation',
                                                                                  'kind': 'editorial-generated'},
                                                                       'pl': 'Codziennie '
                                                                             'rozmawiam '
                                                                             'z '
                                                                             'mamą.'},
 'vp-p-rozmawiac-talk-with-z-instrumental-o-locative-4e586b18cf98': {'audioEligible': False,
                                                                     'en': "I'm "
                                                                           'talking '
                                                                           'to '
                                                                           'the '
                                                                           'doctor '
                                                                           'about '
                                                                           'the '
                                                                           'test '
                                                                           'results.',
                                                                     'id': 'vp-e-rozmawiac-talk-with-z-instrumental-o-locative-doctor-about-test-results-6080f6504f29',
                                                                     'key': 'doctor-about-test-results',
                                                                     'origin': {'adoptedAt': '2026-08-18',
                                                                                'generatorRef': 'priority7-example-generation',
                                                                                'kind': 'editorial-generated'},
                                                                     'pl': 'Rozmawiam '
                                                                           'z '
                                                                           'lekarzem '
                                                                           'o '
                                                                           'wynikach '
                                                                           'badań.'},
 'vp-p-sluchac-obey-genitive-object-674adae2dec3': {'audioEligible': False,
                                                    'en': 'This dog obeys '
                                                          'its owner.',
                                                    'id': 'vp-e-sluchac-obey-genitive-object-dog-obeys-its-owner-f1216029cb1b',
                                                    'key': 'dog-obeys-its-owner',
                                                    'origin': {'adoptedAt': '2026-08-18',
                                                               'generatorRef': 'priority7-example-generation',
                                                               'kind': 'editorial-generated'},
                                                    'pl': 'Ten pies słucha '
                                                          'swojego pana.'},
 'vp-p-ufac-trust-dative-object-10988adac8cd': {'audioEligible': False,
                                                'en': 'I trust my teacher.',
                                                'id': 'vp-e-ufac-trust-dative-object-trusting-my-teacher-618816d6a6ea',
                                                'key': 'trusting-my-teacher',
                                                'origin': {'adoptedAt': '2026-08-18',
                                                           'generatorRef': 'priority7-example-generation',
                                                           'kind': 'editorial-generated'},
                                                'pl': 'Ufam swojej '
                                                      'nauczycielce.'},
 'vp-p-wierzyc-have-trust-dative-object-f38bb3e72123': {'audioEligible': False,
                                                        'en': 'I believe '
                                                              'my friend '
                                                              'because she '
                                                              'never lies.',
                                                        'id': 'vp-e-wierzyc-have-trust-dative-object-believing-a-friend-b65c5d71b199',
                                                        'key': 'believing-a-friend',
                                                        'origin': {'adoptedAt': '2026-08-18',
                                                                   'generatorRef': 'priority7-example-generation',
                                                                   'kind': 'editorial-generated'},
                                                        'pl': 'Wierzę '
                                                              'koleżance, '
                                                              'bo nigdy '
                                                              'nie '
                                                              'kłamie.'},
 'vp-p-wierzyc-have-trust-w-accusative-target-6561408ea8d1': {'audioEligible': False,
                                                              'en': 'The '
                                                                    'coach '
                                                                    'believes '
                                                                    'in '
                                                                    'this '
                                                                    'team.',
                                                              'id': 'vp-e-wierzyc-have-trust-w-accusative-target-believing-in-the-team-9695f1faa84b',
                                                              'key': 'believing-in-the-team',
                                                              'origin': {'adoptedAt': '2026-08-18',
                                                                         'generatorRef': 'priority7-example-generation',
                                                                         'kind': 'editorial-generated'},
                                                              'pl': 'Trener '
                                                                    'wierzy '
                                                                    'w tę '
                                                                    'drużynę.'},
 'vp-p-zajmowac-sie-occupation-activity-instrumental-topic-3321df3f989e': {'audioEligible': False,
                                                                           'en': 'My '
                                                                                 'dad '
                                                                                 'works '
                                                                                 'in '
                                                                                 'computer '
                                                                                 'repair.',
                                                                           'id': 'vp-e-zajmowac-sie-occupation-activity-instrumental-topic-dad-repairs-computers-1ad6678e41cb',
                                                                           'key': 'dad-repairs-computers',
                                                                           'origin': {'adoptedAt': '2026-08-18',
                                                                                      'generatorRef': 'priority7-example-generation',
                                                                                      'kind': 'editorial-generated'},
                                                                           'pl': 'Mój '
                                                                                 'tata '
                                                                                 'zajmuje '
                                                                                 'się '
                                                                                 'naprawą '
                                                                                 'komputerów.'},
 'vp-p-zalezec-matter-to-someone-dative-experiencer-na-locative-1fc4131471cc': {'audioEligible': False,
                                                                                'en': 'This '
                                                                                      'job '
                                                                                      'really '
                                                                                      'matters '
                                                                                      'to '
                                                                                      'me.',
                                                                                'id': 'vp-e-zalezec-matter-to-someone-dative-experiencer-na-locative-this-job-matters-to-me-49c780e0667f',
                                                                                'key': 'this-job-matters-to-me',
                                                                                'origin': {'adoptedAt': '2026-08-18',
                                                                                           'generatorRef': 'priority7-example-generation',
                                                                                           'kind': 'editorial-generated'},
                                                                                'pl': 'Bardzo '
                                                                                      'mi '
                                                                                      'zależy '
                                                                                      'na '
                                                                                      'tej '
                                                                                      'pracy.'}}
)

#: Per identity, the exact events Phase 4F-H2 appended, in order, each with
#: its statically pinned tier-2 scope digest.
H2_APPENDED_EVENTS = (
{'vp-p-bac-sie-be-afraid-of-genitive-stimulus-4f1d684a5144': [{'decision': 'accept',
                                                               'kind': 'correction',
                                                               'note': 'Owner-authorized '
                                                                       'correction, '
                                                                       '2026-08-18: '
                                                                       'add '
                                                                       'English '
                                                                       'glosses '
                                                                       'to '
                                                                       'the '
                                                                       'Polish '
                                                                       'illustrations '
                                                                       'in '
                                                                       'the '
                                                                       'learner-facing '
                                                                       'English '
                                                                       'prose '
                                                                       'and, '
                                                                       'where '
                                                                       'applicable, '
                                                                       'complete '
                                                                       'the '
                                                                       'example '
                                                                       'treatment. '
                                                                       'The '
                                                                       'corrected '
                                                                       'wording '
                                                                       'itself '
                                                                       'is '
                                                                       'not '
                                                                       'product-approved.',
                                                               'reviewedAt': '2026-08-18',
                                                               'reviewerRef': 'product-owner-001'},
                                                              {'actorRef': 'priority7-editorial-review',
                                                               'decision': 'changes-requested',
                                                               'kind': 'editorial-review',
                                                               'note': 'H2 '
                                                                       'content '
                                                                       'change: '
                                                                       'English '
                                                                       'glosses '
                                                                       'added '
                                                                       'to '
                                                                       'this '
                                                                       "pattern's "
                                                                       'Polish '
                                                                       'illustrations '
                                                                       'in '
                                                                       'the '
                                                                       'learner-facing '
                                                                       'English '
                                                                       'prose. '
                                                                       'Tier-2 '
                                                                       'scope '
                                                                       'moved, '
                                                                       'so '
                                                                       'the '
                                                                       'standing '
                                                                       'editorial '
                                                                       'acceptance '
                                                                       'is '
                                                                       'withdrawn.',
                                                               'reviewedAt': '2026-08-18'},
                                                              {'actorRef': 'priority7-editorial-review',
                                                               'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                               'decision': 'accept',
                                                               'kind': 'editorial-review',
                                                               'note': 'H2 '
                                                                       're-review: '
                                                                       'an '
                                                                       'authoring '
                                                                       'pass '
                                                                       'drafted '
                                                                       'the '
                                                                       'glosses '
                                                                       'and '
                                                                       'examples '
                                                                       'and '
                                                                       'a '
                                                                       'separate '
                                                                       'final '
                                                                       'editorial '
                                                                       'pass '
                                                                       'audited '
                                                                       'translation '
                                                                       'accuracy, '
                                                                       'Polish '
                                                                       'grammaticality, '
                                                                       'pattern '
                                                                       'fit, '
                                                                       'register '
                                                                       'and '
                                                                       'CEFR. '
                                                                       'Accepted '
                                                                       'against '
                                                                       'the '
                                                                       'current '
                                                                       'tier-2 '
                                                                       'scope.',
                                                               'reviewedAt': '2026-08-18',
                                                               'scopeDigest': 'sha256:b4cd9d36f29ce2e15908905ccfb4ab987cc3d9944841736b097f6a48f3be2e03',
                                                               'scopeVersion': 1}],
 'vp-p-bac-sie-worry-about-o-accusative-concern-c4b9b8d6811b': [{'decision': 'accept',
                                                                 'kind': 'correction',
                                                                 'note': 'Owner-authorized '
                                                                         'correction, '
                                                                         '2026-08-18: '
                                                                         'add '
                                                                         'English '
                                                                         'glosses '
                                                                         'to '
                                                                         'the '
                                                                         'Polish '
                                                                         'illustrations '
                                                                         'in '
                                                                         'the '
                                                                         'learner-facing '
                                                                         'English '
                                                                         'prose '
                                                                         'and, '
                                                                         'where '
                                                                         'applicable, '
                                                                         'complete '
                                                                         'the '
                                                                         'example '
                                                                         'treatment. '
                                                                         'The '
                                                                         'corrected '
                                                                         'wording '
                                                                         'itself '
                                                                         'is '
                                                                         'not '
                                                                         'product-approved.',
                                                                 'reviewedAt': '2026-08-18',
                                                                 'reviewerRef': 'product-owner-001'},
                                                                {'actorRef': 'priority7-editorial-review',
                                                                 'decision': 'changes-requested',
                                                                 'kind': 'editorial-review',
                                                                 'note': 'H2 '
                                                                         'content '
                                                                         'change: '
                                                                         'English '
                                                                         'glosses '
                                                                         'added '
                                                                         'to '
                                                                         'the '
                                                                         'Polish '
                                                                         'illustrations '
                                                                         'and '
                                                                         'a '
                                                                         'first '
                                                                         'example '
                                                                         'added '
                                                                         'to '
                                                                         'this '
                                                                         'pattern. '
                                                                         'Tier-2 '
                                                                         'scope '
                                                                         'moved, '
                                                                         'so '
                                                                         'the '
                                                                         'standing '
                                                                         'editorial '
                                                                         'acceptance '
                                                                         'is '
                                                                         'withdrawn.',
                                                                 'reviewedAt': '2026-08-18'},
                                                                {'actorRef': 'priority7-editorial-review',
                                                                 'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                                 'decision': 'accept',
                                                                 'kind': 'editorial-review',
                                                                 'note': 'H2 '
                                                                         're-review: '
                                                                         'an '
                                                                         'authoring '
                                                                         'pass '
                                                                         'drafted '
                                                                         'the '
                                                                         'glosses '
                                                                         'and '
                                                                         'examples '
                                                                         'and '
                                                                         'a '
                                                                         'separate '
                                                                         'final '
                                                                         'editorial '
                                                                         'pass '
                                                                         'audited '
                                                                         'translation '
                                                                         'accuracy, '
                                                                         'Polish '
                                                                         'grammaticality, '
                                                                         'pattern '
                                                                         'fit, '
                                                                         'register '
                                                                         'and '
                                                                         'CEFR. '
                                                                         'Accepted '
                                                                         'against '
                                                                         'the '
                                                                         'current '
                                                                         'tier-2 '
                                                                         'scope.',
                                                                 'reviewedAt': '2026-08-18',
                                                                 'scopeDigest': 'sha256:1e7c983641c89c7224be14404de3484b8a6bf8fa684017f22086ea6a2a6b1bb8',
                                                                 'scopeVersion': 1}],
 'vp-p-byc-predicate-role-instrumental-predicate-3b90a83fbb30': [{'decision': 'accept',
                                                                  'kind': 'correction',
                                                                  'note': 'Owner-authorized '
                                                                          'correction, '
                                                                          '2026-08-18: '
                                                                          'add '
                                                                          'English '
                                                                          'glosses '
                                                                          'to '
                                                                          'the '
                                                                          'Polish '
                                                                          'illustrations '
                                                                          'in '
                                                                          'the '
                                                                          'learner-facing '
                                                                          'English '
                                                                          'prose '
                                                                          'and, '
                                                                          'where '
                                                                          'applicable, '
                                                                          'complete '
                                                                          'the '
                                                                          'example '
                                                                          'treatment. '
                                                                          'The '
                                                                          'corrected '
                                                                          'wording '
                                                                          'itself '
                                                                          'is '
                                                                          'not '
                                                                          'product-approved.',
                                                                  'reviewedAt': '2026-08-18',
                                                                  'reviewerRef': 'product-owner-001'},
                                                                 {'actorRef': 'priority7-editorial-review',
                                                                  'decision': 'changes-requested',
                                                                  'kind': 'editorial-review',
                                                                  'note': 'H2 '
                                                                          'content '
                                                                          'change: '
                                                                          'English '
                                                                          'glosses '
                                                                          'added '
                                                                          'to '
                                                                          'this '
                                                                          "pattern's "
                                                                          'Polish '
                                                                          'illustrations '
                                                                          'in '
                                                                          'the '
                                                                          'learner-facing '
                                                                          'English '
                                                                          'prose. '
                                                                          'Tier-2 '
                                                                          'scope '
                                                                          'moved, '
                                                                          'so '
                                                                          'the '
                                                                          'standing '
                                                                          'editorial '
                                                                          'acceptance '
                                                                          'is '
                                                                          'withdrawn.',
                                                                  'reviewedAt': '2026-08-18'},
                                                                 {'actorRef': 'priority7-editorial-review',
                                                                  'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                                  'decision': 'accept',
                                                                  'kind': 'editorial-review',
                                                                  'note': 'H2 '
                                                                          're-review: '
                                                                          'an '
                                                                          'authoring '
                                                                          'pass '
                                                                          'drafted '
                                                                          'the '
                                                                          'glosses '
                                                                          'and '
                                                                          'examples '
                                                                          'and '
                                                                          'a '
                                                                          'separate '
                                                                          'final '
                                                                          'editorial '
                                                                          'pass '
                                                                          'audited '
                                                                          'translation '
                                                                          'accuracy, '
                                                                          'Polish '
                                                                          'grammaticality, '
                                                                          'pattern '
                                                                          'fit, '
                                                                          'register '
                                                                          'and '
                                                                          'CEFR. '
                                                                          'Accepted '
                                                                          'against '
                                                                          'the '
                                                                          'current '
                                                                          'tier-2 '
                                                                          'scope.',
                                                                  'reviewedAt': '2026-08-18',
                                                                  'scopeDigest': 'sha256:968afd166fbde1a319dfa565dcbb1567b0cd68bb8afeb4ef9ea530df80afe8ec',
                                                                  'scopeVersion': 1}],
 'vp-p-czekac-wait-for-na-accusative-target-3c9ac823ecde': [{'decision': 'accept',
                                                             'kind': 'correction',
                                                             'note': 'Owner-authorized '
                                                                     'correction, '
                                                                     '2026-08-18: '
                                                                     'add '
                                                                     'English '
                                                                     'glosses '
                                                                     'to '
                                                                     'the '
                                                                     'Polish '
                                                                     'illustrations '
                                                                     'in '
                                                                     'the '
                                                                     'learner-facing '
                                                                     'English '
                                                                     'prose '
                                                                     'and, '
                                                                     'where '
                                                                     'applicable, '
                                                                     'complete '
                                                                     'the '
                                                                     'example '
                                                                     'treatment. '
                                                                     'The '
                                                                     'corrected '
                                                                     'wording '
                                                                     'itself '
                                                                     'is '
                                                                     'not '
                                                                     'product-approved.',
                                                             'reviewedAt': '2026-08-18',
                                                             'reviewerRef': 'product-owner-001'},
                                                            {'actorRef': 'priority7-editorial-review',
                                                             'decision': 'changes-requested',
                                                             'kind': 'editorial-review',
                                                             'note': 'H2 '
                                                                     'content '
                                                                     'change: '
                                                                     'English '
                                                                     'glosses '
                                                                     'added '
                                                                     'to '
                                                                     'this '
                                                                     "pattern's "
                                                                     'Polish '
                                                                     'illustrations '
                                                                     'in '
                                                                     'the '
                                                                     'learner-facing '
                                                                     'English '
                                                                     'prose. '
                                                                     'Tier-2 '
                                                                     'scope '
                                                                     'moved, '
                                                                     'so '
                                                                     'the '
                                                                     'standing '
                                                                     'editorial '
                                                                     'acceptance '
                                                                     'is '
                                                                     'withdrawn.',
                                                             'reviewedAt': '2026-08-18'},
                                                            {'actorRef': 'priority7-editorial-review',
                                                             'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                             'decision': 'accept',
                                                             'kind': 'editorial-review',
                                                             'note': 'H2 '
                                                                     're-review: '
                                                                     'an '
                                                                     'authoring '
                                                                     'pass '
                                                                     'drafted '
                                                                     'the '
                                                                     'glosses '
                                                                     'and '
                                                                     'examples '
                                                                     'and '
                                                                     'a '
                                                                     'separate '
                                                                     'final '
                                                                     'editorial '
                                                                     'pass '
                                                                     'audited '
                                                                     'translation '
                                                                     'accuracy, '
                                                                     'Polish '
                                                                     'grammaticality, '
                                                                     'pattern '
                                                                     'fit, '
                                                                     'register '
                                                                     'and '
                                                                     'CEFR. '
                                                                     'Accepted '
                                                                     'against '
                                                                     'the '
                                                                     'current '
                                                                     'tier-2 '
                                                                     'scope.',
                                                             'reviewedAt': '2026-08-18',
                                                             'scopeDigest': 'sha256:8c14f7f47edbc7f1c2286e86372ec51c4ef447c17153e0c496e9def266f2f891',
                                                             'scopeVersion': 1}],
 'vp-p-dbac-take-care-of-o-accusative-target-d3e3eb63129c': [{'decision': 'accept',
                                                              'kind': 'correction',
                                                              'note': 'Owner-authorized '
                                                                      'correction, '
                                                                      '2026-08-18: '
                                                                      'add '
                                                                      'English '
                                                                      'glosses '
                                                                      'to '
                                                                      'the '
                                                                      'Polish '
                                                                      'illustrations '
                                                                      'in '
                                                                      'the '
                                                                      'learner-facing '
                                                                      'English '
                                                                      'prose '
                                                                      'and, '
                                                                      'where '
                                                                      'applicable, '
                                                                      'complete '
                                                                      'the '
                                                                      'example '
                                                                      'treatment. '
                                                                      'The '
                                                                      'corrected '
                                                                      'wording '
                                                                      'itself '
                                                                      'is '
                                                                      'not '
                                                                      'product-approved.',
                                                              'reviewedAt': '2026-08-18',
                                                              'reviewerRef': 'product-owner-001'},
                                                             {'actorRef': 'priority7-editorial-review',
                                                              'decision': 'changes-requested',
                                                              'kind': 'editorial-review',
                                                              'note': 'H2 '
                                                                      'content '
                                                                      'change: '
                                                                      'English '
                                                                      'glosses '
                                                                      'added '
                                                                      'to '
                                                                      'this '
                                                                      "pattern's "
                                                                      'Polish '
                                                                      'illustrations '
                                                                      'in '
                                                                      'the '
                                                                      'learner-facing '
                                                                      'English '
                                                                      'prose. '
                                                                      'Tier-2 '
                                                                      'scope '
                                                                      'moved, '
                                                                      'so '
                                                                      'the '
                                                                      'standing '
                                                                      'editorial '
                                                                      'acceptance '
                                                                      'is '
                                                                      'withdrawn.',
                                                              'reviewedAt': '2026-08-18'},
                                                             {'actorRef': 'priority7-editorial-review',
                                                              'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                              'decision': 'accept',
                                                              'kind': 'editorial-review',
                                                              'note': 'H2 '
                                                                      're-review: '
                                                                      'an '
                                                                      'authoring '
                                                                      'pass '
                                                                      'drafted '
                                                                      'the '
                                                                      'glosses '
                                                                      'and '
                                                                      'examples '
                                                                      'and '
                                                                      'a '
                                                                      'separate '
                                                                      'final '
                                                                      'editorial '
                                                                      'pass '
                                                                      'audited '
                                                                      'translation '
                                                                      'accuracy, '
                                                                      'Polish '
                                                                      'grammaticality, '
                                                                      'pattern '
                                                                      'fit, '
                                                                      'register '
                                                                      'and '
                                                                      'CEFR. '
                                                                      'Accepted '
                                                                      'against '
                                                                      'the '
                                                                      'current '
                                                                      'tier-2 '
                                                                      'scope.',
                                                              'reviewedAt': '2026-08-18',
                                                              'scopeDigest': 'sha256:7c450e7d2b864050b40e353828ff9023c1ebdab8cd7a5380f26429e95c676344',
                                                              'scopeVersion': 1}],
 'vp-p-dziekowac-thank-dative-recipient-za-accusative-057197dd300f': [{'decision': 'accept',
                                                                       'kind': 'correction',
                                                                       'note': 'Owner-authorized '
                                                                               'correction, '
                                                                               '2026-08-18: '
                                                                               'add '
                                                                               'English '
                                                                               'glosses '
                                                                               'to '
                                                                               'the '
                                                                               'Polish '
                                                                               'illustrations '
                                                                               'in '
                                                                               'the '
                                                                               'learner-facing '
                                                                               'English '
                                                                               'prose '
                                                                               'and, '
                                                                               'where '
                                                                               'applicable, '
                                                                               'complete '
                                                                               'the '
                                                                               'example '
                                                                               'treatment. '
                                                                               'The '
                                                                               'corrected '
                                                                               'wording '
                                                                               'itself '
                                                                               'is '
                                                                               'not '
                                                                               'product-approved.',
                                                                       'reviewedAt': '2026-08-18',
                                                                       'reviewerRef': 'product-owner-001'},
                                                                      {'actorRef': 'priority7-editorial-review',
                                                                       'decision': 'changes-requested',
                                                                       'kind': 'editorial-review',
                                                                       'note': 'H2 '
                                                                               'content '
                                                                               'change: '
                                                                               'English '
                                                                               'glosses '
                                                                               'added '
                                                                               'to '
                                                                               'this '
                                                                               "pattern's "
                                                                               'Polish '
                                                                               'illustrations '
                                                                               'in '
                                                                               'the '
                                                                               'learner-facing '
                                                                               'English '
                                                                               'prose. '
                                                                               'Tier-2 '
                                                                               'scope '
                                                                               'moved, '
                                                                               'so '
                                                                               'the '
                                                                               'standing '
                                                                               'editorial '
                                                                               'acceptance '
                                                                               'is '
                                                                               'withdrawn.',
                                                                       'reviewedAt': '2026-08-18'},
                                                                      {'actorRef': 'priority7-editorial-review',
                                                                       'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                                       'decision': 'accept',
                                                                       'kind': 'editorial-review',
                                                                       'note': 'H2 '
                                                                               're-review: '
                                                                               'an '
                                                                               'authoring '
                                                                               'pass '
                                                                               'drafted '
                                                                               'the '
                                                                               'glosses '
                                                                               'and '
                                                                               'examples '
                                                                               'and '
                                                                               'a '
                                                                               'separate '
                                                                               'final '
                                                                               'editorial '
                                                                               'pass '
                                                                               'audited '
                                                                               'translation '
                                                                               'accuracy, '
                                                                               'Polish '
                                                                               'grammaticality, '
                                                                               'pattern '
                                                                               'fit, '
                                                                               'register '
                                                                               'and '
                                                                               'CEFR. '
                                                                               'Accepted '
                                                                               'against '
                                                                               'the '
                                                                               'current '
                                                                               'tier-2 '
                                                                               'scope.',
                                                                       'reviewedAt': '2026-08-18',
                                                                       'scopeDigest': 'sha256:801120db4358cb63265fc76f59f003cd9ab8c4d82d12557f350618e0b95f8848',
                                                                       'scopeVersion': 1}],
 'vp-p-dziekowac-thank-za-accusative-reason-fd31baa1b1ad': [{'decision': 'accept',
                                                             'kind': 'correction',
                                                             'note': 'Owner-authorized '
                                                                     'correction, '
                                                                     '2026-08-18: '
                                                                     'add '
                                                                     'English '
                                                                     'glosses '
                                                                     'to '
                                                                     'the '
                                                                     'Polish '
                                                                     'illustrations '
                                                                     'in '
                                                                     'the '
                                                                     'learner-facing '
                                                                     'English '
                                                                     'prose '
                                                                     'and, '
                                                                     'where '
                                                                     'applicable, '
                                                                     'complete '
                                                                     'the '
                                                                     'example '
                                                                     'treatment. '
                                                                     'The '
                                                                     'corrected '
                                                                     'wording '
                                                                     'itself '
                                                                     'is '
                                                                     'not '
                                                                     'product-approved.',
                                                             'reviewedAt': '2026-08-18',
                                                             'reviewerRef': 'product-owner-001'},
                                                            {'actorRef': 'priority7-editorial-review',
                                                             'decision': 'changes-requested',
                                                             'kind': 'editorial-review',
                                                             'note': 'H2 '
                                                                     'content '
                                                                     'change: '
                                                                     'English '
                                                                     'glosses '
                                                                     'added '
                                                                     'to '
                                                                     'this '
                                                                     "pattern's "
                                                                     'Polish '
                                                                     'illustrations '
                                                                     'in '
                                                                     'the '
                                                                     'learner-facing '
                                                                     'English '
                                                                     'prose. '
                                                                     'Tier-2 '
                                                                     'scope '
                                                                     'moved, '
                                                                     'so '
                                                                     'the '
                                                                     'standing '
                                                                     'editorial '
                                                                     'acceptance '
                                                                     'is '
                                                                     'withdrawn.',
                                                             'reviewedAt': '2026-08-18'},
                                                            {'actorRef': 'priority7-editorial-review',
                                                             'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                             'decision': 'accept',
                                                             'kind': 'editorial-review',
                                                             'note': 'H2 '
                                                                     're-review: '
                                                                     'an '
                                                                     'authoring '
                                                                     'pass '
                                                                     'drafted '
                                                                     'the '
                                                                     'glosses '
                                                                     'and '
                                                                     'examples '
                                                                     'and '
                                                                     'a '
                                                                     'separate '
                                                                     'final '
                                                                     'editorial '
                                                                     'pass '
                                                                     'audited '
                                                                     'translation '
                                                                     'accuracy, '
                                                                     'Polish '
                                                                     'grammaticality, '
                                                                     'pattern '
                                                                     'fit, '
                                                                     'register '
                                                                     'and '
                                                                     'CEFR. '
                                                                     'Accepted '
                                                                     'against '
                                                                     'the '
                                                                     'current '
                                                                     'tier-2 '
                                                                     'scope.',
                                                             'reviewedAt': '2026-08-18',
                                                             'scopeDigest': 'sha256:802ce5a63c322d5f7ad1e255e46add9dbcfc1707381db87908d1bb82ea4ffc1c',
                                                             'scopeVersion': 1}],
 'vp-p-interesowac-sie-be-interested-in-instrumental-topic-1ab788e84e01': [{'decision': 'accept',
                                                                            'kind': 'correction',
                                                                            'note': 'Owner-authorized '
                                                                                    'correction, '
                                                                                    '2026-08-18: '
                                                                                    'add '
                                                                                    'English '
                                                                                    'glosses '
                                                                                    'to '
                                                                                    'the '
                                                                                    'Polish '
                                                                                    'illustrations '
                                                                                    'in '
                                                                                    'the '
                                                                                    'learner-facing '
                                                                                    'English '
                                                                                    'prose '
                                                                                    'and, '
                                                                                    'where '
                                                                                    'applicable, '
                                                                                    'complete '
                                                                                    'the '
                                                                                    'example '
                                                                                    'treatment. '
                                                                                    'The '
                                                                                    'corrected '
                                                                                    'wording '
                                                                                    'itself '
                                                                                    'is '
                                                                                    'not '
                                                                                    'product-approved.',
                                                                            'reviewedAt': '2026-08-18',
                                                                            'reviewerRef': 'product-owner-001'},
                                                                           {'actorRef': 'priority7-editorial-review',
                                                                            'decision': 'changes-requested',
                                                                            'kind': 'editorial-review',
                                                                            'note': 'H2 '
                                                                                    'content '
                                                                                    'change: '
                                                                                    'English '
                                                                                    'glosses '
                                                                                    'added '
                                                                                    'to '
                                                                                    'this '
                                                                                    "pattern's "
                                                                                    'Polish '
                                                                                    'illustrations '
                                                                                    'in '
                                                                                    'the '
                                                                                    'learner-facing '
                                                                                    'English '
                                                                                    'prose. '
                                                                                    'Tier-2 '
                                                                                    'scope '
                                                                                    'moved, '
                                                                                    'so '
                                                                                    'the '
                                                                                    'standing '
                                                                                    'editorial '
                                                                                    'acceptance '
                                                                                    'is '
                                                                                    'withdrawn.',
                                                                            'reviewedAt': '2026-08-18'},
                                                                           {'actorRef': 'priority7-editorial-review',
                                                                            'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                                            'decision': 'accept',
                                                                            'kind': 'editorial-review',
                                                                            'note': 'H2 '
                                                                                    're-review: '
                                                                                    'an '
                                                                                    'authoring '
                                                                                    'pass '
                                                                                    'drafted '
                                                                                    'the '
                                                                                    'glosses '
                                                                                    'and '
                                                                                    'examples '
                                                                                    'and '
                                                                                    'a '
                                                                                    'separate '
                                                                                    'final '
                                                                                    'editorial '
                                                                                    'pass '
                                                                                    'audited '
                                                                                    'translation '
                                                                                    'accuracy, '
                                                                                    'Polish '
                                                                                    'grammaticality, '
                                                                                    'pattern '
                                                                                    'fit, '
                                                                                    'register '
                                                                                    'and '
                                                                                    'CEFR. '
                                                                                    'Accepted '
                                                                                    'against '
                                                                                    'the '
                                                                                    'current '
                                                                                    'tier-2 '
                                                                                    'scope.',
                                                                            'reviewedAt': '2026-08-18',
                                                                            'scopeDigest': 'sha256:2676472607aaa36cfbe95a9836c98d6838c09686321e6394e53e0d64c52b3f41',
                                                                            'scopeVersion': 1}],
 'vp-p-lubic-enjoy-thing-or-activity-accusative-object-7e585a50878f': [{'decision': 'accept',
                                                                        'kind': 'correction',
                                                                        'note': 'Owner-authorized '
                                                                                'correction, '
                                                                                '2026-08-18: '
                                                                                'add '
                                                                                'English '
                                                                                'glosses '
                                                                                'to '
                                                                                'the '
                                                                                'Polish '
                                                                                'illustrations '
                                                                                'in '
                                                                                'the '
                                                                                'learner-facing '
                                                                                'English '
                                                                                'prose '
                                                                                'and, '
                                                                                'where '
                                                                                'applicable, '
                                                                                'complete '
                                                                                'the '
                                                                                'example '
                                                                                'treatment. '
                                                                                'The '
                                                                                'corrected '
                                                                                'wording '
                                                                                'itself '
                                                                                'is '
                                                                                'not '
                                                                                'product-approved.',
                                                                        'reviewedAt': '2026-08-18',
                                                                        'reviewerRef': 'product-owner-001'},
                                                                       {'actorRef': 'priority7-editorial-review',
                                                                        'decision': 'changes-requested',
                                                                        'kind': 'editorial-review',
                                                                        'note': 'H2 '
                                                                                'content '
                                                                                'change: '
                                                                                'English '
                                                                                'glosses '
                                                                                'added '
                                                                                'to '
                                                                                'this '
                                                                                "pattern's "
                                                                                'Polish '
                                                                                'illustrations '
                                                                                'in '
                                                                                'the '
                                                                                'learner-facing '
                                                                                'English '
                                                                                'prose. '
                                                                                'Tier-2 '
                                                                                'scope '
                                                                                'moved, '
                                                                                'so '
                                                                                'the '
                                                                                'standing '
                                                                                'editorial '
                                                                                'acceptance '
                                                                                'is '
                                                                                'withdrawn.',
                                                                        'reviewedAt': '2026-08-18'},
                                                                       {'actorRef': 'priority7-editorial-review',
                                                                        'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                                        'decision': 'accept',
                                                                        'kind': 'editorial-review',
                                                                        'note': 'H2 '
                                                                                're-review: '
                                                                                'an '
                                                                                'authoring '
                                                                                'pass '
                                                                                'drafted '
                                                                                'the '
                                                                                'glosses '
                                                                                'and '
                                                                                'examples '
                                                                                'and '
                                                                                'a '
                                                                                'separate '
                                                                                'final '
                                                                                'editorial '
                                                                                'pass '
                                                                                'audited '
                                                                                'translation '
                                                                                'accuracy, '
                                                                                'Polish '
                                                                                'grammaticality, '
                                                                                'pattern '
                                                                                'fit, '
                                                                                'register '
                                                                                'and '
                                                                                'CEFR. '
                                                                                'Accepted '
                                                                                'against '
                                                                                'the '
                                                                                'current '
                                                                                'tier-2 '
                                                                                'scope.',
                                                                        'reviewedAt': '2026-08-18',
                                                                        'scopeDigest': 'sha256:a7f1345490ac609bd55fece8480d8899f5dcd65ea5241092d81c7dba0f95e703',
                                                                        'scopeVersion': 1}],
 'vp-p-lubic-enjoy-thing-or-activity-infinitive-activity-be3742b7ce45': [{'decision': 'accept',
                                                                          'kind': 'correction',
                                                                          'note': 'Owner-authorized '
                                                                                  'correction, '
                                                                                  '2026-08-18: '
                                                                                  'add '
                                                                                  'English '
                                                                                  'glosses '
                                                                                  'to '
                                                                                  'the '
                                                                                  'Polish '
                                                                                  'illustrations '
                                                                                  'in '
                                                                                  'the '
                                                                                  'learner-facing '
                                                                                  'English '
                                                                                  'prose '
                                                                                  'and, '
                                                                                  'where '
                                                                                  'applicable, '
                                                                                  'complete '
                                                                                  'the '
                                                                                  'example '
                                                                                  'treatment. '
                                                                                  'The '
                                                                                  'corrected '
                                                                                  'wording '
                                                                                  'itself '
                                                                                  'is '
                                                                                  'not '
                                                                                  'product-approved.',
                                                                          'reviewedAt': '2026-08-18',
                                                                          'reviewerRef': 'product-owner-001'},
                                                                         {'actorRef': 'priority7-editorial-review',
                                                                          'decision': 'changes-requested',
                                                                          'kind': 'editorial-review',
                                                                          'note': 'H2 '
                                                                                  'content '
                                                                                  'change: '
                                                                                  'English '
                                                                                  'glosses '
                                                                                  'added '
                                                                                  'to '
                                                                                  'this '
                                                                                  "pattern's "
                                                                                  'Polish '
                                                                                  'illustrations '
                                                                                  'in '
                                                                                  'the '
                                                                                  'learner-facing '
                                                                                  'English '
                                                                                  'prose. '
                                                                                  'Tier-2 '
                                                                                  'scope '
                                                                                  'moved, '
                                                                                  'so '
                                                                                  'the '
                                                                                  'standing '
                                                                                  'editorial '
                                                                                  'acceptance '
                                                                                  'is '
                                                                                  'withdrawn.',
                                                                          'reviewedAt': '2026-08-18'},
                                                                         {'actorRef': 'priority7-editorial-review',
                                                                          'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                                          'decision': 'accept',
                                                                          'kind': 'editorial-review',
                                                                          'note': 'H2 '
                                                                                  're-review: '
                                                                                  'an '
                                                                                  'authoring '
                                                                                  'pass '
                                                                                  'drafted '
                                                                                  'the '
                                                                                  'glosses '
                                                                                  'and '
                                                                                  'examples '
                                                                                  'and '
                                                                                  'a '
                                                                                  'separate '
                                                                                  'final '
                                                                                  'editorial '
                                                                                  'pass '
                                                                                  'audited '
                                                                                  'translation '
                                                                                  'accuracy, '
                                                                                  'Polish '
                                                                                  'grammaticality, '
                                                                                  'pattern '
                                                                                  'fit, '
                                                                                  'register '
                                                                                  'and '
                                                                                  'CEFR. '
                                                                                  'Accepted '
                                                                                  'against '
                                                                                  'the '
                                                                                  'current '
                                                                                  'tier-2 '
                                                                                  'scope.',
                                                                          'reviewedAt': '2026-08-18',
                                                                          'scopeDigest': 'sha256:f2465cdf75665291751bfefda8f2eedff757e9da6df017f8fbdff36fa7a4a14a',
                                                                          'scopeVersion': 1}],
 'vp-p-miec-possess-accusative-object-7181f802bd57': [{'decision': 'accept',
                                                       'kind': 'correction',
                                                       'note': 'Owner-authorized '
                                                               'correction, '
                                                               '2026-08-18: '
                                                               'add '
                                                               'English '
                                                               'glosses to '
                                                               'the Polish '
                                                               'illustrations '
                                                               'in the '
                                                               'learner-facing '
                                                               'English '
                                                               'prose and, '
                                                               'where '
                                                               'applicable, '
                                                               'complete '
                                                               'the '
                                                               'example '
                                                               'treatment. '
                                                               'The '
                                                               'corrected '
                                                               'wording '
                                                               'itself is '
                                                               'not '
                                                               'product-approved.',
                                                       'reviewedAt': '2026-08-18',
                                                       'reviewerRef': 'product-owner-001'},
                                                      {'actorRef': 'priority7-editorial-review',
                                                       'decision': 'changes-requested',
                                                       'kind': 'editorial-review',
                                                       'note': 'H2 content '
                                                               'change: '
                                                               'English '
                                                               'glosses '
                                                               'added to '
                                                               'this '
                                                               "pattern's "
                                                               'Polish '
                                                               'illustrations '
                                                               'in the '
                                                               'learner-facing '
                                                               'English '
                                                               'prose. '
                                                               'Tier-2 '
                                                               'scope '
                                                               'moved, so '
                                                               'the '
                                                               'standing '
                                                               'editorial '
                                                               'acceptance '
                                                               'is '
                                                               'withdrawn.',
                                                       'reviewedAt': '2026-08-18'},
                                                      {'actorRef': 'priority7-editorial-review',
                                                       'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                       'decision': 'accept',
                                                       'kind': 'editorial-review',
                                                       'note': 'H2 '
                                                               're-review: '
                                                               'an '
                                                               'authoring '
                                                               'pass '
                                                               'drafted '
                                                               'the '
                                                               'glosses '
                                                               'and '
                                                               'examples '
                                                               'and a '
                                                               'separate '
                                                               'final '
                                                               'editorial '
                                                               'pass '
                                                               'audited '
                                                               'translation '
                                                               'accuracy, '
                                                               'Polish '
                                                               'grammaticality, '
                                                               'pattern '
                                                               'fit, '
                                                               'register '
                                                               'and CEFR. '
                                                               'Accepted '
                                                               'against '
                                                               'the '
                                                               'current '
                                                               'tier-2 '
                                                               'scope.',
                                                       'reviewedAt': '2026-08-18',
                                                       'scopeDigest': 'sha256:a8abed99f3049ff688700815f406260046a3b5d1e08a1c1c45021d6943194522',
                                                       'scopeVersion': 1}],
 'vp-p-mowic-tell-content-dative-recipient-accusative-content-2f2b1add1960': [{'decision': 'accept',
                                                                               'kind': 'correction',
                                                                               'note': 'Owner-authorized '
                                                                                       'correction, '
                                                                                       '2026-08-18: '
                                                                                       'add '
                                                                                       'English '
                                                                                       'glosses '
                                                                                       'to '
                                                                                       'the '
                                                                                       'Polish '
                                                                                       'illustrations '
                                                                                       'in '
                                                                                       'the '
                                                                                       'learner-facing '
                                                                                       'English '
                                                                                       'prose '
                                                                                       'and, '
                                                                                       'where '
                                                                                       'applicable, '
                                                                                       'complete '
                                                                                       'the '
                                                                                       'example '
                                                                                       'treatment. '
                                                                                       'The '
                                                                                       'corrected '
                                                                                       'wording '
                                                                                       'itself '
                                                                                       'is '
                                                                                       'not '
                                                                                       'product-approved.',
                                                                               'reviewedAt': '2026-08-18',
                                                                               'reviewerRef': 'product-owner-001'},
                                                                              {'actorRef': 'priority7-editorial-review',
                                                                               'decision': 'changes-requested',
                                                                               'kind': 'editorial-review',
                                                                               'note': 'H2 '
                                                                                       'content '
                                                                                       'change: '
                                                                                       'English '
                                                                                       'glosses '
                                                                                       'added '
                                                                                       'to '
                                                                                       'the '
                                                                                       'Polish '
                                                                                       'illustrations '
                                                                                       'and '
                                                                                       'a '
                                                                                       'first '
                                                                                       'example '
                                                                                       'added '
                                                                                       'to '
                                                                                       'this '
                                                                                       'pattern. '
                                                                                       'Tier-2 '
                                                                                       'scope '
                                                                                       'moved, '
                                                                                       'so '
                                                                                       'the '
                                                                                       'standing '
                                                                                       'editorial '
                                                                                       'acceptance '
                                                                                       'is '
                                                                                       'withdrawn.',
                                                                               'reviewedAt': '2026-08-18'},
                                                                              {'actorRef': 'priority7-editorial-review',
                                                                               'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                                               'decision': 'accept',
                                                                               'kind': 'editorial-review',
                                                                               'note': 'H2 '
                                                                                       're-review: '
                                                                                       'an '
                                                                                       'authoring '
                                                                                       'pass '
                                                                                       'drafted '
                                                                                       'the '
                                                                                       'glosses '
                                                                                       'and '
                                                                                       'examples '
                                                                                       'and '
                                                                                       'a '
                                                                                       'separate '
                                                                                       'final '
                                                                                       'editorial '
                                                                                       'pass '
                                                                                       'audited '
                                                                                       'translation '
                                                                                       'accuracy, '
                                                                                       'Polish '
                                                                                       'grammaticality, '
                                                                                       'pattern '
                                                                                       'fit, '
                                                                                       'register '
                                                                                       'and '
                                                                                       'CEFR. '
                                                                                       'Accepted '
                                                                                       'against '
                                                                                       'the '
                                                                                       'current '
                                                                                       'tier-2 '
                                                                                       'scope.',
                                                                               'reviewedAt': '2026-08-18',
                                                                               'scopeDigest': 'sha256:a6ee042c9f36c8cda1c41890a26120cd579abae139b6bc4196e96c3a1e4db641',
                                                                               'scopeVersion': 1}],
 'vp-p-mowic-tell-content-dative-recipient-ze-clause-a01ddc4a4736': [{'decision': 'accept',
                                                                      'kind': 'correction',
                                                                      'note': 'Owner-authorized '
                                                                              'correction, '
                                                                              '2026-08-18: '
                                                                              'add '
                                                                              'English '
                                                                              'glosses '
                                                                              'to '
                                                                              'the '
                                                                              'Polish '
                                                                              'illustrations '
                                                                              'in '
                                                                              'the '
                                                                              'learner-facing '
                                                                              'English '
                                                                              'prose '
                                                                              'and, '
                                                                              'where '
                                                                              'applicable, '
                                                                              'complete '
                                                                              'the '
                                                                              'example '
                                                                              'treatment. '
                                                                              'The '
                                                                              'corrected '
                                                                              'wording '
                                                                              'itself '
                                                                              'is '
                                                                              'not '
                                                                              'product-approved.',
                                                                      'reviewedAt': '2026-08-18',
                                                                      'reviewerRef': 'product-owner-001'},
                                                                     {'actorRef': 'priority7-editorial-review',
                                                                      'decision': 'changes-requested',
                                                                      'kind': 'editorial-review',
                                                                      'note': 'H2 '
                                                                              'content '
                                                                              'change: '
                                                                              'English '
                                                                              'glosses '
                                                                              'added '
                                                                              'to '
                                                                              'the '
                                                                              'Polish '
                                                                              'illustrations '
                                                                              'and '
                                                                              'a '
                                                                              'first '
                                                                              'example '
                                                                              'added '
                                                                              'to '
                                                                              'this '
                                                                              'pattern. '
                                                                              'Tier-2 '
                                                                              'scope '
                                                                              'moved, '
                                                                              'so '
                                                                              'the '
                                                                              'standing '
                                                                              'editorial '
                                                                              'acceptance '
                                                                              'is '
                                                                              'withdrawn.',
                                                                      'reviewedAt': '2026-08-18'},
                                                                     {'actorRef': 'priority7-editorial-review',
                                                                      'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                                      'decision': 'accept',
                                                                      'kind': 'editorial-review',
                                                                      'note': 'H2 '
                                                                              're-review: '
                                                                              'an '
                                                                              'authoring '
                                                                              'pass '
                                                                              'drafted '
                                                                              'the '
                                                                              'glosses '
                                                                              'and '
                                                                              'examples '
                                                                              'and '
                                                                              'a '
                                                                              'separate '
                                                                              'final '
                                                                              'editorial '
                                                                              'pass '
                                                                              'audited '
                                                                              'translation '
                                                                              'accuracy, '
                                                                              'Polish '
                                                                              'grammaticality, '
                                                                              'pattern '
                                                                              'fit, '
                                                                              'register '
                                                                              'and '
                                                                              'CEFR. '
                                                                              'Accepted '
                                                                              'against '
                                                                              'the '
                                                                              'current '
                                                                              'tier-2 '
                                                                              'scope.',
                                                                      'reviewedAt': '2026-08-18',
                                                                      'scopeDigest': 'sha256:f951b741fc0703aee8f8bcc96b13939932f4930466a852c52ba155d9ebb786d8',
                                                                      'scopeVersion': 1}],
 'vp-p-myslec-think-about-o-locative-topic-edf0461e0dd2': [{'decision': 'accept',
                                                            'kind': 'correction',
                                                            'note': 'Owner-authorized '
                                                                    'correction, '
                                                                    '2026-08-18: '
                                                                    'add '
                                                                    'English '
                                                                    'glosses '
                                                                    'to '
                                                                    'the '
                                                                    'Polish '
                                                                    'illustrations '
                                                                    'in '
                                                                    'the '
                                                                    'learner-facing '
                                                                    'English '
                                                                    'prose '
                                                                    'and, '
                                                                    'where '
                                                                    'applicable, '
                                                                    'complete '
                                                                    'the '
                                                                    'example '
                                                                    'treatment. '
                                                                    'The '
                                                                    'corrected '
                                                                    'wording '
                                                                    'itself '
                                                                    'is '
                                                                    'not '
                                                                    'product-approved.',
                                                            'reviewedAt': '2026-08-18',
                                                            'reviewerRef': 'product-owner-001'},
                                                           {'actorRef': 'priority7-editorial-review',
                                                            'decision': 'changes-requested',
                                                            'kind': 'editorial-review',
                                                            'note': 'H2 '
                                                                    'content '
                                                                    'change: '
                                                                    'English '
                                                                    'glosses '
                                                                    'added '
                                                                    'to '
                                                                    'this '
                                                                    "pattern's "
                                                                    'Polish '
                                                                    'illustrations '
                                                                    'in '
                                                                    'the '
                                                                    'learner-facing '
                                                                    'English '
                                                                    'prose. '
                                                                    'Tier-2 '
                                                                    'scope '
                                                                    'moved, '
                                                                    'so '
                                                                    'the '
                                                                    'standing '
                                                                    'editorial '
                                                                    'acceptance '
                                                                    'is '
                                                                    'withdrawn.',
                                                            'reviewedAt': '2026-08-18'},
                                                           {'actorRef': 'priority7-editorial-review',
                                                            'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                            'decision': 'accept',
                                                            'kind': 'editorial-review',
                                                            'note': 'H2 '
                                                                    're-review: '
                                                                    'an '
                                                                    'authoring '
                                                                    'pass '
                                                                    'drafted '
                                                                    'the '
                                                                    'glosses '
                                                                    'and '
                                                                    'examples '
                                                                    'and a '
                                                                    'separate '
                                                                    'final '
                                                                    'editorial '
                                                                    'pass '
                                                                    'audited '
                                                                    'translation '
                                                                    'accuracy, '
                                                                    'Polish '
                                                                    'grammaticality, '
                                                                    'pattern '
                                                                    'fit, '
                                                                    'register '
                                                                    'and '
                                                                    'CEFR. '
                                                                    'Accepted '
                                                                    'against '
                                                                    'the '
                                                                    'current '
                                                                    'tier-2 '
                                                                    'scope.',
                                                            'reviewedAt': '2026-08-18',
                                                            'scopeDigest': 'sha256:4a6f1fb87972022b4eb36432d08c6f3868f8d4762ce2061c00f70be5e8c08efe',
                                                            'scopeVersion': 1}],
 'vp-p-opiekowac-sie-care-for-instrumental-object-8aa6f0a91e5b': [{'decision': 'accept',
                                                                   'kind': 'correction',
                                                                   'note': 'Owner-authorized '
                                                                           'correction, '
                                                                           '2026-08-18: '
                                                                           'add '
                                                                           'English '
                                                                           'glosses '
                                                                           'to '
                                                                           'the '
                                                                           'Polish '
                                                                           'illustrations '
                                                                           'in '
                                                                           'the '
                                                                           'learner-facing '
                                                                           'English '
                                                                           'prose '
                                                                           'and, '
                                                                           'where '
                                                                           'applicable, '
                                                                           'complete '
                                                                           'the '
                                                                           'example '
                                                                           'treatment. '
                                                                           'The '
                                                                           'corrected '
                                                                           'wording '
                                                                           'itself '
                                                                           'is '
                                                                           'not '
                                                                           'product-approved.',
                                                                   'reviewedAt': '2026-08-18',
                                                                   'reviewerRef': 'product-owner-001'},
                                                                  {'actorRef': 'priority7-editorial-review',
                                                                   'decision': 'changes-requested',
                                                                   'kind': 'editorial-review',
                                                                   'note': 'H2 '
                                                                           'content '
                                                                           'change: '
                                                                           'English '
                                                                           'glosses '
                                                                           'added '
                                                                           'to '
                                                                           'this '
                                                                           "pattern's "
                                                                           'Polish '
                                                                           'illustrations '
                                                                           'in '
                                                                           'the '
                                                                           'learner-facing '
                                                                           'English '
                                                                           'prose. '
                                                                           'Tier-2 '
                                                                           'scope '
                                                                           'moved, '
                                                                           'so '
                                                                           'the '
                                                                           'standing '
                                                                           'editorial '
                                                                           'acceptance '
                                                                           'is '
                                                                           'withdrawn.',
                                                                   'reviewedAt': '2026-08-18'},
                                                                  {'actorRef': 'priority7-editorial-review',
                                                                   'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                                   'decision': 'accept',
                                                                   'kind': 'editorial-review',
                                                                   'note': 'H2 '
                                                                           're-review: '
                                                                           'an '
                                                                           'authoring '
                                                                           'pass '
                                                                           'drafted '
                                                                           'the '
                                                                           'glosses '
                                                                           'and '
                                                                           'examples '
                                                                           'and '
                                                                           'a '
                                                                           'separate '
                                                                           'final '
                                                                           'editorial '
                                                                           'pass '
                                                                           'audited '
                                                                           'translation '
                                                                           'accuracy, '
                                                                           'Polish '
                                                                           'grammaticality, '
                                                                           'pattern '
                                                                           'fit, '
                                                                           'register '
                                                                           'and '
                                                                           'CEFR. '
                                                                           'Accepted '
                                                                           'against '
                                                                           'the '
                                                                           'current '
                                                                           'tier-2 '
                                                                           'scope.',
                                                                   'reviewedAt': '2026-08-18',
                                                                   'scopeDigest': 'sha256:8a9d70c10c163ddd0d9d3cdbbfdccc76f8ba20f09259c1e56598e95a1b44c9f3',
                                                                   'scopeVersion': 1}],
 'vp-p-placic-pay-instrumental-method-ef4313d0d5ce': [{'decision': 'accept',
                                                       'kind': 'correction',
                                                       'note': 'Owner-authorized '
                                                               'correction, '
                                                               '2026-08-18: '
                                                               'add '
                                                               'English '
                                                               'glosses to '
                                                               'the Polish '
                                                               'illustrations '
                                                               'in the '
                                                               'learner-facing '
                                                               'English '
                                                               'prose and, '
                                                               'where '
                                                               'applicable, '
                                                               'complete '
                                                               'the '
                                                               'example '
                                                               'treatment. '
                                                               'The '
                                                               'corrected '
                                                               'wording '
                                                               'itself is '
                                                               'not '
                                                               'product-approved.',
                                                       'reviewedAt': '2026-08-18',
                                                       'reviewerRef': 'product-owner-001'},
                                                      {'actorRef': 'priority7-editorial-review',
                                                       'decision': 'changes-requested',
                                                       'kind': 'editorial-review',
                                                       'note': 'H2 content '
                                                               'change: '
                                                               'English '
                                                               'glosses '
                                                               'added to '
                                                               'this '
                                                               "pattern's "
                                                               'Polish '
                                                               'illustrations '
                                                               'in the '
                                                               'learner-facing '
                                                               'English '
                                                               'prose. '
                                                               'Tier-2 '
                                                               'scope '
                                                               'moved, so '
                                                               'the '
                                                               'standing '
                                                               'editorial '
                                                               'acceptance '
                                                               'is '
                                                               'withdrawn.',
                                                       'reviewedAt': '2026-08-18'},
                                                      {'actorRef': 'priority7-editorial-review',
                                                       'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                       'decision': 'accept',
                                                       'kind': 'editorial-review',
                                                       'note': 'H2 '
                                                               're-review: '
                                                               'an '
                                                               'authoring '
                                                               'pass '
                                                               'drafted '
                                                               'the '
                                                               'glosses '
                                                               'and '
                                                               'examples '
                                                               'and a '
                                                               'separate '
                                                               'final '
                                                               'editorial '
                                                               'pass '
                                                               'audited '
                                                               'translation '
                                                               'accuracy, '
                                                               'Polish '
                                                               'grammaticality, '
                                                               'pattern '
                                                               'fit, '
                                                               'register '
                                                               'and CEFR. '
                                                               'Accepted '
                                                               'against '
                                                               'the '
                                                               'current '
                                                               'tier-2 '
                                                               'scope.',
                                                       'reviewedAt': '2026-08-18',
                                                       'scopeDigest': 'sha256:74f94db96b2397208e3fe224360efab6cfaf3964d83b7974a1371e07743708b4',
                                                       'scopeVersion': 1}],
 'vp-p-placic-pay-za-accusative-goods-73c6760c091d': [{'decision': 'accept',
                                                       'kind': 'correction',
                                                       'note': 'Owner-authorized '
                                                               'correction, '
                                                               '2026-08-18: '
                                                               'add '
                                                               'English '
                                                               'glosses to '
                                                               'the Polish '
                                                               'illustrations '
                                                               'in the '
                                                               'learner-facing '
                                                               'English '
                                                               'prose and, '
                                                               'where '
                                                               'applicable, '
                                                               'complete '
                                                               'the '
                                                               'example '
                                                               'treatment. '
                                                               'The '
                                                               'corrected '
                                                               'wording '
                                                               'itself is '
                                                               'not '
                                                               'product-approved.',
                                                       'reviewedAt': '2026-08-18',
                                                       'reviewerRef': 'product-owner-001'},
                                                      {'actorRef': 'priority7-editorial-review',
                                                       'decision': 'changes-requested',
                                                       'kind': 'editorial-review',
                                                       'note': 'H2 content '
                                                               'change: '
                                                               'English '
                                                               'glosses '
                                                               'added to '
                                                               'this '
                                                               "pattern's "
                                                               'Polish '
                                                               'illustrations '
                                                               'in the '
                                                               'learner-facing '
                                                               'English '
                                                               'prose. '
                                                               'Tier-2 '
                                                               'scope '
                                                               'moved, so '
                                                               'the '
                                                               'standing '
                                                               'editorial '
                                                               'acceptance '
                                                               'is '
                                                               'withdrawn.',
                                                       'reviewedAt': '2026-08-18'},
                                                      {'actorRef': 'priority7-editorial-review',
                                                       'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                       'decision': 'accept',
                                                       'kind': 'editorial-review',
                                                       'note': 'H2 '
                                                               're-review: '
                                                               'an '
                                                               'authoring '
                                                               'pass '
                                                               'drafted '
                                                               'the '
                                                               'glosses '
                                                               'and '
                                                               'examples '
                                                               'and a '
                                                               'separate '
                                                               'final '
                                                               'editorial '
                                                               'pass '
                                                               'audited '
                                                               'translation '
                                                               'accuracy, '
                                                               'Polish '
                                                               'grammaticality, '
                                                               'pattern '
                                                               'fit, '
                                                               'register '
                                                               'and CEFR. '
                                                               'Accepted '
                                                               'against '
                                                               'the '
                                                               'current '
                                                               'tier-2 '
                                                               'scope.',
                                                       'reviewedAt': '2026-08-18',
                                                       'scopeDigest': 'sha256:161cd99af0098afebbdf790cbd384fc162e79171ae806163016d0fb347bf52f0',
                                                       'scopeVersion': 1}],
 'vp-p-podobac-sie-appeal-to-nominative-stimulus-dative-experiencer-ef199e675ee9': [{'decision': 'accept',
                                                                                     'kind': 'correction',
                                                                                     'note': 'Owner-authorized '
                                                                                             'correction, '
                                                                                             '2026-08-18: '
                                                                                             'add '
                                                                                             'English '
                                                                                             'glosses '
                                                                                             'to '
                                                                                             'the '
                                                                                             'Polish '
                                                                                             'illustrations '
                                                                                             'in '
                                                                                             'the '
                                                                                             'learner-facing '
                                                                                             'English '
                                                                                             'prose '
                                                                                             'and, '
                                                                                             'where '
                                                                                             'applicable, '
                                                                                             'complete '
                                                                                             'the '
                                                                                             'example '
                                                                                             'treatment. '
                                                                                             'The '
                                                                                             'corrected '
                                                                                             'wording '
                                                                                             'itself '
                                                                                             'is '
                                                                                             'not '
                                                                                             'product-approved.',
                                                                                     'reviewedAt': '2026-08-18',
                                                                                     'reviewerRef': 'product-owner-001'},
                                                                                    {'actorRef': 'priority7-editorial-review',
                                                                                     'decision': 'changes-requested',
                                                                                     'kind': 'editorial-review',
                                                                                     'note': 'H2 '
                                                                                             'content '
                                                                                             'change: '
                                                                                             'English '
                                                                                             'glosses '
                                                                                             'added '
                                                                                             'to '
                                                                                             'the '
                                                                                             'Polish '
                                                                                             'illustrations '
                                                                                             'and '
                                                                                             'a '
                                                                                             'first '
                                                                                             'example '
                                                                                             'added '
                                                                                             'to '
                                                                                             'this '
                                                                                             'pattern. '
                                                                                             'Tier-2 '
                                                                                             'scope '
                                                                                             'moved, '
                                                                                             'so '
                                                                                             'the '
                                                                                             'standing '
                                                                                             'editorial '
                                                                                             'acceptance '
                                                                                             'is '
                                                                                             'withdrawn.',
                                                                                     'reviewedAt': '2026-08-18'},
                                                                                    {'actorRef': 'priority7-editorial-review',
                                                                                     'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                                                     'decision': 'accept',
                                                                                     'kind': 'editorial-review',
                                                                                     'note': 'H2 '
                                                                                             're-review: '
                                                                                             'an '
                                                                                             'authoring '
                                                                                             'pass '
                                                                                             'drafted '
                                                                                             'the '
                                                                                             'glosses '
                                                                                             'and '
                                                                                             'examples '
                                                                                             'and '
                                                                                             'a '
                                                                                             'separate '
                                                                                             'final '
                                                                                             'editorial '
                                                                                             'pass '
                                                                                             'audited '
                                                                                             'translation '
                                                                                             'accuracy, '
                                                                                             'Polish '
                                                                                             'grammaticality, '
                                                                                             'pattern '
                                                                                             'fit, '
                                                                                             'register '
                                                                                             'and '
                                                                                             'CEFR. '
                                                                                             'Accepted '
                                                                                             'against '
                                                                                             'the '
                                                                                             'current '
                                                                                             'tier-2 '
                                                                                             'scope.',
                                                                                     'reviewedAt': '2026-08-18',
                                                                                     'scopeDigest': 'sha256:aeb16b71b3e975b79ac4d19a54b2190997e289b383b0a1b6badd1384519c4156',
                                                                                     'scopeVersion': 1}],
 'vp-p-pomagac-assist-dative-recipient-9f0a375c5e81': [{'decision': 'accept',
                                                        'kind': 'correction',
                                                        'note': 'Owner-authorized '
                                                                'correction, '
                                                                '2026-08-18: '
                                                                'add '
                                                                'English '
                                                                'glosses '
                                                                'to the '
                                                                'Polish '
                                                                'illustrations '
                                                                'in the '
                                                                'learner-facing '
                                                                'English '
                                                                'prose '
                                                                'and, '
                                                                'where '
                                                                'applicable, '
                                                                'complete '
                                                                'the '
                                                                'example '
                                                                'treatment. '
                                                                'The '
                                                                'corrected '
                                                                'wording '
                                                                'itself is '
                                                                'not '
                                                                'product-approved.',
                                                        'reviewedAt': '2026-08-18',
                                                        'reviewerRef': 'product-owner-001'},
                                                       {'actorRef': 'priority7-editorial-review',
                                                        'decision': 'changes-requested',
                                                        'kind': 'editorial-review',
                                                        'note': 'H2 '
                                                                'content '
                                                                'change: '
                                                                'English '
                                                                'glosses '
                                                                'added to '
                                                                'the '
                                                                'Polish '
                                                                'illustrations '
                                                                'and a '
                                                                'first '
                                                                'example '
                                                                'added to '
                                                                'this '
                                                                'pattern. '
                                                                'Tier-2 '
                                                                'scope '
                                                                'moved, so '
                                                                'the '
                                                                'standing '
                                                                'editorial '
                                                                'acceptance '
                                                                'is '
                                                                'withdrawn.',
                                                        'reviewedAt': '2026-08-18'},
                                                       {'actorRef': 'priority7-editorial-review',
                                                        'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                        'decision': 'accept',
                                                        'kind': 'editorial-review',
                                                        'note': 'H2 '
                                                                're-review: '
                                                                'an '
                                                                'authoring '
                                                                'pass '
                                                                'drafted '
                                                                'the '
                                                                'glosses '
                                                                'and '
                                                                'examples '
                                                                'and a '
                                                                'separate '
                                                                'final '
                                                                'editorial '
                                                                'pass '
                                                                'audited '
                                                                'translation '
                                                                'accuracy, '
                                                                'Polish '
                                                                'grammaticality, '
                                                                'pattern '
                                                                'fit, '
                                                                'register '
                                                                'and CEFR. '
                                                                'Accepted '
                                                                'against '
                                                                'the '
                                                                'current '
                                                                'tier-2 '
                                                                'scope.',
                                                        'reviewedAt': '2026-08-18',
                                                        'scopeDigest': 'sha256:fe7d03896010373866cd827f549c5be9cdf056b2604779c8805cbca1700a4572',
                                                        'scopeVersion': 1}],
 'vp-p-pomagac-assist-dative-recipient-w-locative-area-1e507dcdb869': [{'decision': 'accept',
                                                                        'kind': 'correction',
                                                                        'note': 'Owner-authorized '
                                                                                'correction, '
                                                                                '2026-08-18: '
                                                                                'add '
                                                                                'English '
                                                                                'glosses '
                                                                                'to '
                                                                                'the '
                                                                                'Polish '
                                                                                'illustrations '
                                                                                'in '
                                                                                'the '
                                                                                'learner-facing '
                                                                                'English '
                                                                                'prose '
                                                                                'and, '
                                                                                'where '
                                                                                'applicable, '
                                                                                'complete '
                                                                                'the '
                                                                                'example '
                                                                                'treatment. '
                                                                                'The '
                                                                                'corrected '
                                                                                'wording '
                                                                                'itself '
                                                                                'is '
                                                                                'not '
                                                                                'product-approved.',
                                                                        'reviewedAt': '2026-08-18',
                                                                        'reviewerRef': 'product-owner-001'},
                                                                       {'actorRef': 'priority7-editorial-review',
                                                                        'decision': 'changes-requested',
                                                                        'kind': 'editorial-review',
                                                                        'note': 'H2 '
                                                                                'content '
                                                                                'change: '
                                                                                'English '
                                                                                'glosses '
                                                                                'added '
                                                                                'to '
                                                                                'the '
                                                                                'Polish '
                                                                                'illustrations '
                                                                                'and '
                                                                                'a '
                                                                                'first '
                                                                                'example '
                                                                                'added '
                                                                                'to '
                                                                                'this '
                                                                                'pattern. '
                                                                                'Tier-2 '
                                                                                'scope '
                                                                                'moved, '
                                                                                'so '
                                                                                'the '
                                                                                'standing '
                                                                                'editorial '
                                                                                'acceptance '
                                                                                'is '
                                                                                'withdrawn.',
                                                                        'reviewedAt': '2026-08-18'},
                                                                       {'actorRef': 'priority7-editorial-review',
                                                                        'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                                        'decision': 'accept',
                                                                        'kind': 'editorial-review',
                                                                        'note': 'H2 '
                                                                                're-review: '
                                                                                'an '
                                                                                'authoring '
                                                                                'pass '
                                                                                'drafted '
                                                                                'the '
                                                                                'glosses '
                                                                                'and '
                                                                                'examples '
                                                                                'and '
                                                                                'a '
                                                                                'separate '
                                                                                'final '
                                                                                'editorial '
                                                                                'pass '
                                                                                'audited '
                                                                                'translation '
                                                                                'accuracy, '
                                                                                'Polish '
                                                                                'grammaticality, '
                                                                                'pattern '
                                                                                'fit, '
                                                                                'register '
                                                                                'and '
                                                                                'CEFR. '
                                                                                'Accepted '
                                                                                'against '
                                                                                'the '
                                                                                'current '
                                                                                'tier-2 '
                                                                                'scope.',
                                                                        'reviewedAt': '2026-08-18',
                                                                        'scopeDigest': 'sha256:9703341f3fcdd7ba596dc511576ba915e9c714ad2e7f4daa8b69820d95d44ac9',
                                                                        'scopeVersion': 1}],
 'vp-p-potrzebowac-need-genitive-object-437fafad17d2': [{'decision': 'accept',
                                                         'kind': 'correction',
                                                         'note': 'Owner-authorized '
                                                                 'correction, '
                                                                 '2026-08-18: '
                                                                 'add '
                                                                 'English '
                                                                 'glosses '
                                                                 'to the '
                                                                 'Polish '
                                                                 'illustrations '
                                                                 'in the '
                                                                 'learner-facing '
                                                                 'English '
                                                                 'prose '
                                                                 'and, '
                                                                 'where '
                                                                 'applicable, '
                                                                 'complete '
                                                                 'the '
                                                                 'example '
                                                                 'treatment. '
                                                                 'The '
                                                                 'corrected '
                                                                 'wording '
                                                                 'itself '
                                                                 'is not '
                                                                 'product-approved.',
                                                         'reviewedAt': '2026-08-18',
                                                         'reviewerRef': 'product-owner-001'},
                                                        {'actorRef': 'priority7-editorial-review',
                                                         'decision': 'changes-requested',
                                                         'kind': 'editorial-review',
                                                         'note': 'H2 '
                                                                 'content '
                                                                 'change: '
                                                                 'English '
                                                                 'glosses '
                                                                 'added to '
                                                                 'this '
                                                                 "pattern's "
                                                                 'Polish '
                                                                 'illustrations '
                                                                 'in the '
                                                                 'learner-facing '
                                                                 'English '
                                                                 'prose. '
                                                                 'Tier-2 '
                                                                 'scope '
                                                                 'moved, '
                                                                 'so the '
                                                                 'standing '
                                                                 'editorial '
                                                                 'acceptance '
                                                                 'is '
                                                                 'withdrawn.',
                                                         'reviewedAt': '2026-08-18'},
                                                        {'actorRef': 'priority7-editorial-review',
                                                         'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                         'decision': 'accept',
                                                         'kind': 'editorial-review',
                                                         'note': 'H2 '
                                                                 're-review: '
                                                                 'an '
                                                                 'authoring '
                                                                 'pass '
                                                                 'drafted '
                                                                 'the '
                                                                 'glosses '
                                                                 'and '
                                                                 'examples '
                                                                 'and a '
                                                                 'separate '
                                                                 'final '
                                                                 'editorial '
                                                                 'pass '
                                                                 'audited '
                                                                 'translation '
                                                                 'accuracy, '
                                                                 'Polish '
                                                                 'grammaticality, '
                                                                 'pattern '
                                                                 'fit, '
                                                                 'register '
                                                                 'and '
                                                                 'CEFR. '
                                                                 'Accepted '
                                                                 'against '
                                                                 'the '
                                                                 'current '
                                                                 'tier-2 '
                                                                 'scope.',
                                                         'reviewedAt': '2026-08-18',
                                                         'scopeDigest': 'sha256:a813d15b5757852a82940f192a2a4ea9002d2fdad199cfa21bdc71c76b1e1a45',
                                                         'scopeVersion': 1}],
 'vp-p-prosic-request-accusative-person-o-accusative-thing-b7a8d9ce1a99': [{'decision': 'accept',
                                                                            'kind': 'correction',
                                                                            'note': 'Owner-authorized '
                                                                                    'correction, '
                                                                                    '2026-08-18: '
                                                                                    'add '
                                                                                    'English '
                                                                                    'glosses '
                                                                                    'to '
                                                                                    'the '
                                                                                    'Polish '
                                                                                    'illustrations '
                                                                                    'in '
                                                                                    'the '
                                                                                    'learner-facing '
                                                                                    'English '
                                                                                    'prose '
                                                                                    'and, '
                                                                                    'where '
                                                                                    'applicable, '
                                                                                    'complete '
                                                                                    'the '
                                                                                    'example '
                                                                                    'treatment. '
                                                                                    'The '
                                                                                    'corrected '
                                                                                    'wording '
                                                                                    'itself '
                                                                                    'is '
                                                                                    'not '
                                                                                    'product-approved.',
                                                                            'reviewedAt': '2026-08-18',
                                                                            'reviewerRef': 'product-owner-001'},
                                                                           {'actorRef': 'priority7-editorial-review',
                                                                            'decision': 'changes-requested',
                                                                            'kind': 'editorial-review',
                                                                            'note': 'H2 '
                                                                                    'content '
                                                                                    'change: '
                                                                                    'English '
                                                                                    'glosses '
                                                                                    'added '
                                                                                    'to '
                                                                                    'the '
                                                                                    'Polish '
                                                                                    'illustrations '
                                                                                    'and '
                                                                                    'a '
                                                                                    'first '
                                                                                    'example '
                                                                                    'added '
                                                                                    'to '
                                                                                    'this '
                                                                                    'pattern. '
                                                                                    'Tier-2 '
                                                                                    'scope '
                                                                                    'moved, '
                                                                                    'so '
                                                                                    'the '
                                                                                    'standing '
                                                                                    'editorial '
                                                                                    'acceptance '
                                                                                    'is '
                                                                                    'withdrawn.',
                                                                            'reviewedAt': '2026-08-18'},
                                                                           {'actorRef': 'priority7-editorial-review',
                                                                            'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                                            'decision': 'accept',
                                                                            'kind': 'editorial-review',
                                                                            'note': 'H2 '
                                                                                    're-review: '
                                                                                    'an '
                                                                                    'authoring '
                                                                                    'pass '
                                                                                    'drafted '
                                                                                    'the '
                                                                                    'glosses '
                                                                                    'and '
                                                                                    'examples '
                                                                                    'and '
                                                                                    'a '
                                                                                    'separate '
                                                                                    'final '
                                                                                    'editorial '
                                                                                    'pass '
                                                                                    'audited '
                                                                                    'translation '
                                                                                    'accuracy, '
                                                                                    'Polish '
                                                                                    'grammaticality, '
                                                                                    'pattern '
                                                                                    'fit, '
                                                                                    'register '
                                                                                    'and '
                                                                                    'CEFR. '
                                                                                    'Accepted '
                                                                                    'against '
                                                                                    'the '
                                                                                    'current '
                                                                                    'tier-2 '
                                                                                    'scope.',
                                                                            'reviewedAt': '2026-08-18',
                                                                            'scopeDigest': 'sha256:abc6667d5036236afc7c307e6c29d7b4ce0bd3b0bfc9b11956f5dc0d21a6bbe2',
                                                                            'scopeVersion': 1}],
 'vp-p-prosic-request-o-accusative-request-06d776fbfd20': [{'decision': 'accept',
                                                            'kind': 'correction',
                                                            'note': 'Owner-authorized '
                                                                    'correction, '
                                                                    '2026-08-18: '
                                                                    'add '
                                                                    'English '
                                                                    'glosses '
                                                                    'to '
                                                                    'the '
                                                                    'Polish '
                                                                    'illustrations '
                                                                    'in '
                                                                    'the '
                                                                    'learner-facing '
                                                                    'English '
                                                                    'prose '
                                                                    'and, '
                                                                    'where '
                                                                    'applicable, '
                                                                    'complete '
                                                                    'the '
                                                                    'example '
                                                                    'treatment. '
                                                                    'The '
                                                                    'corrected '
                                                                    'wording '
                                                                    'itself '
                                                                    'is '
                                                                    'not '
                                                                    'product-approved.',
                                                            'reviewedAt': '2026-08-18',
                                                            'reviewerRef': 'product-owner-001'},
                                                           {'actorRef': 'priority7-editorial-review',
                                                            'decision': 'changes-requested',
                                                            'kind': 'editorial-review',
                                                            'note': 'H2 '
                                                                    'content '
                                                                    'change: '
                                                                    'English '
                                                                    'glosses '
                                                                    'added '
                                                                    'to '
                                                                    'this '
                                                                    "pattern's "
                                                                    'Polish '
                                                                    'illustrations '
                                                                    'in '
                                                                    'the '
                                                                    'learner-facing '
                                                                    'English '
                                                                    'prose. '
                                                                    'Tier-2 '
                                                                    'scope '
                                                                    'moved, '
                                                                    'so '
                                                                    'the '
                                                                    'standing '
                                                                    'editorial '
                                                                    'acceptance '
                                                                    'is '
                                                                    'withdrawn.',
                                                            'reviewedAt': '2026-08-18'},
                                                           {'actorRef': 'priority7-editorial-review',
                                                            'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                            'decision': 'accept',
                                                            'kind': 'editorial-review',
                                                            'note': 'H2 '
                                                                    're-review: '
                                                                    'an '
                                                                    'authoring '
                                                                    'pass '
                                                                    'drafted '
                                                                    'the '
                                                                    'glosses '
                                                                    'and '
                                                                    'examples '
                                                                    'and a '
                                                                    'separate '
                                                                    'final '
                                                                    'editorial '
                                                                    'pass '
                                                                    'audited '
                                                                    'translation '
                                                                    'accuracy, '
                                                                    'Polish '
                                                                    'grammaticality, '
                                                                    'pattern '
                                                                    'fit, '
                                                                    'register '
                                                                    'and '
                                                                    'CEFR. '
                                                                    'Accepted '
                                                                    'against '
                                                                    'the '
                                                                    'current '
                                                                    'tier-2 '
                                                                    'scope.',
                                                            'reviewedAt': '2026-08-18',
                                                            'scopeDigest': 'sha256:8d8ed43f477dd7601663ccf6f15f28fc4ff19b5784d1eabde3935e954d2be6d9',
                                                            'scopeVersion': 1}],
 'vp-p-pytac-ask-for-information-accusative-person-o-accusative-topic-841b41ed735a': [{'decision': 'accept',
                                                                                       'kind': 'correction',
                                                                                       'note': 'Owner-authorized '
                                                                                               'correction, '
                                                                                               '2026-08-18: '
                                                                                               'add '
                                                                                               'English '
                                                                                               'glosses '
                                                                                               'to '
                                                                                               'the '
                                                                                               'Polish '
                                                                                               'illustrations '
                                                                                               'in '
                                                                                               'the '
                                                                                               'learner-facing '
                                                                                               'English '
                                                                                               'prose '
                                                                                               'and, '
                                                                                               'where '
                                                                                               'applicable, '
                                                                                               'complete '
                                                                                               'the '
                                                                                               'example '
                                                                                               'treatment. '
                                                                                               'The '
                                                                                               'corrected '
                                                                                               'wording '
                                                                                               'itself '
                                                                                               'is '
                                                                                               'not '
                                                                                               'product-approved.',
                                                                                       'reviewedAt': '2026-08-18',
                                                                                       'reviewerRef': 'product-owner-001'},
                                                                                      {'actorRef': 'priority7-editorial-review',
                                                                                       'decision': 'changes-requested',
                                                                                       'kind': 'editorial-review',
                                                                                       'note': 'H2 '
                                                                                               'content '
                                                                                               'change: '
                                                                                               'English '
                                                                                               'glosses '
                                                                                               'added '
                                                                                               'to '
                                                                                               'this '
                                                                                               "pattern's "
                                                                                               'Polish '
                                                                                               'illustrations '
                                                                                               'in '
                                                                                               'the '
                                                                                               'learner-facing '
                                                                                               'English '
                                                                                               'prose. '
                                                                                               'Tier-2 '
                                                                                               'scope '
                                                                                               'moved, '
                                                                                               'so '
                                                                                               'the '
                                                                                               'standing '
                                                                                               'editorial '
                                                                                               'acceptance '
                                                                                               'is '
                                                                                               'withdrawn.',
                                                                                       'reviewedAt': '2026-08-18'},
                                                                                      {'actorRef': 'priority7-editorial-review',
                                                                                       'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                                                       'decision': 'accept',
                                                                                       'kind': 'editorial-review',
                                                                                       'note': 'H2 '
                                                                                               're-review: '
                                                                                               'an '
                                                                                               'authoring '
                                                                                               'pass '
                                                                                               'drafted '
                                                                                               'the '
                                                                                               'glosses '
                                                                                               'and '
                                                                                               'examples '
                                                                                               'and '
                                                                                               'a '
                                                                                               'separate '
                                                                                               'final '
                                                                                               'editorial '
                                                                                               'pass '
                                                                                               'audited '
                                                                                               'translation '
                                                                                               'accuracy, '
                                                                                               'Polish '
                                                                                               'grammaticality, '
                                                                                               'pattern '
                                                                                               'fit, '
                                                                                               'register '
                                                                                               'and '
                                                                                               'CEFR. '
                                                                                               'Accepted '
                                                                                               'against '
                                                                                               'the '
                                                                                               'current '
                                                                                               'tier-2 '
                                                                                               'scope.',
                                                                                       'reviewedAt': '2026-08-18',
                                                                                       'scopeDigest': 'sha256:5a2ff6fd3752aeb2980873a5e88519f8c9f7fedf7e41be16fc2275e855ca9b8d',
                                                                                       'scopeVersion': 1}],
 'vp-p-pytac-ask-for-information-o-accusative-topic-c89674d989d8': [{'decision': 'accept',
                                                                     'kind': 'correction',
                                                                     'note': 'Owner-authorized '
                                                                             'correction, '
                                                                             '2026-08-18: '
                                                                             'add '
                                                                             'English '
                                                                             'glosses '
                                                                             'to '
                                                                             'the '
                                                                             'Polish '
                                                                             'illustrations '
                                                                             'in '
                                                                             'the '
                                                                             'learner-facing '
                                                                             'English '
                                                                             'prose '
                                                                             'and, '
                                                                             'where '
                                                                             'applicable, '
                                                                             'complete '
                                                                             'the '
                                                                             'example '
                                                                             'treatment. '
                                                                             'The '
                                                                             'corrected '
                                                                             'wording '
                                                                             'itself '
                                                                             'is '
                                                                             'not '
                                                                             'product-approved.',
                                                                     'reviewedAt': '2026-08-18',
                                                                     'reviewerRef': 'product-owner-001'},
                                                                    {'actorRef': 'priority7-editorial-review',
                                                                     'decision': 'changes-requested',
                                                                     'kind': 'editorial-review',
                                                                     'note': 'H2 '
                                                                             'content '
                                                                             'change: '
                                                                             'English '
                                                                             'glosses '
                                                                             'added '
                                                                             'to '
                                                                             'this '
                                                                             "pattern's "
                                                                             'Polish '
                                                                             'illustrations '
                                                                             'in '
                                                                             'the '
                                                                             'learner-facing '
                                                                             'English '
                                                                             'prose. '
                                                                             'Tier-2 '
                                                                             'scope '
                                                                             'moved, '
                                                                             'so '
                                                                             'the '
                                                                             'standing '
                                                                             'editorial '
                                                                             'acceptance '
                                                                             'is '
                                                                             'withdrawn.',
                                                                     'reviewedAt': '2026-08-18'},
                                                                    {'actorRef': 'priority7-editorial-review',
                                                                     'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                                     'decision': 'accept',
                                                                     'kind': 'editorial-review',
                                                                     'note': 'H2 '
                                                                             're-review: '
                                                                             'an '
                                                                             'authoring '
                                                                             'pass '
                                                                             'drafted '
                                                                             'the '
                                                                             'glosses '
                                                                             'and '
                                                                             'examples '
                                                                             'and '
                                                                             'a '
                                                                             'separate '
                                                                             'final '
                                                                             'editorial '
                                                                             'pass '
                                                                             'audited '
                                                                             'translation '
                                                                             'accuracy, '
                                                                             'Polish '
                                                                             'grammaticality, '
                                                                             'pattern '
                                                                             'fit, '
                                                                             'register '
                                                                             'and '
                                                                             'CEFR. '
                                                                             'Accepted '
                                                                             'against '
                                                                             'the '
                                                                             'current '
                                                                             'tier-2 '
                                                                             'scope.',
                                                                     'reviewedAt': '2026-08-18',
                                                                     'scopeDigest': 'sha256:223f73fcac21fa445fbfd574dc985bb8b334ac699a810eb5c7f755d5495f380d',
                                                                     'scopeVersion': 1}],
 'vp-p-rozmawiac-talk-with-o-locative-topic-b1c59475ac05': [{'decision': 'accept',
                                                             'kind': 'correction',
                                                             'note': 'Owner-authorized '
                                                                     'correction, '
                                                                     '2026-08-18: '
                                                                     'add '
                                                                     'English '
                                                                     'glosses '
                                                                     'to '
                                                                     'the '
                                                                     'Polish '
                                                                     'illustrations '
                                                                     'in '
                                                                     'the '
                                                                     'learner-facing '
                                                                     'English '
                                                                     'prose '
                                                                     'and, '
                                                                     'where '
                                                                     'applicable, '
                                                                     'complete '
                                                                     'the '
                                                                     'example '
                                                                     'treatment. '
                                                                     'The '
                                                                     'corrected '
                                                                     'wording '
                                                                     'itself '
                                                                     'is '
                                                                     'not '
                                                                     'product-approved.',
                                                             'reviewedAt': '2026-08-18',
                                                             'reviewerRef': 'product-owner-001'},
                                                            {'actorRef': 'priority7-editorial-review',
                                                             'decision': 'changes-requested',
                                                             'kind': 'editorial-review',
                                                             'note': 'H2 '
                                                                     'content '
                                                                     'change: '
                                                                     'English '
                                                                     'glosses '
                                                                     'added '
                                                                     'to '
                                                                     'the '
                                                                     'Polish '
                                                                     'illustrations '
                                                                     'and '
                                                                     'a '
                                                                     'first '
                                                                     'example '
                                                                     'added '
                                                                     'to '
                                                                     'this '
                                                                     'pattern. '
                                                                     'Tier-2 '
                                                                     'scope '
                                                                     'moved, '
                                                                     'so '
                                                                     'the '
                                                                     'standing '
                                                                     'editorial '
                                                                     'acceptance '
                                                                     'is '
                                                                     'withdrawn.',
                                                             'reviewedAt': '2026-08-18'},
                                                            {'actorRef': 'priority7-editorial-review',
                                                             'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                             'decision': 'accept',
                                                             'kind': 'editorial-review',
                                                             'note': 'H2 '
                                                                     're-review: '
                                                                     'an '
                                                                     'authoring '
                                                                     'pass '
                                                                     'drafted '
                                                                     'the '
                                                                     'glosses '
                                                                     'and '
                                                                     'examples '
                                                                     'and '
                                                                     'a '
                                                                     'separate '
                                                                     'final '
                                                                     'editorial '
                                                                     'pass '
                                                                     'audited '
                                                                     'translation '
                                                                     'accuracy, '
                                                                     'Polish '
                                                                     'grammaticality, '
                                                                     'pattern '
                                                                     'fit, '
                                                                     'register '
                                                                     'and '
                                                                     'CEFR. '
                                                                     'Accepted '
                                                                     'against '
                                                                     'the '
                                                                     'current '
                                                                     'tier-2 '
                                                                     'scope.',
                                                             'reviewedAt': '2026-08-18',
                                                             'scopeDigest': 'sha256:d5a2d770b9ebad308980336ac17c6397acffe1c00d34ebc2bf69dce4bdb76c49',
                                                             'scopeVersion': 1}],
 'vp-p-rozmawiac-talk-with-z-instrumental-interlocutor-8398fa7449ca': [{'decision': 'accept',
                                                                        'kind': 'correction',
                                                                        'note': 'Owner-authorized '
                                                                                'correction, '
                                                                                '2026-08-18: '
                                                                                'add '
                                                                                'English '
                                                                                'glosses '
                                                                                'to '
                                                                                'the '
                                                                                'Polish '
                                                                                'illustrations '
                                                                                'in '
                                                                                'the '
                                                                                'learner-facing '
                                                                                'English '
                                                                                'prose '
                                                                                'and, '
                                                                                'where '
                                                                                'applicable, '
                                                                                'complete '
                                                                                'the '
                                                                                'example '
                                                                                'treatment. '
                                                                                'The '
                                                                                'corrected '
                                                                                'wording '
                                                                                'itself '
                                                                                'is '
                                                                                'not '
                                                                                'product-approved.',
                                                                        'reviewedAt': '2026-08-18',
                                                                        'reviewerRef': 'product-owner-001'},
                                                                       {'actorRef': 'priority7-editorial-review',
                                                                        'decision': 'changes-requested',
                                                                        'kind': 'editorial-review',
                                                                        'note': 'H2 '
                                                                                'content '
                                                                                'change: '
                                                                                'English '
                                                                                'glosses '
                                                                                'added '
                                                                                'to '
                                                                                'the '
                                                                                'Polish '
                                                                                'illustrations '
                                                                                'and '
                                                                                'a '
                                                                                'first '
                                                                                'example '
                                                                                'added '
                                                                                'to '
                                                                                'this '
                                                                                'pattern. '
                                                                                'Tier-2 '
                                                                                'scope '
                                                                                'moved, '
                                                                                'so '
                                                                                'the '
                                                                                'standing '
                                                                                'editorial '
                                                                                'acceptance '
                                                                                'is '
                                                                                'withdrawn.',
                                                                        'reviewedAt': '2026-08-18'},
                                                                       {'actorRef': 'priority7-editorial-review',
                                                                        'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                                        'decision': 'accept',
                                                                        'kind': 'editorial-review',
                                                                        'note': 'H2 '
                                                                                're-review: '
                                                                                'an '
                                                                                'authoring '
                                                                                'pass '
                                                                                'drafted '
                                                                                'the '
                                                                                'glosses '
                                                                                'and '
                                                                                'examples '
                                                                                'and '
                                                                                'a '
                                                                                'separate '
                                                                                'final '
                                                                                'editorial '
                                                                                'pass '
                                                                                'audited '
                                                                                'translation '
                                                                                'accuracy, '
                                                                                'Polish '
                                                                                'grammaticality, '
                                                                                'pattern '
                                                                                'fit, '
                                                                                'register '
                                                                                'and '
                                                                                'CEFR. '
                                                                                'Accepted '
                                                                                'against '
                                                                                'the '
                                                                                'current '
                                                                                'tier-2 '
                                                                                'scope.',
                                                                        'reviewedAt': '2026-08-18',
                                                                        'scopeDigest': 'sha256:35225e59a978ecf8fc6c7f4cc7fdef95da8dcb710da64075f0c22a4318fcc6f3',
                                                                        'scopeVersion': 1}],
 'vp-p-rozmawiac-talk-with-z-instrumental-o-locative-4e586b18cf98': [{'actorRef': 'priority7-editorial-review',
                                                                      'decision': 'changes-requested',
                                                                      'kind': 'editorial-review',
                                                                      'note': 'H2 '
                                                                              'content '
                                                                              'change: '
                                                                              'a '
                                                                              'first '
                                                                              'example '
                                                                              'added '
                                                                              'to '
                                                                              'this '
                                                                              'pattern; '
                                                                              'its '
                                                                              'English '
                                                                              'prose '
                                                                              'carried '
                                                                              'no '
                                                                              'Polish '
                                                                              'illustration '
                                                                              'to '
                                                                              'gloss. '
                                                                              'Tier-2 '
                                                                              'scope '
                                                                              'moved, '
                                                                              'so '
                                                                              'the '
                                                                              'standing '
                                                                              'editorial '
                                                                              'acceptance '
                                                                              'is '
                                                                              'withdrawn.',
                                                                      'reviewedAt': '2026-08-18'},
                                                                     {'actorRef': 'priority7-editorial-review',
                                                                      'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                                      'decision': 'accept',
                                                                      'kind': 'editorial-review',
                                                                      'note': 'H2 '
                                                                              're-review: '
                                                                              'an '
                                                                              'authoring '
                                                                              'pass '
                                                                              'drafted '
                                                                              'the '
                                                                              'glosses '
                                                                              'and '
                                                                              'examples '
                                                                              'and '
                                                                              'a '
                                                                              'separate '
                                                                              'final '
                                                                              'editorial '
                                                                              'pass '
                                                                              'audited '
                                                                              'translation '
                                                                              'accuracy, '
                                                                              'Polish '
                                                                              'grammaticality, '
                                                                              'pattern '
                                                                              'fit, '
                                                                              'register '
                                                                              'and '
                                                                              'CEFR. '
                                                                              'Accepted '
                                                                              'against '
                                                                              'the '
                                                                              'current '
                                                                              'tier-2 '
                                                                              'scope.',
                                                                      'reviewedAt': '2026-08-18',
                                                                      'scopeDigest': 'sha256:98a6840df655b3883c40647bff0d7f6e121d4bb2b1c430d4a8381dbb8ab1c438',
                                                                      'scopeVersion': 1}],
 'vp-p-sluchac-listen-to-genitive-target-a274f84c8d93': [{'decision': 'accept',
                                                          'kind': 'correction',
                                                          'note': 'Owner-authorized '
                                                                  'correction, '
                                                                  '2026-08-18: '
                                                                  'add '
                                                                  'English '
                                                                  'glosses '
                                                                  'to the '
                                                                  'Polish '
                                                                  'illustrations '
                                                                  'in the '
                                                                  'learner-facing '
                                                                  'English '
                                                                  'prose '
                                                                  'and, '
                                                                  'where '
                                                                  'applicable, '
                                                                  'complete '
                                                                  'the '
                                                                  'example '
                                                                  'treatment. '
                                                                  'The '
                                                                  'corrected '
                                                                  'wording '
                                                                  'itself '
                                                                  'is not '
                                                                  'product-approved.',
                                                          'reviewedAt': '2026-08-18',
                                                          'reviewerRef': 'product-owner-001'},
                                                         {'actorRef': 'priority7-editorial-review',
                                                          'decision': 'changes-requested',
                                                          'kind': 'editorial-review',
                                                          'note': 'H2 '
                                                                  'content '
                                                                  'change: '
                                                                  'English '
                                                                  'glosses '
                                                                  'added '
                                                                  'to this '
                                                                  "pattern's "
                                                                  'Polish '
                                                                  'illustrations '
                                                                  'in the '
                                                                  'learner-facing '
                                                                  'English '
                                                                  'prose. '
                                                                  'Tier-2 '
                                                                  'scope '
                                                                  'moved, '
                                                                  'so the '
                                                                  'standing '
                                                                  'editorial '
                                                                  'acceptance '
                                                                  'is '
                                                                  'withdrawn.',
                                                          'reviewedAt': '2026-08-18'},
                                                         {'actorRef': 'priority7-editorial-review',
                                                          'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                          'decision': 'accept',
                                                          'kind': 'editorial-review',
                                                          'note': 'H2 '
                                                                  're-review: '
                                                                  'an '
                                                                  'authoring '
                                                                  'pass '
                                                                  'drafted '
                                                                  'the '
                                                                  'glosses '
                                                                  'and '
                                                                  'examples '
                                                                  'and a '
                                                                  'separate '
                                                                  'final '
                                                                  'editorial '
                                                                  'pass '
                                                                  'audited '
                                                                  'translation '
                                                                  'accuracy, '
                                                                  'Polish '
                                                                  'grammaticality, '
                                                                  'pattern '
                                                                  'fit, '
                                                                  'register '
                                                                  'and '
                                                                  'CEFR. '
                                                                  'Accepted '
                                                                  'against '
                                                                  'the '
                                                                  'current '
                                                                  'tier-2 '
                                                                  'scope.',
                                                          'reviewedAt': '2026-08-18',
                                                          'scopeDigest': 'sha256:4d46083fbdaae42e0ac2fec30e3365395a2498403717118028cac94b16b5e67f',
                                                          'scopeVersion': 1}],
 'vp-p-sluchac-obey-genitive-object-674adae2dec3': [{'decision': 'accept',
                                                     'kind': 'correction',
                                                     'note': 'Owner-authorized '
                                                             'correction, '
                                                             '2026-08-18: '
                                                             'add English '
                                                             'glosses to '
                                                             'the Polish '
                                                             'illustrations '
                                                             'in the '
                                                             'learner-facing '
                                                             'English '
                                                             'prose and, '
                                                             'where '
                                                             'applicable, '
                                                             'complete the '
                                                             'example '
                                                             'treatment. '
                                                             'The '
                                                             'corrected '
                                                             'wording '
                                                             'itself is '
                                                             'not '
                                                             'product-approved.',
                                                     'reviewedAt': '2026-08-18',
                                                     'reviewerRef': 'product-owner-001'},
                                                    {'actorRef': 'priority7-editorial-review',
                                                     'decision': 'changes-requested',
                                                     'kind': 'editorial-review',
                                                     'note': 'H2 content '
                                                             'change: '
                                                             'English '
                                                             'glosses '
                                                             'added to the '
                                                             'Polish '
                                                             'illustrations '
                                                             'and a first '
                                                             'example '
                                                             'added to '
                                                             'this '
                                                             'pattern. '
                                                             'Tier-2 scope '
                                                             'moved, so '
                                                             'the standing '
                                                             'editorial '
                                                             'acceptance '
                                                             'is '
                                                             'withdrawn.',
                                                     'reviewedAt': '2026-08-18'},
                                                    {'actorRef': 'priority7-editorial-review',
                                                     'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                     'decision': 'accept',
                                                     'kind': 'editorial-review',
                                                     'note': 'H2 '
                                                             're-review: '
                                                             'an authoring '
                                                             'pass drafted '
                                                             'the glosses '
                                                             'and examples '
                                                             'and a '
                                                             'separate '
                                                             'final '
                                                             'editorial '
                                                             'pass audited '
                                                             'translation '
                                                             'accuracy, '
                                                             'Polish '
                                                             'grammaticality, '
                                                             'pattern fit, '
                                                             'register and '
                                                             'CEFR. '
                                                             'Accepted '
                                                             'against the '
                                                             'current '
                                                             'tier-2 '
                                                             'scope.',
                                                     'reviewedAt': '2026-08-18',
                                                     'scopeDigest': 'sha256:9c42624dcb17a21ea9d695630280f5c0bf9c6ab7b8b3510d400da411de0b5a12',
                                                     'scopeVersion': 1}],
 'vp-p-szukac-seek-genitive-target-71dc6eff512c': [{'decision': 'accept',
                                                    'kind': 'correction',
                                                    'note': 'Owner-authorized '
                                                            'correction, '
                                                            '2026-08-18: '
                                                            'add English '
                                                            'glosses to '
                                                            'the Polish '
                                                            'illustrations '
                                                            'in the '
                                                            'learner-facing '
                                                            'English prose '
                                                            'and, where '
                                                            'applicable, '
                                                            'complete the '
                                                            'example '
                                                            'treatment. '
                                                            'The corrected '
                                                            'wording '
                                                            'itself is not '
                                                            'product-approved.',
                                                    'reviewedAt': '2026-08-18',
                                                    'reviewerRef': 'product-owner-001'},
                                                   {'actorRef': 'priority7-editorial-review',
                                                    'decision': 'changes-requested',
                                                    'kind': 'editorial-review',
                                                    'note': 'H2 content '
                                                            'change: '
                                                            'English '
                                                            'glosses added '
                                                            'to this '
                                                            "pattern's "
                                                            'Polish '
                                                            'illustrations '
                                                            'in the '
                                                            'learner-facing '
                                                            'English '
                                                            'prose. Tier-2 '
                                                            'scope moved, '
                                                            'so the '
                                                            'standing '
                                                            'editorial '
                                                            'acceptance is '
                                                            'withdrawn.',
                                                    'reviewedAt': '2026-08-18'},
                                                   {'actorRef': 'priority7-editorial-review',
                                                    'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                    'decision': 'accept',
                                                    'kind': 'editorial-review',
                                                    'note': 'H2 re-review: '
                                                            'an authoring '
                                                            'pass drafted '
                                                            'the glosses '
                                                            'and examples '
                                                            'and a '
                                                            'separate '
                                                            'final '
                                                            'editorial '
                                                            'pass audited '
                                                            'translation '
                                                            'accuracy, '
                                                            'Polish '
                                                            'grammaticality, '
                                                            'pattern fit, '
                                                            'register and '
                                                            'CEFR. '
                                                            'Accepted '
                                                            'against the '
                                                            'current '
                                                            'tier-2 scope.',
                                                    'reviewedAt': '2026-08-18',
                                                    'scopeDigest': 'sha256:e098b809e5db5950e180e5326e84463bd15f021226ac70a41f7b98c7812374c1',
                                                    'scopeVersion': 1}],
 'vp-p-tesknic-miss-za-instrumental-target-f866502502c7': [{'decision': 'accept',
                                                            'kind': 'correction',
                                                            'note': 'Owner-authorized '
                                                                    'correction, '
                                                                    '2026-08-18: '
                                                                    'add '
                                                                    'English '
                                                                    'glosses '
                                                                    'to '
                                                                    'the '
                                                                    'Polish '
                                                                    'illustrations '
                                                                    'in '
                                                                    'the '
                                                                    'learner-facing '
                                                                    'English '
                                                                    'prose '
                                                                    'and, '
                                                                    'where '
                                                                    'applicable, '
                                                                    'complete '
                                                                    'the '
                                                                    'example '
                                                                    'treatment. '
                                                                    'The '
                                                                    'corrected '
                                                                    'wording '
                                                                    'itself '
                                                                    'is '
                                                                    'not '
                                                                    'product-approved.',
                                                            'reviewedAt': '2026-08-18',
                                                            'reviewerRef': 'product-owner-001'},
                                                           {'actorRef': 'priority7-editorial-review',
                                                            'decision': 'changes-requested',
                                                            'kind': 'editorial-review',
                                                            'note': 'H2 '
                                                                    'content '
                                                                    'change: '
                                                                    'English '
                                                                    'glosses '
                                                                    'added '
                                                                    'to '
                                                                    'this '
                                                                    "pattern's "
                                                                    'Polish '
                                                                    'illustrations '
                                                                    'in '
                                                                    'the '
                                                                    'learner-facing '
                                                                    'English '
                                                                    'prose. '
                                                                    'Tier-2 '
                                                                    'scope '
                                                                    'moved, '
                                                                    'so '
                                                                    'the '
                                                                    'standing '
                                                                    'editorial '
                                                                    'acceptance '
                                                                    'is '
                                                                    'withdrawn.',
                                                            'reviewedAt': '2026-08-18'},
                                                           {'actorRef': 'priority7-editorial-review',
                                                            'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                            'decision': 'accept',
                                                            'kind': 'editorial-review',
                                                            'note': 'H2 '
                                                                    're-review: '
                                                                    'an '
                                                                    'authoring '
                                                                    'pass '
                                                                    'drafted '
                                                                    'the '
                                                                    'glosses '
                                                                    'and '
                                                                    'examples '
                                                                    'and a '
                                                                    'separate '
                                                                    'final '
                                                                    'editorial '
                                                                    'pass '
                                                                    'audited '
                                                                    'translation '
                                                                    'accuracy, '
                                                                    'Polish '
                                                                    'grammaticality, '
                                                                    'pattern '
                                                                    'fit, '
                                                                    'register '
                                                                    'and '
                                                                    'CEFR. '
                                                                    'Accepted '
                                                                    'against '
                                                                    'the '
                                                                    'current '
                                                                    'tier-2 '
                                                                    'scope.',
                                                            'reviewedAt': '2026-08-18',
                                                            'scopeDigest': 'sha256:b1b9fd0ccbb697ff394736d4f45cd34d205f071030cf146b8db5a7f37e4ab183',
                                                            'scopeVersion': 1}],
 'vp-p-uczyc-sie-study-genitive-subject-matter-44c5fdb95dd7': [{'decision': 'accept',
                                                                'kind': 'correction',
                                                                'note': 'Owner-authorized '
                                                                        'correction, '
                                                                        '2026-08-18: '
                                                                        'add '
                                                                        'English '
                                                                        'glosses '
                                                                        'to '
                                                                        'the '
                                                                        'Polish '
                                                                        'illustrations '
                                                                        'in '
                                                                        'the '
                                                                        'learner-facing '
                                                                        'English '
                                                                        'prose '
                                                                        'and, '
                                                                        'where '
                                                                        'applicable, '
                                                                        'complete '
                                                                        'the '
                                                                        'example '
                                                                        'treatment. '
                                                                        'The '
                                                                        'corrected '
                                                                        'wording '
                                                                        'itself '
                                                                        'is '
                                                                        'not '
                                                                        'product-approved.',
                                                                'reviewedAt': '2026-08-18',
                                                                'reviewerRef': 'product-owner-001'},
                                                               {'actorRef': 'priority7-editorial-review',
                                                                'decision': 'changes-requested',
                                                                'kind': 'editorial-review',
                                                                'note': 'H2 '
                                                                        'content '
                                                                        'change: '
                                                                        'English '
                                                                        'glosses '
                                                                        'added '
                                                                        'to '
                                                                        'this '
                                                                        "pattern's "
                                                                        'Polish '
                                                                        'illustrations '
                                                                        'in '
                                                                        'the '
                                                                        'learner-facing '
                                                                        'English '
                                                                        'prose. '
                                                                        'Tier-2 '
                                                                        'scope '
                                                                        'moved, '
                                                                        'so '
                                                                        'the '
                                                                        'standing '
                                                                        'editorial '
                                                                        'acceptance '
                                                                        'is '
                                                                        'withdrawn.',
                                                                'reviewedAt': '2026-08-18'},
                                                               {'actorRef': 'priority7-editorial-review',
                                                                'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                                'decision': 'accept',
                                                                'kind': 'editorial-review',
                                                                'note': 'H2 '
                                                                        're-review: '
                                                                        'an '
                                                                        'authoring '
                                                                        'pass '
                                                                        'drafted '
                                                                        'the '
                                                                        'glosses '
                                                                        'and '
                                                                        'examples '
                                                                        'and '
                                                                        'a '
                                                                        'separate '
                                                                        'final '
                                                                        'editorial '
                                                                        'pass '
                                                                        'audited '
                                                                        'translation '
                                                                        'accuracy, '
                                                                        'Polish '
                                                                        'grammaticality, '
                                                                        'pattern '
                                                                        'fit, '
                                                                        'register '
                                                                        'and '
                                                                        'CEFR. '
                                                                        'Accepted '
                                                                        'against '
                                                                        'the '
                                                                        'current '
                                                                        'tier-2 '
                                                                        'scope.',
                                                                'reviewedAt': '2026-08-18',
                                                                'scopeDigest': 'sha256:2c2ad1425db885624d0318661c03abf43a7e5fc05e2df7c3205e429f2a5064b0',
                                                                'scopeVersion': 1}],
 'vp-p-uczyc-sie-study-infinitive-skill-ab708776387e': [{'decision': 'accept',
                                                         'kind': 'correction',
                                                         'note': 'Owner-authorized '
                                                                 'correction, '
                                                                 '2026-08-18: '
                                                                 'add '
                                                                 'English '
                                                                 'glosses '
                                                                 'to the '
                                                                 'Polish '
                                                                 'illustrations '
                                                                 'in the '
                                                                 'learner-facing '
                                                                 'English '
                                                                 'prose '
                                                                 'and, '
                                                                 'where '
                                                                 'applicable, '
                                                                 'complete '
                                                                 'the '
                                                                 'example '
                                                                 'treatment. '
                                                                 'The '
                                                                 'corrected '
                                                                 'wording '
                                                                 'itself '
                                                                 'is not '
                                                                 'product-approved.',
                                                         'reviewedAt': '2026-08-18',
                                                         'reviewerRef': 'product-owner-001'},
                                                        {'actorRef': 'priority7-editorial-review',
                                                         'decision': 'changes-requested',
                                                         'kind': 'editorial-review',
                                                         'note': 'H2 '
                                                                 'content '
                                                                 'change: '
                                                                 'English '
                                                                 'glosses '
                                                                 'added to '
                                                                 'this '
                                                                 "pattern's "
                                                                 'Polish '
                                                                 'illustrations '
                                                                 'in the '
                                                                 'learner-facing '
                                                                 'English '
                                                                 'prose. '
                                                                 'Tier-2 '
                                                                 'scope '
                                                                 'moved, '
                                                                 'so the '
                                                                 'standing '
                                                                 'editorial '
                                                                 'acceptance '
                                                                 'is '
                                                                 'withdrawn.',
                                                         'reviewedAt': '2026-08-18'},
                                                        {'actorRef': 'priority7-editorial-review',
                                                         'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                         'decision': 'accept',
                                                         'kind': 'editorial-review',
                                                         'note': 'H2 '
                                                                 're-review: '
                                                                 'an '
                                                                 'authoring '
                                                                 'pass '
                                                                 'drafted '
                                                                 'the '
                                                                 'glosses '
                                                                 'and '
                                                                 'examples '
                                                                 'and a '
                                                                 'separate '
                                                                 'final '
                                                                 'editorial '
                                                                 'pass '
                                                                 'audited '
                                                                 'translation '
                                                                 'accuracy, '
                                                                 'Polish '
                                                                 'grammaticality, '
                                                                 'pattern '
                                                                 'fit, '
                                                                 'register '
                                                                 'and '
                                                                 'CEFR. '
                                                                 'Accepted '
                                                                 'against '
                                                                 'the '
                                                                 'current '
                                                                 'tier-2 '
                                                                 'scope.',
                                                         'reviewedAt': '2026-08-18',
                                                         'scopeDigest': 'sha256:7ddf2f5df501438ac4ccbe675a083227e6a725df534c438d643c9a74942e11ae',
                                                         'scopeVersion': 1}],
 'vp-p-ufac-trust-dative-object-10988adac8cd': [{'decision': 'accept',
                                                 'kind': 'correction',
                                                 'note': 'Owner-authorized '
                                                         'correction, '
                                                         '2026-08-18: add '
                                                         'English glosses '
                                                         'to the Polish '
                                                         'illustrations in '
                                                         'the '
                                                         'learner-facing '
                                                         'English prose '
                                                         'and, where '
                                                         'applicable, '
                                                         'complete the '
                                                         'example '
                                                         'treatment. The '
                                                         'corrected '
                                                         'wording itself '
                                                         'is not '
                                                         'product-approved.',
                                                 'reviewedAt': '2026-08-18',
                                                 'reviewerRef': 'product-owner-001'},
                                                {'actorRef': 'priority7-editorial-review',
                                                 'decision': 'changes-requested',
                                                 'kind': 'editorial-review',
                                                 'note': 'H2 content '
                                                         'change: English '
                                                         'glosses added to '
                                                         'the Polish '
                                                         'illustrations '
                                                         'and a first '
                                                         'example added to '
                                                         'this pattern. '
                                                         'Tier-2 scope '
                                                         'moved, so the '
                                                         'standing '
                                                         'editorial '
                                                         'acceptance is '
                                                         'withdrawn.',
                                                 'reviewedAt': '2026-08-18'},
                                                {'actorRef': 'priority7-editorial-review',
                                                 'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                 'decision': 'accept',
                                                 'kind': 'editorial-review',
                                                 'note': 'H2 re-review: an '
                                                         'authoring pass '
                                                         'drafted the '
                                                         'glosses and '
                                                         'examples and a '
                                                         'separate final '
                                                         'editorial pass '
                                                         'audited '
                                                         'translation '
                                                         'accuracy, Polish '
                                                         'grammaticality, '
                                                         'pattern fit, '
                                                         'register and '
                                                         'CEFR. Accepted '
                                                         'against the '
                                                         'current tier-2 '
                                                         'scope.',
                                                 'reviewedAt': '2026-08-18',
                                                 'scopeDigest': 'sha256:d649069182480b873b061394e5c4115f01cb8a94dbc2eb18cca73ea3c659e85a',
                                                 'scopeVersion': 1}],
 'vp-p-uzywac-use-genitive-object-2c5cb44fe85d': [{'decision': 'accept',
                                                   'kind': 'correction',
                                                   'note': 'Owner-authorized '
                                                           'correction, '
                                                           '2026-08-18: '
                                                           'add English '
                                                           'glosses to the '
                                                           'Polish '
                                                           'illustrations '
                                                           'in the '
                                                           'learner-facing '
                                                           'English prose '
                                                           'and, where '
                                                           'applicable, '
                                                           'complete the '
                                                           'example '
                                                           'treatment. The '
                                                           'corrected '
                                                           'wording itself '
                                                           'is not '
                                                           'product-approved.',
                                                   'reviewedAt': '2026-08-18',
                                                   'reviewerRef': 'product-owner-001'},
                                                  {'actorRef': 'priority7-editorial-review',
                                                   'decision': 'changes-requested',
                                                   'kind': 'editorial-review',
                                                   'note': 'H2 content '
                                                           'change: '
                                                           'English '
                                                           'glosses added '
                                                           'to this '
                                                           "pattern's "
                                                           'Polish '
                                                           'illustrations '
                                                           'in the '
                                                           'learner-facing '
                                                           'English prose. '
                                                           'Tier-2 scope '
                                                           'moved, so the '
                                                           'standing '
                                                           'editorial '
                                                           'acceptance is '
                                                           'withdrawn.',
                                                   'reviewedAt': '2026-08-18'},
                                                  {'actorRef': 'priority7-editorial-review',
                                                   'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                   'decision': 'accept',
                                                   'kind': 'editorial-review',
                                                   'note': 'H2 re-review: '
                                                           'an authoring '
                                                           'pass drafted '
                                                           'the glosses '
                                                           'and examples '
                                                           'and a separate '
                                                           'final '
                                                           'editorial pass '
                                                           'audited '
                                                           'translation '
                                                           'accuracy, '
                                                           'Polish '
                                                           'grammaticality, '
                                                           'pattern fit, '
                                                           'register and '
                                                           'CEFR. Accepted '
                                                           'against the '
                                                           'current tier-2 '
                                                           'scope.',
                                                   'reviewedAt': '2026-08-18',
                                                   'scopeDigest': 'sha256:2ad2d3e9ada297a28983a6ecbfb7a034f0b2abd11c05099a6dce115ee8ff74f1',
                                                   'scopeVersion': 1}],
 'vp-p-widziec-perceive-visually-accusative-object-80b697e51432': [{'decision': 'accept',
                                                                    'kind': 'correction',
                                                                    'note': 'Owner-authorized '
                                                                            'correction, '
                                                                            '2026-08-18: '
                                                                            'add '
                                                                            'English '
                                                                            'glosses '
                                                                            'to '
                                                                            'the '
                                                                            'Polish '
                                                                            'illustrations '
                                                                            'in '
                                                                            'the '
                                                                            'learner-facing '
                                                                            'English '
                                                                            'prose '
                                                                            'and, '
                                                                            'where '
                                                                            'applicable, '
                                                                            'complete '
                                                                            'the '
                                                                            'example '
                                                                            'treatment. '
                                                                            'The '
                                                                            'corrected '
                                                                            'wording '
                                                                            'itself '
                                                                            'is '
                                                                            'not '
                                                                            'product-approved.',
                                                                    'reviewedAt': '2026-08-18',
                                                                    'reviewerRef': 'product-owner-001'},
                                                                   {'actorRef': 'priority7-editorial-review',
                                                                    'decision': 'changes-requested',
                                                                    'kind': 'editorial-review',
                                                                    'note': 'H2 '
                                                                            'content '
                                                                            'change: '
                                                                            'English '
                                                                            'glosses '
                                                                            'added '
                                                                            'to '
                                                                            'this '
                                                                            "pattern's "
                                                                            'Polish '
                                                                            'illustrations '
                                                                            'in '
                                                                            'the '
                                                                            'learner-facing '
                                                                            'English '
                                                                            'prose. '
                                                                            'Tier-2 '
                                                                            'scope '
                                                                            'moved, '
                                                                            'so '
                                                                            'the '
                                                                            'standing '
                                                                            'editorial '
                                                                            'acceptance '
                                                                            'is '
                                                                            'withdrawn.',
                                                                    'reviewedAt': '2026-08-18'},
                                                                   {'actorRef': 'priority7-editorial-review',
                                                                    'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                                    'decision': 'accept',
                                                                    'kind': 'editorial-review',
                                                                    'note': 'H2 '
                                                                            're-review: '
                                                                            'an '
                                                                            'authoring '
                                                                            'pass '
                                                                            'drafted '
                                                                            'the '
                                                                            'glosses '
                                                                            'and '
                                                                            'examples '
                                                                            'and '
                                                                            'a '
                                                                            'separate '
                                                                            'final '
                                                                            'editorial '
                                                                            'pass '
                                                                            'audited '
                                                                            'translation '
                                                                            'accuracy, '
                                                                            'Polish '
                                                                            'grammaticality, '
                                                                            'pattern '
                                                                            'fit, '
                                                                            'register '
                                                                            'and '
                                                                            'CEFR. '
                                                                            'Accepted '
                                                                            'against '
                                                                            'the '
                                                                            'current '
                                                                            'tier-2 '
                                                                            'scope.',
                                                                    'reviewedAt': '2026-08-18',
                                                                    'scopeDigest': 'sha256:15c470cbc5bde23d7b8fe0b362ab694ea98e0c11baeee3276981d34ac03a88fe',
                                                                    'scopeVersion': 1}],
 'vp-p-wierzyc-have-trust-dative-object-f38bb3e72123': [{'decision': 'accept',
                                                         'kind': 'correction',
                                                         'note': 'Owner-authorized '
                                                                 'correction, '
                                                                 '2026-08-18: '
                                                                 'add '
                                                                 'English '
                                                                 'glosses '
                                                                 'to the '
                                                                 'Polish '
                                                                 'illustrations '
                                                                 'in the '
                                                                 'learner-facing '
                                                                 'English '
                                                                 'prose '
                                                                 'and, '
                                                                 'where '
                                                                 'applicable, '
                                                                 'complete '
                                                                 'the '
                                                                 'example '
                                                                 'treatment. '
                                                                 'The '
                                                                 'corrected '
                                                                 'wording '
                                                                 'itself '
                                                                 'is not '
                                                                 'product-approved.',
                                                         'reviewedAt': '2026-08-18',
                                                         'reviewerRef': 'product-owner-001'},
                                                        {'actorRef': 'priority7-editorial-review',
                                                         'decision': 'changes-requested',
                                                         'kind': 'editorial-review',
                                                         'note': 'H2 '
                                                                 'content '
                                                                 'change: '
                                                                 'English '
                                                                 'glosses '
                                                                 'added to '
                                                                 'the '
                                                                 'Polish '
                                                                 'illustrations '
                                                                 'and a '
                                                                 'first '
                                                                 'example '
                                                                 'added to '
                                                                 'this '
                                                                 'pattern. '
                                                                 'Tier-2 '
                                                                 'scope '
                                                                 'moved, '
                                                                 'so the '
                                                                 'standing '
                                                                 'editorial '
                                                                 'acceptance '
                                                                 'is '
                                                                 'withdrawn.',
                                                         'reviewedAt': '2026-08-18'},
                                                        {'actorRef': 'priority7-editorial-review',
                                                         'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                         'decision': 'accept',
                                                         'kind': 'editorial-review',
                                                         'note': 'H2 '
                                                                 're-review: '
                                                                 'an '
                                                                 'authoring '
                                                                 'pass '
                                                                 'drafted '
                                                                 'the '
                                                                 'glosses '
                                                                 'and '
                                                                 'examples '
                                                                 'and a '
                                                                 'separate '
                                                                 'final '
                                                                 'editorial '
                                                                 'pass '
                                                                 'audited '
                                                                 'translation '
                                                                 'accuracy, '
                                                                 'Polish '
                                                                 'grammaticality, '
                                                                 'pattern '
                                                                 'fit, '
                                                                 'register '
                                                                 'and '
                                                                 'CEFR. '
                                                                 'Accepted '
                                                                 'against '
                                                                 'the '
                                                                 'current '
                                                                 'tier-2 '
                                                                 'scope.',
                                                         'reviewedAt': '2026-08-18',
                                                         'scopeDigest': 'sha256:ee375bda6a234abf52bb5381b2c531a4f7fc0968410d0f21afd195d413f748a1',
                                                         'scopeVersion': 1}],
 'vp-p-wierzyc-have-trust-w-accusative-target-6561408ea8d1': [{'decision': 'accept',
                                                               'kind': 'correction',
                                                               'note': 'Owner-authorized '
                                                                       'correction, '
                                                                       '2026-08-18: '
                                                                       'add '
                                                                       'English '
                                                                       'glosses '
                                                                       'to '
                                                                       'the '
                                                                       'Polish '
                                                                       'illustrations '
                                                                       'in '
                                                                       'the '
                                                                       'learner-facing '
                                                                       'English '
                                                                       'prose '
                                                                       'and, '
                                                                       'where '
                                                                       'applicable, '
                                                                       'complete '
                                                                       'the '
                                                                       'example '
                                                                       'treatment. '
                                                                       'The '
                                                                       'corrected '
                                                                       'wording '
                                                                       'itself '
                                                                       'is '
                                                                       'not '
                                                                       'product-approved.',
                                                               'reviewedAt': '2026-08-18',
                                                               'reviewerRef': 'product-owner-001'},
                                                              {'actorRef': 'priority7-editorial-review',
                                                               'decision': 'changes-requested',
                                                               'kind': 'editorial-review',
                                                               'note': 'H2 '
                                                                       'content '
                                                                       'change: '
                                                                       'English '
                                                                       'glosses '
                                                                       'added '
                                                                       'to '
                                                                       'the '
                                                                       'Polish '
                                                                       'illustrations '
                                                                       'and '
                                                                       'a '
                                                                       'first '
                                                                       'example '
                                                                       'added '
                                                                       'to '
                                                                       'this '
                                                                       'pattern. '
                                                                       'Tier-2 '
                                                                       'scope '
                                                                       'moved, '
                                                                       'so '
                                                                       'the '
                                                                       'standing '
                                                                       'editorial '
                                                                       'acceptance '
                                                                       'is '
                                                                       'withdrawn.',
                                                               'reviewedAt': '2026-08-18'},
                                                              {'actorRef': 'priority7-editorial-review',
                                                               'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                               'decision': 'accept',
                                                               'kind': 'editorial-review',
                                                               'note': 'H2 '
                                                                       're-review: '
                                                                       'an '
                                                                       'authoring '
                                                                       'pass '
                                                                       'drafted '
                                                                       'the '
                                                                       'glosses '
                                                                       'and '
                                                                       'examples '
                                                                       'and '
                                                                       'a '
                                                                       'separate '
                                                                       'final '
                                                                       'editorial '
                                                                       'pass '
                                                                       'audited '
                                                                       'translation '
                                                                       'accuracy, '
                                                                       'Polish '
                                                                       'grammaticality, '
                                                                       'pattern '
                                                                       'fit, '
                                                                       'register '
                                                                       'and '
                                                                       'CEFR. '
                                                                       'Accepted '
                                                                       'against '
                                                                       'the '
                                                                       'current '
                                                                       'tier-2 '
                                                                       'scope.',
                                                               'reviewedAt': '2026-08-18',
                                                               'scopeDigest': 'sha256:029aca3a712f99e50fa7893f892450de4ac67bf320fd61f7564d5ceea61b0852',
                                                               'scopeVersion': 1}],
 'vp-p-zajmowac-sie-occupation-activity-instrumental-topic-3321df3f989e': [{'decision': 'accept',
                                                                            'kind': 'correction',
                                                                            'note': 'Owner-authorized '
                                                                                    'correction, '
                                                                                    '2026-08-18: '
                                                                                    'add '
                                                                                    'English '
                                                                                    'glosses '
                                                                                    'to '
                                                                                    'the '
                                                                                    'Polish '
                                                                                    'illustrations '
                                                                                    'in '
                                                                                    'the '
                                                                                    'learner-facing '
                                                                                    'English '
                                                                                    'prose '
                                                                                    'and, '
                                                                                    'where '
                                                                                    'applicable, '
                                                                                    'complete '
                                                                                    'the '
                                                                                    'example '
                                                                                    'treatment. '
                                                                                    'The '
                                                                                    'corrected '
                                                                                    'wording '
                                                                                    'itself '
                                                                                    'is '
                                                                                    'not '
                                                                                    'product-approved.',
                                                                            'reviewedAt': '2026-08-18',
                                                                            'reviewerRef': 'product-owner-001'},
                                                                           {'actorRef': 'priority7-editorial-review',
                                                                            'decision': 'changes-requested',
                                                                            'kind': 'editorial-review',
                                                                            'note': 'H2 '
                                                                                    'content '
                                                                                    'change: '
                                                                                    'English '
                                                                                    'glosses '
                                                                                    'added '
                                                                                    'to '
                                                                                    'the '
                                                                                    'Polish '
                                                                                    'illustrations '
                                                                                    'and '
                                                                                    'a '
                                                                                    'first '
                                                                                    'example '
                                                                                    'added '
                                                                                    'to '
                                                                                    'this '
                                                                                    'pattern. '
                                                                                    'Tier-2 '
                                                                                    'scope '
                                                                                    'moved, '
                                                                                    'so '
                                                                                    'the '
                                                                                    'standing '
                                                                                    'editorial '
                                                                                    'acceptance '
                                                                                    'is '
                                                                                    'withdrawn.',
                                                                            'reviewedAt': '2026-08-18'},
                                                                           {'actorRef': 'priority7-editorial-review',
                                                                            'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                                            'decision': 'accept',
                                                                            'kind': 'editorial-review',
                                                                            'note': 'H2 '
                                                                                    're-review: '
                                                                                    'an '
                                                                                    'authoring '
                                                                                    'pass '
                                                                                    'drafted '
                                                                                    'the '
                                                                                    'glosses '
                                                                                    'and '
                                                                                    'examples '
                                                                                    'and '
                                                                                    'a '
                                                                                    'separate '
                                                                                    'final '
                                                                                    'editorial '
                                                                                    'pass '
                                                                                    'audited '
                                                                                    'translation '
                                                                                    'accuracy, '
                                                                                    'Polish '
                                                                                    'grammaticality, '
                                                                                    'pattern '
                                                                                    'fit, '
                                                                                    'register '
                                                                                    'and '
                                                                                    'CEFR. '
                                                                                    'Accepted '
                                                                                    'against '
                                                                                    'the '
                                                                                    'current '
                                                                                    'tier-2 '
                                                                                    'scope.',
                                                                            'reviewedAt': '2026-08-18',
                                                                            'scopeDigest': 'sha256:71c19ed127affd69c72ba2ebd1912e6f5271ad24a2c5408e2eb9647eb2f4dbea',
                                                                            'scopeVersion': 1}],
 'vp-p-zalezec-depend-on-od-genitive-source-1ad29f7a1318': [{'decision': 'accept',
                                                             'kind': 'correction',
                                                             'note': 'Owner-authorized '
                                                                     'correction, '
                                                                     '2026-08-18: '
                                                                     'add '
                                                                     'English '
                                                                     'glosses '
                                                                     'to '
                                                                     'the '
                                                                     'Polish '
                                                                     'illustrations '
                                                                     'in '
                                                                     'the '
                                                                     'learner-facing '
                                                                     'English '
                                                                     'prose '
                                                                     'and, '
                                                                     'where '
                                                                     'applicable, '
                                                                     'complete '
                                                                     'the '
                                                                     'example '
                                                                     'treatment. '
                                                                     'The '
                                                                     'corrected '
                                                                     'wording '
                                                                     'itself '
                                                                     'is '
                                                                     'not '
                                                                     'product-approved.',
                                                             'reviewedAt': '2026-08-18',
                                                             'reviewerRef': 'product-owner-001'},
                                                            {'actorRef': 'priority7-editorial-review',
                                                             'decision': 'changes-requested',
                                                             'kind': 'editorial-review',
                                                             'note': 'H2 '
                                                                     'content '
                                                                     'change: '
                                                                     'English '
                                                                     'glosses '
                                                                     'added '
                                                                     'to '
                                                                     'this '
                                                                     "pattern's "
                                                                     'Polish '
                                                                     'illustrations '
                                                                     'in '
                                                                     'the '
                                                                     'learner-facing '
                                                                     'English '
                                                                     'prose. '
                                                                     'Tier-2 '
                                                                     'scope '
                                                                     'moved, '
                                                                     'so '
                                                                     'the '
                                                                     'standing '
                                                                     'editorial '
                                                                     'acceptance '
                                                                     'is '
                                                                     'withdrawn.',
                                                             'reviewedAt': '2026-08-18'},
                                                            {'actorRef': 'priority7-editorial-review',
                                                             'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                             'decision': 'accept',
                                                             'kind': 'editorial-review',
                                                             'note': 'H2 '
                                                                     're-review: '
                                                                     'an '
                                                                     'authoring '
                                                                     'pass '
                                                                     'drafted '
                                                                     'the '
                                                                     'glosses '
                                                                     'and '
                                                                     'examples '
                                                                     'and '
                                                                     'a '
                                                                     'separate '
                                                                     'final '
                                                                     'editorial '
                                                                     'pass '
                                                                     'audited '
                                                                     'translation '
                                                                     'accuracy, '
                                                                     'Polish '
                                                                     'grammaticality, '
                                                                     'pattern '
                                                                     'fit, '
                                                                     'register '
                                                                     'and '
                                                                     'CEFR. '
                                                                     'Accepted '
                                                                     'against '
                                                                     'the '
                                                                     'current '
                                                                     'tier-2 '
                                                                     'scope.',
                                                             'reviewedAt': '2026-08-18',
                                                             'scopeDigest': 'sha256:a0b63faff7f90b9c9d22f1e6afd63cc3bac1810fbfac8bc5e3334cdf8783fa73',
                                                             'scopeVersion': 1}],
 'vp-p-zalezec-matter-to-someone-dative-experiencer-na-locative-1fc4131471cc': [{'actorRef': 'priority7-editorial-review',
                                                                                 'decision': 'changes-requested',
                                                                                 'kind': 'editorial-review',
                                                                                 'note': 'H2 '
                                                                                         'content '
                                                                                         'change: '
                                                                                         'a '
                                                                                         'first '
                                                                                         'example '
                                                                                         'added '
                                                                                         'to '
                                                                                         'this '
                                                                                         'pattern; '
                                                                                         'its '
                                                                                         'English '
                                                                                         'prose '
                                                                                         'carried '
                                                                                         'no '
                                                                                         'Polish '
                                                                                         'illustration '
                                                                                         'to '
                                                                                         'gloss. '
                                                                                         'Tier-2 '
                                                                                         'scope '
                                                                                         'moved, '
                                                                                         'so '
                                                                                         'the '
                                                                                         'standing '
                                                                                         'editorial '
                                                                                         'acceptance '
                                                                                         'is '
                                                                                         'withdrawn.',
                                                                                 'reviewedAt': '2026-08-18'},
                                                                                {'actorRef': 'priority7-editorial-review',
                                                                                 'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                                                 'decision': 'accept',
                                                                                 'kind': 'editorial-review',
                                                                                 'note': 'H2 '
                                                                                         're-review: '
                                                                                         'an '
                                                                                         'authoring '
                                                                                         'pass '
                                                                                         'drafted '
                                                                                         'the '
                                                                                         'glosses '
                                                                                         'and '
                                                                                         'examples '
                                                                                         'and '
                                                                                         'a '
                                                                                         'separate '
                                                                                         'final '
                                                                                         'editorial '
                                                                                         'pass '
                                                                                         'audited '
                                                                                         'translation '
                                                                                         'accuracy, '
                                                                                         'Polish '
                                                                                         'grammaticality, '
                                                                                         'pattern '
                                                                                         'fit, '
                                                                                         'register '
                                                                                         'and '
                                                                                         'CEFR. '
                                                                                         'Accepted '
                                                                                         'against '
                                                                                         'the '
                                                                                         'current '
                                                                                         'tier-2 '
                                                                                         'scope.',
                                                                                 'reviewedAt': '2026-08-18',
                                                                                 'scopeDigest': 'sha256:f60351ce09671d3262e6cf28d75f00c167c0d506abfbb009e049dec40b065016',
                                                                                 'scopeVersion': 1}],
 'vp-p-znac-be-acquainted-with-accusative-object-379e19b36299': [{'decision': 'accept',
                                                                  'kind': 'correction',
                                                                  'note': 'Owner-authorized '
                                                                          'correction, '
                                                                          '2026-08-18: '
                                                                          'add '
                                                                          'English '
                                                                          'glosses '
                                                                          'to '
                                                                          'the '
                                                                          'Polish '
                                                                          'illustrations '
                                                                          'in '
                                                                          'the '
                                                                          'learner-facing '
                                                                          'English '
                                                                          'prose '
                                                                          'and, '
                                                                          'where '
                                                                          'applicable, '
                                                                          'complete '
                                                                          'the '
                                                                          'example '
                                                                          'treatment. '
                                                                          'The '
                                                                          'corrected '
                                                                          'wording '
                                                                          'itself '
                                                                          'is '
                                                                          'not '
                                                                          'product-approved.',
                                                                  'reviewedAt': '2026-08-18',
                                                                  'reviewerRef': 'product-owner-001'},
                                                                 {'actorRef': 'priority7-editorial-review',
                                                                  'decision': 'changes-requested',
                                                                  'kind': 'editorial-review',
                                                                  'note': 'H2 '
                                                                          'content '
                                                                          'change: '
                                                                          'English '
                                                                          'glosses '
                                                                          'added '
                                                                          'to '
                                                                          'this '
                                                                          "pattern's "
                                                                          'Polish '
                                                                          'illustrations '
                                                                          'in '
                                                                          'the '
                                                                          'learner-facing '
                                                                          'English '
                                                                          'prose. '
                                                                          'Tier-2 '
                                                                          'scope '
                                                                          'moved, '
                                                                          'so '
                                                                          'the '
                                                                          'standing '
                                                                          'editorial '
                                                                          'acceptance '
                                                                          'is '
                                                                          'withdrawn.',
                                                                  'reviewedAt': '2026-08-18'},
                                                                 {'actorRef': 'priority7-editorial-review',
                                                                  'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                                  'decision': 'accept',
                                                                  'kind': 'editorial-review',
                                                                  'note': 'H2 '
                                                                          're-review: '
                                                                          'an '
                                                                          'authoring '
                                                                          'pass '
                                                                          'drafted '
                                                                          'the '
                                                                          'glosses '
                                                                          'and '
                                                                          'examples '
                                                                          'and '
                                                                          'a '
                                                                          'separate '
                                                                          'final '
                                                                          'editorial '
                                                                          'pass '
                                                                          'audited '
                                                                          'translation '
                                                                          'accuracy, '
                                                                          'Polish '
                                                                          'grammaticality, '
                                                                          'pattern '
                                                                          'fit, '
                                                                          'register '
                                                                          'and '
                                                                          'CEFR. '
                                                                          'Accepted '
                                                                          'against '
                                                                          'the '
                                                                          'current '
                                                                          'tier-2 '
                                                                          'scope.',
                                                                  'reviewedAt': '2026-08-18',
                                                                  'scopeDigest': 'sha256:4ffab4e6dbff85dcf02f80ba3babd85606c851f69d390b4b5db9be1193f804ab',
                                                                  'scopeVersion': 1}],
 'vp-p-znalezc-find-accusative-object-d80c52211462': [{'decision': 'accept',
                                                       'kind': 'correction',
                                                       'note': 'Owner-authorized '
                                                               'correction, '
                                                               '2026-08-18: '
                                                               'add '
                                                               'English '
                                                               'glosses to '
                                                               'the Polish '
                                                               'illustrations '
                                                               'in the '
                                                               'learner-facing '
                                                               'English '
                                                               'prose and, '
                                                               'where '
                                                               'applicable, '
                                                               'complete '
                                                               'the '
                                                               'example '
                                                               'treatment. '
                                                               'The '
                                                               'corrected '
                                                               'wording '
                                                               'itself is '
                                                               'not '
                                                               'product-approved.',
                                                       'reviewedAt': '2026-08-18',
                                                       'reviewerRef': 'product-owner-001'},
                                                      {'actorRef': 'priority7-editorial-review',
                                                       'decision': 'changes-requested',
                                                       'kind': 'editorial-review',
                                                       'note': 'H2 content '
                                                               'change: '
                                                               'English '
                                                               'glosses '
                                                               'added to '
                                                               'this '
                                                               "pattern's "
                                                               'Polish '
                                                               'illustrations '
                                                               'in the '
                                                               'learner-facing '
                                                               'English '
                                                               'prose. '
                                                               'Tier-2 '
                                                               'scope '
                                                               'moved, so '
                                                               'the '
                                                               'standing '
                                                               'editorial '
                                                               'acceptance '
                                                               'is '
                                                               'withdrawn.',
                                                       'reviewedAt': '2026-08-18'},
                                                      {'actorRef': 'priority7-editorial-review',
                                                       'corroboratingActorRefs': ['priority7-editorial-corroboration'],
                                                       'decision': 'accept',
                                                       'kind': 'editorial-review',
                                                       'note': 'H2 '
                                                               're-review: '
                                                               'an '
                                                               'authoring '
                                                               'pass '
                                                               'drafted '
                                                               'the '
                                                               'glosses '
                                                               'and '
                                                               'examples '
                                                               'and a '
                                                               'separate '
                                                               'final '
                                                               'editorial '
                                                               'pass '
                                                               'audited '
                                                               'translation '
                                                               'accuracy, '
                                                               'Polish '
                                                               'grammaticality, '
                                                               'pattern '
                                                               'fit, '
                                                               'register '
                                                               'and CEFR. '
                                                               'Accepted '
                                                               'against '
                                                               'the '
                                                               'current '
                                                               'tier-2 '
                                                               'scope.',
                                                       'reviewedAt': '2026-08-18',
                                                       'scopeDigest': 'sha256:e72f96378738e396bba38f510a72f12649c68cd2b3e00b97cb4a18f08db94fb4',
                                                       'scopeVersion': 1}]}
)

#: The exact paragraph Phase 4F-H2 appended to ``contextNotice``.
H2_CONTEXT_NOTICE_SUFFIX = (
(' Phase 4F-H2 is a content-completion phase and it supersedes exactly '
 'two statements made above - that all 45 patterns are approved, and '
 'that no correction authority has been named - while leaving every '
 'other statement in this notice standing. On 2026-08-18 the product '
 'owner authorized a correction plan: every learner-facing English '
 'prose field that quotes a Polish illustration must give that '
 "illustration's English translation, and every pattern must carry "
 'exactly one example. Authorizing the plan is not approval of the '
 'resulting wording. H2 added English glosses to 55 Polish '
 'illustrations across 54 fields on 42 patterns, and added the 16 '
 'missing examples: 2 repository-reuse rows resolved through the '
 'repository index and byte-identical to their cited fields, and 14 '
 'editorial-generated rows naming priority7-example-generation as '
 'generatorRef. The corpus now holds 45 examples on 45 patterns, 20 '
 'repository-reuse and 25 editorial-generated. No existing example was '
 'altered, no human author was invented and authorRegistry stays '
 'EMPTY. The 42 patterns whose existing learner-facing prose changed '
 'each carry one correction event dated 2026-08-18, recorded under '
 "product-owner-001's existing product authority; no new correction, "
 'reopen or external-verification authority was registered and no new '
 'reviewer or nonhuman actor identity exists. Tier 1 is unchanged on '
 'all 45, so no reference-verification event was created, altered or '
 'invalidated and the 47 reference acceptances stand. Tier 2 and tier '
 '3 moved on exactly the 44 changed patterns: each carries an '
 'editorial-review changes-requested event followed by a fresh '
 'editorial-review acceptance bound to its recomputed tier-2 scope '
 'digest and corroborated by priority7-editorial-corroboration, so '
 'those 44 are now editorial-reviewed. The 45 historical '
 'product-approval acceptances are preserved unchanged; on the 44 '
 'changed patterns they are stale because their tier-3 scope moved. No '
 'new product-approval event was created and the corrected content is '
 'NOT product-approved. '
 'vp-p-zajmowac-sie-look-after-person-instrumental-object-6f93facbd939 '
 'was not touched by H2, keeps all its current digests and remains '
 'approved. releaseMode stays solo-maintainer-reference-backed, '
 'activityEligibility stays empty on all 45, no audio was enabled, and '
 'nothing was frozen, released or projected to runtime.')
)


def iter_patterns(corpus):
    """Yield ``(lemma, meaning, pattern)`` in document order."""
    for lemma in corpus.get("lemmas", []):
        for meaning in lemma.get("meanings", []):
            for pattern in meaning.get("patterns", []):
                yield lemma, meaning, pattern


def appended_h2_events(pattern_id):
    """Return the statically pinned events H2 appended to ``pattern_id``.

    ``pattern_id`` must be one of the 44 literal H2 identities.  In
    particular, this function never reads a live lemma, meaning, pattern or
    event to decide what the H2 transition was.
    """
    if pattern_id not in H2_EXPECTED_PATTERN_IDS:
        raise KeyError(f"pattern identity is outside Phase 4F-H2: {pattern_id!r}")
    return copy.deepcopy(H2_APPENDED_EVENTS[pattern_id])


def _h2_transition_matches(pattern):
    """True when ``pattern`` still carries the exact pinned H2 transition."""
    pattern_id = pattern.get("id")
    if pattern_id not in H2_EXPECTED_PATTERN_IDS:
        return False
    if pattern.get("reviewState") != H2_FINAL_REVIEW_STATE:
        return False
    events = pattern.get("reviewEvents")
    expected_events = H2_APPENDED_EVENTS[pattern_id]
    if not isinstance(events, list) or len(events) <= len(expected_events):
        return False
    if events[-len(expected_events):] != expected_events:
        return False
    for path, (_before, after) in H2_FIELD_REWRITES.get(pattern_id, {}).items():
        if _read_field(pattern, path) != after:
            return False
    if pattern_id in H2_EXAMPLE_PATTERN_IDS:
        if pattern.get("examples") != [H2_NEW_EXAMPLES[pattern_id]]:
            return False
    return True


def _read_field(pattern, path):
    if path == "learnerExplanationEn":
        return pattern.get("learnerExplanationEn")
    prefix, _, suffix = path.partition("]")
    if not prefix.startswith("errorNotes[") or suffix != ".guidanceEn":
        raise KeyError(f"unknown pinned field path: {path!r}")
    index = int(prefix[len("errorNotes["):])
    notes = pattern.get("errorNotes")
    if not isinstance(notes, list) or index >= len(notes):
        return None
    note = notes[index]
    return note.get("guidanceEn") if isinstance(note, dict) else None


def _write_field(pattern, path, value):
    if path == "learnerExplanationEn":
        pattern["learnerExplanationEn"] = value
        return
    index = int(path[len("errorNotes["):path.index("]")])
    pattern["errorNotes"][index]["guidanceEn"] = value


def without_phase_4fh2_content_completion(corpus):
    """Return a copy of ``corpus`` with the Phase 4F-H2 transition reverted.

    A pattern is normalised only when its ID is in the literal 44-identity
    allowlist and every pinned fact about its H2 transition still holds:
    the final review state, the exact trailing event objects, the exact
    rewritten prose, and the exact new example.  Anything else -- a different
    wording, a repinned digest, a duplicated or missing event, an extra or
    edited example -- is left wholly visible.
    """
    corpus = copy.deepcopy(corpus)
    for _lemma, _meaning, pattern in iter_patterns(corpus):
        if not _h2_transition_matches(pattern):
            continue
        pattern_id = pattern["id"]
        del pattern["reviewEvents"][-len(H2_APPENDED_EVENTS[pattern_id]):]
        for path, (before, _after) in H2_FIELD_REWRITES.get(pattern_id, {}).items():
            _write_field(pattern, path, before)
        if pattern_id in H2_EXAMPLE_PATTERN_IDS:
            del pattern["examples"]
        pattern["reviewState"] = H2_PRIOR_REVIEW_STATE
    return corpus


def without_phase_4fh2_context(context):
    """Return a copy of ``context`` with the H2 notice paragraph reverted.

    Phase 4F-H2 registered no reviewer and no nonhuman actor, so the notice
    is the only context change there is to revert, and it is removed only
    when it is still the exact appended suffix.
    """
    context = copy.deepcopy(context)
    notice = context.get("contextNotice")
    if isinstance(notice, str) and notice.endswith(H2_CONTEXT_NOTICE_SUFFIX):
        context["contextNotice"] = notice[:-len(H2_CONTEXT_NOTICE_SUFFIX)]
    return context


def without_phase_4fh2_corpus_text(text):
    """Reconstruct the corpus file text as it stood before Phase 4F-H2.

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
            "4F-H2 text normaliser cannot reconstruct it safely")
    return json.dumps(
        without_phase_4fh2_content_completion(document),
        indent=2, ensure_ascii=False) + "\n"


def without_phase_4fh2_context_text(text):
    """Reconstruct the context file text as it stood before Phase 4F-H2.

    Byte surgery on the one block Phase 4F-H2 inserted -- the appended notice
    paragraph -- so the result keeps the file's hand-maintained formatting
    exactly.  The block must appear exactly once; an edit to it leaves it
    unrecognised and the caller's byte comparison then fails, which is the
    intent.
    """
    if text.count(H2_CONTEXT_NOTICE_SUFFIX) == 1:
        text = text.replace(H2_CONTEXT_NOTICE_SUFFIX, "", 1)
    return text
