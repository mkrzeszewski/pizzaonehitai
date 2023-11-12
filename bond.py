from demoparser2 import DemoParser

parser = DemoParser("demo.dem")
ticks = parser.parse_event("round_end")["tick"][6:]

df = parser.parse_ticks(["kills_total"], ticks=[100])
names = df["name"]

wanted_fields = ["kills_total", "deaths_total"]
print(names)
minDeaths = 0
minKills = 0
for tick in ticks:
    df = parser.parse_ticks(wanted_fields, ticks=[tick])
    currRoundMinDeaths = 0
    currRoundMinKills = 0
    for i in range(0,len(names)):
        kills = df['kills_total'][i]
        deaths = df['deaths_total'][i]
        
        

        if kills == 0 and deaths == 1:
            print(f"{names[i]} BOND")
            print(df)
    if minDeaths > 7 or minKills > 0:
        break
