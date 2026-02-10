import random
from discord import Embed, Colour, File
import time
from os import environ
from datetime import datetime, timedelta
import requests
import plugins.points as points
import plugins.pizzadatabase as db
import plugins.ai as ai

BARTOLO_KEY = environ["BARTOLO_KEY"]
API_KEY="&key=" + environ["GOOGLE_MAPS_API_KEY"]

ICON_ARRAY = ["https://cdn.metatft.com/file/metatft/traits/rebel.png", 
              "https://cdn.metatft.com/file/metatft/traits/warband.png", 
              "https://cdn.metatft.com/file/metatft/traits/squad.png", 
              "https://cdn.metatft.com/file/metatft/traits/crime.png"]

GAMBA_RANDOM_ICON_ARRAY = ["https://cdn3.emoji.gg/emojis/5897-peepo-gamba.gif",
                           "https://cdn3.emoji.gg/emojis/3135-pepegamble.gif",
                           "https://cdn3.emoji.gg/emojis/3955-gamba-addict.gif"]

BIRTHDAY_RANDOM_ICON_ARRAY = [ "https://cdn3.emoji.gg/emojis/83280-confettipopper.gif",
                                "https://cdn3.emoji.gg/emojis/82548-balloons.gif"]

SIGN_ICON_ARRAY = {
    "baran": "https://cdn3.emoji.gg/emojis/42434-aries.png",
    "byk": "https://cdn3.emoji.gg/emojis/44512-taurus.png",
    "bliznieta": "https://cdn3.emoji.gg/emojis/42244-gemini.png",
    "rak": "https://cdn3.emoji.gg/emojis/87993-cancer.png",
    "lew": "https://cdn3.emoji.gg/emojis/85770-leo.png",
    "panna": "https://cdn3.emoji.gg/emojis/47057-virgo.png",
    "waga": "https://cdn3.emoji.gg/emojis/12487-libra.png",
    "skorpion": "https://cdn3.emoji.gg/emojis/6245-scorpio.png",
    "strzelec": "https://cdn3.emoji.gg/emojis/68830-sagittarius.png",
    "koziorozec": "https://cdn3.emoji.gg/emojis/27440-capricorn.png",
    "wodnik": "https://cdn3.emoji.gg/emojis/53835-aquarius.png",
    "ryby": "https://cdn3.emoji.gg/emojis/9982-pisces.png"
}

PEPE_BIRTHDAY_EMOTE = "<:pepebirthday:1127216158974677084>"

#help function to ensure text is <1000 characters
def split_text(text: str, max_length: int = 1000):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

##################################################################

class BaseEmbedGen:
    def __init__(self):
        self.DEFAULT_FOOTER_ICON = "https://cdn3.emoji.gg/emojis/16965-cutepizza.png"
        self.DEFAULT_AUTHOR_ICON = "https://cdn3.emoji.gg/emojis/48134-bmodancing.gif"
        self.DEFAULT_FOOT_TEXT = "Sztuczna inteligencja na twoim discordzie!"
        self.DEFAULT_AUTHOR = "Pizza One Hit AI"
        self.NEUTRAL_COLOR = Colour.light_grey()
        self.help_hint = ""

    def _create_base(self, title, description, color=None, thumbnail=None):
        embed_color = color if color else self.NEUTRAL_COLOR
        full_description = f"{description}{self.help_hint}"
        embed = Embed(
            title=title,
            description=full_description,
            color=embed_color
        )
        embed.set_author(name=self.DEFAULT_AUTHOR, icon_url=self.DEFAULT_AUTHOR_ICON)
        embed.set_footer(text=self.DEFAULT_FOOT_TEXT, icon_url=self.DEFAULT_FOOTER_ICON)

        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        return embed
    
    def neutral_msg(self, title, message):
        return self._create_base(title, message)
    
##################################################################

class GambleEmbedGen(BaseEmbedGen):
    def __init__(self):
        super().__init__()
        self.help_hint = "\n\n💡 `!slots`, `!gamble`"
        self.color = Colour.light_grey()

class HoroscopeEmbedGen(BaseEmbedGen):
    def __init__(self):
        super().__init__()
        # Simple back button for horoscopes
        self.help_hint = "\nhttps://horoskop.wp.pl/horoskop/horoskop-dzienny/\n\n🔮 Sprawdź swoj horoskop na dzis (lub kogoś) `!horoskop`, `!horoskop @<USER>`"
        self.color = Colour.pink()

    def horoscope(self, msg, sign):
        return self._create_base("Horoskop na dzis dla " + str(sign), msg, self.color, db.icon("BOGDANOFF_ICON"), thumbnail = SIGN_ICON_ARRAY[sign])
    
class HeistEmbedGen(BaseEmbedGen):
    def __init__(self):
        super().__init__()
        # Simple back button for horoscopes
        self.help_hint = "\nhttps://horoskop.wp.pl/horoskop/horoskop-dzienny/\n\n🔮 Sprawdź swoj horoskop na dzis (lub kogoś) `!horoskop`, `!horoskop @<USER>`"
        self.color = Colour.pink()

    def horoscope(self, msg, sign):
        return self._create_base("Horoskop na dzis dla " + str(sign), msg, self.color, db.icon("BOGDANOFF_ICON"), thumbnail = SIGN_ICON_ARRAY[sign])
##################################################################

