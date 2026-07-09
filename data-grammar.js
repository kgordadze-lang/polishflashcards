/* Po polsku - lesson data: Grammar
   Registered onto window.PP_LEVELS by index.html (loaded in order).
   Safe to edit this file alone; a syntax error here shows a load
   message instead of breaking the app engine. */
(function(){
  window.PP_LEVELS = window.PP_LEVELS || [];
  window.PP_LEVELS.push(
    {
      level: "Grammar",
      blurb: "Cases & rules",
      topics: [
        {
          name: "Mianownik (Nominative)", emoji: "\uD83C\uDFC1", kind: "grammar", chip: "Grammar A1",
          desc: "The dictionary case: the subject of the sentence",
          teach: [
            { front:"What the Nominative does",
              sub:"It marks the subject - the person or thing <i>doing</i> the action.",
              points:[
                "Answers <b>kto?</b> (who?) or <b>co?</b> (what?)",
                "This is the <b>dictionary form</b> - the shape you'll see in every wordlist.",
                "Also used after <b>to jest / to są</b> (this is / these are)."
              ],
              examples:[
                { pl:"Anna czyta książkę.", en:"Anna is reading a book." },
                { pl:"To jest kot.", en:"This is a cat." },
                { pl:"To są studenci.", en:"These are students." }
              ] },
            { front:"When to use it",
              sub:"Three easy signals tell you the Nominative is coming.",
              points:[
                "The <b>subject</b> of any sentence: <i>Piotr pracuje.</i>",
                "After <b>to jest / to są</b>: <i>To jest moja siostra.</i>",
                "In lists and labels: menus, name tags, signs."
              ],
              note:"After <b>być</b> + a profession (jestem lekarzem), you use Instrumental instead. That's a separate case - covered later.",
              examples:[
                { pl:"Ten samochód jest nowy.", en:"This car is new." },
                { pl:"To są moi rodzice.", en:"These are my parents." }
              ] },
            { front:"Singular: no change",
              sub:"In the singular, the Nominative is the dictionary form. Nothing changes.",
              table:[
                { g:"Masculine", e:"kot, dom, samochód", ex:"Kot śpi." },
                { g:"Feminine", e:"kobieta, kawa, książka", ex:"Kawa jest gorąca." },
                { g:"Neuter", e:"okno, dziecko, mleko", ex:"Dziecko śpi." }
              ],
              explain:"You can spot gender from the ending: <b>-a</b> is usually feminine, <b>-o/-e/-ę</b> neuter, most consonant endings masculine.",
              examples:[
                { pl:"Ten dom jest duży.", en:"This house is big." }
              ] },
            { front:"Plural: the big split",
              sub:"Polish has TWO plural forms, depending on who's in the group.",
              points:[
                "<b>Oni</b> plural: any group with at least one man (masculine personal).",
                "<b>One</b> plural: everything else - women only, children, animals, objects.",
                "This choice affects the endings on nouns, adjectives, and pronouns."
              ],
              examples:[
                { pl:"Oni są w domu.", en:"They are at home. (men or mixed)" },
                { pl:"One są w domu.", en:"They are at home. (women / things)" }
              ] },
            { front:"'One' plural endings",
              sub:"The easy plural: things, women, animals.",
              table:[
                { g:"Masc. non-personal", e:"-y / -i", ex:"kot \u2192 koty, samochód \u2192 samochody" },
                { g:"Feminine", e:"-y / -i", ex:"kobieta \u2192 kobiety, książka \u2192 książki" },
                { g:"Neuter", e:"-a", ex:"okno \u2192 okna, mieszkanie \u2192 mieszkania" }
              ],
              explain:"After <b>k, g</b> use <b>-i</b> instead of <b>-y</b>: książka \u2192 książki, noga \u2192 nogi.",
              examples:[
                { pl:"Te książki są nowe.", en:"These books are new." },
                { pl:"Moje koty śpią.", en:"My cats are sleeping." }
              ] },
            { front:"'Oni' plural endings",
              sub:"Groups with men - endings soften and consonants often change.",
              table:[
                { g:"Basic ending", e:"-i / -y", ex:"student \u2192 studenci" },
                { g:"Prestigious", e:"-owie", ex:"szef \u2192 szefowie, pan \u2192 panowie" },
                { g:"Soft -e", e:"-e", ex:"lekarz \u2192 lekarze, nauczyciel \u2192 nauczyciele" }
              ],
              note:"See <b>Zawody</b> and <b>Narodowości</b> for the full patterns - this is the trickiest area of Polish grammar.",
              examples:[
                { pl:"Nasi studenci są bardzo mądrzy.", en:"Our students are very smart." },
                { pl:"Ci panowie to lekarze.", en:"These men are doctors." }
              ] },
            { front:"Watch out: after 'to jest' \u2192 always Nominative",
              sub:"Even in negation, even with adjectives, this construction never changes case.",
              points:[
                "<b>To jest kot.</b> - This is a cat. (Nominative)",
                "<b>To nie jest kot.</b> - This is not a cat. (still Nominative!)",
                "<b>To jest moja siostra.</b> - This is my sister. (Nominative)"
              ],
              explain:"Compare with <i>On jest lekarzem</i> (He is a doctor) - here <b>być</b> takes Instrumental. But <i>To jest lekarz</i> uses Nominative. The little word <b>to</b> makes the difference.",
              examples:[
                { pl:"To nie jest moja książka.", en:"This is not my book." },
                { pl:"To są bardzo dobre studenci.", en:"These are very good students." }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"To jest ___ kawa.", promptEn:"This is my coffee.",
              options:["moja","mój","moje"], answer:"moja",
              explain:"'Kawa' is feminine, so 'my' becomes 'moja'. In Nominative singular, feminine takes -a.", full:"To jest moja kawa.", fullEn:"This is my coffee." },
            { type:"choose", prompt:"Ten ___ jest bardzo duży.", promptEn:"This house is very big.",
              options:["dom","domu","domem"], answer:"dom",
              explain:"After 'ten' (this) we need Nominative, and masculine nouns take no ending - just the dictionary form.", full:"Ten dom jest bardzo duży.", fullEn:"This house is very big." },
            { type:"choose", prompt:"___ dziecko śpi.", promptEn:"The child is sleeping.",
              options:["To","Ten","Ta"], answer:"To",
              explain:"'Dziecko' is neuter (ends in -o), so we point with 'to'.", full:"To dziecko śpi.", fullEn:"The child is sleeping." },
            { type:"build", promptEn:"This is my new car.",
              answer:["To","jest","mój","nowy","samochód"],
              explain:"After 'to jest' everything stays in Nominative. 'Samochód' is masculine, so 'mój nowy' agree in masculine.", full:"To jest mój nowy samochód.", fullEn:"This is my new car." },
            { type:"choose", prompt:"Te ___ są bardzo ładne.", promptEn:"These flowers are very pretty.",
              options:["kwiaty","kwiat","kwiatów"], answer:"kwiaty",
              explain:"Plural subject in Nominative. 'Kwiat' is masculine non-personal (a thing), so it takes -y.", full:"Te kwiaty są bardzo ładne.", fullEn:"These flowers are very pretty." },
            { type:"choose", prompt:"Moi ___ są w biurze.", promptEn:"My colleagues are in the office.",
              options:["koledzy","kolegi","kolegami"], answer:"koledzy",
              explain:"'Koledzy' is the 'oni' plural (a group with men). Notice 'moi' also takes the special masculine-personal form.", full:"Moi koledzy są w biurze.", fullEn:"My colleagues are in the office." },
            { type:"build", promptEn:"These are my parents.",
              answer:["To","są","moi","rodzice"],
              explain:"'Rodzice' (parents) includes fathers, so it's an 'oni' group. That triggers 'moi', not 'moje'.", full:"To są moi rodzice.", fullEn:"These are my parents." },
            { type:"choose", prompt:"Ta ___ jest ciekawa.", promptEn:"This book is interesting.",
              options:["książka","książkę","książki"], answer:"książka",
              explain:"Subject of the sentence \u2192 Nominative. 'Książka' is the dictionary form.", full:"Ta książka jest ciekawa.", fullEn:"This book is interesting." },
            { type:"choose", prompt:"To nie ___ moja siostra.", promptEn:"This is not my sister.",
              options:["jest","ma","są"], answer:"jest",
              explain:"'To (nie) jest' + Nominative is the standard 'this is (not)' pattern.", full:"To nie jest moja siostra.", fullEn:"This is not my sister." },
            { type:"build", promptEn:"These children are hungry.",
              answer:["Te","dzieci","są","głodne"],
              explain:"'Dzieci' (children) is treated as an 'one' group (not 'oni'), so we use 'te' and 'głodne', not 'ci' and 'głodni'.", full:"Te dzieci są głodne.", fullEn:"These children are hungry." },
            { type:"choose", prompt:"___ studenci są z Polski.", promptEn:"These students are from Poland.",
              options:["Ci","Te","To"], answer:"Ci",
              explain:"'Studenci' is masculine personal ('oni'), so we point with 'ci', not 'te'.", full:"Ci studenci są z Polski.", fullEn:"These students are from Poland." },
            { type:"build", promptEn:"That is not a cat.",
              answer:["To","nie","jest","kot"],
              explain:"After 'to (nie) jest' Nominative stays. 'Kot' is the dictionary form.", full:"To nie jest kot.", fullEn:"That is not a cat." },
            { type:"choose", prompt:"Nasze ___ są bardzo mądre.", promptEn:"Our sisters are very smart.",
              options:["siostry","siostrę","sióstr"], answer:"siostry",
              explain:"'Siostry' is a women-only group ('one'), plural Nominative takes -y.", full:"Nasze siostry są bardzo mądre.", fullEn:"Our sisters are very smart." },
            { type:"choose", prompt:"To ___ mój brat.", promptEn:"This is my brother.",
              options:["jest","są","ma"], answer:"jest",
              explain:"Singular subject after 'to' \u2192 'jest'. Plural would be 'to są'.", full:"To jest mój brat.", fullEn:"This is my brother." }
          ]
        },
        {
          name: "Dopełniacz (Genitive)", emoji: "\uD83D\uDCE6", kind: "grammar", chip: "Grammar A1",
          desc: "The 'of / no / from' case: absence, possession, quantity",
          teach: [
            { front:"What the Genitive does",
              sub:"The Genitive shows <b>absence, possession, or amount</b>. It answers <b>kogo? czego?</b> (of whom? of what?).",
              points:[
                "Absence: <b>nie ma czasu</b> - there's no time",
                "Possession: <b>samochód brata</b> - brother's car",
                "Quantity: <b>szklanka wody</b> - a glass of water"
              ],
              examples:[
                { pl:"Nie ma mleka.", en:"There's no milk." },
                { pl:"To jest książka Anny.", en:"This is Anna's book." }
              ] },
            { front:"Signals that trigger Genitive",
              sub:"Memorize these triggers and half the work is done.",
              points:[
                "<b>nie ma</b> (there isn't) + Gen: <i>nie ma czasu</i>",
                "<b>Negated verbs</b>: nie mam <b>samochodu</b>, nie widzę <b>Anny</b>",
                "Prepositions: <b>z, do, od, dla, bez, u, obok</b>",
                "Numbers <b>5+</b> and <b>dużo/mało/trochę/ile</b>: dużo <b>ludzi</b>"
              ],
              note:"The negation rule is crucial: any direct object flips from Accusative to Genitive when the verb is negated. <b>Mam czas</b> \u2192 <b>Nie mam czasu</b>.",
              examples:[
                { pl:"Jadę do Warszawy.", en:"I'm going to Warsaw." },
                { pl:"Kupuję kawę bez cukru.", en:"I'm buying coffee without sugar." }
              ] },
            { front:"Masculine singular: -a or -u",
              sub:"The trickiest part of the Genitive - two possible endings.",
              table:[
                { g:"People & animals", e:"-a", ex:"brat \u2192 brata, kot \u2192 kota" },
                { g:"Tools, body parts, months", e:"-a", ex:"nóż \u2192 noża, palec \u2192 palca, styczeń \u2192 stycznia" },
                { g:"Abstract & uncountable", e:"-u", ex:"czas \u2192 czasu, cukier \u2192 cukru, sport \u2192 sportu" }
              ],
              explain:"Rule of thumb: <b>-a</b> for living things, tools, body parts, months, and currencies. <b>-u</b> for abstracts, liquids, materials, and feelings. Some common words break the pattern (chleb \u2192 chleba, dom \u2192 domu) - just memorize them.",
              examples:[
                { pl:"Nie ma brata.", en:"Brother isn't here." },
                { pl:"Nie ma cukru.", en:"There's no sugar." }
              ] },
            { front:"Feminine singular: -y or -i",
              sub:"Much simpler than masculine - just watch the last consonant.",
              table:[
                { g:"Default", e:"-y", ex:"kawa \u2192 kawy, kobieta \u2192 kobiety" },
                { g:"After k, g", e:"-i", ex:"książka \u2192 książki, noga \u2192 nogi" },
                { g:"After soft consonant", e:"-i", ex:"ulica \u2192 ulicy, kuchnia \u2192 kuchni" }
              ],
              explain:"If the word ends in <b>-ka, -ga</b>, use <b>-i</b>. If it ends in a soft consonant (like -nia, -cia), you also usually get <b>-i</b>. Everything else takes <b>-y</b>.",
              examples:[
                { pl:"Szklanka wody, proszę.", en:"A glass of water, please." },
                { pl:"Nie ma książki.", en:"The book isn't here." }
              ] },
            { front:"Neuter singular: -a",
              sub:"Neuter nouns almost always take -a in the Genitive.",
              table:[
                { g:"-o \u2192 -a", e:"okno \u2192 okna", ex:"Nie ma okna." },
                { g:"-e \u2192 -a", e:"mieszkanie \u2192 mieszkania", ex:"Szukam mieszkania." },
                { g:"-ę \u2192 -ęcia / -enia", e:"dziecko \u2192 dziecka", ex:"Nie mamy dziecka." }
              ],
              note:"'Dziecko' is neuter and follows the -o \u2192 -a rule in the singular. Its plural is famously irregular (dzieci).",
              examples:[
                { pl:"Nie ma piwa.", en:"There's no beer." },
                { pl:"Kawa bez mleka.", en:"Coffee without milk." }
              ] },
            { front:"Plural Genitive: the trickiest form",
              sub:"Plural Genitive endings depend on the gender and are notoriously varied.",
              table:[
                { g:"Masculine personal", e:"-\u00f3w", ex:"studentów, Polaków, panów" },
                { g:"Masc. non-personal", e:"-\u00f3w / -y / -i", ex:"kotów, samochodów, dni" },
                { g:"Feminine", e:"zero ending", ex:"kobiet, książek, sióstr" },
                { g:"Neuter", e:"zero ending", ex:"okien, mieszkań, dzieci" }
              ],
              explain:"Feminine and neuter often <b>drop the final vowel</b>, sometimes inserting an <b>-e-</b>: książka \u2192 książek, okno \u2192 okien. This is called the fleeting vowel.",
              examples:[
                { pl:"Pięciu studentów jest w klasie.", en:"Five students are in the class." },
                { pl:"Dużo książek na stole.", en:"Lots of books on the table." }
              ] },
            { front:"Watch out: negation flips Accusative to Genitive",
              sub:"This is the #1 mistake foreigners make in Polish.",
              points:[
                "<b>Mam kawę.</b> (Acc) \u2192 <b>Nie mam kawy.</b> (Gen)",
                "<b>Widzę Annę.</b> (Acc) \u2192 <b>Nie widzę Anny.</b> (Gen)",
                "<b>Lubię pizzę.</b> (Acc) \u2192 <b>Nie lubię pizzy.</b> (Gen)"
              ],
              explain:"Any verb that took a direct object in Accusative switches its object to Genitive under negation. There are no exceptions.",
              examples:[
                { pl:"Nie znam tego człowieka.", en:"I don't know this person." },
                { pl:"Nie piję kawy.", en:"I don't drink coffee." }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"Nie ma ___ w lodówce.", promptEn:"There's no milk in the fridge.",
              options:["mleka","mleko","mlekiem"], answer:"mleka",
              explain:"'Nie ma' always triggers Genitive. 'Mleko' is neuter, so -o \u2192 -a.", full:"Nie ma mleka w lodówce.", fullEn:"There's no milk in the fridge." },
            { type:"choose", prompt:"Poproszę kawę bez ___ .", promptEn:"I'd like a coffee without sugar.",
              options:["cukru","cukier","cukrem"], answer:"cukru",
              explain:"'Bez' (without) is one of the classic Genitive prepositions. 'Cukier' is masculine uncountable, so it takes -u.", full:"Poproszę kawę bez cukru.", fullEn:"I'd like a coffee without sugar." },
            { type:"choose", prompt:"Jadę do ___ jutro.", promptEn:"I'm going to Warsaw tomorrow.",
              options:["Warszawy","Warszawa","Warszawą"], answer:"Warszawy",
              explain:"'Do' (to a place) always takes Genitive. Feminine 'Warszawa' \u2192 'Warszawy'.", full:"Jadę do Warszawy jutro.", fullEn:"I'm going to Warsaw tomorrow." },
            { type:"choose", prompt:"Nie mam ___ .", promptEn:"I don't have time.",
              options:["czasu","czas","czasem"], answer:"czasu",
              explain:"Negated 'mieć' flips its object from Accusative to Genitive. 'Czas' is masculine abstract, so -u.", full:"Nie mam czasu.", fullEn:"I don't have time." },
            { type:"build", promptEn:"I don't drink coffee.",
              answer:["Nie","piję","kawy"],
              explain:"Negated verb \u2192 Genitive object. Feminine 'kawa' \u2192 'kawy'.", full:"Nie piję kawy.", fullEn:"I don't drink coffee." },
            { type:"choose", prompt:"To jest samochód ___ .", promptEn:"This is my brother's car.",
              options:["brata","brat","bratem"], answer:"brata",
              explain:"Possession \u2192 Genitive. 'Brat' is a living being (masculine personal), so it takes -a.", full:"To jest samochód brata.", fullEn:"This is my brother's car." },
            { type:"choose", prompt:"Dużo ___ jest w klasie.", promptEn:"There are lots of students in class.",
              options:["studentów","studenci","studentom"], answer:"studentów",
              explain:"'Dużo' triggers Genitive plural. Masculine personal plural takes -ów.", full:"Dużo studentów jest w klasie.", fullEn:"There are lots of students in class." },
            { type:"build", promptEn:"There's no bread.",
              answer:["Nie","ma","chleba"],
              explain:"'Nie ma' + Genitive. 'Chleb' (bread) is one of those masculine words that takes -a even though it's uncountable.", full:"Nie ma chleba.", fullEn:"There's no bread." },
            { type:"choose", prompt:"Szklanka ___ , proszę.", promptEn:"A glass of water, please.",
              options:["wody","woda","wodą"], answer:"wody",
              explain:"Quantity ('a glass of') \u2192 Genitive. Feminine 'woda' \u2192 'wody'.", full:"Szklanka wody, proszę.", fullEn:"A glass of water, please." },
            { type:"choose", prompt:"Wracam od ___ .", promptEn:"I'm coming back from the doctor.",
              options:["lekarza","lekarz","lekarzem"], answer:"lekarza",
              explain:"'Od' (from a person) takes Genitive. 'Lekarz' is masculine personal \u2192 -a.", full:"Wracam od lekarza.", fullEn:"I'm coming back from the doctor." },
            { type:"build", promptEn:"I don't have a sister.",
              answer:["Nie","mam","siostry"],
              explain:"Negated 'mieć' \u2192 Genitive. Feminine 'siostra' \u2192 'siostry'.", full:"Nie mam siostry.", fullEn:"I don't have a sister." },
            { type:"choose", prompt:"Ten prezent jest dla ___ .", promptEn:"This gift is for Anna.",
              options:["Anny","Anna","Anną"], answer:"Anny",
              explain:"'Dla' (for) takes Genitive. Feminine name 'Anna' \u2192 'Anny'.", full:"Ten prezent jest dla Anny.", fullEn:"This gift is for Anna." },
            { type:"choose", prompt:"Pięciu ___ pracuje tutaj.", promptEn:"Five men work here.",
              options:["mężczyzn","mężczyźni","mężczyzną"], answer:"mężczyzn",
              explain:"Numbers 5+ trigger Genitive plural. Note the 'zero ending' plural: mężczyźni \u2192 mężczyzn.", full:"Pięciu mężczyzn pracuje tutaj.", fullEn:"Five men work here." },
            { type:"build", promptEn:"I'm looking for an apartment.",
              answer:["Szukam","mieszkania"],
              explain:"'Szukać' (to look for) always takes Genitive. Neuter 'mieszkanie' \u2192 'mieszkania'.", full:"Szukam mieszkania.", fullEn:"I'm looking for an apartment." }
          ]
        },
        {
          name: "Celownik (Dative)", emoji: "\uD83C\uDF81", kind: "grammar", chip: "Grammar A1",
          desc: "The 'to / for' case: indirect objects and how you feel",
          teach: [
            { front:"What the Dative does",
              sub:"The Dative marks the <b>recipient</b> - the person you give, tell, or show something to. It answers <b>komu? czemu?</b> (to whom?).",
              points:[
                "Giving: <b>Daję Ani prezent.</b> - I'm giving Anna a gift.",
                "Telling: <b>Mówię koledze prawdę.</b> - I'm telling my colleague the truth.",
                "Helping: <b>Pomagam mamie.</b> - I'm helping mom."
              ],
              examples:[
                { pl:"Dziękuję koledze.", en:"Thank you (to my colleague)." },
                { pl:"Kupię bratu książkę.", en:"I'll buy my brother a book." }
              ] },
            { front:"Signals that trigger Dative",
              sub:"Certain verbs always take a Dative object - just memorize the list.",
              points:[
                "<b>dawać / dać</b> (to give)",
                "<b>pomagać</b> (to help)",
                "<b>mówić / powiedzieć</b> (to say to)",
                "<b>dziękować</b> (to thank)",
                "<b>ufać</b> (to trust), <b>wierzyć</b> (to believe)",
                "Feelings: <b>jest mi zimno/gorąco/smutno</b> - I feel cold/hot/sad"
              ],
              note:"'Jest mi...' is one of the most common Dative constructions in daily speech. Master it and you can express emotions and physical states.",
              examples:[
                { pl:"Jest mi zimno.", en:"I'm cold. (lit: it's cold to me)" },
                { pl:"Pomagam mamie w kuchni.", en:"I'm helping mom in the kitchen." }
              ] },
            { front:"Masculine singular: -owi (usually)",
              sub:"Most masculine nouns take -owi, but a small group of common words take -u.",
              table:[
                { g:"Default: -owi", e:"student \u2192 studentowi", ex:"Daję studentowi książkę." },
                { g:"Default: -owi", e:"lekarz \u2192 lekarzowi", ex:"Dziękuję lekarzowi." },
                { g:"Exceptions: -u", e:"brat \u2192 bratu, pan \u2192 panu", ex:"Powiem bratu." },
                { g:"Exceptions: -u", e:"ojciec \u2192 ojcu, chłopiec \u2192 chłopcu", ex:"Kupię chłopcu prezent." }
              ],
              explain:"Almost every masculine noun takes <b>-owi</b>. The main exceptions to memorize: <b>brat, pan, ojciec, chłopiec, ksiądz, Bóg, kot, pies</b> - all take <b>-u</b>.",
              note:"These -u exceptions are all extremely common words, so you'll drill them naturally in daily speech.",
              examples:[
                { pl:"Daję studentowi książkę.", en:"I'm giving the student a book." },
                { pl:"Powiem bratu.", en:"I'll tell my brother." }
              ] },
            { front:"Feminine singular: -e or -i",
              sub:"Feminine Dative often changes the final consonant - watch closely.",
              table:[
                { g:"Default", e:"-e (with softening)", ex:"kobieta \u2192 kobiecie, siostra \u2192 siostrze" },
                { g:"After k, g", e:"-ce, -dze", ex:"Polka \u2192 Polce, koleżanka \u2192 koleżance" },
                { g:"Soft ending", e:"-i", ex:"kuchnia \u2192 kuchni, pani \u2192 pani" }
              ],
              explain:"The Dative causes consonant softening: <b>t \u2192 ci</b>, <b>d \u2192 dzi</b>, <b>r \u2192 rz</b>, <b>k \u2192 c</b>, <b>g \u2192 dz</b>. That's why 'kobieta' becomes 'kobiecie', not 'kobiete'.",
              examples:[
                { pl:"Kupię siostrze prezent.", en:"I'll buy my sister a gift." },
                { pl:"Pomagam mamie.", en:"I'm helping mom." }
              ] },
            { front:"Neuter singular: -u",
              sub:"Neuter is easy in the Dative - almost always -u.",
              table:[
                { g:"-o \u2192 -u", e:"dziecko \u2192 dziecku", ex:"Kupię dziecku lody." },
                { g:"-e \u2192 -u", e:"pole \u2192 polu", ex:"Idę ku polu." },
                { g:"-ę \u2192 -ęciu", e:"imię \u2192 imieniu", ex:"(rare)" }
              ],
              examples:[
                { pl:"Daję dziecku zabawkę.", en:"I'm giving the child a toy." }
              ] },
            { front:"Plural Dative: -om",
              sub:"The easiest plural in all of Polish. One ending fits every gender.",
              table:[
                { g:"Masculine personal", e:"-om", ex:"studentom, panom, kolegom" },
                { g:"Masc. non-personal", e:"-om", ex:"kotom, samochodom" },
                { g:"Feminine", e:"-om", ex:"kobietom, siostrom, książkom" },
                { g:"Neuter", e:"-om", ex:"dzieciom, oknom" }
              ],
              explain:"If you remember one ending in all of Polish grammar, make it plural Dative <b>-om</b>. It never varies.",
              examples:[
                { pl:"Pomagam kolegom.", en:"I'm helping my colleagues." },
                { pl:"Kupuję prezenty dzieciom.", en:"I'm buying gifts for the children." }
              ] },
            { front:"The pronoun forms you'll use every day",
              sub:"Dative pronouns are extremely common in daily speech.",
              table:[
                { g:"to me", e:"mi", ex:"Jest mi zimno." },
                { g:"to you (sg)", e:"ci", ex:"Powiem ci prawdę." },
                { g:"to him/it", e:"mu", ex:"Daję mu książkę." },
                { g:"to her", e:"jej", ex:"Kupię jej prezent." },
                { g:"to us / to them", e:"nam / im", ex:"Pomóż nam!" }
              ],
              note:"<b>Jest mi ciekawie / smutno / dobrze</b> - these emotion patterns will feel unusual at first but Poles use them constantly.",
              examples:[
                { pl:"Jest mi bardzo miło.", en:"I'm very pleased. (lit: it's nice to me)" }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"Daję ___ prezent.", promptEn:"I'm giving Anna a gift.",
              options:["Ani","Anna","Annie"], answer:"Ani",
              explain:"'Anna' takes the same Dative form 'Ani' in colloquial speech - soft ending drops to -i.", full:"Daję Ani prezent.", fullEn:"I'm giving Anna a gift." },
            { type:"choose", prompt:"Jest ___ zimno.", promptEn:"I'm cold.",
              options:["mi","ja","mnie"], answer:"mi",
              explain:"Feelings use 'jest' + Dative pronoun. 'Mi' is the Dative of 'ja' (I).", full:"Jest mi zimno.", fullEn:"I'm cold." },
            { type:"choose", prompt:"Pomagam ___ w kuchni.", promptEn:"I'm helping mom in the kitchen.",
              options:["mamie","mama","mamą"], answer:"mamie",
              explain:"'Pomagać' takes Dative. Feminine 'mama' \u2192 'mamie' (m stays soft).", full:"Pomagam mamie w kuchni.", fullEn:"I'm helping mom in the kitchen." },
            { type:"build", promptEn:"I'm giving the child a toy.",
              answer:["Daję","dziecku","zabawkę"],
              explain:"'Dać' takes Dative for the recipient. Neuter 'dziecko' \u2192 'dziecku'.", full:"Daję dziecku zabawkę.", fullEn:"I'm giving the child a toy." },
            { type:"choose", prompt:"Dziękuję ___ za pomoc.", promptEn:"I thank the doctor for the help.",
              options:["lekarzowi","lekarza","lekarzem"], answer:"lekarzowi",
              explain:"'Dziękować' takes Dative. Masculine 'lekarz' \u2192 'lekarzowi' (default -owi).", full:"Dziękuję lekarzowi za pomoc.", fullEn:"I thank the doctor for the help." },
            { type:"build", promptEn:"I'll tell my brother.",
              answer:["Powiem","bratu"],
              explain:"'Mówić / powiedzieć' takes Dative. 'Brat' is one of the exception words - takes -u, not -owi.", full:"Powiem bratu.", fullEn:"I'll tell my brother." },
            { type:"choose", prompt:"Kupuję prezenty ___ .", promptEn:"I'm buying gifts for the children.",
              options:["dzieciom","dzieci","dziećmi"], answer:"dzieciom",
              explain:"Plural Dative always ends in -om, no matter the gender.", full:"Kupuję prezenty dzieciom.", fullEn:"I'm buying gifts for the children." },
            { type:"choose", prompt:"Nie wierzę ___ .", promptEn:"I don't believe him.",
              options:["mu","go","jego"], answer:"mu",
              explain:"'Wierzyć' takes Dative. 'Mu' is the Dative of 'on' (he).", full:"Nie wierzę mu.", fullEn:"I don't believe him." },
            { type:"build", promptEn:"Help us!",
              answer:["Pomóż","nam"],
              explain:"'Pomóc' + Dative. 'Nam' = to us.", full:"Pomóż nam!", fullEn:"Help us!" },
            { type:"choose", prompt:"Powiedz ___ , że wracam.", promptEn:"Tell her that I'm coming back.",
              options:["jej","ją","ona"], answer:"jej",
              explain:"'Powiedzieć' + Dative. 'Jej' = to her.", full:"Powiedz jej, że wracam.", fullEn:"Tell her that I'm coming back." },
            { type:"build", promptEn:"I'm giving the student a book.",
              answer:["Daję","studentowi","książkę"],
              explain:"'Dać' + Dative recipient. Masculine 'student' takes the default -owi.", full:"Daję studentowi książkę.", fullEn:"I'm giving the student a book." },
            { type:"choose", prompt:"Jest ___ smutno.", promptEn:"He is sad.",
              options:["mu","on","jego"], answer:"mu",
              explain:"Feelings use 'jest' + Dative pronoun. 'Mu' = to him.", full:"Jest mu smutno.", fullEn:"He is sad." },
            { type:"choose", prompt:"Kupię ___ nowy telefon.", promptEn:"I'll buy my sister a new phone.",
              options:["siostrze","siostra","siostrą"], answer:"siostrze",
              explain:"'Kupić' takes Dative for the recipient. Feminine 'siostra' \u2192 'siostrze' with r softening to rz.", full:"Kupię siostrze nowy telefon.", fullEn:"I'll buy my sister a new phone." },
            { type:"build", promptEn:"I'll show you the way.",
              answer:["Pokażę","ci","drogę"],
              explain:"'Pokazać' + Dative recipient. 'Ci' = to you (informal singular).", full:"Pokażę ci drogę.", fullEn:"I'll show you the way." }
          ]
        },
        {
          name: "Biernik (Accusative)", emoji: "\uD83C\uDFAF", kind: "grammar", chip: "Grammar A1",
          desc: "The direct object case: what you eat, buy, love, see",
          teach: [
            { front:"What the Accusative does",
              sub:"The Accusative marks the <b>direct object</b> - the thing being acted on. It answers <b>kogo? co?</b> (whom? what?).",
              points:[
                "<b>Mam kawę.</b> - I have coffee.",
                "<b>Lubię pizzę.</b> - I like pizza.",
                "<b>Kupuję samochód.</b> - I'm buying a car."
              ],
              examples:[
                { pl:"Widzę Annę.", en:"I see Anna." },
                { pl:"Jem jabłko.", en:"I'm eating an apple." }
              ] },
            { front:"Signals that trigger Accusative",
              sub:"Any verb that acts on a direct object usually takes Accusative.",
              points:[
                "<b>Mam, lubię, chcę, widzę, znam, kupuję, jem, piję</b> - all take Accusative objects",
                "Prepositions of movement: <b>na, w, przez, o</b>: <i>jadę na wakacje</i>",
                "Time: <b>w</b> + day of week, <b>o</b> + hour, <b>za</b> + time from now"
              ],
              note:"When you negate these verbs, the object flips to Genitive: <b>Mam kawę</b> \u2192 <b>Nie mam kawy</b>.",
              examples:[
                { pl:"Jem obiad o drugiej.", en:"I'm eating lunch at two." },
                { pl:"Jadę na spotkanie.", en:"I'm going to a meeting." }
              ] },
            { front:"Feminine singular: -\u0119",
              sub:"The most recognizable Polish ending - one letter, one rule.",
              table:[
                { g:"-a \u2192 -\u0119", e:"kawa \u2192 kawę", ex:"Piję kawę." },
                { g:"-a \u2192 -\u0119", e:"kobieta \u2192 kobietę", ex:"Widzę kobietę." },
                { g:"-a \u2192 -\u0119", e:"Anna \u2192 Annę", ex:"Znam Annę." }
              ],
              explain:"If you learn only one Accusative rule, learn this one: feminine <b>-a</b> becomes <b>-ę</b>. It's everywhere in daily speech.",
              examples:[
                { pl:"Kupuję gazetę.", en:"I'm buying a newspaper." },
                { pl:"Lubię muzykę.", en:"I like music." }
              ] },
            { front:"Neuter: no change",
              sub:"Neuter nouns look identical in Accusative and Nominative.",
              table:[
                { g:"-o = -o", e:"okno = okno", ex:"Widzę okno." },
                { g:"-e = -e", e:"mieszkanie = mieszkanie", ex:"Mam mieszkanie." },
                { g:"-ę = -ę", e:"imię = imię", ex:"Znam twoje imię." }
              ],
              explain:"For neuter nouns, don't do anything - use the dictionary form.",
              examples:[
                { pl:"Jem jabłko.", en:"I'm eating an apple." }
              ] },
            { front:"Masculine: the animacy trap",
              sub:"Masculine nouns split into two groups, and each behaves differently.",
              table:[
                { g:"Living (people, animals)", e:"= Genitive", ex:"kot \u2192 kota, brat \u2192 brata, człowiek \u2192 człowieka" },
                { g:"Non-living (objects)", e:"= Nominative", ex:"dom = dom, samochód = samochód, telefon = telefon" }
              ],
              explain:"<b>Living things borrow their Accusative from the Genitive.</b> Non-living stay in Nominative form. So: <i>Widzę kota</i> (living \u2192 -a) vs <i>Widzę dom</i> (thing \u2192 no change).",
              note:"This is the single most important masculine rule to internalize. It also affects adjectives and pronouns: <i>Mam dobrego brata</i> vs <i>Mam dobry samochód</i>.",
              examples:[
                { pl:"Znam twojego brata.", en:"I know your brother." },
                { pl:"Kupuję nowy telefon.", en:"I'm buying a new phone." }
              ] },
            { front:"Plural Accusative: two forms again",
              sub:"Plural repeats the animacy split, but at the group level.",
              table:[
                { g:"Masculine personal (oni)", e:"= Genitive plural", ex:"studenci \u2192 studentów" },
                { g:"Everything else (one)", e:"= Nominative plural", ex:"koty, książki, dzieci" }
              ],
              explain:"Only groups of men (or mixed) act like living-Accusatives. Groups of women, animals, and things use the Nominative plural unchanged.",
              examples:[
                { pl:"Znam tych studentów.", en:"I know these students." },
                { pl:"Kupuję nowe książki.", en:"I'm buying new books." }
              ] },
            { front:"Personal pronouns in Accusative",
              sub:"You need these constantly. Short and long forms exist for emphasis.",
              table:[
                { g:"me", e:"mnie / mi\u0119", ex:"Kocham cię." },
                { g:"you (sg)", e:"ciebie / cię", ex:"Widzę cię!" },
                { g:"him", e:"jego / go", ex:"Znam go." },
                { g:"her", e:"ją", ex:"Lubię ją." },
                { g:"us / them (m) / them (rest)", e:"nas / ich / je", ex:"Widzę ich." }
              ],
              note:"The short forms (mię, cię, go) can never start a sentence and are unstressed. The long forms (mnie, ciebie, jego) go at the start or when emphasized.",
              examples:[
                { pl:"Kocham cię.", en:"I love you." },
                { pl:"Ciebie kocham, nie jego!", en:"It's you I love, not him!" }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"Piję ___ .", promptEn:"I'm drinking coffee.",
              options:["kawę","kawa","kawy"], answer:"kawę",
              explain:"'Pić' takes Accusative. Feminine 'kawa' \u2192 'kawę'.", full:"Piję kawę.", fullEn:"I'm drinking coffee." },
            { type:"choose", prompt:"Widzę ___ .", promptEn:"I see the cat.",
              options:["kota","kot","kotu"], answer:"kota",
              explain:"'Widzieć' takes Accusative. 'Kot' is a living being (animal), so Accusative = Genitive form 'kota'.", full:"Widzę kota.", fullEn:"I see the cat." },
            { type:"choose", prompt:"Kupuję nowy ___ .", promptEn:"I'm buying a new phone.",
              options:["telefon","telefonu","telefonem"], answer:"telefon",
              explain:"'Telefon' is a masculine object (non-living), so Accusative = Nominative. No change.", full:"Kupuję nowy telefon.", fullEn:"I'm buying a new phone." },
            { type:"build", promptEn:"I'm eating an apple.",
              answer:["Jem","jabłko"],
              explain:"'Jabłko' is neuter, so Accusative = Nominative. No change.", full:"Jem jabłko.", fullEn:"I'm eating an apple." },
            { type:"choose", prompt:"Znam ___ .", promptEn:"I know Anna.",
              options:["Annę","Anna","Anny"], answer:"Annę",
              explain:"'Znać' takes Accusative. Feminine name 'Anna' \u2192 'Annę'.", full:"Znam Annę.", fullEn:"I know Anna." },
            { type:"choose", prompt:"Lubię ___ .", promptEn:"I like this book.",
              options:["tę książkę","ta książka","tej książki"], answer:"tę książkę",
              explain:"'Lubić' takes Accusative. Feminine 'książka' \u2192 'książkę', and 'ta' \u2192 'tę'.", full:"Lubię tę książkę.", fullEn:"I like this book." },
            { type:"build", promptEn:"I love you.",
              answer:["Kocham","cię"],
              explain:"'Kochać' takes Accusative. 'Cię' is the short Accusative of 'ty' (you), placed after the verb.", full:"Kocham cię.", fullEn:"I love you." },
            { type:"choose", prompt:"Mam dobrego ___ .", promptEn:"I have a good brother.",
              options:["brata","brat","bratu"], answer:"brata",
              explain:"'Brat' is masculine living, so Accusative = Genitive 'brata'. The adjective 'dobrego' also takes the living form.", full:"Mam dobrego brata.", fullEn:"I have a good brother." },
            { type:"choose", prompt:"Widzę tych ___ .", promptEn:"I see these students.",
              options:["studentów","studenci","studentom"], answer:"studentów",
              explain:"Masculine personal plural in Accusative = Genitive plural, so 'studenci' \u2192 'studentów'.", full:"Widzę tych studentów.", fullEn:"I see these students." },
            { type:"build", promptEn:"I like music.",
              answer:["Lubię","muzykę"],
              explain:"'Lubić' + Accusative. Feminine 'muzyka' \u2192 'muzykę'.", full:"Lubię muzykę.", fullEn:"I like music." },
            { type:"choose", prompt:"Znam ___ .", promptEn:"I know him.",
              options:["go","mu","jego"], answer:"go",
              explain:"'Znać' + Accusative. 'Go' is the unstressed Accusative of 'on' - the everyday form.", full:"Znam go.", fullEn:"I know him." },
            { type:"choose", prompt:"Jadę na ___ .", promptEn:"I'm going on vacation.",
              options:["wakacje","wakacji","wakacjach"], answer:"wakacje",
              explain:"'Na' + Accusative for direction/purpose. 'Wakacje' is plural neuter-form (only used in plural), Nominative = Accusative.", full:"Jadę na wakacje.", fullEn:"I'm going on vacation." },
            { type:"build", promptEn:"I'm buying new books.",
              answer:["Kupuję","nowe","książki"],
              explain:"Feminine plural things \u2192 Accusative = Nominative plural 'książki'.", full:"Kupuję nowe książki.", fullEn:"I'm buying new books." },
            { type:"choose", prompt:"Mam ładny ___ .", promptEn:"I have a nice house.",
              options:["dom","domu","domem"], answer:"dom",
              explain:"'Dom' is masculine non-living, so Accusative = Nominative. 'Ładny' also stays in the non-living form.", full:"Mam ładny dom.", fullEn:"I have a nice house." },
            { type:"build", promptEn:"I love her.",
              answer:["Kocham","ją"],
              explain:"'Kochać' + Accusative. 'Ją' is the Accusative of 'ona' (she).", full:"Kocham ją.", fullEn:"I love her." }
          ]
        },
        {
          name: "Narzędnik (Instrumental)", emoji: "\uD83D\uDD27", kind: "grammar", chip: "Grammar A1",
          desc: "The 'with / by' case: means, transport, and being someone",
          teach: [
            { front:"What the Instrumental does",
              sub:"The Instrumental shows <b>the means or the identity</b>. It answers <b>kim? czym?</b> (with whom? with what?).",
              points:[
                "Tools: <b>Piszę długopisem.</b> - I'm writing with a pen.",
                "Transport: <b>Jadę autobusem.</b> - I'm going by bus.",
                "Identity: <b>Jestem lekarzem.</b> - I am a doctor."
              ],
              examples:[
                { pl:"Piję kawę z mlekiem.", en:"I drink coffee with milk." },
                { pl:"Interesuję się muzyką.", en:"I'm interested in music." }
              ] },
            { front:"Signals that trigger Instrumental",
              sub:"A short, memorable list of triggers.",
              points:[
                "<b>Być + profession/role</b>: <i>Jestem studentem.</i>",
                "<b>Transport</b>: jadę <b>autobusem, pociągiem, samochodem</b>",
                "<b>Z</b> = with: kawa <b>z mlekiem</b>",
                "<b>Interesować się, zajmować się</b> + Instr: <i>Interesuję się sportem.</i>",
                "<b>Przed, za, nad, pod, między</b> + Instr (location)"
              ],
              note:"'Z' has two meanings: with (Instrumental) and from (Genitive). Context tells you which: <i>z mlekiem</i> (with milk, Instr) vs <i>z Polski</i> (from Poland, Gen).",
              examples:[
                { pl:"Rozmawiam z Anną.", en:"I'm talking with Anna." }
              ] },
            { front:"Masculine & Neuter singular: -em",
              sub:"One ending, two genders - the simplest part of the Instrumental.",
              table:[
                { g:"Masculine", e:"-em", ex:"student \u2192 studentem, kot \u2192 kotem" },
                { g:"Neuter", e:"-em", ex:"okno \u2192 oknem, dziecko \u2192 dzieckiem" },
                { g:"After k, g", e:"-iem", ex:"pociąg \u2192 pociągiem, Polak \u2192 Polakiem" }
              ],
              explain:"After <b>k</b> or <b>g</b>, insert an <b>i</b>: pociąg \u2192 pociągiem, not pociągem. This preserves the soft sound.",
              examples:[
                { pl:"Jadę pociągiem.", en:"I'm going by train." },
                { pl:"Piszę długopisem.", en:"I'm writing with a pen." }
              ] },
            { front:"Feminine singular: -\u0105",
              sub:"Another instantly recognizable Polish ending.",
              table:[
                { g:"-a \u2192 -\u0105", e:"kobieta \u2192 kobietą", ex:"Rozmawiam z kobietą." },
                { g:"-a \u2192 -\u0105", e:"kawa \u2192 kawą", ex:"z kawą i ciastem" },
                { g:"-a \u2192 -\u0105", e:"Anna \u2192 Anną", ex:"z Anną" }
              ],
              explain:"Feminine <b>-a</b> becomes <b>-ą</b>. It's the mirror image of the Accusative -ę. Both endings are hallmarks of Polish.",
              examples:[
                { pl:"Kawa z mlekiem, proszę.", en:"Coffee with milk, please." },
                { pl:"Interesuję się fotografią.", en:"I'm interested in photography." }
              ] },
            { front:"Plural Instrumental: -ami",
              sub:"Almost universally -ami, regardless of gender.",
              table:[
                { g:"Masculine", e:"-ami", ex:"studentami, kotami, pociągami" },
                { g:"Feminine", e:"-ami", ex:"kobietami, książkami" },
                { g:"Neuter", e:"-ami", ex:"oknami, dziećmi (!)" }
              ],
              note:"A few very common words take <b>-mi</b> instead: <b>dziećmi</b> (children), <b>ludźmi</b> (people), <b>braćmi</b> (brothers). Memorize these three.",
              examples:[
                { pl:"Idę z przyjaciółmi.", en:"I'm going with friends." }
              ] },
            { front:"Being someone: profession & role",
              sub:"After <b>być</b>, Polish always uses Instrumental for profession, nationality, role.",
              points:[
                "<b>Jestem studentem.</b> - I am a student.",
                "<b>Ona jest lekarką.</b> - She is a doctor.",
                "<b>Chcę być inżynierem.</b> - I want to be an engineer."
              ],
              explain:"Compare: <i>To jest lekarz</i> (Nom - 'This is a doctor', pointing) vs <i>Jestem lekarzem</i> (Instr - 'I am a doctor', identifying). The pattern with <b>to jest</b> is the exception that stays in Nominative.",
              examples:[
                { pl:"Mój tata jest kierowcą.", en:"My dad is a driver." },
                { pl:"Chciałabym być nauczycielką.", en:"I would like to be a teacher." }
              ] },
            { front:"Instrumental pronouns",
              sub:"Compact and common - you'll hear these constantly.",
              table:[
                { g:"with me", e:"ze mną", ex:"Chodź ze mną." },
                { g:"with you (sg)", e:"z tobą", ex:"Rozmawiam z tobą." },
                { g:"with him / her", e:"z nim / z nią", ex:"z nim wczoraj" },
                { g:"with us / with them", e:"z nami / z nimi", ex:"z nami na kawie" }
              ],
              note:"Notice <b>ze mną</b> - not 'z mną'. The extra 'e' makes it pronounceable.",
              examples:[
                { pl:"Chcesz iść z nami?", en:"Do you want to go with us?" }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"Jadę ___ do pracy.", promptEn:"I go to work by bus.",
              options:["autobusem","autobus","autobusu"], answer:"autobusem",
              explain:"Transport takes Instrumental. Masculine 'autobus' \u2192 'autobusem'.", full:"Jadę autobusem do pracy.", fullEn:"I go to work by bus." },
            { type:"choose", prompt:"Piję kawę z ___ .", promptEn:"I drink coffee with milk.",
              options:["mlekiem","mleko","mleka"], answer:"mlekiem",
              explain:"'Z' meaning 'with' takes Instrumental. Neuter 'mleko' \u2192 'mlekiem'.", full:"Piję kawę z mlekiem.", fullEn:"I drink coffee with milk." },
            { type:"choose", prompt:"Jestem ___ .", promptEn:"I am a student.",
              options:["studentem","student","studenta"], answer:"studentem",
              explain:"'Być' + profession takes Instrumental. Masculine \u2192 -em.", full:"Jestem studentem.", fullEn:"I am a student." },
            { type:"build", promptEn:"I'm going by train.",
              answer:["Jadę","pociągiem"],
              explain:"Transport + Instrumental. Note: after 'g' we insert 'i' \u2192 'pociągiem', not 'pociągem'.", full:"Jadę pociągiem.", fullEn:"I'm going by train." },
            { type:"choose", prompt:"Rozmawiam z ___ .", promptEn:"I'm talking with Anna.",
              options:["Anną","Anna","Annę"], answer:"Anną",
              explain:"'Z' + Instrumental. Feminine 'Anna' \u2192 'Anną'.", full:"Rozmawiam z Anną.", fullEn:"I'm talking with Anna." },
            { type:"choose", prompt:"Ona jest ___ .", promptEn:"She is a doctor.",
              options:["lekarką","lekarka","lekarki"], answer:"lekarką",
              explain:"'Być' + profession \u2192 Instrumental. Feminine 'lekarka' \u2192 'lekarką'.", full:"Ona jest lekarką.", fullEn:"She is a doctor." },
            { type:"build", promptEn:"I'm interested in sports.",
              answer:["Interesuję","się","sportem"],
              explain:"'Interesować się' always takes Instrumental. Masculine 'sport' \u2192 'sportem'.", full:"Interesuję się sportem.", fullEn:"I'm interested in sports." },
            { type:"choose", prompt:"Chodź ___ do kina.", promptEn:"Come with me to the cinema.",
              options:["ze mną","z ja","ze mnie"], answer:"ze mną",
              explain:"'With me' is always 'ze mną' - note the extra 'e' for pronounceability.", full:"Chodź ze mną do kina.", fullEn:"Come with me to the cinema." },
            { type:"choose", prompt:"Piszę ___ .", promptEn:"I write with a pen.",
              options:["długopisem","długopis","długopisu"], answer:"długopisem",
              explain:"Tool \u2192 Instrumental. Masculine 'długopis' \u2192 'długopisem'.", full:"Piszę długopisem.", fullEn:"I write with a pen." },
            { type:"build", promptEn:"I want to be an engineer.",
              answer:["Chcę","być","inżynierem"],
              explain:"'Być' + profession \u2192 Instrumental. Masculine 'inżynier' \u2192 'inżynierem'.", full:"Chcę być inżynierem.", fullEn:"I want to be an engineer." },
            { type:"choose", prompt:"Idę z ___ .", promptEn:"I'm going with friends.",
              options:["przyjaciółmi","przyjaciele","przyjaciół"], answer:"przyjaciółmi",
              explain:"Plural Instrumental. 'Przyjaciele' is one of the special -mi words.", full:"Idę z przyjaciółmi.", fullEn:"I'm going with friends." },
            { type:"choose", prompt:"Mój tata jest ___ .", promptEn:"My dad is a driver.",
              options:["kierowcą","kierowca","kierowce"], answer:"kierowcą",
              explain:"'Być' + profession \u2192 Instrumental. Masculine 'kierowca' (ends in -a but is masculine) \u2192 'kierowcą'.", full:"Mój tata jest kierowcą.", fullEn:"My dad is a driver." },
            { type:"build", promptEn:"Coffee with milk, please.",
              answer:["Kawa","z","mlekiem","proszę"],
              explain:"'Z' meaning 'with' + Instrumental. Neuter 'mleko' \u2192 'mlekiem'.", full:"Kawa z mlekiem, proszę.", fullEn:"Coffee with milk, please." },
            { type:"choose", prompt:"Interesuję się polską ___ .", promptEn:"I'm interested in Polish culture.",
              options:["kulturą","kultura","kulturę"], answer:"kulturą",
              explain:"'Interesować się' + Instrumental. Feminine 'kultura' \u2192 'kulturą'.", full:"Interesuję się polską kulturą.", fullEn:"I'm interested in Polish culture." }
          ]
        },
        {
          name: "Miejscownik (Locative)", emoji: "\uD83D\uDCCD", kind: "grammar", chip: "Grammar A1",
          desc: "The location case: where things are, what you talk about",
          teach: [
            { front:"What the Locative does",
              sub:"The Locative marks <b>location and topic</b>. It answers <b>o kim? o czym? gdzie?</b> - about whom, about what, where.",
              points:[
                "Location: <b>w domu</b> - at home, <b>na stole</b> - on the table",
                "Topic: <b>rozmawiamy o pogodzie</b> - we're talking about the weather",
                "Never appears without a preposition."
              ],
              examples:[
                { pl:"Mieszkam w Warszawie.", en:"I live in Warsaw." },
                { pl:"Myślę o wakacjach.", en:"I'm thinking about vacation." }
              ] },
            { front:"Signals: only after prepositions",
              sub:"The Locative NEVER appears on its own. Five prepositions always trigger it.",
              points:[
                "<b>w</b> - in: <i>w domu, w Warszawie</i>",
                "<b>na</b> - on: <i>na stole, na ulicy</i>",
                "<b>o</b> - about: <i>o pracy, o książce</i>",
                "<b>przy</b> - at, near: <i>przy stole</i>",
                "<b>po</b> - after / around: <i>po pracy, po Warszawie</i>"
              ],
              note:"If you see one of these five prepositions AND you're describing where something is or what something is about, use Locative.",
              examples:[
                { pl:"Rozmawiamy o książce.", en:"We're talking about the book." },
                { pl:"Kot śpi na kanapie.", en:"The cat is sleeping on the couch." }
              ] },
            { front:"Masculine singular: -e or -u",
              sub:"The Locative softens the last consonant. Some common words take -u instead.",
              table:[
                { g:"Default -e (with softening)", e:"student \u2192 studencie", ex:"o studencie" },
                { g:"Default -e (with softening)", e:"brat \u2192 bracie, stół \u2192 stole", ex:"na stole" },
                { g:"After k, g, ch \u2192 -u", e:"pociąg \u2192 pociągu, dach \u2192 dachu", ex:"na dachu" },
                { g:"After soft cons. \u2192 -u", e:"nauczyciel \u2192 nauczycielu, koń \u2192 koniu", ex:"o nauczycielu" },
                { g:"Common exceptions \u2192 -u", e:"dom \u2192 domu, syn \u2192 synu, pan \u2192 panu", ex:"w domu" }
              ],
              explain:"The consonant changes are the same as in feminine Dative: <b>t\u2192ci, d\u2192dzi, r\u2192rz, s\u2192si, z\u2192zi</b>. Study 'student \u2192 studencie' and 'brat \u2192 bracie' as your models.",
              examples:[
                { pl:"Jestem w domu.", en:"I'm at home." },
                { pl:"Książka o studencie.", en:"A book about a student." }
              ] },
            { front:"Feminine singular: -e or -i",
              sub:"Same rules as feminine Dative - the two cases share a form.",
              table:[
                { g:"Default", e:"-e (with softening)", ex:"kobieta \u2192 kobiecie, praca \u2192 pracy" },
                { g:"After k, g", e:"-ce, -dze", ex:"Polka \u2192 Polce, książka \u2192 książce" },
                { g:"Soft ending", e:"-i", ex:"kuchnia \u2192 kuchni, ulica \u2192 ulicy" }
              ],
              explain:"Feminine Locative = feminine Dative. If you learned one, you know the other.",
              examples:[
                { pl:"Mieszkam w Warszawie.", en:"I live in Warsaw." },
                { pl:"Kot jest w kuchni.", en:"The cat is in the kitchen." }
              ] },
            { front:"Neuter singular: -e or -u",
              sub:"Similar to masculine, with the same softening rules.",
              table:[
                { g:"Default", e:"-e (softening)", ex:"okno \u2192 oknie, miasto \u2192 mieście" },
                { g:"After k, g, ch", e:"-u", ex:"mleko \u2192 mleku, ucho \u2192 uchu" },
                { g:"-ie \u2192 -iu", e:"-iu", ex:"mieszkanie \u2192 mieszkaniu" }
              ],
              examples:[
                { pl:"Kot śpi na oknie.", en:"The cat sleeps on the window." },
                { pl:"Mieszkam w mieszkaniu.", en:"I live in an apartment." }
              ] },
            { front:"Plural Locative: -ach",
              sub:"Easy plural: always -ach, for every gender.",
              table:[
                { g:"Masculine", e:"-ach", ex:"studentach, domach" },
                { g:"Feminine", e:"-ach", ex:"kobietach, książkach" },
                { g:"Neuter", e:"-ach", ex:"oknach, dzieciach" }
              ],
              explain:"Plural Locative is unmissable: <b>-ach</b> everywhere. If a word ends in -ach after a preposition, you're almost certainly in Locative.",
              examples:[
                { pl:"Myślę o wakacjach.", en:"I'm thinking about vacation." },
                { pl:"Kot bawi się w książkach.", en:"The cat plays in the books." }
              ] },
            { front:"'W' vs 'na': in or on?",
              sub:"The eternal question. There's a pattern - not a rule.",
              points:[
                "<b>w</b> = enclosed spaces: <i>w domu, w szkole, w Polsce, w mieszkaniu</i>",
                "<b>na</b> = open spaces & events: <i>na ulicy, na wakacjach, na koncercie</i>",
                "<b>na</b> = surfaces: <i>na stole, na podłodze, na ścianie</i>"
              ],
              note:"Many words are just conventional: <b>na uniwersytecie, na poczcie, w szkole, w kinie</b>. Memorize them with the preposition attached.",
              examples:[
                { pl:"Pracuję na uniwersytecie.", en:"I work at the university." },
                { pl:"Uczę się w szkole.", en:"I study at school." }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"Mieszkam w ___ .", promptEn:"I live in Warsaw.",
              options:["Warszawie","Warszawa","Warszawą"], answer:"Warszawie",
              explain:"'W' + Locative for a city. Feminine 'Warszawa' \u2192 'Warszawie'.", full:"Mieszkam w Warszawie.", fullEn:"I live in Warsaw." },
            { type:"choose", prompt:"Kot śpi na ___ .", promptEn:"The cat sleeps on the table.",
              options:["stole","stół","stołem"], answer:"stole",
              explain:"'Na' + Locative for surface. Masculine 'stół' \u2192 'stole' (with vowel shift ó\u2192o).", full:"Kot śpi na stole.", fullEn:"The cat sleeps on the table." },
            { type:"choose", prompt:"Rozmawiamy o ___ .", promptEn:"We're talking about the book.",
              options:["książce","książka","książkę"], answer:"książce",
              explain:"'O' (about) + Locative. Feminine 'książka' \u2192 'książce' (k \u2192 c softening).", full:"Rozmawiamy o książce.", fullEn:"We're talking about the book." },
            { type:"build", promptEn:"I am at home.",
              answer:["Jestem","w","domu"],
              explain:"'W' + Locative. 'Dom' is one of the exception words - takes -u, not -e.", full:"Jestem w domu.", fullEn:"I am at home." },
            { type:"choose", prompt:"Pracuję na ___ .", promptEn:"I work at the university.",
              options:["uniwersytecie","uniwersytet","uniwersytetem"], answer:"uniwersytecie",
              explain:"'Uniwersytet' is conventionally used with 'na'. Locative shows t \u2192 ci softening.", full:"Pracuję na uniwersytecie.", fullEn:"I work at the university." },
            { type:"choose", prompt:"Myślę o ___ .", promptEn:"I'm thinking about vacation.",
              options:["wakacjach","wakacje","wakacji"], answer:"wakacjach",
              explain:"'Wakacje' is plural-only. Plural Locative = -ach.", full:"Myślę o wakacjach.", fullEn:"I'm thinking about vacation." },
            { type:"choose", prompt:"Uczę się w ___ .", promptEn:"I study at school.",
              options:["szkole","szkoła","szkołę"], answer:"szkole",
              explain:"'W' + Locative for school. Feminine 'szkoła' \u2192 'szkole' (regular -e ending).", full:"Uczę się w szkole.", fullEn:"I study at school." },
            { type:"build", promptEn:"The cat is in the kitchen.",
              answer:["Kot","jest","w","kuchni"],
              explain:"'W' + Locative. Feminine 'kuchnia' has a soft ending, so \u2192 'kuchni'.", full:"Kot jest w kuchni.", fullEn:"The cat is in the kitchen." },
            { type:"choose", prompt:"Książka o ___ .", promptEn:"A book about the student.",
              options:["studencie","student","studenta"], answer:"studencie",
              explain:"'O' + Locative. Masculine 'student' \u2192 'studencie' with t \u2192 ci softening.", full:"Książka o studencie.", fullEn:"A book about the student." },
            { type:"build", promptEn:"I live in an apartment.",
              answer:["Mieszkam","w","mieszkaniu"],
              explain:"'W' + Locative. Neuter 'mieszkanie' (soft ending -ie) \u2192 'mieszkaniu'.", full:"Mieszkam w mieszkaniu.", fullEn:"I live in an apartment." },
            { type:"choose", prompt:"Jadę pociągiem po ___ .", promptEn:"I'm traveling by train around Poland.",
              options:["Polsce","Polska","Polską"], answer:"Polsce",
              explain:"'Po' (around) + Locative. Feminine 'Polska' \u2192 'Polsce' (k \u2192 c softening).", full:"Jadę pociągiem po Polsce.", fullEn:"I'm traveling by train around Poland." },
            { type:"choose", prompt:"Byłem na ___ wczoraj.", promptEn:"I was at a concert yesterday.",
              options:["koncercie","koncert","koncertu"], answer:"koncercie",
              explain:"'Na' + event + Locative. Masculine 'koncert' \u2192 'koncercie'.", full:"Byłem na koncercie wczoraj.", fullEn:"I was at a concert yesterday." },
            { type:"build", promptEn:"I'm thinking about my brother.",
              answer:["Myślę","o","bracie"],
              explain:"'O' + Locative. 'Brat' \u2192 'bracie' with t \u2192 ci softening.", full:"Myślę o bracie.", fullEn:"I'm thinking about my brother." },
            { type:"choose", prompt:"Kot jest na ___ .", promptEn:"The cat is on the couch.",
              options:["kanapie","kanapa","kanapę"], answer:"kanapie",
              explain:"'Na' + surface + Locative. Feminine 'kanapa' \u2192 'kanapie'.", full:"Kot jest na kanapie.", fullEn:"The cat is on the couch." }
          ]
        },
        {
          name: "Wołacz (Vocative)", emoji: "\uD83D\uDCE3", kind: "grammar", chip: "Grammar A1",
          desc: "The address case: calling someone by name or title",
          teach: [
            { front:"What the Vocative does",
              sub:"The Vocative is used to <b>address or call</b> someone directly. It's a special case for names, titles, and greetings.",
              points:[
                "Direct address: <b>Aniu, chodź tutaj!</b>",
                "In letters and emails: <b>Drogi Piotrze!</b>",
                "In greetings: <b>Dzień dobry, panie profesorze!</b>"
              ],
              examples:[
                { pl:"Aniu, gdzie jesteś?", en:"Anna, where are you?" },
                { pl:"Panie doktorze, mam pytanie.", en:"Doctor, I have a question." }
              ] },
            { front:"Signals: when to use it",
              sub:"The Vocative is only used when speaking TO someone.",
              points:[
                "Calling out to a person",
                "Starting a letter or email (\"Drogi/Droga...\")",
                "Formal addresses with pan / pani + title",
                "Emotional exclamations: <i>O Boże!</i>"
              ],
              note:"In casual modern Polish, the Vocative is <b>often replaced by the Nominative</b> for common names: 'Anna, chodź!' instead of 'Anno, chodź!' - but Aniu (diminutive) is very common.",
              examples:[
                { pl:"Mamo, gdzie klucze?", en:"Mom, where are the keys?" }
              ] },
            { front:"Feminine singular: -o or -u",
              sub:"Feminine names split into two groups: standard and affectionate.",
              table:[
                { g:"Standard names", e:"-o", ex:"Anna \u2192 Anno, Ewa \u2192 Ewo, mama \u2192 mamo" },
                { g:"Diminutives", e:"-u", ex:"Ania \u2192 Aniu, Kasia \u2192 Kasiu, babcia \u2192 babciu" },
                { g:"Soft ending", e:"-i", ex:"pani \u2192 pani (no change)" }
              ],
              explain:"Diminutive names (Ania, Kasia, Basia, Zosia) end in -a but take -u in Vocative. These are the affectionate everyday forms you'll hear all the time.",
              examples:[
                { pl:"Aniu, mam pytanie.", en:"Ania, I have a question." },
                { pl:"Mamo, kocham cię.", en:"Mom, I love you." }
              ] },
            { front:"Masculine singular: -e or -u",
              sub:"Masculine also splits, based on the type of noun.",
              table:[
                { g:"Default (formal)", e:"-e (with softening)", ex:"pan \u2192 panie, Piotr \u2192 Piotrze" },
                { g:"After k, g, ch", e:"-u", ex:"Marek \u2192 Marku, syn \u2192 synu" },
                { g:"Soft / diminutive", e:"-u", ex:"nauczyciel \u2192 nauczycielu, tato \u2192 tato" }
              ],
              explain:"Same softening rules as Locative: <b>t\u2192ci, d\u2192dzi, r\u2192rz</b>. So 'brat' \u2192 'bracie', 'Piotr' \u2192 'Piotrze'.",
              note:"'Bóg' becomes 'Boże' in the famous exclamation <b>O Boże!</b> (Oh my God!).",
              examples:[
                { pl:"Piotrze, gdzie jesteś?", en:"Piotr, where are you?" },
                { pl:"Panie profesorze, dziękuję.", en:"Professor, thank you." }
              ] },
            { front:"Neuter & plural: mostly unchanged",
              sub:"For neuter singular and all plurals, Vocative = Nominative.",
              table:[
                { g:"Neuter singular", e:"= Nominative", ex:"dziecko \u2192 dziecko!" },
                { g:"Any plural", e:"= Nominative", ex:"koleżanki! studenci! dzieci!" }
              ],
              explain:"You only need to remember the singular masculine and feminine forms. Everything else stays as-is.",
              examples:[
                { pl:"Dzieci, chodźcie tu!", en:"Kids, come here!" },
                { pl:"Kochani, dziękuję!", en:"Dear ones, thank you!" }
              ] },
            { front:"The 'pan / pani' formula",
              sub:"For formal address, use <b>pan / pani</b> + title, both in Vocative.",
              table:[
                { g:"Sir", e:"panie", ex:"Panie doktorze!" },
                { g:"Ma'am", e:"pani", ex:"Pani doktor! (title often stays in Nom)" },
                { g:"Professor", e:"panie profesorze", ex:"Panie profesorze, dzień dobry!" },
                { g:"Director", e:"panie dyrektorze", ex:"Panie dyrektorze, mam pytanie." }
              ],
              note:"Feminine titles are often left in Nominative in modern Polish: <i>Pani doktor</i>, not <i>Pani doktorko</i>. This is completely standard.",
              examples:[
                { pl:"Dzień dobry, panie doktorze.", en:"Good morning, doctor." }
              ] },
            { front:"When you can skip it",
              sub:"Modern Polish increasingly uses Nominative for casual address - but never in formal speech.",
              points:[
                "Casual: <b>Ania, chodź!</b> \u2b05 acceptable in everyday speech",
                "Affectionate: <b>Aniu, chodź!</b> \u2b05 warmer, more caring",
                "Formal: <b>Panie profesorze!</b> \u2b05 always use Vocative"
              ],
              explain:"For politeness and warmth, Vocative signals genuine care. In writing (letters, emails, ceremonies), it's still expected.",
              examples:[
                { pl:"Droga Aniu, dziękuję za list.", en:"Dear Ania, thank you for the letter." }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"___ , gdzie jesteś?", promptEn:"Ania, where are you? (affectionate)",
              options:["Aniu","Ania","Ani"], answer:"Aniu",
              explain:"Diminutive feminine names in -ia take -u in Vocative. Warm and everyday.", full:"Aniu, gdzie jesteś?", fullEn:"Ania, where are you?" },
            { type:"choose", prompt:"___ , mam pytanie.", promptEn:"Mom, I have a question.",
              options:["Mamo","Mama","Mamę"], answer:"Mamo",
              explain:"Standard feminine noun 'mama' takes -o in Vocative.", full:"Mamo, mam pytanie.", fullEn:"Mom, I have a question." },
            { type:"choose", prompt:"Panie ___ , dzień dobry!", promptEn:"Good morning, professor!",
              options:["profesorze","profesor","profesora"], answer:"profesorze",
              explain:"Formal address uses Vocative. Masculine 'profesor' \u2192 'profesorze' with r \u2192 rz softening.", full:"Panie profesorze, dzień dobry!", fullEn:"Good morning, professor!" },
            { type:"build", promptEn:"Piotr, come here!",
              answer:["Piotrze","chodź","tutaj"],
              explain:"Masculine name 'Piotr' \u2192 'Piotrze' in Vocative. The softening turns -r into -rz.", full:"Piotrze, chodź tutaj!", fullEn:"Piotr, come here!" },
            { type:"choose", prompt:"___ , kocham cię.", promptEn:"Mom, I love you.",
              options:["Mamo","Mama","Mamą"], answer:"Mamo",
              explain:"'Mama' is a standard feminine noun \u2192 -o in Vocative.", full:"Mamo, kocham cię.", fullEn:"Mom, I love you." },
            { type:"choose", prompt:"Droga ___ , dziękuję za list.", promptEn:"Dear Ania, thank you for the letter.",
              options:["Aniu","Ania","Anny"], answer:"Aniu",
              explain:"Letter opening \u2192 always Vocative. Diminutive 'Ania' \u2192 'Aniu'.", full:"Droga Aniu, dziękuję za list.", fullEn:"Dear Ania, thank you for the letter." },
            { type:"choose", prompt:"O ___ , co się stało?", promptEn:"Oh God, what happened?",
              options:["Boże","Bóg","Boga"], answer:"Boże",
              explain:"'Bóg' \u2192 'Boże' in Vocative. This is the fixed exclamation form.", full:"O Boże, co się stało?", fullEn:"Oh God, what happened?" },
            { type:"build", promptEn:"Kids, come here!",
              answer:["Dzieci","chodźcie","tu"],
              explain:"Plural nouns don't change in Vocative - 'dzieci' stays 'dzieci'.", full:"Dzieci, chodźcie tu!", fullEn:"Kids, come here!" },
            { type:"choose", prompt:"Panie ___ , mam pytanie.", promptEn:"Doctor, I have a question.",
              options:["doktorze","doktor","doktora"], answer:"doktorze",
              explain:"Formal address \u2192 Vocative. 'Doktor' \u2192 'doktorze' with r \u2192 rz softening.", full:"Panie doktorze, mam pytanie.", fullEn:"Doctor, I have a question." },
            { type:"choose", prompt:"___ , dziękuję za wszystko.", promptEn:"Kasia, thank you for everything.",
              options:["Kasiu","Kasia","Kasi"], answer:"Kasiu",
              explain:"Diminutive 'Kasia' \u2192 'Kasiu' in Vocative.", full:"Kasiu, dziękuję za wszystko.", fullEn:"Kasia, thank you for everything." },
            { type:"build", promptEn:"Grandma, I miss you.",
              answer:["Babciu","tęsknię","za","tobą"],
              explain:"Affectionate 'babcia' \u2192 'babciu' in Vocative.", full:"Babciu, tęsknię za tobą.", fullEn:"Grandma, I miss you." },
            { type:"choose", prompt:"___ , chodź na obiad!", promptEn:"Marek, come for lunch!",
              options:["Marku","Marek","Marka"], answer:"Marku",
              explain:"Names ending in -k take -u in Vocative: 'Marek' \u2192 'Marku'.", full:"Marku, chodź na obiad!", fullEn:"Marek, come for lunch!" },
            { type:"choose", prompt:"Drogi ___ , piszę z Warszawy.", promptEn:"Dear Piotr, I'm writing from Warsaw.",
              options:["Piotrze","Piotr","Piotra"], answer:"Piotrze",
              explain:"Letter opening \u2192 Vocative. 'Piotr' \u2192 'Piotrze'.", full:"Drogi Piotrze, piszę z Warszawy.", fullEn:"Dear Piotr, I'm writing from Warsaw." },
            { type:"build", promptEn:"Dear friends, thank you!",
              answer:["Kochani","dziękuję"],
              explain:"Plural doesn't change in Vocative. 'Kochani' (dear ones) is the same as in Nominative.", full:"Kochani, dziękuję!", fullEn:"Dear friends, thank you!" }
          ]
        },
        {
          name: "Przymiotniki (Adjectives & Traits)", emoji: "\uD83C\uDFAD", kind: "grammar", chip: "Grammar A2",
          desc: "Describing people: the 'oni' plural for character traits",
          teach: [
            { front:"Adjectives change with the group",
              sub:"When describing a group, adjectives must match the gender - and Polish has TWO plurals to choose from.",
              points:[
                "<b>One</b> group (women, animals, things): just add <b>-e</b>. <i>miły \u2192 miłe</i>",
                "<b>Oni</b> group (with men): add <b>-i</b> or <b>-y</b>, often changing the consonant before it.",
                "Getting this right is the mark of natural Polish."
              ],
              examples:[
                { pl:"Te kobiety są miłe.", en:"These women are nice." },
                { pl:"Ci panowie są mili.", en:"These men are nice." }
              ] },
            { front:"Pattern 1: -ty \u2192 -ci",
              sub:"When an adjective ends in -ty, the t softens to c and takes -i for 'oni'.",
              table:[
                { g:"stubborn", e:"uparty \u2192 uparci", ex:"Oni są bardzo <b>uparci</b>." },
                { g:"hardworking", e:"pracowity \u2192 pracowici", ex:"Moi koledzy są <b>pracowici</b>." },
                { g:"open", e:"otwarty \u2192 otwarci", ex:"Jesteśmy <b>otwarci</b> na pomysły." }
              ],
              explain:"Compare with the 'one' plural: <i>Te dziewczyny są pracowite</i> (women) vs <i>Ci chłopcy są pracowici</i> (men).",
              examples:[
                { pl:"Ci studenci są bardzo pracowici.", en:"These students are very hardworking." }
              ] },
            { front:"Pattern 2: -ry \u2192 -rzy",
              sub:"The r softens to rz - one of the most important adjective patterns.",
              table:[
                { g:"honest", e:"szczery \u2192 szczerzy", ex:"Bądźmy ze sobą <b>szczerzy</b>." },
                { g:"good", e:"dobry \u2192 dobrzy", ex:"To są <b>dobrzy</b> ludzie." },
                { g:"smart", e:"mądry \u2192 mądrzy", ex:"Moi rodzice są <b>mądrzy</b>." }
              ],
              note:"'Dobry' and 'mądry' are extremely common in daily speech. Master these first.",
              examples:[
                { pl:"Zawsze byliśmy szczerzy.", en:"We have always been honest." }
              ] },
            { front:"Pattern 3: -ły \u2192 -li",
              sub:"The hard \u0142 softens into a plain l.",
              table:[
                { g:"nice", e:"miły \u2192 mili", ex:"Sąsiedzi są bardzo <b>mili</b>." },
                { g:"shy", e:"nieśmiały \u2192 nieśmiali", ex:"Chłopcy byli <b>nieśmiali</b>." },
                { g:"merry", e:"wesoły \u2192 weseli", ex:"Jesteśmy dzisiaj <b>weseli</b>." }
              ],
              explain:"For 'wesoły \u2192 weseli', the 'o' also shifts to an 'e' to make pronunciation smoother.",
              examples:[
                { pl:"Nasi nowi sąsiedzi są bardzo mili.", en:"Our new neighbors are very nice." }
              ] },
            { front:"Pattern 4: -ki / -ski to -cy / -scy",
              sub:"These are the trickiest transformations, but very common.",
              table:[
                { g:"sociable", e:"towarzyski \u2192 towarzyscy", ex:"Są bardzo <b>towarzyscy</b>." },
                { g:"tall", e:"wysoki \u2192 wysocy", ex:"Koszykarze są <b>wysocy</b>." },
                { g:"Polish", e:"polski \u2192 polscy", ex:"<b>Polscy</b> studenci są mądrzy." }
              ],
              explain:"The -ski ending is extremely common in nationality-based adjectives (polski, angielski, francuski). All follow this pattern.",
              examples:[
                { pl:"Moi bracia są bardzo wysocy i towarzyscy.", en:"My brothers are very tall and sociable." }
              ] },
            { front:"The easy ones: just add -i",
              sub:"Many consonants don't need to change - they just add -i.",
              table:[
                { g:"lazy", e:"leniwy \u2192 leniwi", ex:"W weekend jesteśmy <b>leniwi</b>." },
                { g:"ambitious", e:"ambitny \u2192 ambitni", ex:"Młodzi ludzie są <b>ambitni</b>." },
                { g:"serious", e:"poważny \u2192 poważni", ex:"Dlaczego jesteście <b>poważni</b>?" }
              ],
              examples:[
                { pl:"Nasi pracownicy są bardzo ambitni.", en:"Our employees are very ambitious." }
              ] },
            { front:"Quick reference: how to tell",
              sub:"Ask yourself two questions before choosing the ending.",
              points:[
                "<b>1. Is there a man in the group?</b> If no \u2192 use 'one' form (-e).",
                "<b>2. If yes, what does the adjective end in?</b> Apply the pattern for that ending.",
                "Same rule applies to <i>ten \u2192 ci</i>, <i>mój \u2192 moi</i>, <i>jaki \u2192 jacy</i>."
              ],
              note:"The 'oni' patterns aren't just for adjectives - they run through the whole Polish plural system. See the <b>Pronouns</b> topic for the full picture.",
              examples:[
                { pl:"Te dziewczyny są mądre. Ci chłopcy są mądrzy.", en:"These girls are smart. These boys are smart." }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"Moi koledzy z zespołu są bardzo ___ .", promptEn:"My teammates are very hardworking.",
              options:["pracowici","pracowity","pracowite"], answer:"pracowici",
              explain:"'Koledzy' is a masculine personal group (oni), so '-ty' softens to '-ci'.", full:"Moi koledzy z zespołu są bardzo pracowici.", fullEn:"My teammates are very hardworking." },
            { type:"choose", prompt:"Bądźmy ze sobą ___ .", promptEn:"Let's be honest with each other.",
              options:["szczerzy","szczery","szczere"], answer:"szczerzy",
              explain:"'Let's be' means a group including us - if the speaker is male or the group is mixed, use 'oni' form. '-ry' \u2192 '-rzy'.", full:"Bądźmy ze sobą szczerzy.", fullEn:"Let's be honest with each other." },
            { type:"build", promptEn:"Our new neighbors are very nice.",
              answer:["Nasi","nowi","sąsiedzi","są","bardzo","mili"],
              explain:"'Sąsiedzi' triggers the 'oni' forms: 'nasi', 'nowi', 'mili' all take the softened endings.", full:"Nasi nowi sąsiedzi są bardzo mili.", fullEn:"Our new neighbors are very nice." },
            { type:"choose", prompt:"Te dziewczyny są bardzo ___ .", promptEn:"These girls are very nice.",
              options:["miłe","mili","miły"], answer:"miłe",
              explain:"'Dziewczyny' is women-only ('one'), so simple -e ending.", full:"Te dziewczyny są bardzo miłe.", fullEn:"These girls are very nice." },
            { type:"choose", prompt:"Moi dziadkowie są bardzo ___ .", promptEn:"My grandparents are very smart.",
              options:["mądrzy","mądre","mądry"], answer:"mądrzy",
              explain:"'Dziadkowie' includes a man, so 'oni' form. -ry \u2192 -rzy.", full:"Moi dziadkowie są bardzo mądrzy.", fullEn:"My grandparents are very smart." },
            { type:"build", promptEn:"They (men) are very stubborn.",
              answer:["Oni","są","bardzo","uparci"],
              explain:"'Oni' = men/mixed group. '-ty' in 'uparty' \u2192 '-ci'.", full:"Oni są bardzo uparci.", fullEn:"They (men) are very stubborn." },
            { type:"choose", prompt:"Czy twoi przyjaciele są ___ ?", promptEn:"Are your friends sociable?",
              options:["towarzyscy","towarzyski","towarzyskie"], answer:"towarzyscy",
              explain:"'Przyjaciele' is a masculine personal group. -ski \u2192 -scy.", full:"Czy twoi przyjaciele są towarzyscy?", fullEn:"Are your friends sociable?" },
            { type:"choose", prompt:"Wszyscy w biurze są dzisiaj ___ .", promptEn:"Everyone in the office is lazy today.",
              options:["leniwi","leniwe","leniwy"], answer:"leniwi",
              explain:"'Wszyscy' (everyone) is masculine personal. 'Leniwy' ends in -wy, just adds -i.", full:"Wszyscy w biurze są dzisiaj leniwi.", fullEn:"Everyone in the office is lazy today." },
            { type:"build", promptEn:"These men are very tall.",
              answer:["Ci","panowie","są","bardzo","wysocy"],
              explain:"'Panowie' \u2192 masculine personal. -ki in 'wysoki' \u2192 -cy.", full:"Ci panowie są bardzo wysocy.", fullEn:"These men are very tall." },
            { type:"choose", prompt:"Moje siostry są bardzo ___ .", promptEn:"My sisters are very ambitious.",
              options:["ambitne","ambitni","ambitny"], answer:"ambitne",
              explain:"'Siostry' is women-only. Use 'one' form: simple -e ending, not -i.", full:"Moje siostry są bardzo ambitne.", fullEn:"My sisters are very ambitious." },
            { type:"choose", prompt:"To są bardzo ___ ludzie.", promptEn:"These are very good people.",
              options:["dobrzy","dobre","dobry"], answer:"dobrzy",
              explain:"'Ludzie' includes men \u2192 'oni'. -ry \u2192 -rzy.", full:"To są bardzo dobrzy ludzie.", fullEn:"These are very good people." },
            { type:"build", promptEn:"Polish students are smart.",
              answer:["Polscy","studenci","są","mądrzy"],
              explain:"'Studenci' \u2192 masc personal. 'Polski' \u2192 'polscy' (-ski to -scy), and 'mądry' \u2192 'mądrzy' (-ry to -rzy).", full:"Polscy studenci są mądrzy.", fullEn:"Polish students are smart." }
          ]
        },
        {
          name: "Zawody (Professions)", emoji: "\uD83D\uDCBC", kind: "grammar", chip: "Grammar A2",
          desc: "How professions change for groups of men (the 'oni' plural)",
          teach: [
            { front:"Professions & the 'oni' plural",
              sub:"When a group of professionals includes at least one man, the noun takes a special ending.",
              points:[
                "Adjectives just take -i or -y. Nouns are more varied: <b>-owie, -e, -cy, -rzy</b>.",
                "The ending you choose depends almost entirely on the last letter of the singular word.",
                "Women-only groups ('one') are easier: usually add <b>-ki</b> (nauczycielki, lekarki, kelnerki)."
              ],
              examples:[
                { pl:"Gdzie są lekarze?", en:"Where are the doctors?" }
              ] },
            { front:"Pattern 1: the prestigious -owie",
              sub:"Many modern, technical, or 'boss' titles take the -owie ending.",
              table:[
                { g:"manager", e:"menedżer \u2192 menedżerowie", ex:"Nasi <b>menedżerowie</b> są na spotkaniu." },
                { g:"engineer", e:"inżynier \u2192 inżynierowie", ex:"To są świetni <b>inżynierowie</b>." },
                { g:"boss", e:"szef \u2192 szefowie", ex:"<b>Szefowie</b> mają dzisiaj wolne." },
                { g:"professor", e:"profesor \u2192 profesorowie", ex:"Ci <b>profesorowie</b> uczą na uniwersytecie." }
              ],
              examples:[
                { pl:"Inżynierowie i menedżerowie pracują razem.", en:"The engineers and managers work together." }
              ] },
            { front:"Pattern 2: the soft -e",
              sub:"Words ending in -arz, -erz, and -iel simply add -e.",
              table:[
                { g:"doctor", e:"lekarz \u2192 lekarze", ex:"Ci <b>lekarze</b> są bardzo dobrzy." },
                { g:"teacher", e:"nauczyciel \u2192 nauczyciele", ex:"Nasi <b>nauczyciele</b> są cierpliwi." },
                { g:"journalist", e:"dziennikarz \u2192 dziennikarze", ex:"<b>Dziennikarze</b> zadają dużo pytań." }
              ],
              note:"Never say 'lekarzy' or 'nauczycieli' in Nominative (subject) - those are Accusative/Genitive forms!",
              examples:[
                { pl:"Lekarze mają dużo pracy.", en:"Doctors have a lot of work." }
              ] },
            { front:"Pattern 3: -ik / -yk \u2192 -icy / -ycy",
              sub:"A strict rule for almost all nouns ending in -ik or -yk.",
              table:[
                { g:"worker", e:"pracownik \u2192 pracownicy", ex:"Wszyscy <b>pracownicy</b> są w biurze." },
                { g:"lawyer", e:"prawnik \u2192 prawnicy", ex:"Ci <b>prawnicy</b> są drodzy." },
                { g:"clerk", e:"urzędnik \u2192 urzędnicy", ex:"<b>Urzędnicy</b> pracują do szesnastej." }
              ],
              explain:"The k softens to c, and -i is added. This is one of the most productive patterns in Polish.",
              examples:[
                { pl:"Moi pracownicy są bardzo zmotywowani.", en:"My employees are very motivated." }
              ] },
            { front:"Pattern 4: -sta and -t \u2192 -ści / -ci",
              sub:"Words ending in -sta or -t undergo heavy softening.",
              table:[
                { g:"programmer", e:"programista \u2192 programiści", ex:"<b>Programiści</b> zarabiają dobrze." },
                { g:"dentist", e:"dentysta \u2192 dentyści", ex:"<b>Dentyści</b> mają dzisiaj dużo pacjentów." },
                { g:"student", e:"student \u2192 studenci", ex:"Ci <b>studenci</b> są z Polski." },
                { g:"policeman", e:"policjant \u2192 policjanci", ex:"<b>Policjanci</b> kierują ruchem." }
              ],
              examples:[
                { pl:"Nasi programiści to świetny zespół.", en:"Our programmers are a great team." }
              ] },
            { front:"Pattern 5: -r and -ca \u2192 -rzy / -cy",
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
              ] },
            { front:"Feminine professions: the easy side",
              sub:"For women, professions usually take -ka in the singular, -ki in the plural.",
              table:[
                { g:"female teacher", e:"nauczycielka \u2192 nauczycielki", ex:"<b>Nauczycielki</b> są w szkole." },
                { g:"female doctor", e:"lekarka \u2192 lekarki", ex:"<b>Lekarki</b> pomagają pacjentom." },
                { g:"female waiter", e:"kelnerka \u2192 kelnerki", ex:"<b>Kelnerki</b> pracują wieczorem." }
              ],
              note:"Some professions in modern Polish are used in both grammatical genders for women (pani doktor, pani inżynier) - this is stylistic, not incorrect.",
              examples:[
                { pl:"Nasze lekarki są bardzo miłe.", en:"Our (female) doctors are very nice." }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"Wszyscy ___ są dzisiaj na spotkaniu.", promptEn:"All employees are at the meeting today.",
              options:["pracownicy","pracowniki","pracownikowie"], answer:"pracownicy",
              explain:"'Pracownik' ends in -ik \u2192 -icy in the masculine personal plural.", full:"Wszyscy pracownicy są dzisiaj na spotkaniu.", fullEn:"All employees are at the meeting today." },
            { type:"choose", prompt:"Nasi ___ mają dzisiaj wolne.", promptEn:"Our bosses have the day off today.",
              options:["szefowie","szefy","szefzy"], answer:"szefowie",
              explain:"'Szef' takes the prestigious -owie ending, like most 'boss' titles.", full:"Nasi szefowie mają dzisiaj wolne.", fullEn:"Our bosses have the day off today." },
            { type:"build", promptEn:"These doctors are very good.",
              answer:["Ci","lekarze","są","bardzo","dobrzy"],
              explain:"'Lekarz' ends in -arz \u2192 -e ending. 'Dobry' \u2192 'dobrzy' for the oni group.", full:"Ci lekarze są bardzo dobrzy.", fullEn:"These doctors are very good." },
            { type:"choose", prompt:"Ci ___ pracują nad nową aplikacją.", promptEn:"These programmers are working on a new app.",
              options:["programiści","programisty","programistowie"], answer:"programiści",
              explain:"Words ending in -sta soften heavily to -ści.", full:"Ci programiści pracują nad nową aplikacją.", fullEn:"These programmers are working on a new app." },
            { type:"choose", prompt:"Pytam, bo moi ___ nie wiedzą.", promptEn:"I ask because my managers don't know.",
              options:["menedżerowie","menedżery","menedżerzy"], answer:"menedżerowie",
              explain:"'Menedżer' takes -owie. 'Menedżerzy' is also heard but -owie is the standard form.", full:"Pytam, bo moi menedżerowie nie wiedzą.", fullEn:"I ask because my managers don't know." },
            { type:"build", promptEn:"The lawyers are in the office.",
              answer:["Prawnicy","są","w","biurze"],
              explain:"'Prawnik' follows the -ik \u2192 -icy rule.", full:"Prawnicy są w biurze.", fullEn:"The lawyers are in the office." },
            { type:"choose", prompt:"Nasi ___ zarabiają bardzo dobrze.", promptEn:"Our engineers earn very well.",
              options:["inżynierowie","inżyniery","inżynierzy"], answer:"inżynierowie",
              explain:"'Inżynier' is a prestigious title \u2192 -owie ending.", full:"Nasi inżynierowie zarabiają bardzo dobrze.", fullEn:"Our engineers earn very well." },
            { type:"choose", prompt:"Czy ci panowie to ___ ?", promptEn:"Are those men waiters?",
              options:["kelnerzy","kelnerowie","kelnery"], answer:"kelnerzy",
              explain:"'Kelner' ends in -r \u2192 -rzy with softening.", full:"Czy ci panowie to kelnerzy?", fullEn:"Are those men waiters?" },
            { type:"build", promptEn:"The students and teachers are here.",
              answer:["Studenci","i","nauczyciele","są","tutaj"],
              explain:"'Student' \u2192 'studenci' (-t softens to -ci). 'Nauczyciel' \u2192 'nauczyciele' (-iel simply adds -e).", full:"Studenci i nauczyciele są tutaj.", fullEn:"The students and teachers are here." },
            { type:"choose", prompt:"Wszyscy ___ stoją w korku.", promptEn:"All the drivers are stuck in a traffic jam.",
              options:["kierowcy","kierowcowie","kierowce"], answer:"kierowcy",
              explain:"'Kierowca' is masculine (despite the -a ending) \u2192 -cy.", full:"Wszyscy kierowcy stoją w korku.", fullEn:"All the drivers are stuck in a traffic jam." },
            { type:"choose", prompt:"Nasze ___ są w szkole.", promptEn:"Our (female) teachers are at school.",
              options:["nauczycielki","nauczycieli","nauczyciele"], answer:"nauczycielki",
              explain:"Women-only group ('one') \u2192 'nauczycielki'. Watch out: 'nauczyciele' is the masculine personal form.", full:"Nasze nauczycielki są w szkole.", fullEn:"Our (female) teachers are at school." },
            { type:"build", promptEn:"These policemen direct traffic.",
              answer:["Ci","policjanci","kierują","ruchem"],
              explain:"'Policjant' \u2192 'policjanci'. The -t softens to -ci.", full:"Ci policjanci kierują ruchem.", fullEn:"These policemen direct traffic." }
          ]
        },
        {
          name: "Zaimki (Pronouns & Determiners)", emoji: "\uD83E\uDDED", kind: "grammar", chip: "Grammar A2",
          desc: "mój, ten, jaki - pointing and owning in Nominative",
          teach: [
            { front:"Polish has 5 'genders' in the plural",
              sub:"You already know 3 in the singular. The plural adds a second dimension.",
              points:[
                "Singular: <b>on</b> (masculine), <b>ona</b> (feminine), <b>ono</b> (neuter)",
                "Plural <b>oni</b>: groups with at least one man (masculine personal)",
                "Plural <b>one</b>: everything else - women only, children, animals, objects"
              ],
              examples:[
                { pl:"Gdzie oni są?", en:"Where are they? (men or mixed)" },
                { pl:"Gdzie one są?", en:"Where are they? (women / things)" }
              ] },
            { front:"Mój & Twój (my & your)",
              sub:"Possessive pronouns change with the noun's gender.",
              table:[
                { g:"Masculine", e:"mój / twój", ex:"mój bilet, twój dom" },
                { g:"Feminine", e:"moja / twoja", ex:"moja kawa, twoja książka" },
                { g:"Neuter", e:"moje / twoje", ex:"moje biurko, twoje dziecko" }
              ],
              note:"In plural: <b>moi / twoi</b> for men (oni), <b>moje / twoje</b> for everything else (one).",
              examples:[
                { pl:"To jest mój kot.", en:"This is my cat." },
                { pl:"To jest twoja kawa.", en:"This is your coffee." }
              ] },
            { front:"Ten & Tamten (this & that)",
              sub:"Pointing at things nearby (ten) vs. further away (tamten).",
              table:[
                { g:"Masculine", e:"ten / tamten", ex:"ten pociąg, tamten dom" },
                { g:"Feminine", e:"ta / tamta", ex:"ta ulica, tamta pani" },
                { g:"Neuter", e:"to / tamto", ex:"to spotkanie, tamto dziecko" }
              ],
              explain:"The neuter form <b>to</b> is also the universal 'this / it' used in constructions like <i>to jest kot</i> - regardless of the noun's gender.",
              examples:[
                { pl:"Ten chleb jest bardzo dobry.", en:"This bread is very good." },
                { pl:"Ta kawa jest moja.", en:"This coffee is mine." }
              ] },
            { front:"Jaki, Który, Czyj (what kind, which, whose)",
              sub:"Three question words that behave like adjectives.",
              points:[
                "<b>Jaki / Jaka / Jakie:</b> what kind? (asking for description)",
                "<b>Który / Która / Które:</b> which one? (choosing from a set)",
                "<b>Czyj / Czyja / Czyje:</b> whose? (asking about ownership)"
              ],
              note:"These change endings exactly like adjectives to match the noun they describe.",
              examples:[
                { pl:"Jaka to jest ulica?", en:"What street is this?" },
                { pl:"Który to twój samochód?", en:"Which one is your car?" },
                { pl:"Czyj to telefon?", en:"Whose phone is this?" }
              ] },
            { front:"The special 'oni' plurals",
              sub:"When talking about groups of men (or mixed groups), the endings soften.",
              table:[
                { g:"my / your", e:"moi / twoi", ex:"moi koledzy" },
                { g:"these / those", e:"ci / tamci", ex:"ci panowie" },
                { g:"which / what", e:"którzy / jacy", ex:"jacy ludzie" }
              ],
              explain:"This is the trickiest column. <i>te</i> \u2192 <b>ci</b>, <i>moje</i> \u2192 <b>moi</b>, <i>które</i> \u2192 <b>którzy</b> - all when referring to men.",
              examples:[
                { pl:"Ci ludzie to moi znajomi.", en:"These people are my friends." }
              ] },
            { front:"Full singular reference chart",
              sub:"Everything you need for the singular in one place.",
              table:[
                { g:"masculine", e:"ten mój dobry kot", ex:"'this my good cat'" },
                { g:"feminine", e:"ta moja dobra kawa", ex:"'this my good coffee'" },
                { g:"neuter", e:"to moje dobre dziecko", ex:"'this my good child'" }
              ],
              explain:"Notice how <b>ten \u2192 ta \u2192 to</b>, <b>mój \u2192 moja \u2192 moje</b>, and <b>dobry \u2192 dobra \u2192 dobre</b> all follow the same rhythm.",
              examples:[
                { pl:"Ta moja dobra siostra jest tutaj.", en:"This good sister of mine is here." }
              ] },
            { front:"Watch out: things that trip up learners",
              sub:"A few common gotchas worth memorizing.",
              points:[
                "<b>Dzieci</b> (children) is treated as 'one', not 'oni', even with boys: <i>te dzieci</i>, not <i>ci dzieci</i>.",
                "<b>Ludzie</b> (people) IS 'oni': <i>ci ludzie</i>.",
                "Animals are always 'one' plural regardless of species: <i>te koty, te psy</i>."
              ],
              note:"A group of 100 boys ages 5-10 is still 'te dzieci' - grammatical children stay grammatical children.",
              examples:[
                { pl:"Te dzieci są głodne.", en:"These children are hungry." },
                { pl:"Ci ludzie są mili.", en:"These people are nice." }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"To jest ___ nowa praca.", promptEn:"This is my new job.",
              options:["moja","mój","moje"], answer:"moja",
              explain:"'Praca' is feminine (ends in -a) \u2192 'moja'.", full:"To jest moja nowa praca.", fullEn:"This is my new job." },
            { type:"choose", prompt:"___ to jest telefon?", promptEn:"Whose phone is this?",
              options:["Czyj","Czyja","Czyje"], answer:"Czyj",
              explain:"'Telefon' is masculine \u2192 'Czyj' (masculine form).", full:"Czyj to jest telefon?", fullEn:"Whose phone is this?" },
            { type:"choose", prompt:"___ studenci są z Polski.", promptEn:"These students are from Poland.",
              options:["Ci","Te","Ta"], answer:"Ci",
              explain:"'Studenci' is masculine personal ('oni') \u2192 'te' softens to 'ci'.", full:"Ci studenci są z Polski.", fullEn:"These students are from Poland." },
            { type:"choose", prompt:"___ to twój samochód?", promptEn:"Which one is your car?",
              options:["Który","Która","Które"], answer:"Który",
              explain:"'Samochód' is masculine \u2192 'Który'.", full:"Który to twój samochód?", fullEn:"Which one is your car?" },
            { type:"build", promptEn:"Which coffee is yours?",
              answer:["Która","kawa","jest","twoja"],
              explain:"'Kawa' is feminine \u2192 'która' and 'twoja' both take -a.", full:"Która kawa jest twoja?", fullEn:"Which coffee is yours?" },
            { type:"choose", prompt:"___ koty są bardzo głodne.", promptEn:"These cats are very hungry.",
              options:["Te","Ci","Ta"], answer:"Te",
              explain:"Animals are 'one' plural \u2192 'te', not 'ci'.", full:"Te koty są bardzo głodne.", fullEn:"These cats are very hungry." },
            { type:"choose", prompt:"___ chleb jest bardzo dobry.", promptEn:"This bread is very good.",
              options:["Ten","Ta","To"], answer:"Ten",
              explain:"'Chleb' is masculine \u2192 'Ten'.", full:"Ten chleb jest bardzo dobry.", fullEn:"This bread is very good." },
            { type:"choose", prompt:"___ to jest ulica?", promptEn:"What street is this?",
              options:["Jaka","Jaki","Jakie"], answer:"Jaka",
              explain:"'Ulica' is feminine \u2192 'Jaka'.", full:"Jaka to jest ulica?", fullEn:"What street is this?" },
            { type:"build", promptEn:"These people are my friends.",
              answer:["Ci","ludzie","to","moi","znajomi"],
              explain:"'Ludzie' (people) is 'oni' \u2192 'ci' + 'moi' + 'znajomi'.", full:"Ci ludzie to moi znajomi.", fullEn:"These people are my friends." },
            { type:"build", promptEn:"This is my cat.",
              answer:["To","jest","mój","kot"],
              explain:"'Kot' is masculine \u2192 'mój'.", full:"To jest mój kot.", fullEn:"This is my cat." },
            { type:"choose", prompt:"___ dzieci są głodne.", promptEn:"These children are hungry.",
              options:["Te","Ci","Ta"], answer:"Te",
              explain:"'Dzieci' is 'one' plural (even for boys!) - a common learner trap.", full:"Te dzieci są głodne.", fullEn:"These children are hungry." },
            { type:"choose", prompt:"___ to jest książka?", promptEn:"Whose book is this?",
              options:["Czyja","Czyj","Czyje"], answer:"Czyja",
              explain:"'Książka' is feminine \u2192 'Czyja'.", full:"Czyja to jest książka?", fullEn:"Whose book is this?" }
          ]
        },
        {
          name: "Narodowości (Nationalities)", emoji: "\u2708\uFE0F", kind: "grammar", chip: "Grammar A2",
          desc: "The tricky 'oni' plurals for 15 common nationalities in Poland",
          teach: [
            { front:"Nationalities & the 'oni' plural",
              sub:"Groups of men cause consonant mutations at the end of the word.",
              points:[
                "Feminine nationalities follow easy rules, usually ending in <b>-ki</b> (Polki, Ukrainki).",
                "The masculine personal ('oni') plural is where the heavy consonant changes happen.",
                "Nationalities in Polish are <b>always capitalized</b> - unlike in English."
              ],
              examples:[
                { pl:"To są Ukraińcy.", en:"These are Ukrainians." },
                { pl:"Czy oni są z Polski?", en:"Are they from Poland?" }
              ] },
            { front:"Pattern 1: -k / -czyk \u2192 -cy",
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
            { front:"Pattern 2: -iec \u2192 -cy",
              sub:"The 'e' drops out completely, and the ending becomes -cy.",
              table:[
                { g:"Ukrainian", e:"Ukrainiec \u2192 Ukraińcy", ex:"Moi koledzy to <b>Ukraińcy</b>." },
                { g:"German", e:"Niemiec \u2192 Niemcy", ex:"Ci <b>Niemcy</b> są turystami." }
              ],
              note:"This is one of the most frequent patterns you'll hear in Warsaw.",
              examples:[
                { pl:"W moim biurze pracują Ukraińcy.", en:"Ukrainians work in my office." }
              ] },
            { front:"Pattern 3: -in and -an \u2192 -nie / -ni",
              sub:"Watch out for the drop of 'in' in words ending with -anin!",
              table:[
                { g:"American", e:"Amerykanin \u2192 Amerykanie", ex:"To są <b>Amerykanie</b>." },
                { g:"Spaniard", e:"Hiszpan \u2192 Hiszpanie", ex:"<b>Hiszpanie</b> lubią słońce." },
                { g:"Belarusian", e:"Białorusin \u2192 Białorusini", ex:"Ci <b>Białorusini</b> to moi znajomi." },
                { g:"Georgian", e:"Gruzin \u2192 Gruzini", ex:"<b>Gruzini</b> robią świetne wino." }
              ],
              explain:"'Amerykanin' loses '-in' entirely and adds '-ie'. 'Białorusin' keeps the 'in' and just adds '-i'. Small pattern, big difference.",
              examples:[
                { pl:"Amerykanie często podróżują.", en:"Americans travel often." }
              ] },
            { front:"Pattern 4: the heavy softeners",
              sub:"Some consonants change entirely to accommodate the 'i' sound.",
              table:[
                { g:"Italian", e:"Włoch \u2192 Włosi", ex:"<b>Włosi</b> robią pizzę." },
                { g:"Czech", e:"Czech \u2192 Czesi", ex:"<b>Czesi</b> są blisko." },
                { g:"French", e:"Francuz \u2192 Francuzi", ex:"To są <b>Francuzi</b>." },
                { g:"Indian", e:"Hindus \u2192 Hindusi", ex:"<b>Hindusi</b> mówią po angielsku." },
                { g:"Turk", e:"Turek \u2192 Turcy", ex:"<b>Turcy</b> piją dużo herbaty." }
              ],
              explain:"'ch' softens to 'si' (Włosi, Czesi), 'z' softens to 'zi' (Francuzi), 's' to 'si' (Hindusi). 'Turek' drops the 'e' entirely.",
              examples:[
                { pl:"Włosi i Francuzi to Europejczycy.", en:"Italians and French are Europeans." }
              ] },
            { front:"Feminine nationalities: the easy side",
              sub:"For women, nationalities are much more regular.",
              table:[
                { g:"Polish woman", e:"Polka \u2192 Polki", ex:"To są <b>Polki</b>." },
                { g:"Ukrainian woman", e:"Ukrainka \u2192 Ukrainki", ex:"<b>Ukrainki</b> mieszkają w Warszawie." },
                { g:"American woman", e:"Amerykanka \u2192 Amerykanki", ex:"<b>Amerykanki</b> są turystkami." }
              ],
              explain:"Feminine nationalities usually end in -ka (singular) \u2192 -ki (plural). This is 'one' plural, so no consonant softening.",
              examples:[
                { pl:"Moje koleżanki to Polki.", en:"My (female) friends are Polish." }
              ] },
            { front:"Quick reference table",
              sub:"The 10 nationalities you'll use most in daily Polish.",
              table:[
                { g:"Pole", e:"Polak \u2192 Polacy / Polka \u2192 Polki", ex:"" },
                { g:"Ukrainian", e:"Ukrainiec \u2192 Ukraińcy / Ukrainka \u2192 Ukrainki", ex:"" },
                { g:"German", e:"Niemiec \u2192 Niemcy / Niemka \u2192 Niemki", ex:"" },
                { g:"American", e:"Amerykanin \u2192 Amerykanie / Amerykanka \u2192 Amerykanki", ex:"" },
                { g:"Italian", e:"Włoch \u2192 Włosi / Włoszka \u2192 Włoszki", ex:"" }
              ],
              note:"Study these five pairs first - they cover most conversations you'll have about people's origins.",
              examples:[
                { pl:"W Polsce mieszkają Polacy, Ukraińcy i Niemcy.", en:"Poles, Ukrainians, and Germans live in Poland." }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"Moi sąsiedzi to ___ .", promptEn:"My neighbors are Ukrainians.",
              options:["Ukraińcy","Ukrainiec","Ukraińce"], answer:"Ukraińcy",
              explain:"'Ukrainiec' ends in -iec \u2192 -cy in the plural.", full:"Moi sąsiedzi to Ukraińcy.", fullEn:"My neighbors are Ukrainians." },
            { type:"choose", prompt:"Czy ci panowie to ___ ?", promptEn:"Are those men Germans?",
              options:["Niemcy","Niemiec","Niemce"], answer:"Niemcy",
              explain:"'Niemiec' follows the -iec \u2192 -cy rule.", full:"Czy ci panowie to Niemcy?", fullEn:"Are those men Germans?" },
            { type:"build", promptEn:"These Americans are my friends.",
              answer:["Ci","Amerykanie","to","moi","znajomi"],
              explain:"'Amerykanin' drops the 'in' and adds -ie \u2192 'Amerykanie'.", full:"Ci Amerykanie to moi znajomi.", fullEn:"These Americans are my friends." },
            { type:"choose", prompt:"___ uwielbiają pizzę.", promptEn:"Italians love pizza.",
              options:["Włosi","Włochy","Włosy"], answer:"Włosi",
              explain:"'Włoch' \u2192 'Włosi'. Watch out: 'Włochy' means Italy (the country), 'włosy' means hair!", full:"Włosi uwielbiają pizzę.", fullEn:"Italians love pizza." },
            { type:"choose", prompt:"Moi koledzy z pracy to ___ .", promptEn:"My colleagues from work are Belarusians.",
              options:["Białorusini","Białorusinie","Białorusin"], answer:"Białorusini",
              explain:"'Białorusin' just adds -i in the masculine personal plural.", full:"Moi koledzy z pracy to Białorusini.", fullEn:"My colleagues from work are Belarusians." },
            { type:"choose", prompt:"Czy ci turyści to ___ ?", promptEn:"Are these tourists British?",
              options:["Brytyjczycy","Brytyjczykowie","Brytyjczyki"], answer:"Brytyjczycy",
              explain:"The -czyk ending always softens to -czycy.", full:"Czy ci turyści to Brytyjczycy?", fullEn:"Are these tourists British?" },
            { type:"build", promptEn:"The Czechs and the Slovaks are here.",
              answer:["Czesi","i","Słowacy","są","tutaj"],
              explain:"'Czech' softens heavily to 'Czesi'. 'Słowak' \u2192 'Słowacy' (-k to -cy).", full:"Czesi i Słowacy są tutaj.", fullEn:"The Czechs and the Slovaks are here." },
            { type:"choose", prompt:"To są bardzo mili ___ .", promptEn:"These are very nice Frenchmen.",
              options:["Francuzi","Francuzy","Francuzowie"], answer:"Francuzi",
              explain:"The 'z' in 'Francuz' softens to 'zi'.", full:"To są bardzo mili Francuzi.", fullEn:"These are very nice Frenchmen." },
            { type:"choose", prompt:"___ prowadzą tę świetną restaurację.", promptEn:"Vietnamese people run this great restaurant.",
              options:["Wietnamczycy","Wietnamczyki","Wietnamczyk"], answer:"Wietnamczycy",
              explain:"Like all -czyk words, it becomes -czycy.", full:"Wietnamczycy prowadzą tę świetną restaurację.", fullEn:"Vietnamese people run this great restaurant." },
            { type:"build", promptEn:"The Georgians make great wine.",
              answer:["Gruzini","robią","świetne","wino"],
              explain:"'Gruzin' simply takes -i in the plural.", full:"Gruzini robią świetne wino.", fullEn:"The Georgians make great wine." },
            { type:"choose", prompt:"Moje koleżanki to ___ .", promptEn:"My (female) friends are Poles.",
              options:["Polki","Polek","Polakami"], answer:"Polki",
              explain:"Women-only group ('one') \u2192 'Polki'. 'Polacy' would be for men or mixed.", full:"Moje koleżanki to Polki.", fullEn:"My (female) friends are Poles." },
            { type:"build", promptEn:"These Poles are my colleagues.",
              answer:["Ci","Polacy","to","moi","koledzy"],
              explain:"Masculine personal ('oni'): 'Polacy' + 'ci' + 'moi' + 'koledzy'.", full:"Ci Polacy to moi koledzy.", fullEn:"These Poles are my colleagues." }
          ]
        }
      ]
    }
  );
})();
