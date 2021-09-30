from leagueapi import LolAPI
from secrets import API_KEY

class Card:
    """Base class for card"""

    def __init__(self, matchJson, homies):
        self.matchJson = matchJson
        self.homies = homies
        self.gameStats = []
        self.goodTeamStats = []
        self.badTeamStats = []
    
    def parseJson(self):
        """
        Description: 
        Parse Json data from API. Populate gameStats
        """
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
            pData['timeCCingOthers'] = p['timeCCingOthers']

            if p['perks']['styles'][0]['selections'][0]['perk'] == 8128:
                pData['DH Damage'] = p['perks']['styles'][0]['selections'][0]['var1']
                pData['DH Stacks'] = p['perks']['styles'][0]['selections'][0]['var2']
            else:
                pData['DH Stacks'] = None
                pData['DH Damage'] = None 
            self.gameStats.append(pData)

    def splitTeamData(self):
        """
        Description: 
        Split up game data into teams. Populate goodTeamStats and badTeamStats
        """
        goodTeamId = 100
        for p in self.gameStats:
            if p['puuid'] in self.homies:
                goodTeamId = p['teamId']
                break
    
        for p in self.gameStats:
            if p['teamId'] == goodTeamId:
                self.goodTeamStats.append(p)
            else:
                self.badTeamStats.append(p)

    def getNPlaceStatWinner(self, statName, N, isGoodTeam):
        """
        statName : string name of statistic of interest
        N : Position of desired result in increasing order. 0 is first place, 1 is second place etc.
        isGoodTeam : TRUE for use good team data. False for bad guys 

        Description
        Return the player that has the N'th highest value for the given statistic

        return a list with format:
            [0] - player data
            [1] - value of players statistic of interest
            [2] - player statistic as a percentage of the teams statistic
        """
        winner = None
        team = self.goodTeamStats if isGoodTeam else self.badTeamStats
        teamStatTotal = 0
        data = []
        for player in team:
            playerStat = player[str(statName)]
            data.append((player['summonerName'], playerStat))
            if playerStat is not None:
                teamStatTotal += playerStat

        relevantData = [i for i in data if i[1] is not None]

        if len(relevantData) <= N:
            ret = [None, 0, 0]
            return ret

        relevantData.sort(key = lambda x: x[1], reverse = True)
        winner = relevantData[N][0]
        winnerStat = relevantData[N][1]

        for player in team:
            if player['summonerName'] == winner:
                winner = player

        ratio = 0 if teamStatTotal == 0 else winnerStat / teamStatTotal
                
        ret = []
        ret.append(winner)
        ret.append(winnerStat)
        ret.append(ratio)
        return ret


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
            [4] - summoner champion
        """

        cardName = "Stack Champion"
        statName = 'DH Stacks'

        winner = self.getNPlaceStatWinner(statName, 0, getCardForGoodTeam)
        second = self.getNPlaceStatWinner(statName, 1, getCardForGoodTeam)
  
        if winner[0] is not None:
            dif = winner[1] - second[1]
            scaling = max(1, min(3, dif / max(10, winner[1]))) if winner[1] > 0 else 0

            ret = []
            ret.append(winner[0]['summonerName'])
            ret.append(cardName)
            ret.append(str(winner[1]) + " stacks. (+" + str(dif) + ")")
            ret.append(basePriority * scaling)
            ret.append(winner[0]['championName'])
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
            [4] - summoner champion
        """
            
        cardName = "IM THE TANK"
        winner = self.getNPlaceStatWinner('damageSelfMitigated', 0, getCardForGoodTeam)
        
        if winner[0] is not None:
            percentMitigated = winner[2] * 100
            scaling = 0 if percentMitigated < 30 else max(1, min(3, percentMitigated / 15))

            ret = []
            ret.append(winner[0]['summonerName'])
            ret.append(cardName)
            ret.append(f'{winner[1]} mitigated damage. {percentMitigated:.2f}% of teams total mitigated damage')
            ret.append(basePriority * scaling)
            ret.append(winner[0]['championName'])
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
            [4] - summoner champion
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
            ret.append(winner['championName'])
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
            [4] - summoner champion
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
            ret.append(winner['championName'])
            return ret
        else:
            return ["", "", "", 0]

    def getFeedingWeenieCard(self, basePriority, getCardForGoodTeam = True):
        """
        basePriority : initial priority value to be scaled by card data
        getCardForGoodTeam : true if get card for homies team, false for enemy team

        Description: 
        10 more deaths than kills

        return a list with format:
            [0] - summoner name
            [1] - card name
            [2] - card text
            [3] - card priority
            [4] - summoner champion
        """
        cardName = "The Feeding Weenie"
        maxDeathDiff = 0
        winner = None
        teamData = self.goodTeamStats if getCardForGoodTeam else self.badTeamStats
        for noob in teamData:
            pDeathDiff = noob['deaths'] - noob['kills']
            if pDeathDiff > maxDeathDiff:
                maxDeathDiff = pDeathDiff
                winner = noob
            
        scaling = 0 if maxDeathDiff < 10 else max(1, min(3, maxDeathDiff / 5))
        if winner is not None:
            ret = []
            deaths = winner['deaths']
            kills = winner['kills']
            ret.append(winner['summonerName'])
            ret.append(cardName)
            ret.append(f'{deaths} deaths all for only {kills} kills. WEENIE')
            ret.append(basePriority * scaling)
            ret.append(winner['championName'])
            return ret
        else:
            return ["", "", "", 0]

    def getCCLordCard(self, basePriority, getCardForGoodTeam = True):
        """
        basePriority : initial priority value to be scaled by card data
        getCardForGoodTeam : true if get card for homies team, false for enemy team

        Description: 
        10 more deaths than kills

        return a list with format:
            [0] - summoner name
            [1] - card name
            [2] - card text
            [3] - card priority
            [4] - summoner champion
        """
        cardName = "The CC Lord"
        statName = "timeCCingOthers"
        winner = self.getNPlaceStatWinner(statName, 0, getCardForGoodTeam)
        if winner[0] is not None:
            ccScore = winner[1]
            scaling = 0 if ccScore < 50 else max(1, min(4, ccScore / 30))

            ret = []
            ret.append(winner[0]['summonerName'])
            ret.append(cardName)
            ret.append(f'CC\'ed enemies for {ccScore} seconds')
            ret.append(basePriority * scaling)
            ret.append(winner[0]['championName'])
            return ret
        else:
            return ["", "", "", 0]


