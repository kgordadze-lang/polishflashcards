/* Po polsku - lesson data: Scenarios
   Registered onto window.PP_LEVELS by index.html (loaded in order).
   Safe to edit this file alone; a syntax error here shows a load
   message instead of breaking the app engine. */
(function(){
  window.PP_LEVELS = window.PP_LEVELS || [];
  window.PP_LEVELS.push(
  {
      level: "Scenarios",
      blurb: "Real conversations",
      topics: [
        {
          name: "W aptece", emoji: "\uD83D\uDC8A", kind: "convo",
          desc: "Describe a symptom, choose a remedy, and pay at the counter",
          role: "Farmaceutka",
          setting: "You're not feeling your best, so you step into a pharmacy. The pharmacist looks up from the counter.",
          goal: "Explain what you need, choose a remedy, and pay. Every reply is a valid path.",
          start: "greet",
          scenes: {
            greet: {
              npc:"Dzień dobry! W czym mogę pomóc?", npcEn:"Good morning! How can I help?",
              options:[
                { pl:"Poproszę coś na ból głowy.", en:"Something for a headache, please.",
                  note:"'na' + accusative names what a remedy is for: na ból głowy, na katar, na gardło.", goto:"headache" },
                { pl:"Szukam czegoś na katar.", en:"I'm looking for something for a runny nose.",
                  note:"'szukać' + genitive: szukam czegoś, szukam apteki.", goto:"cold" }
              ]
            },
            headache: {
              npc:"Tabletki czy syrop?", npcEn:"Tablets or syrup?",
              options:[
                { pl:"Tabletki, proszę.", en:"Tablets, please.", goto:"strength" },
                { pl:"A co pani poleca?", en:"And what do you recommend?",
                  note:"'polecać' = to recommend - a neat way to hand the choice back.", goto:"recommendH" }
              ]
            },
            recommendH: {
              npc:"Polecam tabletki - działają szybciej.", npcEn:"I recommend tablets - they work faster.",
              options:[
                { pl:"Dobrze, poproszę tabletki.", en:"Alright, tablets please.", goto:"strength" }
              ]
            },
            strength: {
              npc:"Mam paracetamol i ibuprofen. Co pan woli?", npcEn:"I have paracetamol and ibuprofen. Which do you prefer?",
              options:[
                { pl:"Paracetamol poproszę.", en:"Paracetamol, please.",
                  note:"'poproszę' is your polite go-to for asking for anything.", goto:"handover" },
                { pl:"Wszystko jedno.", en:"Either one's fine.",
                  note:"'wszystko jedno' says you don't mind which.", goto:"handover" }
              ]
            },
            cold: {
              npc:"Krople do nosa czy tabletki?", npcEn:"Nose drops or tablets?",
              options:[
                { pl:"Krople, proszę.", en:"Drops, please.", goto:"coldExtra" },
                { pl:"A co pani poleca?", en:"And what do you recommend?",
                  note:"'polecać' = to recommend.", goto:"recommendC" }
              ]
            },
            recommendC: {
              npc:"Polecam krople, są bardzo skuteczne.", npcEn:"I recommend the drops, they're very effective.",
              options:[
                { pl:"Świetnie, poproszę krople.", en:"Great, the drops please.", goto:"coldExtra" }
              ]
            },
            coldExtra: {
              npc:"Mam też syrop na gardło. Coś jeszcze?", npcEn:"I also have throat syrup. Anything else?",
              options:[
                { pl:"Nie, dziękuję. To wszystko.", en:"No thanks, that's all.", goto:"handover" },
                { pl:"Tak, poproszę też syrop.", en:"Yes, the syrup too, please.",
                  note:"'też' = too / also - handy for adding to an order.", goto:"handover" }
              ]
            },
            handover: {
              npc:"Proszę bardzo. Coś jeszcze?", npcEn:"Here you go. Anything else?",
              options:[
                { pl:"Jak często mam to stosować?", en:"How often should I use it?",
                  note:"'mam' + infinitive = 'should I / am I to': mam stosować, mam czekać, mam zapłacić.", goto:"dose" },
                { pl:"Nie, ile płacę?", en:"No, how much do I pay?", goto:"price" }
              ]
            },
            dose: {
              npc:"Dwa razy dziennie, po jedzeniu.", npcEn:"Twice a day, after food.",
              options:[
                { pl:"Rozumiem, dziękuję.", en:"I understand, thank you.", goto:"price" },
                { pl:"A ile to kosztuje?", en:"And how much is it?",
                  note:"'Ile to kosztuje?' is your everyday how-much question.", goto:"price" }
              ]
            },
            price: {
              npc:"To będzie dwadzieścia złotych.", npcEn:"That'll be twenty zloty.",
              options:[
                { pl:"Proszę, karta.", en:"Here you go, card.",
                  note:"Card and phone payment work almost everywhere in Poland.", goto:"end" },
                { pl:"Płacę gotówką.", en:"I'll pay cash.",
                  note:"'gotówka' = cash; 'gotówką' = in cash.", goto:"end" }
              ]
            },
            end: {
              npc:"Dziękuję. Życzę zdrowia i miłego dnia!", npcEn:"Thank you. Wishing you good health and a nice day!",
              end:true
            }
          }
        },
        {
          name: "U lekarza", emoji: "\uD83E\uDE7A", kind: "convo",
          desc: "Tell the doctor what's wrong and get a prescription",
          role: "Lekarka",
          setting: "It's your turn at the clinic. The doctor calls you into the office.",
          goal: "Describe your symptoms, get a prescription or a sick note, and find out what to do next. Every reply is a valid path.",
          start: "greet",
          scenes: {
            greet: {
              npc:"Dzień dobry. Prosz\u0119 usi\u0105\u015b\u0107. Co si\u0119 dzieje?", npcEn:"Good morning. Please have a seat. What's going on?",
              options:[
                { pl:"Od kilku dni boli mnie gard\u0142o.", en:"My throat has hurt for a few days.",
                  note:"'boli mnie...' = ... hurts (me): boli mnie gard\u0142o, boli mnie g\u0142owa, boli mnie brzuch.", goto:"throat" },
                { pl:"Mam kaszel i gor\u0105czk\u0119.", en:"I have a cough and a fever.",
                  note:"'mam' + symptom: mam kaszel, mam katar, mam gor\u0105czk\u0119.", goto:"fever" }
              ]
            },
            throat: {
              npc:"Prosz\u0119 otworzy\u0107 usta... Gard\u0142o jest zaczerwienione. Czy jest gor\u0105czka?", npcEn:"Please open your mouth... Your throat is red. Is there a fever?",
              options:[
                { pl:"Tak, mam troch\u0119 gor\u0105czki.", en:"Yes, I have a slight fever.",
                  note:"'troch\u0119' + genitive: troch\u0119 gor\u0105czki, troch\u0119 czasu, troch\u0119 wody.", goto:"diagnosis" },
                { pl:"Nie, gor\u0105czki nie ma.", en:"No, there's no fever.",
                  note:"'nie ma' + genitive for 'there isn't': nie ma gor\u0105czki, nie ma czasu.", goto:"diagnosis" }
              ]
            },
            fever: {
              npc:"Od jak dawna to trwa?", npcEn:"How long has this been going on?",
              options:[
                { pl:"Od trzech dni.", en:"For three days.",
                  note:"'od' + genitive for 'since / for': od trzech dni, od poniedzia\u0142ku, od rana.", goto:"diagnosis" },
                { pl:"Od tygodnia.", en:"For a week.",
                  note:"'tydzie\u0144' becomes 'tygodnia' in the genitive after 'od'.", goto:"diagnosis" }
              ]
            },
            diagnosis: {
              npc:"To wygl\u0105da na infekcj\u0119. Przepisz\u0119 lekarstwo.", npcEn:"It looks like an infection. I'll prescribe some medicine.",
              options:[
                { pl:"Czy potrzebuj\u0119 recepty?", en:"Do I need a prescription?",
                  note:"'potrzebowa\u0107' + genitive: potrzebuj\u0119 recepty, potrzebuj\u0119 pomocy.", goto:"recepta" },
                { pl:"Czy dostan\u0119 zwolnienie z pracy?", en:"Will I get a sick note for work?",
                  note:"'zwolnienie (lekarskie)' = a doctor's sick note.", goto:"zwolnienie" }
              ]
            },
            recepta: {
              npc:"Tak, oto recepta. Prosz\u0119 wykupi\u0107 lekarstwo w aptece.", npcEn:"Yes, here's the prescription. Please pick up the medicine at the pharmacy.",
              options:[
                { pl:"Dzi\u0119kuj\u0119. A czy mog\u0119 te\u017c dosta\u0107 zwolnienie?", en:"Thank you. Can I also get a sick note?", goto:"zwolnienie" },
                { pl:"Dzi\u0119kuj\u0119. Jak cz\u0119sto mam bra\u0107 lekarstwo?", en:"Thank you. How often should I take the medicine?",
                  note:"'mam bra\u0107' = should I take; 'mam' + infinitive gives you instructions.", goto:"dosage" }
              ]
            },
            zwolnienie: {
              npc:"Oczywi\u015bcie. Wystawi\u0119 zwolnienie na pi\u0119\u0107 dni.", npcEn:"Of course. I'll issue a sick note for five days.",
              options:[
                { pl:"Bardzo dzi\u0119kuj\u0119. Jak cz\u0119sto mam bra\u0107 lekarstwo?", en:"Thank you very much. How often should I take the medicine?", goto:"dosage" },
                { pl:"\u015awietnie, dzi\u0119kuj\u0119 za pomoc.", en:"Great, thank you for your help.",
                  note:"'dzi\u0119kuj\u0119 za' + accusative: dzi\u0119kuj\u0119 za pomoc, za informacj\u0119.", goto:"farewell" }
              ]
            },
            dosage: {
              npc:"Dwa razy dziennie, rano i wieczorem. Prosz\u0119 du\u017co odpoczywa\u0107.", npcEn:"Twice a day, morning and evening. Please rest a lot.",
              options:[
                { pl:"Dobrze, b\u0119d\u0119 odpoczywa\u0107. Dzi\u0119kuj\u0119.", en:"Alright, I'll rest. Thank you.", goto:"farewell" },
                { pl:"Rozumiem. Czy mam wr\u00f3ci\u0107 na kontrol\u0119?", en:"I understand. Should I come back for a check-up?",
                  note:"'na kontrol\u0119' = for a check-up (accusative after 'na').", goto:"followup" }
              ]
            },
            followup: {
              npc:"Je\u015bli objawy nie min\u0105 w tydzie\u0144, prosz\u0119 wr\u00f3ci\u0107.", npcEn:"If the symptoms don't go away within a week, please come back.",
              options:[
                { pl:"Dobrze, dzi\u0119kuj\u0119 bardzo.", en:"Alright, thank you very much.", goto:"farewell" }
              ]
            },
            farewell: {
              npc:"Prosz\u0119 dba\u0107 o siebie. Do widzenia!", npcEn:"Take care of yourself. Goodbye!",
              end:true
            }
          }
        }
      ]
    }
  );
})();