class StocksGen(BaseEmbedGen):
    def __init__(self):
        super().__init__()
        self.help_hint = "\n\n💡 `!stonks`, `!fullstonks`, `!buy`, `!sell`"
        self.GREEN = Colour.dark_green()
        self.RED = Colour.dark_red()
        self.GOLD = Colour.dark_gold()

    def _format_mcap(self, val):
        """Helper to format Market Cap numbers."""
        if val >= 1000000: return f"{val/1000000:.2f}M"
        if val >= 1000: return f"{val/1000:.2f}k"
        return str(val)

    def full_stonks(self, stocks):
        sorted_stocks = sorted(stocks, key=lambda s: int(s['price']) * int(s.get('totalShares', 1)), reverse=True)
        description = "🚀 **Oto obecnie dostępne akcje na giełdzie P1H:**\n"
        
        for s in sorted_stocks:
            mcap = self._format_mcap(int(s['price']) * int(s.get('totalShares', 1)))
            description += f"\n**{s['symbol']}** | {s['name']}\n┗ 💰 *Market Cap:* `{mcap} ppkt.`\n"
            
        return self._create_base("📈 Giełda Pizza One Hit", description, self.GREEN, db.icon("STONKS_ICON"))

    def rundown(self, msg):
        return self._create_base("Co tam słychać na giełdzie?", msg, self.GREEN, db.icon("BOGDANOFF_ICON"))

    def overview(self, stocks):
        sorted_stocks = sorted(stocks, key=lambda s: int(s['price']) * int(s.get('totalShares', 1)), reverse=True)
        table = f"{'SYM':<5} | {'PRICE':<6} | {'AVAILABLE':<10} | {'MCAP':<8}\n"
        table += "—" * 40 + "\n"
        
        for s in sorted_stocks:
            mcap = self._format_mcap(int(s['price']) * int(s.get('totalShares', 1)))
            table += f"{s['symbol']:<5} | {s['price']:<6} | {s['availableShares']:<10} | {mcap:<8}\n"
            
        return self._create_base("WallStreet - Pizza One Hit", f"```py\n{table}```", self.GREEN, db.icon("STONKS_ICON"))

    def bottom_stocks(self, stocks):
        description = ""
        for s in stocks:
            description += f"* **[{s['symbol']}]** {s['name']}:\n   Dostępne: `{s['availableShares']}` | Cena: `{s['price']}`\n\n"
        return self._create_base("Giełda P1H - Bottom 5", description, self.RED, db.icon("BOGDANOFF_ICON"))

    def bankruptcy(self, stock, bad_investors=None):
        # AI Logic stays here
        ai_msg = ai.askAI(f"Poinformuj o bankructwie {stock['name']}. CEO {stock['ceo']} coś odjebał. Zrób to żartobliwie.")
        description = str(ai_msg)
        
        if bad_investors:
            investors_list = "\n".join([f" - {i}" for i in bad_investors])
            description += f"\n\n**Nieudacznicy, którzy stracili kasę:**\n{investors_list}"
            
        return self._create_base(f"{stock['name']} bankrutuje!", description, self.RED, db.icon("STINKS_ICON"))

    def user_portfolio(self, user, avatar=None):
        description = ""
        total = 0
        if user.get('stocksOwned'):
            for share in user['stocksOwned']:
                stock = db.retrieveStock('symbol', share['symbol'])
                description += f"* **[{stock['symbol']}]** {stock['name']} - {share['amount']} udz.\n"
                total += int(stock['price'] * share['amount'])
            description += f"\n💰 **Wartość portfela:** `{total} ppkt.`"
        else:
            description = f"Użytkownik {user['name']} nie posiada akcji."
            
        return self._create_base(f"Portfel - {user['name']}", description, self.GOLD, avatar or db.icon("STINKS_ICON"))

    def stock_event(self, user, stock, msg, event_type="buy"):
        if event_type == "buy":
            title = f"{user['name']} kupuje akcje {stock['name']}!"
            icon = db.icon("PURCHASE_STOCK_ICON")
            color = self.GREEN
        elif event_type == "sell":
            title = f"{user['name']} sprzedaje akcje {stock['name']}!"
            icon = db.icon("SELL_STOCK_ICON")
            color = self.RED
        else: # "cashout"
            title = f"{user['name']} ma dość! Sprzedaje wszystko!"
            icon = db.icon("SELL_STOCK_ICON")
            color = self.RED

        return self._create_base(title, msg, color, icon)

##################################################################

