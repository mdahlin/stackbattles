from leagueapi import LolAPI
from secrets import API_KEY

def getStacks(matchJson):
    """specific match info"""
    playerMetrics = []
    gameMode = matchJson['info']['gameMode']

    for p in matchJson['info']['participants']:
        stats = {}
        stats['summonerName'] = p['summonerName']
        stats['championName'] = p['championName']
        stats['totalDamageDealtToChampions'] = p['totalDamageDealtToChampions']
        stats['kills'] = p['kills']
        stats['deaths'] = p['deaths']
        stats['assists'] = p['assists']
        stats['win'] = p['win']

        if p['perks']['styles'][0]['selections'][0]['perk'] == 8128:
            stats['DH Damage'] = p['perks']['styles'][0]['selections'][0]['var1']
            stats['DH Stacks'] = p['perks']['styles'][0]['selections'][0]['var2']
        else:
            stats['DH Stacks'] = None
            stats['DH Damage'] = None

        playerMetrics.append(stats)
    return playerMetrics


api = LolAPI(API_KEY, 'americas')

puuid = api.getPUUID('Mahat Magandalf', 'NA1')
matches = api.getMatchIdList(puuid, 1)

match = api.getMatchInfo(matches[0])

stacksInfo = getStacks(match)

for i in stacksInfo:
    print(i)
