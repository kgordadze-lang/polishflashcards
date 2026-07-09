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
        },
        {
          name: "Sklep i usługi", emoji: "\uD83D\uDCB0", kind: "convo",
          desc: "Paying, ordering, and quick everyday errands",
          role: "Sprzedawcy i kasjerki",
          setting: "You're running errands around town - a shop, a café, a parcel pickup. Quick, everyday exchanges keep coming your way.",
          goal: "Answer naturally and quickly. Every reply is a valid path.",
          start: "s1",
          scenes: {
            s1: {
              npc:"Karta czy gotówka?", npcEn:"(At the till) Card or cash?",
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
              npc:"Potrzebuje pan/pani paragon?", npcEn:"(Cashier) Do you need a receipt?",
              options:[
                { pl:"Nie, dziękuję.", en:"No, thanks.", goto:"s4" },
                { pl:"Tak, poproszę.", en:"Yes, please.", goto:"s4" }
              ]
            },
            s4: {
              npc:"Czy może być dłużna grosika?", npcEn:"(Cashier, short of small change) Would you mind if I owe you a few grosze?",
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
              options:[
                { pl:"Poproszę duże cappuccino.", en:"A large cappuccino, please.",
                  note:"'Poproszę' + Accusative is the standard ordering formula - swap in any drink or dish.", goto:"s9" }
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
          start: "s1",
          scenes: {
            s1: {
              npc:"(Chcesz zapytać, jak dojść do stacji metra.)", npcEn:"(You want to ask how to get to the metro station.)",
              options:[
                { pl:"Przepraszam, jak dojść do stacji metra?", en:"Excuse me, how do I get to the metro station?",
                  note:"'Jak dojść do...' + Genitive is the go-to formula for asking directions on foot.", goto:"s2" }
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
                  note:"'Czy' opens any yes/no question - just add it in front of a statement.", goto:"s4" }
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
                  note:"Literally 'is this place free?' - always ask before sitting next to a stranger.", goto:"s6" }
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
                { pl:"Przepraszam, gdzie jest biletomat?", en:"Excuse me, where is the ticket machine?", goto:"s9" }
              ]
            },
            s9: {
              npc:"Tam, przy wejściu.", npcEn:"Over there, by the entrance.",
              options:[
                { pl:"Dzięki!", en:"Thanks!",
                  note:"'Dzięki' is the casual, everyday version of 'dziękuję' - fine with strangers in informal settings like this.", goto:"s10" }
              ]
            },
            s10: {
              npc:"(Chcesz wiedzieć, kiedy odjeżdża twój pociąg.)", npcEn:"(You want to know when your train leaves.)",
              options:[
                { pl:"O której odjeżdża pociąg?", en:"What time does the train leave?", goto:"s11" }
              ]
            },
            s11: {
              npc:"Za dziesięć minut.", npcEn:"In ten minutes.",
              options:[
                { pl:"Dziękuję, zdążę.", en:"Thank you, I'll make it.",
                  note:"'Zdążyć' = to make it in time - a handy verb for anything transit-related.", goto:"s12" }
              ]
            },
            s12: {
              npc:"(Nie wiesz, czy możesz tu zostawić samochód.)", npcEn:"(You're not sure if you can park here.)",
              options:[
                { pl:"Czy można tu zaparkować?", en:"Can I park here?", goto:"s13" }
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
                { pl:"Gdzie znajdę toaletę?", en:"Where can I find the restroom?", goto:"s15" }
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
                  note:"BLIK is Poland's near-universal mobile payment code - assume it works almost everywhere.", goto:"s17" }
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
                { pl:"Czy daleko stąd do dworca?", en:"Is it far from here to the station?", goto:"s19" }
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
          start: "s1",
          scenes: {
            s1: {
              npc:"(Chcesz zapytać, czy sztanga obok jest wolna.)", npcEn:"(You want to ask if the barbell nearby is free.)",
              options:[
                { pl:"Przepraszam, czy ta sztanga jest wolna?", en:"Excuse me, is this barbell free?", goto:"s2" }
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
                  note:"'Seria' = a set (of an exercise) - a key gym vocabulary word.", goto:"s4" },
                { pl:"To moja ostatnia.", en:"This is my last one.", goto:"s4" }
              ]
            },
            s4: {
              npc:"Możemy robić na zmianę?", npcEn:"(Same person) Can we alternate?",
              options:[
                { pl:"Pewnie, wchodź.", en:"Sure, jump in.",
                  note:"'Wchodź' (from wchodzić, to enter/join) is the casual invite to alternate sets with someone.", goto:"s5" }
              ]
            },
            s5: {
              npc:"Potrzebujesz asekuracji?", npcEn:"(Someone nearby) Need a spot?",
              options:[
                { pl:"Tak, przydałaby się.", en:"Yes, that would be helpful.",
                  note:"'Przydałoby się' = 'would come in handy' - a soft, polite way to accept an offer.", goto:"s6" },
                { pl:"Nie, dzięki, dam radę.", en:"No thanks, I got it.",
                  note:"'Dam radę' = 'I can manage' - very common everyday confidence phrase.", goto:"s6" }
              ]
            },
            s6: {
              npc:"(Chcesz wiedzieć, czy ktoś używa tych hantli.)", npcEn:"(You want to know if someone's using these dumbbells.)",
              options:[
                { pl:"Używasz tych hantli?", en:"Are you using these dumbbells?", goto:"s7" }
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
              options:[
                { pl:"Jeszcze jakieś pięć minut.", en:"About five more minutes.", goto:"s9" }
              ]
            },
            s9: {
              npc:"(Zapomniałeś magnezji i chcesz kogoś zapytać.)", npcEn:"(You forgot your chalk and want to ask someone.)",
              options:[
                { pl:"Czy masz może magnezję?", en:"Do you have chalk by chance?",
                  note:"'Może' softens the question - 'by chance' makes any ask feel less demanding.", goto:"s10" }
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
                { pl:"Czy ta szafka jest zajęta?", en:"Is this locker taken?", goto:"s12" }
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
                { pl:"Gdzie mogę zostawić kurtkę?", en:"Where can I leave my jacket?", goto:"s14" }
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
                { pl:"O której dzisiaj zamykacie?", en:"What time do you close today?", goto:"s16" }
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
          start: "s1",
          scenes: {
            s1: {
              npc:"Idziemy na kawę?", npcEn:"(A colleague) Going for a coffee?",
              options:[
                { pl:"Chętnie.", en:"I'd love to.", goto:"s2" },
                { pl:"Nie mogę, mam spotkanie.", en:"I can't, I have a meeting.", goto:"s2" }
              ]
            },
            s2: {
              npc:"O której masz jutro wykład?", npcEn:"(A classmate) What time is your lecture tomorrow?",
              options:[
                { pl:"O dziesiątej.", en:"At 10:00.", goto:"s3" }
              ]
            },
            s3: {
              npc:"Pomóc ci w czymś?", npcEn:"(A colleague) Need help with something?",
              options:[
                { pl:"Nie, dzięki, radzę sobie.", en:"No thanks, I'm managing.",
                  note:"'Radzę sobie' = 'I'm managing / coping' - a natural, not-too-formal way to decline help.", goto:"s4" }
              ]
            },
            s4: {
              npc:"Prześlesz mi notatki?", npcEn:"(A classmate) Will you send me the notes?",
              options:[
                { pl:"Jasne, wyślę ci wieczorem.", en:"Sure, I'll send them tonight.", goto:"s5" }
              ]
            },
            s5: {
              npc:"Jesteś dzisiaj w biurze?", npcEn:"(A colleague, messaging you) Are you in the office today?",
              options:[
                { pl:"Pracuję z domu.", en:"I'm working from home.", goto:"s6" }
              ]
            },
            s6: {
              npc:"Masz chwilę?", npcEn:"(A colleague) Do you have a second?",
              options:[
                { pl:"Tak, o co chodzi?", en:"Yes, what's up?", goto:"s7" },
                { pl:"Daj mi pięć minut.", en:"Give me five minutes.", goto:"s7" }
              ]
            },
            s7: {
              npc:"Kiedy masz deadline?", npcEn:"(A colleague) When is your deadline?",
              options:[
                { pl:"W przyszłym tygodniu.", en:"Next week.", goto:"s8" }
              ]
            },
            s8: {
              npc:"Idziemy coś zjeść?", npcEn:"(A colleague) Should we go grab something to eat?",
              options:[
                { pl:"Pewnie, jestem głodny.", en:"Sure, I'm hungry.", goto:"s9" }
              ]
            },
            s9: {
              npc:"Jaki masz plan na weekend?", npcEn:"(A colleague, small talk) What's your plan for the weekend?",
              options:[
                { pl:"Żadnych planów, po prostu odpoczywam.", en:"No plans, just resting.", goto:"s10" }
              ]
            },
            s10: {
              npc:"Działa ci internet?", npcEn:"(A colleague, before a call) Is your internet working?",
              options:[
                { pl:"Nie, znowu coś przerywa.", en:"No, it's cutting out again.", goto:"end" }
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
          start: "s1",
          scenes: {
            s1: {
              npc:"Jaka dzisiaj pogoda?", npcEn:"(A neighbor) What's the weather like today?",
              options:[
                { pl:"Zimno i pada.", en:"Cold and raining.", goto:"s2" },
                { pl:"Całkiem ładnie.", en:"Quite nice.", goto:"s2" }
              ]
            },
            s2: {
              npc:"Co u ciebie?", npcEn:"(A neighbor) What's up with you?",
              options:[
                { pl:"Stara bieda.", en:"Same old.",
                  note:"Literally 'old poverty' - a set phrase Poles use to mean 'nothing new, same as always.'", goto:"s3" }
              ]
            },
            s3: {
              npc:"Masz jakieś zwierzęta?", npcEn:"(A neighbor) Do you have any pets?",
              options:[
                { pl:"Tak, mam kota.", en:"Yes, I have a cat.", goto:"s4" }
              ]
            },
            s4: {
              npc:"Długo tu mieszkasz?", npcEn:"(A neighbor) Have you lived here long?",
              options:[
                { pl:"Od kilku lat.", en:"For a few years.", goto:"s5" }
              ]
            },
            s5: {
              npc:"Czy winda działa?", npcEn:"(A neighbor, in the lobby) Is the elevator working?",
              options:[
                { pl:"Znowu zepsuta.", en:"Broken again.", goto:"s6" }
              ]
            },
            s6: {
              npc:"Kto to zostawił na klatce?", npcEn:"(A neighbor) Who left this in the stairwell?",
              options:[
                { pl:"Nie mam pojęcia.", en:"I have no idea.", goto:"s7" }
              ]
            },
            s7: {
              npc:"Mógłbyś ściszyć muzykę?", npcEn:"(A neighbor) Could you turn the music down?",
              options:[
                { pl:"Oczywiście, przepraszam.", en:"Of course, sorry.", goto:"s8" }
              ]
            },
            s8: {
              npc:"Masz ogień?", npcEn:"(A stranger) Do you have a light?",
              options:[
                { pl:"Nie palę, przykro mi.", en:"I don't smoke, sorry.", goto:"s9" }
              ]
            },
            s9: {
              npc:"Gdzie wyrzucić ten karton?", npcEn:"(A neighbor) Where do I throw away this cardboard?",
              options:[
                { pl:"Do niebieskiego pojemnika.", en:"In the blue bin.",
                  note:"Poland sorts recycling by color: blue = paper/cardboard, yellow = plastic & metal, green = glass.", goto:"s10" }
              ]
            },
            s10: {
              npc:"Miłego dnia!", npcEn:"(Parting words) Have a nice day!",
              options:[
                { pl:"Nawzajem!", en:"You too!",
                  note:"'Nawzajem' = 'likewise / same to you' - the all-purpose reply to any good wish.", goto:"end" }
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
