from leagueapi import LolAPI
from secrets import API_KEY

api = LolAPI(API_KEY, 'americas')

homies = ['Mahat Magandalf', 'Dahlin', '4th Migo', 'Kabib Nurmagabob', 'Lacr3188', 'Eminems Sweater', 'GROBGOBGLOBGROD']
homies_puuid = [api.getPUUID(homie, 'NA1') for homie in homies]

def getStacks(matchJson):
    """specific match info"""
    playerMetrics = []
    gameMode = matchJson['info']['gameMode']

    for p in matchJson['info']['participants']:
        stats = {}
        stats['puuid'] = p['puuid']
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


puuid = api.getPUUID('Mahat Magandalf', 'NA1')
match_ids = api.getMatchIdList(puuid, 100)

winner = None
for match_id in match_ids:
    match = api.getMatchInfo(match_id)

    gameMode = match['info']['gameMode']

    if gameMode != 'ARAM':
        continue

    stacksInfo = getStacks(match)

    max_stacks = 0
    for stacker in stacksInfo:
        if stacker['DH Stacks'] is not None and stacker['DH Stacks'] >= max_stacks and stacker['puuid'] in homies_puuid:
            if stacker['DH Stacks'] == max_stacks:
                if stacker['totalDamageDealtToChampions'] < winner['totalDamageDealtToChampions']:
                    continue

            winner = stacker
            max_stacks = stacker['DH Stacks']

    break


print(winner)
