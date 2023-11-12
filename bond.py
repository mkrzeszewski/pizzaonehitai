from demoparser2 import DemoParser

parser = DemoParser("demo.dem")
ticks = parser.parse_event("round_end")["tick"]

df = parser.parse_ticks(["kills_total"], ticks=[1])
names = df["name"]

wanted_fields = ["kills_total", "deaths_total"]

for tick in ticks:
    df = parser.parse_ticks(wanted_fields, ticks=[tick])

    for i in range(0,len(names)):
        kills = df['kills_total'][i]
        deaths = df['deaths_total'][i]

        if kills == 0 and deaths == 7:
            print(f"{names[i]} BOND")
            print(df)
