import random
import plugins.ai as ai
import plugins.pizzadatabase as db
import plugins.points as points
from datetime import datetime
import json

random.seed(datetime.now().timestamp())
medium_chance = 90

medium_target_list = ["KFC", "McDonalds", "Pizzerie IT&AM", "Bank Spermy", "Siedzibe Discorda", "Dozorce z Metin2", "Muzeum Figur Woskowych", "Wesole miasteczko", "Teatr Muzyczny w Lodzi", "Bank na de_overpass w CS2", "Bank w Tibii", "Disneyland", "Siedzibe Valve", "Salon Dacia", "Kopalnie soli w Wieliczce", "Kopalnie w Belchatowie"]
hard_target_list = ["Platinum Casino w Bulgarii", "Bank Narodowy", "Lotnisko Chopina w Warszawie", "Bialy Dom w Waszyngtonie", "Siedziba El Chapo w Meksyku"]
circumstances = ["", " w bialy dzien", " pod oslona nocy", " w samo poludnie", " podczas burzy piaskowej", " w czarny piatek", " - Walentynkowy Rabunek", " z udzialem tresowanej papugi", " z uzyciem gumowych kurczakow", " z uzyciem balonow na wode", " z uzyciem konfetti", ""]


#returns level ["hard", "medium"] and heist name
def generateHeist():
    heist_list = medium_target_list
    level = "medium"
    initial_loot = random.randint(1000,10000)
    initial_chance = random.randint(50,80)
    if random.randint(1, 100) > medium_chance:
        heist_list = hard_target_list
        initial_loot = random.randint(10000,50000)
        initial_chance = random.randint(30,50)
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
            finalChance = initial_chance
            for member in members:
                memberStr += str(member[0]) + ":" +str(member[1]) + ","
                totalContribution += int(member[1])
                finalChance += 2
            finalChance += int(totalContribution / 1000)

            listOfCommands.append("members: "+memberStr[:-1])
            listOfCommands.append("chance: " + str(finalChance) + "%")
            listOfCommands.append("expected_loot: "+str(initial_loot))
            acts = ai.generateHeist(listOfCommands).split("ROZDZIELNIK_ETAP")
            return acts[0], acts[1], acts[2], acts[3].strip().lstrip('```json\n').rstrip('```')
        else:
            #return points to player
            points.addPoints(db.retrieveUser('name', member[0])['discord_id'], int(member[1]))
            return "Za malo osob wzielo udzial w napadzie.", None, None, None
    else:
        return "Nikt nie wzial udzialu w napadzie.", None, None, None

def finalizeHeist(json_result):
    db.moveCurrentHeistToHistory(json_result)
    if json_result:
        json_result = json.loads(json_result)
        for member in json_result['members']:
            if member['arrested']:
                print("omegalul")
            else:
                points.addPoints(db.retrieveUser('name', member['name'])['discord_id'], int(member['loot']) + int(member['contribution']))
        else:
            return "OH"
        return None