class UtilityEmbedGen(BaseEmbedGen):
    def __init__(self):
        super().__init__()
        self.ERROR_COLOR = Colour.red()
        self.INFO_COLOR = Colour.blue()
        self.REWARD_COLOR = Colour.gold()
        self.SUCCESS_COLOR = Colour.dark_green()

    def error_msg(self, action_name, error_text, usage=None):
        title = f"❌ Błąd: {action_name}"
        description = f"**Problem:** {error_text}"
        if usage:
            description += f"\n\n**Poprawne użycie:**\n`{usage}`"
            
        return self._create_base(title, description, color=self.ERROR_COLOR, thumbnail="https://cdn.7tv.app/emote/01G4ZTECKR0002P97QQ94BDSP4/4x.avif")
    
    def main_help(self):
        title = "Tutorial używania bota:"
        description = "Oto lista dostępnych komend, które pomogą Ci przetrwać na serwerze."
        
        embed = self._create_base(
            title=title, 
            description=description, 
            color=self.INFO_COLOR,
            thumbnail="https://cdn.7tv.app/emote/01G4ZTECKR0002P97QQ94BDSP4/4x.avif"
        )
        
        commands = (
            "`!help` - to okno.\n"
            "`!analyzetft <id>` - analiza meczu TFT.\n"
            "`!analyzelol <id>` - analiza meczu LOL'a.\n"
            "`!points` - aktualna liczba punktów.\n"
            "`!top X` - top X bogaczy.\n"
            "`!horoskop` - horoskop na dziś!\n"
            "`!ai <pytanie>` - zadaj pytanie AI!\n"
            "`!stocks` - giełda P1H\n"
        )
        embed.add_field(name="Komendy:", value=commands, inline=False)
        return embed
    
    def achievements(self, achievements_list):
        title = "🏆 Osiągnięcia na serwerze Pizza One Hit"
        description = "Oto lista legendarnych czynów dokonanych na naszym serwerze!"
        embed = self._create_base(
            title=title,
            description=description,
            color=self.REWARD_COLOR,
            thumbnail=db.icon("PEPE_PUCHAR")
        )
        for ach in achievements_list:
            who = ach['user'] if ach['user'] != "" else "👑 [TU MOŻESZ BYĆ TY!]"
            field_name = f"✨ {ach['achievement']} — {who}"
            field_value = f"*{ach['description']}*"
            embed.add_field(name=field_name, value=field_value, inline=False)
        return embed
    
    def user_points(self, user, avatarURL=""):
        points = int(user['points'])
        title = f"Portfel użytkownika {user['name']}"
        
        # 1. Dynamic Ranking Logic
        if points < 1000:
            rank = "📉 Totalny Biedak"
            color = self.NEUTRAL_COLOR
        elif points < 5000:
            rank = "😐 Przechodzień"
            color = self.INFO_COLOR
        elif points < 10000:
            rank = "🎮 Niedzielny Gracz"
            color = self.INFO_COLOR
        elif points < 20000:
            rank = "💼 Przedsiębiorca"
            color = self.INFO_COLOR
        elif points < 40000:
            rank = "📈 Inwestor"
            color = self.SUCCESS_COLOR
        elif points < 50000:
            rank = "💰 Szycha"
            color = self.SUCCESS_COLOR
        elif points < 100000:
            rank = "💎 Specjalista"
            color = self.REWARD_COLOR
        elif points < 1000000:
            rank = "🎩 Elita P1H"
            color = self.REWARD_COLOR
        elif points < 10000000:
            rank = "🏦 Legenda Giełdy"
            color = 0xFFD700 # Gold
        else:
            rank = "👑 Bóg Pieniędzy"
            color = 0x00FFFF # Cyan/Godly

        formatted_points = f"{points:,}"
        description = (
            f"**Ranga:** {rank}\n"
            f"💰 **Saldo:** `{formatted_points}` ppkt\n"
            f"───────────────────"
        )

        # 3. Create the Embed
        embed = self._create_base(
            title=title,
            description=description,
            color=color,
            thumbnail=avatarURL if avatarURL else db.icon("DEFAULT_POINTS_ICON")
        )
        
        # If they are super rich, add a special flair field
        if points >= 1000000:
            embed.add_field(name="Status", value="✨ Ten użytkownik jest nietykalny!", inline=False)
            
        return embed
    
    def leaderboards(self, users, amount, board_type="top"):
        # 1. Setup specific board details
        if board_type == "top":
            title_prefix = "📈 Najbogatsi"
            field_name = f"__Top {amount}:__"
            thumb = db.icon("POINTS_ICON")
            start_rank = 1
            step = 1
        else:
            title_prefix = "📉 Najbiedniejsi"
            field_name = f"__Bottom {amount}:__"
            thumb = db.icon("POINTS_ICON")
            # For bottom, we calculate the starting rank based on total users
            total_users = len(list(db.retrieveAllUsers()))
            start_rank = total_users
            step = -1

        # 2. Build the list string
        string_list = ""
        current_rank = start_rank
        for user in users:
            points = f"{user['points']:,}" # 1,000,000 instead of 1000000
            string_list += f"**{current_rank})** {user['name']} — `{points}` ppkt\n"
            current_rank += step

        # 3. Create the base
        embed = self._create_base(
            title=f"{title_prefix} na DC Pizza One Hit!",
            description="Ranking użytkowników według posiadanych punktów.",
            color=self.INFO_COLOR,
            thumbnail=thumb
        )
        embed.add_field(name=field_name, value=string_list if string_list else "Brak danych.", inline=False)
        return embed
    
    def beggar_handout(self, user):
        title = "🚮 Zapomoga dla Biedaka"
        description = (
            f"Patrzcie na niego! **{user['name']}** jest absolutnie spłukany.. "
            "Zupełnie nic mu nie zostało, więc rzucamy mu ochłapy, żeby nie płakał.\n\n"
            "💰 **Jałmużna:** `100` pkt\n"
            "🐢 *Postaraj się nie stracić tego w 30 sekund...*"
        )

        return self._create_base(
            title=title,
            description=description,
            color=self.NEUTRAL_COLOR,
            thumbnail=db.icon("BEGGAR_ICON")
        )

    def admin_add_points(self, target_user, amount, admin_name):
        title = "🏦 Interwencja Banku Centralnego"
        description = (
            f"Wielki Admin **{admin_name}** wyczarował punkty z niebytu!\n\n"
            f"👤 **Odbiorca:** {target_user['name']}\n"
            f"💰 **Kwota:** `{amount:,}` pkt\n"
            f"✨ *Saldo zostało zaktualizowane pomyślnie.*"
        )

        return self._create_base(
            title=title,
            description=description,
            color=self.SUCCESS_COLOR,
            thumbnail=db.icon("ADMIN_CASH")
        )
    
    def admin_set_points(self, target_user, new_amount, admin_name):
        title = "⚖️ Korekta Salda przez Admina"
        description = (
            f"Admin **{admin_name}** dokonał ręcznej korekty portfela.\n\n"
            f"👤 **Użytkownik:** {target_user['name']}\n"
            f"🎯 **Nowe saldo:** `{new_amount:,}` pkt\n"
            f"📢 *Poprzednie punkty zostały zastąpione nową wartością.*"
        )

        return self._create_base(
            title=title,
            description=description,
            color=self.ERROR_COLOR, # Używamy czerwonego/pomarańczowego, bo to drastyczna zmiana
            thumbnail=db.icon("ADMIN_CASH")
        )
##################################################################

class GambleEmbedGen(BaseEmbedGen):
    def __init__(self):
        super().__init__()
        self.WIN_COLOR = Colour.dark_green()
        self.LOSE_COLOR = Colour.dark_red()

##################################################################

class TheatreEmbedGen(BaseEmbedGen):
    def __init__(self):
        super().__init__()
        self.DEFAULT_COLOR = Colour.purple()

    def theatre_event_list(self, theatre, event, dates):
        description = "Nowe daty spektakli na wydarzenie!\n"
        for date in dates:
            description += f"\n - {date['text']}"
            
        embed = self._create_base(
            title=f"{theatre} - {event}.",
            description=description,
            color=self.DEFAULT_COLOR,
            thumbnail=db.icon("GENTLEMAN_CAT_ICON")
        )
        
        # Note: Footer and Author are already set by _create_base!
        return embed

