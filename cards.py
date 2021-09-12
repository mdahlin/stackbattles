from leagueapi import LolAPI
from secrets import API_KEY

api = LolAPI(API_KEY, 'americas')

homies = ['Mahat Magandalf', 'Dahlin', '4th Migo', 'Kabib Nurmagabob', 'Lacr3188', 'Eminems Sweater', 'GROBGOBGLOBGROD']
homies_puuid = [api.getPUUID(homie, 'NA1') for homie in homies]

def getStackCard(matchJson, basePriority):
    """return a list with format:
        [0] - summoner name
        [1] - card name
        [2] - card text
        [3] - card priority """

    cardName = "Stack Champion"
    playerMetrics = []

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

    max_stacks = 0
    second_place = 0
    winner = None
    for stacker in playerMetrics:
        if stacker['DH Stacks'] is not None and stacker['DH Stacks'] >= max_stacks and stacker['puuid'] in homies_puuid:
            if stacker['DH Stacks'] == max_stacks:
                second_place = stacker['DH Stacks']
                if stacker['totalDamageDealtToChampions'] < winner['totalDamageDealtToChampions']:
                    continue

            winner = stacker
            max_stacks = stacker['DH Stacks']

        if stacker['DH Stacks'] is not None and stacker['DH Stacks'] > second_place and stacker['DH Stacks'] < max_stacks:
            second_place = stacker['DH Stacks']

    dif = max_stacks - second_place
    scaling = max(1, min(3, dif / max(10, second_place)))
        
    if winner is not None:
        ret = []
        ret.append(winner['summonerName'])
        ret.append(cardName)
        ret.append(str(winner['DH Stacks']) + " stacks. (+" + str(dif) + ")")
        ret.append(basePriority * scaling)
        return ret
    else:
        return ["", "", "", 1]
    

puuid = api.getPUUID('Kabib Nurmagabob', 'NA1')
match_id = api.getMatchIdList(puuid, 1)
match = api.getMatchInfo(match_id[0])
result = getStackCard(match, 5)
print(result)