# Priority 7 — Phase 5-A: syntetyczne zamrożenie i próba autoryzacji wydania

## 1. Wynik

Całkowicie fikcyjny kandydat Priority 7 przeszedł **prawdziwą** maszynerię
zarządzania wydaniem — walidację redakcyjną, wyprowadzenie stanu review,
zamrożenie identyfikatorów, projekcję release-authoritative, walidację
publicznego runtime i shipping loader z Phase 3F-A — a każdy niepoprawny,
nieaktualny lub niekompletnie zrecenzowany kandydat został zablokowany.

Most Python → JS działa na **rzeczywistych bajtach** projekcji
release-authoritative: nic nie zostało po drodze przepisane ręcznie do osobnego
fixture'u loadera.

**To nie jest prawdziwe zatwierdzenie, prawdziwe zamrożenie ani prawdziwe
wydanie.** Rzeczywisty korpus 45 wzorców pozostaje bajt w bajt identyczny z HEAD,
w całości w stanie `research`, bez ani jednego zdarzenia review.

Nie wykonano commita, pushu ani dodania remote. Nie zmieniono żadnego pliku
produkcyjnego.

## 2. Baseline bezpieczeństwa

- Katalog roboczy: `/Users/Kaj/Downloads/Repository for Claude - Priority 7 Phase 5A`
- Gałąź: `priority-7-phase-5a-synthetic-freeze`
- Baseline HEAD: `82ea6fe5ce90c6b209cb0b370d7db628dc5846ca`
- Baseline tree: `e420563853635fba6918ccf8517b670d3ca32539`
- Remotes: **zero** (zweryfikowane przed i po)
- `push.default`: `nothing`
- Stan początkowy: czysty

### Baseline testów (zmierzony, nie założony)

| Kontrola | Wynik |
| --- | --- |
| Python (`unittest discover`) | **354 testy, 0 błędów** |
| JXA (`tests/*.js`) | **35 zestawów, 10 497 asercji, 0 błędów** |
| `validate_content.py` | OK (1675 ID, sha256 `2a71401d…`) |
| `verify_audio.py` | OK (3377 fraz / 3377 wpisów / 3377 MP3) |
| `build_pages.py --check` | OK (23 + 6 stron + hub, 32 URL-e) |
| `git diff --check` | czysto |

Baseline zgodny z oczekiwaniami z Phase 3F-A. Nie był czerwony.

## 3. Zidentyfikowana ścieżka release-authoritative

Ścieżka autorytatywna **istnieje już** w `priority7_tooling.py` i jest to
biblioteczne API, bez żadnego opakowania CLI:

```
freeze_editorial(document, revision, context, previous=…, tombstones=…)
        ↓  (pełna koperta zamrożenia)
validate_frozen_release(frozen)
        ↓
verified_runtime_from_frozen(frozen)  →  publiczny runtime
```

Ścieżka nieautorytatywna, wyraźnie tak nazwana w kodzie:

```
project_runtime_nonrelease(...)  /  project_nonrelease_fixture(...)
```

**Nie dodano żadnego nowego API produkcyjnego.** Brakującego prymitywu nie było,
więc zgodnie z §30 nic nie dopisano do `priority7_tooling.py`.

### Dowód, że projekcja standalone nie nadaje autorytetu

| Własność | `project_runtime_nonrelease` | `freeze_editorial` + `verified_runtime_from_frozen` |
| --- | --- | --- |
| Poprawny publiczny kształt | tak | tak |
| Akceptuje dowolną dodatnią rewizję | **tak** (1, 2, 7, 424242 — wszystkie przechodzą) | nie |
| Rejestr alokacji / historia tombstone | nie | tak |
| Kontrakt rewizji względem poprzedniego snapshotu | nie | tak |
| Zwraca kopertę `artifactStatus` | `…nonrelease-fixture`, `releaseAuthorized:false` | `priority-7-frozen-fixture-nonproduction` |

Sama koperta runtime **nie może** ponownie wejść na ścieżkę autorytatywną:
`verified_runtime_from_frozen(runtime)` zgłasza `SCHEMA_REQUIRED` dla wszystkich
siedmiu brakujących wymiarów (`allocations`, `identity`, `structure`, `wording`,
`policy`, `tombstones`, `reviewHistory`) oraz `artifactStatus`. Tak samo odrzucana
jest koperta nonrelease.

**Autoryzacji wydania nie da się wywnioskować z kształtu publicznego JSON-a.**
Ręcznie podrobiony dokument o poprawnym kształcie przechodzi `validate_runtime`
(bo to walidator kształtu), a mimo to `validate_frozen_release` go odrzuca.
`PP_VERB_PATTERNS.available` również mówi wyłącznie „przyjęto wartość właściwego
kształtu”, co jest udokumentowane w samym `pp-verb-patterns.js`.