def generateEmbedFromTFTMatch(results,players,matchID, date):
    #title of embed - ranked/normal - set
    topTitle = results[0] + " - " + results[1]

    #we random icons for now (left - up corner)
    embedIcon = random.choice(ICON_ARRAY)
    endColour = Colour.blue()

    #main title and embed data 
    embed = Embed(title = str("Nowa partia z P1H w TFT!"), description = None, colour = endColour )
    embed.set_author(name = topTitle, icon_url = embedIcon)
    embed.set_thumbnail(url = db.icon("TFT_ICON"))

    playerList = ""
    iterator = 0
    for player in players:
        #if its one of our players - we want to underline and bold him
        #if player in importantPeople:
        #    player = "__**" + player + "**__"
        iterator += 1
        playerList = playerList + str (iterator) + ". " + player + "\n"

    #list players (strin playerList consist newlines)
    embed.add_field(name = "__Gracze w lobby:__", value = (playerList), inline = False)
    
    #we delete info of ranked/normal and set - no longer needed in later part
    del results[0]
    del results[0]

    # CAN BE DONE BETTER - this field is to split player section and trivia section
    embed.add_field(name = "Interesting stuff: ", value = "=======================================", inline = False)

    #trivia print (given form analyze match method)
    for result in results:
        embed.add_field(name = "", value = result, inline = False)

    #footer with match ID + date
    formatted_time = time.strftime('%Y-%m-%d %H:%M', time.gmtime(int(date)))
    embed.set_footer(text = str(matchID) + "                                                                            " + str(formatted_time), icon_url = db.icon("FOOTER_TFT_ICON"))

    #print(datetime.datetime.fromtimestamp(date))
    return embed

def generateEmbedFromLeagueMatch(results,players,matchID):

    playerList = ""
    for player in players:
        playerList = playerList + player + ", "
    playerList = playerList[:-2]
    print (str("Chłopaki: " + playerList + " zagrali sobie ARAMka!"))
    print(results[:-1])
    
    endGameStatus = "Kolejna przegrana.."
    endGameIcon = db.icon("LOSE_ICON")
    endColour = Colour.red()

    if(results[-2] == "win"):
        endGameStatus = "EZ WIN"
        endGameIcon = db.icon("WIN_ICON")
        endColour = Colour.green()
        
    embed = Embed(title = str(playerList + " zagrali sobie ARAMka!"), description = str(results[-1]), colour = endColour )
    embed.set_author(name = endGameStatus, icon_url = endGameIcon)
    embed.set_thumbnail(url = db.icon("TFT_ICON"))
    for result in results[:-2]:
        embed.add_field(name = "", value = result, inline = False)

    embed.set_footer(text = str(matchID), icon_url = db.icon("FOOTER_ICON"))
    return embed

def generateEmbedFromRestaurant(restaurant):
    embedIcon = random.choice(ICON_ARRAY)
    endColour = Colour.blue()
    
    #print(restaurant['photos']['photo_reference'])
    #print(PHOTO_REFERENCE_URL + str(restaurant['photos'][0]['photo_reference']) + API_KEY)
    #print(restaurant['photos'][0]['photo_reference'])
    #main title and embed data 
    embed = Embed(title = restaurant['name'], description = restaurant['vicinity'], colour = endColour )
    embed.set_author(name = "Restauracja wybrana!", icon_url = restaurant['icon'])
    #if restaurant['photos']:
    #embed.set_thumbnail(url = requests.get(PHOTO_REFERENCE_URL + str(restaurant['photos'][0]['photo_reference']) + API_KEY, allow_redirects = False).headers['location'])
    return embed

def generateEmbedFromHoroscope(text, sign, name):
    embed = Embed(colour = Colour.purple(), title = str(sign).capitalize(), description = text)
    embed.set_author(name = "Horoskop na dzis - dla Ciebie, " + str(name) + "!", icon_url = SIGN_ICON_ARRAY[sign])
    embed.set_footer(text = "source : https://horoskop.wp.pl/horoskop/horoskop-dzienny/")
    return embed

def generateHelpEmbed():
    embed = Embed(colour = Colour.yellow())
    embed.set_author(name = "Tutorial uzywania bota:", icon_url = "https://cdn.7tv.app/emote/01GR7R0H9G000FEKDNHQTECH62/2x.avif")
    embed.set_thumbnail(url = "https://cdn.7tv.app/emote/01G4ZTECKR0002P97QQ94BDSP4/4x.avif")
    listOfCommands = "`!help` - to okno.\n"
    listOfCommands += "`!analyzetft <match_id>` - analiza meczu TFT.\n"
    listOfCommands += "`!analyzelol <match_id>` - analiza meczu LOL'a.\n"
    listOfCommands += "`!points` - wyswietla aktualna liczbe punktow.\n"
    listOfCommands += "`!top X` - wyswietla top X posiadaczy punktow.\n"
    listOfCommands += "`!horoskop` - zwraca horoskop na dzis!\n"
    listOfCommands += "`!ai <pytanie>` - zadaj pytanie AI!\n"
    listOfCommands += "`!stocks - gielda P1H\n"
    embed.add_field(name = "Komendy:", value = listOfCommands)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def generateTopPointsEmbed(users, amount):
    stringList = ""
    increment = 0
    for user in users:
        increment = increment + 1
        stringList = stringList + str(increment) + ") " + user['name'] + " - " + str(user['points']) + " ppkt.\n"

    embed = Embed(title = "pizzopunkty na DC Pizza One Hit!", colour = Colour.og_blurple())
    embed.set_author(name = "Pizza One Hit AI", icon_url = db.icon("BOT_GIF_ADDRESS"))
    embed.set_thumbnail(url = db.icon("POINTS_ICON"))
    embed.add_field(name = "__Top " + str(amount) + ":__", value = (stringList), inline = False)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def generateBottomPointsEmbed(users, amount):
    stringList = ""
    increment = 0
    userList = list(db.retrieveAllUsers())
    allUsersLen = len(userList)
    for user in users:
        stringList = stringList + str(int(allUsersLen - increment)) + ") " + user['name'] + " - " + str(user['points']) + " ppkt.\n"
        increment = increment + 1

    embed = Embed(title = "pizzopunkty na DC Pizza One Hit!", colour = Colour.og_blurple())
    embed.set_author(name = "Pizza One Hit AI", icon_url = db.icon("BOT_GIF_ADDRESS"))
    embed.set_thumbnail(url = db.icon("POINTS_ICON_URL"))
    embed.add_field(name = "__Bottom " + str(amount) + ":__", value = (stringList), inline = False)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def generateRuletaWheel(id = 0, gif_path = "assets/gif/ruleta.gif"):
    embed = Embed(title="Ruleta #" + str(id), description="A zwycieza...", color=Colour.darker_grey())

    file = File(gif_path, filename = gif_path.split("/")[-1])
    embed.set_image(url="attachment://"+ gif_path.split("/")[-1])

    embed.set_author(name = "Pizza One Hit AI", icon_url = GAMBA_RANDOM_ICON_ARRAY[random.randint(0,len(GAMBA_RANDOM_ICON_ARRAY) - 1)])
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed, file

