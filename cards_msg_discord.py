from time import sleep


from secrets import API_KEY, TOKEN
from leagueapi import  LolAPI
from discordapi import DiscordAPI
from cards import CardManager, SQUAD_PUUID
from card_counts import updateMessageData, getCardCountString, makeMessageData
from card_data import CardData


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

def getCardsString(cards, streak, stagger):
    string = str(cards)
    streakString = getWinLossStreak(streak)
    string += streakString
    string += stagger
    return string

def calc_aram_death_timer(level: int) -> int:
    """calculates time (in ms) spent dead

    per https://leagueoflegends.fandom.com/wiki/Death
    """
    return (level * 2 + 4) * 1000

def find_overlaping_ranges(ranges: list[tuple], leeway: int = 0) -> list[tuple]:
    """merges ranges that overlap

    Mostly yoinked from https://stackoverflow.com/a/59378344

    Examples
    --------
    ranges = [(1, 50), (45, 47), (49, 70), (75, 85), (84, 88), (87, 92)]
    list(find_overlapping_ranges(ranges))
    [(1, 70), (75, 92)]

    ranges = [(1, 50), (51, 85), (84, 88), (87, 92)]
    print(list(find_overlapping_ranges(ranges, leeway=4)))
    [(1, 92)]
    """
    it = iter(ranges)
    try:
        curr_start, curr_stop = next(it)
    except StopIteration:
        return
    for start, stop in it:
        if curr_start <= start <= (curr_stop + leeway):
            curr_stop = max(curr_stop, stop)
        else:
            yield curr_start, curr_stop
            curr_start, curr_stop = start, stop
    yield curr_start, curr_stop

def getMaxStaggerStr(match_id: str, squad_puuids: list[str], api: LolAPI) -> str:
    """str for card output about how long we staggered for

    TODOs
    -----
    Akshan?
    Non-ARAM game modes?
    """
    match = api.getMatchInfo(match_id)
    matchType = match['info']['gameMode']
    if matchType != "ARAM":
        return ""

    match_timeline = api.getMatchTimeline(match_id)
    participants = match_timeline["info"]["participants"]
    participant_ids = [x["participantId"] for x in participants if x["puuid"] in squad_puuids]

    if min(participant_ids) > 5 and max(participant_ids) <= 10:
        good_team_side = [6, 7, 8, 9, 10]
    elif min(participant_ids) > 0 and max(participant_ids) <= 5:
        good_team_side = [1, 2, 3, 4, 5]
    else:
        raise RuntimeError("on separate sides?")

    lvl_by_player_id = {} # holder to keep track of current level

    death_data = []

    for frame in match_timeline["info"]["frames"]:
        for component in frame["events"]:
            if component["type"] == "CHAMPION_KILL":
                victim = component['victimId']
                if victim in good_team_side:
                    timestamp = component['timestamp']
                    victim_level = lvl_by_player_id[victim]
                    death_data.append((timestamp, timestamp + calc_aram_death_timer(victim_level)))

            if component["type"] == "LEVEL_UP":
                lvl_by_player_id[component["participantId"]] = component["level"]

    # leeway=5000 means that if someone has spawned withing 5 seconds of next
    # death still conts as a stagger
    overlapping_ranges = list(find_overlaping_ranges(death_data, leeway=5000))
    stagger_times = [x[1] - x[0] for x in overlapping_ranges if x not in death_data]
    res = f"Longest stagger {max(stagger_times)/1000:.0f}s"
    return res

def getWinLossStreak(streak):
    if streak > 0:
        return str(streak) + " win streak"
    elif streak < 0:
        return str(abs(streak)) + " loss streak"
    else:
        return ""

def updateWinLossStreak(isWin, streak):
    if streak > 0:
        if isWin:
            streak += 1
        else:
            streak = -1
    elif streak < 0:
        if isWin:
            streak = 1
        else:
            streak -= 1
    else:
        if isWin:
            streak = 1
        else:
            streak = -1
    return streak

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

streak = 0
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
            cardData = man.getCards(match_id, 5)
            stagger = getMaxStaggerStr(last_match[0], SQUAD_PUUID.values(), lol_api)
            streak = updateWinLossStreak(cardData.getIsWin(), streak)
            discord_api.sendMessage(CHANNEL_ID, {"content": getCardsString(cardData, streak, stagger)})
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
            stagger = getMaxStaggerStr(last_match[0], SQUAD_PUUID.values(), lol_api)
            cardData = man.getCards(last_match[0], 5)
            discord_api.sendMessage(CHANNEL_ID, {"content": getCardsString(cardData, streak, stagger)})

        if checkDiscordMessages(discord_messages, "!enemyteam"):
            last_matches = [lol_api.getMatchIdList(puuid, 1)
                for puuid in SQUAD_PUUID.values()]
            last_match = max(last_matches)
            cardData = man.getCards(last_match[0], 5, True)
            discord_api.sendMessage(CHANNEL_ID, {"content": getCardsString(cardData, streak, "")})

        if checkDiscordMessages(discord_messages, "!counts"):
            updateMessageData(discord_api, CHANNEL_ID)
            discord_api.sendMessage(CHANNEL_ID, {"content": getCardCountString()})

        if discord_messages:  # if list is not empty, update last  message
            last_message_id = discord_messages[0]["id"]  # first element is latest

    except Exception as e:
        print(e)
        pass

    sleep(30)
