# Priority 7 — Phase 3F-A: audyt ścieżki wydania i próba syntetyczna

## 1. Wynik

Ścieżka przyszłego wydania została przećwiczona bez wydawania danych Priority 7.
Dodano uśpioną, wstrzykiwaną granicę transportu do istniejącego konsumenta
`pp-verb-patterns.js`, surowy syntetyczny dokument runtime oraz testy powodzenia,
awarii, atomowej zmiany stanu, izolacji i przyszłego pakietu wydania. Zwykły start
aplikacji nadal nie pobiera runtime Priority 7, rzeczywisty korpus nadal ma wyłącznie
status badawczy, a Service Worker, wersje, cache, migracje i pliki produkcyjne nie
zostały zmienione.

Wynik gotowości brzmi **GO dla dalszej pracy nad mechaniką wydania, NO-GO dla
publikacji rzeczywistego runtime**. Targeted correction pass zamknął dwa ustalenia
HIGH i trzy MEDIUM z niezależnego review: trwałość testów po commicie, prawidłowy
opis defektu offline helpera, wielowydaniowe wersjonowanie, bezpośredni test warstwy
defence-in-depth oraz jednolity `Promise<boolean>`. Nadal brakuje autoryzowanej
projekcji, zakończonego review i kompletnego atomowego pakietu opisanego w sekcji 9.

## 2. Granica bezpieczeństwa i baseline

- Katalog roboczy: `/Users/Kaj/Downloads/Repository for Codex - Priority 7 Phase 3FA`
- Gałąź: `priority-7-phase-3fa-release-readiness`
- Baseline HEAD: `a0d0117bf904ab69aeba8d7821fbdbf2ae8f5058`
- Baseline tree: `e44efe09b5b7ce99ee2662a149d6d24756e10911`
- Stan początkowy: czysty
- Remotes: zero
- `push.default`: `nothing`
- Nie wykonano commita, pushu ani dodania remote.

Przed zmianami przeszły: **337 testów Python**, **34 zestawy JXA / 10 429 asercji /
0 błędów**, `validate_content.py`, `verify_audio.py`, `build_pages.py --check` i
`git diff --check`.

Faza nie wykonała projekcji rzeczywistego korpusu, nie utworzyła
`content/verb-patterns.json`, nie nadała statusu review/release, nie dodała ćwiczeń,
audio, analityki ani zapisu postępu. Nie zmieniono `index.html`, `sw.js`, manifestu,
generatorów, danych, treści redakcyjnych ani wygenerowanych stron.

## 3. Audyt obecnej ścieżki aplikacji

### 3.1 Start i ładowanie skryptów

`index.html` ładuje dane w kolejności:

1. `data-a1.js`, `data-a2.js`, `data-b1.js`, `data-grammar.js`, `data-verbs.js`,
   `data-scenarios.js`, `data-podcasts.js`;
2. `pp-usage.js`, `pp-answer.js`, `pp-distractor.js`, `pp-migrate.js`;
3. `pp-verb-patterns.js`.

Zwykły start ma dokładnie dwa wyrażenia `fetch(`:

- `fetch("audio-manifest.json", { cache:"no-store" })` — manifest audio;
- `fetch("./", { method:"HEAD", cache:"no-store" })` — kontrola świeżości.

Kontrola świeżości uruchamia się raz na starcie i ponownie po `focus` lub powrocie
zakładki do stanu widocznego. Rejestracja Service Workera odbywa się w obsłudze
`load`. Nie ma wywołania `loadRuntimeDocument`, ścieżki
`content/verb-patterns.json`, parametru zapytania, flagi deweloperskiej ani innego
przełącznika uruchamiającego Priority 7. Kafelek Verb Patterns pozostaje widoczny,
lecz ekran startuje w neutralnym stanie niedostępności.

Znaczniki pozostają bez zmian:

- `APP_VERSION = "8.10"` w `index.html`;
- `CACHE = "popolsku-v65"` w `sw.js`;
- `AUDIO_CACHE = "popolsku-audio"` w `sw.js`;
- `SCHEMA_VERSION = 2` i `CONTENT_MIGRATION_REVISION = 2` w `pp-migrate.js`.

### 3.2 Obecny Service Worker

`sw.js` instaluje wymagany shell atomowo: każdy wymagany zasób musi odpowiedzieć
poprawnie i mieć dozwolony typ mediów; niepełny cache jest usuwany, a instalacja
kończy się błędem. Osobno traktuje zasoby opcjonalne i pełny, dokładny spis stron
wygenerowanych.

Routing obecnej wersji:

- nawigacje do root i stron wygenerowanych — network-first;
- `data-*.js` i `audio-manifest.json` — network-first;
- jawnie dopuszczone zasoby statyczne — cache-first;
- audio — cache-first w oddzielnym `AUDIO_CACHE`;
- nieznane żądania — network-only.

Worker nie wywołuje wykonywalnego `skipWaiting()` ani `clients.claim()`. Nowa
generacja czeka, aż starsze klienty znikną; podczas aktywacji usuwa stare numerowane
cache shell. `pp-verb-patterns.js` jest już ładowany przez `index.html`, lecz nie
należy obecnie ani do `REQUIRED_ASSETS`, ani do jawnej listy statycznej, więc worker
klasyfikuje go jako unknown/network-only. Jest to **rzeczywisty defekt offline
obecnego drzewa integracyjnego**: cache może dostarczyć `index.html`, a brak sieci
uniemożliwić dostarczenie helpera; późniejszy inline script dereferuje
`PP_VERB_PATTERNS`, więc inicjalizacja aplikacji może zostać przerwana. Nie jest to
dzisiejsza regresja produkcyjna tylko dlatego, że integracja Priority 7 nie została
wydana, ale nie wolno traktować precache helpera jako opcjonalnego ulepszenia.

Correction pass celowo nie zmienia `sw.js`: helper i autoryzowany runtime muszą wejść
razem z numerem nowej generacji w rzeczywistym atomowym pakiecie. Phase 3F-A nie
przypina już helpera poza SW; nowa asercja A2 w release-loader suite sprawdza wyłącznie
brak realnego `content/verb-patterns.json`. Nie zmienia to pre-existing testów, które
kodują dokładny dzisiejszy inwentarz SW — m.in. `tests/test_priority7_phase3d1.py`,
`tests/test_priority7_patterns_ui.js` i `tests/test_phase4b1_service_worker_cache.js`.
Te testy będą zgodnie wymagały aktualizacji dopiero w rzeczywistym atomowym pakiecie
razem z `sw.js`; nie zostały teraz przedwcześnie rozluźnione.

## 4. Uśpiony loader

W `pp-verb-patterns.js` dodano:

```text
loadRuntimeDocument(request, url)
```

Granica jest celowo mała:

- otrzymuje funkcję podobną do `fetch` i URL jako zależności;
- wykonuje najwyżej jedno `request(url, { cache: "no-store" })`;
- wymaga dokładnie `response.ok === true`;
- wymaga asynchronicznego `response.json()`;
- przekazuje cały dokument do istniejącej walidacji publicznego kontraktu;
- zawsze zwraca `Promise<boolean>`: każda awaria rozstrzyga się do `false`, a sukces
  do `true`, bez wyjątku na zewnątrz, retry, timera, logowania, DOM, storage lub
  własnego komunikatu błędu;
- nie zna ścieżki produkcyjnego runtime i nie sięga po globalny `fetch`;
- ewaluacja modułu nie wykonuje sieci, a `index.html` nie ma callsite'u.