def generateRuletaResults(players, winner, id = 0):
    color = Colour.dark_blue()
    text = "niebieski"
    if winner == "Red":
        color = Colour.dark_red()
        text = "czerwony"
    elif winner == "Green":
        color = Colour.dark_green()
        text = "zielony"
        
    embed = Embed(title="Ruleta #" + str(id), description="Wygrywa... " + str(text) + "!", color=color)
    embed.set_author(name = "Pizza One Hit AI", icon_url = GAMBA_RANDOM_ICON_ARRAY[random.randint(0,len(GAMBA_RANDOM_ICON_ARRAY) - 1)])
    listOfPlayers = ""
    for player in players:
        sign = ""
        if int(player[2]) > 0:
            sign = "+"
        listOfPlayers = listOfPlayers + str(player[0]) + ": "+ str(sign) + str(player[2]) + "ppkt.\n"
    embed.add_field(name = "Bilans: ", value = listOfPlayers)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def generateRuletaChoices(id = 0):
    formatted_time = (datetime.now() + timedelta(hours=1, minutes=4)).strftime('%H:%M:%S')
    embed = Embed(title="Ruleta #" + str(id), description="Czas na gre do: " + str(formatted_time), color=Colour.darker_grey())
    embed.set_author(name = "Pizza One Hit AI", icon_url = GAMBA_RANDOM_ICON_ARRAY[random.randint(0,len(GAMBA_RANDOM_ICON_ARRAY) - 1)])
    embed.add_field(name = "Koszt - 50 PPKT", value = "!niebieski = x2!\n!czerwony = x2! \n !zielony = x25!")
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def generateRuletaPlayers(players, id = 0):
    embed = Embed(title="Ruleta #" + str(id), description="", color=Colour.darker_grey())
    embed.set_author(name = "Pizza One Hit AI", icon_url = GAMBA_RANDOM_ICON_ARRAY[random.randint(0,len(GAMBA_RANDOM_ICON_ARRAY) - 1)])
    embed.add_field(name = "Oto zawodnicy:", value = players)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def generateAIResponse(input, response):
    embed = Embed(title="Twoje pytanie: ", description=str(input), color=Colour.darker_grey())
    embed.add_field(name = "Odpowiedz: ", value = response)
    embed.set_author(name = "Pizza One Hit AI", icon_url = db.icon("BOT_GIF_ADDRESS"))
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def generateBirthdayEmbed(user, facts, wrozba):
    bdayPhrases = list(db.getAllBdayPhrases())
    embed = Embed(title="Dzis sa twoje urodziny, " + user['name'] + "!", description = PEPE_BIRTHDAY_EMOTE + " " + bdayPhrases[random.randint(0,len(bdayPhrases) - 1)], color=Colour.pink())
    embed.set_author(name = "Pizza One Hit AI", icon_url = BIRTHDAY_RANDOM_ICON_ARRAY[random.randint(0,len(BIRTHDAY_RANDOM_ICON_ARRAY) - 1)])
    body = ""
    if facts:
        for fact in facts:
            body = body + str(fact) + "\n"
    embed.add_field(name = "Ciekawostki: ", value = body, inline = False)
    embed.add_field(name = "Wrozba: ", value = wrozba, inline = False)
    embed.set_footer(text = "Do twojego konta zostalo przypisane 5000 pizzopkt!", icon_url = db.icon("PARTY_FACE"))
    return embed

def generateWinnerEmbed(user, userAvatarURL):
    aiMode = random.choice(list(db.getAllAiModes()))
    embed = Embed(title="Gratulacje, " + user['name'] + "!", description=ai.askAI("Pogratuluj uzytkownikowi: \""+ user['name'] + "\" wygranej w dziennej loterii pizzopunktow. Mów w nastepujacy  w sposob " + str(aiMode) + "."), color=Colour.dark_green())
    embed.set_thumbnail(url = userAvatarURL)
    embed.add_field(name = "Do twojego konta przypisalismy 500 ppkt + 15% twojej dotychczasowej ilosci pizzopunktow!", value="Woohoo!", inline = False)
    embed.set_author(name = "Pizza One Hit AI", icon_url = db.icon("BOT_GIF_ADDRESS"))
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def generateLoserEmbed(user, userAvatarURL):
    aiMode = random.choice(list(db.getAllAiModes()))
    #embed = Embed(title="Ojojoj, " + user['name'] + "...", description="Jestes dzisiejszym przegrywem..", color=Colour.dark_red())
    embed = Embed(title="Przykro nam, " + user['name'] + "!", description=ai.askAI("Poinformuj uzytkownika: \""+ user['name'] + "\" ze przegral w dziennej loterii pizzopunktow (tj zostaly mu pobrane z konta punkty). Mów w nastepujacy sposob " + str(aiMode) + "."), color=Colour.dark_red())
    embed.set_thumbnail(url = userAvatarURL)
    embed.add_field(name = "Z twojego konta zostalo odebrane 15% ppkt.", value="Sprobuj sie odbic na hazard-lounge!", inline = False)
    embed.set_author(name = "Pizza One Hit AI", icon_url = db.icon("BOT_GIF_ADDRESS"))
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def uploadDoBartola(gif_path):
    try:
        headers = {
            "Authorization":BARTOLO_KEY
        }

        fc = None
        with open(gif_path, "rb") as f:
            fc = f.read()

        files = {
            "file":fc
        }
        response = requests.post('https://slots.smnfbb.com/upload', headers=headers, files=files)

        if response.status_code == 200:
            points.addPoints(db.retrieveUser('name', "Bartolo")['discord_id'], 10) # prowizja 
            return response.json()["url"]
        else:
            points.addPoints(db.retrieveUser('name', "Bartolo")['discord_id'], -1000) # kara
            return None
    except Exception as e:
        return None


