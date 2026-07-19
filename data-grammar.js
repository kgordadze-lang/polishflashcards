/* Po polsku - lesson data: Grammar
   Registered onto window.PP_LEVELS by index.html (loaded in order).
   Safe to edit this file alone; a syntax error here shows a load
   message instead of breaking the app engine. */
(function(){
  window.PP_LEVELS = window.PP_LEVELS || [];
  window.PP_LEVELS.push(
    {
      level: "Grammar Cases",
      blurb: "The seven cases",
      group: "grammar",
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
                { pl:"To są bardzo dobrzy studenci.", en:"These are very good students." }
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
                "Giving: <b>Daję Ani prezent.</b> - I'm giving Ania a gift.",
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
            { type:"choose", prompt:"Daję ___ prezent.", promptEn:"I'm giving Ania a gift.",
              options:["Ani","Ania","Anią"], answer:"Ani",
              explain:"Diminutive 'Ania' has a soft ending, so its Dative is 'Ani'. The full name 'Anna' would be 'Annie'.", full:"Daję Ani prezent.", fullEn:"I'm giving Ania a gift." },
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
                "Time: <b>w</b> + day of week (w środę), <b>za</b> + time from now (za godzinę). Clock time (<i>o drugiej</i>) is Locative - see Miejscownik."
              ],
              note:"When you negate these verbs, the object flips to Genitive: <b>Mam kawę</b> \u2192 <b>Nie mam kawy</b>.",
              examples:[
                { pl:"Wrócę za godzinę.", en:"I'll be back in an hour." },
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
                { g:"me", e:"mnie", ex:"Kocham cię." },
                { g:"you (sg)", e:"ciebie / cię", ex:"Widzę cię!" },
                { g:"him", e:"jego / go", ex:"Znam go." },
                { g:"her", e:"ją", ex:"Lubię ją." },
                { g:"us / them (m) / them (rest)", e:"nas / ich / je", ex:"Widzę ich." }
              ],
              note:"The short forms (cię, go) can never start a sentence and are unstressed. The long forms (mnie, ciebie, jego) go at the start or when emphasized.",
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
              explain:"'Na' + Accusative for direction/purpose. 'Wakacje' is a plural-only noun (non-masculine-personal), so Accusative = Nominative.", full:"Jadę na wakacje.", fullEn:"I'm going on vacation." },
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
              note:"A few very common words take <b>-mi</b> instead: <b>dziećmi</b> (children), <b>ludźmi</b> (people), <b>braćmi</b> (brothers), <b>przyjaciółmi</b> (friends), <b>pieniędzmi</b> (money). Memorize this short list.",
              examples:[
                { pl:"Idę z przyjaciółmi.", en:"I'm going with friends." }
              ] },
            { front:"Being someone: profession & role",
              sub:"After <b>być</b>, Polish always uses Instrumental for profession, nationality, role.",
              points:[
                "<b>Jestem studentem.</b> - I am a student. Feminine form: Jestem studentką.",
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
              explain:"'Być' + profession takes Instrumental. Masculine \u2192 -em. Feminine form: Jestem studentką (fem. \u2192 -ą).", full:"Jestem studentem.", fullEn:"I am a student." },
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
                { g:"Default", e:"-e (with softening)", ex:"kobieta \u2192 kobiecie, szkoła \u2192 szkole" },
                { g:"After k, g", e:"-ce, -dze", ex:"Polka \u2192 Polce, książka \u2192 książce" },
                { g:"After c, cz, rz, ż", e:"-y", ex:"praca \u2192 pracy, ulica \u2192 ulicy" },
                { g:"Soft ending", e:"-i", ex:"kuchnia \u2192 kuchni, pani \u2192 pani" }
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
                { pl:"Rozmawiamy o książkach.", en:"We're talking about the books." }
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
                { g:"After k, g, ch (and syn)", e:"-u", ex:"Marek \u2192 Marku, syn \u2192 synu" },
                { g:"Soft / diminutive", e:"-u", ex:"nauczyciel \u2192 nauczycielu, Tomek \u2192 Tomku" }
              ],
              explain:"Same softening rules as Locative: <b>t\u2192ci, d\u2192dzi, r\u2192rz</b>. So 'brat' \u2192 'bracie', 'Piotr' \u2192 'Piotrze'.",
              note:"'Bóg' becomes 'Boże' in the famous exclamation <b>O Boże!</b> (Oh my God!). And 'tata' \u2192 <b>tato</b> - like the feminine -o pattern.",
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
        }
      ]
    }
  );
  window.PP_LEVELS.push(
    {
      level: "People & Numbers",
      blurb: "Adjectives, pronouns, quantifiers, jobs",
      group: "grammar",
      topics: [
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
          ]        },

        /* 5 ------------------------------------- EVERY vs ALL (quantifiers) */
        {
          name: "Każdy i Wszyscy (Every vs All)", emoji: "\u2705", kind: "grammar", chip: "Grammar A2",
          desc: "każdy takes a singular verb, wszyscy a plural - plus the wszystko trap",
          teach: [
            { front:"Every vs all - the core split",
              sub:"English blurs these. Polish makes you choose, and the verb follows your choice.",
              points:[
                "<b>każdy</b> = every / each. Always <b>singular</b>: każdy student <b>ma</b>...",
                "<b>wszyscy / wszystkie</b> = all. Always <b>plural</b>: wszyscy studenci <b>mają</b>...",
                "Same people, different lens: <b>każdy</b> zooms in on one at a time, <b>wszyscy</b> takes them together.",
                "So the mistake to avoid is <i>każdy studenci mają</i> - mixing a singular word with a plural verb."
              ],
              examples:[
                { pl:"Każdy student ma indeks.", en:"Every student has an ID card." },
                { pl:"Wszyscy studenci mają indeksy.", en:"All the students have ID cards." }
              ] },

            { front:"każdy changes for gender",
              sub:"It behaves like an adjective - match it to the noun it sits in front of.",
              table:[
                { g:"masculine", e:"każdy", ex:"Każdy dzień jest inny." },
                { g:"feminine", e:"każda", ex:"Każda godzina się liczy." },
                { g:"neuter", e:"każde", ex:"Każde dziecko to wie." }
              ],
              note:"There is no plural of <b>każdy</b> in this meaning. When you need a plural, you switch words entirely - to <b>wszyscy</b> or <b>wszystkie</b>." },

            { front:"wszyscy or wszystkie? The oni / one rule again",
              sub:"You already know this split - it's exactly the same one as oni / one, and panowie / panie.",
              points:[
                "<b>wszyscy</b> - groups with at least one man (like <b>oni</b>): wszyscy koledzy, wszyscy ludzie.",
                "<b>wszystkie</b> - women, things, animals, children (like <b>one</b>): wszystkie koleżanki, wszystkie bilety.",
                "One man in the group is enough to tip it to wszyscy."
              ],
              table:[
                { g:"men / mixed", e:"wszyscy", ex:"Wszyscy koledzy przyszli." },
                { g:"women", e:"wszystkie", ex:"Wszystkie koleżanki przyszły." },
                { g:"things", e:"wszystkie", ex:"Wszystkie bilety są sprzedane." }
              ],
              note:"The past tense follows too: wszyscy <b>przyszli</b> vs wszystkie <b>przyszły</b> - the same -li / -ły split you met with panowie byli / panie były." },

            { front:"The wszystko trap",
              sub:"wszystko and wszystkie look like twins. They are not.",
              points:[
                "<b>wszystko</b> = <i>everything</i>. It stands alone, with no noun after it: <i>Wszystko jest dobrze.</i>",
                "<b>wszystkie</b> = <i>all the...</i> and needs a plural noun after it: <i>Wszystkie rzeczy są tutaj.</i>",
                "Quick test: if English says 'everything', use <b>wszystko</b>. If English says 'all the [things]', use <b>wszystkie</b>."
              ],
              examples:[
                { pl:"Wszystko w porządku?", en:"Is everything alright?" },
                { pl:"Wszystkie rzeczy są w torbie.", en:"All the things are in the bag." }
              ] },

            { front:"Set phrases you'll use daily",
              sub:"These are frozen - learn them whole rather than building them.",
              table:[
                { g:"every day", e:"każdego dnia", ex:"Każdego dnia uczę się polskiego." },
                { g:"every time", e:"za każdym razem", ex:"Za każdym razem to samo." },
                { g:"in any case", e:"w każdym razie", ex:"W każdym razie dziękuję." },
                { g:"all the best", e:"wszystkiego najlepszego", ex:"Wszystkiego najlepszego!" },
                { g:"thanks everyone", e:"dziękuję wszystkim", ex:"Dziękuję wszystkim za pomoc." },
                { g:"for everything", e:"za wszystko", ex:"Dziękuję za wszystko." }
              ],
              note:"Look at the cases hiding inside: <b>każdego dnia</b> is dopełniacz, <b>za każdym razem</b> is narzędnik, and <b>wszystkiego najlepszego</b> is dopełniacz too - it's short for 'życzę ci wszystkiego najlepszego'." }
          ],
          drills: [
            { type:"choose", prompt:"Każdy student ___ indeks.", promptEn:"Every student has an ID card.",
              options:["ma","mają","mieć"], answer:"ma",
              explain:"każdy is singular, so the verb is singular: ma.", full:"Każdy student ma indeks.", fullEn:"Every student has an ID card." },
            { type:"choose", prompt:"Wszyscy studenci ___ indeksy.", promptEn:"All the students have ID cards.",
              options:["ma","mają","miały"], answer:"mają",
              explain:"wszyscy is plural, so the verb is plural: mają.", full:"Wszyscy studenci mają indeksy.", fullEn:"All the students have ID cards." },
            { type:"choose", prompt:"___ koledzy przyszli.", promptEn:"All the colleagues came. (men)",
              options:["Wszyscy","Wszystkie","Każdy"], answer:"Wszyscy",
              explain:"A group of men → wszyscy (like oni).", full:"Wszyscy koledzy przyszli.", fullEn:"All the colleagues came." },
            { type:"choose", prompt:"___ koleżanki przyszły.", promptEn:"All the colleagues came. (women)",
              options:["Wszyscy","Wszystkie","Każda"], answer:"Wszystkie",
              explain:"All women → wszystkie (like one), and the past is przyszły.", full:"Wszystkie koleżanki przyszły.", fullEn:"All the colleagues came." },
            { type:"choose", prompt:"___ bilety są sprzedane.", promptEn:"All the tickets are sold out.",
              options:["Wszyscy","Wszystkie","Każde"], answer:"Wszystkie",
              explain:"Things are never wszyscy - only people-with-a-man are.", full:"Wszystkie bilety są sprzedane.", fullEn:"All the tickets are sold out." },
            { type:"choose", prompt:"___ w porządku?", promptEn:"Is everything alright?",
              options:["Wszystko","Wszystkie","Wszyscy"], answer:"Wszystko",
              explain:"'everything' standing alone → wszystko.", full:"Wszystko w porządku?", fullEn:"Is everything alright?" },
            { type:"choose", prompt:"___ rzeczy są w torbie.", promptEn:"All the things are in the bag.",
              options:["Wszystko","Wszystkie","Wszyscy"], answer:"Wszystkie",
              explain:"There's a plural noun after it (rzeczy), so it's wszystkie - not wszystko.", full:"Wszystkie rzeczy są w torbie.", fullEn:"All the things are in the bag." },
            { type:"choose", prompt:"___ dnia uczę się polskiego.", promptEn:"Every day I study Polish.",
              options:["Każdy","Każdego","Każdym"], answer:"Każdego",
              explain:"'każdego dnia' = every day - a frozen dopełniacz phrase.", full:"Każdego dnia uczę się polskiego.", fullEn:"Every day I study Polish." },
            { type:"choose", prompt:"Za ___ razem to samo.", promptEn:"The same thing every time.",
              options:["każdy","każdego","każdym"], answer:"każdym",
              explain:"'za każdym razem' = every time - narzędnik after za.", full:"Za każdym razem to samo.", fullEn:"The same thing every time." },
            { type:"choose", prompt:"___ najlepszego!", promptEn:"All the best! (a birthday wish)",
              options:["Wszystko","Wszystkiego","Wszystkim"], answer:"Wszystkiego",
              explain:"Short for 'życzę ci wszystkiego najlepszego' - życzyć takes dopełniacz.", full:"Wszystkiego najlepszego!", fullEn:"All the best!" },
            { type:"build", promptEn:"Thank you everyone for your help.",
              answer:["Dziękuję","wszystkim","za","pomoc"],
              explain:"dziękować + celownik: wszystkim.", full:"Dziękuję wszystkim za pomoc.", fullEn:"Thank you everyone for your help." },
            { type:"build", promptEn:"Every hour counts.",
              answer:["Każda","godzina","się","liczy"],
              explain:"'godzina' is feminine → każda; the verb stays singular.", full:"Każda godzina się liczy.", fullEn:"Every hour counts." }
          ]
        },
        {
          name: "Stopniowanie (Comparison)", emoji: "📈", kind: "grammar", chip: "Grammar A2",
          desc: "Bigger, better, cheapest - comparing with -szy, bardziej, and naj-",
          teach: [
            { front:"Two ways to compare",
              sub:"Polish has a short road and a long road - the adjective decides which one you take.",
              points:[
                "Short, common adjectives add <b>-szy</b>: stary → star<b>szy</b> (older), młody → młod<b>szy</b> (younger).",
                "Long adjectives and participle-like ones use <b>bardziej</b>: bardziej interesujący, bardziej zmęczony.",
                "Rule of thumb: if the adjective feels basic and everyday, try -szy first. If it's three-plus syllables or ends in -ony / -ący, reach for bardziej.",
                "Never both at once: <i>bardziej starszy</i> is the classic learner error."
              ],
              examples:[
                { pl:"Mój brat jest starszy.", en:"My brother is older." },
                { pl:"Ta książka jest bardziej interesująca.", en:"This book is more interesting." }
              ] },

            { front:"The regular -szy family",
              sub:"The ending often softens or swaps the last consonant - patterns you'll start hearing everywhere.",
              table:[
                { g:"stary → starszy", e:"older", ex:"Jestem starszy od brata." },
                { g:"młody → młodszy", e:"younger", ex:"Ona jest młodsza ode mnie." },
                { g:"tani → tańszy", e:"cheaper", ex:"Ten sklep jest tańszy." },
                { g:"drogi → droższy", e:"more expensive", ex:"Taksówka jest droższa." },
                { g:"wysoki → wyższy", e:"taller / higher", ex:"On jest wyższy niż ja." },
                { g:"długi → dłuższy", e:"longer", ex:"Dni są coraz dłuższe." },
                { g:"łatwy → łatwiejszy", e:"easier", ex:"Polski jest łatwiejszy, niż myślisz." },
                { g:"trudny → trudniejszy", e:"harder", ex:"Egzamin był trudniejszy niż rok temu." }
              ],
              note:"Notice <b>-ki / -oki</b> drop before the ending: wyso<b>ki</b> → wyż-szy, not <i>wysokiszy</i>. The comparative still declines like a normal adjective: starsz<b>a</b> siostra, starsz<b>e</b> miasto." },

            { front:"The five irregulars you can't skip",
              sub:"The most common adjectives are also the most irregular - exactly like English good → better.",
              table:[
                { g:"dobry → lepszy", e:"good → better", ex:"Ta kawa jest lepsza." },
                { g:"zły → gorszy", e:"bad → worse", ex:"Pogoda jest dziś gorsza." },
                { g:"duży → większy", e:"big → bigger", ex:"Potrzebuję większego mieszkania." },
                { g:"mały → mniejszy", e:"small → smaller", ex:"Wolę mniejsze miasto." },
                { g:"lekki → lżejszy", e:"light → lighter", ex:"Ta torba jest lżejsza." }
              ],
              note:"These five carry half of daily conversation. If you memorise nothing else from this lesson, memorise <b>lepszy / gorszy / większy / mniejszy</b>." },

            { front:"The superlative: just add naj-",
              sub:"Take the comparative you already built and glue naj- on the front. Done.",
              points:[
                "starszy → <b>naj</b>starszy (the oldest), lepszy → <b>naj</b>lepszy (the best), gorszy → <b>naj</b>gorszy (the worst).",
                "With bardziej the naj- lands on bardziej: <b>najbardziej</b> interesujący.",
                "Superlatives decline too: najlepsz<b>a</b> kawa w mieście, najstarsz<b>e</b> miasto w Polsce."
              ],
              examples:[
                { pl:"To najlepsza kawiarnia w Warszawie.", en:"This is the best café in Warsaw." },
                { pl:"Zima to najgorsza pora roku.", en:"Winter is the worst season." }
              ] },

            { front:"Than: niż or od?",
              sub:"Both mean 'than'. They just demand different grammar afterwards - pick whichever you can build fastest.",
              points:[
                "<b>niż</b> + Nominative - simply continue the sentence: On jest wyższy <b>niż ja</b>.",
                "<b>od</b> + Genitive - the noun changes case: On jest wyższy <b>od brata</b>.",
                "With 'me' the od-version has a special form: wyższy <b>ode mnie</b>.",
                "Both are equally natural - Poles switch between them freely."
              ],
              examples:[
                { pl:"Kawa jest tańsza niż herbata.", en:"Coffee is cheaper than tea." },
                { pl:"Kawa jest tańsza od herbaty.", en:"Coffee is cheaper than tea." }
              ] },

            { front:"Comparing adverbs: szybciej, lepiej",
              sub:"How you do something compares too - and the most common ones are irregular.",
              table:[
                { g:"szybko → szybciej", e:"faster", ex:"Mów wolniej, nie szybciej!" },
                { g:"dobrze → lepiej", e:"better", ex:"Dziś czuję się lepiej." },
                { g:"źle → gorzej", e:"worse", ex:"Wczoraj było gorzej." },
                { g:"dużo → więcej", e:"more", ex:"Potrzebuję więcej czasu." },
                { g:"mało → mniej", e:"less", ex:"Mam mniej pracy niż wczoraj." },
                { g:"często → częściej", e:"more often", ex:"Powinienem częściej ćwiczyć." }
              ],
              note:"Superlative works the same way: naj + comparative = <b>najlepiej</b>, <b>najszybciej</b>, <b>najczęściej</b>." },

            { front:"Set phrases built on comparison",
              sub:"These frozen patterns show up constantly - learn them as whole chunks.",
              table:[
                { g:"coraz + comparative", e:"more and more", ex:"Mówisz coraz lepiej po polsku!" },
                { g:"im..., tym...", e:"the..., the...", ex:"Im więcej ćwiczysz, tym lepiej mówisz." },
                { g:"jak naj + superlative", e:"as ... as possible", ex:"Przyjdź jak najszybciej." },
                { g:"coś jest coraz gorsze", e:"getting worse", ex:"Pogoda jest coraz gorsza." }
              ],
              note:"<b>coraz lepiej</b> is what Poles will start telling you about your Polish - now you'll know exactly what it means and how it's built." }
          ],
          drills: [
            { type:"choose", prompt:"Mój brat jest ___ ode mnie.", promptEn:"My brother is older than me.",
              options:["starszy","bardziej stary","najstarszy"], answer:"starszy",
              explain:"Short everyday adjective → -szy form. 'bardziej stary' is the classic error.", full:"Mój brat jest starszy ode mnie.", fullEn:"My brother is older than me." },
            { type:"choose", prompt:"Ta kawa jest ___ niż tamta.", promptEn:"This coffee is better than that one.",
              options:["lepsza","dobrzejsza","bardziej dobra"], answer:"lepsza",
              explain:"dobry is irregular: dobry → lepszy, here feminine lepsza.", full:"Ta kawa jest lepsza niż tamta.", fullEn:"This coffee is better than that one." },
            { type:"choose", prompt:"Potrzebuję ___ mieszkania.", promptEn:"I need a bigger flat.",
              options:["większego","dużejszego","bardziej dużego"], answer:"większego",
              explain:"duży → większy (irregular), here Genitive after potrzebować: większego.", full:"Potrzebuję większego mieszkania.", fullEn:"I need a bigger flat." },
            { type:"choose", prompt:"On jest wyższy ___ brata.", promptEn:"He is taller than his brother.",
              options:["od","niż","z"], answer:"od",
              explain:"Before Genitive 'brata' the word for 'than' is od. With niż it would stay Nominative: niż brat.", full:"On jest wyższy od brata.", fullEn:"He is taller than his brother." },
            { type:"choose", prompt:"Kawa jest tańsza ___ herbata.", promptEn:"Coffee is cheaper than tea.",
              options:["niż","od","do"], answer:"niż",
              explain:"'herbata' is Nominative, so 'than' must be niż. With od it would be: od herbaty.", full:"Kawa jest tańsza niż herbata.", fullEn:"Coffee is cheaper than tea." },
            { type:"choose", prompt:"To ___ restauracja w mieście.", promptEn:"This is the best restaurant in town.",
              options:["najlepsza","lepsza","najbardziej dobra"], answer:"najlepsza",
              explain:"Superlative = naj + comparative: naj + lepsza. 'The best' needs naj-.", full:"To najlepsza restauracja w mieście.", fullEn:"This is the best restaurant in town." },
            { type:"choose", prompt:"Ta książka jest ___ interesująca.", promptEn:"This book is more interesting.",
              options:["bardziej","więcej","najbardziej"], answer:"bardziej",
              explain:"Long adjectives compare with bardziej. 'więcej' is for amounts, not qualities.", full:"Ta książka jest bardziej interesująca.", fullEn:"This book is more interesting." },
            { type:"choose", prompt:"Dziś czuję się ___ niż wczoraj.", promptEn:"Today I feel better than yesterday.",
              options:["lepiej","lepszy","dobrzej"], answer:"lepiej",
              explain:"Feeling is an adverb situation: dobrze → lepiej. 'lepszy' would describe a noun.", full:"Dziś czuję się lepiej niż wczoraj.", fullEn:"Today I feel better than yesterday." },
            { type:"choose", prompt:"Mówisz ___ lepiej po polsku!", promptEn:"You speak Polish better and better!",
              options:["coraz","bardzo","więcej"], answer:"coraz",
              explain:"coraz + comparative = more and more: coraz lepiej.", full:"Mówisz coraz lepiej po polsku!", fullEn:"You speak Polish better and better!" },
            { type:"choose", prompt:"Przyjdź jak ___.", promptEn:"Come as soon as possible.",
              options:["najszybciej","szybciej","najszybszy"], answer:"najszybciej",
              explain:"jak naj + superlative adverb = as ... as possible: jak najszybciej.", full:"Przyjdź jak najszybciej.", fullEn:"Come as soon as possible." },
            { type:"choose", prompt:"Im więcej ćwiczysz, ___ lepiej mówisz.", promptEn:"The more you practise, the better you speak.",
              options:["tym","to","tam"], answer:"tym",
              explain:"The pair is fixed: im..., tym... - the..., the...", full:"Im więcej ćwiczysz, tym lepiej mówisz.", fullEn:"The more you practise, the better you speak." },
            { type:"choose", prompt:"Potrzebuję ___ czasu.", promptEn:"I need more time.",
              options:["więcej","bardziej","najwięcej"], answer:"więcej",
              explain:"An amount of time → więcej (dużo → więcej). 'bardziej' compares qualities.", full:"Potrzebuję więcej czasu.", fullEn:"I need more time." }
          ]
        },
        {
          name: "Liczebniki (Numbers meet cases)", emoji: "🔢", kind: "grammar", chip: "Grammar A2",
          desc: "dwa piwa but pięć piw - the number rules Polish is infamous for",
          teach: [
            { front:"The big three-way split",
              sub:"Every Polish number belongs to one of three teams, and the team decides what happens to the noun.",
              points:[
                "<b>1</b> - singular, agreeing in gender: jeden bilet, jedna kawa, jedno piwo.",
                "<b>2, 3, 4</b> - plural Nominative, like English: dwa bilety, trzy kawy, cztery piwa.",
                "<b>5 and up</b> - Genitive plural, and the verb goes singular: pięć biletów, sześć kaw, dziesięć piw.",
                "This is the single most famous rule in Polish. Once it clicks, ordering 'pięć piw' correctly feels like a superpower."
              ],
              examples:[
                { pl:"Dwa piwa poproszę.", en:"Two beers, please." },
                { pl:"Pięć piw poproszę.", en:"Five beers, please." }
              ] },

            { front:"The pattern side by side",
              sub:"Watch one word travel through all three teams.",
              table:[
                { g:"1", e:"jedno piwo / jedna kawa", ex:"Jedno piwo poproszę." },
                { g:"2-4", e:"dwa piwa / dwie kawy", ex:"Dwie kawy i trzy piwa." },
                { g:"5+", e:"pięć piw / pięć kaw", ex:"Pięć piw dla nas!" }
              ],
              note:"Feminine nouns take <b>dwie</b>, not dwa: <b>dwie</b> kawy, <b>dwie</b> godziny. Masculine and neuter share <b>dwa</b>: dwa bilety, dwa okna." },

            { front:"Compound numbers: the last word decides",
              sub:"22, 34, 95 - only the final digit-word matters. With two famous traps.",
              points:[
                "22 ends in 'dwa' → 2-4 team: dwadzieścia <b>dwa piwa</b>.",
                "25 ends in 'pięć' → 5+ team: dwadzieścia <b>pięć piw</b>.",
                "Trap 1: the teens <b>12, 13, 14</b> are single words, not compounds - they follow the 5+ rule: dwanaście <b>piw</b>.",
                "Trap 2: numbers ending in <b>jeden</b> (21, 31...) also take the 5+ rule, and jeden never changes: dwadzieścia jeden <b>piw</b>."
              ],
              examples:[
                { pl:"Mam dwadzieścia trzy lata.", en:"I am twenty-three years old." },
                { pl:"Ona ma dwadzieścia jeden lat.", en:"She is twenty-one years old." }
              ] },

            { front:"Years of age: rok, lata, lat",
              sub:"The word for 'year' follows the same three teams - and it's how everyone asks your age.",
              table:[
                { g:"1", e:"rok", ex:"Mieszkam tu rok." },
                { g:"2-4", e:"lata", ex:"On ma cztery lata." },
                { g:"5+", e:"lat", ex:"Mam trzydzieści lat." }
              ],
              note:"<b>Ile masz lat?</b> (how old are you?) uses lat because <b>ile</b> behaves like a 5+ number. So do <b>kilka</b> (a few), <b>wiele</b> (many), and <b>dużo</b>: kilka lat, dużo osób." },

            { front:"Money: złote czy złotych?",
              sub:"Prices are the rule's daily workout - you'll hear this at every till in Poland.",
              table:[
                { g:"1", e:"jeden złoty / jeden grosz", ex:"To kosztuje jeden złoty." },
                { g:"2-4", e:"dwa złote / dwa grosze", ex:"Dwa złote i trzy grosze." },
                { g:"5+", e:"pięć złotych / pięć groszy", ex:"Pięć złotych poproszę." },
                { g:"compound", e:"dwadzieścia dwa złote", ex:"To kosztuje dwadzieścia dwa złote." },
                { g:"teens trap", e:"czternaście złotych", ex:"Bilet kosztuje czternaście złotych." }
              ],
              note:"Cashiers speak fast, but they always follow the rule: 24,50 = 'dwadzieścia cztery złote pięćdziesiąt'. Listen for złote vs złotych - it tells you which team the number is on." },

            { front:"Counting men: the special forms",
              sub:"Groups that include men get their own number forms - the same masculine-personal theme as oni and wszyscy.",
              points:[
                "Everyday way: <b>dwóch panów</b> czekało, <b>trzech studentów</b> przyszło, <b>pięciu mężczyzn</b> pracuje - Genitive plural and a singular verb.",
                "Formal alternative for 2-4: <b>dwaj panowie</b> czekali, <b>trzej studenci</b> przyszli - Nominative with a plural verb. Both are correct.",
                "From 5 up there's only one option: <b>pięciu</b> panów, <b>sześciu</b> kolegów.",
                "Women and things never do this: dwie panie czekały, dwa autobusy przyjechały."
              ],
              examples:[
                { pl:"Dwóch kolegów czekało na mnie.", en:"Two friends were waiting for me." },
                { pl:"W firmie pracuje pięciu programistów.", en:"Five programmers work at the company." }
              ] },

            { front:"Survival chunks with numbers",
              sub:"Frozen phrases that hide the rule inside - use them whole from day one.",
              table:[
                { g:"twice / three times", e:"dwa razy / trzy razy", ex:"Byłem tam dwa razy." },
                { g:"5+ times", e:"pięć razy", ex:"Dzwoniłem pięć razy!" },
                { g:"a few people", e:"kilka osób", ex:"Przyszło tylko kilka osób." },
                { g:"in five minutes", e:"za pięć minut", ex:"Będę za pięć minut." },
                { g:"a couple of days", e:"parę dni", ex:"Wracam za parę dni." }
              ],
              note:"<b>raz / razy / razy</b>: jeden raz, dwa razy, pięć razy - 'razy' happens to look the same for both teams, one less thing to worry about." }
          ],
          drills: [
            { type:"choose", prompt:"Poproszę dwa ___.", promptEn:"Two beers, please.",
              options:["piwa","piw","piwo"], answer:"piwa",
              explain:"2-4 team → plural Nominative: dwa piwa.", full:"Poproszę dwa piwa.", fullEn:"Two beers, please." },
            { type:"choose", prompt:"Poproszę pięć ___.", promptEn:"Five beers, please.",
              options:["piw","piwa","piwo"], answer:"piw",
              explain:"5+ team → Genitive plural: pięć piw.", full:"Poproszę pięć piw.", fullEn:"Five beers, please." },
            { type:"choose", prompt:"Poproszę ___ kawy.", promptEn:"Two coffees, please.",
              options:["dwie","dwa","dwóch"], answer:"dwie",
              explain:"kawa is feminine → dwie, not dwa.", full:"Poproszę dwie kawy.", fullEn:"Two coffees, please." },
            { type:"choose", prompt:"To kosztuje dwadzieścia dwa ___.", promptEn:"It costs twenty-two zlotys.",
              options:["złote","złotych","złoty"], answer:"złote",
              explain:"Compound number ending in dwa → 2-4 team: złote.", full:"To kosztuje dwadzieścia dwa złote.", fullEn:"It costs twenty-two zlotys." },
            { type:"choose", prompt:"Bilet kosztuje czternaście ___.", promptEn:"The ticket costs fourteen zlotys.",
              options:["złotych","złote","złoty"], answer:"złotych",
              explain:"Teens trap: 12-14 are single words and follow the 5+ rule → złotych.", full:"Bilet kosztuje czternaście złotych.", fullEn:"The ticket costs fourteen zlotys." },
            { type:"choose", prompt:"Mam trzydzieści ___.", promptEn:"I am thirty years old.",
              options:["lat","lata","rok"], answer:"lat",
              explain:"30 ends the 5+ way → Genitive plural: lat.", full:"Mam trzydzieści lat.", fullEn:"I am thirty years old." },
            { type:"choose", prompt:"Moja córka ma trzy ___.", promptEn:"My daughter is three years old.",
              options:["lata","lat","roki"], answer:"lata",
              explain:"2-4 team → lata. ('roki' doesn't exist - rok goes rok / lata / lat.)", full:"Moja córka ma trzy lata.", fullEn:"My daughter is three years old." },
            { type:"choose", prompt:"Ona ma dwadzieścia jeden ___.", promptEn:"She is twenty-one years old.",
              options:["lat","lata","rok"], answer:"lat",
              explain:"Numbers ending in jeden take the 5+ rule, and jeden stays frozen: dwadzieścia jeden lat.", full:"Ona ma dwadzieścia jeden lat.", fullEn:"She is twenty-one years old." },
            { type:"choose", prompt:"Ile masz ___?", promptEn:"How old are you?",
              options:["lat","lata","roku"], answer:"lat",
              explain:"ile behaves like a 5+ number → Genitive plural: Ile masz lat?", full:"Ile masz lat?", fullEn:"How old are you?" },
            { type:"choose", prompt:"Pięć osób ___ na przystanku.", promptEn:"Five people are waiting at the stop.",
              options:["czeka","czekają","czekacie"], answer:"czeka",
              explain:"With 5+ numbers the verb goes singular: pięć osób czeka.", full:"Pięć osób czeka na przystanku.", fullEn:"Five people are waiting at the stop." },
            { type:"choose", prompt:"___ kolegów czekało na mnie.", promptEn:"Two friends (men) were waiting for me.",
              options:["Dwóch","Dwa","Dwie"], answer:"Dwóch",
              explain:"Counting men → the masculine-personal form dwóch + Genitive: dwóch kolegów.", full:"Dwóch kolegów czekało na mnie.", fullEn:"Two friends were waiting for me." },
            { type:"choose", prompt:"W firmie pracuje ___ programistów.", promptEn:"Five programmers work at the company.",
              options:["pięciu","pięć","pięcioro"], answer:"pięciu",
              explain:"Men from 5 up → pięciu + Genitive, singular verb: pracuje pięciu programistów.", full:"W firmie pracuje pięciu programistów.", fullEn:"Five programmers work at the company." },
            { type:"choose", prompt:"Byłem tam dwa ___.", promptEn:"I was there twice.",
              options:["razy","raz","razów"], answer:"razy",
              explain:"raz → dwa razy. Handy: razy also serves the 5+ team (pięć razy).", full:"Byłem tam dwa razy.", fullEn:"I was there twice." },
            { type:"choose", prompt:"Przyszło tylko kilka ___.", promptEn:"Only a few people came.",
              options:["osób","osoby","osobów"], answer:"osób",
              explain:"kilka behaves like 5+ → Genitive plural: kilka osób. ('osobów' doesn't exist.)", full:"Przyszło tylko kilka osób.", fullEn:"Only a few people came." }
          ]
        }
      ]
    }
  );
  window.PP_LEVELS.push(
    {
      level: "Politeness",
      blurb: "Pan, pani and formal address",
      group: "grammar",
      topics: [
        {
          name: "Pan i Pani (Formal address)", emoji: "\uD83D\uDE4B", kind: "grammar", chip: "Grammar A2",
          desc: "When to use pan/pani instead of ty - and the third-person rule that trips everyone up",
          teach: [
            { front:"Two ways to say 'you'",
              sub:"Polish makes you choose a register before you open your mouth.",
              points:[
                "<b>ty</b> - friends, family, children, people your own age you already know.",
                "<b>pan</b> (to a man) / <b>pani</b> (to a woman) - strangers, shops, offices, doctors, older people. This is the safe default with any adult you don't know.",
                "Getting this wrong isn't a grammar slip, it's a social one. When unsure, use pan/pani and let the other person offer ty."
              ],
              examples:[
                { pl:"Przepraszam, czy pan wie, gdzie jest apteka?", en:"Excuse me, do you know where the pharmacy is? (to a man)" },
                { pl:"Cześć, wiesz, gdzie jest apteka?", en:"Hi, do you know where the pharmacy is? (to a friend)" }
              ] },

            { front:"The golden rule: pan and pani take 'he/she' forms",
              sub:"This is the one thing to get right. Think of it as talking about someone who happens to be standing in front of you.",
              table:[
                { g:"ty", e:"wiesz", ex:"Wiesz, gdzie to jest?" },
                { g:"pan / pani", e:"wie", ex:"Czy pan wie, gdzie to jest?" },
                { g:"ty", e:"masz", ex:"Masz chwilę?" },
                { g:"pan / pani", e:"ma", ex:"Czy pani ma chwilę?" },
                { g:"ty", e:"chcesz", ex:"Chcesz kawę?" },
                { g:"pan / pani", e:"chce", ex:"Czy pani chce kawę?" }
              ],
              note:"So it's <b>Czy pan wie?</b> - never <i>czy pan wiesz</i>. Starting with <b>czy</b> also makes a formal question sound softer." },

            { front:"pan and pani in the cases",
              sub:"pan declines like a normal noun. pani barely moves - one form does nearly all the work.",
              table:[
                { g:"Mianownik", e:"pan / pani", ex:"Czy pan wie?" },
                { g:"Dopełniacz", e:"pana / pani", ex:"Nie ma pana w biurze." },
                { g:"Celownik", e:"panu / pani", ex:"Dziękuję panu." },
                { g:"Biernik", e:"pana / panią", ex:"Przepraszam panią." },
                { g:"Narzędnik", e:"panem / panią", ex:"Rozmawiam z panią." },
                { g:"Miejscownik", e:"panu / pani", ex:"Mówiliśmy o panu." }
              ],
              note:"Good news: <b>pani</b> only really changes to <b>panią</b> (biernik and narzędnik). Everywhere else it stays <i>pani</i>." },

            { front:"Talking to more than one person",
              sub:"Three plural forms, depending on who is in the group.",
              table:[
                { g:"panowie", e:"a group of men", ex:"Czy panowie są gotowi?" },
                { g:"panie", e:"a group of women", ex:"Czy panie mają bilety?" },
                { g:"państwo", e:"a mixed group / a couple", ex:"Czy państwo chcą stolik?" }
              ],
              note:"The verb goes to third person <b>plural</b>: państwo <b>chcą</b>, panowie <b>są</b>. In shops and restaurants you'll also hear the second-person plural - <i>Płacicie państwo razem czy osobno?</i> Strictly it should be <i>Czy państwo płacą...</i>, but the 'płacicie' version is everywhere in service Polish." },

            { front:"Softening, and switching to ty",
              sub:"Two everyday moves that make formal Polish feel natural rather than stiff.",
              points:[
                "<b>Proszę</b> + infinitive is the polite command: <i>Proszę usiąść.</i> You never need a bare imperative with a stranger.",
                "To get someone's attention: <b>proszę pana</b> / <b>proszę pani</b>.",
                "With a first name you get a middle register, common at work: <b>pan Marek → panie Marku</b>, <b>pani Anna → pani Anno</b>.",
                "Moving to ty is offered, not taken: <b>Czy możemy przejść na ty?</b> - usually proposed by the older or more senior person. In startups and many offices, ty is the default from day one."
              ],
              examples:[
                { pl:"Proszę pana, zgubił pan portfel.", en:"Excuse me sir, you dropped your wallet." },
                { pl:"Czy możemy przejść na ty?", en:"Shall we switch to first names?" }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"Czy pan ___, gdzie jest dworzec?", promptEn:"Do you know where the station is? (to a man)",
              options:["wiesz","wie","wiem"], answer:"wie",
              explain:"pan takes the on/ona form: wie, never wiesz.", full:"Czy pan wie, gdzie jest dworzec?", fullEn:"Do you know where the station is?" },
            { type:"choose", prompt:"Czy pani ___ chwilę?", promptEn:"Do you have a moment? (to a woman)",
              options:["masz","ma","mam"], answer:"ma",
              explain:"pani takes the on/ona form: ma.", full:"Czy pani ma chwilę?", fullEn:"Do you have a moment?" },
            { type:"choose", prompt:"Dziękuję ___ za pomoc.", promptEn:"Thank you for your help. (to a man)",
              options:["pan","pana","panu"], answer:"panu",
              explain:"dziękować + celownik (dative): panu.", full:"Dziękuję panu za pomoc.", fullEn:"Thank you for your help." },
            { type:"choose", prompt:"Przepraszam ___.", promptEn:"Excuse me. (to a woman)",
              options:["pani","panią","panu"], answer:"panią",
              explain:"przepraszać + biernik (accusative): panią - one of the two forms where pani changes.", full:"Przepraszam panią.", fullEn:"Excuse me." },
            { type:"choose", prompt:"Czy państwo ___ stolik?", promptEn:"Would you like a table? (to a couple)",
              options:["chce","chcą","chcecie"], answer:"chcą",
              explain:"państwo takes third person plural: chcą.", full:"Czy państwo chcą stolik?", fullEn:"Would you like a table?" },
            { type:"choose", prompt:"Czy panowie ___ gotowi?", promptEn:"Are you ready? (to a group of men)",
              options:["jest","są","jesteście"], answer:"są",
              explain:"panowie → third person plural of być: są.", full:"Czy panowie są gotowi?", fullEn:"Are you ready?" },
            { type:"choose", prompt:"___ usiąść.", promptEn:"Please sit down. (politely, to a stranger)",
              options:["Siądź","Proszę","Siadaj"], answer:"Proszę",
              explain:"Proszę + infinitive is the polite command; siądź / siadaj are for friends.", full:"Proszę usiąść.", fullEn:"Please sit down." },
            { type:"choose", prompt:"Rozmawiałam wczoraj z ___.", promptEn:"I spoke with you yesterday. (to a woman)",
              options:["pani","panią","panie"], answer:"panią",
              explain:"z + narzędnik (instrumental): z panią.", full:"Rozmawiałam wczoraj z panią.", fullEn:"I spoke with you yesterday." },
            { type:"choose", prompt:"Proszę ___, gdzie jest wyjście?", promptEn:"Excuse me sir, where's the exit?",
              options:["pan","pana","panu"], answer:"pana",
              explain:"'Proszę pana' gets a man's attention; 'proszę pani' for a woman.", full:"Proszę pana, gdzie jest wyjście?", fullEn:"Excuse me sir, where's the exit?" },
            { type:"build", promptEn:"Shall we switch to first names?",
              answer:["Czy","możemy","przejść","na","ty?"],
              explain:"'przejść na ty' = to move to first-name terms.", full:"Czy możemy przejść na ty?", fullEn:"Shall we switch to first names?" },
            { type:"build", promptEn:"Can I help you? (to a man)",
              answer:["Czy","mogę","panu","pomóc?"],
              explain:"pomóc + celownik (dative): pomóc panu.", full:"Czy mogę panu pomóc?", fullEn:"Can I help you?" }
          ]
        },

        /* 2 -------------------------------------- PLURAL FORMAL ADDRESS */
        {
          name: "Panowie, Panie, Państwo (Plural formal address)", emoji: "\uD83D\uDC65", kind: "grammar", chip: "Grammar A2",
          desc: "Addressing a group formally - and the past tense where the three forms split",
          teach: [
            { front:"Three ways to say 'you' to a group",
              sub:"Which one you pick depends entirely on who is standing in front of you.",
              points:[
                "<b>panowie</b> - two or more men.",
                "<b>panie</b> - two or more women.",
                "<b>państwo</b> - a mixed group, or a couple. One man and one woman is already państwo.",
                "This is the same logic as oni / one: one man in the group tips it to the 'men' form."
              ],
              examples:[
                { pl:"Czy panowie czekają na stolik?", en:"Are you waiting for a table? (to two men)" },
                { pl:"Czy panie mają rezerwację?", en:"Do you have a reservation? (to two women)" },
                { pl:"Czy państwo są razem?", en:"Are you together? (to a mixed couple)" }
              ] },

            { front:"The verb goes to 'they'",
              sub:"Just as pan / pani take the he-she form, all three plurals take the oni / one form.",
              table:[
                { g:"wy (informal)", e:"wiecie", ex:"Wiecie, gdzie to jest?" },
                { g:"panowie", e:"wiedzą", ex:"Czy panowie wiedzą, gdzie to jest?" },
                { g:"panie", e:"wiedzą", ex:"Czy panie wiedzą, gdzie to jest?" },
                { g:"państwo", e:"wiedzą", ex:"Czy państwo wiedzą, gdzie to jest?" },
                { g:"państwo", e:"są / mają", ex:"Czy państwo mają bilety?" },
                { g:"państwo", e:"chcą / płacą", ex:"Czy państwo płacą razem?" }
              ],
              note:"Good news: all three take the <b>same</b> verb form in the present. Pick the right noun and the verb takes care of itself - <b>są, mają, chcą, wiedzą, płacą</b>." },

            { front:"In the past tense, the group's gender shows",
              sub:"This is where the three forms finally split - and it catches everyone.",
              table:[
                { g:"panowie", e:"byli / mieli", ex:"Czy panowie byli zadowoleni?" },
                { g:"panie", e:"były / miały", ex:"Czy panie były zadowolone?" },
                { g:"państwo", e:"byli / mieli", ex:"Czy państwo byli zadowoleni?" }
              ],
              note:"<b>Państwo</b> counts as a mixed group, so it takes the men's form: <b>byli</b>, not <i>były</i>. The adjective follows too: <b>zadowoleni</b> (panowie, państwo) vs <b>zadowolone</b> (panie)." },

            { front:"państwo - the one you'll use most",
              sub:"In shops, restaurants, trains and emails, państwo is everywhere. These five forms cover it.",
              table:[
                { g:"Mianownik", e:"państwo", ex:"Czy państwo czekają?" },
                { g:"Dopełniacz", e:"państwa", ex:"To jest dla państwa." },
                { g:"Celownik", e:"państwu", ex:"Dziękuję państwu za spotkanie." },
                { g:"Biernik", e:"państwa", ex:"Przepraszam państwa!" },
                { g:"Narzędnik", e:"państwem", ex:"Miło mi z państwem współpracować." }
              ],
              note:"Written with a capital letter, <b>Szanowni Państwo</b> opens a formal email or announcement. With a small letter, <i>państwo</i> also means 'a state / country' - context makes it obvious." },

            { front:"What you'll actually hear",
              sub:"Real lines from real days out.",
              table:[
                { g:"w sklepie", e:"płacą", ex:"Czy państwo płacą razem czy osobno?" },
                { g:"w restauracji", e:"dla państwa", ex:"Co dla państwa?" },
                { g:"w pociągu", e:"proszę państwa", ex:"Proszę państwa, następna stacja: Centrum." },
                { g:"w mailu", e:"Szanowni Państwo", ex:"Szanowni Państwo, piszę w sprawie rezerwacji." }
              ],
              note:"You'll also hear the second-person plural in service Polish - <i>Płacicie państwo razem?</i> Strictly it should be <i>Czy państwo płacą...</i>, but the 'płacicie' version is everywhere." }
          ],
          drills: [
            { type:"choose", prompt:"Czy panowie ___ na stolik?", promptEn:"Are you waiting for a table? (to two men)",
              options:["czeka","czekają","czekacie"], answer:"czekają",
              explain:"panowie → third person plural: czekają.", full:"Czy panowie czekają na stolik?", fullEn:"Are you waiting for a table?" },
            { type:"choose", prompt:"Czy panie ___ rezerwację?", promptEn:"Do you have a reservation? (to two women)",
              options:["ma","mają","macie"], answer:"mają",
              explain:"panie → third person plural: mają.", full:"Czy panie mają rezerwację?", fullEn:"Do you have a reservation?" },
            { type:"choose", prompt:"Czy ___ są razem?", promptEn:"Are you together? (to a man and a woman)",
              options:["panowie","panie","państwo"], answer:"państwo",
              explain:"A mixed group → państwo. One man and one woman is enough.", full:"Czy państwo są razem?", fullEn:"Are you together?" },
            { type:"choose", prompt:"Dziękuję ___ za spotkanie.", promptEn:"Thank you for the meeting. (to a mixed group)",
              options:["państwo","państwa","państwu"], answer:"państwu",
              explain:"dziękować + celownik (dative): państwu.", full:"Dziękuję państwu za spotkanie.", fullEn:"Thank you for the meeting." },
            { type:"choose", prompt:"Przepraszam ___!", promptEn:"Excuse me! (to a mixed group)",
              options:["państwo","państwa","państwem"], answer:"państwa",
              explain:"przepraszać + biernik (accusative): państwa.", full:"Przepraszam państwa!", fullEn:"Excuse me!" },
            { type:"choose", prompt:"To jest dla ___.", promptEn:"This is for you. (to a couple)",
              options:["państwo","państwa","państwem"], answer:"państwa",
              explain:"dla + dopełniacz (genitive): dla państwa.", full:"To jest dla państwa.", fullEn:"This is for you." },
            { type:"choose", prompt:"Czy panowie ___ zadowoleni?", promptEn:"Were you satisfied? (to two men)",
              options:["były","byli","byliście"], answer:"byli",
              explain:"panowie (men) → byli, the -li form.", full:"Czy panowie byli zadowoleni?", fullEn:"Were you satisfied?" },
            { type:"choose", prompt:"Czy panie ___ zadowolone?", promptEn:"Were you satisfied? (to two women)",
              options:["byli","były","byłyście"], answer:"były",
              explain:"panie (all women) → były, the -ły form.", full:"Czy panie były zadowolone?", fullEn:"Were you satisfied?" },
            { type:"choose", prompt:"Czy państwo ___ zadowoleni z pokoju?", promptEn:"Were you satisfied with the room? (to a couple)",
              options:["były","byli","byliście"], answer:"byli",
              explain:"państwo is a mixed group → it takes the men's form: byli.", full:"Czy państwo byli zadowoleni z pokoju?", fullEn:"Were you satisfied with the room?" },
            { type:"build", promptEn:"Are you paying together or separately? (to a couple)",
              answer:["Czy","państwo","płacą","razem","czy","osobno?"],
              explain:"państwo + third person plural: płacą.", full:"Czy państwo płacą razem czy osobno?", fullEn:"Are you paying together or separately?" },
            { type:"build", promptEn:"What can I get you? (waiter, to a table)",
              answer:["Co","dla","państwa?"],
              explain:"dla + dopełniacz: dla państwa.", full:"Co dla państwa?", fullEn:"What can I get you?" }
          ]
        },

        /* 3 ---------------------------------------------- CONDITIONAL */
        {
          name: "Tryb przypuszczający (Conditional)", emoji: "\u2728", kind: "grammar", chip: "Grammar B1",
          desc: "Chciałbym, czy mógłby pan - the -bym ending that turns blunt into polite",
          teach: [
            { front:"What -bym does",
              sub:"It turns a blunt statement into a polite, soft, or hypothetical one. This is the politeness engine of Polish.",
              points:[
                "<b>Chcę kawę.</b> = I want a coffee. Correct, but blunt.",
                "<b>Chciałbym kawę.</b> = I'd like a coffee. This is what people actually say.",
                "It also carries English 'would': <i>Zrobiłbym to inaczej.</i> = I'd do it differently.",
                "Use it for requests, offers, suggestions, and soft refusals."
              ],
              examples:[
                { pl:"Chciałbym zamówić kawę.", en:"I'd like to order a coffee. (man speaking)" },
                { pl:"Chciałabym zamówić kawę.", en:"I'd like to order a coffee. (woman speaking)" }
              ] },

            { front:"How to build it",
              sub:"You already know every piece: it's the past tense stem + -by- + a person ending.",
              points:[
                "Take the past form: <b>chciał-</b> (m) / <b>chciała-</b> (f).",
                "Add <b>-by</b> plus the ending: chciał<b>bym</b>, chciał<b>byś</b>, chciał<b>by</b>.",
                "Because it sits on the past stem, it is <b>gendered</b> exactly like the past tense."
              ],
              table:[
                { g:"ja", e:"chciałbym / chciałabym", ex:"Chciałbym kawę." },
                { g:"ty", e:"chciałbyś / chciałabyś", ex:"Chciałabyś kawę?" },
                { g:"on / ona", e:"chciałby / chciałaby", ex:"Ona chciałaby zostać." },
                { g:"my", e:"chcielibyśmy / chciałybyśmy", ex:"Chcielibyśmy stolik." },
                { g:"wy", e:"chcielibyście / chciałybyście", ex:"Chcielibyście zostać?" },
                { g:"oni / one", e:"chcieliby / chciałyby", ex:"Oni chcieliby pomóc." }
              ] },

            { front:"The polite request toolkit",
              sub:"Four patterns cover almost every everyday situation.",
              table:[
                { g:"I'd like...", e:"Chciałbym / Chciałabym", ex:"Chciałbym zarezerwować stolik." },
                { g:"Could you...?", e:"Czy mógłby pan...?", ex:"Czy mógłby pan powtórzyć?" },
                { g:"Could I...?", e:"Czy mogłabym...?", ex:"Czy mogłabym prosić o rachunek?" },
                { g:"I'd prefer...", e:"Wolałbym / Wolałabym", ex:"Wolałbym jutro." }
              ],
              note:"Notice <b>Czy mógłby pan...?</b> - pan takes the he-form, so it's mógłby, not mógłbyś. Formal address and the conditional stack neatly." },

            { front:"Where the -bym jumps to",
              sub:"One quirk worth knowing, because it's how 'if' sentences work.",
              points:[
                "Normally the ending sits on the verb: <i>Chciał<b>bym</b> to zrobić.</i>",
                "After <b>gdyby</b> and <b>żeby</b>, it hops onto that word instead: <i>Chciałbym, <b>żebyś</b> przyszedł.</i>",
                "<b>Gdybym miał czas...</b> = If I had time... - this is the standard 'if' opener.",
                "The verb after it goes to the past form: gdybym <b>miał</b>, żebyś <b>przyszedł</b>."
              ],
              examples:[
                { pl:"Gdybym miał czas, poszedłbym z tobą.", en:"If I had time, I'd go with you." },
                { pl:"Chciałbym, żebyś przyszedł.", en:"I'd like you to come." }
              ] },

            { front:"Saying no, gently",
              sub:"The conditional is also how you decline without slamming a door.",
              points:[
                "<b>Wolałbym nie.</b> = I'd rather not.",
                "<b>Nie chciałbym przeszkadzać.</b> = I wouldn't want to intrude.",
                "<b>Mogłoby być lepiej.</b> = It could be better. (a soft complaint)",
                "Compare the register: <i>Powtórz!</i> (Repeat!) → <i>Czy mógłby pan powtórzyć?</i> (Could you repeat?)"
              ],
              examples:[
                { pl:"Wolałabym nie, dziękuję.", en:"I'd rather not, thank you." },
                { pl:"Czy mógłby pan mówić wolniej?", en:"Could you speak more slowly?" }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"___ zamówić kawę.", promptEn:"I'd like to order a coffee. (man speaking)",
              options:["Chciałabym","Chciałbym","Chcę"], answer:"Chciałbym",
              explain:"A man says chciałbym; chcę would be blunt here.", full:"Chciałbym zamówić kawę.", fullEn:"I'd like to order a coffee." },
            { type:"choose", prompt:"___ zamówić kawę.", promptEn:"I'd like to order a coffee. (woman speaking)",
              options:["Chciałbym","Chciałabym","Chciałaby"], answer:"Chciałabym",
              explain:"A woman uses the -abym ending: chciałabym.", full:"Chciałabym zamówić kawę.", fullEn:"I'd like to order a coffee." },
            { type:"choose", prompt:"Czy ___ pan powtórzyć?", promptEn:"Could you repeat that? (to a man)",
              options:["mógłbyś","mógłby","mógłbym"], answer:"mógłby",
              explain:"pan takes the he-form, so it's mógłby - not mógłbyś.", full:"Czy mógłby pan powtórzyć?", fullEn:"Could you repeat that?" },
            { type:"choose", prompt:"Czy ___ prosić o rachunek?", promptEn:"Could I have the bill? (woman speaking)",
              options:["mógłbym","mogłabym","mogłaby"], answer:"mogłabym",
              explain:"A woman asking about herself: mogłabym.", full:"Czy mogłabym prosić o rachunek?", fullEn:"Could I have the bill?" },
            { type:"choose", prompt:"Ona ___ zostać dłużej.", promptEn:"She'd like to stay longer.",
              options:["chciałby","chciałaby","chciałabym"], answer:"chciałaby",
              explain:"'ona' → chciałaby.", full:"Ona chciałaby zostać dłużej.", fullEn:"She'd like to stay longer." },
            { type:"choose", prompt:"My ___ stolik przy oknie.", promptEn:"We'd like a table by the window.",
              options:["chciałbym","chcielibyśmy","chcieliby"], answer:"chcielibyśmy",
              explain:"'my' (mixed or male group) → chcielibyśmy.", full:"Chcielibyśmy stolik przy oknie.", fullEn:"We'd like a table by the window." },
            { type:"choose", prompt:"___ miał czas, poszedłbym z tobą.", promptEn:"If I had time, I'd go with you.",
              options:["Gdyby","Gdybym","Żebym"], answer:"Gdybym",
              explain:"'if I' → gdybym; the -bym hops onto gdyby.", full:"Gdybym miał czas, poszedłbym z tobą.", fullEn:"If I had time, I'd go with you." },
            { type:"choose", prompt:"Chciałbym, ___ przyszedł.", promptEn:"I'd like you to come.",
              options:["żeby","żebyś","gdybyś"], answer:"żebyś",
              explain:"'that you' → żebyś; the ending jumps onto żeby.", full:"Chciałbym, żebyś przyszedł.", fullEn:"I'd like you to come." },
            { type:"choose", prompt:"___ nie, dziękuję.", promptEn:"I'd rather not, thank you. (woman speaking)",
              options:["Wolałbym","Wolałabym","Wolę"], answer:"Wolałabym",
              explain:"A woman: wolałabym - softer than the blunt 'nie chcę'.", full:"Wolałabym nie, dziękuję.", fullEn:"I'd rather not, thank you." },
            { type:"build", promptEn:"Could you speak more slowly? (to a man)",
              answer:["Czy","mógłby","pan","mówić","wolniej?"],
              explain:"pan + mógłby + infinitive.", full:"Czy mógłby pan mówić wolniej?", fullEn:"Could you speak more slowly?" },
            { type:"build", promptEn:"I'd like to book a table. (woman speaking)",
              answer:["Chciałabym","zarezerwować","stolik"],
              explain:"chciałabym + infinitive.", full:"Chciałabym zarezerwować stolik.", fullEn:"I'd like to book a table." }
          ]
        },

        /* 4 ---------------------------------------------- DIMINUTIVES */
        {
          name: "Zdrobnienia (Diminutives)", emoji: "\uD83D\uDE42", kind: "grammar", chip: "Grammar B1",
          desc: "Kawka, chwileczkę, piwko - how Polish shrinks words to sound warm",
          teach: [
            { front:"Polish shrinks words to be nice",
              sub:"A diminutive is not mainly about size. It's warmth, politeness, and softening.",
              points:[
                "<b>kawa → kawka</b> isn't a smaller coffee. It's a friendlier one.",
                "<b>chwila → chwileczkę</b> makes 'wait a moment' sound gentle instead of curt.",
                "Poles use them constantly - with food, drinks, time, money, and names.",
                "Recognising them matters more than building them: you'll hear far more than you'll make."
              ],
              examples:[
                { pl:"Chwileczkę, zaraz sprawdzę.", en:"Just a moment, I'll check right away." },
                { pl:"Masz ochotę na kawkę?", en:"Fancy a coffee?" }
              ] },

            { front:"How they're formed",
              sub:"Most take a predictable suffix, matched to the word's gender.",
              table:[
                { g:"-ek (masc)", e:"dom → domek", ex:"Mamy mały domek pod Warszawą." },
                { g:"-ka (fem)", e:"kawa → kawka", ex:"Skoczymy na kawkę?" },
                { g:"-ko (neut)", e:"piwo → piwko", ex:"Idziemy na piwko?" },
                { g:"-eczka", e:"chwila → chwileczka", ex:"Chwileczkę, proszę." },
                { g:"-usia (extra warm)", e:"kawa → kawusia", ex:"Zrobić ci kawusię?" }
              ],
              note:"The stem often shifts a little (kot → kot<b>ek</b>, chleb → chleb<b>ek</b>). Note the two coffees: <b>kawka</b> is the everyday default you'll hear constantly, while <b>kawusia</b> is a notch warmer and much rarer - affectionate, a bit sweet, often from older speakers. Learn the common ones as whole words rather than deriving them on the fly." },

            { front:"The ones you'll hear every day",
              sub:"These four will come at you within your first week.",
              table:[
                { g:"chwila", e:"chwileczkę", ex:"Chwileczkę, zaraz będę." },
                { g:"sekunda", e:"sekundkę", ex:"Sekundkę, szukam klucza." },
                { g:"moment", e:"momencik", ex:"Momencik, już idę." },
                { g:"pieniądze", e:"pieniążki", ex:"Nie mam pieniążków." }
              ],
              note:"<b>Chwileczkę</b> and <b>sekundkę</b> are in the accusative because they answer 'for how long?' - they're frozen as set phrases, so just learn the form." },

            { front:"Names - and when NOT to use diminutives",
              sub:"There is a line here, and crossing it is awkward.",
              points:[
                "Names shrink too: <b>Anna → Ania</b>, <b>Katarzyna → Kasia</b>, <b>Piotr → Piotrek</b>, <b>Tomasz → Tomek</b>.",
                "Using someone's diminutive name means you're on <b>ty</b> terms. Don't use it with a stranger or your boss's boss.",
                "In the wrong mouth they sound patronising: a clerk saying <i>pieniążki</i> to an adult can grate.",
                "Safe zone: food, drinks, time (<i>chwileczkę</i>), and friends."
              ],
              examples:[
                { pl:"Cześć, jestem Kasia.", en:"Hi, I'm Kasia. (from Katarzyna)" },
                { pl:"Momencik, zaraz będę.", en:"One moment, I'll be right there." }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"___, zaraz sprawdzę.", promptEn:"Just a moment, I'll check right away.",
              options:["Chwila","Chwileczkę","Chwilę"], answer:"Chwileczkę",
              explain:"The set phrase is chwileczkę - softer than the bare 'chwila'.", full:"Chwileczkę, zaraz sprawdzę.", fullEn:"Just a moment, I'll check right away." },
            { type:"choose", prompt:"Idziemy na ___?", promptEn:"Shall we go for a beer? (casually)",
              options:["piwo","piwko","piwek"], answer:"piwko",
              explain:"piwo → piwko (-ko for neuter). Friendlier than 'piwo'.", full:"Idziemy na piwko?", fullEn:"Shall we go for a beer?" },
            { type:"choose", prompt:"Masz ochotę na ___?", promptEn:"Fancy a coffee?",
              options:["kawka","kawkę","kawki"], answer:"kawkę",
              explain:"'na' + biernik: kawka → kawkę. This is the everyday diminutive of kawa.", full:"Masz ochotę na kawkę?", fullEn:"Fancy a coffee?" },
            { type:"choose", prompt:"Mamy mały ___ pod Warszawą.", promptEn:"We have a little house near Warsaw.",
              options:["dom","domek","domku"], answer:"domek",
              explain:"dom → domek (-ek for masculine).", full:"Mamy mały domek pod Warszawą.", fullEn:"We have a little house near Warsaw." },
            { type:"choose", prompt:"Katarzyna \u2192 ___", promptEn:"Katarzyna's everyday short form",
              options:["Kasia","Katka","Karolina"], answer:"Kasia",
              explain:"Katarzyna → Kasia. Using it means you're on ty terms.", full:"Cześć, jestem Kasia.", fullEn:"Hi, I'm Kasia." },
            { type:"choose", prompt:"___, już idę!", promptEn:"One moment, I'm coming!",
              options:["Moment","Momencik","Momentu"], answer:"Momencik",
              explain:"moment → momencik - warmer and very common.", full:"Momencik, już idę!", fullEn:"One moment, I'm coming!" },
            { type:"choose", prompt:"Nie mam ___.", promptEn:"I don't have any money. (diminutive)",
              options:["pieniążki","pieniążków","pieniądze"], answer:"pieniążków",
              explain:"nie mam + dopełniacz: pieniążki → pieniążków.", full:"Nie mam pieniążków.", fullEn:"I don't have any money." },
            { type:"build", promptEn:"Shall we pop out for a coffee?",
              answer:["Skoczymy","na","kawkę?"],
              explain:"kawa → kawka → na kawkę (biernik).", full:"Skoczymy na kawkę?", fullEn:"Shall we pop out for a coffee?" },
            { type:"build", promptEn:"Just a second, I'm looking for the key.",
              answer:["Sekundkę,","szukam","klucza"],
              explain:"sekundkę = the set phrase; szukać + dopełniacz: klucza.", full:"Sekundkę, szukam klucza.", fullEn:"Just a second, I'm looking for the key." }
          ]
        },

        /* 5 ------------------------------------------- FORMAL WRITING */
        {
          name: "Korespondencja (Formal writing)", emoji: "\u2709\uFE0F", kind: "grammar", chip: "Grammar B1",
          desc: "Emails, cover letters, and the Witam trap",
          teach: [
            { front:"Opening a formal message",
              sub:"Get the first line right and the rest follows.",
              table:[
                { g:"group / unknown", e:"Szanowni Państwo,", ex:"Szanowni Państwo, piszę w sprawie oferty." },
                { g:"to a woman", e:"Szanowna Pani,", ex:"Szanowna Pani, dziękuję za wiadomość." },
                { g:"to a man", e:"Szanowny Panie,", ex:"Szanowny Panie, w nawiązaniu do rozmowy..." },
                { g:"neutral / modern", e:"Dzień dobry,", ex:"Dzień dobry, mam pytanie o rezerwację." }
              ],
              note:"<b>Dzień dobry</b> at the top of an email is now completely normal - it's the safe modern default when Szanowni Państwo feels too stiff." },

            { front:"The Witam trap",
              sub:"The single most common opener mistake - and it's invisible to learners.",
              points:[
                "<b>Witam</b> looks like a friendly 'hello'. It actually means 'I welcome you', spoken from the position of a host.",
                "Opening an email to a stranger or someone senior with <i>Witam</i> reads as presumptuous or over-familiar to many Poles.",
                "It's fine downward or among equals you know - a boss to their team, a host to guests. It is <b>not</b> a neutral hello.",
                "Safe every time: <b>Szanowni Państwo</b> (formal) or <b>Dzień dobry</b> (neutral)."
              ],
              examples:[
                { pl:"Szanowni Państwo, piszę w sprawie oferty pracy.", en:"Dear Sir or Madam, I'm writing regarding the job offer." },
                { pl:"Dzień dobry, mam pytanie o rezerwację.", en:"Hello, I have a question about a reservation." }
              ] },

            { front:"Closing",
              sub:"Pick by distance, not by mood.",
              table:[
                { g:"most formal", e:"Z poważaniem", ex:"Z poważaniem, Anna Kowalska" },
                { g:"formal", e:"Z wyrazami szacunku", ex:"Z wyrazami szacunku, Jan Nowak" },
                { g:"everyday work", e:"Pozdrawiam", ex:"Pozdrawiam, Kasia" },
                { g:"warm", e:"Pozdrawiam serdecznie", ex:"Pozdrawiam serdecznie, Tomek" }
              ],
              note:"<b>Z poważaniem</b> is the CV and cover-letter default. <b>Pozdrawiam</b> is the everyday work default - after a couple of exchanges most people drop to it." },

            { front:"Phrases for the body",
              sub:"These five do most of the work in a normal email.",
              table:[
                { g:"I'm writing about", e:"Piszę w sprawie...", ex:"Piszę w sprawie oferty pracy." },
                { g:"with reference to", e:"W nawiązaniu do...", ex:"W nawiązaniu do naszej rozmowy telefonicznej." },
                { g:"I attach", e:"W załączeniu przesyłam...", ex:"W załączeniu przesyłam moje CV." },
                { g:"I'd be grateful", e:"Będę wdzięczny / wdzięczna", ex:"Będę wdzięczna za szybką odpowiedź." },
                { g:"thanks in advance", e:"Z góry dziękuję", ex:"Z góry dziękuję za pomoc." }
              ],
              note:"<b>Będę wdzięczny / wdzięczna</b> is gendered: a man writes wdzięczny, a woman wdzięczna. <b>Piszę w sprawie</b> + dopełniacz: w sprawie ofert<b>y</b>." }
          ],
          drills: [
            { type:"choose", prompt:"___ Państwo, piszę w sprawie oferty.", promptEn:"Dear Sir or Madam, I'm writing regarding the offer.",
              options:["Szanowni","Drodzy","Witam"], answer:"Szanowni",
              explain:"The standard formal opener is Szanowni Państwo.", full:"Szanowni Państwo, piszę w sprawie oferty.", fullEn:"Dear Sir or Madam, I'm writing regarding the offer." },
            { type:"choose", prompt:"Mail do nieznajomej osoby zaczynasz: ___", promptEn:"Opening an email to someone you don't know",
              options:["Witam,","Dzień dobry,","Cześć,"], answer:"Dzień dobry,",
              explain:"'Witam' sounds presumptuous to a stranger; 'Dzień dobry' is the safe neutral opener.", full:"Dzień dobry, mam pytanie o rezerwację.", fullEn:"Hello, I have a question about a reservation." },
            { type:"choose", prompt:"___ Pani, dziękuję za wiadomość.", promptEn:"Dear Madam, thank you for your message.",
              options:["Szanowny","Szanowna","Szanowni"], answer:"Szanowna",
              explain:"To a woman: Szanowna Pani.", full:"Szanowna Pani, dziękuję za wiadomość.", fullEn:"Dear Madam, thank you for your message." },
            { type:"choose", prompt:"List motywacyjny kończysz: ___", promptEn:"Closing a cover letter",
              options:["Cześć","Z poważaniem","Trzymaj się"], answer:"Z poważaniem",
              explain:"Z poważaniem is the CV and cover-letter default.", full:"Z poważaniem, Anna Kowalska", fullEn:"Yours faithfully, Anna Kowalska" },
            { type:"choose", prompt:"Mail do kolegi z zespołu kończysz: ___", promptEn:"Closing an email to a teammate",
              options:["Z poważaniem","Pozdrawiam","Z wyrazami szacunku"], answer:"Pozdrawiam",
              explain:"Pozdrawiam is the everyday work default - Z poważaniem would be stiff here.", full:"Pozdrawiam, Kasia", fullEn:"Best regards, Kasia" },
            { type:"choose", prompt:"W ___ przesyłam moje CV.", promptEn:"I'm attaching my CV.",
              options:["załączeniu","nawiązaniu","sprawie"], answer:"załączeniu",
              explain:"W załączeniu przesyłam... = please find attached.", full:"W załączeniu przesyłam moje CV.", fullEn:"I'm attaching my CV." },
            { type:"choose", prompt:"Piszę w ___ rezerwacji.", promptEn:"I'm writing regarding a reservation.",
              options:["sprawie","sprawa","sprawę"], answer:"sprawie",
              explain:"'w sprawie' + dopełniacz: w sprawie rezerwacji.", full:"Piszę w sprawie rezerwacji.", fullEn:"I'm writing regarding a reservation." },
            { type:"choose", prompt:"Będę ___ za szybką odpowiedź.", promptEn:"I'd be grateful for a quick reply. (woman writing)",
              options:["wdzięczny","wdzięczna","wdzięczni"], answer:"wdzięczna",
              explain:"A woman writes wdzięczna; a man wdzięczny.", full:"Będę wdzięczna za szybką odpowiedź.", fullEn:"I'd be grateful for a quick reply." },
            { type:"build", promptEn:"Thanks in advance for your help.",
              answer:["Z","góry","dziękuję","za","pomoc"],
              explain:"'Z góry dziękuję za' + biernik: za pomoc.", full:"Z góry dziękuję za pomoc.", fullEn:"Thanks in advance for your help." },
            { type:"build", promptEn:"With reference to our phone conversation.",
              answer:["W","nawiązaniu","do","naszej","rozmowy","telefonicznej"],
              explain:"'W nawiązaniu do' + dopełniacz: do rozmowy.", full:"W nawiązaniu do naszej rozmowy telefonicznej.", fullEn:"With reference to our phone conversation." }
          ]
        }
      ]
    }
  );

  window.PP_LEVELS.push(
    {
      level: "Building Sentences",
      blurb: "który, jeśli, żeby - joining ideas together",
      group: "grammar",
      topics: [
        {
          name: "Który (Relative clauses)", emoji: "🔗", kind: "grammar", chip: "Grammar B1",
          desc: "The man who..., the film that... - który declines like an adjective",
          teach: [
            { front:"What który does",
              sub:"It glues a description onto a noun - the man <b>who</b> lives here, the film <b>that</b> we watched.",
              points:[
                "który stands in for the noun inside the added clause: Człowiek, <b>który</b> tu mieszka... (the man who lives here).",
                "It's one word for who / which / that - Polish doesn't split them the way English does.",
                "A comma always comes before it. Polish commas are grammar, not style: <i>Człowiek<b>,</b> który...</i>",
                "The good news: który declines exactly like an adjective - everything from the case lessons transfers."
              ],
              examples:[
                { pl:"Człowiek, który tam stoi, to mój sąsiad.", en:"The man who is standing there is my neighbour." },
                { pl:"Film, który oglądaliśmy, był świetny.", en:"The film that we watched was great." }
              ] },

            { front:"Gender and number come from the noun",
              sub:"Look left at the noun being described - który copies its gender and number.",
              table:[
                { g:"masculine", e:"który", ex:"chłopak, który..." },
                { g:"feminine", e:"która", ex:"kobieta, która..." },
                { g:"neuter", e:"które", ex:"dziecko, które..." },
                { g:"men / mixed group", e:"którzy", ex:"ludzie, którzy..." },
                { g:"other plurals", e:"które", ex:"książki, które..." }
              ],
              note:"<b>którzy</b> is the same masculine-personal club as oni and wszyscy - people-with-a-man get their own form, everything else takes które." },

            { front:"The case comes from the clause",
              sub:"Gender from the left, case from the right: whatever job który does inside its own clause sets the case.",
              points:[
                "Subject of the clause → Nominative: Kobieta, <b>która</b> tu pracuje...",
                "Object of the clause → Accusative: Kobieta, <b>którą</b> poznałem... (I met <i>her</i> → object).",
                "Receiving something → Dative: Dziewczyna, <b>której</b> dałem kwiaty...",
                "This is why the same noun can be followed by different forms - the clause decides."
              ],
              examples:[
                { pl:"Kobieta, która tu pracuje, jest z Krakowa.", en:"The woman who works here is from Krakow." },
                { pl:"Kobieta, którą wczoraj poznałem, jest z Krakowa.", en:"The woman I met yesterday is from Krakow." }
              ] },

            { front:"With prepositions: z którym, w którym",
              sub:"The preposition moves to the front of który and brings its case along - no dangling prepositions like in English.",
              table:[
                { g:"z + Instrumental", e:"z którym / z którą", ex:"kolega, z którym pracuję" },
                { g:"w + Locative", e:"w którym / w której", ex:"mieszkanie, w którym mieszkam" },
                { g:"o + Locative", e:"o którym / o której", ex:"film, o którym mówiłem" },
                { g:"na + Accusative", e:"na który / na którą", ex:"autobus, na który czekam" },
                { g:"do + Genitive", e:"do którego / do której", ex:"sklep, do którego chodzę" }
              ],
              note:"English says 'the flat I live <b>in</b>'. Polish never leaves the preposition at the end: <i>mieszkanie, <b>w którym</b> mieszkam</i>." },

            { front:"co - when there's no noun",
              sub:"For 'that which / what / everything that', Polish switches from który to co.",
              points:[
                "After to, wszystko, nic: <i>wszystko, <b>co</b> mam</i> - everything (that) I have.",
                "<b>to, co</b> = 'what' as a thing: <i>Rób <b>to, co</b> lubisz</i> - do what you like.",
                "który needs a concrete noun to lean on; co covers the abstract leftovers."
              ],
              examples:[
                { pl:"To wszystko, co mam.", en:"That's everything I have." },
                { pl:"Nie rozumiem tego, co mówisz.", en:"I don't understand what you're saying." }
              ] }
          ],
          drills: [
            { type:"choose", prompt:"Człowiek, ___ tam stoi, to mój sąsiad.", promptEn:"The man who is standing there is my neighbour.",
              options:["który","którego","którym"], answer:"który",
              explain:"He is the subject of 'stoi' → Nominative: który.", full:"Człowiek, który tam stoi, to mój sąsiad.", fullEn:"The man who is standing there is my neighbour." },
            { type:"choose", prompt:"Kobieta, ___ wczoraj poznałem, jest z Krakowa.", promptEn:"The woman I met yesterday is from Krakow.",
              options:["którą","która","której"], answer:"którą",
              explain:"I met HER - object of poznać → Accusative feminine: którą.", full:"Kobieta, którą wczoraj poznałem, jest z Krakowa.", fullEn:"The woman I met yesterday is from Krakow." },
            { type:"choose", prompt:"Ludzie, ___ tu pracują, są bardzo mili.", promptEn:"The people who work here are very nice.",
              options:["którzy","które","który"], answer:"którzy",
              explain:"ludzie = people with men → masculine-personal plural: którzy.", full:"Ludzie, którzy tu pracują, są bardzo mili.", fullEn:"The people who work here are very nice." },
            { type:"choose", prompt:"Książki, ___ czytam, są po polsku.", promptEn:"The books I read are in Polish.",
              options:["które","którzy","których"], answer:"które",
              explain:"Books are things → które (never którzy), and inanimate Accusative looks like Nominative.", full:"Książki, które czytam, są po polsku.", fullEn:"The books I read are in Polish." },
            { type:"choose", prompt:"Kolega, z ___ pracuję, jest z Ukrainy.", promptEn:"The colleague I work with is from Ukraine.",
              options:["którym","który","którego"], answer:"którym",
              explain:"z + Instrumental → z którym.", full:"Kolega, z którym pracuję, jest z Ukrainy.", fullEn:"The colleague I work with is from Ukraine." },
            { type:"choose", prompt:"Mieszkanie, w ___ mieszkam, jest małe.", promptEn:"The flat I live in is small.",
              options:["którym","które","którego"], answer:"którym",
              explain:"w + Locative → w którym. Polish never leaves 'in' at the end of the sentence.", full:"Mieszkanie, w którym mieszkam, jest małe.", fullEn:"The flat I live in is small." },
            { type:"choose", prompt:"Dziewczyna, ___ dałem kwiaty, ma na imię Ola.", promptEn:"The girl I gave flowers to is called Ola.",
              options:["której","którą","która"], answer:"której",
              explain:"Giving TO her → Dative feminine: której.", full:"Dziewczyna, której dałem kwiaty, ma na imię Ola.", fullEn:"The girl I gave flowers to is called Ola." },
            { type:"choose", prompt:"Autobus, na ___ czekam, ma opóźnienie.", promptEn:"The bus I'm waiting for is delayed.",
              options:["który","którym","którego"], answer:"który",
              explain:"czekać na + Accusative; bus is inanimate, so Accusative = Nominative: na który.", full:"Autobus, na który czekam, ma opóźnienie.", fullEn:"The bus I'm waiting for is delayed." },
            { type:"choose", prompt:"Film, o ___ mówiłem, jest w kinie.", promptEn:"The film I was talking about is in the cinema.",
              options:["którym","który","którego"], answer:"którym",
              explain:"mówić o + Locative → o którym.", full:"Film, o którym mówiłem, jest w kinie.", fullEn:"The film I was talking about is in the cinema." },
            { type:"choose", prompt:"Rób to, ___ lubisz.", promptEn:"Do what you like.",
              options:["co","które","który"], answer:"co",
              explain:"After 'to' with no concrete noun → co, not który.", full:"Rób to, co lubisz.", fullEn:"Do what you like." },
            { type:"choose", prompt:"To wszystko, ___ mam.", promptEn:"That's everything I have.",
              options:["co","które","czego"], answer:"co",
              explain:"After wszystko → co.", full:"To wszystko, co mam.", fullEn:"That's everything I have." },
            { type:"choose", prompt:"Sklep, do ___ chodzę, jest za rogiem.", promptEn:"The shop I go to is around the corner.",
              options:["którego","którym","który"], answer:"którego",
              explain:"do + Genitive → do którego.", full:"Sklep, do którego chodzę, jest za rogiem.", fullEn:"The shop I go to is around the corner." }
          ]
        },
        {
          name: "Jeśli i gdyby (Conditions)", emoji: "🔀", kind: "grammar", chip: "Grammar B1",
          desc: "Real ifs vs what-ifs - and the future tense English hides",
          teach: [
            { front:"Two kinds of if",
              sub:"Polish splits 'if' by how real the situation is.",
              points:[
                "<b>jeśli</b> - real, possible, might well happen: <i>Jeśli będzie padać, zostanę w domu.</i>",
                "<b>gdyby</b> - hypothetical, imagined, probably not: <i>Gdybym miał milion, kupiłbym dom.</i>",
                "Quick test: can you sensibly add 'and we'll see'? Then it's jeśli. Is it daydreaming? Then gdyby.",
                "<b>jeżeli</b> = jeśli, just slightly more formal. <b>jak</b> = jeśli in casual speech: <i>Jak będziesz w Warszawie, zadzwoń.</i>"
              ],
              examples:[
                { pl:"Jeśli masz czas, chodź z nami.", en:"If you have time, come with us." },
                { pl:"Gdybym miał czas, poszedłbym z wami.", en:"If I had time, I would go with you." }
              ] },

            { front:"The future English hides",
              sub:"The number-one error zone: English says 'if it rains' in the present. Polish says the future out loud.",
              points:[
                "English: If it <b>rains</b> tomorrow... Polish: Jeśli jutro <b>będzie padać</b>...",
                "Both halves can be future: Jeśli <b>będę miał</b> czas, <b>przyjdę</b>.",
                "Saying <i>jeśli pada jutro</i> is the direct-translation trap - if the condition is about the future, use the future."
              ],
              examples:[
                { pl:"Jeśli będzie ładna pogoda, pojedziemy nad jezioro.", en:"If the weather is nice, we'll go to the lake." },
                { pl:"Jeśli będziesz miał pytania, napisz do mnie.", en:"If you have questions, write to me." }
              ] },

            { front:"gdyby carries personal endings",
              sub:"gdyby conjugates like a verb - the ending tells you who, and the verb after it takes the past form.",
              table:[
                { g:"ja", e:"gdybym", ex:"Gdybym wiedział..." },
                { g:"ty", e:"gdybyś", ex:"Gdybyś chciał..." },
                { g:"on / ona", e:"gdyby", ex:"Gdyby mogła..." },
                { g:"my", e:"gdybyśmy", ex:"Gdybyśmy mieli czas..." },
                { g:"wy", e:"gdybyście", ex:"Gdybyście byli głodni..." }
              ],
              note:"The verb after gdyby- is in the past form and agrees with your gender: gdybym <b>miał</b> (a man) / gdybym <b>miała</b> (a woman) - the same -ł/-ła split as the normal past tense." },

            { front:"The other half: -bym in the result",
              sub:"A gdyby sentence usually answers with the conditional you know from Politeness: kupiłbym, poszłabym.",
              points:[
                "Pattern: <b>Gdybym</b> miał pieniądze, <b>kupiłbym</b> samochód.",
                "Optional <b>to</b> can open the second half: Gdybym mógł, <b>to</b> bym pomógł.",
                "The 'by' is mobile - <i>kupiłbym</i> and <i>bym kupił</i> both work; the meaning doesn't change.",
                "You've already met this machinery in <i>Tryb przypuszczający</i> - here it's just doing what-if work instead of politeness work."
              ],
              examples:[
                { pl:"Gdybym miał pieniądze, kupiłbym samochód.", en:"If I had money, I would buy a car." },
                { pl:"Co byś zrobił, gdybyś wygrał milion?", en:"What would you do if you won a million?" }
              ] },

            { front:"Everyday if-phrases",
              sub:"Chunks you'll hear daily - each one quietly follows the rules above.",
              table:[
                { g:"if I were you", e:"na twoim miejscu", ex:"Na twoim miejscu bym zadzwonił." },
                { g:"if necessary", e:"jeśli trzeba / w razie czego", ex:"W razie czego dzwoń." },
                { g:"casual if", e:"jak", ex:"Jak coś, jestem u siebie." },
                { g:"if possible", e:"jeśli to możliwe", ex:"Jeśli to możliwe, wolę rano." }
              ],
              note:"<b>Jak coś...</b> (literally 'if something...') is the Polish 'if anything comes up' - vague, friendly, and everywhere." }
          ],
          drills: [
            { type:"choose", prompt:"___ będzie padać, zostanę w domu.", promptEn:"If it rains, I'll stay home.",
              options:["Jeśli","Gdyby","Żeby"], answer:"Jeśli",
              explain:"Real, possible situation → jeśli. Gdyby would make it a daydream.", full:"Jeśli będzie padać, zostanę w domu.", fullEn:"If it rains, I'll stay home." },
            { type:"choose", prompt:"Jeśli jutro ___ czas, przyjdę.", promptEn:"If I have time tomorrow, I'll come.",
              options:["będę miał","mam","miałbym"], answer:"będę miał",
              explain:"The condition is about tomorrow → future tense, even though English says 'have'.", full:"Jeśli jutro będę miał czas, przyjdę.", fullEn:"If I have time tomorrow, I'll come." },
            { type:"choose", prompt:"___ miał milion, kupiłbym mieszkanie.", promptEn:"If I had a million, I would buy a flat.",
              options:["Gdybym","Jeśli","Gdyby"], answer:"Gdybym",
              explain:"Hypothetical + 'I' → gdyby with the -m ending: gdybym.", full:"Gdybym miał milion, kupiłbym mieszkanie.", fullEn:"If I had a million, I would buy a flat." },
            { type:"choose", prompt:"Gdybym wiedział, ___ ci.", promptEn:"If I had known, I would have told you.",
              options:["powiedziałbym","powiem","powiedziałem"], answer:"powiedziałbym",
              explain:"The result half of a gdyby sentence takes -by: powiedziałbym.", full:"Gdybym wiedział, powiedziałbym ci.", fullEn:"If I had known, I would have told you." },
            { type:"choose", prompt:"Co byś zrobił, ___ wygrał milion?", promptEn:"What would you do if you won a million?",
              options:["gdybyś","jeśli","gdybym"], answer:"gdybyś",
              explain:"Hypothetical + 'you' → gdybyś. The -ś ending marks ty.", full:"Co byś zrobił, gdybyś wygrał milion?", fullEn:"What would you do if you won a million?" },
            { type:"choose", prompt:"___ mieli czas, pojechalibyśmy nad morze.", promptEn:"If we had time, we would go to the seaside.",
              options:["Gdybyśmy","Gdybym","Jeśli"], answer:"Gdybyśmy",
              explain:"Hypothetical + 'we' → gdybyśmy.", full:"Gdybyśmy mieli czas, pojechalibyśmy nad morze.", fullEn:"If we had time, we would go to the seaside." },
            { type:"choose", prompt:"Jeśli będziesz w Warszawie, ___ do mnie.", promptEn:"If you're in Warsaw, call me.",
              options:["zadzwoń","zadzwoniłbyś","dzwoniłeś"], answer:"zadzwoń",
              explain:"Real condition → the result can simply be an imperative: zadzwoń.", full:"Jeśli będziesz w Warszawie, zadzwoń do mnie.", fullEn:"If you're in Warsaw, call me." },
            { type:"choose", prompt:"Na twoim miejscu ___ zadzwonił.", promptEn:"If I were you, I would call.",
              options:["bym","by","będę"], answer:"bym",
              explain:"na twoim miejscu + conditional; 'by' takes the -m for ja: bym zadzwonił.", full:"Na twoim miejscu bym zadzwonił.", fullEn:"If I were you, I would call." },
            { type:"choose", prompt:"Gdyby ona ___, na pewno by przyszła.", promptEn:"If she could, she would definitely come.",
              options:["mogła","mógł","może"], answer:"mogła",
              explain:"After gdyby the verb is a past form agreeing with gender: ona → mogła.", full:"Gdyby ona mogła, na pewno by przyszła.", fullEn:"If she could, she would definitely come." },
            { type:"choose", prompt:"___ coś, jestem u siebie.", promptEn:"If anything comes up, I'm at my place.",
              options:["Jak","Gdyby","Który"], answer:"Jak",
              explain:"Casual speech uses jak for jeśli: Jak coś... - the everyday 'if anything'.", full:"Jak coś, jestem u siebie.", fullEn:"If anything comes up, I'm at my place." }
          ]
        },
        {
          name: "Żeby (So that / want to)", emoji: "🎯", kind: "grammar", chip: "Grammar B1",
          desc: "Chcę, żebyś przyszedł - wanting, asking, and doing things for a purpose",
          teach: [
            { front:"What żeby does",
              sub:"One little word covers 'in order to', 'so that', and 'want someone to' - three things English builds differently.",
              points:[
                "Purpose: Uczę się, <b>żeby</b> zdać egzamin - I study (in order) to pass.",
                "Wanting someone else to act: Chcę, <b>żebyś</b> przyszedł - I want you to come.",
                "English has no direct equivalent of that second one - 'I want that you come' is exactly how Polish thinks.",
                "<b>aby</b> = żeby, one notch more formal. You'll see it in emails and official texts."
              ],
              examples:[
                { pl:"Uczę się polskiego, żeby rozmawiać z sąsiadami.", en:"I'm learning Polish to talk with my neighbours." },
                { pl:"Chcę, żebyś przyszedł na moje urodziny.", en:"I want you to come to my birthday." }
              ] },

            { front:"Same subject: żeby + infinitive",
              sub:"When the same person does both halves, keep it simple - infinitive.",
              points:[
                "Pracuję dużo, <b>żeby zarobić</b> na wakacje - I work a lot to earn for holidays. (I work, I earn.)",
                "Dzwonię, <b>żeby zapytać</b> o godziny otwarcia - I'm calling to ask about opening hours.",
                "Negative purpose works the same way: Mówię cicho, <b>żeby nie obudzić</b> dziecka - so as not to wake the child."
              ],
              examples:[
                { pl:"Wyszedłem wcześniej, żeby zdążyć na pociąg.", en:"I left earlier to make the train." },
                { pl:"Mówię cicho, żeby nie obudzić dziecka.", en:"I'm speaking quietly so as not to wake the child." }
              ] },

            { front:"Different subjects: żeby grows endings",
              sub:"When someone else should do it, żeby conjugates - the same endings as gdyby.",
              table:[
                { g:"ja", e:"żebym", ex:"Szef chce, żebym został." },
                { g:"ty", e:"żebyś", ex:"Chcę, żebyś wiedział." },
                { g:"on / ona", e:"żeby", ex:"Proszę, żeby zaczekał." },
                { g:"my", e:"żebyśmy", ex:"Chcą, żebyśmy przyszli." },
                { g:"wy", e:"żebyście", ex:"Chcemy, żebyście wiedzieli." }
              ],
              note:"And just like gdyby, the verb after it takes the <b>past form</b>: żebyś przyszed<b>ł</b> (to a man) / przysz<b>ła</b> (to a woman) - even though nothing past is happening." },

            { front:"The verbs that trigger it",
              sub:"A small club of verbs almost always hands off to żeby when another person is involved.",
              table:[
                { g:"chcieć", e:"to want", ex:"Chcę, żebyś to zobaczył." },
                { g:"prosić", e:"to ask / request", ex:"Proszę, żebyś był punktualny." },
                { g:"powiedzieć / mówić", e:"to tell (someone to do)", ex:"Powiedz mu, żeby zadzwonił." },
                { g:"zależeć (mi na tym)", e:"to care / matter", ex:"Zależy mi, żeby wszystko było gotowe." },
                { g:"woleć", e:"to prefer", ex:"Wolę, żebyśmy zostali w domu." }
              ],
              note:"Telling someone to do something = powiedzieć + żeby: <i>Powiedz jej, żeby przyszła</i> - literally 'tell her that she should come'." }
          ],
          drills: [
            { type:"choose", prompt:"Chcę, ___ przyszedł na moje urodziny.", promptEn:"I want you to come to my birthday.",
              options:["żebyś","żeby","jeśli"], answer:"żebyś",
              explain:"You should come → żeby + the -ś ending for ty: żebyś.", full:"Chcę, żebyś przyszedł na moje urodziny.", fullEn:"I want you to come to my birthday." },
            { type:"choose", prompt:"Uczę się polskiego, ___ rozmawiać z sąsiadami.", promptEn:"I'm learning Polish to talk with my neighbours.",
              options:["żeby","żebym","który"], answer:"żeby",
              explain:"Same person learns and talks → plain żeby + infinitive.", full:"Uczę się polskiego, żeby rozmawiać z sąsiadami.", fullEn:"I'm learning Polish to talk with my neighbours." },
            { type:"choose", prompt:"Prosiłem go, żeby ___.", promptEn:"I asked him to help.",
              options:["pomógł","pomóc","pomoże"], answer:"pomógł",
              explain:"Different subject after żeby → past form: żeby pomógł, not the infinitive.", full:"Prosiłem go, żeby pomógł.", fullEn:"I asked him to help." },
            { type:"choose", prompt:"Powiedz jej, ___ zadzwoniła do mnie.", promptEn:"Tell her to call me.",
              options:["żeby","żebyś","żebym"], answer:"żeby",
              explain:"She should call - third person → plain żeby (the ending stays empty for on/ona).", full:"Powiedz jej, żeby zadzwoniła do mnie.", fullEn:"Tell her to call me." },
            { type:"choose", prompt:"Mówię cicho, żeby nie ___ dziecka.", promptEn:"I'm speaking quietly so as not to wake the child.",
              options:["obudzić","obudził","obudzę"], answer:"obudzić",
              explain:"Same subject (I speak, I would wake) → infinitive after żeby nie.", full:"Mówię cicho, żeby nie obudzić dziecka.", fullEn:"I'm speaking quietly so as not to wake the child." },
            { type:"choose", prompt:"Chcą, ___ przyszli na spotkanie.", promptEn:"They want us to come to the meeting.",
              options:["żebyśmy","żebyście","żeby"], answer:"żebyśmy",
              explain:"We should come → żebyśmy.", full:"Chcą, żebyśmy przyszli na spotkanie.", fullEn:"They want us to come to the meeting." },
            { type:"choose", prompt:"Zależy mi, ___ wszystko było gotowe.", promptEn:"I care that everything is ready.",
              options:["żeby","jeśli","które"], answer:"żeby",
              explain:"zależeć mi hands off to żeby: zależy mi, żeby...", full:"Zależy mi, żeby wszystko było gotowe.", fullEn:"I care that everything is ready." },
            { type:"choose", prompt:"Wyszedłem wcześniej, żeby ___ na pociąg.", promptEn:"I left earlier to make the train.",
              options:["zdążyć","zdążył","zdążę"], answer:"zdążyć",
              explain:"Same subject → infinitive: żeby zdążyć.", full:"Wyszedłem wcześniej, żeby zdążyć na pociąg.", fullEn:"I left earlier to make the train." },
            { type:"choose", prompt:"Chcę, żebyś ___ prawdę.", promptEn:"I want you to know the truth. (to a man)",
              options:["znał","znać","znasz"], answer:"znał",
              explain:"After żebyś → past form agreeing with gender: znał (to a woman: znała). Truth pairs with znać, not wiedzieć.", full:"Chcę, żebyś znał prawdę.", fullEn:"I want you to know the truth." },
            { type:"choose", prompt:"Wolę, ___ zostali w domu.", promptEn:"I prefer that we stay home.",
              options:["żebyśmy","żebym","żeby"], answer:"żebyśmy",
              explain:"woleć + żeby; 'we' → żebyśmy zostali.", full:"Wolę, żebyśmy zostali w domu.", fullEn:"I prefer that we stay home." }
          ]
        },
        {
          name: "Przeczenie (Negation)", emoji: "🚫", kind: "grammar", chip: "Grammar B1",
          desc: "Nigdy nic nikomu nie mówię - why Polish stacks its negatives",
          teach: [
            { front:"nie goes before the verb. Always.",
              sub:"One position, no exceptions, no contractions to memorise.",
              points:[
                "<b>Nie</b> mam czasu. <b>Nie</b> wiem. <b>Nie</b> lubię poniedziałków.",
                "It stays glued to the verb even in questions: Czy ty <b>nie widzisz</b>?",
                "Compare English's don't / doesn't / didn't / won't - Polish has one word for all of it."
              ],
              examples:[
                { pl:"Nie rozumiem tego pytania.", en:"I don't understand this question." },
                { pl:"Ona nie pracuje w piątki.", en:"She doesn't work on Fridays." }
              ] },

            { front:"Negatives stack - and they must",
              sub:"In English two negatives cancel. In Polish they team up, and skipping one is an error.",
              points:[
                "Nigdy <b>nie</b> palę - I never smoke. The nie is not optional.",
                "They pile up freely: <b>Nigdy nikomu nic nie</b> mówię - I never tell anyone anything. Four negatives, one meaning.",
                "The trap runs in reverse for English speakers: <i>Nigdy palę</i> (missing nie) sounds as wrong to Poles as 'I never don't smoke' does to you."
              ],
              examples:[
                { pl:"Nikt nic nie powiedział.", en:"Nobody said anything." },
                { pl:"Nigdy nigdzie nie wychodzę wieczorem.", en:"I never go out anywhere in the evening." }
              ] },

            { front:"The ni- family",
              sub:"The negative words all start with ni- - and they decline through the cases like everything else.",
              table:[
                { g:"nikt → nikogo, nikomu", e:"nobody", ex:"Nie znam tu nikogo." },
                { g:"nic → niczego, niczym", e:"nothing", ex:"Nic nie widzę." },
                { g:"nigdy", e:"never", ex:"Nigdy tam nie byłem." },
                { g:"nigdzie", e:"nowhere", ex:"Nigdzie nie mogę znaleźć kluczy." },
                { g:"żaden / żadna / żadne", e:"no / none", ex:"Nie mam żadnych pytań." }
              ],
              note:"<b>Nikogo nie było w domu</b> - nobody was home. After nie było, the person goes to the Genitive: the genitive-of-negation you met in Dopełniacz, working overtime." },

            { front:"Negation changes the case",
              sub:"The Dopełniacz reminder: a negated verb pushes its object from Accusative into Genitive.",
              points:[
                "Mam czas → Nie mam <b>czasu</b>. Lubię kawę → Nie lubię <b>kawy</b>.",
                "There is / there isn't: Jest mleko → <b>Nie ma mleka</b>.",
                "This only touches direct objects. Other cases stay put: Nie ufam <b>mu</b> (still Dative)."
              ],
              examples:[
                { pl:"Nie mam dzisiaj czasu.", en:"I don't have time today." },
                { pl:"W lodówce nie ma mleka.", en:"There's no milk in the fridge." }
              ] },

            { front:"ani... ani, jeszcze nie, już nie",
              sub:"Three finishing touches that make your negatives sound native.",
              table:[
                { g:"neither... nor", e:"ani... ani", ex:"Nie lubię ani kawy, ani herbaty." },
                { g:"not yet", e:"jeszcze nie", ex:"Jeszcze nie jadłem." },
                { g:"not anymore", e:"już nie", ex:"Już tam nie pracuję." },
                { g:"not at all", e:"w ogóle nie", ex:"W ogóle nie rozumiem." },
                { g:"almost never", e:"prawie nigdy", ex:"Prawie nigdy nie choruję." }
              ],
              note:"<b>jeszcze nie</b> vs <b>już nie</b> is the pair worth drilling: jeszcze nie = hasn't happened yet; już nie = happened, but stopped. <i>Jeszcze nie jem</i> (I'm not eating yet) vs <i>Już nie jem</i> (I've stopped eating)." }
          ],
          drills: [
            { type:"choose", prompt:"Nigdy ___ palę.", promptEn:"I never smoke.",
              options:["nie","-","już"], answer:"nie",
              explain:"nigdy demands its nie - dropping it is the classic English-speaker error.", full:"Nigdy nie palę.", fullEn:"I never smoke." },
            { type:"choose", prompt:"Nikt nic ___ powiedział.", promptEn:"Nobody said anything.",
              options:["nie","ani","już"], answer:"nie",
              explain:"Stack them all: nikt + nic + nie. Every negative word joins in.", full:"Nikt nic nie powiedział.", fullEn:"Nobody said anything." },
            { type:"choose", prompt:"Nie znam tu ___.", promptEn:"I don't know anyone here.",
              options:["nikogo","nikt","nikomu"], answer:"nikogo",
              explain:"Negated znać takes the Genitive - nikt becomes nikogo.", full:"Nie znam tu nikogo.", fullEn:"I don't know anyone here." },
            { type:"choose", prompt:"Nie mam ___.", promptEn:"I don't have time.",
              options:["czasu","czas","czasem"], answer:"czasu",
              explain:"Negation pushes the object to Genitive: czas → czasu.", full:"Nie mam czasu.", fullEn:"I don't have time." },
            { type:"choose", prompt:"W lodówce nie ma ___.", promptEn:"There's no milk in the fridge.",
              options:["mleka","mleko","mlekiem"], answer:"mleka",
              explain:"nie ma + Genitive: mleka.", full:"W lodówce nie ma mleka.", fullEn:"There's no milk in the fridge." },
            { type:"choose", prompt:"___ nie było w domu.", promptEn:"Nobody was home.",
              options:["Nikogo","Nikt","Nikomu"], answer:"Nikogo",
              explain:"nie było takes Genitive - nikt becomes nikogo.", full:"Nikogo nie było w domu.", fullEn:"Nobody was home." },
            { type:"choose", prompt:"Nie mam ___ pytań.", promptEn:"I have no questions.",
              options:["żadnych","żaden","żadne"], answer:"żadnych",
              explain:"żaden agrees with the Genitive plural pytań → żadnych.", full:"Nie mam żadnych pytań.", fullEn:"I have no questions." },
            { type:"choose", prompt:"Nie lubię ___ kawy, ani herbaty.", promptEn:"I like neither coffee nor tea.",
              options:["ani","albo","czy"], answer:"ani",
              explain:"Neither... nor = ani... ani, both halves.", full:"Nie lubię ani kawy, ani herbaty.", fullEn:"I like neither coffee nor tea." },
            { type:"choose", prompt:"Jadłeś już obiad? - ___ nie.", promptEn:"Have you eaten lunch? - Not yet.",
              options:["Jeszcze","Już","Nigdy"], answer:"Jeszcze",
              explain:"Hasn't happened yet → jeszcze nie. Już nie would mean you've stopped eating lunches altogether.", full:"Jadłeś już obiad? - Jeszcze nie.", fullEn:"Have you eaten lunch? - Not yet." },
            { type:"choose", prompt:"___ tam nie pracuję.", promptEn:"I don't work there anymore.",
              options:["Już","Jeszcze","Ani"], answer:"Już",
              explain:"Happened, then stopped → już nie.", full:"Już tam nie pracuję.", fullEn:"I don't work there anymore." },
            { type:"choose", prompt:"Nigdzie nie mogę znaleźć ___.", promptEn:"I can't find my keys anywhere.",
              options:["kluczy","klucze","kluczami"], answer:"kluczy",
              explain:"Negated znaleźć → Genitive: kluczy. Plus nigdzie stacking with nie.", full:"Nigdzie nie mogę znaleźć kluczy.", fullEn:"I can't find my keys anywhere." },
            { type:"choose", prompt:"W ogóle ___ rozumiem.", promptEn:"I don't understand at all.",
              options:["nie","już","ani"], answer:"nie",
              explain:"w ogóle nie = not at all - the nie still shows up.", full:"W ogóle nie rozumiem.", fullEn:"I don't understand at all." }
          ]
        }
      ]
    }
  );

})();