Przyjmowanie jest teraz atomowe dla całego kandydata. Niepoprawny lemma, meaning
lub pattern odrzuca cały dokument; nic nie jest częściowo przycinane. Nowy stan
jest budowany przed zmianą `STATE`. Po udanym przyjęciu publiczne rekordy są
kopiowane, więc późniejsza mutacja obiektu przekazanego przez wywołującego nie może
po cichu zmienić widoków. Nieudany reload zachowuje ostatni poprawny stan w pamięci;
nieudany pierwszy load pozostawia neutralny stan niedostępności.

To zaostrza wcześniejszy opis Phase 3A, który dopuszczał per-entity pruning.
**Jeden malformed pattern unieważnia cały publiczny kandydat runtime**, więc ekran
Verb Patterns pozostaje niedostępny albo zachowuje poprzedni poprawny runtime zamiast
przyjąć poprawne sibling patterns. Jest to świadomy koszt bezpieczeństwa atomowego
release: częściowe przyjęcie nie pozwala odróżnić kompletnego publicznego artefaktu
od jego przypadkowo ocalałego fragmentu.

Loader jest przeznaczony do jednego wywołania na starcie. Nakładające się wywołania
nie mają koordynacji i obowiązuje last-to-settle. Przyszła integracja musi wykonać
jedno ładowanie, bez ręcznego/background refresh i retry. Jeżeli kiedykolwiek powstaną
wielokrotne loady, najpierw trzeba dodać generation/in-flight guard.

## 5. Syntetyczny runtime

`tests/fixtures/priority7/release-runtime-fixture.json` jest surowym dokumentem
publicznym, nie opakowaniem. Ma dokładnie trzy pola najwyższego poziomu:

- `formatVersion: 1`;
- `patternDataRevision: 424242`;
- `lemmas`.

Zawiera tylko dwa jawnie wymyślone, niepolskie lemmas: `quuxify` i `zorbulate`,
dwa patterns oraz widoczne ciągi `TEST-ONLY`. Ma puste listy
`activityEligibility` i zero przykładów z `audioEligible: true`. Nie zawiera
statusów artefaktu, review, dowodów, rejestrów, autorów, reviewerów ani żadnego
z 26 prywatnych kluczy blokowanych przez runtime.

Fixture przechodzi dokładnie ten sam publiczny walidator:

```text
python3 priority7_tooling.py validate-runtime \
  tests/fixtures/priority7/release-runtime-fixture.json --repository-root .
```

Nie znajduje się w `content/`, `grammar/`, `vocabulary/`, `guide/`, manifeście,
sitemapie, `index.html` ani `sw.js`. Nie jest dostępny przez zwykły start aplikacji.

## 6. Macierz próby syntetycznej

| Warunek | Oczekiwane zachowanie | Wynik |
|---|---|---|
| Poprawna odpowiedź 200 + poprawny JSON | Jeden request, pełna walidacja, atomowa aktywacja, 2 lemmas / 2 patterns | PASS |
| Rzut synchroniczny transportu | `false`, brak retry, stan neutralny lub ostatni poprawny | PASS |
| Odrzucona Promise sieci | Jak wyżej | PASS |
| HTTP 404 / 500 | Odrzucenie przed parsowaniem | PASS |
| `ok` inne niż Boolean `true` | Odrzucenie | PASS |
| Brak `json()`, rzut parsera lub odrzucona Promise JSON | Odrzucenie | PASS |
| Nieasynchroniczna odpowiedź albo body | Odrzucenie; brak testowej ścieżki specjalnej | PASS |
| Zły typ top-level, brak pola lub obce pole envelope | Odrzucenie całego dokumentu | PASS |
| Puste `lemmas` | Odrzucenie; kontrakt wymaga co najmniej jednego lemma | PASS |
| Niepoprawny lemma / meaning / pattern lub obce pole zagnieżdżone | Odrzucenie całego dokumentu, bez pruning | PASS |
| Dowolny z 26 prywatnych kluczy na dowolnej głębokości | Odrzucenie całego dokumentu | PASS |
| Pole redakcyjne/autoryzacyjne w root | Odrzucenie przez zamknięty envelope | PASS |
| Nieudany pierwszy load | Neutralny ekran niedostępności, bez częściowego widoku | PASS |
| Nieudany reload po poprawnym loadzie | Ostatni poprawny stan pozostaje niezmieniony | PASS |
| Kolejny poprawny load | Cały stary stan zastąpiony całym nowym stanem | PASS |
| Mutacja wejścia po accept | Brak wpływu na przyjęte widoki | PASS |
| Niższa dodatnia rewizja | Przyjęta, jeśli dokument jest poprawny; browser nie jest autorytetem monotoniczności | PASS |
| Wrogie znaczniki HTML w ciągach | Pozostają tekstem w shippingowym rendererze | PASS |
| Filtr bez wyniku | Prawdziwy stan zero, bez powrotu do All | PASS |
| Każda gałąź loadera | Natywny Promise/thenable rozstrzygający się do Boolean | PASS w JXA i prawdziwej przeglądarce |