def generateSlotsAnimation(id = 0, gif_path = "assets/gif/slots.gif", amount = 0, user = None):
    description = "Gratulacje, " + user['name'] + "!"
    color = Colour.dark_green()
    infoString = " - wygrales " + str(amount) + " pizzopunktow!"
    if amount < 0:
        description = "Oops.."
        color = Colour.dark_red()
        infoString = " - przegrales " + str(amount * -1) + " pizzopunktow.."
    embed = Embed(title="Slotsy #" + str(id), description=description, color=color)

    file = File(gif_path, filename = gif_path.split("/")[-1])
    embed.set_image(url="attachment://"+ gif_path.split("/")[-1])

    embed.set_author(name = "Pizza One Hit AI", icon_url = GAMBA_RANDOM_ICON_ARRAY[random.randint(0,len(GAMBA_RANDOM_ICON_ARRAY) - 1)])
    embed.add_field(name = "Bilans gry:", value= user['name'] + infoString)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed, file

def generateUnknownUser(discord_id):
    embed = Embed(title="Nieznany uzytkownik" + str(discord_id), description="Uzytkownik o podanym ID nie istnieje w bazie!", color=Colour.red)
    embed.set_author(name = "Pizza One Hit AI", icon_url = db.icon("BOT_GIF_ADDRESS"))
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def generateHeistInvite(level, heist_name, message, time, id = 0):
    
    color = Colour.dark_orange()
    if level == "hard":
        color = Colour.dark_red()
    embed = Embed(title="Nowy napad grupowy!", description="Czas na dolaczenie: " + str(time) + ".", color = color)
    embed.set_author(name = "Pizza One Hit AI", icon_url = db.icon("BOT_GIF_ADDRESS"))

    embed.set_thumbnail(url = db.icon("CRIMINAL_ICON"))
    embed.add_field(name = heist_name, value=message, inline = False)

    embed.add_field(name = "Aby dolaczyc napisz **!joinheist <KWOTA>**", value = "Twoj wklad ma wplyw na wysokosc potencjalnej nagrody!", inline = False)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def generateHeistIntro(level, heist_name, message, id = 0):
    color = Colour.dark_orange()
    if level == "hard":
        color = Colour.dark_red()
    embed = Embed(title=heist_name, description=message, color = color)
    embed.set_author(name = "Pizza One Hit AI", icon_url = db.icon("BOT_GIF_ADDRESS"))

    embed.set_thumbnail(url = db.icon("CRIMINAL_ICON"))
    embed.add_field(name = "", value = "Trwaja przygotowania do napadu! Za jakis czas dowiecie sie, jak sprawdziliscie sie w swoich rolach!", inline = False)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def generateHeistBody(level, heist_name, message, id = 0):
    color = Colour.dark_orange()
    if level == "hard":
        color = Colour.dark_red()
    embed = Embed(title=heist_name, description=message, color = color)
    embed.set_author(name = "Pizza One Hit AI", icon_url = db.icon("BOT_GIF_ADDRESS"))

    embed.set_thumbnail(url = db.icon("CRIMINAL_ICON"))
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def generateHeistEnding(level, heist_name, message, id = 0):
    color = Colour.dark_orange()
    if level == "hard":
        color = Colour.dark_red()
    embed = Embed(title=heist_name, description=message, color = color)
    embed.set_author(name = "Pizza One Hit AI", icon_url = db.icon("BOT_GIF_ADDRESS"))

    embed.set_thumbnail(url = db.icon("CRIMINAL_ICON"))
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def generateHeistInfo(level, heist_name, time, members):
    color = Colour.dark_orange()
    if level == "hard":
        color = Colour.dark_red()
    embed = Embed(title="Obecnie zbieramy ekipe na :", description=heist_name, color = color)
    embed.set_author(name = "Pizza One Hit AI", icon_url = db.icon("BOT_GIF_ADDRESS"))
    description = ""
    for user in members:
        description += "* " + user[0] + "\n"
    embed.set_thumbnail(url = db.icon("CRIMINAL_ICON"))
    if description != "":
        embed.add_field(name = "Obecna ekipa sklada sie z:", value=description, inline = False)
    else:
        embed.add_field(name = "Obecnie nie ma chetnych na ten napad. Mozesz byc pierwszy!", value=description, inline = False)

    embed.add_field(name = "Aby dolaczyc napisz **!joinheist <KWOTA>**", value = "Czas na dolaczenie do: " + str(time) + ".", inline = False)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed
  
