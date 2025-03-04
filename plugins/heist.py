import random
import plugins.ai as ai
import plugins.pizzadatabase as db
import plugins.points as points
from datetime import datetime
import json

random.seed(datetime.now().timestamp())
medium_chance = 90

medium_target_list = ["KFC", "McDonalds", "Pizzerie \"IT&AM\"", "Bank Spermy", "Bank Zywnosci", "Budke z Kebabem", "Siedzibe Discorda", "Dozorce z Metin2", "Skarbiec Kowala z Metin2", "Muzeum Figur Woskowych", "Wesole miasteczko", "Teatr Muzyczny", "Zaklad Wyrobow Metalowych", "Tibijski Bank", "Disneyland", "Siedzibe Valve", "Salon Samochodowy", "Kopalnie soli w Wieliczce", "Automatyczne Myjnie Samochodowe", "Siedzibe Gangu Albanii", "Hurtownie Jaboli", "Jubilera"]
hard_target_list = ["Platinum Casino w Bulgarii", "Bank Narodowy", "Lotnisko Chopina w Warszawie", "Bialy Dom w Waszyngtonie", "Siedzibe El Chapo w Meksyku", "Baze Klientow Orange Polska", "Posesje na ulicy Smolika"]
circumstances = ["", "", "", "", "", " w bialy dzien", " pod oslona nocy", " w samo poludnie", " w czarny piatek", " - Walentynkowy Rabunek", " z udzialem tresowanej papugi", " z uzyciem gumowych kurczakow", " z uzyciem pistoletow na wode", " z uzyciem konfetti", " w strojach mikolajow", " - Sylwestrowa Akcja", " przebrani za krasnale ogrodowe", " - Wielkanocna Akcja", " w asyscie Golebia", " w calkowitej ciszy", " w rytmie walca wiedenskeigo", " przebrani za postacie z bajek"]

#returns level ["hard", "medium"] and heist name
def generateHeist():
    heist_list = medium_target_list
    level = "medium"
    initial_loot = random.randint(5000,15000)
    initial_chance = random.randint(20,80)
    if random.randint(1, 100) > medium_chance:
        heist_list = hard_target_list
        initial_loot = random.randint(30000,100000)
        initial_chance = random.randint(10,30)
        level = "hard"
    
    heist_name = "Napad na " + random.choice(heist_list) + random.choice(circumstances)
    db.initializeHeist(heist_name, initial_loot, initial_chance)
    return level, heist_name, initial_loot, initial_chance

def generateHeistIntro(heist_name):
    return ai.askAI("Wygeneruj zabawny, krotki wstep do napadu o nazwie:" + str(heist_name) + ", zachejaca uczestnikow gry tekstowej do przystapienia do zabawy. Nie informuj jak dolaczyc do napadu - ta czesc zostanie dodana przeze mnie.")

#returns - intro, simulation, ending, json with results
def heistSimulation(heist_name, initial_loot, initial_chance):
    members = list(db.retrieveHeistMembers())
    if members:
        if len(members) > 1:
            db.setHeistOngoing()
            listOfCommands = []
            listOfCommands.append("heist_name: " + str(heist_name))
            memberStr = ""
            totalContribution = 0
            finalLoot = initial_loot
            finalChance = initial_chance
            for member in members:
                finalLoot += int(finalLoot * 0.2)
                memberStr += str(member[0]) + ":" +str(member[1]) + ","
                totalContribution += int(member[1])
                finalChance += 1
            finalChance += int(totalContribution / 10000)

            listOfCommands.append("members: "+memberStr[:-1])
            listOfCommands.append("chance: " + str(finalChance) + "%")
            listOfCommands.append("expected_loot: "+str(finalLoot))
            acts = ai.generateHeist(listOfCommands).split("ROZDZIELNIK_ETAP")
            return acts[0], acts[1], acts[2], acts[3].strip().lstrip('```json\n').rstrip('```')
        else:
            #return points to player
            points.addPoints(db.retrieveUser('name', members[0][0])['discord_id'], int(members[0][1]))
            return "Za malo osob wzielo udzial w napadzie.", None, None, None
    else:
        return "Nikt nie wzial udzialu w napadzie.", None, None, None

def finalizeHeist(json_result):
    db.moveCurrentHeistToHistory(json_result)
    if json_result:
        json_result = json.loads(json_result)
        for member in json_result['members']:
            if member['arrested']:
                db.arrestUser('name', member['name'])
            else:
                if json_result['heist_success']:
                    points.addPoints(db.retrieveUser('name', member['name'])['discord_id'], int(member['loot']) + int(member['contribution']))
                else:
                    points.addPoints(db.retrieveUser('name', member['name'])['discord_id'], int(member['loot']))
    return None