Próba renderuje syntetyczny indeks, filtr, widok lemma i stan zero przez istniejące
funkcje aplikacji oraz fake DOM. Nie powstał drugi renderer ani alternatywny loader.

## 7. Semantyka pustych danych, awarii i rewizji

W bieżącym publicznym kontrakcie `lemmas: []` nie jest poprawnym pustym runtime.
Test nie przedstawia go jako sukcesu. Rozróżnienie jest następujące:

- brak pierwszego dokumentu, błąd sieci lub niepoprawny dokument — neutralne
  „unavailable”, zero wierszy i filtrów;
- poprawny dokument, ale wspierany filtr bez trafień — dostępny ekran i prawdziwy
  wynik zero;
- awaria po wcześniejszym poprawnym loadzie — zachowanie ostatniego poprawnego
  stanu tylko w pamięci bieżącej strony.

Browser sprawdza, że `patternDataRevision` jest dodatnią liczbą całkowitą. Nie
porównuje jej z poprzednią, nie zapisuje jej i nie uznaje za dowód autoryzacji.
Monotoniczność należy do procesu build/release: `freeze_editorial` wymaga rewizji 1
dla pierwszego wydania, a później zwiększenia o 1 wtedy i tylko wtedy, gdy zmienił
się publiczny payload bez pola rewizji. Dlatego rollback również nie powinien
obniżać rewizji; powinien publikować odtworzoną treść jako nową rewizję.

## 8. Decyzja dotycząca cache i offline

Przyszły `content/verb-patterns.json` musi być:

1. wymaganym zasobem instalacyjnym razem z `pp-verb-patterns.js`, co jednocześnie
   naprawia opisany wyżej obecny defekt offline helpera;
2. obsługiwany cache-first w numerowanej generacji shell;
3. aktualizowany wyłącznie wraz ze zmianą generacji `CACHE`.

To jest świadoma korekta wcześniejszej rekomendacji Phase 3A „required precache +
network-first runtime”. Obecny worker pozwala zasobowi network-first zmienić się
wewnątrz generacji, więc stary JavaScript mógłby zobaczyć nowy runtime. Cache-first
wiąże helper, shell i JSON z jedną generacją. `patternDataRevision` zachowuje własną
semantykę redakcyjną; nie musi mieć tego samego numeru co `APP_VERSION` lub `CACHE`,
ale każda publikacja runtime musi utworzyć nową generację cache.

`AUDIO_CACHE` pozostaje niezależny. Priority 7 nie ma obecnie zaakceptowanego audio,
więc nie należy go ruszać w pierwszym wydaniu wzorców.

