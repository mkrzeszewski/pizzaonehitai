import random
import plugins.ai as ai
import plugins.pizzadatabase as db

medium_chance = 80

medium_target_list = ["KFC", "McDonalds", "Pizzerie IT&AM", "Bank Spermy", "Siedzibe Discorda", "Dozorce z Metin2", "Muzeum Figur Woskowych", "Wesole miasteczko", "Teatr Muzyczny w Lodzi", "Bank na de_overpass w CS2", "Bank w Tibii"]
hard_target_list = ["Platinum Casino w Bulgarii", "Bank Narodowy", "Lotnisko Chopina w Warszawie", "Bialy Dom w Waszyngtonie", "Siedziba El Chapo w Meksyku"]
circumstances = ["", " w bialy dzien", " pod oslona nocy", " w samo poludnie", " podczas burzy piaskowej", " w czarny piatek", " - Walentynkowy Rabunek", " z udzialem tresowanej papugi"]

#returns level ["hard", "medium"] and heist name
def generateHeistName():
    heist_list = medium_target_list
    level = "medium"
    if random.randint(1, 100) < medium_chance:
        heist_list = hard_target_list
        level = "hard"
    return level, "Napad na " + random.choice(heist_list) + random.choice(circumstances)

def generateHeistIntro(heist_name):
    return ai.askAI("Wygeneruj zabawny, krotki wstep do napadu o nazwie:" + str(heist_name) + ", zachejaca uczestnikow gry tekstowej do przystapienia do zabawy. Nie informuj jak dolaczyc do napadu - ta czesc zostanie dodana przeze mnie.")

#returns - intro, simulation, ending, json with results
def heistGeneration(heist_name, members):
    if members:
        if len(members) > 1:
            listOfCommands = []
            listOfCommands.append("heist_name: " + str(heist_name))
            memberStr = ""
            for member in members:
                memberStr += str(member[0]) + ":" +str(member[1]) + ","
            listOfCommands.append("members: "+memberStr[:-1])
            listOfCommands.append("chance: " + str(random.randint(30,80)) + "%")
            listOfCommands.append("expected_loot: "+str(random.randint(1000,10000)))
            acts = ai.generateHeist(listOfCommands).split("ROZDZIELNIK_ETAP")
            return acts[0], acts[1], acts[2], acts[3].strip().lstrip('```json\n').rstrip('```')
        else:
            return "Za malo osob wzielo udzial w napadzie."