class CardManager:
    """
    Base Class for card manager
    Initialize with player name for cards
    Call getCards
    """
    def __init__(self, player = "Kabib Nurmagabob", region = "NA1", apiKey = API_KEY):
        """
        Initialize with desired player, region, and if possible, API Key
        """
        self.player = player
        self.region = region
        self.key = apiKey

    def getCards(self, numCards = 4):
        api = LolAPI(self.key, 'americas')
        homies = ['Mahat Magandalf', 'Dahlin', '4th Migo', 'Kabib Nurmagabob', 'Lacr3188', 'Eminems Sweater', 'GROBGOBGLOBGROD']
        homies_puuid = [api.getPUUID(homie, self.region) for homie in homies]
        puuid = api.getPUUID(self.player, self.region)
        match_id = api.getMatchIdList(puuid, 2)
        match = api.getMatchInfo(match_id[1])
        mCard = Card(match, homies_puuid)
        mCard.parseJson()
        mCard.splitTeamData()
        cardStack = []
        card = mCard.getStackCard(5)
        cardStack.append((card[3], card))
        card = mCard.getTankmasterCard(3)
        cardStack.append((card[3], card))
        card = mCard.getTrueDamageCard(2)
        cardStack.append((card[3], card))
        card = mCard.getPvECard(3)
        cardStack.append((card[3], card))
        card = mCard.getFeedingWeenieCard(3)
        cardStack.append((card[3], card))
        card = mCard.getCCLordCard(3)
        cardStack.append((card[3], card))

        if len(cardStack) <= numCards:
            return [x[1] for x in cardStack]
        else:
            cardStack.sort(key = lambda x: x[0], reverse = True)
            return cardStack[0:numCards]

man = CardManager()
ret = man.getCards(8)
print(ret)