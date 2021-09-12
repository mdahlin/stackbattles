from leagueapi import LolAPI
from secrets import API_KEY

api = LolAPI(API_KEY, 'americas')

homies = ['Mahat Magandalf', 'Dahlin', '4th Migo', 'Kabib Nurmagabob', 'Lacr3188', 'Eminems Sweater', 'GROBGOBGLOBGROD']
homies_puuid = [api.getPUUID(homie, 'NA1') for homie in homies]

class Card:
    """Base class for card"""

    def __init__(self, matchJson):
        self.matchJson = matchJson
        self.gameStats = []
        self.goodTeamStats = []
        self.badTeamStats = []
    
    def parseJson(self):
        for p in self.matchJson['info']['participants']:
            pData = {}
            pData['puuid'] = p['puuid']
            pData['summonerName'] = p['summonerName']
            pData['championName'] = p['championName']
            pData['totalDamageDealtToChampions'] = p['totalDamageDealtToChampions']
            pData['kills'] = p['kills']
            pData['deaths'] = p['deaths']
            pData['assists'] = p['assists']
            pData['win'] = p['win']
            pData['damageSelfMitigated'] = p['damageSelfMitigated']
            pData['teamId'] = p['teamId']


            if p['perks']['styles'][0]['selections'][0]['perk'] == 8128:
                pData['DH Damage'] = p['perks']['styles'][0]['selections'][0]['var1']
                pData['DH Stacks'] = p['perks']['styles'][0]['selections'][0]['var2']
            else:
                pData['DH Stacks'] = None
                pData['DH Damage'] = None 
            self.gameStats.append(pData)

    def splitTeamData(self):
        goodTeamId = 100
        for p in self.gameStats:
            if p['puuid'] in homies_puuid:
                goodTeamId = p['teamId']
                break
    
        for p in self.gameStats:
            if p['teamId'] == goodTeamId:
                self.goodTeamStats.append(p)
            else:
                self.badTeamStats.append(p)
            

        

    def getStackCard(self, basePriority, getCardForGoodTeam = True):
        """
        basePriority : initial priority value to be scaled by card data
        getCardForGoodTeam : true if get card for homies team, false for enemy team

        return a list with format:
            [0] - summoner name
            [1] - card name
            [2] - card text
            [3] - card priority """

        cardName = "Stack Champion"
        max_stacks = 0
        second_place = 0
        winner = None
        stackingTeam = self.goodTeamStats if getCardForGoodTeam else self.badTeamStats
        for stacker in stackingTeam:
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

    def getTankmasterCard(self, basePriority, getGoodTeamStats = True):
        """return a list with format:
            [0] - summoner name
            [1] - card name
            [2] - card text
            [3] - card priority """
            
        cardName = "IM THE TANK"
        max_mitigated = 0
        team_mitigated = 0
        winner = None
        teamData = self.goodTeamStats if getGoodTeamStats else self.badTeamStats
        for tonk in teamData:
            pMitigatedDamage = tonk['damageSelfMitigated']
            team_mitigated += pMitigatedDamage
            if pMitigatedDamage > max_mitigated:
                max_mitigated = pMitigatedDamage
                winner = tonk
            
        percentMitigated = (max_mitigated / team_mitigated) * 100
        scaling = max(1, min(3, percentMitigated / .25))
        if winner is not None:
            ret = []
            ret.append(winner['summonerName'])
            ret.append(cardName)
            ret.append(f'{max_mitigated} mitigated damage. {percentMitigated:.2f}% of teams total mitigated damage')
            ret.append(basePriority * scaling)
            return ret
        else:
            return ["", "", "", 1]
            

puuid = api.getPUUID('Kabib Nurmagabob', 'NA1')
match_id = api.getMatchIdList(puuid, 3)
match = api.getMatchInfo(match_id[1])
mCard = Card(match)
mCard.parseJson()
mCard.splitTeamData()
print(mCard.getStackCard(5))
print(mCard.getTankmasterCard(3))