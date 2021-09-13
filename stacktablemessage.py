from discordapi import DiscordAPI
from leagueapi import LolAPI

from secrets import TOKEN, API_KEY

discordapi = DiscordAPI(TOKEN)
lolapi = LolAPI(API_KEY, 'americas')

puuid = lolapi.getPUUID('Dahlin', 'NA1')
matches = lolapi.getMatchIdList(puuid, 1)
match_data = lolapi.getMatchInfo(matches[0])

def makeChampionStackTable(match_data: dict) -> str:
    team1 = []
    team2 = []
    
    def getStacks(participant_data: dict) -> int:
        if participant_data['perks']['styles'][0]['selections'][0]['perk'] == 8128:
            return participant_data['perks']['styles'][0]['selections'][0]['var2']
        else:
            return 0

    for player in match_data['info']['participants']:
        #line = [player['championName'], player['summonerName'],
        #        getStacks(player), player['totalDamageDealtToChampions'],
        #        player['kills'], player['deaths'], player['assists']]
        #fmt_line = '{:29}{:25}\t{}\t{}\t{}\\{}\\{}'.format(*line)
        fmt_line = str(player['championName']).ljust(20)\
                + str(player['summonerName']).ljust(20)\
                + str(getStacks(player)).ljust(3)\
                + f'{player["totalDamageDealtToChampions"]:,}'.ljust(8)\
                + f'{player["kills"]}/{player["deaths"]}/{player["assists"]}'

        if player['teamId'] == 100:
            team1.append(fmt_line)
        else:
            team2.append(fmt_line)
    
    out_str = ''
    out_str += '\n__Team 1__\n'
    out_str += '\n'.join(team1)
    out_str += '\n__Team 2__\n'
    out_str += '\n'.join(team2)

    return out_str

body = {
        'content': makeChampionStackTable(match_data)
    }

channel_id = '886455871603892234'
discordapi.sendMessage(channel_id, body)