| Sytuacja | Zachowanie docelowe |
|---|---|
| Pierwsza wizyta bez sieci i bez zainstalowanego shell | Aplikacja nie może obiecać dostępności; normalna awaria nawigacji |
| Pierwsza wizyta online | Nowy worker instaluje helper i runtime jako required; loader przyjmuje tylko cały poprawny dokument |
| Późniejszy start offline | Helper i runtime pochodzą z tej samej generacji cache; wzorce są dostępne |
| Runtime brakujący podczas instalacji | Instalacja nowej generacji upada, niepełny cache jest usuwany, stary worker pozostaje |
| Runtime uszkodzony lub prywatny | Loader odrzuca go w całości; ekran neutralny albo ostatni poprawny stan w bieżącej pamięci |
| Aktualizacja przy otwartej karcie | Nowy worker czeka; stary klient używa starej generacji; przejście następuje po zamknięciu starych klientów |
| Nowy shell zobaczony przez starego workera podczas publikacji | Callsite musi sprawdzać obecność metody; brak zgodnego helpera daje bezpieczne „unavailable”, nie wyjątek ani częściowy widok |

Walidacja odpowiedzi w workerze sprawdza status i media type, ale nie semantykę JSON.
Ostateczna walidacja zamkniętego kontraktu i blokada pól prywatnych muszą więc pozostać
w loaderze nawet po dodaniu precache.

## 9. Atomowy pakiet przyszłego wydania

Pierwszy rzeczywisty release nie może polegać na osobnym wdrażaniu plików. Jeden
commit i jeden artefakt wdrożeniowy muszą zawierać jednocześnie:

- zatwierdzony wynik projekcji `content/verb-patterns.json` i zapis jego
  kanonicznego hasha;
- `pp-verb-patterns.js` z loaderem i kontraktem odpowiadającym `formatVersion`;
- callsite w `index.html`, przekazujący jawny URL i `fetch`, z bezpiecznym
  feature-detection oraz bez retry/pollingu;
- wpisy obu plików w `REQUIRED_ASSETS` w `sw.js`;
- jawne sklasyfikowanie runtime jako cache-first zasobu generacji, nie jako
  network-first danych i nie jako unknown/network-only;
- nowy, nigdy wcześniej nieużyty numer `CACHE`;
- nowy `APP_VERSION`, bo pojawia się funkcja widoczna dla ucznia;
- testy kontraktu, instalacji, routingu, offline, wersji i kompletności pakietu;
- aktualizacje dokumentacji i raportu wydania.

Bez osobnej potrzeby nie zmieniają się: `AUDIO_CACHE`, schema i rewizja migracji,
format danych kart, wygenerowane strony ani sitemap.

Test `test_future_activation_is_guarded_as_one_atomic_dependency_bundle` jest celowo
warunkową przyszłą bramką. Dziś wymaga braku produkcyjnego runtime i callsite'u,
ale nie wymaga nieobecności helpera w SW. Gdy pojawia się call, ścieżka runtime,
plik runtime albo wpis workerowy, bramka wymaga poprawnego dokumentu, zgodnego
`formatVersion`, obu wymaganych zasobów SW i cache-first routingu.

Porównanie wersji jest wielowydaniowe i nie używa zamrożonych `8.10`/`v65`:

- kandydat w worktree, który zmienia komponent release, porównuje się z `HEAD`;
- czysty tree, w którym release commit jest już `HEAD`, porównuje się z `HEAD^`;
- późniejszy czysty commit niezwiązany z komponentami release nie wymusza fałszywego
  kolejnego bumpu.

Jeżeli aktywny kandydat zostanie uruchomiony poza checkoutem Git albo bez użytecznej
historii, test pomija porównanie release z jawnym komunikatem zamiast kończyć się
błędem technicznym. W normalnym repozytorium zachowanie i wymaganie bumpu pozostają
bez zmian.

`APP_VERSION` i numer `popolsku-vNN` muszą być większe od bezpośrednio poprzedniego
stanu. Osobny test tworzy syntetyczny pierwszy release `8.11`/`v66`, zmienia runtime
bez kolejnego bumpu i uzyskuje FAIL, a następnie przechodzi dla `8.12`/`v67`, zarówno
przed commitem (`HEAD`) jak i po czystym commicie (`HEAD^`). Nie ma związku równości
między `patternDataRevision`, `APP_VERSION` i numerem cache.

