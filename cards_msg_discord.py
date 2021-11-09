from time import sleep


from secrets import API_KEY, TOKEN
from cards import CardManager, SQUAD_PUUID
from discordapi import DiscordAPI

man = CardManager(player_puuid=SQUAD_PUUID["Fey"])
discord_api = DiscordAPI(TOKEN)
# initialize
CHANNEL_ID = '894438526580555817'
old_matches = man.getLastNMatchIds(10)
last_message_id = discord_api.getChannelMessages(CHANNEL_ID, {"limit": 1})[0]["id"]

def getCardsString(cards):
    cards.sort(key=lambda x: x[3], reverse=True)

    string = ''
    for card in cards:
        string += '{0} - {4} | **{1}** - {2}'.format(*card)
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
        print("Checking for new matches")
        match_id, cards = man.getCards(5)

        if match_id not in old_matches:
            print("New match found")
            # occasionally request errors, so just keep trying
            discord_api.sendMessage(CHANNEL_ID, {"content": getCardsString(cards)})
            old_matches.append(match_id)

        print("Checking for keyword")
        discord_messages = discord_api.getChannelMessages(CHANNEL_ID,
                                                          {"after": last_message_id})

        if checkDiscordMessages(discord_messages, "!leaderboard"):
            print("Keyword match found")
            leaderboard = man.getLeaderboard()
            highscores = getLeaderboardString(leaderboard)
            discord_api.sendMessage(CHANNEL_ID, {"content": highscores})

        if discord_messages:  # if list is not empty, update last  message
            last_message_id = discord_messages[0]["id"]  # first element is latest

    except Exception as e:
        print(e)
        pass

    sleep(30)