### Brak wrappera CLI — celowo

`priority7_tooling.py main()` udostępnia wyłącznie `validate-specification`,
`validate-editorial`, `validate-runtime` i `project-fixture`. Jedyne polecenie,
które zapisuje plik (`project-fixture --output`), emituje kopertę z
`releaseAuthorized: false`. Żadne polecenie nie potrafi wyprodukować artefaktu
release-authoritative — co jest właściwym stanem dla Phase 5-A.

## 4. Projekt syntetycznego fixture'u redakcyjnego

Plik: `tests/fixtures/priority7/synthetic-release-editorial.json` (351 linii)

Koperta pliku jest jawnie testowa i **nie** podszywa się pod korpus redakcyjny:

```
testOnlyNotice            — „SYNTHETIC TEST-ONLY … nothing here is Polish …”
artifactStatus            — priority-7-phase-5a-synthetic-editorial-nonproduction
syntheticIdentities       — reviewerRegistry / authorRegistry / sourceRegistry
syntheticRepositorySources— wstrzykiwany, w pełni syntetyczny korpus źródłowy
reviewContextDate         — 2026-08-09 (deterministyczny `context.today`)
editorial                 — właściwy dokument w zwykłej kopercie redakcyjnej
```

Zawartość: dwa wymyślone, niepolskie lematy.

| Lemat | Wzorzec | `teachingStatus` | `reviewState` | Projektuje się? |
| --- | --- | --- | --- | --- |
| `zorbulate` | `direct-object` (biernik) | active-production | approved | **tak** |
| `zorbulate` | `clause-content` (zdanie `że`) | recognition-only | approved | **tak** |
| `quuxify` | `infinitive-content` | active-production | research | **nie** |

Cechy istotne dla próby:

- brak jakiegokolwiek znaku wyłącznie polskiego w `canonicalLemma`, `pl`, `en`,
  `glossesEn` (asercja automatyczna);
- zero wspólnych ciągów i zero wspólnych ID z rzeczywistym korpusem (asercja
  automatyczna, porównanie zbiorów);
- jedyny `contentRefs` wskazuje na syntetyczną kartę `p7-phase5a-synthetic-card-001`;
- obie ścieżki proweniencji przykładu obecne (`original` i `repository-reuse`);
- cyfrowe skróty (`scopeDigest`, `supportingEvidenceDigests`) są **prawdziwe** i
  zapisane w pliku — jeśli treść i skrót się rozjadą, testy padają głośno.

Fixture **nie** znajduje się w prawdziwym `editorial/`.

## 5. Syntetyczne tożsamości recenzenta i autora

Minimalny zestaw wymagany przez rzeczywistą maszynerię:

| Referencja | Rola | `human` |
| --- | --- | --- |
| `test-reviewer-external-001` | `external-verification` | true |
| `test-reviewer-native-001` | `native-linguistic` | true |
| `test-reviewer-product-001` | `product-approval`, `correction`, `reopen` | true |
| `test-author-original-001` | autor przykładów `original` | true |

Trzy różne osoby, bo tooling wymaga `ownerAllowsMultipleRoles` dla jednego
recenzenta pełniącego wiele etapów — nie skorzystano z tego wyjątku.

Test automatyczny odrzuca plik, jeśli pojawi się w nim `Kaj`, `GPT`, `Claude`,
`Codex`, `OpenAI`, `Anthropic` lub `gordadze`, i wymaga prefiksu `test-` dla każdej
tożsamości. **Żadnego z tych rekordów nie wolno czytać jako dowodu prawdziwego
review.**

## 6. Ścieżka stanu review i prawidłowa kolejność (§17)

Model stanu jest **wyprowadzany**, nie deklarowany: `reviewState` musi zgadzać się
z tym, co wynika z historii zdarzeń i aktualności skrótów, inaczej pada
`REVIEW_STATE_MISMATCH`.

Wymuszona kolejność etapów:

```
research → external-verification(accept)  → externally-verified
         → native-linguistic(accept)      → native-reviewed
         → product-approval(accept)       → approved
```

Ustalona bezpieczna kolejność operacji, potwierdzona eksperymentalnie:

| Kolejność | Wynik |
| --- | --- |
| zmiana treści → freeze | **odrzucone** (`REVIEW_STATE_MISMATCH`) |
| zmiana → ponowne review → freeze | **odrzucone** dla wydanego brzmienia (`FROZEN_WORDING_CORRECTION_REQUIRED`) |
| zmiana → korekta właściciela → ponowne review → freeze | **przyjęte** |

