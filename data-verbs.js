/* Po polsku - lesson data: Verbs
   Registered onto window.PP_LEVELS by index.html (loaded in order).
   Safe to edit this file alone; a syntax error here shows a load
   message instead of breaking the app engine.

   Every topic carries kind:"grammar", so this whole level renders as its
   own practice tile ("Verbs") and each topic uses the teach+drills UI.

   Topics are ordered as a learning path (present -> reflexive -> aspect ->
   past -> future -> modals -> imperative -> motion); chips mark the CEFR
   step so learners can see the progression. */
(function(){
  window.PP_LEVELS = window.PP_LEVELS || [];
  window.PP_LEVELS.push(
    {
      level: "Verbs",
      blurb: "How verbs change",
      group: "grammar",
      topics: [

        /* 1 -------------------------------------------------- PRESENT TENSE */
        {
          name: "Czas teraźniejszy (Present tense)", emoji: "\uD83D\uDDE3\uFE0F", kind: "grammar", chip: "Verbs A1",
          desc: "Say what happens now - być and the four conjugation groups",
          teach: [
            { front:"What the present tense does",
              sub:"One Polish present covers English 'I do', 'I am doing' and 'I do do'.",
              points:[
                "There is no helper verb - the ending alone carries the person.",
                "You drop the subject pronoun when it is obvious: <i>Mieszkam w Warszawie.</i>",
                "Almost every verb falls into one of four ending patterns. Learn the pattern, not each verb."
              ],
              examples:[
                { pl:"Mieszkam w Warszawie.", en:"I live in Warsaw." },
                { pl:"Co robisz?", en:"What are you doing?" }
              ] },

            { front:"Start with być (to be)",
              sub:"It is irregular, but you will use it constantly - learn it as a chant.",
              table:[
                { g:"ja", e:"jestem", ex:"Jestem z Gruzji." },
                { g:"ty", e:"jesteś", ex:"Jesteś gotowy?" },
                { g:"on / ona / ono", e:"jest", ex:"Ona jest lekarką." },
                { g:"my", e:"jesteśmy", ex:"Jesteśmy w domu." },
                { g:"wy", e:"jesteście", ex:"Jesteście razem?" },
                { g:"oni / one", e:"są", ex:"Oni są z Polski." }
              ],
              examples:[ { pl:"Jestem głodny.", en:"I'm hungry." } ] },

            { front:"Group 1: -am / -asz (the easiest)",
              sub:"Most verbs ending in -ać go here. Predictable and friendly.",
              table:[
                { g:"ja", e:"mieszkam", ex:"Mieszkam tutaj." },
                { g:"ty", e:"mieszkasz", ex:"Gdzie mieszkasz?" },
                { g:"on / ona", e:"mieszka", ex:"On mieszka sam." },
                { g:"my", e:"mieszkamy", ex:"Mieszkamy w centrum." },
                { g:"wy", e:"mieszkacie", ex:"Mieszkacie blisko?" },
                { g:"oni / one", e:"mieszkają", ex:"Oni mieszkają razem." }
              ],
              explain:"Same pattern: <b>czytać</b> (czytam, czytasz...), <b>mieć</b> (mam, masz, ma, mamy, macie, mają).",
              examples:[ { pl:"Czytam książkę.", en:"I'm reading a book." } ] },

            { front:"Group 2: -ę / -isz",
              sub:"Many -ić / -yć verbs. The 'ja' form ends in the nasal -ę.",
              table:[
                { g:"ja", e:"robię", ex:"Co robię źle?" },
                { g:"ty", e:"robisz", ex:"Co robisz?" },
                { g:"on / ona", e:"robi", ex:"Ona robi kawę." },
                { g:"my", e:"robimy", ex:"Robimy projekt." },
                { g:"wy", e:"robicie", ex:"Co robicie?" },
                { g:"oni / one", e:"robią", ex:"Oni robią hałas." }
              ],
              explain:"Same pattern: <b>mówić</b> (mówię, mówisz...), <b>lubić</b> (lubię, lubisz...).",
              examples:[ { pl:"Mówię trochę po polsku.", en:"I speak a little Polish." } ] },

            { front:"Group 3: -ę / -esz",
              sub:"Often -ać or -ować verbs, but the stem changes - watch it.",
              table:[
                { g:"ja", e:"piszę", ex:"Piszę wiadomość." },
                { g:"ty", e:"piszesz", ex:"Do kogo piszesz?" },
                { g:"on / ona", e:"pisze", ex:"On pisze list." },
                { g:"my", e:"piszemy", ex:"Piszemy test." },
                { g:"wy", e:"piszecie", ex:"Piszecie po polsku?" },
                { g:"oni / one", e:"piszą", ex:"Oni piszą książkę." }
              ],
              note:"The stem often shifts (pisać → pisz-). Learn the 'ja' and 'ty' forms together and the rest follow.",
              examples:[ { pl:"Piszę e-mail do szefa.", en:"I'm writing an email to the boss." } ] },

            { front:"Group 4: -em / -esz (small but essential)",
              sub:"Only a handful of verbs use it - but they are ones you say daily.",
              table:[
                { g:"ja", e:"jem", ex:"Jem śniadanie." },
                { g:"ty", e:"jesz", ex:"Co jesz?" },
                { g:"on / ona", e:"je", ex:"On je zupę." },
                { g:"my", e:"jemy", ex:"Jemy razem." },
                { g:"wy", e:"jecie", ex:"Co jecie?" },
                { g:"oni / one", e:"jedzą", ex:"Oni jedzą obiad." }
              ],
              explain:"<b>wiedzieć</b> (wiem, wiesz, wie...) and <b>rozumieć</b> (rozumiem, rozumiesz...) follow the same pattern. You already met <b>nie wiem</b> and <b>nie rozumiem</b> in A1.",
              examples:[ { pl:"Nie wiem, gdzie to jest.", en:"I don't know where it is." } ] }
          ],
          drills: [
            { type:"choose", prompt:"Gdzie ty ___?", promptEn:"Where do you live?",
              options:["mieszkam","mieszkasz","mieszka"], answer:"mieszkasz",
              explain:"'ty' → -asz: mieszkasz.", full:"Gdzie mieszkasz?", fullEn:"Where do you live?" },
            { type:"choose", prompt:"Ja ___ po polsku.", promptEn:"I speak Polish.",
              options:["mówisz","mówię","mówi"], answer:"mówię",
              explain:"'ja' in the -ę/-isz group → -ę: mówię.", full:"Mówię po polsku.", fullEn:"I speak Polish." },
            { type:"choose", prompt:"Oni ___ w centrum.", promptEn:"They live in the centre.",
              options:["mieszkają","mieszkacie","mieszkamy"], answer:"mieszkają",
              explain:"'oni' → -ają in the -am/-asz group.", full:"Oni mieszkają w centrum.", fullEn:"They live in the centre." },
            { type:"choose", prompt:"___ głodny.", promptEn:"I'm hungry.",
              options:["Jesteś","Jestem","Jest"], answer:"Jestem",
              explain:"być, 'ja' form: jestem.", full:"Jestem głodny.", fullEn:"I'm hungry." },
            { type:"build", promptEn:"What are you doing?",
              answer:["Co","robisz"],
              explain:"'ty' form of robić is robisz.", full:"Co robisz?", fullEn:"What are you doing?" },
            { type:"choose", prompt:"My ___ projekt.", promptEn:"We're doing a project.",
              options:["robisz","robimy","robią"], answer:"robimy",
              explain:"'my' → -imy: robimy.", full:"Robimy projekt.", fullEn:"We're doing a project." },
            { type:"choose", prompt:"Nie ___, gdzie to jest.", promptEn:"I don't know where it is.",
              options:["wiesz","wiem","wie"], answer:"wiem",
              explain:"wiedzieć, 'ja' form: wiem (group 4).", full:"Nie wiem, gdzie to jest.", fullEn:"I don't know where it is." },
            { type:"build", promptEn:"We live in Warsaw.",
              answer:["Mieszkamy","w","Warszawie"],
              explain:"'my' form of mieszkać is mieszkamy; the pronoun drops.", full:"Mieszkamy w Warszawie.", fullEn:"We live in Warsaw." }
          ]
        },

        /* 2 ------------------------------------------------ REFLEXIVE VERBS */
        {
          name: "Czasowniki zwrotne (Reflexive verbs)", emoji: "\uD83D\uDD04", kind: "grammar", chip: "Verbs A1",
          desc: "The little word 'się' - and the everyday verbs that need it",
          teach: [
            { front:"What is 'się'?",
              sub:"Many common verbs carry a small partner word: się. Think of it as part of the verb.",
              points:[
                "You conjugate the verb normally and keep <b>się</b> alongside it.",
                "Sometimes it means '-self' (myć się = to wash oneself), but often it is just baked into the verb (nazywać się = to be called).",
                "You cannot translate <b>się</b> word-for-word - learn each verb together with it."
              ],
              examples:[
                { pl:"Jak się nazywasz?", en:"What's your name?" },
                { pl:"Uczę się polskiego.", en:"I'm learning Polish." }
              ] },

            { front:"nazywać się (to be called)",
              sub:"The verb changes for the person; się just tags along.",
              table:[
                { g:"ja", e:"nazywam się", ex:"Nazywam się Kai." },
                { g:"ty", e:"nazywasz się", ex:"Jak się nazywasz?" },
                { g:"on / ona", e:"nazywa się", ex:"Ona nazywa się Ada." },
                { g:"my", e:"nazywamy się", ex:"Nazywamy się Kowalscy." },
                { g:"wy", e:"nazywacie się", ex:"Jak się nazywacie?" },
                { g:"oni / one", e:"nazywają się", ex:"Oni nazywają się Nowak." }
              ],
              examples:[ { pl:"Nazywam się Anna.", en:"My name is Anna." } ] },

            { front:"Where does 'się' go?",
              sub:"It is flexible, with one firm rule.",
              points:[
                "<b>Się</b> sits right next to the verb - usually just before it, sometimes just after.",
                "The firm rule: <b>się</b> never starts a sentence or clause.",
                "In questions it usually slips in front of the verb: <i>Jak <b>się</b> masz?</i>, <i>Jak <b>się</b> czujesz?</i>"
              ],
              examples:[
                { pl:"Jak się czujesz?", en:"How do you feel?" },
                { pl:"Czuję się dobrze.", en:"I feel fine." }
              ] },

            { front:"Everyday reflexive verbs",
              sub:"These come up constantly - meet them as a set.",
              table:[
                { g:"uczyć się", e:"to learn", ex:"Uczę się polskiego." },
                { g:"czuć się", e:"to feel", ex:"Czuję się zmęczony." },
                { g:"nazywać się", e:"to be called", ex:"Nazywam się Kai." },
                { g:"spotykać się", e:"to meet", ex:"Spotykamy się o piątej." },
                { g:"cieszyć się", e:"to be glad", ex:"Cieszę się!" },
                { g:"spieszyć się", e:"to hurry", ex:"Spieszę się." }
              ],
              note:"After <b>uczyć się</b> the thing you learn takes the genitive: uczę się <b>polskiego</b>, uczę się <b>gramatyki</b>." }
          ],
          drills: [
            { type:"choose", prompt:"Jak ty ___ nazywasz?", promptEn:"What's your name?",
              options:["się","sobie","siebie"], answer:"się",
              explain:"The reflexive marker is 'się'.", full:"Jak się nazywasz?", fullEn:"What's your name?" },
            { type:"choose", prompt:"Ja ___ polskiego.", promptEn:"I'm learning Polish.",
              options:["uczysz się","uczę się","uczą się"], answer:"uczę się",
              explain:"'ja' form of uczyć się is uczę się.", full:"Uczę się polskiego.", fullEn:"I'm learning Polish." },
            { type:"choose", prompt:"Jak się ___?", promptEn:"How do you feel?",
              options:["czuję","czujesz","czuje"], answer:"czujesz",
              explain:"'ty' form of czuć się is czujesz się.", full:"Jak się czujesz?", fullEn:"How do you feel?" },
            { type:"build", promptEn:"My name is Anna.",
              answer:["Nazywam","się","Anna"],
              explain:"nazywać się, 'ja' form: nazywam się.", full:"Nazywam się Anna.", fullEn:"My name is Anna." },
            { type:"choose", prompt:"Uczę się ___.", promptEn:"I'm learning Polish.",
              options:["polski","polskiego","polsku"], answer:"polskiego",
              explain:"After uczyć się the object takes the genitive: polskiego.", full:"Uczę się polskiego.", fullEn:"I'm learning Polish." },
            { type:"build", promptEn:"We meet at five.",
              answer:["Spotykamy","się","o","piątej"],
              explain:"spotykać się, 'my' form: spotykamy się.", full:"Spotykamy się o piątej.", fullEn:"We meet at five." },
            { type:"choose", prompt:"Czuję ___ dobrze.", promptEn:"I feel fine.",
              options:["siebie","się","sobą"], answer:"się",
              explain:"czuć się always keeps 'się'.", full:"Czuję się dobrze.", fullEn:"I feel fine." }
          ]
        },

        /* 3 --------------------------------------------------------- ASPECT */
        {
          name: "Aspekt (Verb aspect)", emoji: "\u2696\uFE0F", kind: "grammar", chip: "Verbs A2",
          desc: "Why verbs come in pairs - process vs. finished result",
          teach: [
            { front:"The big idea: verbs come in pairs",
              sub:"This is the most important idea in Polish verbs. Take it slowly.",
              points:[
                "<b>Imperfective</b> = the process, a habit, or something ongoing. 'was doing', 'do regularly', 'am doing'.",
                "<b>Perfective</b> = one whole, finished action with a result. 'did', 'finished', 'got it done'.",
                "Most verbs have both: <b>robić / zrobić</b>, <b>pisać / napisać</b>. Same meaning, different lens."
              ],
              examples:[
                { pl:"Codziennie robię zakupy.", en:"I do the shopping every day. (habit)" },
                { pl:"Właśnie zrobiłem zakupy.", en:"I've just done the shopping. (finished)" }
              ] },

            { front:"Common aspect pairs",
              sub:"Learn verbs in pairs from now on - imperfective first, perfective second.",
              table:[
                { g:"do / make", e:"robić / zrobić", ex:"Zrobię to jutro." },
                { g:"write", e:"pisać / napisać", ex:"Napisałem list." },
                { g:"read", e:"czytać / przeczytać", ex:"Przeczytam to." },
                { g:"eat", e:"jeść / zjeść", ex:"Zjadłem obiad." },
                { g:"buy", e:"kupować / kupić", ex:"Kupiłem chleb." },
                { g:"say", e:"mówić / powiedzieć", ex:"Powiedz mi." }
              ],
              note:"Often the perfective just adds a prefix (na-, z-, prze-), but not always - <b>mówić / powiedzieć</b> is a whole new word. Memorise the tricky ones." },

            { front:"How to choose",
              sub:"Ask: process, or finished result?",
              points:[
                "Repeated or habitual → <b>imperfective</b>: <i>Zawsze czytam wieczorem.</i>",
                "Ongoing / in progress → <b>imperfective</b>: <i>Właśnie piszę e-mail.</i>",
                "One completed action / a result → <b>perfective</b>: <i>Napisałem e-mail.</i>",
                "Signal words: często, zwykle, codziennie → imperfective. już, wreszcie, nagle → perfective."
              ],
              examples:[
                { pl:"Zwykle piszę rano.", en:"I usually write in the morning." },
                { pl:"Już napisałem raport.", en:"I've already written the report." }
              ] },

            { front:"A key warning about the present",
              sub:"Perfective verbs have no present meaning.",
              points:[
                "A perfective verb cannot describe something happening right now - a finished action can't be 'in progress'.",
                "So the present-looking form of a perfective verb points to the <b>future</b>: <b>zrobię</b> = 'I will do (and finish)'.",
                "This is exactly what powers the future tense - you'll use it in the next topic."
              ],
              examples:[
                { pl:"Teraz robię zadanie.", en:"I'm doing the task now. (imperfective = present)" },
                { pl:"Jutro zrobię zadanie.", en:"I'll do the task tomorrow. (perfective = future)" }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"Codziennie ___ kawę rano.", promptEn:"I make coffee every morning.",
              options:["zrobię","robię","zrobiłem"], answer:"robię",
              explain:"'Codziennie' = a habit → imperfective robię.", full:"Codziennie robię kawę rano.", fullEn:"I make coffee every morning." },
            { type:"choose", prompt:"Wreszcie ___ ten raport.", promptEn:"I finally wrote that report.",
              options:["pisałem","napisałem","piszę"], answer:"napisałem",
              explain:"'Wreszcie' + one finished result → perfective napisałem.", full:"Wreszcie napisałem ten raport.", fullEn:"I finally wrote that report." },
            { type:"choose", prompt:"Jutro ___ zakupy.", promptEn:"I'll do the shopping tomorrow.",
              options:["robię","zrobię","robiłem"], answer:"zrobię",
              explain:"A single finished future action → perfective zrobię.", full:"Jutro zrobię zakupy.", fullEn:"I'll do the shopping tomorrow." },
            { type:"choose", prompt:"Zwykle ___ książki wieczorem.", promptEn:"I usually read books in the evening.",
              options:["przeczytam","czytam","przeczytałem"], answer:"czytam",
              explain:"'Zwykle' = habit → imperfective czytam.", full:"Zwykle czytam książki wieczorem.", fullEn:"I usually read books in the evening." },
            { type:"choose", prompt:"Właśnie ___ obiad, jestem najedzony.", promptEn:"I've just eaten lunch, I'm full.",
              options:["jem","zjadłem","jadłem"], answer:"zjadłem",
              explain:"Finished, with a result (full) → perfective zjadłem.", full:"Właśnie zjadłem obiad.", fullEn:"I've just eaten lunch." },
            { type:"build", promptEn:"Tell me. (one quick thing)",
              answer:["Powiedz","mi"],
              explain:"A single, complete request → perfective powiedzieć → powiedz.", full:"Powiedz mi.", fullEn:"Tell me." },
            { type:"choose", prompt:"Teraz ___ e-mail, poczekaj chwilę.", promptEn:"I'm writing an email right now, wait a moment.",
              options:["napiszę","piszę","napisałem"], answer:"piszę",
              explain:"In progress right now → imperfective piszę.", full:"Teraz piszę e-mail.", fullEn:"I'm writing an email right now." }
          ]
        },

        /* 4 ----------------------------------------------------- PAST TENSE */
        {
          name: "Czas przeszły (Past tense)", emoji: "\u23EA", kind: "grammar", chip: "Verbs A2",
          desc: "Talk about yesterday - with endings that match your gender",
          teach: [
            { front:"How the past is built",
              sub:"Take the infinitive, drop -ć, add -ł- plus an ending that shows person AND gender.",
              points:[
                "robić → robi<b>ł</b>- → robiłem (m) / robiłam (f).",
                "The gender ending matters even for 'I' and 'you' - a man says byłem, a woman byłam.",
                "Good news: perfective verbs form the past exactly the same way (zrobiłem, napisałam)."
              ],
              examples:[
                { pl:"Wczoraj byłem w kinie.", en:"Yesterday I was at the cinema. (man speaking)" },
                { pl:"Wczoraj byłam w kinie.", en:"Yesterday I was at the cinema. (woman speaking)" }
              ] },

            { front:"być in the past",
              sub:"The forms split by gender in the singular and by group in the plural.",
              table:[
                { g:"ja", e:"byłem / byłam", ex:"Byłem w domu." },
                { g:"ty", e:"byłeś / byłaś", ex:"Gdzie byłeś?" },
                { g:"on / ona / ono", e:"był / była / było", ex:"Ona była chora." },
                { g:"my", e:"byliśmy / byłyśmy", ex:"Byliśmy razem." },
                { g:"wy", e:"byliście / byłyście", ex:"Byliście tam?" },
                { g:"oni / one", e:"byli / były", ex:"Oni byli w pracy." }
              ],
              note:"Plural has two forms: use <b>-li</b> (byli, byliśmy) when at least one man is in the group, <b>-ły</b> (były, byłyśmy) for all-female or non-personal groups." },

            { front:"A regular verb: robić",
              sub:"Once you know być, every regular verb follows the same endings.",
              table:[
                { g:"ja", e:"robiłem / robiłam", ex:"Robiłem obiad." },
                { g:"ty", e:"robiłeś / robiłaś", ex:"Co robiłeś?" },
                { g:"on / ona", e:"robił / robiła", ex:"Ona robiła kawę." },
                { g:"my", e:"robiliśmy / robiłyśmy", ex:"Robiliśmy projekt." },
                { g:"wy", e:"robiliście / robiłyście", ex:"Co robiliście?" },
                { g:"oni / one", e:"robili / robiły", ex:"Oni robili hałas." }
              ] },

            { front:"Aspect in the past - the real payoff",
              sub:"This is where the aspect pairs earn their keep.",
              points:[
                "<b>Imperfective past</b> = was doing / used to do (no guarantee it finished): <i>Robiłem zadanie.</i>",
                "<b>Perfective past</b> = did it, finished it, got the result: <i>Zrobiłem zadanie.</i>",
                "Same sentence, different message: one describes the activity, the other reports the result."
              ],
              examples:[
                { pl:"Czytałem tę książkę.", en:"I was reading that book. (maybe unfinished)" },
                { pl:"Przeczytałem tę książkę.", en:"I read that book. (finished it)" }
              ] },

            { front:"A few irregular stems",
              sub:"Common verbs whose past stem shifts - worth memorising.",
              table:[
                { g:"iść (go)", e:"szedłem / szłam", ex:"Szedłem do domu." },
                { g:"mieć (have)", e:"miałem / miałam", ex:"Miałem czas." },
                { g:"jeść (eat)", e:"jadłem / jadłam", ex:"Jadłem obiad." }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"Wczoraj ___ w pracy. (mężczyzna)", promptEn:"Yesterday I was at work. (a man speaking)",
              options:["byłam","byłem","był"], answer:"byłem",
              explain:"A man says byłem; a woman byłam.", full:"Wczoraj byłem w pracy.", fullEn:"Yesterday I was at work." },
            { type:"choose", prompt:"Wczoraj ___ w pracy. (kobieta)", promptEn:"Yesterday I was at work. (a woman speaking)",
              options:["byłam","byłem","była"], answer:"byłam",
              explain:"A woman uses the -am ending: byłam.", full:"Wczoraj byłam w pracy.", fullEn:"Yesterday I was at work." },
            { type:"choose", prompt:"Ona ___ kawę.", promptEn:"She was making coffee.",
              options:["robił","robiła","robiłem"], answer:"robiła",
              explain:"'ona' → -ła: robiła.", full:"Ona robiła kawę.", fullEn:"She was making coffee." },
            { type:"choose", prompt:"___ całą książkę i wiem, jak się kończy.", promptEn:"I read the whole book and I know how it ends.",
              options:["Czytałem","Przeczytałem","Czytam"], answer:"Przeczytałem",
              explain:"Finished, with a result → perfective przeczytałem.", full:"Przeczytałem całą książkę.", fullEn:"I read the whole book." },
            { type:"build", promptEn:"We were together. (a mixed group)",
              answer:["Byliśmy","razem"],
              explain:"A group with at least one man → byliśmy (-li).", full:"Byliśmy razem.", fullEn:"We were together." },
            { type:"choose", prompt:"Oni ___ w kinie.", promptEn:"They were at the cinema.",
              options:["były","byliśmy","byli"], answer:"byli",
              explain:"'oni' (men / mixed) → byli.", full:"Oni byli w kinie.", fullEn:"They were at the cinema." },
            { type:"choose", prompt:"Wczoraj ___ do domu pieszo. (mężczyzna)", promptEn:"Yesterday I walked home. (a man speaking)",
              options:["szłam","szedłem","szedł"], answer:"szedłem",
              explain:"iść has an irregular past: szedłem (m) / szłam (f).", full:"Wczoraj szedłem do domu pieszo.", fullEn:"Yesterday I walked home." }
          ]
        },

        /* 5 --------------------------------------------------- FUTURE TENSE */
        {
          name: "Czas przyszły (Future tense)", emoji: "\u23E9", kind: "grammar", chip: "Verbs A2",
          desc: "Two futures - and aspect decides which one you use",
          teach: [
            { front:"First, the future of być",
              sub:"You need these forms for the ongoing future - learn them like the present.",
              table:[
                { g:"ja", e:"będę", ex:"Będę w domu." },
                { g:"ty", e:"będziesz", ex:"Będziesz tam?" },
                { g:"on / ona", e:"będzie", ex:"Ona będzie później." },
                { g:"my", e:"będziemy", ex:"Będziemy razem." },
                { g:"wy", e:"będziecie", ex:"Będziecie gotowi?" },
                { g:"oni / one", e:"będą", ex:"Oni będą jutro." }
              ],
              examples:[ { pl:"Jutro będę w pracy.", en:"Tomorrow I'll be at work." } ] },

            { front:"Future 1: ongoing (imperfective)",
              sub:"For a future action seen as a process or a habit.",
              points:[
                "Take <b>będę / będziesz...</b> and add the <b>imperfective infinitive</b>: <i>będę robić</i>.",
                "You can also use the -ł form: <i>będę robił / będę robiła</i> - both are correct and common.",
                "Use it for 'will be doing', 'will do (repeatedly)'."
              ],
              examples:[
                { pl:"Jutro będę pracować.", en:"Tomorrow I'll be working." },
                { pl:"Będę się uczyć polskiego.", en:"I'll be studying Polish." }
              ] },

            { front:"Future 2: finished (perfective)",
              sub:"No będę needed - the verb does it alone.",
              points:[
                "Remember the warning from aspect: a perfective verb's present-looking form points to the future.",
                "So <b>zrobię</b> already means 'I will do (and finish)'. Just conjugate the perfective verb.",
                "Use it for one completed future action with a result."
              ],
              examples:[
                { pl:"Jutro zrobię to zadanie.", en:"I'll do (and finish) that task tomorrow." },
                { pl:"Napiszę do ciebie wieczorem.", en:"I'll write to you in the evening." }
              ] },

            { front:"Which future do I use?",
              sub:"Same question as always - process or finished result?",
              table:[
                { g:"process / habit", e:"będę + verb", ex:"Będę czytać wieczorem." },
                { g:"one finished result", e:"perfective", ex:"Przeczytam to dziś." },
                { g:"ongoing state", e:"będę być → będę", ex:"Będę w domu." }
              ],
              note:"Compare: <b>Będę się uczyć</b> (I'll be studying, ongoing) vs <b>Nauczę się</b> (I'll learn it / master it, finished)." }
          ],
          drills: [
            { type:"choose", prompt:"Jutro ___ w domu.", promptEn:"Tomorrow I'll be at home.",
              options:["jestem","będę","byłem"], answer:"będę",
              explain:"Future of być, 'ja': będę.", full:"Jutro będę w domu.", fullEn:"Tomorrow I'll be at home." },
            { type:"choose", prompt:"Wieczorem ___ pracować.", promptEn:"In the evening I'll be working.",
              options:["będę","zrobię","jestem"], answer:"będę",
              explain:"Ongoing future = będę + imperfective infinitive.", full:"Wieczorem będę pracować.", fullEn:"In the evening I'll be working." },
            { type:"choose", prompt:"Jutro ___ to zadanie i skończę.", promptEn:"Tomorrow I'll do (and finish) that task.",
              options:["będę robić","zrobię","robię"], answer:"zrobię",
              explain:"One finished result → perfective zrobię (no będę).", full:"Jutro zrobię to zadanie.", fullEn:"Tomorrow I'll do that task." },
            { type:"choose", prompt:"Ona ___ później.", promptEn:"She'll be here later.",
              options:["będą","będzie","będziesz"], answer:"będzie",
              explain:"Future of być, 'ona': będzie.", full:"Ona będzie później.", fullEn:"She'll be here later." },
            { type:"build", promptEn:"I'll write to you in the evening. (one message)",
              answer:["Napiszę","do","ciebie","wieczorem"],
              explain:"A single finished action → perfective napiszę.", full:"Napiszę do ciebie wieczorem.", fullEn:"I'll write to you in the evening." },
            { type:"choose", prompt:"Cały weekend ___ się uczyć.", promptEn:"All weekend I'll be studying.",
              options:["nauczę","będę","będzie"], answer:"będę",
              explain:"Ongoing, all weekend → będę + uczyć się.", full:"Cały weekend będę się uczyć.", fullEn:"All weekend I'll be studying." },
            { type:"choose", prompt:"My ___ jutro gotowi.", promptEn:"We'll be ready tomorrow.",
              options:["będziemy","będziecie","będą"], answer:"będziemy",
              explain:"Future of być, 'my': będziemy.", full:"Będziemy jutro gotowi.", fullEn:"We'll be ready tomorrow." }
          ]
        },

        /* 6 -------------------------------------------------- MODAL VERBS */
        {
          name: "Czasowniki modalne (Modal verbs)", emoji: "\uD83D\uDCAD", kind: "grammar", chip: "Verbs A2",
          desc: "Can, must, want, should - each followed by the infinitive",
          teach: [
            { front:"How modals work",
              sub:"A modal verb sets the mood; a second verb (infinitive) says the action.",
              points:[
                "Pattern: <b>modal (conjugated) + infinitive</b>. <i>Muszę iść.</i> = I must go.",
                "Only the modal changes for the person; the second verb stays in the infinitive.",
                "The four you need first: <b>móc</b> (can), <b>musieć</b> (must), <b>chcieć</b> (want), <b>powinien</b> (should)."
              ],
              examples:[
                { pl:"Muszę już iść.", en:"I have to go now." },
                { pl:"Chcę odpocząć.", en:"I want to rest." }
              ] },

            { front:"móc (can / to be able)",
              sub:"Also the polite 'may I...?': Czy mogę...?",
              table:[
                { g:"ja", e:"mogę", ex:"Mogę ci pomóc." },
                { g:"ty", e:"możesz", ex:"Możesz mi pomóc?" },
                { g:"on / ona", e:"może", ex:"On może przyjść." },
                { g:"my", e:"możemy", ex:"Możemy iść." },
                { g:"wy", e:"możecie", ex:"Możecie poczekać?" },
                { g:"oni / one", e:"mogą", ex:"Oni mogą zostać." }
              ],
              examples:[ { pl:"Czy mogę zapłacić kartą?", en:"Can I pay by card?" } ] },

            { front:"musieć (must) and chcieć (want)",
              sub:"Two more you'll use every day.",
              table:[
                { g:"muszę / chcę", e:"I must / want", ex:"Muszę iść. Chcę spać." },
                { g:"musisz / chcesz", e:"you must / want", ex:"Musisz odpocząć." },
                { g:"musi / chce", e:"he-she must / wants", ex:"Ona chce kawę." },
                { g:"musimy / chcemy", e:"we must / want", ex:"Musimy się spieszyć." },
                { g:"musicie / chcecie", e:"you must / want", ex:"Chcecie zostać?" },
                { g:"muszą / chcą", e:"they must / want", ex:"Oni chcą pomóc." }
              ],
              note:"<b>chcieć</b> can also take a noun object: <i>Chcę kawę.</i> (I want a coffee.)" },

            { front:"powinien (should) and impersonal modals",
              sub:"'Should' changes for gender; a few handy impersonals need no subject.",
              points:[
                "<b>powinien</b>: powinienem / powinnam (m/f), powinieneś / powinnaś, powinien / powinna + infinitive.",
                "<b>trzeba</b> + infinitive = 'one needs to / it's necessary': <i>Trzeba iść.</i>",
                "<b>można</b> + infinitive = 'one can / it's allowed': <i>Czy można tu palić?</i>",
                "<b>wolno</b> = 'is permitted': <i>Nie wolno tu parkować.</i>"
              ],
              examples:[
                { pl:"Powinieneś odpocząć.", en:"You should rest." },
                { pl:"Trzeba kupić bilet.", en:"You need to buy a ticket." }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"___ ci pomóc?", promptEn:"Can I help you?",
              options:["Mogę","Możesz","Muszę"], answer:"Mogę",
              explain:"'ja' form of móc: mogę.", full:"Mogę ci pomóc?", fullEn:"Can I help you?" },
            { type:"choose", prompt:"Muszę już ___.", promptEn:"I have to go now.",
              options:["idę","iść","poszedłem"], answer:"iść",
              explain:"After a modal the second verb stays in the infinitive: iść.", full:"Muszę już iść.", fullEn:"I have to go now." },
            { type:"choose", prompt:"Czy ___ zapłacić kartą?", promptEn:"Can I pay by card?",
              options:["mogę","może","mogą"], answer:"mogę",
              explain:"Polite 'may I' uses móc, 'ja' → mogę.", full:"Czy mogę zapłacić kartą?", fullEn:"Can I pay by card?" },
            { type:"choose", prompt:"Ona ___ odpocząć.", promptEn:"She wants to rest.",
              options:["chcę","chce","chcą"], answer:"chce",
              explain:"chcieć, 'ona' form: chce.", full:"Ona chce odpocząć.", fullEn:"She wants to rest." },
            { type:"build", promptEn:"We have to hurry.",
              answer:["Musimy","się","spieszyć"],
              explain:"musieć 'my' → musimy, + reflexive spieszyć się.", full:"Musimy się spieszyć.", fullEn:"We have to hurry." },
            { type:"choose", prompt:"___ odpocząć. (rada dla mężczyzny)", promptEn:"You should rest. (advice to a man)",
              options:["Powinnaś","Powinieneś","Powinien"], answer:"Powinieneś",
              explain:"powinien, 'ty' masculine: powinieneś.", full:"Powinieneś odpocząć.", fullEn:"You should rest." },
            { type:"choose", prompt:"___ kupić bilet.", promptEn:"You need to buy a ticket.",
              options:["Trzeba","Chcę","Mogę"], answer:"Trzeba",
              explain:"Impersonal 'one needs to' = trzeba + infinitive.", full:"Trzeba kupić bilet.", fullEn:"You need to buy a ticket." }
          ]
        },

        /* 7 --------------------------------------------------- IMPERATIVE */
        {
          name: "Tryb rozkazujący (Imperative)", emoji: "\uD83D\uDCE3", kind: "grammar", chip: "Verbs A2",
          desc: "Giving instructions, asking, and telling someone not to",
          teach: [
            { front:"What the imperative does",
              sub:"It tells someone to do (or not do) something - instructions, requests, encouragement.",
              points:[
                "It has forms for <b>ty</b> (rób!), <b>my</b> (róbmy! = let's), and <b>wy</b> (róbcie!).",
                "There is no 'ja' imperative - you don't command yourself.",
                "For polite requests to strangers, Polish usually avoids the bare command (see the last card)."
              ],
              examples:[
                { pl:"Chodź tutaj!", en:"Come here!" },
                { pl:"Poczekaj chwilę.", en:"Wait a moment." }
              ] },

            { front:"Forming the ty command",
              sub:"Start from the 'on / ona' present form and trim it.",
              table:[
                { g:"robić", e:"rób", ex:"Rób to powoli." },
                { g:"pisać", e:"pisz", ex:"Pisz wyraźnie." },
                { g:"iść", e:"idź", ex:"Idź prosto." },
                { g:"czekać", e:"czekaj", ex:"Czekaj tutaj." },
                { g:"być", e:"bądź", ex:"Bądź cierpliwy." }
              ],
              note:"Rough rule: take the 'on/ona' form (robi, pisze) and cut the ending → rób, pisz. Verbs like czekać keep -aj (czekaj)." },

            { front:"my and wy commands",
              sub:"Add -my for 'let's' and -cie for plural 'you'.",
              table:[
                { g:"ty", e:"zrób", ex:"Zrób to teraz." },
                { g:"my (let's)", e:"zróbmy", ex:"Zróbmy przerwę." },
                { g:"wy", e:"zróbcie", ex:"Zróbcie to razem." }
              ],
              examples:[ { pl:"Chodźmy do domu.", en:"Let's go home." } ] },

            { front:"Aspect flips the meaning",
              sub:"A subtle but important pattern in commands.",
              points:[
                "A positive command is usually <b>perfective</b> - do it and finish: <i>Zrób to!</i>",
                "A negative command is usually <b>imperfective</b> - don't (be) doing it: <i>Nie rób tego!</i>",
                "So the pair often flips: <b>Zamknij okno!</b> (close it) vs <b>Nie zamykaj okna!</b> (don't close it)."
              ],
              examples:[
                { pl:"Nie martw się.", en:"Don't worry." },
                { pl:"Zadzwoń do mnie.", en:"Call me." }
              ] },

            { front:"The polite way",
              sub:"To strangers, soften the command - Poles rarely bark orders.",
              points:[
                "<b>Proszę</b> + infinitive is the everyday polite form: <i>Proszę usiąść.</i> (Please sit down.)",
                "<b>Proszę</b> alone softens almost anything: <i>Proszę poczekać.</i>",
                "Bare commands (rób, chodź) are for friends, family, and children."
              ],
              examples:[
                { pl:"Proszę wejść.", en:"Please come in." },
                { pl:"Proszę mówić wolniej.", en:"Please speak more slowly." }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"___ tutaj! (do kolegi)", promptEn:"Come here! (to a friend)",
              options:["Chodź","Chodzę","Chodzisz"], answer:"Chodź",
              explain:"ty command of chodzić: chodź.", full:"Chodź tutaj!", fullEn:"Come here!" },
            { type:"choose", prompt:"___ chwilę.", promptEn:"Wait a moment.",
              options:["Czekasz","Poczekaj","Czekam"], answer:"Poczekaj",
              explain:"Command from poczekać: poczekaj.", full:"Poczekaj chwilę.", fullEn:"Wait a moment." },
            { type:"choose", prompt:"Nie ___ się, wszystko będzie dobrze.", promptEn:"Don't worry, everything will be fine.",
              options:["martw","zmartw","martwię"], answer:"martw",
              explain:"Negative command → imperfective: nie martw się.", full:"Nie martw się.", fullEn:"Don't worry." },
            { type:"build", promptEn:"Let's take a break.",
              answer:["Zróbmy","przerwę"],
              explain:"'let's' adds -my: zróbmy.", full:"Zróbmy przerwę.", fullEn:"Let's take a break." },
            { type:"choose", prompt:"___ usiąść. (uprzejmie)", promptEn:"Please sit down. (politely)",
              options:["Siądź","Proszę","Siadaj"], answer:"Proszę",
              explain:"Polite form: Proszę + infinitive (usiąść).", full:"Proszę usiąść.", fullEn:"Please sit down." },
            { type:"choose", prompt:"___ do mnie wieczorem.", promptEn:"Call me in the evening.",
              options:["Dzwoń","Zadzwoń","Dzwonisz"], answer:"Zadzwoń",
              explain:"Positive command → perfective: zadzwoń.", full:"Zadzwoń do mnie wieczorem.", fullEn:"Call me in the evening." },
            { type:"build", promptEn:"Please speak more slowly.",
              answer:["Proszę","mówić","wolniej"],
              explain:"Proszę + infinitive mówić.", full:"Proszę mówić wolniej.", fullEn:"Please speak more slowly." }
          ]
        },

        /* 8 ------------------------------------------------ VERBS OF MOTION */
        {
          name: "Czasowniki ruchu (Verbs of motion)", emoji: "\uD83D\uDEB6", kind: "grammar", chip: "Verbs A2",
          desc: "iść vs chodzić, jechać vs jeździć - on foot or by vehicle, once or often",
          teach: [
            { front:"Two kinds of 'to go'",
              sub:"Polish splits motion two ways at once. Take it one axis at a time.",
              points:[
                "Axis 1 - <b>how</b>: on foot (<b>iść / chodzić</b>) vs by vehicle (<b>jechać / jeździć</b>).",
                "Axis 2 - <b>when</b>: one trip happening now (<b>iść, jechać</b>) vs habitual / general (<b>chodzić, jeździć</b>).",
                "So 'I go' has four flavours depending on foot-or-wheels and now-or-usually."
              ],
              examples:[
                { pl:"Idę do sklepu.", en:"I'm going to the shop. (on foot, now)" },
                { pl:"Codziennie chodzę do pracy.", en:"I go to work every day. (on foot, habit)" }
              ] },

            { front:"iść - going on foot, right now",
              sub:"One specific trip, one direction, happening now.",
              table:[
                { g:"ja", e:"idę", ex:"Idę do domu." },
                { g:"ty", e:"idziesz", ex:"Gdzie idziesz?" },
                { g:"on / ona", e:"idzie", ex:"Ona idzie do pracy." },
                { g:"my", e:"idziemy", ex:"Idziemy na kawę." },
                { g:"wy", e:"idziecie", ex:"Idziecie z nami?" },
                { g:"oni / one", e:"idą", ex:"Oni idą do parku." }
              ] },

            { front:"jechać - going by vehicle, right now",
              sub:"Same 'now, one trip' idea, but by bus, car, train...",
              table:[
                { g:"ja", e:"jadę", ex:"Jadę do Krakowa." },
                { g:"ty", e:"jedziesz", ex:"Czym jedziesz?" },
                { g:"on / ona", e:"jedzie", ex:"On jedzie autobusem." },
                { g:"my", e:"jedziemy", ex:"Jedziemy nad morze." },
                { g:"wy", e:"jedziecie", ex:"Dokąd jedziecie?" },
                { g:"oni / one", e:"jadą", ex:"Oni jadą pociągiem." }
              ],
              note:"The vehicle takes the instrumental: autobus<b>em</b>, pociągi<b>em</b>, samochod<b>em</b>." },

            { front:"chodzić / jeździć - habits and general truths",
              sub:"For repeated trips, no single direction: 'usually', 'often', 'every day'.",
              table:[
                { g:"chodzić (on foot)", e:"chodzę, chodzisz...", ex:"Chodzę na siłownię." },
                { g:"jeździć (by vehicle)", e:"jeżdżę, jeździsz...", ex:"Jeżdżę do pracy tramwajem." }
              ],
              examples:[
                { pl:"Często jeżdżę do Krakowa.", en:"I often go to Kraków." },
                { pl:"Dzieci chodzą do szkoły.", en:"The children go to school." }
              ] },

            { front:"Prefixes add direction (and finish the action)",
              sub:"Stick a prefix on iść to say exactly where the movement goes - these are perfective.",
              table:[
                { g:"pójść", e:"to set off", ex:"Muszę już pójść." },
                { g:"przyjść", e:"to arrive", ex:"Przyjdę o piątej." },
                { g:"wyjść", e:"to go out", ex:"Wyszedłem z domu." },
                { g:"wejść", e:"to go in", ex:"Wejdź, proszę." }
              ],
              note:"The same prefixes work on jechać: <b>przyjechać</b> (arrive by vehicle), <b>wyjechać</b> (leave / travel away)." }
          ],
          drills: [
            { type:"choose", prompt:"___ do sklepu, wrócę za chwilę.", promptEn:"I'm going to the shop, I'll be back soon.",
              options:["Chodzę","Idę","Jadę"], answer:"Idę",
              explain:"One trip on foot, now → idę.", full:"Idę do sklepu.", fullEn:"I'm going to the shop." },
            { type:"choose", prompt:"Codziennie ___ do pracy.", promptEn:"I go to work every day.",
              options:["idę","chodzę","jadę"], answer:"chodzę",
              explain:"'Codziennie' = habit on foot → chodzę.", full:"Codziennie chodzę do pracy.", fullEn:"I go to work every day." },
            { type:"choose", prompt:"Jutro ___ do Krakowa pociągiem.", promptEn:"Tomorrow I'm going to Kraków by train.",
              options:["idę","jeżdżę","jadę"], answer:"jadę",
              explain:"One trip by vehicle → jadę.", full:"Jutro jadę do Krakowa pociągiem.", fullEn:"Tomorrow I'm going to Kraków by train." },
            { type:"choose", prompt:"Często ___ do rodziny na weekend.", promptEn:"I often go to my family for the weekend.",
              options:["jadę","jeżdżę","idę"], answer:"jeżdżę",
              explain:"'Często' = habit by vehicle → jeżdżę.", full:"Często jeżdżę do rodziny na weekend.", fullEn:"I often go to my family for the weekend." },
            { type:"choose", prompt:"On jedzie ___.", promptEn:"He's going by bus.",
              options:["autobus","autobusem","autobusu"], answer:"autobusem",
              explain:"The vehicle takes the instrumental: autobusem.", full:"On jedzie autobusem.", fullEn:"He's going by bus." },
            { type:"build", promptEn:"Please come in.",
              answer:["Wejdź","proszę"],
              explain:"wejść (go in), ty command: wejdź.", full:"Wejdź, proszę.", fullEn:"Please come in." },
            { type:"choose", prompt:"___ o piątej, czekaj na mnie.", promptEn:"I'll arrive at five, wait for me.",
              options:["Idę","Przyjdę","Chodzę"], answer:"Przyjdę",
              explain:"Arrive (finished, future) → perfective przyjdę.", full:"Przyjdę o piątej.", fullEn:"I'll arrive at five." }
          ]
        }

      ]
    }
  );
})();
