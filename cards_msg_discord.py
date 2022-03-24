from time import sleep


from secrets import API_KEY, TOKEN
from leagueapi import  LolAPI
from discordapi import DiscordAPI
from cards import CardManager, SQUAD_PUUID
from card_counts import updateMessageData, getCardCountString, makeMessageData


discord_api = DiscordAPI(TOKEN)
CHANNEL_ID = '894438526580555817'
last_message_id = discord_api.getChannelMessages(CHANNEL_ID, {"limit": 1})[0]["id"]
makeMessageData(discord_api, CHANNEL_ID)

# manager to make the getCards call
man = CardManager(player_puuid=SQUAD_PUUID["Dahlin"])

def getLastNMatchIds(puuids: list, n_matches: int, api: LolAPI) -> set:
    match_ids = [api.getMatchIdList(puuid, n_matches)
                 for puuid in puuids]
    # flatten out list and turn into a set
    match_ids = set([match_id for sublist in match_ids
                     for match_id in sublist])
    return match_ids

lol_api = LolAPI(API_KEY, "americas")
old_matches = getLastNMatchIds(SQUAD_PUUID.values(), 10, lol_api)

def getCardsString(cards):
    cards.sort(key=lambda x: x[3], reverse=True)

    string = ''
    for card in cards:
        string += '{0} - {4} | **{1}** - {2}'.format(*card)
        if cards[1] == "The PvE Player":
            string += "Shoutout urgot!"
        string += '\n'
    return string

def getLeaderboardString(leaderboard):
    string = ''
    for stat in leaderboard:
        cardname = list(stat)[0]
        data = stat[cardname]
        string += '**{0}**: {1} with {2:.2f} as {3}'.format(cardname, data['playername'], data['statvalue'], data['playerchampion'])
        string += '\n'
    return string

def checkDiscordMessages(messages_json: list, keyword: str) -> bool:
    """checks if messages includes keyword"""
    messages = [msg["content"] for msg in messages_json]  # parse json

    if any(keyword in msg for msg in messages):
        return True

    return False

while True:
    try:
        # occasionally request errors, so just keep trying
        print("Checking for new matches")
        new_matches = getLastNMatchIds(SQUAD_PUUID.values(), 1, lol_api)

        if len(old_matches | new_matches) > len(old_matches):
            print("New match found")
            # first element of new_matches in case two different
            # matches finish at the same time
            match_id = list(new_matches - old_matches)[0]
            cards = man.getCards(match_id, 5)
            discord_api.sendMessage(CHANNEL_ID, {"content": getCardsString(cards)})
            # update old matches to include the latest match printed
            old_matches.add(match_id)

        print("Checking for keyword")
        discord_messages = discord_api.getChannelMessages(CHANNEL_ID,
                                                          {"after": last_message_id})

        if checkDiscordMessages(discord_messages, "!leaderboard"):
            print("Keyword match found")
            leaderboard = man.getLeaderboard()
            highscores = getLeaderboardString(leaderboard)
            discord_api.sendMessage(CHANNEL_ID, {"content": highscores})

        if checkDiscordMessages(discord_messages, "!lastgame"):
            last_matches = [lol_api.getMatchIdList(puuid, 1)
                for puuid in SQUAD_PUUID.values()]
            last_match = max(last_matches)
            cards = man.getCards(last_match[0], 5)
            discord_api.sendMessage(CHANNEL_ID, {"content": getCardsString(cards)})

        if checkDiscordMessages(discord_messages, "!enemyteam"):
            last_matches = [lol_api.getMatchIdList(puuid, 1)
                for puuid in SQUAD_PUUID.values()]
            last_match = max(last_matches)
            cards = man.getCards(last_match[0], 5, True)
            discord_api.sendMessage(CHANNEL_ID, {"content": getCardsString(cards)})

        if checkDiscordMessages(discord_messages, "!counts"):
            updateMessageData(discord_api, CHANNEL_ID)
            discord_api.sendMessage(CHANNEL_ID, {"content": getCardCountString()})

        if discord_messages:  # if list is not empty, update last  message
            last_message_id = discord_messages[0]["id"]  # first element is latest

    except Exception as e:
        print(e)
        pass

    sleep(30)