Bramka sprawdza semantykę, a nie jedną pisownię callsite'u: obecność wywołania,
ścieżki, poprawnego runtime, wymaganych wpisów SW, cache-first oraz postęp wersji.
Nie wymaga literalnego `loadRuntimeDocument(fetch, ...)` ani dokładnego formatowania
linii `sw.js`. Macierz mutacji A–F blokuje niepełne kombinacje z sekcji poniżej.

### Niedozwolone kombinacje

- **Loader bez runtime:** nowa instalacja SW nie może się zakończyć; przejściowy
  shell ma pozostać w neutralnym stanie.
- **Nowy runtime + stary JS:** starsza generacja cache nie może pobierać mutowalnego
  runtime z sieci; przy pierwszym wydaniu stary JS nie ma callsite'u.
- **Nowy shell + stary SW:** feature-detection zapobiega wywołaniu nieistniejącej
  metody; brak pełnego zestawu daje neutralny stan.
- **Nowy helper + stary runtime:** wspólna generacja cache i `formatVersion`
  zapobiegają niekontrolowanemu zestawieniu; niezgodność jest odrzucana.
- **Dokument częściowy, prywatny lub malformed:** cały kandydat jest odrzucany;
  ostatni poprawny stan nie jest czyszczony.
- **Nowa nazwa cache bez wymaganego zasobu:** instalacja upada i nie przejmuje
  klientów.

Sam atomowy commit nie dowodzi, że dowolny hosting publikuje pliki atomowo. Bramka
instalacyjna i bezpieczny callsite są dlatego nadal obowiązkowe. Weryfikacja
konkretnego pipeline'u hostingowego należy do fazy rzeczywistego wydania.

## 10. Rollback

Preferowany rollback jest nowym wdrożeniem pełnego, zgodnego pakietu, a nie ponownym
użyciem starej nazwy cache:

1. odtworzyć ostatnią znaną poprawną publiczną treść i zgodny shell/helper;
2. nadać nowy `patternDataRevision`, jeśli publiczny payload zmienia się względem
   ostatniego wydania;
3. nadać nowy, nieużywany `CACHE` i odpowiedni `APP_VERSION`;
4. uruchomić pełne bramki release;
5. wdrożyć jeden artefakt i pozwolić workerowi przejść przez zwykły stan waiting.

Gitowy revert może być podstawą zawartości, ale bezpośrednie cofnięcie do użytej już
nazwy `popolsku-vNN` ryzykuje kolizję z częściowo zachowanym cache. Roll-forward
rollback z nowym numerem generacji jest jednoznaczny. Brak `skipWaiting()` i
`clients.claim()` chroni otwarte sesje przed przejęciem w połowie użycia.

## 11. Ochrona przed wyciekiem i zakresem funkcji

- **Ochroną podstawową** są zamknięte zbiory kluczy envelope i każdego rekordu
  publicznego. Prywatna lub inna nieznana nazwa zostaje obecnie odrzucona przez tę
  walidację, zanim rekursywny sweep mógłby przesądzić wynik.
- Lista 26 prywatnych kluczy jest dokładnym cross-language odpowiednikiem
  `PRIVATE_RUNTIME_KEYS` z `priority7_tooling.py` i pozostaje celową, redundantną
  warstwą defence-in-depth. Test-only metoda `__holdsPrivateKeyForTest` bezpośrednio
  sprawdza wszystkie 26 nazw w zagnieżdżonym obiekcie, więc usunięcie lub zepsucie
  sweepu powoduje błąd niezależnie od zamkniętych validatorów. Metoda zwraca tylko
  Boolean, nie odczytuje/ujawnia private data i nie jest używana przez `index.html`.
- Envelope publiczny jest zamknięty: dokładnie `formatVersion`,
  `patternDataRevision`, `lemmas`; zamknięte są także rekordy zagnieżdżone.