Dodatkowo wymuszone:

- historia review wydanego wzorca musi pozostać **dokładnym prefiksem**
  (`FROZEN_REVIEW_HISTORY_NOT_APPEND_ONLY`) — przepisanie łańcucha zdarzeń jest
  samo w sobie naruszeniem, nawet gdy nowe zdarzenia są poprawne;
- kolejność dowodów jest append-only (`FROZEN_EVIDENCE_NOT_APPEND_ONLY`);
- stan `rejected`/`deferred` wymaga jawnego `reopen` (`REVIEW_REOPEN_REQUIRED`),
  a reopen po odrzuceniu wymaga autorytetu `product-approval`.

## 7. Zamrożenie ID, alokacje i tombstone'y (§11–§12)

Pierwsze zamrożenie alokuje **9 encji** (1+1 lemat, 1+1 znaczenie, 3 wzorce,
2 przykłady) w czterech rodzinach `vp-l` / `vp-m` / `vp-p` / `vp-e`. Powtórne
zamrożenie identycznego dokumentu jest bajt w bajt identyczne.

| Przypadek | Zachowanie | Kod |
| --- | --- | --- |
| **A** encja niezmieniona | zachowuje zamrożone ID; `allocations` i `identity` identyczne | — |
| **B** nowa encja | nowa deterministyczna alokacja; poprzednie zachowane (podzbiór właściwy); 2 alokacje przykładów pod nowym rodzicem | — |
| **C** encja usunięta | wymaga tombstone'u | `FROZEN_REMOVAL_WITHOUT_TOMBSTONE` |
| **C** ID po wycofaniu | znika z `identity`, **zostaje** w `allocations` (zarezerwowane) | — |
| **D** powrót tej samej encji | zablokowany | `TOMBSTONE_RESURRECTION` |
| **D** inna encja bierze ID | zablokowany trzema warstwami | `ALLOCATION_KEY` + `REVIEW_STATE_MISMATCH`; bez alokacji: `ID_RECOMPUTATION` |
| **E** zmiana `relationType` | wymaga wymiany | `FROZEN_RELATION_REPLACEMENT_REQUIRED` |
| **E** zmiana `key` w miejscu | zablokowana | `ALLOCATION_KEY` |
| **E** zmiana identyczności complementu | wymaga wymiany | `FROZEN_COMPLEMENT_REPLACEMENT_REQUIRED` |

Dodatkowo: `retirementRevision` musi równać się rewizji przejścia
(`TOMBSTONE_REVISION`); nie można wystawić tombstone'u dla nigdy niewydanego ID
(`TOMBSTONE_UNKNOWN_ID`); ponowne dodanie lub podmiana istniejącego tombstone'u
przez interfejs przejścia jest odrzucana (`TOMBSTONE_IMMUTABLE`).

