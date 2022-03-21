#' This script will create a picle object containing all of the messages
#' from the Squad Memes cards text channel. It also contains the 
#' functions to produce the message that will be sent by discord
#' with the counts of each card member for every card

import pickle
import re
from os.path import exists
from functools import reduce
from collections import Counter

def makeMessageData(api, channel_id: str) -> None:
    if exists("message_data.p"):
        pass
    else:
        # create message_data.p
        # get all of the messages from the channel
        messages = api.getChannelMessages(channel_id, {"limit": 1}, False).json()
        i = 100
        # get historical messages 100 at a time
        while i >= 100:
            res = api.getChannelMessages(
                    channel_id,
                    {"before": messages[-1]["id"], "limit": 100},
                    False)

            # could look at headers to sleep after rate limit excedence
            # but this should work with way less effort
            if res.status_code == 200:
                new_messages = res.json()
                i = len(new_messages)
                messages += new_messages

        pickle.dump(messages, open("message_data.p", "wb"))
        print(f"message_data.p created with {len(messages)} messages")
    
def updateMessageData(api, channel_id: str) -> None:
    messages = pickle.load( open("message_data.p", "rb") )
    # update messages list
    messages_len = len(messages)
    i = 100
    while i >= 100: 
        res = api.getChannelMessages(channel_id,
                                  {"after": messages[0]["id"], "limit": 100},
                                  False)

        # could look at headers to sleep after rate limit excedence
        # but this should work with way less effort
        if res.status_code == 200:
            new_messages = res.json()
            i = len(new_messages)
            messages = new_messages + messages
    pickle.dump(messages, open("message_data.p", "wb"))
    print(f"Udpated and added {len(messages) - messages_len} new messages")


def parseCardMessage(card: str, pattern, names) -> dict:
    parsed = {}
    for line in card.splitlines():
       name, card_name = pattern.match(line).groups()

       name = names.get(name, "Random")
       if name != "Random":
           parsed[card_name] = [name]

    return parsed

def getCardCountString():
    messages = pickle.load( open("message_data.p", "rb") )
    CARD_PATTERN = re.compile("(.+) - .+ \| \*\*(.+)\*\*.*")
    cards = set()  # set to check for duplicates (could be a list)

    SQUAD_NAMES = {
            "Dahlin": "Dahlin",
            "Julia Roberts": "Bentley",
            "Poop in Jort": "Bentley",
            "Eminems Sweater": "Gerry",
            "Kabib Nurmagabob": "Fey",
            "Khamzat ChiMama": "Fey",
            "Lacr3188": "Colt",
            "Mahat Magandalf": "Micky",
            "TheScaryDoor123": "Steve",
            "Frumpy Dumpster": "Sam",
            "GR0BG0BGL0BGR0D": "Sam",
            "JTD and FTH": "Sam",
            "PHpremiumm": "Calvin"
            }
    parsed_cards = []
    for msg in messages:
        card = msg["content"]
        # ignore non-card messages
        if CARD_PATTERN.match(card):
            # ignore duplicates
            if card not in cards:
                cards.add(card)
                parsed_cards.append(parseCardMessage(card, CARD_PATTERN, SQUAD_NAMES))

    combined_cards = reduce(lambda dict1, dict2: {k: dict1.get(k, []) + dict2.get(k, [])
                                                  for k in dict1.keys() | dict2.keys()},
                            parsed_cards)

    discord_message = ""
    for key, value in combined_cards.items():
        discord_message +=\
                f"**{key}** {', '.join([f'{n}: {c}' for n, c in Counter(value).most_common()])}\n"

    return discord_message

