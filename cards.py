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
            pData['totalDamageDealt'] = p['totalDamageDealt']
            pData['totalDamageDealtToChampions'] = p['totalDamageDealtToChampions']
            pData['kills'] = p['kills']
            pData['deaths'] = p['deaths']
            pData['assists'] = p['assists']
            pData['win'] = p['win']
            pData['damageSelfMitigated'] = p['damageSelfMitigated']
            pData['physicalDamageDealtToChampions'] = p['physicalDamageDealtToChampions']
            pData['magicDamageDealtToChampions'] = p['magicDamageDealtToChampions']
            pData['trueDamageDealtToChampions'] = p['trueDamageDealtToChampions']
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

        Description: 
        Get the player with the most Dark Harvest stacks.
        Scale priority based off of difference between stack winner and second place
        Return priority 0 if no winner

        return a list with format:
            [0] - summoner name
            [1] - card name
            [2] - card text
            [3] - card priority
        """

        cardName = "Stack Champion"
        maxStacks = 0
        secondPlace = 0
        winner = None
        stackingTeam = self.goodTeamStats if getCardForGoodTeam else self.badTeamStats
        for stacker in stackingTeam:
            if stacker['DH Stacks'] is not None and stacker['DH Stacks'] >= maxStacks and stacker['puuid'] in homies_puuid:
                if secondPlace == 0:
                    secondPlace = stacker['DH Stacks']
                if stacker['DH Stacks'] == maxStacks:
                    secondPlace = stacker['DH Stacks']
                    if stacker['totalDamageDealtToChampions'] < winner['totalDamageDealtToChampions']:
                        continue

                winner = stacker
                maxStacks = stacker['DH Stacks']

            if stacker['DH Stacks'] is not None and stacker['DH Stacks'] > secondPlace and stacker['DH Stacks'] < maxStacks:
                secondPlace = stacker['DH Stacks']

        dif = maxStacks - secondPlace
        scaling = max(1, min(3, dif / max(10, secondPlace)))
            
        if winner is not None:
            ret = []
            ret.append(winner['summonerName'])
            ret.append(cardName)
            ret.append(str(winner['DH Stacks']) + " stacks. (+" + str(dif) + ")")
            ret.append(basePriority * scaling)
            return ret
        else:
            return ["", "", "", 0]

    def getTankmasterCard(self, basePriority, getCardForGoodTeam = True):
        """
        basePriority : initial priority value to be scaled by card data
        getCardForGoodTeam : true if get card for homies team, false for enemy team

        Description: 
        Get the player with the highest self mitigated damage
        Scale priority based off of winners percent of teams mitigated damage
        Return priority 0 if winners self mitigated damage percentage is less than 30% of the teams self mitigated damage

        return a list with format:
            [0] - summoner name
            [1] - card name
            [2] - card text
            [3] - card priority 
        """
            
        cardName = "IM THE TANK"
        maxMitigated = 0
        teamMitigated = 0
        winner = None
        teamData = self.goodTeamStats if getCardForGoodTeam else self.badTeamStats
        for tonk in teamData:
            pMitigatedDamage = tonk['damageSelfMitigated']
            teamMitigated += pMitigatedDamage
            if pMitigatedDamage > maxMitigated:
                maxMitigated = pMitigatedDamage
                winner = tonk
            
        percentMitigated = (maxMitigated / teamMitigated) * 100
        scaling = 0 if percentMitigated < 30 else max(1, min(3, percentMitigated / 20))
        if winner is not None:
            ret = []
            ret.append(winner['summonerName'])
            ret.append(cardName)
            ret.append(f'{maxMitigated} mitigated damage. {percentMitigated:.2f}% of teams total mitigated damage')
            ret.append(basePriority * scaling)
            return ret
        else:
            return ["", "", "", 0]

    def getTrueDamageCard(self, basePriority, getCardForGoodTeam = True):
        """
        basePriority : initial priority value to be scaled by card data
        getCardForGoodTeam : true if get card for homies team, false for enemy team

        Description: 
        Get the player with the highest percentage of their damage dealt as true damage
        Scale priority based off of winners percent of true damage dealt
        Return priority 0 if winners percentage of true damage dealt is less than 25%

        return a list with format:
            [0] - summoner name
            [1] - card name
            [2] - card text
            [3] - card priority
        """

        cardName = "No counterplay"
        highestPercent = 0
        winner = None
        teamData = self.goodTeamStats if getCardForGoodTeam else self.badTeamStats
        for dmg in teamData:
            totalDamage = dmg['magicDamageDealtToChampions'] + dmg['physicalDamageDealtToChampions'] + dmg['trueDamageDealtToChampions']
            trueDamage = dmg['trueDamageDealtToChampions']
            percentTrue = trueDamage / totalDamage
            if(percentTrue > highestPercent):
                highestPercent = percentTrue
                winner = dmg

        highestPercent *= 100
        scaling = 0 if highestPercent < 25 else min(1, max(3, highestPercent / 20))
        if winner is not None:
            ret = []
            ret.append(winner['summonerName'])
            ret.append(cardName)
            ret.append(f'{highestPercent:.2f}% of damage dealt as true damage')
            ret.append(basePriority * scaling)
            return ret
        else:
            return ["", "", "", 0]
        
    def getPvECard(self, basePriority, getCardForGoodTeam = True):
        """
        basePriority : initial priority value to be scaled by card data
        getCardForGoodTeam : true if get card for homies team, false for enemy team

        Description: 
        Get the player with the highest percentage of damage dealt to non-champions
        Scale priority based off of winners percent of damage dealt to non-champions
        Return priority 0 if winners percentage of non-champion damage is less than 30%

        return a list with format:
            [0] - summoner name
            [1] - card name
            [2] - card text
            [3] - card priority
        """
        cardName = "The PvE Player"
        lowestPercent = 1
        winner = None
        teamData = self.goodTeamStats if getCardForGoodTeam else self.badTeamStats
        for dmg in teamData:
            percentage = dmg['totalDamageDealtToChampions'] / dmg['totalDamageDealt']
            if percentage < lowestPercent:
                lowestPercent = percentage
                winner = dmg
        
        lowestPercent *= 100
        scaling = 0 if lowestPercent > 30 else min(1, max(3, 30 / lowestPercent))
        if winner is not None:
            ret = []
            ret.append(winner['summonerName'])
            ret.append(cardName)
            ret.append(f'Only {lowestPercent:.2f}% of total damage dealt to champions')
            ret.append(basePriority * scaling)
            return ret
        else:
            return ["", "", "", 0]


puuid = api.getPUUID('Kabib Nurmagabob', 'NA1')
match_id = api.getMatchIdList(puuid, 3)
match = api.getMatchInfo(match_id[0])
mCard = Card(match)
mCard.parseJson()
mCard.splitTeamData()
print(mCard.getStackCard(5))
print(mCard.getTankmasterCard(3))
print(mCard.getTrueDamageCard(2))
print(mCard.getPvECard(3))