- Syntetyczny fixture nie zawiera metadanych review, dowodów, autorów ani
  autoryzacji.
- Rzeczywisty korpus pozostaje poza przeglądarką: **45 patterns**, zbiór stanów
  `{research}`, **0 review events**, **0 activity-eligibility entries**,
  **0 audio-eligible examples**, brak exercise keys/IDs, puste rejestry reviewerów
  i autorów.
- Nie istnieje `content/verb-patterns.json` ani katalog produkcyjny `content/`.
- Loader nie zapisuje danych i nie emituje analityki. Nie dodano progress, mastery,
  scoringu, activity entry ani nowych identyfikatorów learner-facing.

Walidacja browserowa dowodzi poprawnego kształtu i bezpieczeństwa renderowania, nie
autoryzacji wydania. Autorytet pozostaje wyłącznie w narzędziach build-time i
prywatnych wejściach redakcyjnych.

## 12. Automatyczne bramki release

Przyszłe wydanie powinno zostać zablokowane, jeśli nie przejdzie dowolna z bramek:

1. zewnętrzna kontrola czystego, oczekiwanego Git baseline, zakresu zmian, remote i
   polityki push; te workflow facts nie są nietrwałym invariantem application suite;
2. zakończone reguły review/autoryzacji build-time;
3. `freeze_editorial` z poprawną monotoniczną rewizją i kanonicznym hashem;
4. `validate-runtime` na dokładnie przyszłym `content/verb-patterns.json`;
5. skan braku wszystkich prywatnych pól na każdej głębokości;
6. atomowa bramka zależności: runtime + helper + callsite + wymagany precache +
   `APP_VERSION` i `CACHE` większe od bezpośrednio poprzedniego stanu w jednym tree;
7. test instalacji z brakującym wymaganym zasobem i potwierdzeniem, że stary worker
   pozostaje aktywny;
8. test routingu cache-first i przejścia old-client/new-worker;
9. pełne Python, JXA, `validate_content.py`, `verify_audio.py`,
   `build_pages.py --check` i `git diff --check`;
10. testy rzeczywistej przeglądarki online → offline, aktualizacji i rollbacku na
    rzeczywistym artefakcie hostingowym;
11. porównanie dokładnej listy zmienionych plików z zaakceptowanym manifestem release.

## 13. Zmienione pliki

- `pp-verb-patterns.js` — uśpiony transport, atomowa walidacja całego kandydata,
  zachowanie ostatniego poprawnego stanu i odłączenie danych wejściowych.
- `tests/fixtures/priority7/release-runtime-fixture.json` — mały surowy publiczny
  runtime wyłącznie do próby.
- `tests/test_priority7_release_loader.js` — jednolity kontrakt Promise, macierz
  transportu, odpowiedzi, parsowania, prywatności, atomowości, rewizji i izolacji.
- `tests/test_priority7_patterns_ui.js` — shippingowy render syntetycznego runtime,
  failure retention, hostile text, zero-result i brak częściowego przyjęcia.
- `tests/test_priority7_phase3fa.py` — trwałe bramki startu, SW, poprzedniego stanu
  release, macierz A–F, drugi release, rzeczywisty korpus i atomowy pakiet; bez
  nietrwałych asercji HEAD/tree/dirty/remotes/push.
- `tests/test_priority7_phase2a.py`, `tests/test_priority7_phase3b.py`,
  `tests/test_priority7_phase3d1.py` — dokładne inwentarze fixture i wąskie
  oczekiwania transportu zaktualizowane o nowy test-only plik.
- `reports/priority-7-phase-3fa-summary.md` — niniejszy raport.

Nie zmieniono `index.html`, żadnego callsite'u startowego, Service Workera, danych,
manifestu, audio, migracji, wersji ani wygenerowanej strony. Zmiana produkcyjnego
helpera pozostaje uśpiona bez takiego callsite'u.

## 14. Testy i walidatory

Końcowe autorytatywne wyniki:

