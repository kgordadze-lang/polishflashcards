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
          desc: "Describe a symptom, choose a remedy, ask how to take it, and pay",
          role: "Farmaceutka",
          setting: "You're not feeling your best, so you step into a pharmacy. The pharmacist looks up from the counter.",
          goal: "Explain what you need, choose a remedy, ask how to take it, and pay. Every reply is a valid path.",
          recap: [
            "<b>boli mnie</b> + body part - boli mnie głowa / gardło",
            "<b>na</b> + accusative for remedies - coś na ból głowy",
            "<b>mam / mogę</b> + infinitive - jak mam to stosować?",
            "instrumental for paying - płacę kartą / gotówką"
          ],
          start: "greet",
          scenes: {
            greet: {
              npc:"Dzień dobry! W czym mogę pomóc?", npcEn:"Good morning! How can I help?",
              tip:"<b>Ściąga:</b> to say what hurts, use <b>boli mnie</b> + the body part - <i>boli mnie głowa, gardło, brzuch</i>.",
              options:[
                { pl:"Poproszę coś na ból głowy.", en:"Something for a headache, please.",
                  note:"'na' + accusative names what a remedy is for: na ból głowy, na katar, na gardło.", goto:"headache" },
                { pl:"Boli mnie głowa od rana.", en:"I've had a headache since this morning.",
                  note:"'boli mnie' + the body part as subject: boli mnie głowa (my head hurts).", goto:"headache" },
                { pl:"Mam katar i trochę kaszlu.", en:"I have a runny nose and a bit of a cough.",
                  note:"'mam' + accusative: mam katar, mam kaszel, mam gorączkę.", goto:"cold" },
                { pl:"Boli mnie gardło.", en:"My throat hurts.",
                  note:"Same 'boli mnie' pattern: boli mnie gardło.", goto:"throat" },
                { pl:"Nie mogę spać od kilku dni.", en:"I haven't been able to sleep for a few days.",
                  note:"Modal 'nie mogę' + infinitive: nie mogę spać.", goto:"sleep" }
              ]
            },
            headache: {
              npc:"Rozumiem. Tabletki czy syrop?", npcEn:"I see. Tablets or syrup?",
              options:[
                { pl:"Tabletki, proszę.", en:"Tablets, please.", goto:"strength" },
                { pl:"Wolę syrop.", en:"I prefer syrup.",
                  note:"'woleć' = to prefer: wolę, wolisz, woli.", goto:"strength" },
                { pl:"A co pani poleca?", en:"And what do you recommend?",
                  note:"'polecać' = to recommend - hands the choice back politely.", goto:"recommendH" }
              ]
            },
            recommendH: {
              npc:"Polecam tabletki - działają szybciej.", npcEn:"I recommend tablets - they work faster.",
              options:[
                { pl:"Dobrze, poproszę tabletki.", en:"Alright, tablets please.", goto:"strength" }
              ]
            },
            strength: {
              npc:"Mam paracetamol i ibuprofen. Co pani woli?", npcEn:"I have paracetamol and ibuprofen. Which do you prefer?",
              options:[
                { pl:"Paracetamol poproszę.", en:"Paracetamol, please.",
                  note:"'poproszę' is your polite go-to for asking for anything.", goto:"handover" },
                { pl:"Ibuprofen, jeśli można.", en:"Ibuprofen, if that's OK.",
                  note:"'jeśli można' = if possible - softens a request.", goto:"handover" },
                { pl:"Wszystko jedno.", en:"Either one's fine.",
                  note:"'wszystko jedno' says you don't mind which.", goto:"handover" }
              ]
            },
            cold: {
              npc:"Krople do nosa czy tabletki?", npcEn:"Nose drops or tablets?",
              options:[
                { pl:"Krople, proszę.", en:"Drops, please.", goto:"coldExtra" },
                { pl:"Wolę tabletki.", en:"I prefer tablets.",
                  note:"'woleć' = to prefer.", goto:"coldExtra" },
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
            throat: {
              npc:"Na gardło mam pastylki do ssania i syrop. Co pani woli?", npcEn:"For the throat I have lozenges and syrup. Which do you prefer?",
              options:[
                { pl:"Poproszę pastylki.", en:"Lozenges, please.", goto:"handover" },
                { pl:"Wolę syrop.", en:"I prefer syrup.", goto:"handover" },
                { pl:"Czy to jest bez recepty?", en:"Is it available without a prescription?",
                  note:"'bez recepty' = over the counter; 'na receptę' = prescription-only.", goto:"recepta" }
              ]
            },
            sleep: {
              npc:"Na sen mogę polecić melatoninę. Jest bez recepty.", npcEn:"For sleep I can recommend melatonin. It's over the counter.",
              options:[
                { pl:"Dobrze, poproszę.", en:"Alright, I'll take it.", goto:"handover" },
                { pl:"Czy mogę ją brać codziennie?", en:"Can I take it every day?",
                  note:"Modal 'mogę' + infinitive: czy mogę brać?", goto:"dose" }
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
              tip:"<b>Ściąga:</b> <b>mam</b> + infinitive asks about instructions - <i>jak mam to stosować?</i> (how am I to use it?). <b>mogę</b> + infinitive asks permission.",
              options:[
                { pl:"Jak często mam to stosować?", en:"How often should I use it?",
                  note:"'mam' + infinitive = 'am I to / should I': mam stosować, mam czekać.", goto:"dose" },
                { pl:"Czy mogę to brać na czczo?", en:"Can I take it on an empty stomach?",
                  note:"Modal 'mogę' + infinitive; 'na czczo' = on an empty stomach.", goto:"dose" },
                { pl:"Czy potrzebuję na to recepty?", en:"Do I need a prescription for it?",
                  note:"'potrzebować' + genitive: potrzebuję recepty.", goto:"recepta" },
                { pl:"Nie, dziękuję. Ile płacę?", en:"No thanks. How much do I pay?", goto:"price" }
              ]
            },
            dose: {
              npc:"Dwa razy dziennie, po jedzeniu.", npcEn:"Twice a day, after food.",
              options:[
                { pl:"Rozumiem, dziękuję.", en:"I understand, thank you.", goto:"price" },
                { pl:"A jak długo mam to brać?", en:"And how long should I take it?",
                  note:"'jak długo' = how long; 'mam brać' = should I take.", goto:"price" },
                { pl:"A ile to kosztuje?", en:"And how much is it?",
                  note:"'Ile to kosztuje?' is your everyday how-much question.", goto:"price" }
              ]
            },
            recepta: {
              npc:"Nie, to jest bez recepty.", npcEn:"No, it's available without a prescription.",
              options:[
                { pl:"Świetnie, to poproszę.", en:"Great, I'll take it then.", goto:"price" },
                { pl:"Dziękuję za informację.", en:"Thanks for the information.", goto:"price" }
              ]
            },
            price: {
              npc:"To będzie dwadzieścia złotych.", npcEn:"That'll be twenty zloty.",
              tip:"<b>Ściąga:</b> how you pay takes the instrumental - <i>kartą</i> (by card), <i>gotówką</i> (in cash).",
              options:[
                { pl:"Płacę kartą.", en:"I'll pay by card.",
                  note:"Instrumental for means of payment: kartą (by card).", goto:"end" },
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
          recap: [
            "<b>boli mnie / bolą mnie</b> + body part - boli mnie gardło, bolą mnie plecy",
            "<b>od</b> + genitive for duration - od trzech dni, od tygodnia",
            "<b>muszę / mam</b> + infinitive - czy muszę brać antybiotyk? jak mam to brać?",
            "<b>potrzebować</b> + genitive - potrzebuję recepty"
          ],
          start: "greet",
          scenes: {
            greet: {
              npc:"Dzień dobry. Proszę usiąść. Co się dzieje?", npcEn:"Good morning. Please have a seat. What's going on?",
              tip:"<b>Ściąga:</b> say what hurts with <b>boli mnie</b> + body part (boli mnie gardło); for a plural body part use <b>bolą mnie</b> (bolą mnie plecy).",
              options:[
                { pl:"Od kilku dni boli mnie gardło.", en:"My throat has hurt for a few days.",
                  note:"'boli mnie' + body part: boli mnie gardło, głowa, brzuch.", goto:"throat" },
                { pl:"Mam kaszel i gorączkę.", en:"I have a cough and a fever.",
                  note:"'mam' + symptom: mam kaszel, mam katar, mam gorączkę.", goto:"fever" },
                { pl:"Mam katar i boli mnie głowa.", en:"I have a runny nose and a headache.",
                  note:"Two at once: mam katar + boli mnie głowa.", goto:"fever" },
                { pl:"Boli mnie brzuch i mam mdłości.", en:"My stomach hurts and I feel nauseous.",
                  note:"'mdłości' = nausea (always plural).", goto:"stomach" },
                { pl:"Czuję się słabo i nie mam apetytu.", en:"I feel weak and have no appetite.",
                  note:"'nie mam' + genitive: nie mam apetytu, nie mam siły.", goto:"fever" }
              ]
            },
            throat: {
              npc:"Proszę otworzyć usta... Gardło jest zaczerwienione. Czy jest gorączka?", npcEn:"Please open your mouth... Your throat is red. Is there a fever?",
              options:[
                { pl:"Tak, mam trochę gorączki.", en:"Yes, I have a slight fever.",
                  note:"'trochę' + genitive: trochę gorączki, trochę czasu.", goto:"diagnosis" },
                { pl:"Nie, gorączki nie ma.", en:"No, there's no fever.",
                  note:"'nie ma' + genitive: nie ma gorączki, nie ma czasu.", goto:"diagnosis" },
                { pl:"Chyba tak, jest mi gorąco.", en:"I think so, I feel hot.",
                  note:"'jest mi gorąco / zimno' = I feel hot / cold (dative construction).", goto:"diagnosis" }
              ]
            },
            fever: {
              npc:"Od jak dawna to trwa?", npcEn:"How long has this been going on?",
              options:[
                { pl:"Od trzech dni.", en:"For three days.",
                  note:"'od' + genitive for 'since / for': od trzech dni, od rana.", goto:"diagnosis" },
                { pl:"Od tygodnia.", en:"For a week.",
                  note:"'tydzień' becomes 'tygodnia' in the genitive after 'od'.", goto:"diagnosis" },
                { pl:"Zaczęło się wczoraj.", en:"It started yesterday.",
                  note:"'zaczęło się' = it started (reflexive past, neuter).", goto:"diagnosis" }
              ]
            },
            stomach: {
              npc:"Rozumiem. Czy to zaczęło się nagle?", npcEn:"I see. Did it start suddenly?",
              options:[
                { pl:"Tak, nagle. Chyba coś mi zaszkodziło.", en:"Yes, suddenly. I think something disagreed with me.",
                  note:"'coś mi zaszkodziło' = something made me ill (dative 'mi').", goto:"diagnosis" },
                { pl:"Nie, boli mnie już od kilku dni.", en:"No, it's been hurting for a few days now.",
                  note:"'od kilku dni' = for a few days (od + genitive).", goto:"diagnosis" }
              ]
            },
            diagnosis: {
              npc:"To wygląda na infekcję. Przepiszę lekarstwo.", npcEn:"It looks like an infection. I'll prescribe some medicine.",
              tip:"<b>Ściąga:</b> <b>muszę / mam</b> + infinitive asks about obligation - <i>czy muszę brać antybiotyk?</i>, <i>jak mam to brać?</i>",
              options:[
                { pl:"Czy potrzebuję recepty?", en:"Do I need a prescription?",
                  note:"'potrzebować' + genitive: potrzebuję recepty, pomocy.", goto:"recepta" },
                { pl:"Czy muszę brać antybiotyk?", en:"Do I have to take an antibiotic?",
                  note:"Modal 'musieć' + infinitive: czy muszę brać?", goto:"recepta" },
                { pl:"Czy dostanę zwolnienie z pracy?", en:"Will I get a sick note for work?",
                  note:"'zwolnienie (lekarskie)' = a doctor's sick note.", goto:"zwolnienie" }
              ]
            },
            recepta: {
              npc:"Tak, oto recepta. Proszę wykupić lekarstwo w aptece.", npcEn:"Yes, here's the prescription. Please pick up the medicine at the pharmacy.",
              options:[
                { pl:"Dziękuję. A czy mogę też dostać zwolnienie?", en:"Thank you. Can I also get a sick note?", goto:"zwolnienie" },
                { pl:"Dziękuję. Jak często mam brać lekarstwo?", en:"Thank you. How often should I take the medicine?",
                  note:"'mam brać' = should I take; 'mam' + infinitive gives instructions.", goto:"dosage" }
              ]
            },
            zwolnienie: {
              npc:"Oczywiście. Wystawię zwolnienie na pięć dni.", npcEn:"Of course. I'll issue a sick note for five days.",
              options:[
                { pl:"Bardzo dziękuję. Jak często mam brać lekarstwo?", en:"Thank you very much. How often should I take the medicine?", goto:"dosage" },
                { pl:"Świetnie, dziękuję za pomoc.", en:"Great, thank you for your help.",
                  note:"'dziękuję za' + accusative: za pomoc, za informację.", goto:"farewell" }
              ]
            },
            dosage: {
              npc:"Dwa razy dziennie, rano i wieczorem. Proszę dużo odpoczywać.", npcEn:"Twice a day, morning and evening. Please rest a lot.",
              options:[
                { pl:"Dobrze, będę odpoczywać. Dziękuję.", en:"Alright, I'll rest. Thank you.",
                  note:"'będę' + infinitive = future: będę odpoczywać (I'll be resting).", goto:"farewell" },
                { pl:"Rozumiem. Czy mam wrócić na kontrolę?", en:"I understand. Should I come back for a check-up?",
                  note:"'na kontrolę' = for a check-up (accusative after 'na').", goto:"followup" },
                { pl:"Czy mogę brać to z jedzeniem?", en:"Can I take it with food?",
                  note:"Modal 'mogę' + infinitive: czy mogę brać?", goto:"followup" }
              ]
            },
            followup: {
              npc:"Jeśli objawy nie miną w ciągu tygodnia, proszę wrócić.", npcEn:"If the symptoms don't go away within a week, please come back.",
              options:[
                { pl:"Dobrze, dziękuję bardzo.", en:"Alright, thank you very much.", goto:"farewell" }
              ]
            },
            farewell: {
              npc:"Proszę dbać o siebie. Do widzenia!", npcEn:"Take care of yourself. Goodbye!",
              end:true
            }
          }
        },
        {
          name: "Sklep i usługi", emoji: "\uD83D\uDCB0", kind: "convo",
          desc: "Paying, ordering, and quick everyday errands",
          role: "Sprzedawcy i kasjerki",
          setting: "You're running errands around town - a shop, a café, a parcel pickup. Quick, everyday exchanges keep coming your way.",
          goal: "Answer naturally and quickly. Every reply is a valid path.",
          recap: [
            "instrumental for paying - <b>kartą, gotówką</b>",
            "<b>poproszę</b> + accusative to order - poproszę kawę, herbatę",
            "<b>czy mogę prosić o...</b> = a polite 'could I have...'",
            "na miejscu / na wynos = for here / to go"
          ],
          start: "s1",
          scenes: {
            s1: {
              npc:"Karta czy gotówka?", npcEn:"(At the till) Card or cash?",
              tip:"<b>Ściąga:</b> how you pay is instrumental - <i>kartą</i> (by card), <i>gotówką</i> (in cash).",
              options:[
                { pl:"Kartą, proszę.", en:"By card, please.",
                  note:"'Kartą' is Instrumental - the means of payment always takes this case.", goto:"s2" },
                { pl:"Gotówką, proszę.", en:"In cash, please.",
                  note:"Same Instrumental pattern: 'gotówka' \u2192 'gotówką'.", goto:"s2" }
              ]
            },
            s2: {
              npc:"Czy ma pan/pani aplikację?", npcEn:"(Supermarket loyalty scheme) Do you have the app?",
              options:[
                { pl:"Nie mam.", en:"I don't have it.",
                  note:"Short and direct - completely natural, no need to explain further.", goto:"s3" },
                { pl:"Tak, mam.", en:"Yes, I do.",
                  note:"If you say yes, they'll usually ask you to scan a code at the register.", goto:"s3" }
              ]
            },
            s3: {
              npc:"Potrzebuje pan/pani paragonu?", npcEn:"(Cashier) Do you need a receipt?",
              options:[
                { pl:"Nie, dziękuję.", en:"No, thanks.", goto:"s4" },
                { pl:"Tak, poproszę.", en:"Yes, please.", goto:"s4" }
              ]
            },
            s4: {
              npc:"Czy mogę być dłużna grosika?", npcEn:"(Cashier, short of small change) Would you mind if I owe you a few grosze?",
              options:[
                { pl:"Jasne, nie ma problemu.", en:"Sure, no problem.",
                  note:"A very Polish small-talk moment - cashiers sometimes round to the nearest few groszy when they're out of coins.", goto:"s5" }
              ]
            },
            s5: {
              npc:"Torbę doliczyć?", npcEn:"(Cashier) Should I add a bag?",
              options:[
                { pl:"Nie, mam swoją.", en:"No, I have my own.",
                  note:"Bags cost extra in Polish shops - bringing your own is the local habit.", goto:"s6" },
                { pl:"Tak, poproszę.", en:"Yes, please.", goto:"s6" }
              ]
            },
            s6: {
              npc:"Odbiera pan/pani paczkę?", npcEn:"(At a parcel locker or pickup point) Are you picking up a package?",
              options:[
                { pl:"Tak, mam kod odbioru.", en:"Yes, I have the pickup code.",
                  note:"'Kod odbioru' - the pickup code sent by SMS or app, standard for Paczkomat/InPost pickups.", goto:"s7" }
              ]
            },
            s7: {
              npc:"Na miejscu czy na wynos?", npcEn:"(Café) For here or to go?",
              options:[
                { pl:"Na wynos, proszę.", en:"To go, please.", goto:"s8" },
                { pl:"Na miejscu, proszę.", en:"For here, please.", goto:"s8" }
              ]
            },
            s8: {
              npc:"Co podać?", npcEn:"(Barista) What can I get you?",
              tip:"<b>Ściąga:</b> ordering uses <b>poproszę</b> + accusative - <i>poproszę kawę, herbatę, wodę</i> (kawa → kawę).",
              options:[
                { pl:"Poproszę duże cappuccino.", en:"A large cappuccino, please.",
                  note:"'Poproszę' + accusative is the standard ordering formula.", goto:"s9" },
                { pl:"Poproszę kawę z mlekiem.", en:"A coffee with milk, please.",
                  note:"'kawa' \u2192 'kawę' in the accusative; 'z mlekiem' = with milk (instrumental).", goto:"s9" },
                { pl:"Poproszę herbatę i sernik.", en:"A tea and a cheesecake, please.",
                  note:"'herbata' \u2192 'herbatę'; 'sernik' = cheesecake.", goto:"s9" },
                { pl:"Czy mogę prosić o sok pomarańczowy?", en:"Could I have an orange juice?",
                  note:"'czy mogę prosić o' + accusative = a softer 'could I have'.", goto:"s9" },
                { pl:"Poproszę to samo co zwykle.", en:"The usual, please.",
                  note:"'to samo co zwykle' = the same as usual.", goto:"s9" }
              ]
            },
            s9: {
              npc:"Czy to wszystko?", npcEn:"(Cashier) Is that all?",
              options:[
                { pl:"Tak, to wszystko.", en:"Yes, that's all.", goto:"s10" },
                { pl:"Jeszcze jedno.", en:"One more thing.",
                  note:"Handy if you remember something else you need.", goto:"s10" }
              ]
            },
            s10: {
              npc:"Płacicie państwo razem czy osobno?", npcEn:"(Waiter, to a group) Are you paying together or separately?",
              options:[
                { pl:"Razem.", en:"Together.", goto:"end" },
                { pl:"Osobno.", en:"Separately.", goto:"end" }
              ]
            },
            end: {
              npc:"Dziękuję, miłego dnia!", npcEn:"Thank you, have a nice day!",
              end:true
            }
          }
        },
        {
          name: "Miasto i transport", emoji: "\uD83D\uDE8B", kind: "convo",
          desc: "Asking directions, catching transit, getting around",
          role: "Przechodnie i kierowcy",
          setting: "You're finding your way around the city - asking directions, catching transit, navigating everyday moments on the way.",
          goal: "Ask naturally, understand the answer, and respond the way a local would.",
          recap: [
            "<b>jak dojść do</b> + genitive (on foot) / <b>jak dojechać do</b> (by transit)",
            "verbs of motion: <b>iść</b> (on foot), <b>jechać</b> (by vehicle) - autobus jedzie",
            "<b>o której...?</b> = at what time; <b>za</b> + time = in (ten minutes)",
            "<b>czy można</b> + infinitive = is it allowed to...?"
          ],
          start: "s1",
          scenes: {
            s1: {
              npc:"(Chcesz zapytać, jak dojść do stacji metra.)", npcEn:"(You want to ask how to get to the metro station.)",
              tip:"<b>Ściąga:</b> ask the way with <b>jak dojść do</b> + genitive (on foot) or <b>jak dojechać do</b> (by transit) - do stacji, do centrum.",
              options:[
                { pl:"Przepraszam, jak dojść do stacji metra?", en:"Excuse me, how do I get to the metro station?",
                  note:"'Jak dojść do...' + genitive is the go-to formula for directions on foot.", goto:"s2" },
                { pl:"Przepraszam, gdzie jest najbliższa stacja metra?", en:"Excuse me, where's the nearest metro station?",
                  note:"'najbliższy' = nearest - najbliższa stacja, najbliższy przystanek.", goto:"s2" },
                { pl:"Jak najlepiej dojechać do centrum?", en:"What's the best way to get to the center?",
                  note:"'dojechać' (by vehicle) vs 'dojść' (on foot) - the iść/jechać split.", goto:"s2" }
              ]
            },
            s2: {
              npc:"Prosto i w lewo.", npcEn:"Straight ahead and then left.",
              options:[
                { pl:"Dziękuję bardzo!", en:"Thank you very much!", goto:"s3" },
                { pl:"Rozumiem, dziękuję.", en:"Got it, thank you.", goto:"s3" }
              ]
            },
            s3: {
              npc:"(Nie jesteś pewien, czy ten autobus jedzie do centrum.)", npcEn:"(You're not sure if this bus goes downtown.)",
              options:[
                { pl:"Czy ten autobus jedzie do centrum?", en:"Does this bus go to the center?",
                  note:"'jechać' (by vehicle): autobus jedzie, ja jadę, ty jedziesz.", goto:"s4" },
                { pl:"Przepraszam, dojadę tym autobusem do centrum?", en:"Excuse me, will this bus get me to the center?",
                  note:"'tym autobusem' = by this bus (instrumental for transport).", goto:"s4" }
              ]
            },
            s4: {
              npc:"Nie, w przeciwnym kierunku.", npcEn:"No, the opposite direction.",
              options:[
                { pl:"O, dziękuję za informację!", en:"Oh, thanks for letting me know!", goto:"s5" }
              ]
            },
            s5: {
              npc:"(Widzisz wolne miejsce obok kogoś w tramwaju.)", npcEn:"(You see a free seat next to someone on the tram.)",
              options:[
                { pl:"Czy to miejsce jest wolne?", en:"Is this seat taken?",
                  note:"Literally 'is this place free?' - always ask before sitting next to a stranger.", goto:"s6" },
                { pl:"Przepraszam, czy mogę usiąść?", en:"Excuse me, may I sit down?",
                  note:"Modal 'mogę' + infinitive: czy mogę usiąść?", goto:"s6" }
              ]
            },
            s6: {
              npc:"Tak, wolne.", npcEn:"Yes, it's free.",
              options:[
                { pl:"Dziękuję.", en:"Thank you.", goto:"s7" }
              ]
            },
            s7: {
              npc:"Wysiada pan/pani na następnym?", npcEn:"(A fellow passenger, trying to get past) Are you getting off at the next stop?",
              options:[
                { pl:"Tak, wysiadam.", en:"Yes, I'm getting off.",
                  note:"Lets them know you'll move out of the way.", goto:"s8" },
                { pl:"Nie, proszę przejść.", en:"No, go ahead.",
                  note:"Invites them to squeeze past you.", goto:"s8" }
              ]
            },
            s8: {
              npc:"(Szukasz automatu do biletów.)", npcEn:"(You're looking for a ticket machine.)",
              options:[
                { pl:"Przepraszam, gdzie jest biletomat?", en:"Excuse me, where is the ticket machine?", goto:"s9" },
                { pl:"Gdzie mogę kupić bilet?", en:"Where can I buy a ticket?",
                  note:"Modal 'mogę' + infinitive: gdzie mogę kupić?", goto:"s9" }
              ]
            },
            s9: {
              npc:"Tam, przy wejściu.", npcEn:"Over there, by the entrance.",
              options:[
                { pl:"Dzięki!", en:"Thanks!",
                  note:"'Dzięki' is the casual, everyday version of 'dziękuję'.", goto:"s10" }
              ]
            },
            s10: {
              npc:"(Chcesz wiedzieć, kiedy odjeżdża twój pociąg.)", npcEn:"(You want to know when your train leaves.)",
              tip:"<b>Ściąga:</b> ask clock time with <b>o której</b> - o której odjeżdża pociąg? The answer often uses <b>za</b> + time: za dziesięć minut.",
              options:[
                { pl:"O której odjeżdża pociąg?", en:"What time does the train leave?",
                  note:"'o której (godzinie)?' = at what time?", goto:"s11" },
                { pl:"Przepraszam, kiedy jest następny pociąg?", en:"Excuse me, when's the next train?",
                  note:"'następny' = next - następny pociąg, następny przystanek.", goto:"s11" }
              ]
            },
            s11: {
              npc:"Za dziesięć minut.", npcEn:"In ten minutes.",
              options:[
                { pl:"Dziękuję, zdążę.", en:"Thank you, I'll make it.",
                  note:"'Zdążyć' = to make it in time - a handy transit verb.", goto:"s12" }
              ]
            },
            s12: {
              npc:"(Nie wiesz, czy możesz tu zostawić samochód.)", npcEn:"(You're not sure if you can park here.)",
              tip:"<b>Ściąga:</b> <b>czy można</b> + infinitive asks if something's allowed - czy można tu zaparkować / płacić / wejść?",
              options:[
                { pl:"Czy można tu zaparkować?", en:"Can I park here?",
                  note:"'czy można' + infinitive = is it allowed to...?", goto:"s13" }
              ]
            },
            s13: {
              npc:"Tak, ale to strefa płatna.", npcEn:"Yes, but it's a paid zone.",
              options:[
                { pl:"Rozumiem, dziękuję.", en:"I understand, thank you.", goto:"s14" }
              ]
            },
            s14: {
              npc:"(Potrzebujesz toalety w centrum handlowym.)", npcEn:"(You need a restroom in the mall.)",
              options:[
                { pl:"Gdzie znajdę toaletę?", en:"Where can I find the restroom?", goto:"s15" },
                { pl:"Przepraszam, gdzie jest toaleta?", en:"Excuse me, where's the toilet?", goto:"s15" }
              ]
            },
            s15: {
              npc:"Na końcu korytarza po prawej.", npcEn:"At the end of the hall on the right.",
              options:[
                { pl:"Dziękuję!", en:"Thank you!", goto:"s16" }
              ]
            },
            s16: {
              npc:"(Chcesz wiedzieć, czy zapłacisz telefonem.)", npcEn:"(You want to know if you can pay with your phone.)",
              options:[
                { pl:"Czy można płacić Blikiem?", en:"Can I pay with Blik?",
                  note:"BLIK is Poland's near-universal mobile payment code.", goto:"s17" }
              ]
            },
            s17: {
              npc:"Oczywiście.", npcEn:"Of course.",
              options:[
                { pl:"Świetnie, dzięki.", en:"Great, thanks.", goto:"s18" }
              ]
            },
            s18: {
              npc:"(Nie jesteś pewien, jak daleko do dworca.)", npcEn:"(You're not sure how far it is to the station.)",
              options:[
                { pl:"Czy daleko stąd do dworca?", en:"Is it far from here to the station?", goto:"s19" },
                { pl:"Ile czasu zajmie dojście na dworzec?", en:"How long does it take to walk to the station?",
                  note:"'dojście' = getting there on foot (a noun from dojść).", goto:"s19" }
              ]
            },
            s19: {
              npc:"Około pięciu minut na piechotę.", npcEn:"About five minutes on foot.",
              options:[
                { pl:"To niedaleko, dziękuję.", en:"That's not far, thank you.", goto:"end" }
              ]
            },
            end: {
              npc:"Miłej podróży!", npcEn:"Have a good trip!",
              end:true
            }
          }
        },
        {
          name: "Siłownia", emoji: "\uD83D\uDD04", kind: "convo",
          desc: "Gym etiquette: sharing equipment and small talk",
          role: "Ludzie na siłowni",
          setting: "You're at the gym - sharing equipment, offering a spot, the small rituals of training alongside strangers.",
          goal: "Handle common gym-etiquette exchanges naturally and politely.",
          recap: [
            "<b>czy ... jest wolny / wolna / wolne?</b> = is it free? (adjective agrees with the noun)",
            "modal <b>mogę / możesz</b> + infinitive - czy mogę wziąć? możesz brać",
            "<b>będę / będziesz</b> + verb = ongoing future - będziesz korzystać",
            "<b>korzystać z</b> + genitive - korzystać z ławki, z hantli"
          ],
          start: "s1",
          scenes: {
            s1: {
              npc:"(Chcesz zapytać, czy sztanga obok jest wolna.)", npcEn:"(You want to ask if the barbell nearby is free.)",
              tip:"<b>Ściąga:</b> ask if something's free with <b>czy ... jest wolny / wolna / wolne</b> - the adjective agrees with the noun (sztanga → wolna, sprzęt → wolny).",
              options:[
                { pl:"Przepraszam, czy ta sztanga jest wolna?", en:"Excuse me, is this barbell free?",
                  note:"'sztanga' is feminine → 'wolna'.", goto:"s2" },
                { pl:"Czy mogę wziąć tę sztangę?", en:"Can I take this barbell?",
                  note:"Modal 'mogę' + infinitive; 'sztanga' → 'sztangę' (accusative).", goto:"s2" }
              ]
            },
            s2: {
              npc:"Tak, skończyłem.", npcEn:"Yes, I'm done.",
              options:[
                { pl:"Super, dzięki!", en:"Great, thanks!", goto:"s3" }
              ]
            },
            s3: {
              npc:"Ile serii ci jeszcze zostało?", npcEn:"(Someone waiting for your equipment) How many sets do you have left?",
              options:[
                { pl:"Dwie serie.", en:"Two sets.",
                  note:"'Seria' = a set (of an exercise) - key gym vocabulary.", goto:"s4" },
                { pl:"To moja ostatnia.", en:"This is my last one.", goto:"s4" }
              ]
            },
            s4: {
              npc:"Możemy robić na zmianę?", npcEn:"(Same person) Can we alternate?",
              options:[
                { pl:"Pewnie, wchodź.", en:"Sure, jump in.",
                  note:"'Wchodź' (from wchodzić) is the casual invite to alternate sets.", goto:"s5" },
                { pl:"Jasne, możemy się zmieniać.", en:"Sure, we can take turns.",
                  note:"'zmieniać się' = to take turns (reflexive).", goto:"s5" }
              ]
            },
            s5: {
              npc:"Potrzebujesz asekuracji?", npcEn:"(Someone nearby) Need a spot?",
              options:[
                { pl:"Tak, przydałaby się.", en:"Yes, that would be helpful.",
                  note:"'Przydałaby się' = 'it would come in handy' - agrees with 'asekuracja' (fem.).", goto:"s6" },
                { pl:"Nie, dzięki, dam radę.", en:"No thanks, I got it.",
                  note:"'Dam radę' = 'I can manage' - a very common confidence phrase.", goto:"s6" }
              ]
            },
            s6: {
              npc:"(Chcesz wiedzieć, czy ktoś używa tych hantli.)", npcEn:"(You want to know if someone's using these dumbbells.)",
              options:[
                { pl:"Używasz tych hantli?", en:"Are you using these dumbbells?",
                  note:"'używać' + genitive: używasz hantli, sprzętu.", goto:"s7" },
                { pl:"Czy mogę wziąć te hantle?", en:"Can I take these dumbbells?",
                  note:"Modal 'mogę' + infinitive: czy mogę wziąć?", goto:"s7" }
              ]
            },
            s7: {
              npc:"Nie, możesz brać.", npcEn:"No, you can take them.",
              options:[
                { pl:"Dzięki.", en:"Thanks.", goto:"s8" }
              ]
            },
            s8: {
              npc:"Długo jeszcze będziesz korzystać z ławki?", npcEn:"(Someone waiting) Will you be using the bench much longer?",
              tip:"<b>Ściąga:</b> ongoing future = <b>będę / będziesz</b> + verb - <i>będziesz korzystać z ławki?</i> ('korzystać z' takes the genitive).",
              options:[
                { pl:"Jeszcze jakieś pięć minut.", en:"About five more minutes.", goto:"s9" },
                { pl:"Już kończę, zaraz będzie wolna.", en:"I'm almost done, it'll be free soon.",
                  note:"'będzie wolna' = it'll be free (future of być + adjective).", goto:"s9" }
              ]
            },
            s9: {
              npc:"(Zapomniałeś magnezji i chcesz kogoś zapytać.)", npcEn:"(You forgot your chalk and want to ask someone.)",
              options:[
                { pl:"Czy masz może magnezję?", en:"Do you have chalk by chance?",
                  note:"'Może' softens the question - 'by chance' makes an ask feel lighter.", goto:"s10" }
              ]
            },
            s10: {
              npc:"Tak, proszę.", npcEn:"Yes, here you go.",
              options:[
                { pl:"Dzięki, oddam za chwilę.", en:"Thanks, I'll give it back in a second.", goto:"s11" }
              ]
            },
            s11: {
              npc:"(Chcesz sprawdzić, czy szafka jest zajęta.)", npcEn:"(You want to check if a locker is taken.)",
              options:[
                { pl:"Czy ta szafka jest zajęta?", en:"Is this locker taken?", goto:"s12" },
                { pl:"Czy ta szafka jest wolna?", en:"Is this locker free?",
                  note:"'zajęta' (taken) vs 'wolna' (free) - two ways to ask the same thing.", goto:"s12" }
              ]
            },
            s12: {
              npc:"Tak, moja.", npcEn:"Yes, it's mine.",
              options:[
                { pl:"A, przepraszam.", en:"Oh, sorry.", goto:"s13" }
              ]
            },
            s13: {
              npc:"(Nie wiesz, gdzie zostawić kurtkę.)", npcEn:"(You don't know where to leave your jacket.)",
              options:[
                { pl:"Gdzie mogę zostawić kurtkę?", en:"Where can I leave my jacket?",
                  note:"Modal 'mogę' + infinitive: gdzie mogę zostawić?", goto:"s14" },
                { pl:"Gdzie zostawia się kurtki?", en:"Where do people leave their jackets?",
                  note:"'zostawia się' = impersonal 'one leaves / people leave' (się + 3rd person).", goto:"s14" }
              ]
            },
            s14: {
              npc:"Szafki są w szatni.", npcEn:"Lockers are in the changing room.",
              options:[
                { pl:"Dziękuję.", en:"Thank you.", goto:"s15" }
              ]
            },
            s15: {
              npc:"(Chcesz wiedzieć, o której siłownia dziś zamyka.)", npcEn:"(You want to know what time the gym closes today.)",
              options:[
                { pl:"O której dzisiaj zamykacie?", en:"What time do you close today?",
                  note:"'o której?' = at what time?", goto:"s16" }
              ]
            },
            s16: {
              npc:"O dwudziestej drugiej.", npcEn:"At 22:00 (10 PM).",
              options:[
                { pl:"Dobrze, dziękuję.", en:"Alright, thank you.", goto:"end" }
              ]
            },
            end: {
              npc:"Udanego treningu!", npcEn:"Enjoy your workout!",
              end:true
            }
          }
        },
        {
          name: "Praca i uczelnia", emoji: "\uD83C\uDF93", kind: "convo",
          desc: "Coffee breaks, deadlines, and office small talk",
          role: "Koledzy z pracy/uczelni",
          setting: "A regular day at work or university - coffee breaks, quick favors, deadlines, and casual check-ins with colleagues or classmates.",
          goal: "Respond naturally to the small talk and requests that fill a normal workday.",
          recap: [
            "future: <b>będę</b> + verb (będę odpoczywać) or a perfective verb (wyślę, pojadę)",
            "modal <b>nie mogę / muszę</b> + infinitive - nie mogę, mam spotkanie",
            "verbs of motion - idziemy na kawę, jadę do rodziny",
            "<b>o której?</b> = at what time (o dziesiątej)"
          ],
          start: "s1",
          scenes: {
            s1: {
              npc:"Idziemy na kawę?", npcEn:"(A colleague) Going for a coffee?",
              options:[
                { pl:"Chętnie.", en:"I'd love to.", goto:"s2" },
                { pl:"Jasne, chodźmy.", en:"Sure, let's go.",
                  note:"'chodźmy' = let's go (imperative of chodzić, the 'my' form).", goto:"s2" },
                { pl:"Nie mogę, mam spotkanie.", en:"I can't, I have a meeting.",
                  note:"Modal 'nie mogę' + a reason.", goto:"s2" },
                { pl:"Za chwilę, muszę coś dokończyć.", en:"In a minute, I have to finish something.",
                  note:"Modal 'muszę' + infinitive: muszę dokończyć.", goto:"s2" }
              ]
            },
            s2: {
              npc:"O której masz jutro wykład?", npcEn:"(A classmate) What time is your lecture tomorrow?",
              options:[
                { pl:"O dziesiątej.", en:"At 10:00.",
                  note:"'o + której' → 'o dziesiątej' (at ten).", goto:"s3" },
                { pl:"Nie mam jutro zajęć.", en:"I don't have classes tomorrow.",
                  note:"'nie mam' + genitive: nie mam zajęć.", goto:"s3" }
              ]
            },
            s3: {
              npc:"Pomóc ci w czymś?", npcEn:"(A colleague) Need help with something?",
              options:[
                { pl:"Nie, dzięki, radzę sobie.", en:"No thanks, I'm managing.",
                  note:"'Radzę sobie' = 'I'm managing / coping'.", goto:"s4" },
                { pl:"Tak, możesz mi pomóc z tym raportem?", en:"Yes, can you help me with this report?",
                  note:"'pomóc' + dative person + 'z' + instrumental thing: pomóc mi z raportem.", goto:"s4" }
              ]
            },
            s4: {
              npc:"Prześlesz mi notatki?", npcEn:"(A classmate) Will you send me the notes?",
              tip:"<b>Ściąga:</b> a perfective verb's present-looking form is future - <b>wyślę</b> = I'll send (and finish), <b>prześlesz</b> = you'll send.",
              options:[
                { pl:"Jasne, wyślę ci wieczorem.", en:"Sure, I'll send them tonight.",
                  note:"'wyślę' = perfective future (I'll send and finish).", goto:"s5" },
                { pl:"Nie mam ich, zapytaj Kasię.", en:"I don't have them, ask Kasia.",
                  note:"'zapytaj' = ask (imperative of zapytać).", goto:"s5" }
              ]
            },
            s5: {
              npc:"Jesteś dzisiaj w biurze?", npcEn:"(A colleague, messaging you) Are you in the office today?",
              options:[
                { pl:"Pracuję z domu.", en:"I'm working from home.", goto:"s6" },
                { pl:"Tak, będę do siedemnastej.", en:"Yes, I'll be here until 5 PM.",
                  note:"'będę' = future of być: I'll be (here).", goto:"s6" }
              ]
            },
            s6: {
              npc:"Masz chwilę?", npcEn:"(A colleague) Do you have a second?",
              options:[
                { pl:"Tak, o co chodzi?", en:"Yes, what's up?", goto:"s7" },
                { pl:"Daj mi pięć minut.", en:"Give me five minutes.",
                  note:"'Daj' = give (imperative of dać).", goto:"s7" }
              ]
            },
            s7: {
              npc:"Kiedy masz deadline?", npcEn:"(A colleague) When is your deadline?",
              options:[
                { pl:"W przyszłym tygodniu.", en:"Next week.", goto:"s8" },
                { pl:"Muszę to skończyć do piątku.", en:"I have to finish it by Friday.",
                  note:"Modal 'muszę' + infinitive; 'do piątku' = by Friday.", goto:"s8" }
              ]
            },
            s8: {
              npc:"Idziemy coś zjeść?", npcEn:"(A colleague) Should we go grab something to eat?",
              options:[
                { pl:"Pewnie, jestem głodny.", en:"Sure, I'm hungry.",
                  note:"Gendered: jestem głodny (m) / jestem głodna (f).", goto:"s9" },
                { pl:"Jasne, umieram z głodu.", en:"Sure, I'm starving.",
                  note:"'umierać z głodu' = to be starving - a gender-free option.", goto:"s9" },
                { pl:"Nie teraz, muszę skończyć zadanie.", en:"Not now, I have to finish a task.",
                  note:"Modal 'muszę' + infinitive.", goto:"s9" }
              ]
            },
            s9: {
              npc:"Jaki masz plan na weekend?", npcEn:"(A colleague, small talk) What's your plan for the weekend?",
              tip:"<b>Ściąga:</b> talk about plans with the future - <b>będę</b> + verb (będę odpoczywać) or a perfective verb (pojadę, zrobię).",
              options:[
                { pl:"Żadnych planów, po prostu odpoczywam.", en:"No plans, just resting.", goto:"s10" },
                { pl:"Jadę do rodziny za miasto.", en:"I'm going to visit family out of town.",
                  note:"'jechać' (by vehicle): jadę do rodziny.", goto:"s10" },
                { pl:"Będę się uczyć do egzaminu.", en:"I'll be studying for an exam.",
                  note:"Ongoing future: będę + uczyć się.", goto:"s10" },
                { pl:"W sobotę idę na siłownię, a w niedzielę odpoczywam.", en:"Saturday I'm going to the gym, Sunday I'm resting.",
                  note:"'iść' (on foot): idę na siłownię.", goto:"s10" },
                { pl:"Jeszcze nie wiem, zobaczymy.", en:"I don't know yet, we'll see.",
                  note:"'zobaczymy' = we'll see (perfective future).", goto:"s10" }
              ]
            },
            s10: {
              npc:"Działa ci internet?", npcEn:"(A colleague, before a call) Is your internet working?",
              options:[
                { pl:"Nie, znowu coś przerywa.", en:"No, it's cutting out again.", goto:"end" },
                { pl:"Tak, wszystko działa.", en:"Yes, everything's working.", goto:"end" }
              ]
            },
            end: {
              npc:"OK, napisz jak wróci.", npcEn:"OK, let me know when it's back.",
              end:true
            }
          }
        },
        {
          name: "Sąsiedzi i codzienność", emoji: "\uD83C\uDFE0", kind: "convo",
          desc: "Small talk with neighbors and everyday building life",
          role: "Sąsiedzi",
          setting: "Everyday life around your building and neighborhood - small talk, favors, and the little frictions of shared spaces.",
          goal: "Handle casual neighborly exchanges the way a local would.",
          recap: [
            "weather: <b>jest ciepło / zimno / słonecznie</b>; <b>pada</b> (it rains), <b>wieje</b> (it's windy)",
            "<b>mam</b> + accusative - mam kota, psa",
            "<b>od</b> + genitive for duration - od kilku lat, od roku",
            "<b>mieszkać</b> (present) - mieszkam tu od roku"
          ],
          start: "s1",
          scenes: {
            s1: {
              npc:"Jaka dzisiaj pogoda?", npcEn:"(A neighbor) What's the weather like today?",
              tip:"<b>Ściąga:</b> weather uses impersonal adverbs - <i>jest ciepło / zimno / słonecznie</i> - or a verb: <i>pada</i> (it's raining), <i>wieje</i> (it's windy).",
              options:[
                { pl:"Zimno i pada.", en:"Cold and raining.",
                  note:"'pada' = it's raining (also 'pada deszcz / śnieg').", goto:"s2" },
                { pl:"Całkiem ładnie, słonecznie.", en:"Quite nice, sunny.",
                  note:"'słonecznie' = sunny (adverb).", goto:"s2" },
                { pl:"Strasznie wieje.", en:"It's terribly windy.",
                  note:"'wieje (wiatr)' = the wind is blowing.", goto:"s2" },
                { pl:"Ciepło, ale pochmurno.", en:"Warm, but cloudy.",
                  note:"'pochmurno' = cloudy; 'ciepło' = warm.", goto:"s2" },
                { pl:"Zrobiło się zimno.", en:"It's turned cold.",
                  note:"'zrobiło się' = it became / turned (reflexive past, neuter).", goto:"s2" }
              ]
            },
            s2: {
              npc:"Co u ciebie?", npcEn:"(A neighbor) What's up with you?",
              options:[
                { pl:"Stara bieda.", en:"Same old.",
                  note:"Literally 'old poverty' - means 'nothing new, same as always'.", goto:"s3" },
                { pl:"Wszystko po staremu.", en:"Everything as usual.",
                  note:"'po staremu' = the same as before.", goto:"s3" }
              ]
            },
            s3: {
              npc:"Masz jakieś zwierzęta?", npcEn:"(A neighbor) Do you have any pets?",
              options:[
                { pl:"Tak, mam kota.", en:"Yes, I have a cat.",
                  note:"'mam' + accusative: 'kot' → 'kota'.", goto:"s4" },
                { pl:"Mam psa i dwa koty.", en:"I have a dog and two cats.",
                  note:"'pies' → 'psa'; 'dwa koty' = two cats.", goto:"s4" },
                { pl:"Nie, nie mam zwierząt.", en:"No, I don't have pets.",
                  note:"'nie mam' + genitive: nie mam zwierząt.", goto:"s4" },
                { pl:"Jeszcze nie, może kiedyś.", en:"Not yet, maybe one day.",
                  note:"'może kiedyś' = maybe someday - a gender-free, non-committal reply.", goto:"s4" }
              ]
            },
            s4: {
              npc:"Długo tu mieszkasz?", npcEn:"(A neighbor) Have you lived here long?",
              options:[
                { pl:"Od kilku lat.", en:"For a few years.",
                  note:"'od' + genitive for duration: od kilku lat.", goto:"s5" },
                { pl:"Mieszkam tu od roku.", en:"I've lived here for a year.",
                  note:"'mieszkać' (present): mieszkam, mieszkasz; 'od roku' = for a year.", goto:"s5" }
              ]
            },
            s5: {
              npc:"Czy winda działa?", npcEn:"(A neighbor, in the lobby) Is the elevator working?",
              options:[
                { pl:"Znowu zepsuta.", en:"Broken again.", goto:"s6" },
                { pl:"Tak, na szczęście działa.", en:"Yes, luckily it's working.",
                  note:"'na szczęście' = luckily / thankfully.", goto:"s6" }
              ]
            },
            s6: {
              npc:"Kto to zostawił na klatce?", npcEn:"(A neighbor) Who left this in the stairwell?",
              options:[
                { pl:"Nie mam pojęcia.", en:"I have no idea.",
                  note:"'nie mam pojęcia' = I have no clue - a set phrase.", goto:"s7" }
              ]
            },
            s7: {
              npc:"Mógłbyś ściszyć muzykę?", npcEn:"(A neighbor) Could you turn the music down?",
              options:[
                { pl:"Oczywiście, przepraszam.", en:"Of course, sorry.", goto:"s8" },
                { pl:"Jasne, już ściszam.", en:"Sure, I'm turning it down now.",
                  note:"'już ściszam' = I'm turning it down right now.", goto:"s8" }
              ]
            },
            s8: {
              npc:"Masz ognia?", npcEn:"(A stranger) Do you have a light?",
              options:[
                { pl:"Nie palę, przykro mi.", en:"I don't smoke, sorry.",
                  note:"'przykro mi' = I'm sorry (I feel bad) - dative construction.", goto:"s9" }
              ]
            },
            s9: {
              npc:"Gdzie wyrzucić ten karton?", npcEn:"(A neighbor) Where do I throw away this cardboard?",
              options:[
                { pl:"Do niebieskiego pojemnika.", en:"In the blue bin.",
                  note:"Poland sorts recycling by color: blue = paper, yellow = plastic & metal, green = glass.", goto:"s10" }
              ]
            },
            s10: {
              npc:"Miłego dnia!", npcEn:"(Parting words) Have a nice day!",
              options:[
                { pl:"Nawzajem!", en:"You too!",
                  note:"'Nawzajem' = likewise / same to you - the reply to any good wish.", goto:"end" },
                { pl:"Dziękuję, wzajemnie!", en:"Thank you, likewise!",
                  note:"'wzajemnie' = likewise (a touch more formal than nawzajem).", goto:"end" }
              ]
            },
            end: {
              npc:"Do zobaczenia!", npcEn:"See you around!",
              end:true
            }
          }
        }
      ]
    }
  );
})();
