/* Po polsku - lesson data: Grammar
   Registered onto window.PP_LEVELS by index.html (loaded in order).
   Safe to edit this file alone; a syntax error here shows a load
   message instead of breaking the app engine. */
(function(){
  window.PP_LEVELS = window.PP_LEVELS || [];
  window.PP_LEVELS.push(
  {
      level: "Grammar",
      blurb: "The 7 cases",
      topics: [
        {
          name: "Mianownik (Nominative)", emoji: "\uD83C\uDFC1", kind: "grammar",
          desc: "kto? co? - the subject / base form",
          teach: [
            { front:"Mianownik - kto? co? The subject.",
              sub:"The <b>base form</b> from the dictionary - the doer of the action.",
              points:[
                "The subject: <b>Kot śpi</b> (the cat sleeps)",
                "After <b>to jest</b>: To jest dom.",
                "Gender lives here: -a usually feminine, a consonant usually masculine, -o / -e neuter"
              ],
              examples:[
                { pl:"To jest mój dom.", en:"This is my house." },
                { pl:"Kawa jest gorąca.", en:"The coffee is hot." }
              ] },
            { front:"Three genders",
              table:[
                { g:"Masculine", e:"-", ex:"kot, dom, student" },
                { g:"Feminine", e:"-a", ex:"kawa, kobieta, książka" },
                { g:"Neuter", e:"-o / -e", ex:"okno, dziecko, mieszkanie" }
              ],
              note:"A few exceptions: <b>mężczyzna</b> (man) is masculine although it ends in -a.",
              examples:[ { pl:"Ten student jest miły.", en:"This student is nice." } ] },
            { front:"Nominative plural - the real change",
              answer:"student &rarr; studenci",
              explain:"Plurals: most nouns take <b>-y / -i</b> (kot &rarr; koty), neuter takes <b>-a</b> (okno &rarr; okna), and groups with men take a special <b>-i</b> (student &rarr; studenci).",
              examples:[
                { pl:"To są moje książki.", en:"These are my books." },
                { pl:"Studenci są tutaj.", en:"The students are here." }
              ] },
            { front:"The subject stays nominative.",
              sub:"Even when other words change case, the <b>subject</b> keeps its base form.",
              points:[
                "<b>Kot</b> śpi. (subject stays) vs Mam <b>kota</b>. (object changes)",
                "After <b>być</b> the job goes to instrumental, but the subject stays nominative"
              ],
              examples:[ { pl:"Mój brat jest studentem.", en:"My brother is a student." } ] }
          ],
          drills: [
            { type:"choose", prompt:"Na parkingu są nowe ___ .", promptEn:"There are new cars in the car park.",
              options:["samochody","samochód","samochodów"], answer:"samochody",
              explain:"Nominative plural &rarr; -y: samochód &rarr; samochody.", full:"Na parkingu są nowe samochody.", fullEn:"There are new cars in the car park." },
            { type:"choose", prompt:"To są duże ___ .", promptEn:"These are big windows.",
              options:["okna","okno","okien"], answer:"okna",
              explain:"Neuter plural &rarr; -a: okno &rarr; okna.", full:"To są duże okna.", fullEn:"These are big windows." },
            { type:"choose", prompt:"Ci ___ są mili.", promptEn:"These students are nice.",
              options:["studenci","studentów","studenty"], answer:"studenci",
              explain:"A plural group with men &rarr; -i: student &rarr; studenci.", full:"Ci studenci są mili.", fullEn:"These students are nice." },
            { type:"choose", prompt:"___ śpi na kanapie.", promptEn:"The cat is sleeping on the sofa.",
              options:["Kot","Kota","Kotem"], answer:"Kot",
              explain:"The subject stays in the nominative.", full:"Kot śpi na kanapie.", fullEn:"The cat is sleeping on the sofa." },
            { type:"choose", prompt:"To jest moja ___ .", promptEn:"This is my sister.",
              options:["siostra","siostrę","siostry"], answer:"siostra",
              explain:"After 'to jest', the noun stays nominative.", full:"To jest moja siostra.", fullEn:"This is my sister." },
            { type:"build", promptEn:"These are my books.",
              answer:["To","są","moje","książki"],
              explain:"Subjects stay nominative; plural książka &rarr; książki.", full:"To są moje książki.", fullEn:"These are my books." },
            { type:"choose", prompt:"Moja ___ jest w domu.", promptEn:"My mum is at home.",
              options:["mama","mamę","mamie"], answer:"mama",
              explain:"The subject is nominative: mama.", full:"Moja mama jest w domu.", fullEn:"My mum is at home." },
            { type:"choose", prompt:"Ten nowy ___ jest drogi.", promptEn:"This new phone is expensive.",
              options:["telefon","telefonu","telefonem"], answer:"telefon",
              explain:"The subject keeps its base nominative form.", full:"Ten nowy telefon jest drogi.", fullEn:"This new phone is expensive." },
            { type:"choose", prompt:"Te ___ są ładne.", promptEn:"These women are pretty.",
              options:["kobiety","kobieta","kobiet"], answer:"kobiety",
              explain:"Nominative plural &rarr; -y: kobieta &rarr; kobiety.", full:"Te kobiety są ładne.", fullEn:"These women are pretty." },
            { type:"build", promptEn:"My brother is a student.",
              answer:["Mój","brat","jest","studentem"],
              explain:"'brat' is the nominative subject; after być, studentem is instrumental.", full:"Mój brat jest studentem.", fullEn:"My brother is a student." }
          ]
        },
        {
          name: "Dopełniacz (Genitive)", emoji: "\uD83D\uDCE6", kind: "grammar",
          desc: "kogo? czego? - of, without, negation",
          teach: [
            { front:"Dopełniacz - 'of', and much more.",
              sub:"It answers <b>kogo?</b> / <b>czego?</b> and shows up everywhere.",
              points:[
                "Possession and 'of': <b>filiżanka kawy</b>",
                "After <b>bez, dla, do, od, z</b> (from), <b>u</b>",
                "Quantity: <b>dużo pracy</b>, <b>trochę czasu</b>",
                "Negation: <b>nie ma mleka</b>"
              ],
              examples:[
                { pl:"Poproszę kawę bez cukru.", en:"A coffee without sugar, please." },
                { pl:"Nie ma mleka w lodówce.", en:"There's no milk in the fridge." }
              ] },
            { front:"How do the endings change?",
              table:[
                { g:"Feminine", e:"-y / -i", ex:"kawa &rarr; kaw<b>y</b>" },
                { g:"Neuter", e:"-a", ex:"mleko &rarr; mlek<b>a</b>" },
                { g:"Masc. (a)", e:"-a", ex:"chleb &rarr; chleb<b>a</b>" },
                { g:"Masc. (u)", e:"-u", ex:"cukier &rarr; cukr<b>u</b>" }
              ],
              note:"Masculine <b>-a</b> vs <b>-u</b> is learned word by word.",
              examples:[ { pl:"Szukam dobrej kawy.", en:"I'm looking for good coffee." } ] },
            { front:"Negation flips the object to genitive.",
              answer:"Nie mam czasu.",
              explain:"After a <b>negated</b> verb, the accusative object becomes genitive: mam kawę &rarr; nie mam kawy.",
              examples:[
                { pl:"Nie mam czasu.", en:"I don't have time." },
                { pl:"Nie ma tu apteki.", en:"There's no pharmacy here." }
              ] },
            { front:"After bez / dla / do / z (from)",
              sub:"These prepositions <b>always</b> take the genitive.",
              points:[
                "<b>bez</b> cukru, <b>dla</b> mamy",
                "<b>do</b> domu, <b>z</b> Polski (from Poland)"
              ],
              examples:[
                { pl:"Idę do domu.", en:"I'm going home." },
                { pl:"To prezent dla mamy.", en:"This is a present for mum." }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"Poproszę kawę bez ___ .", promptEn:"A coffee without sugar, please.",
              options:["cukru","cukier","cukrem"], answer:"cukru",
              explain:"bez + genitive; cukier &rarr; cukru.", full:"Poproszę kawę bez cukru.", fullEn:"A coffee without sugar, please." },
            { type:"choose", prompt:"W lodówce nie ma ___ .", promptEn:"There's no milk in the fridge.",
              options:["mleka","mleko","mlekiem"], answer:"mleka",
              explain:"nie ma + genitive; neuter &rarr; -a.", full:"W lodówce nie ma mleka.", fullEn:"There's no milk in the fridge." },
            { type:"choose", prompt:"Nie mam ___ .", promptEn:"I don't have time.",
              options:["czasu","czas","czasem"], answer:"czasu",
              explain:"A negated object goes into the genitive; czas &rarr; czasu.", full:"Nie mam czasu.", fullEn:"I don't have time." },
            { type:"choose", prompt:"Szukam dobrej ___ .", promptEn:"I'm looking for good coffee.",
              options:["kawy","kawa","kawę"], answer:"kawy",
              explain:"szukać + genitive; kawa &rarr; kawy.", full:"Szukam dobrej kawy.", fullEn:"I'm looking for good coffee." },
            { type:"choose", prompt:"Wracam do ___ .", promptEn:"I'm going back home.",
              options:["domu","dom","domem"], answer:"domu",
              explain:"do + genitive; dom &rarr; domu.", full:"Wracam do domu.", fullEn:"I'm going back home." },
            { type:"build", promptEn:"There's no pharmacy here.",
              answer:["Nie","ma","tu","apteki"],
              explain:"nie ma + genitive; apteka &rarr; apteki.", full:"Nie ma tu apteki.", fullEn:"There's no pharmacy here." },
            { type:"choose", prompt:"To prezent dla ___ .", promptEn:"This is a present for mum.",
              options:["mamy","mama","mamę"], answer:"mamy",
              explain:"dla + genitive; mama &rarr; mamy.", full:"To prezent dla mamy.", fullEn:"This is a present for mum." },
            { type:"choose", prompt:"Mam dużo ___ .", promptEn:"I have a lot of work.",
              options:["pracy","praca","pracę"], answer:"pracy",
              explain:"dużo + genitive; praca &rarr; pracy.", full:"Mam dużo pracy.", fullEn:"I have a lot of work." },
            { type:"choose", prompt:"Jestem z ___ .", promptEn:"I'm from Poland.",
              options:["Polski","Polska","Polską"], answer:"Polski",
              explain:"z (from) + genitive; Polska &rarr; Polski.", full:"Jestem z Polski.", fullEn:"I'm from Poland." },
            { type:"build", promptEn:"I don't have time today.",
              answer:["Nie","mam","dzisiaj","czasu"],
              explain:"Negation &rarr; genitive: czas &rarr; czasu.", full:"Nie mam dzisiaj czasu.", fullEn:"I don't have time today." }
          ]
        },
        {
          name: "Celownik (Dative)", emoji: "\uD83C\uDF81", kind: "grammar",
          desc: "komu? czemu? - to / for someone",
          teach: [
            { front:"Celownik - komu? czemu? (to/for whom?)",
              sub:"The <b>receiver</b> - the indirect object.",
              points:[
                "After <b>dawać, pomagać, dziękować, mówić</b> (+ komuś)",
                "Impersonal feelings: <b>jest mi zimno</b>, <b>podoba mi się</b>",
                "Verbs that take it: pomagać, dziękować, ufać komuś"
              ],
              examples:[
                { pl:"Pomagam mamie w kuchni.", en:"I help mum in the kitchen." },
                { pl:"Jest mi zimno.", en:"I'm cold." }
              ] },
            { front:"How do the endings change?",
              table:[
                { g:"Masculine", e:"-owi", ex:"student &rarr; student<b>owi</b>" },
                { g:"Neuter", e:"-u", ex:"dziecko &rarr; dzieck<b>u</b>" },
                { g:"Feminine", e:"-e / -i", ex:"mama &rarr; mam<b>ie</b>" }
              ],
              note:"Feminine often changes the consonant: mama &rarr; mamie, siostra &rarr; siostrze.",
              examples:[ { pl:"Dziękuję lekarzowi.", en:"I thank the doctor." } ] },
            { front:"The little words: mi, ci, mu, jej, nam, im",
              answer:"Podoba mi się.",
              explain:"Dative pronouns appear constantly: <b>daj mi</b> (give me), <b>mówię ci</b> (I'm telling you), <b>pomagam mu</b> (I help him).",
              examples:[
                { pl:"Podoba mi się ten film.", en:"I like this film." },
                { pl:"Daj mi wodę.", en:"Give me water." }
              ] },
            { front:"Verbs that always take the dative.",
              sub:"In English these take a direct object, but Polish uses the dative.",
              points:[
                "<b>pomagać</b> komuś - to help someone",
                "<b>dziękować</b> komuś - to thank someone",
                "<b>ufać</b> komuś - to trust someone"
              ],
              examples:[
                { pl:"Dziękuję ci bardzo.", en:"Thank you very much." },
                { pl:"Ufam ci.", en:"I trust you." }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"Dziękuję ___ .", promptEn:"I thank the doctor.",
              options:["lekarzowi","lekarza","lekarzem"], answer:"lekarzowi",
              explain:"Masculine dative &rarr; -owi.", full:"Dziękuję lekarzowi.", fullEn:"I thank the doctor." },
            { type:"choose", prompt:"Podoba ___ się ten film.", promptEn:"I like this film.",
              options:["mi","ja","mną"], answer:"mi",
              explain:"podobać się + the dative pronoun 'mi'.", full:"Podoba mi się ten film.", fullEn:"I like this film." },
            { type:"choose", prompt:"Pomagam ___ .", promptEn:"I help my sister.",
              options:["siostrze","siostrę","siostry"], answer:"siostrze",
              explain:"Feminine dative: siostra &rarr; siostrze (r &rarr; rz).", full:"Pomagam siostrze.", fullEn:"I help my sister." },
            { type:"choose", prompt:"Dziękuję ___ bardzo.", promptEn:"Thank you very much.",
              options:["ci","cię","ciebie"], answer:"ci",
              explain:"dziękować + dative; 'you' = ci.", full:"Dziękuję ci bardzo.", fullEn:"Thank you very much." },
            { type:"choose", prompt:"Kupiłem ___ prezent.", promptEn:"I bought my son a present.",
              options:["synowi","syna","synem"], answer:"synowi",
              explain:"Masculine dative &rarr; -owi; the receiver of the gift.", full:"Kupiłem synowi prezent.", fullEn:"I bought my son a present." },
            { type:"build", promptEn:"I'm giving him a present.",
              answer:["Daję","mu","prezent"],
              explain:"mu = 'to him' (dative pronoun).", full:"Daję mu prezent.", fullEn:"I'm giving him a present." },
            { type:"choose", prompt:"Kupujemy prezent ___ .", promptEn:"We're buying a present for the child.",
              options:["dziecku","dziecko","dziecka"], answer:"dziecku",
              explain:"Neuter dative &rarr; -u: dziecko &rarr; dziecku.", full:"Kupujemy prezent dziecku.", fullEn:"We're buying a present for the child." },
            { type:"choose", prompt:"Jest ___ zimno.", promptEn:"I'm cold.",
              options:["mi","mną","ja"], answer:"mi",
              explain:"Impersonal feelings use the dative: jest mi zimno.", full:"Jest mi zimno.", fullEn:"I'm cold." },
            { type:"choose", prompt:"Ufam ___ .", promptEn:"I trust you.",
              options:["ci","cię","ty"], answer:"ci",
              explain:"ufać + dative.", full:"Ufam ci.", fullEn:"I trust you." },
            { type:"build", promptEn:"I help my mum in the kitchen.",
              answer:["Pomagam","mamie","w","kuchni"],
              explain:"pomagać + dative: mama &rarr; mamie.", full:"Pomagam mamie w kuchni.", fullEn:"I help my mum in the kitchen." }
          ]
        },
        {
          name: "Biernik (Accusative)", emoji: "\uD83C\uDFAF", kind: "grammar",
          desc: "kogo? co? - the direct object",
          teach: [
            { front:"Biernik - kogo? co? (whom? what?)",
              sub:"The <b>direct object</b> - what the action lands on.",
              points:[
                "After <b>lubić, mieć, jeść, pić, widzieć, kupować</b>",
                "Feminine <b>-a &rarr; -ę</b>: kawa &rarr; kawę",
                "Masculine inanimate: <b>no change</b> (mam bilet)",
                "Masculine animate &rarr; <b>-a</b> (mam psa, brata)"
              ],
              examples:[
                { pl:"Lubię czarną kawę.", en:"I like black coffee." },
                { pl:"Mam nowy telefon.", en:"I have a new phone." }
              ] },
            { front:"How do the endings change?",
              table:[
                { g:"Feminine", e:"-ę", ex:"kawa &rarr; kaw<b>ę</b>" },
                { g:"Masc. inanimate", e:"=", ex:"bilet &rarr; bilet" },
                { g:"Masc. animate", e:"-a", ex:"pies &rarr; ps<b>a</b>" },
                { g:"Neuter", e:"=", ex:"okno &rarr; okno" }
              ],
              note:"Adjectives agree: <b>czarną</b> kawę, <b>małego</b> psa.",
              examples:[ { pl:"Czytam ciekawą książkę.", en:"I'm reading an interesting book." } ] },
            { front:"Feminine: -a becomes -ę",
              answer:"Lubię kawę.",
              explain:"Feminine nouns swap <b>-a</b> for <b>-ę</b>: kawa &rarr; kawę, książka &rarr; książkę, herbata &rarr; herbatę.",
              examples:[
                { pl:"Piję zieloną herbatę.", en:"I'm drinking green tea." },
                { pl:"Kupuję nową książkę.", en:"I'm buying a new book." }
              ] },
            { front:"Where are you going? Also accusative.",
              sub:"<b>na</b> / <b>w</b> for direction, and <b>w</b> + a day, take the accusative.",
              points:[
                "Direction: <b>idę na koncert</b>, <b>jadę w góry</b>",
                "Time: <b>w sobotę</b>, <b>w niedzielę</b>"
              ],
              examples:[
                { pl:"Idę na obiad.", en:"I'm going for lunch." },
                { pl:"W sobotę mam czas.", en:"On Saturday I have time." }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"Lubię czarną ___ .", promptEn:"I like black coffee.",
              options:["kawę","kawa","kawy"], answer:"kawę",
              explain:"Feminine -a &rarr; -ę.", full:"Lubię czarną kawę.", fullEn:"I like black coffee." },
            { type:"choose", prompt:"Czytam ciekawą ___ .", promptEn:"I'm reading an interesting book.",
              options:["książkę","książka","książki"], answer:"książkę",
              explain:"Feminine -a &rarr; -ę: książka &rarr; książkę.", full:"Czytam ciekawą książkę.", fullEn:"I'm reading an interesting book." },
            { type:"choose", prompt:"Mam nowy ___ .", promptEn:"I have a new phone.",
              options:["telefon","telefonu","telefona"], answer:"telefon",
              explain:"Masculine inanimate - no change.", full:"Mam nowy telefon.", fullEn:"I have a new phone." },
            { type:"choose", prompt:"Mam małego ___ .", promptEn:"I have a small dog.",
              options:["psa","pies","psu"], answer:"psa",
              explain:"Animate masculine &rarr; -a (like the genitive).", full:"Mam małego psa.", fullEn:"I have a small dog." },
            { type:"choose", prompt:"Piję zieloną ___ .", promptEn:"I'm drinking green tea.",
              options:["herbatę","herbata","herbaty"], answer:"herbatę",
              explain:"Feminine -a &rarr; -ę.", full:"Piję zieloną herbatę.", fullEn:"I'm drinking green tea." },
            { type:"build", promptEn:"On Saturday I have time.",
              answer:["W","sobotę","mam","czas"],
              explain:"w + a day &rarr; accusative (sobotę); czas is the object.", full:"W sobotę mam czas.", fullEn:"On Saturday I have time." },
            { type:"choose", prompt:"W niedzielę idę na ___ .", promptEn:"On Sunday I'm going to a concert.",
              options:["koncert","koncercie","koncertu"], answer:"koncert",
              explain:"na + direction &rarr; accusative; koncert (inanimate) is unchanged.", full:"W niedzielę idę na koncert.", fullEn:"On Sunday I'm going to a concert." },
            { type:"choose", prompt:"Widzę moją ___ .", promptEn:"I see my sister.",
              options:["siostrę","siostra","siostry"], answer:"siostrę",
              explain:"Feminine -a &rarr; -ę, even for people.", full:"Widzę moją siostrę.", fullEn:"I see my sister." },
            { type:"choose", prompt:"Znam tego ___ .", promptEn:"I know this doctor.",
              options:["lekarza","lekarz","lekarzowi"], answer:"lekarza",
              explain:"People are animate &rarr; -a: lekarz &rarr; lekarza.", full:"Znam tego lekarza.", fullEn:"I know this doctor." },
            { type:"build", promptEn:"I really like black coffee.",
              answer:["Bardzo","lubię","czarną","kawę"],
              explain:"kawa &rarr; kawę (feminine -a &rarr; -ę).", full:"Bardzo lubię czarną kawę.", fullEn:"I really like black coffee." }
          ]
        },
        {
          name: "Narzędnik (Instrumental)", emoji: "\uD83D\uDD27", kind: "grammar",
          desc: "z kim? z czym? - jobs, transport, interests",
          teach: [
            { front:"Narzędnik - when do you use it?",
              sub:"It answers <b>z kim?</b> / <b>z czym?</b> - with whom / with what.",
              points:[
                "Tools and transport: <b>jadę autobusem</b> (no preposition)",
                "After <b>być</b> - jobs and identity: <b>jestem nauczycielem</b>",
                "After <b>interesować się</b>: <b>interesuję się sportem</b>",
                "After <b>z</b> = (together) with: <b>kawa z mlekiem</b>"
              ],
              examples:[
                { pl:"Jadę do pracy autobusem.", en:"I go to work by bus." },
                { pl:"Interesuję się sportem.", en:"I'm interested in sport." }
              ] },
            { front:"How do the endings change?",
              table:[
                { g:"Masculine", e:"-em", ex:"nauczyciel &rarr; nauczyciel<b>em</b>" },
                { g:"after k, g", e:"-iem", ex:"pociąg &rarr; pociąg<b>iem</b>" },
                { g:"Neuter", e:"-em", ex:"okno &rarr; okn<b>em</b>" },
                { g:"Feminine", e:"-ą", ex:"kawa &rarr; kaw<b>ą</b>" },
                { g:"Plural", e:"-ami", ex:"koledzy &rarr; koleg<b>ami</b>" }
              ],
              note:"Adjectives agree too: <b>dobrym</b> nauczycielem, <b>dobrą</b> kawą.",
              examples:[ { pl:"Rozmawiam z kolegami z pracy.", en:"I'm talking with colleagues from work." } ] },
            { front:"Jestem ___ . <span class='muted'>(nauczyciel)</span>",
              answer:"Jestem nauczycielem.",
              explain:"After <b>być</b>, your profession or identity takes the instrumental. A woman says: <b>Jestem nauczycielką</b>.",
              examples:[
                { pl:"On jest lekarzem.", en:"He is a doctor." },
                { pl:"Ona jest lekarką.", en:"She is a doctor." }
              ] },
            { front:"Jadę do pracy ___ . <span class='muted'>(tramwaj)</span>",
              answer:"Jadę do pracy tramwajem.",
              explain:"Means of transport take the instrumental with <b>no preposition</b>: autobusem, tramwajem, samochodem, rowerem.",
              examples:[
                { pl:"Piszę długopisem.", en:"I write with a pen." },
                { pl:"Jadę rowerem do parku.", en:"I ride a bike to the park." }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"Jestem ___ .", promptEn:"I am a teacher.",
              options:["nauczycielem","nauczyciela","nauczyciel"], answer:"nauczycielem",
              explain:"być + profession &rarr; the ending -em.", full:"Jestem nauczycielem.", fullEn:"I am a teacher." },
            { type:"choose", prompt:"Ona jest ___ .", promptEn:"She is a doctor.",
              options:["lekarką","lekarkę","lekarka"], answer:"lekarką",
              explain:"Feminine -a changes to -ą.", full:"Ona jest lekarką.", fullEn:"She is a doctor." },
            { type:"choose", prompt:"Codziennie jadę do pracy ___ .", promptEn:"I go to work by tram every day.",
              options:["tramwajem","tramwaju","tramwaj"], answer:"tramwajem",
              explain:"Transport takes -em, with no preposition.", full:"Codziennie jadę do pracy tramwajem.", fullEn:"I go to work by tram every day." },
            { type:"choose", prompt:"Wolę podróżować ___ .", promptEn:"I prefer to travel by train.",
              options:["pociągiem","pociągem","pociąga"], answer:"pociągiem",
              explain:"After k / g the ending softens to -iem.", full:"Wolę podróżować pociągiem.", fullEn:"I prefer to travel by train." },
            { type:"choose", prompt:"Interesuję się ___ .", promptEn:"I'm interested in music.",
              options:["muzyką","muzykę","muzyki"], answer:"muzyką",
              explain:"interesować się is always followed by the instrumental.", full:"Interesuję się muzyką.", fullEn:"I'm interested in music." },
            { type:"build", promptEn:"My brother is a teacher.",
              answer:["Mój","brat","jest","nauczycielem"],
              explain:"być &rarr; the job goes into the instrumental: nauczycielem.", full:"Mój brat jest nauczycielem.", fullEn:"My brother is a teacher." },
            { type:"choose", prompt:"Idę do kina z ___ .", promptEn:"I'm going to the cinema with a friend.",
              options:["przyjacielem","przyjaciela","przyjacielu"], answer:"przyjacielem",
              explain:"z = 'with' &rarr; the instrumental.", full:"Idę do kina z przyjacielem.", fullEn:"I'm going to the cinema with a friend." },
            { type:"choose", prompt:"Mieszkam z ___ .", promptEn:"I live with my sister.",
              options:["siostrą","siostrę","siostry"], answer:"siostrą",
              explain:"z + feminine -a &rarr; -ą.", full:"Mieszkam z siostrą.", fullEn:"I live with my sister." },
            { type:"choose", prompt:"Rozmawiam z ___ z pracy.", promptEn:"I talk with colleagues from work.",
              options:["kolegami","kolegów","koledzy"], answer:"kolegami",
              explain:"Plural instrumental &rarr; -ami.", full:"Rozmawiam z kolegami z pracy.", fullEn:"I talk with colleagues from work." },
            { type:"build", promptEn:"I go to work by tram.",
              answer:["Jadę","do","pracy","tramwajem"],
              explain:"Transport with no preposition: tramwajem.", full:"Jadę do pracy tramwajem.", fullEn:"I go to work by tram." }
          ]
        },
        {
          name: "Miejscownik (Locative)", emoji: "\uD83D\uDCCD", kind: "grammar",
          desc: "gdzie? o czym? - only after prepositions",
          teach: [
            { front:"Miejscownik - only after a preposition.",
              sub:"It <b>never stands alone</b> - always with a preposition.",
              points:[
                "Location with <b>w</b> (in) / <b>na</b> (on): w domu, na stole",
                "Topic with <b>o</b> (about): mówimy o pogodzie",
                "Also <b>przy</b> (by), <b>po</b> (after)"
              ],
              examples:[
                { pl:"Mieszkam w Warszawie.", en:"I live in Warsaw." },
                { pl:"Książka jest na stole.", en:"The book is on the table." }
              ] },
            { front:"How do the endings change?",
              table:[
                { g:"Feminine", e:"-e / -i", ex:"szkoła &rarr; szkol<b>e</b>" },
                { g:"Masc / Neut", e:"-e / -u", ex:"dom &rarr; dom<b>u</b>" },
                { g:"Watch the change", e:"", ex:"miasto &rarr; mie<b>ście</b>" }
              ],
              note:"The locative loves consonant changes - learn frequent phrases whole: w domu, w pracy, w mieście.",
              examples:[ { pl:"Jestem w pracy.", en:"I'm at work." } ] },
            { front:"Fixed phrases you'll use daily.",
              answer:"Jestem w domu.",
              explain:"Learn these as blocks: <b>w domu</b> (at home), <b>w pracy</b> (at work), <b>w szkole</b> (at school), <b>w kinie</b> (at the cinema).",
              examples:[
                { pl:"Jestem w domu.", en:"I'm at home." },
                { pl:"Uczę się w szkole.", en:"I study at school." }
              ] },
            { front:"o + locative = about",
              sub:"For talking or thinking <b>about</b> something.",
              points:[
                "<b>mówić o</b> - to talk about",
                "<b>myśleć o</b> - to think about"
              ],
              examples:[
                { pl:"Rozmawiamy o pogodzie.", en:"We're talking about the weather." },
                { pl:"Myślę o wakacjach.", en:"I'm thinking about the holidays." }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"Mieszkam w ___ .", promptEn:"I live in Warsaw.",
              options:["Warszawie","Warszawa","Warszawę"], answer:"Warszawie",
              explain:"w + locative; Warszawa &rarr; Warszawie.", full:"Mieszkam w Warszawie.", fullEn:"I live in Warsaw." },
            { type:"choose", prompt:"Jestem w ___ .", promptEn:"I'm at home.",
              options:["domu","dom","domem"], answer:"domu",
              explain:"w + locative; dom &rarr; domu.", full:"Jestem w domu.", fullEn:"I'm at home." },
            { type:"choose", prompt:"Jestem w ___ .", promptEn:"I'm at work.",
              options:["pracy","praca","pracę"], answer:"pracy",
              explain:"w + locative; praca &rarr; pracy.", full:"Jestem w pracy.", fullEn:"I'm at work." },
            { type:"choose", prompt:"Książka leży na ___ .", promptEn:"The book is lying on the table.",
              options:["stole","stół","stołem"], answer:"stole",
              explain:"na + locative; stół &rarr; stole (ó &rarr; o).", full:"Książka leży na stole.", fullEn:"The book is lying on the table." },
            { type:"choose", prompt:"Rozmawiamy o ___ .", promptEn:"We're talking about the weather.",
              options:["pogodzie","pogoda","pogodę"], answer:"pogodzie",
              explain:"o (about) + locative; pogoda &rarr; pogodzie.", full:"Rozmawiamy o pogodzie.", fullEn:"We're talking about the weather." },
            { type:"build", promptEn:"The book is on the table.",
              answer:["Książka","jest","na","stole"],
              explain:"na + locative: stół &rarr; stole.", full:"Książka jest na stole.", fullEn:"The book is on the table." },
            { type:"choose", prompt:"Uczę się w ___ .", promptEn:"I study at school.",
              options:["szkole","szkoła","szkołę"], answer:"szkole",
              explain:"w + locative; szkoła &rarr; szkole.", full:"Uczę się w szkole.", fullEn:"I study at school." },
            { type:"choose", prompt:"Jesteśmy w ___ .", promptEn:"We're at the cinema.",
              options:["kinie","kino","kina"], answer:"kinie",
              explain:"w + locative; kino &rarr; kinie.", full:"Jesteśmy w kinie.", fullEn:"We're at the cinema." },
            { type:"choose", prompt:"Mieszkam w ___ .", promptEn:"I live in the city.",
              options:["mieście","miasto","miastem"], answer:"mieście",
              explain:"w + locative; miasto &rarr; mieście (a big consonant change).", full:"Mieszkam w mieście.", fullEn:"I live in the city." },
            { type:"build", promptEn:"I'm thinking about the holidays.",
              answer:["Myślę","o","wakacjach"],
              explain:"o + locative (plural): wakacje &rarr; wakacjach.", full:"Myślę o wakacjach.", fullEn:"I'm thinking about the holidays." }
          ]
        },
        {
          name: "Wołacz (Vocative)", emoji: "\uD83D\uDCE3", kind: "grammar",
          desc: "direct address - calling someone",
          teach: [
            { front:"Wołacz - for calling or addressing someone.",
              sub:"Used when you <b>call out to</b> or address a person directly.",
              points:[
                "Polite address: <b>Panie profesorze!</b>",
                "Family: <b>Mamo!</b>, <b>Tato!</b>",
                "In letters: <b>Drogi Piotrze</b>, <b>Szanowna Pani</b>",
                "In casual speech, first names often just use the nominative"
              ],
              examples:[
                { pl:"Mamo, gdzie jesteś?", en:"Mum, where are you?" },
                { pl:"Dzień dobry, panie profesorze!", en:"Good morning, professor!" }
              ] },
            { front:"How do the endings change?",
              table:[
                { g:"Feminine", e:"-o", ex:"mama &rarr; mam<b>o</b>" },
                { g:"Feminine (soft)", e:"-u", ex:"Kasia &rarr; Kasi<b>u</b>" },
                { g:"Masculine", e:"-e / -u", ex:"pan &rarr; pan<b>ie</b>" }
              ],
              note:"Neuter and many first names in casual speech just use the nominative.",
              examples:[ { pl:"Aniu, chodź tutaj!", en:"Ania, come here!" } ] },
            { front:"Family and affection.",
              answer:"Mamo, gdzie jesteś?",
              explain:"Warm, everyday address: <b>mama &rarr; mamo</b>, <b>tata &rarr; tato</b>, <b>syn &rarr; synu</b>, <b>babcia &rarr; babciu</b>.",
              examples:[
                { pl:"Tato, pomóż mi.", en:"Dad, help me." },
                { pl:"Synu, chodź na obiad.", en:"Son, come for dinner." }
              ] },
            { front:"Polite and formal address.",
              sub:"This is where the vocative stays alive in daily Polish.",
              points:[
                "<b>Panie</b> + title: Panie doktorze, Panie profesorze",
                "Used with strangers, officials, in shops"
              ],
              examples:[
                { pl:"Dzień dobry, pani Anno!", en:"Good morning, Mrs Anna!" },
                { pl:"Panie doktorze, mam pytanie.", en:"Doctor, I have a question." }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"___, gdzie jesteś?", promptEn:"Mum, where are you?",
              options:["Mamo","Mama","Mamę"], answer:"Mamo",
              explain:"Feminine vocative &rarr; -o: mama &rarr; mamo.", full:"Mamo, gdzie jesteś?", fullEn:"Mum, where are you?" },
            { type:"choose", prompt:"___, chodź na obiad!", promptEn:"Son, come for dinner!",
              options:["Synu","Syn","Syna"], answer:"Synu",
              explain:"syn &rarr; synu (vocative).", full:"Synu, chodź na obiad!", fullEn:"Son, come for dinner!" },
            { type:"choose", prompt:"Dzień dobry, pani ___ !", promptEn:"Good morning, Mrs Anna!",
              options:["Anno","Anna","Annę"], answer:"Anno",
              explain:"Feminine name &rarr; -o: Anna &rarr; Anno.", full:"Dzień dobry, pani Anno!", fullEn:"Good morning, Mrs Anna!" },
            { type:"choose", prompt:"Panie ___ , mam pytanie.", promptEn:"Doctor, I have a question.",
              options:["doktorze","doktor","doktora"], answer:"doktorze",
              explain:"Masculine vocative &rarr; -e: doktor &rarr; doktorze.", full:"Panie doktorze, mam pytanie.", fullEn:"Doctor, I have a question." },
            { type:"choose", prompt:"___, chodź tutaj!", promptEn:"Kasia, come here!",
              options:["Kasiu","Kasia","Kasię"], answer:"Kasiu",
              explain:"Soft feminine &rarr; -u: Kasia &rarr; Kasiu.", full:"Kasiu, chodź tutaj!", fullEn:"Kasia, come here!" },
            { type:"build", promptEn:"Dad, help me.",
              answer:["Tato","pomóż","mi"],
              explain:"tata &rarr; tato (vocative).", full:"Tato, pomóż mi.", fullEn:"Dad, help me." },
            { type:"choose", prompt:"Cześć, ___ !", promptEn:"Hi, Piotr!",
              options:["Piotrze","Piotr","Piotra"], answer:"Piotrze",
              explain:"Masculine name &rarr; -e: Piotr &rarr; Piotrze.", full:"Cześć, Piotrze!", fullEn:"Hi, Piotr!" },
            { type:"choose", prompt:"___, jak się masz?", promptEn:"Ewa, how are you?",
              options:["Ewo","Ewa","Ewę"], answer:"Ewo",
              explain:"Feminine name &rarr; -o: Ewa &rarr; Ewo.", full:"Ewo, jak się masz?", fullEn:"Ewa, how are you?" },
            { type:"choose", prompt:"Dziękuję, ___ profesorze.", promptEn:"Thank you, professor.",
              options:["panie","pan","pana"], answer:"panie",
              explain:"pan &rarr; panie (vocative), used with titles.", full:"Dziękuję, panie profesorze.", fullEn:"Thank you, professor." },
            { type:"build", promptEn:"Good morning, professor!",
              answer:["Dzień","dobry","panie","profesorze"],
              explain:"Addressing with a title uses the vocative: panie profesorze.", full:"Dzień dobry, panie profesorze!", fullEn:"Good morning, professor!" }
          ]
        },
        {
          name: "Przymiotniki (Adjectives & Traits)", emoji: "\uD83C\uDFAD", kind: "grammar",
          desc: "Describing people: The 'oni' plural for character traits",
          teach: [
            { front:"Adjectives for groups: One vs. Oni",
              sub:"Adjectives must match the gender of the group they describe.",
              points:[
                "For <b>one</b> (women, objects, animals), just add <b>-e</b>: miły \u2192 miłe.",
                "For <b>oni</b> (groups with men), the ending softens to <b>-i</b> or <b>-y</b>, often changing the consonant before it."
              ],
              examples:[
                { pl:"Te kobiety są miłe.", en:"These women are nice." },
                { pl:"Ci panowie są mili.", en:"These men are nice." }
              ] },
            { front:"Pattern 1: -t becomes -c",
              sub:"When an adjective ends in -ty, it softens to -ci for 'oni'.",
              table:[
                { g:"stubborn", e:"uparty \u2192 uparci", ex:"Oni są bardzo <b>uparci</b>." },
                { g:"hardworking", e:"pracowity \u2192 pracowici", ex:"Moi koledzy są <b>pracowici</b>." },
                { g:"open", e:"otwarty \u2192 otwarci", ex:"Jesteśmy <b>otwarci</b> na pomysły." }
              ],
              examples:[
                { pl:"Ci studenci są bardzo pracowici.", en:"These students are very hardworking." }
              ] },
            { front:"Pattern 2: -r becomes -rz",
              sub:"When an adjective ends in -ry, it shifts to -rzy.",
              table:[
                { g:"honest", e:"szczery \u2192 szczerzy", ex:"Bądźmy ze sobą <b>szczerzy</b>." },
                { g:"good", e:"dobry \u2192 dobrzy", ex:"To są <b>dobrzy</b> ludzie." },
                { g:"smart", e:"mądry \u2192 mądrzy", ex:"Moi rodzice są <b>mądrzy</b>." }
              ],
              note:"'Dobry' and 'mądry' are extremely common and follow this exact same rule as 'szczery'.",
              examples:[
                { pl:"Zawsze byliśmy szczerzy.", en:"We have always been honest." }
              ] },
            { front:"Pattern 3: -ł becomes -l",
              sub:"The hard 'ł' softens into a standard 'l'.",
              table:[
                { g:"nice", e:"miły \u2192 mili", ex:"Sąsiedzi są bardzo <b>mili</b>." },
                { g:"shy", e:"nieśmiały \u2192 nieśmiali", ex:"Chłopcy byli <b>nieśmiali</b>." },
                { g:"merry/cheerful", e:"wesoły \u2192 weseli", ex:"Jesteśmy dzisiaj <b>weseli</b>." }
              ],
              explain:"Notice that for 'wesoły \u2192 weseli', the 'o' also shifts to an 'e' to make pronunciation smoother.",
              examples:[
                { pl:"Nasi nowi sąsiedzi są bardzo mili.", en:"Our new neighbors are very nice." }
              ] },
            { front:"Pattern 4: -sk becomes -sc & -k becomes -c",
              sub:"These are the trickiest transformations, but very common.",
              table:[
                { g:"sociable", e:"towarzyski \u2192 towarzyscy", ex:"Są bardzo <b>towarzyscy</b>." },
                { g:"tall/high", e:"wysoki \u2192 wysocy", ex:"Koszykarze są <b>wysocy</b>." }
              ],
              examples:[
                { pl:"Moi bracia są bardzo wysocy i towarzyscy.", en:"My brothers are very tall and sociable." }
              ] },
            { front:"The Easy Ones: Just add -i",
              sub:"Many consonants don't change at all, they just take an 'i'.",
              table:[
                { g:"lazy", e:"leniwy \u2192 leniwi", ex:"W weekend jesteśmy <b>leniwi</b>." },
                { g:"ambitious", e:"ambitny \u2192 ambitni", ex:"Młodzi ludzie są <b>ambitni</b>." },
                { g:"serious", e:"poważny \u2192 poważni", ex:"Dlaczego jesteście <b>poważni</b>?" }
              ],
              examples:[
                { pl:"Nasi pracownicy są bardzo ambitni.", en:"Our employees are very ambitious." }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"Moi koledzy z zespołu są bardzo ___ .", promptEn:"My teammates are very hardworking.",
              options:["pracowici","pracowity","pracowite"], answer:"pracowici",
              explain:"'Koledzy' is a masculine personal group (oni), so '-ty' softens to '-ci'.", full:"Moi koledzy z zespołu są bardzo pracowici.", fullEn:"My teammates are very hardworking." },
            { type:"choose", prompt:"Bądźmy ze sobą ___ .", promptEn:"Let's be honest with each other.",
              options:["szczerzy","szczery","szczere"], answer:"szczerzy",
              explain:"For a mixed/male group (we), '-ry' shifts to '-rzy'.", full:"Bądźmy ze sobą szczerzy.", fullEn:"Let's be honest with each other." },
            { type:"build", promptEn:"Our new neighbors are very nice.",
              answer:["Nasi","nowi","sąsiedzi","są","bardzo","mili"],
              explain:"'Sąsiedzi' triggers the 'oni' forms, turning 'miły' into 'mili'.", full:"Nasi nowi sąsiedzi są bardzo mili.", fullEn:"Our new neighbors are very nice." },
            { type:"choose", prompt:"Te dziewczyny są bardzo ___ .", promptEn:"These girls are very nice.",
              options:["miłe","mili","miły"], answer:"miłe",
              explain:"'Dziewczyny' forms a women-only group (one), which takes the simple '-e' ending.", full:"Te dziewczyny są bardzo miłe.", fullEn:"These girls are very nice." },
            { type:"choose", prompt:"Moi dziadkowie są bardzo ___ .", promptEn:"My grandparents are very smart.",
              options:["mądrzy","mądre","mądry"], answer:"mądrzy",
              explain:"'Dziadkowie' (grandparents) includes a man, so '-ry' shifts to '-rzy'.", full:"Moi dziadkowie są bardzo mądrzy.", fullEn:"My grandparents are very smart." },
            { type:"build", promptEn:"They (men) are very stubborn.",
              answer:["Oni","są","bardzo","uparci"],
              explain:"The '-ty' in 'uparty' changes to '-ci' for the 'oni' plural.", full:"Oni są bardzo uparci.", fullEn:"They (men) are very stubborn." },
            { type:"choose", prompt:"Czy twoi przyjaciele są ___ ?", promptEn:"Are your friends sociable?",
              options:["towarzyscy","towarzyski","towarzyskie"], answer:"towarzyscy",
              explain:"The '-ski' ending transforms into '-scy' for masculine personal groups.", full:"Czy twoi przyjaciele są towarzyscy?", fullEn:"Are your friends sociable?" },
            { type:"choose", prompt:"Wszyscy w biurze są dzisiaj ___ .", promptEn:"Everyone in the office is lazy today.",
              options:["leniwi","leniwe","leniwy"], answer:"leniwi",
              explain:"'Wszyscy' (everyone) is treated as an 'oni' group. Words ending in 'w' just add 'i'.", full:"Wszyscy w biurze są dzisiaj leniwi.", fullEn:"Everyone in the office is lazy today." },
            { type:"build", promptEn:"These men are very tall.",
              answer:["Ci","panowie","są","bardzo","wysocy"],
              explain:"The '-ki' in 'wysoki' softens into '-cy' for 'oni'.", full:"Ci panowie są bardzo wysocy.", fullEn:"These men are very tall." },
            { type:"choose", prompt:"Moje siostry są bardzo ___ .", promptEn:"My sisters are very ambitious.",
              options:["ambitne","ambitni","ambitny"], answer:"ambitne",
              explain:"'Siostry' is a female group (one), so it takes the simple '-e' ending, NOT '-i'.", full:"Moje siostry są bardzo ambitne.", fullEn:"My sisters are very ambitious." }
          ]
        },
        {
          name: "Zawody (Professions)", emoji: "\uD83D\uDCBC", kind: "grammar",
          desc: "How professions change for groups of men (the 'oni' plural)",
          teach: [
            { front:"Professions in the 'Oni' Plural",
              sub:"When a group of professionals includes at least one man, the noun takes a special ending.",
              points:[
                "Unlike adjectives (which just take -i or -y), professions have a few different endings: <b>-owie</b>, <b>-e</b>, <b>-cy</b>, and <b>-rzy</b>.",
                "The ending you choose depends almost entirely on the last letter of the singular word.",
                "For women-only groups (<b>one</b>), the rule is easy: usually just add <b>-ki</b> (nauczycielki, lekarki, kelnerki)."
              ],
              examples:[
                { pl:"Gdzie są lekarze?", en:"Where are the doctors?" }
              ] },
            { front:"Pattern 1: The Prestigious '-owie'",
              sub:"Many modern, technical, or 'boss' titles take the '-owie' ending.",
              table:[
                { g:"manager", e:"menedżer \u2192 menedżerowie", ex:"Nasi <b>menedżerowie</b> są na spotkaniu." },
                { g:"engineer", e:"inżynier \u2192 inżynierowie", ex:"To są świetni <b>inżynierowie</b>." },
                { g:"boss", e:"szef \u2192 szefowie", ex:"<b>Szefowie</b> mają dzisiaj wolne." },
                { g:"professor", e:"profesor \u2192 profesorowie", ex:"Ci <b>profesorowie</b> uczą na uniwersytecie." }
              ],
              examples:[
                { pl:"Inżynierowie i menedżerowie pracują razem.", en:"The engineers and managers work together." }
              ] },
            { front:"Pattern 2: The Soft '-e'",
              sub:"Words ending in '-arz', '-erz', and '-iel' simply add an '-e'.",
              table:[
                { g:"doctor", e:"lekarz \u2192 lekarze", ex:"Ci <b>lekarze</b> są bardzo dobrzy." },
                { g:"teacher", e:"nauczyciel \u2192 nauczyciele", ex:"Nasi <b>nauczyciele</b> są cierpliwi." },
                { g:"journalist", e:"dziennikarz \u2192 dziennikarze", ex:"<b>Dziennikarze</b> zadają dużo pytań." }
              ],
              note:"Never say 'lekarzy' or 'nauczycieli' in the Nominative (subject) case!",
              examples:[
                { pl:"Lekarze mają dużo pracy.", en:"Doctors have a lot of work." }
              ] },
            { front:"Pattern 3: The '-ik' / '-yk' becomes '-icy' / '-ycy'",
              sub:"A very strict rule for almost all nouns ending in -ik/-yk.",
              table:[
                { g:"worker", e:"pracownik \u2192 pracownicy", ex:"Wszyscy <b>pracownicy</b> są w biurze." },
                { g:"lawyer", e:"prawnik \u2192 prawnicy", ex:"Ci <b>prawnicy</b> są drodzy." },
                { g:"clerk", e:"urzędnik \u2192 urzędnicy", ex:"<b>Urzędnicy</b> pracują do szesnastej." }
              ],
              examples:[
                { pl:"Moi pracownicy są bardzo zmotywowani.", en:"My employees are very motivated." }
              ] },
            { front:"Pattern 4: The '-sta' and '-t' to '-ści' / '-ci'",
              sub:"Words ending in -sta or -t undergo a heavy softening.",
              table:[
                { g:"programmer", e:"programista \u2192 programiści", ex:"<b>Programiści</b> zarabiają dobrze." },
                { g:"dentist", e:"dentysta \u2192 dentyści", ex:"<b>Dentyści</b> mają dzisiaj dużo pacjentów." },
                { g:"student", e:"student \u2192 studenci", ex:"Ci <b>studenci</b> są z Polski." },
                { g:"policeman", e:"policjant \u2192 policjanci", ex:"<b>Policjanci</b> kierują ruchem." }
              ],
              examples:[
                { pl:"Nasi programiści to świetny zespół.", en:"Our programmers are a great team." }
              ] },
            { front:"Pattern 5: The '-r' and '-ca' to '-rzy' / '-cy'",
              sub:"More consonant softening for everyday jobs.",
              table:[
                { g:"actor", e:"aktor \u2192 aktorzy", ex:"Ci <b>aktorzy</b> są sławni." },
                { g:"waiter", e:"kelner \u2192 kelnerzy", ex:"<b>Kelnerzy</b> przynoszą rachunek." },
                { g:"director", e:"dyrektor \u2192 dyrektorzy", ex:"<b>Dyrektorzy</b> mają spotkanie." },
                { g:"driver", e:"kierowca \u2192 kierowcy", ex:"<b>Kierowcy</b> autobusów mają przerwę." },
                { g:"seller", e:"sprzedawca \u2192 sprzedawcy", ex:"<b>Sprzedawcy</b> są w sklepie." }
              ],
              examples:[
                { pl:"Kelnerzy i kierowcy pracują na zmiany.", en:"Waiters and drivers work in shifts." }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"Wszyscy ___ są dzisiaj na spotkaniu.", promptEn:"All employees are at the meeting today.",
              options:["pracownicy","pracowniki","pracownikowie"], answer:"pracownicy",
              explain:"Words ending in '-ik' (pracownik) change to '-icy' in the plural.", full:"Wszyscy pracownicy są dzisiaj na spotkaniu.", fullEn:"All employees are at the meeting today." },
            { type:"choose", prompt:"Nasi ___ mają dzisiaj wolne.", promptEn:"Our bosses have the day off today.",
              options:["szefowie","szefy","szefzy"], answer:"szefowie",
              explain:"'Szef' takes the prestigious '-owie' ending.", full:"Nasi szefowie mają dzisiaj wolne.", fullEn:"Our bosses have the day off today." },
            { type:"build", promptEn:"These doctors are very good.",
              answer:["Ci","lekarze","są","bardzo","dobrzy"],
              explain:"'Lekarz' ends in '-arz', so it simply takes the '-e' ending.", full:"Ci lekarze są bardzo dobrzy.", fullEn:"These doctors are very good." },
            { type:"choose", prompt:"Ci ___ pracują nad nową aplikacją.", promptEn:"These programmers are working on a new app.",
              options:["programiści","programisty","programistowie"], answer:"programiści",
              explain:"Words ending in '-sta' (programista) heavily soften to '-ści'.", full:"Ci programiści pracują nad nową aplikacją.", fullEn:"These programmers are working on a new app." },
            { type:"choose", prompt:"Pytam, bo moi ___ nie wiedzą.", promptEn:"I ask because my managers don't know.",
              options:["menedżerowie","menedżery","menedżerzy"], answer:"menedżerowie",
              explain:"While 'menedżerzy' is sometimes used, 'menedżerowie' is the standard, safer plural form.", full:"Pytam, bo moi menedżerowie nie wiedzą.", fullEn:"I ask because my managers don't know." },
            { type:"build", promptEn:"The lawyers are in the office.",
              answer:["Prawnicy","są","w","biurze"],
              explain:"'Prawnik' follows the '-ik' to '-icy' rule.", full:"Prawnicy są w biurze.", fullEn:"The lawyers are in the office." },
            { type:"choose", prompt:"Nasi ___ zarabiają bardzo dobrze.", promptEn:"Our engineers earn very well.",
              options:["inżynierowie","inżyniery","inżynierzy"], answer:"inżynierowie",
              explain:"'Inżynier' is a title that takes the '-owie' ending.", full:"Nasi inżynierowie zarabiają bardzo dobrze.", fullEn:"Our engineers earn very well." },
            { type:"choose", prompt:"Czy ci panowie to ___ ?", promptEn:"Are those men waiters?",
              options:["kelnerzy","kelnerowie","kelnery"], answer:"kelnerzy",
              explain:"'Kelner' ends in '-r', which softens to '-rzy'.", full:"Czy ci panowie to kelnerzy?", fullEn:"Are those men waiters?" },
            { type:"build", promptEn:"The students and teachers are here.",
              answer:["Studenci","i","nauczyciele","są","tutaj"],
              explain:"'Student' becomes 'studenci', and 'nauczyciel' becomes 'nauczyciele'.", full:"Studenci i nauczyciele są tutaj.", fullEn:"The students and teachers are here." },
            { type:"choose", prompt:"Wszyscy ___ stoją w korku.", promptEn:"All the drivers are stuck in a traffic jam.",
              options:["kierowcy","kierowcowie","kierowce"], answer:"kierowcy",
              explain:"'Kierowca' is a masculine word ending in '-a'. It shifts to '-cy'.", full:"Wszyscy kierowcy stoją w korku.", fullEn:"All the drivers are stuck in a traffic jam." }
          ]
        },
        {
          name: "Zaimki (Pronouns & Determiners)", emoji: "\uD83E\uDDED", kind: "grammar",
          desc: "mój, ten, jaki - pointing and owning in the Nominative",
          teach: [
            { front:"On, ona, ono, one, oni - The 5 Genders",
              sub:"Polish splits plurals based on exactly who is in the group.",
              points:[
                "Singular: <b>on</b> (masculine), <b>ona</b> (feminine), <b>ono</b> (neuter)",
                "Plural <b>oni</b>: Groups with at least one man (masculine personal)",
                "Plural <b>one</b>: Women, children, animals, and all objects"
              ],
              examples:[
                { pl:"Gdzie oni są?", en:"Where are they? (men/mixed)" },
                { pl:"Gdzie one są?", en:"Where are they? (women/objects)" }
              ] },
            { front:"Mój & Twój (My & Your)",
              table:[
                { g:"Masculine", e:"mój / twój", ex:"mój bilet" },
                { g:"Feminine", e:"moja / twoja", ex:"twoja kawa" },
                { g:"Neuter", e:"moje / twoje", ex:"moje biurko" }
              ],
              note:"In the plural, use <b>moi / twoi</b> for men (oni), and <b>moje / twoje</b> for everything else (one).",
              examples:[ 
                { pl:"To jest mój kot.", en:"This is my cat." } 
              ] },
            { front:"Ten & Tamten (This & That)",
              sub:"Pointing at things nearby (ten) vs. further away (tamten).",
              table:[
                { g:"Masculine", e:"ten / tamten", ex:"ten pociąg" },
                { g:"Feminine", e:"ta / tamta", ex:"ta ulica" },
                { g:"Neuter", e:"to / tamto", ex:"to spotkanie" }
              ],
              examples:[
                { pl:"Ten chleb jest bardzo dobry.", en:"This bread is very good." },
                { pl:"Ta kawa jest moja.", en:"This coffee is mine." }
              ] },
            { front:"Jaki, Który, Czyj (What kind, Which, Whose)",
              points:[
                "<b>Jaki / Jaka / Jakie:</b> What kind? (Asking for descriptions)",
                "<b>Który / Która / Które:</b> Which one? (Choosing from a set)",
                "<b>Czyj / Czyja / Czyje:</b> Whose? (Asking about ownership)"
              ],
              note:"These change their endings exactly like adjectives to match the noun they describe.",
              examples:[
                { pl:"Jaka to jest ulica?", en:"What street is this?" },
                { pl:"Który to twój samochód?", en:"Which one is your car?" }
              ] },
            { front:"The special 'ONI' plurals",
              sub:"When talking about groups of men (or mixed groups), the endings soften.",
              table:[
                { g:"My / Your", e:"moi / twoi", ex:"moi koledzy" },
                { g:"These / Those", e:"ci / tamci", ex:"ci panowie" },
                { g:"Which / What", e:"którzy / jacy", ex:"jacy ludzie" }
              ],
              explain:"This is the trickiest column in the grammar table! Notice how <i>te</i> becomes <b>ci</b>, and <i>moje</i> becomes <b>moi</b> when referring to men.",
              examples:[
                { pl:"Ci ludzie to moi znajomi.", en:"These people are my friends." }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"To jest ___ nowa praca.", promptEn:"This is my new job.",
              options:["moja","mój","moje"], answer:"moja",
              explain:"'Praca' is feminine, so we use 'moja'.", full:"To jest moja nowa praca.", fullEn:"This is my new job." },
            { type:"choose", prompt:"___ to jest telefon?", promptEn:"Whose phone is this?",
              options:["Czyj","Czyja","Czyje"], answer:"Czyj",
              explain:"'Telefon' is masculine, so we use 'Czyj'.", full:"Czyj to jest telefon?", fullEn:"Whose phone is this?" },
            { type:"choose", prompt:"___ studenci są z Polski.", promptEn:"These students are from Poland.",
              options:["Ci","Te","Ta"], answer:"Ci",
              explain:"'Studenci' is a masculine personal plural (oni), so 'te' softens to 'ci'.", full:"Ci studenci są z Polski.", fullEn:"These students are from Poland." },
            { type:"choose", prompt:"___ to twój samochód?", promptEn:"Which one is your car?",
              options:["Który","Która","Które"], answer:"Który",
              explain:"'Samochód' is masculine, so we use 'Który'.", full:"Który to twój samochód?", fullEn:"Which one is your car?" },
            { type:"build", promptEn:"Which coffee is yours?",
              answer:["Która","kawa","jest","twoja"],
              explain:"'Kawa' is feminine, so both 'która' and 'twoja' take the -a ending.", full:"Która kawa jest twoja?", fullEn:"Which coffee is yours?" },
            { type:"choose", prompt:"___ koty są bardzo głodne.", promptEn:"These cats are very hungry.",
              options:["Te","Ci","Ta"], answer:"Te",
              explain:"Animals belong to the 'one' plural group, so we use 'Te', not 'Ci'.", full:"Te koty są bardzo głodne.", fullEn:"These cats are very hungry." },
            { type:"choose", prompt:"___ chleb jest bardzo dobry.", promptEn:"This bread is very good.",
              options:["Ten","Ta","To"], answer:"Ten",
              explain:"'Chleb' is masculine, so we use 'Ten'.", full:"Ten chleb jest bardzo dobry.", fullEn:"This bread is very good." },
            { type:"choose", prompt:"___ to jest ulica?", promptEn:"What street is this?",
              options:["Jaka","Jaki","Jakie"], answer:"Jaka",
              explain:"'Ulica' is feminine, so we ask 'Jaka'.", full:"Jaka to jest ulica?", fullEn:"What street is this?" },
            { type:"build", promptEn:"These people are my friends.",
              answer:["Ci","ludzie","to","moi","znajomi"],
              explain:"'Ludzie' (people) includes men, triggering the 'oni' forms: 'ci' and 'moi'.", full:"Ci ludzie to moi znajomi.", fullEn:"These people are my friends." },
            { type:"build", promptEn:"This is my cat.",
              answer:["To","jest","mój","kot"],
              explain:"'Kot' is masculine, so we use 'mój'.", full:"To jest mój kot.", fullEn:"This is my cat." }
          ]
        },
        {
          name: "Narodowości (Nationalities)", emoji: "\u2708\uFE0F", kind: "grammar",
          desc: "The tricky 'oni' plurals for 15 common nationalities in Poland",
          teach: [
            { front:"Nationalities and the 'Oni' Plural",
              sub:"Groups of men (or mixed groups) cause consonant mutations at the end of the word.",
              points:[
                "Feminine nationalities follow easy rules, usually ending in <b>-ki</b> (Polki, Ukrainki).",
                "The masculine personal (<b>oni</b>) plural is where the heavy consonant changes happen.",
                "Nationalities in Polish are always capitalized."
              ],
              examples:[
                { pl:"To są Ukraińcy.", en:"These are Ukrainians." },
                { pl:"Czy oni są z Polski?", en:"Are they from Poland?" }
              ] },
            { front:"Pattern 1: -k and -czyk become -cy",
              sub:"The hard 'k' softens into a 'c'.",
              table:[
                { g:"Pole", e:"Polak \u2192 Polacy", ex:"Znamy się, to <b>Polacy</b>." },
                { g:"Slovak", e:"Słowak \u2192 Słowacy", ex:"Ci <b>Słowacy</b> są mili." },
                { g:"Brit", e:"Brytyjczyk \u2192 Brytyjczycy", ex:"To są <b>Brytyjczycy</b>." },
                { g:"Vietnamese", e:"Wietnamczyk \u2192 Wietnamczycy", ex:"<b>Wietnamczycy</b> świetnie gotują." }
              ],
              examples:[
                { pl:"Polacy i Słowacy to sąsiedzi.", en:"Poles and Slovaks are neighbors." }
              ] },
            { front:"Pattern 2: -iec becomes -cy",
              sub:"The 'e' drops out completely, and the ending becomes -cy.",
              table:[
                { g:"Ukrainian", e:"Ukrainiec \u2192 Ukraińcy", ex:"Moi koledzy to <b>Ukraińcy</b>." },
                { g:"German", e:"Niemiec \u2192 Niemcy", ex:"Ci <b>Niemcy</b> są turystami." }
              ],
              note:"This is one of the most frequent patterns you will hear in Warsaw.",
              examples:[
                { pl:"W moim biurze pracują Ukraińcy.", en:"Ukrainians work in my office." }
              ] },
            { front:"Pattern 3: -in and -an become -nie / -ni",
              sub:"Watch out for the drop of 'in' in words ending with '-anin'!",
              table:[
                { g:"American", e:"Amerykanin \u2192 Amerykanie", ex:"To są <b>Amerykanie</b>." },
                { g:"Spaniard", e:"Hiszpan \u2192 Hiszpanie", ex:"<b>Hiszpanie</b> lubią słońce." },
                { g:"Belarusian", e:"Białorusin \u2192 Białorusini", ex:"Ci <b>Białorusini</b> to moi znajomi." },
                { g:"Georgian", e:"Gruzin \u2192 Gruzini", ex:"<b>Gruzini</b> robią świetne wino." }
              ],
              examples:[
                { pl:"Amerykanie często podróżują.", en:"Americans travel often." }
              ] },
            { front:"Pattern 4: The Heavy Softeners",
              sub:"Some consonants change entirely to accommodate the 'i' sound.",
              table:[
                { g:"Italian", e:"Włoch \u2192 Włosi", ex:"<b>Włosi</b> robią pizzę." },
                { g:"Czech", e:"Czech \u2192 Czesi", ex:"<b>Czesi</b> są blisko." },
                { g:"French", e:"Francuz \u2192 Francuzi", ex:"To są <b>Francuzi</b>." },
                { g:"Indian", e:"Hindus \u2192 Hindusi", ex:"<b>Hindusi</b> mówią po angielsku." },
                { g:"Turk", e:"Turek \u2192 Turcy", ex:"<b>Turcy</b> piją dużo herbaty." }
              ],
              explain:"Notice how 'ch' softens to 'si' (Włosi, Czesi), and 'z' softens to 'zi' (Francuzi). 'Turek' drops the 'e' completely.",
              examples:[
                { pl:"Włosi i Francuzi to Europejczycy.", en:"Italians and French are Europeans." }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"Moi sąsiedzi to ___ .", promptEn:"My neighbors are Ukrainians.",
              options:["Ukraińcy","Ukrainiec","Ukraińce"], answer:"Ukraińcy",
              explain:"'Ukrainiec' ends in -iec, which changes to -cy in the plural.", full:"Moi sąsiedzi to Ukraińcy.", fullEn:"My neighbors are Ukrainians." },
            { type:"choose", prompt:"Czy ci panowie to ___ ?", promptEn:"Are those men Germans?",
              options:["Niemcy","Niemiec","Niemce"], answer:"Niemcy",
              explain:"'Niemiec' follows the -iec to -cy rule.", full:"Czy ci panowie to Niemcy?", fullEn:"Are those men Germans?" },
            { type:"build", promptEn:"These Americans are my friends.",
              answer:["Ci","Amerykanie","to","moi","znajomi"],
              explain:"Words ending in -anin (Amerykanin) drop the 'in' to become -anie.", full:"Ci Amerykanie to moi znajomi.", fullEn:"These Americans are my friends." },
            { type:"choose", prompt:"___ uwielbiają pizzę.", promptEn:"Italians love pizza.",
              options:["Włosi","Włochy","Włosy"], answer:"Włosi",
              explain:"'Włoch' (Italian man) changes to 'Włosi'. 'Włochy' means Italy (the country), and 'włosy' means hair!", full:"Włosi uwielbiają pizzę.", fullEn:"Italians love pizza." },
            { type:"choose", prompt:"Moi koledzy z pracy to ___ .", promptEn:"My colleagues from work are Belarusians.",
              options:["Białorusini","Białorusinie","Białorusin"], answer:"Białorusini",
              explain:"'Białorusin' takes the simple -i ending.", full:"Moi koledzy z pracy to Białorusini.", fullEn:"My colleagues from work are Belarusians." },
            { type:"choose", prompt:"Czy ci turyści to ___ ?", promptEn:"Are these tourists British?",
              options:["Brytyjczycy","Brytyjczykowie","Brytyjczyki"], answer:"Brytyjczycy",
              explain:"The -czyk ending always softens to -czycy.", full:"Czy ci turyści to Brytyjczycy?", fullEn:"Are these tourists British?" },
            { type:"build", promptEn:"The Czechs and the Slovaks are here.",
              answer:["Czesi","i","Słowacy","są","tutaj"],
              explain:"'Czech' softens to 'Czesi', and 'Słowak' softens to 'Słowacy'.", full:"Czesi i Słowacy są tutaj.", fullEn:"The Czechs and the Slovaks are here." },
            { type:"choose", prompt:"To są bardzo mili ___ .", promptEn:"These are very nice Frenchmen.",
              options:["Francuzi","Francuzy","Francuzowie"], answer:"Francuzi",
              explain:"The 'z' in 'Francuz' softens to 'zi'.", full:"To są bardzo mili Francuzi.", fullEn:"These are very nice Frenchmen." },
            { type:"choose", prompt:"___ prowadzą tę świetną restaurację.", promptEn:"Vietnamese people run this great restaurant.",
              options:["Wietnamczycy","Wietnamczyki","Wietnamczyk"], answer:"Wietnamczycy",
              explain:"Like all -czyk words, it becomes -czycy.", full:"Wietnamczycy prowadzą tę świetną restaurację.", fullEn:"Vietnamese people run this great restaurant." },
            { type:"build", promptEn:"The Georgians make great wine.",
              answer:["Gruzini","robią","świetne","wino"],
              explain:"'Gruzin' simply takes the -i ending to become 'Gruzini'.", full:"Gruzini robią świetne wino.", fullEn:"The Georgians make great wine." }
          ]
        }
      ]
    }
  );
})();