| Polecenie / zestaw | Wynik |
|---|---|
| `python3 -m unittest discover -s tests -p 'test_*.py'` | **354 testy, OK** |
| Wszystkie `tests/*.js` w JXA | **35 zestawów, 10 497 asercji, 0 błędów** |
| `python3 -m unittest tests.test_priority7_phase3fa` | **17 testów, OK** |
| `tests/test_priority7_release_loader.js` | **57 passed, 0 failed** |
| `tests/test_priority7_patterns_ui.js` | **438 passed, 0 failed** |
| `tests/test_priority7_choose_ui.js` | **327 passed, 0 failed** |
| `tests/test_grammar_interaction.js` | **616 passed, 0 failed** |
| `tests/test_phase3_closeout.js` | **510 passed, 0 failed** |
| `tests/test_phase3b_overlays.js` | **108 passed, 0 failed** |
| `tests/test_phase3b_focus_scroll.js` | **316 passed, 0 failed** |
| `tests/test_phase3b_mobile_layout.js` | **169 passed, 0 failed** |
| `tests/test_phase1a_accessibility.js` | **82 passed, 0 failed** |
| `tests/test_phase1b_keyboard_focus.js` | **214 passed, 0 failed** |
| `tests/test_phase2a_core_activity_accessibility.js` | **127 passed, 0 failed** |
| Committed-scratch: czysty tree po lokalnym scratch commitcie | **17 testów Phase 3F-A, OK** |
| Scratch: sam helper dodany do `REQUIRED_ASSETS`, runtime/callsite nadal nieobecne | **17 testów Phase 3F-A + 57 loader assertions, OK** |
| Release mutations A–F | **6/6 niepełnych pakietów zablokowanych; pełny pakiet PASS** |
| Drugi release | **niezmienione 8.11/v66 FAIL; 8.12/v67 PASS przed i po commicie** |
| Natywna przeglądarka: loader Promise | **6/6 gałęzi było `Promise`; 6/6 rozstrzygnęło Boolean** |
| `python3 validate_content.py` | **OK** — 10 poziomów, 97 tematów, 1 215 kart, 353 ćwiczenia, 1 675 ids; SHA-256 `2a71401d…` |
| `python3 verify_audio.py` | **OK** — 3 377 fraz / 3 377 wpisów manifestu / 3 377 MP3; zero orphanów |
| `python3 build_pages.py --check` | **OK** — 23 strony grammar + 6 vocabulary, guide hub, 32 URL-e sitemap, 380 pozycji audio |
| `git diff --check` | **OK** |

## 15. Ograniczenia

Główna próba transportu jest deterministyczna i nie wykonuje prawdziwej sieci. JXA
uruchamia shippingowy helper i renderer. Dodatkowa lokalna próba w prawdziwej
przeglądarce potwierdziła natywne `Promise<boolean>` dla braku requestu/URL, rzutu
synchronicznego, odrzucenia sieci, malformed response i sukcesu. Nie emulowała jednak
rzeczywistego cyklu życia Service Workera. Nie wykonano prawdziwego deploymentu,
instalacji online, odłączenia sieci, aktywacji workera, aktualizacji wielu kart ani
rollbacku hostingu. Nie użyto rzeczywistego runtime, gdyż jego utworzenie byłoby
naruszeniem granicy fazy.

Dlatego przyszłe zachowanie offline i atomowość pakietu są obecnie dowiedzione przez
kontrakty, istniejące testy SW i statyczne bramki przyszłej aktywacji, ale nadal
wymagają próby w prawdziwej przeglądarce na rzeczywistym artefakcie przed release.

## 16. Stan dostawy

Końcowy HEAD i tree pozostają baseline'em; zmiany są wyłącznie niezatwierdzonym
kandydatem Phase 3F-A w worktree. Remotes pozostają zero, `push.default` pozostaje
`nothing`. Nie wykonano commita, pushu, projekcji, publikacji ani zmiany wersji/cache.