def generateHeistCanceled(heist_name):
    color = Colour.dark_orange()
    embed = Embed(title="Napad zostaje anulowany z powodu braku wystarczajacych uczestnikow! (min 2):", description=heist_name, color = color)
    embed.set_thumbnail(url = db.icon("CRIMINAL_ICON"))
    embed.add_field(name = "Sprobujcie szczescia w nastepnym napadzie..", value="Punkty zostaly zwrocone.", inline = False)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def generatePrisonRelease(users):
    color = Colour.dark_orange()
    description = ""
    for user in users:
        description += "* " + user['name'] + "\n"
    embed = Embed(title="Czlonkowie Pizza One Hit opuszczaja wiezienie!", description=description, color = color)
    embed.set_author(name = "Pizza One Hit AI", icon_url = db.icon("BOT_GIF_ADDRESS"))
    embed.set_thumbnail(url = db.icon("PEPE_PRISON"))
    embed.add_field(name = "Mozecie ponownie korzystac z komend na DC!", value="", inline = False)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def generateUserArrestedInfo(user):
    color = Colour.dark_gray()
    embed = Embed(title="Niestety, jestes aresztowany!", description="Nie mozesz korzystac z funkcjonalnosci bota.. Zostaniesz wypuszczony o 7 rano.", color = color)
    embed.set_author(name = "Pizza One Hit AI", icon_url = db.icon("BOT_GIF_ADDRESS"))
    embed.set_thumbnail(url = db.icon("PEPE_PRISON"))
    pointsInfo = "Obecnie posiadasz "
    if user:
        pointsInfo += str(user['points']) + " ppkt.\nUzyj komendy **!wykup** aby wyjsc z wiezienia."
    embed.add_field(name = "Mozesz sie wykupic za 50% wartosci swoich punktow! (minimum 300)", value=pointsInfo, inline = False)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def generateFreedUser(user, cost):
    color = Colour.dark_green()
    embed = Embed(title="Witamy na wolnosci, " + user['name'] + "!", description="Po uiszczeniu oplaty w wysokosci "+str(cost)+" twoj prawnik Cie wyciagnal!", color = color)
    embed.set_author(name = "Pizza One Hit AI", icon_url = db.icon("BOT_GIF_ADDRESS"))
    embed.set_thumbnail(url = db.icon("PEPE_LAWYER"))
    embed.add_field(name = "Mozesz ponownie korzystac z komend na DC!", value="", inline = False)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def generateArrestedUsersInfo(users):
    color = Colour.dark_gray()
    description = ""
    for user in users:
        description += "* " + user['name'] + "\n"
    embed = Embed(title="Oto obecni zaaresztowani zloczyncy:", description=description, color = color)
    embed.set_author(name = "Pizza One Hit AI", icon_url = db.icon("BOT_GIF_ADDRESS"))
    embed.set_thumbnail(url = db.icon("PEPE_PRISON"))
    embed.add_field(name = "", value="Wyslijcie im paczki na swieta..", inline = False)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def generateRewards(rewards):
    color = Colour.dark_green()
    embed = Embed(title="Nagrody na serwerze Pizza One Hit", description="Aby wykupic nagrode, napisz do roLab na PRIV.", color = color)
    embed.set_author(name = "Pizza One Hit AI", icon_url = db.icon("BOT_GIF_ADDRESS"))
    description = ""
    for reward in rewards:
        description += "* " + str(reward['text']) + " - " + str(reward['cost']) + "\n"
    embed.set_thumbnail(url = db.icon("PEPE_COIN"))
    embed.add_field(name = "Oto dostepne nagrody:", value=description, inline = False)
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def generateAchievements(achievements):
    color = Colour.gold()
    description = ""
    for achievement in achievements:
        who = achievement['user']
        if who == "":
            who = "[TU MOZESZ BYC TY!]"
        description += "* " + str(achievement['achievement']) + " - " + str(who) + "\n" + str(achievement['description']) + "\n\n"
    embed = Embed(title="Osiagniecia na serwerze Pizza One Hit", description=str(description), color = color)
    embed.set_author(name = "Pizza One Hit AI", icon_url = db.icon("BOT_GIF_ADDRESS"))
    embed.set_thumbnail(url = db.icon("PEPE_PUCHAR"))
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def generateStocksOverview(stocks):
    color = Colour.dark_green()
    sorted_stocks = sorted(
        stocks, 
        key=lambda s: int(s['price']) * int(s.get('totalShares', 1)), 
        reverse=True
    )
    description = "🚀 **Oto obecnie dostępne akcje na gieldzie P1H:**\n"
    
    for stock in sorted_stocks:
        # Calculate Market Cap
        mcap_val = int(stock['price']) * int(stock.get('totalShares', 1))
        if mcap_val >= 1000000:
            mcap_str = f"{mcap_val/1000000:.2f}M"
        elif mcap_val >= 1000:
            mcap_str = f"{mcap_val/1000:.1f}k"
        else:
            mcap_str = str(mcap_val)
        description += f"\n**{stock['symbol']}** | {stock['name']}\n┗ 💰 *Market Cap:* `{mcap_str} ppkt.`\n"

    description += "\n💡 `!stonks`, `!fullstonks`, `!buy`, `!sell`"
    embed = Embed(title="📈 Giełda Pizza One Hit", description=description, color=color)
    embed.set_author(name="Pizza One Hit AI", icon_url=db.icon("BOT_GIF_ADDRESS"))
    embed.set_thumbnail(url=db.icon("STONKS_ICON"))
    embed.set_footer(text="Sztuczna inteligencja na twoim discordzie!", icon_url=db.icon("PIZZA_ICON"))
    return embed

