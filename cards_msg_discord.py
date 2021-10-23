from time import sleep


from secrets import API_KEY, TOKEN
from cards import CardManager
from discordapi import DiscordAPI

man = CardManager(player='Dahlin')
discord_api = DiscordAPI(TOKEN)
# initialize
last_match_id = man.getCards(5)[0]

def getCardsString(cards):
    cards.sort(key=lambda x: x[0], reverse=True)

    string = ''
    for card in cards:
        string += '{0} - {4} | **{1}** - {2}'.format(*card[1])
        string += '\n'
    return string

while True:
    try:
        print("Checking for new matches")
        match_id, cards = man.getCards(5)

        if match_id != last_match_id:
            print("New match found")
            # occasionally request errors, so just keep trying
            discord_api.sendMessage('894438526580555817', 
                    {"content": getCardsString(cards)})

            last_match_id = match_id
    except Exception as e:
        print(e)
        pass

    sleep(30)
