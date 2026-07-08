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
        }
      ]
    }
  );
})();