**Ograniczenie odnotowane uczciwie:** `freeze_editorial` traktuje `previous` jako
zaufane wejście. Edycja zapisanego pliku zamrożenia (np. przepisanie `reason`
tombstone'u) nie jest wykrywalna, bo funkcja nie ma niezależnej pamięci tego, co
baseline mówił wcześniej. Integralność przechowywanego artefaktu należy do
przyszłej komendy wydania / warstwy składowania, nie do tej czystej funkcji.
Sama retencja ID mimo to obowiązuje. Udokumentowane testem
`test_tombstone_tampering_inside_the_stored_baseline_is_out_of_scope`.

Żadne ID z rzeczywistego pilota 45 wzorców nie zostało zaalokowane ani zamrożone.

## 8. Unieważnianie przez skróty (§13–§14)

`evidence_digest` obejmuje **kompletny rekord, wraz z `note`** — potwierdzone
osobnym testem (usunięcie `note` i zmiana `note` dają inne skróty).

| Mutacja | Wykryta jako |
| --- | --- |
| zmiana `locator` dowodu | `REVIEW_STATE_MISMATCH` |
| zmiana samego `note` dowodu | `REVIEW_STATE_MISMATCH` |
| usunięcie przypiętego dowodu | `REVIEW_STATE_MISMATCH` |
| zmiana dowodu **nieużywanego** przez żaden `errorNote` | `REVIEW_STATE_MISMATCH` → stan spada do `research` |
| zmiana `aspect` lematu (rodzic) | `REVIEW_STATE_MISMATCH` na **obu** wzorcach potomnych |
| zmiana `glossesEn` znaczenia (rodzic) | `REVIEW_STATE_MISMATCH` |
| nieaktualny skrót etapu native | stan spada dokładnie do `externally-verified` |
| nieaktualny skrót etapu product | stan spada dokładnie do `native-reviewed` |
| `scopeVersion` = 2 | `REVIEW_SCOPE_VERSION` |

Test przypięcia dowodu jest celowo odizolowany: mutowany jest drugi rekord
dowodowy, do którego nie odwołuje się żaden `errorNote`, więc nie wpływa on na
żaden skrót zakresu — jedyne, co może pęknąć, to przypięcie w akceptacji
zewnętrznej. To odróżnia regułę przypięcia od reguły zakresu.

**Naprawa po wydaniu jest dopisaniem, nie edycją.** Edycja wydanego rekordu
dowodowego jest odrzucana wprost (`FROZEN_EVIDENCE_NOT_APPEND_ONLY`), ponieważ
odwołania `errorNotes.evidenceRefs` są pozycyjne. Wspierana ścieżka — dopisanie
nowego rekordu + korekta właściciela + ponowne review — przechodzi, a rewizja
zostaje na miejscu, bo dowody są prywatne.

## 9. Proweniencja przykładów (§15)

**Repository-reuse** wymaga dokładnego źródła:

| Przypadek | Kod |
| --- | --- |
| tekst ≠ pole źródłowe | `REPOSITORY_SOURCE_MISMATCH` |
| nieistniejące `id` źródła | `REPOSITORY_SOURCE_DANGLING` |
| złe pole właściwego źródła | `REPOSITORY_SOURCE_MISMATCH` |
| brak `repositorySource` | `ORIGIN_REPOSITORY_REQUIRED` |
| brak indeksu repozytorium | `REPOSITORY_INDEX_REQUIRED` |
| `authorRef` przy reuse | `ORIGIN_AUTHOR_FORBIDDEN` |

**Original** wymaga prawdziwej tożsamości autora:

| Przypadek | Kod |
| --- | --- |
| brak `authorRef` | `SCHEMA_REQUIRED` |
| niezarejestrowany autor | `AUTHOR_REGISTRY_DANGLING` |
| autor z `human: false` | `AUTHOR_NOT_HUMAN` |
| `repositorySource` przy original | `ORIGIN_REPOSITORY_FORBIDDEN` |

Zmiana `origin` już wydanego przykładu wymaga świeżej korekty właściciela
(`FROZEN_WORDING_CORRECTION_REQUIRED`).

## 10. Uprawnienia do aktywności (§16)

Nie utworzono żadnej rzeczywistej aktywności ani ćwiczenia.

| Reguła | Kod |
| --- | --- |
| `recognition-only` zakazuje `grammar-build` i `type-it` | `RECOGNITION_PRODUCTION_ACTIVITY` |
| `deferred` nie może wystawić żadnej aktywności | `DEFERRED_ACTIVITY` |
| uprawnienia wymagają stanu `approved` | `UNAPPROVED_ACTIVITY` |
| audio wymaga `listening` **i** `approved` | `AUDIO_NOT_AUTHORIZED` |
| listening/aktywna gramatyka wymaga przykładu | `ACTIVITY_EXAMPLE_REQUIRED` |

Uprawnienia domyślnie są zamknięte: nierecenzowany lemat `quuxify` nie wnosi do
runtime niczego, bo nie trafia tam w ogóle. Uprawnienia przechodzą przez projekcję
dokładnie (posortowane, bez zmian wartości).

## 11. Kontrakt `patternDataRevision` (§18)

Zweryfikowany **wobec rzeczywistego kodu** (`freeze_editorial`, linie 4045–4047 i
4367–4378), nie wobec pamięci. Porównanie dotyczy wyłącznie
`runtimeProjection` po usunięciu pola rewizji.

| Scenariusz | Zachowanie | Dowód |
| --- | --- | --- |
| pierwsze wydanie syntetyczne | rewizja **1** wymuszona | rewizja 2/3 → `FROZEN_INITIAL_REVISION`; 0/−1 → `FROZEN_REVISION` |
| identyczna ponowna projekcja | rewizja **pozostaje 1** | podbicie na 2 → `FROZEN_REVISION_TRANSITION` |
| zmiana publicznego ładunku | rewizja **poprzednia + 1** | pozostawienie 1 → `FROZEN_REVISION_TRANSITION` |
| zmiana **wyłącznie** metadanych prywatnych | rewizja **pozostaje poprzednia** | `internalScope` zmienione, `wording` różne, `runtimeProjection` identyczne; próba podbicia → `FROZEN_REVISION_TRANSITION` |
| przeskok rewizji (3, 4, 42 po 1) | odrzucone | `FROZEN_REVISION_TRANSITION` |
| sekwencja wielowydaniowa | 1 → 2 → 3, po jednym kroku | pełna koperta waliduje się na każdym etapie |

Zachowanie dla zmiany wyłącznie prywatnej zostało **ustalone z implementacji, nie
zgadnięte**: kod porównuje wyłącznie publiczną projekcję, więc zmiana niewidoczna
publicznie nie może i nie powinna podbijać rewizji publicznej.

Nie przydzielono żadnej rzeczywistej rewizji projektu.

## 12. Prywatność projekcji publicznej (§19)

Publiczny runtime z udanej projekcji release-authoritative zawiera na najwyższym
poziomie **dokładnie** `formatVersion`, `patternDataRevision`, `lemmas`.

Kontrole rekurencyjne, na dowolnej głębokości:

- zero kluczy z `PRIVATE_RUNTIME_KEYS` (sweep po całej strukturze);
- zero referencji recenzenta, autora i źródła;
- zero `internalScope`, `locator`, notatek dowodowych, notatek review,
  `scopeDigest`, `reviewedAt`, `checkedAt`, `authoredAt`;
- zero ciągów `sha256:`, `tombstone`, `retirementRevision`, `allocations`,
  `reviewHistory`, statusów artefaktów redakcyjnych/zamrożenia;
- nierecenzowany lemat `quuxify` nie pojawia się ani jako ID, ani jako tekst;
- zbiór ID wzorców w runtime = dokładnie zbiór wzorców `approved`.

Kontrola prywatności celowo **nie** opiera się wyłącznie na walidatorze: dodatkowo
dla **każdego** z 26 kluczy `PRIVATE_RUNTIME_KEYS` wstrzyknięcie go do runtime
zostaje odrzucone przez `validate_runtime`.

Uwaga kontraktowa: `usage.note` jest polem **publicznym** z założenia
(`_project_usage`). Test prywatności celowo tego nie zgłasza — asercja „żaden klucz
o nazwie note” twierdziłaby coś, czego kontrakt nigdy nie obiecywał.

## 13. Walidacja publicznego runtime (§20)

Autoryzowana projekcja przechodzi `validate_runtime` bez uwag. Odrzucane są m.in.:
`patterns: null`, `lemmas` jako string, pusta tablica `lemmas`, nieznany
identyfikator przypadka, `teachingStatus: deferred`, `patternDataRevision` 1.0 / 0,
`formatVersion: 2`, dodatkowy klucz koperty. Walidatora nie osłabiono.

## 14. Most Python → JS do loadera Phase 3F-A (§21–§22)

Most prowadzony jest w obie strony i za każdym razem na **rzeczywistym wyjściu**
ścieżki release-authoritative:

- **Python → JS** (`tests/test_priority7_phase5a.py`, `LoaderBridgeTests`):
  zamrożenie → weryfikacja koperty → runtime → zapis do katalogu tymczasowego →
  `osascript` uruchamia `tests/fixtures/priority7/phase5a-loader-harness.js`,
  który wykonuje **shipping** `loadRuntimeDocument` i konsumenta.
- **JS → Python** (`tests/test_priority7_phase5a_bridge.js`): zestaw JXA sam
  wywołuje `python3`, prosi ścieżkę release-authoritative o bajty i podaje je
  loaderowi, dzięki czemu most jest objęty również zwykłym przebiegiem JXA.

Wynik siedmiu wymaganych punktów:

| # | Dowód | Wynik |
| --- | --- | --- |
| 1 | projektor release-authoritative emituje publiczny runtime | tak, identyczny z `frozen["runtimeProjection"]` |
| 2 | runtime przechodzi walidator publiczny | tak, zero uwag |
| 3 | loader Phase 3F-A go przyjmuje | `settled === true` |
| 4 | `PP_VERB_PATTERNS.available === true` | tak (przed ładowaniem `false`) |
| 5 | indeks/podsumowanie wyprowadzalne | `{lemmas: 1, patterns: 2}`, „1 verb · 2 patterns”, indeks z `ZORBULATE — TEST-ONLY SYNTHETIC`, filtry `all/accusative/no-case`, `cardSupport` → `doorway` |
| 6 | brak stanu prywatnego w runtime | `__holdsPrivateKeyForTest` → `false` |
| 7 | brak trwałego zapisu | dokładnie jedno wywołanie transportu z `cache: no-store`; runtime tylko w katalogu tymczasowym |

Runtime nigdy nie został zapisany do repozytorium. `content/verb-patterns.json`
nie powstał; katalog `content/` nie istnieje.

### Parytet międzyjęzykowy (§22)

Porównane wprost, z wartości odczytanych z obu źródeł (bez tworzenia drugiego
źródła prawdy): `FORMAT_VERSION`, klucze koperty, `PRIVATE_RUNTIME_KEYS` ↔
`PRIVATE_KEYS` (26 pozycji, dokładne lustro), identyfikatory przypadków, typy
complementów, typy relacji, role, klucze aktywności, poziomy CEFR, priorytety
użycia, rejestry, rodzaje zdań podrzędnych, rodzaje i cele `contentRefs`.

Jedna **zamierzona** asymetria, zapisana jako asercja: JS akceptuje węższy zbiór
`TEACHING_STATUSES` (`active-production`, `recognition-only`) niż enum redakcyjny,
bo `deferred` nigdy nie może się projektować.

## 15. Macierz negatywna end-to-end (§23)

Wszystkie dziesięć przypadków A–J jest **rzeczywiście egzekwowanych**; żaden nie
jest tylko udokumentowany. Test `test_matrix_coverage_is_complete_and_honest`
pilnuje, by litery A–J faktycznie istniały.

| # | Przypadek | Kod |
| --- | --- | --- |
| A | rekord wyłącznie `research` | `PROJECTION_EMPTY` |
| B | brak wymaganego review native | `REVIEW_STAGE_ORDER` |
| C | nieaktualny skrót dowodu | `REVIEW_STATE_MISMATCH` |
| D | nieaktualny skrót review | `REVIEW_STATE_MISMATCH` |
| E | brak/niepoprawna alokacja | `FROZEN_IDENTITY_UNALLOCATED`, `FROZEN_ALLOCATION_COVERAGE`, `FROZEN_SEED` |
| F | ponowne użycie ID z tombstone | `TOMBSTONE_RESURRECTION` |
| G | niepoprawna proweniencja przykładu | `REPOSITORY_SOURCE_DANGLING`, `AUTHOR_REGISTRY_DANGLING` |
| H | uprawnienia sprzeczne ze statusem | `RECOGNITION_PRODUCTION_ACTIVITY` |
| I | pole prywatne wstrzyknięte do runtime | `RUNTIME_PRIVATE_FIELD` + odrzucenie przez loader |
| J | zmiana ładunku bez poprawnej rewizji | `FROZEN_REVISION_TRANSITION` |

Po stronie JS loader odrzuca dodatkowo: wstrzyknięty `reviewState`, wstrzyknięte
`evidence`, `origin` na głębokości przykładu, klucz `key` na poziomie znaczenia,
kopertę nonrelease, nadmiarowy klucz koperty, błędny complement, `patterns: null`,
`pl` jako liczbę, rewizję 0 i 1.5, `formatVersion: 2` oraz pustą listę lematów.

## 16. Atomowość i zapisy plików (§24–§25)

**Ścieżka release-authoritative jest czysta i w pamięci.** Udowodnione
mechanicznie, nie deklaratywnie: na czas wywołania podmieniane są `builtins.open`
(tryby zapisu), `Path.write_text`, `Path.write_bytes`, `os.replace` i `os.rename`
na pułapki zgłaszające błąd — `freeze_editorial`, `verified_runtime_from_frozen`
i `project_runtime_nonrelease` nadal kończą się sukcesem.

Wynika stąd, że:

- nieudana walidacja **nie zwraca żadnego wyniku** — zgłasza `ValidationFailure`,
  nie istnieje częściowo zbudowana koperta do odczytania;
- nieudane przejście **nie mutuje wejść** — porównanie bajtowe `previous` i
  dokumentu przed i po nieudanym wywołaniu;
- poprzedni dobry snapshot przeżywa nieudane przejście i nadal jest wydawalny;
- żaden rejestr alokacji nie zmienia się nieoczekiwanie.

Jedynym punktem wejścia, który zapisuje plik, jest `project-fixture --output`, a
ten emituje kopertę z `releaseAuthorized: false`.

**Zgodnie z §25 kwestia atomowości zapisu (temp-file + replace) jest odroczona do
przyszłej komendy wydania / wrappera**, ponieważ dzisiejsze tooling nic nie
zapisuje. To samo dotyczy integralności przechowywanego baseline'u (§7 powyżej).

Po stronie JS odrzucony kandydat nie narusza wcześniej przyjętej wartości:
`available` pozostaje `true`, a podsumowanie niezmienione.

## 17. Testowanie mutacyjne (§31)

Przeprowadzone na **kopii roboczej w katalogu scratch**, nigdy na drzewie
repozytorium. Dwanaście mutacji strażników w `priority7_tooling.py` i
`pp-verb-patterns.js`; sygnałem jest pojawienie się nowych czerwonych testów.

| Mutacja | Wykryta przez |
| --- | --- |
| usunięcie kolejności etapu native | 1 test |
| ignorowanie aktualności review native | 2 testy |
| ignorowanie przypięć dowodowych | 1 test |
| ignorowanie skrótu product-approval | 2 testy |
| dopuszczenie przeskoków rewizji | 5 testów |
| dopuszczenie pól prywatnych w runtime | 1 test |
| obejście walidacji release-authoritative | 2 testy |
| usunięcie bez tombstone'u | 1 test |
| `recognition-only` uczy produkcji | 2 testy |
| loader: usunięcie kontroli zamkniętej koperty | 1 test |
| ponowne użycie ID z tombstone (jedna warstwa) | **0** — patrz niżej |
| loader: usunięcie sweepu kluczy prywatnych | **0** — patrz niżej |

Pierwsze uruchomienie ujawniło **trzy rzeczywiste luki w moich asercjach**
(kolejność etapu native, aktualność native, izolacja przypięcia dowodu). Dodano
cztery ukierunkowane testy; wszystkie trzy mutacje są teraz wykrywane.

Dwie pozostałe „niewykryte” mutacje to **prawdziwa obrona wielowarstwowa w
toolingu**, nie słabość testów:

- `TOMBSTONE_RESURRECTION` jest egzekwowane **dwukrotnie** — w `freeze_editorial`
  (linia 4302) i niezależnie w `_validate_frozen_document` (linia 3876). Po
  usunięciu **obu** warstw padają trzy testy Phase 5-A. Zweryfikowane wprost.
- Sweep kluczy prywatnych w `accept()` jest redundantny: zamknięta walidacja
  kluczy w `build()` odrzuca **każdy** klucz prywatny z `PRIVATE_RUNTIME_KEYS`
  umieszczony na poziomie koperty, lematu, znaczenia, wzorca, complementu,
  `usage` i `cefr` — sprawdzone wyczerpująco, zero przypadków, które przeżywają.
  Bezpośredni test samej funkcji należy do zestawu Phase 3F-A
  (`__holdsPrivateKeyForTest`), powtórzony też w moście Phase 5-A.

## 18. Zmiany w toolingu

**Żadnych.** `priority7_tooling.py` i `pp-verb-patterns.js` są bajt w bajt
identyczne z HEAD. Nie dodano API produkcyjnego, nie dodano polecenia CLI, nie
osłabiono żadnego walidatora.

## 19. Dokładny zakres plików

### Nowe (4)

| Plik | Linie | Rola |
| --- | --- | --- |
| `tests/test_priority7_phase5a.py` | 2044 | 95 testów zarządzania wydaniem |
| `tests/test_priority7_phase5a_bridge.js` | 348 | 47 asercji mostu międzyjęzykowego |
| `tests/fixtures/priority7/synthetic-release-editorial.json` | 351 | syntetyczny prywatny fixture redakcyjny |
| `tests/fixtures/priority7/phase5a-loader-harness.js` | 206 | harness JXA sterujący shipping loaderem |

### Zmodyfikowane (4) — wyłącznie rozszerzenia list dozwolonych plików

| Plik | Zmiana |
| --- | --- |
| `tests/test_priority7_phase2a.py` | +25 / −0 |
| `tests/test_priority7_phase3b.py` | +12 / −4 |
| `tests/test_priority7_phase3d1.py` | +6 / −2 |
| `tests/test_priority7_phase3fa.py` | +5 / −0 |

Cztery istniejące testy egzekwują dokładny inwentarz
`tests/fixtures/priority7/` („fail closed, nie pojawiaj się po cichu”) i
zadziałały dokładnie tak, jak zaprojektowano — nowe fixture'y je wywróciły.
Zgodnie z precedensem Phase 3D-1 i Phase 3F-A („NARROWED … not relaxed”) listy
zostały **rozszerzone o wyliczone pozycje, nie rozluźnione**, wraz z dodatkową
asercją, że syntetyczny fixture redakcyjny nosi własny znacznik
nieprodukcyjny i zachowuje zwykłą kopertę redakcyjną wewnątrz.

**Nie zmieniono żadnego pliku produkcyjnego.** `index.html`, `sw.js`,
`manifest.json`, `pp-verb-patterns.js`, `priority7_tooling.py`, dane, treści
redakcyjne i wygenerowane strony pozostały nietknięte.

## 20. Pełna walidacja końcowa

| Kontrola | Baseline | Po zmianach |
| --- | --- | --- |
| Python | 354 testy, 0 błędów | **449 testów, 0 błędów** (+95) |
| JXA | 35 zestawów / 10 497 asercji / 0 błędów | **36 zestawów / 10 544 asercje / 0 błędów** (+1 / +47) |
| `validate_content.py` | OK | **OK** (sha256 `2a71401d…` bez zmian) |
| `verify_audio.py` | OK | **OK** (3377 / 3377 / 3377) |
| `build_pages.py --check` | OK | **OK** (wyjście aktualne) |
| `git diff --check` | czysto | **czysto** |

Zestawy objęte przebiegiem: Priority 7 Phase 2A, 3B, 3C, 3D-1, 3F-A, 5-A;
loader JXA, patterns UI, choose UI, Grammar, keyboard/focus/mobile,
Phase 3 closeout — wszystkie w pełnych przebiegach powyżej.

## 21. Granica wydania — dowód końcowy (§35)

| # | Warunek | Stan |
| --- | --- | --- |
| 1 | rzeczywisty korpus bajt w bajt jak HEAD | tak, sha256 `b6fb8139ed99368a2a1527db6dd79d32f06df3e2e069cf59ae559a798176435f`; `git diff HEAD -- editorial/` czysty |
| 2 | 45/45 wzorców nadal `research` | tak (30 lematów, 34 znaczenia, 45 wzorców) |
| 3 | zero rzeczywistych zdarzeń review | tak |
| 4 | zero rzeczywistych uprawnień aktywności | tak |
| 5 | zero rzeczywistych uprawnień audio | tak |
| 6 | zero rzeczywistych ID ćwiczeń | tak, brak `vp-x-` |
| 7 | brak rzeczywistej tożsamości recenzenta/autora | tak, oba rejestry puste |
| 8 | brak zmian w rzeczywistych alokacjach | tak, `allocationRegistry` pusty |
| 9 | brak przydzielonej rzeczywistej `patternDataRevision` | tak |
| 10 | brak rzeczywistego publicznego runtime | tak |
| 11 | brak `content/verb-patterns.json` | tak, katalog `content/` nie istnieje |
| 12 | brak pobierania Priority 7 przy starcie | tak |
| 13 | brak zmian w Service Workerze | tak, `sw.js` bez zmian |
| 14 | brak zmian `APP_VERSION` | tak, `8.10` |
| 15 | brak zmian cache | tak, `popolsku-v65` / `popolsku-audio` |
| 16 | brak zmian schematu/migracji | tak, `SCHEMA_VERSION = 2`, `CONTENT_MIGRATION_REVISION = 2` |
| 17 | brak postępu/mastery | tak |
| 18 | brak analityki | tak |
| 19 | produkcja nietknięta | tak |
| 20 | zero remotes | tak |
| 21 | brak commita | tak |
| 22 | brak pushu | tak |

## 22. Ograniczenia

1. **Integralność przechowywanego zamrożenia** nie jest sprawdzana przez
   `freeze_editorial`; `previous` jest zaufanym wejściem. Należy do przyszłej
   komendy wydania.
2. **Atomowość zapisu plików** (temp-file + replace) jest odroczona, bo dzisiejsza
   ścieżka autorytatywna niczego nie zapisuje. Udowodniono czystość, nie
   atomowość zapisu.
3. **Natywne `Promise`** — oba zestawy JXA używają synchronicznego zamiennika
   `Immediate`, zgodnie z konwencją `tests/test_priority7_release_loader.js`,
   ponieważ host JavaScriptCore w `osascript` nie opróżnia kolejki mikrozadań.
   Dowód na prawdziwych `Promise` pozostaje po stronie kontroli w przeglądarce.
4. **Sweep kluczy prywatnych w loaderze** jest dziś nieosiągalny jako jedyny
   strażnik; nie da się skonstruować przypadku, w którym to on decyduje.
5. **Brak wrappera CLI** dla ścieżki release-authoritative — zamierzone, ale
   oznacza, że przyszła komenda wydania będzie musiała mieć własne testy
   atomowości i uprawnień.
6. **Rehearsal nie mówi nic o języku.** Wszystkie lematy, zdania, dowody,
   recenzenci i autorzy są wymyśleni. Żadne stwierdzenie o polszczyźnie nie jest
   tu wypowiadane ani implikowane.

## 23. Wniosek

**GO — syntetyczny most zamrożenia/wydania jest solidny.**

To **nie** autoryzuje rzeczywistego review, zamrożenia ani publikacji runtime
Priority 7. Nie rozpoczynać prawdziwej Phase 5. Nie wprowadzać wyników ludzkiego
review. Nie rozpoczynać Phase 4C. Nie publikować runtime.