def generateStocksRundown(msg):
    color = Colour.dark_green()
    description = msg
    description += "\n💡 `!stonks`, `!fullstonks`, `!buy`, `!sell`"
    embed = Embed(title="Co tam slychac na gieldzie?", description=str(description), color = color)
    embed.set_author(name = "Pizza One Hit AI", icon_url = db.icon("BOT_GIF_ADDRESS"))
    embed.set_thumbnail(url = db.icon("BOGDANOFF_ICON"))
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def generateFullStonks(stocks):
    color = Colour.dark_green()
    sorted_stocks = sorted(
        stocks, 
        key=lambda s: int(s['price']) * int(s.get('totalShares', 1)), 
        reverse=True
    )

    description = "```py\n"
    description += f"{'SYM':<5} | {'PRICE':<6} | {'AVAILABLE SHARES':<16} | {'MCAP':<10}\n"
    description += "—" * 42 + "\n"
    
    for stock in sorted_stocks:
        sym = stock['symbol']
        prc = f"{stock['price']}"
        shr = f"{stock['availableShares']}"
        mcap_val = int(stock['price']) * int(stock.get('totalShares', 1))
        if mcap_val >= 1000000:
            mcap_str = f"{mcap_val/1000000:.2f}M"
        elif mcap_val >= 1000:
            mcap_str = f"{mcap_val/1000:.2f}k"
        else:
            mcap_str = str(mcap_val)
        description += f"{sym:<5} | {prc:<6} | {shr:<16} | {mcap_str:<10}\n"
        
    description += "```"
    description += "\n💡 `!stonks`, `!fullstonks`, `!buy`, `!sell`"
    embed = Embed(title="WallStreet - Pizza One Hit", description=str(description), color = color)
    embed.set_author(name = "Pizza One Hit AI", icon_url = db.icon("BOT_GIF_ADDRESS"))
    embed.set_thumbnail(url = db.icon("STONKS_ICON"))
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def generateBottomStocks(stocks):
    color = Colour.dark_red()
    description = ""
    for stock in stocks:
        description += "* [" + str(stock['symbol']) + "] " + str(stock['name']) + ":\nAvailable shares: [" + str(stock['availableShares']) + "]\nCurrent price: [" + str(stock['price']) + "]\n\n"
    description += "\n💡 `!stonks`, `!fullstonks`, `!buy`, `!sell`"
    embed = Embed(title="Gielda Pizza One Hit - bottom 5", description=str(description), color = color)
    embed.set_thumbnail(url = db.icon("BOGDANOFF_ICON"))
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def testMarkdown():
    color = Colour.dark_green()
    description = "```py\ntest\n```"
    embed = Embed(title="Test backticks.", description=str(description), color = color)
    embed.set_author(name = "Pizza One Hit AI", icon_url = db.icon("BOT_GIF_ADDRESS"))
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def generateBankrupcy(stock, userAvatarURL = 0, badInvestors = None):
    color = Colour.dark_red()
    description = str(ai.askAI("Poinformuj, ze firma " + str(stock['name']) + "oglosila bankrupctwo, i zartobliwie opisz dlaczego, uwzgledniajac dlaczego to sie stalo bo cos odjebal CEO o nicku " + str(stock['ceo']) + "."))
    if badInvestors:
        description += "\nNieudacznicy, ktorzy probowali zainwestowac w te firme: "
        for investor in badInvestors:
            description += "\n - " + str(investor)
    description += "\n💡 `!stonks`, `!fullstonks`, `!buy`, `!sell`"
    embed = Embed(title=str(stock['name']) + " bankrutuje!", description=str(description), color = color)
    if userAvatarURL:
        embed.set_thumbnail(url = userAvatarURL)
    else:
        embed.set_thumbnail(url = db.icon("STINKS_ICON"))
    embed.set_thumbnail(url = db.icon("STINKS_ICON"))
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def generateUserPortfolioEmbed(user, userAvatarURL = 0):
    color = Colour.dark_gold()
    description = ""
    totalAmount = 0
    if user['stocksOwned']:
        for share in user['stocksOwned']:
            stock = db.retrieveStock('symbol',share['symbol'])
            description += "* [" + str(stock['symbol']) + "] " + str(stock['name']) + " - " + str(share['amount']) + " udzialow.\n"
            totalAmount += int(stock['price'] * share['amount'])
        description += "Obecna wartosc akcji uzytkownika = " + str(totalAmount) + " pizzopuntkow."
    else:
        description += "Uzytkownik " + str(user['name']) + " nie posiada obecnie zadnych akcji."
    description += "\n💡 `!stonks`, `!fullstonks`, `!buy`, `!sell`"
    embed = Embed(title="Aktualne akcje - " + str(user['name']), description=str(description), color = color)
    if userAvatarURL:
        embed.set_thumbnail(url = userAvatarURL)
    else:
        embed.set_thumbnail(url = db.icon("STINKS_ICON"))
    embed.set_author(name = "Pizza One Hit AI", icon_url = db.icon("BOT_GIF_ADDRESS"))
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def generateUserStockPurchase(user, stock, msg = ""):
    color = Colour.dark_green()
    description = msg
    description += "\n💡 `!stonks`, `!fullstonks`, `!buy`, `!sell`"
    embed = Embed(title=str(user['name']) + " kupuje akcje " + str(stock['name']) + "!", description=str(description), color = color)
    embed.set_thumbnail(url = db.icon("PURCHASE_STOCK_ICON"))
    embed.set_author(name = "Pizza One Hit AI", icon_url = db.icon("BOT_GIF_ADDRESS"))
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def generateUserStockSale(user, stock, msg = ""):
    color = Colour.dark_red()
    description = msg
    description += "\n💡 `!stonks`, `!fullstonks`, `!buy`, `!sell`"
    embed = Embed(title=str(user['name']) + " sprzedaje akcje " + str(stock['name']) + "!", description=str(description), color = color)
    embed.set_thumbnail(url = db.icon("SELL_STOCK_ICON"))
    embed.set_author(name = "Pizza One Hit AI", icon_url = db.icon("BOT_GIF_ADDRESS"))
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

def generateUserStockCashout(user, msg = ""):
    color = Colour.dark_red()
    description = msg
    description += "\n💡 `!stonks`, `!fullstonks`, `!buy`, `!sell`"
    embed = Embed(title=str(user['name']) + " ma dosc! Sprzedaje wszystkie swoje akcje!", description=str(description), color = color)
    embed.set_thumbnail(url = db.icon("SELL_STOCK_ICON"))
    embed.set_author(name = "Pizza One Hit AI", icon_url = db.icon("BOT_GIF_ADDRESS"))
    embed.set_footer(text = "Sztuczna inteligencja na twoim discordzie!", icon_url = db.icon("PIZZA_ICON"))
    return embed

