from re import match
from leagueapi import LolAPI
from secrets import API_KEY

NUM_CARDS = 12 #pls update if adding cards

class Card:
    """
    Base class for card
    Note: ALL CARD FUNCTIONS MUST INCLUDE getCard AS THE FIRST WORDS OF THE FUNCTION
    """

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
            pData['goldEarned'] = p['goldEarned']
            pData['largestCriticalStrike'] = p['largestCriticalStrike']
            pData['damageDealtToBuildings'] = p['damageDealtToBuildings']
            pData['damageDealtToTurrets'] = p['damageDealtToTurrets']
            pData['totalMinionsKilled'] = p['totalMinionsKilled']
            pData['timePlayed'] = p['timePlayed']

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


    def getCardStack(self, basePriority, getCardForGoodTeam = True):
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
            if dif == 0:
                if winner[0]['totalDamageDealtToChampions'] < second[0]['totalDamageDealtToChampions']:
                    t = winner
                    winner = second
                    second = t
                    
            scaling = max(1, min(3, dif / max(10, winner[1]))) if winner[1] > 0 else 0
            if self.matchJson['info']['gameMode'] == 'ARAM':        #always show stack card in aram
                scaling = 100

            ret = []
            ret.append(winner[0]['summonerName'])
            ret.append(cardName)
            ret.append(str(winner[1]) + " stacks. (+" + str(dif) + ")")
            ret.append(basePriority * scaling)
            ret.append(winner[0]['championName'])
            return ret
        else:
            return ["", "", "", 0]

    def getCardTankmaster(self, basePriority, getCardForGoodTeam = True):
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

    def getCardTrueDamage(self, basePriority, getCardForGoodTeam = True):
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
        
    def getCardPvE(self, basePriority, getCardForGoodTeam = True):
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
        scaling = 0 if lowestPercent > 25 else min(1, max(3, 25 / lowestPercent))
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

    def getCardFeedingWeenie(self, basePriority, getCardForGoodTeam = True):
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

    def getCardCCLord(self, basePriority, getCardForGoodTeam = True):
        """
        basePriority : initial priority value to be scaled by card data
        getCardForGoodTeam : true if get card for homies team, false for enemy team

        Description: 
        Highest CC score

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

    def getCardMoneySpender(self, basePriority, getCardForGoodTeam = True):
        """
        basePriority : initial priority value to be scaled by card data
        getCardForGoodTeam : true if get card for homies team, false for enemy team

        Description: 
        Most money

        return a list with format:
            [0] - summoner name
            [1] - card name
            [2] - card text
            [3] - card priority
            [4] - summoner champion
        """
        cardName = "Big Money"
        statName = "goldEarned"
        winner = self.getNPlaceStatWinner(statName, 0, getCardForGoodTeam)
        if winner[0] is not None:
            goldEarnedPercent = winner[2]*100
            scaling = 0 if goldEarnedPercent < 25 else max(1, min(4, goldEarnedPercent / 20))

            ret = []
            ret.append(winner[0]['summonerName'])
            ret.append(cardName)
            ret.append(f'Earned {goldEarnedPercent:.2f}% of the teams gold')
            ret.append(basePriority * scaling)
            ret.append(winner[0]['championName'])
            return ret
        else:
            return ["", "", "", 0]

    def getCardBigDeeps(self, basePriority, getCardForGoodTeam = True):
        """
        basePriority : initial priority value to be scaled by card data
        getCardForGoodTeam : true if get card for homies team, false for enemy team

        Description: 
        Most damage

        return a list with format:
            [0] - summoner name
            [1] - card name
            [2] - card text
            [3] - card priority
            [4] - summoner champion
        """
        cardName = "Big Deeps"
        statName = "totalDamageDealtToChampions"
        winner = self.getNPlaceStatWinner(statName, 0, getCardForGoodTeam)
        if winner[0] is not None:
            damagePercent = winner[2]*100
            scaling = 0 if damagePercent < 25 else max(1, min(4, damagePercent / 20))

            ret = []
            ret.append(winner[0]['summonerName'])
            ret.append(cardName)
            ret.append(f'Dealt {damagePercent:.2f}% of the teams damage')
            ret.append(basePriority * scaling)
            ret.append(winner[0]['championName'])
            return ret
        else:
            return ["", "", "", 0]


    def getCardBigCrit(self, basePriority, getCardForGoodTeam = True):
        """
        basePriority : initial priority value to be scaled by card data
        getCardForGoodTeam : true if get card for homies team, false for enemy team

        Description: 
        Largest critical strike

        return a list with format:
            [0] - summoner name
            [1] - card name
            [2] - card text
            [3] - card priority
            [4] - summoner champion
        """
        cardName = "Crit King"
        statName = "largestCriticalStrike"
        winner = self.getNPlaceStatWinner(statName, 0, getCardForGoodTeam)
        if winner[0] is not None:
            biggestCrit = winner[1]
            scaling = 0 if biggestCrit < 1200 else max(1, min(4, biggestCrit / 800))

            ret = []
            ret.append(winner[0]['summonerName'])
            ret.append(cardName)
            ret.append(f'Biggest crit: {biggestCrit}')
            ret.append(basePriority * scaling)
            ret.append(winner[0]['championName'])
            return ret
        else:
            return ["", "", "", 0]


    def getCardObjectivePlayer(self, basePriority, getCardForGoodTeam = True):
        """
        basePriority : initial priority value to be scaled by card data
        getCardForGoodTeam : true if get card for homies team, false for enemy team

        Description: 
        Most damage to towers / inhibs

        return a list with format:
            [0] - summoner name
            [1] - card name
            [2] - card text
            [3] - card priority
            [4] - summoner champion
        """
        cardName = "Tower Toppler"
        maxBuildingDamage = 0
        teamBuildingDamage = 0
        winner = None
        teamData = self.goodTeamStats if getCardForGoodTeam else self.badTeamStats
        for player in teamData:
            pBuildingDamage = player['damageDealtToBuildings'] + player['damageDealtToTurrets']
            teamBuildingDamage += pBuildingDamage
            if pBuildingDamage > maxBuildingDamage:
                maxBuildingDamage = pBuildingDamage
                winner = player
            
        damagePercentage = (maxBuildingDamage / teamBuildingDamage) * 100
        scaling = 0 if damagePercentage < 25 else max(1, min(3, damagePercentage / 15))
        if winner is not None:
            ret = []
            ret.append(winner['summonerName'])
            ret.append(cardName)
            ret.append(f'Dealt {damagePercentage:.2f}% of the teams damage to structures')
            ret.append(basePriority * scaling)
            ret.append(winner['championName'])
            return ret
        else:
            return ["", "", "", 0]

    def getCardNoDamage(self, basePriority, getCardForGoodTeam = True):
        """
        basePriority : initial priority value to be scaled by card data
        getCardForGoodTeam : true if get card for homies team, false for enemy team

        Description: 
        Least Damage

        return a list with format:
            [0] - summoner name
            [1] - card name
            [2] - card text
            [3] - card priority
            [4] - summoner champion
        """
        cardName = "I did no dAmage!"
        statName = "totalDamageDealtToChampions"
        winner = self.getNPlaceStatWinner(statName, 4, getCardForGoodTeam)
        if winner[0] is not None:
            noDamage = winner[1]
            noDamagePercent = winner[2] * 100
            scaling = 0 if noDamagePercent > 14 else max(1, min(4, 10 / max(1, noDamagePercent)))
            if(winner[0]['summonerName'] == "4th Migo"):
                scaling = 100

            ret = []
            ret.append(winner[0]['summonerName'])
            ret.append(cardName)
            ret.append(f'Only {noDamage} damage. ({noDamagePercent:.2f}% of teams damage. noob)')
            ret.append(basePriority * scaling)
            ret.append(winner[0]['championName'])
            return ret
        else:
            return ["", "", "", 0]

    def getCardCSWinner(self, basePriority, getCardForGoodTeam = True):
        """
        basePriority : initial priority value to be scaled by card data
        getCardForGoodTeam : true if get card for homies team, false for enemy team

        Description: 
        Least Damage

        return a list with format:
            [0] - summoner name
            [1] - card name
            [2] - card text
            [3] - card priority
            [4] - summoner champion
        """
        cardName = "Farming Queen"
        statName = "totalMinionsKilled"
        winner = self.getNPlaceStatWinner(statName, 0, getCardForGoodTeam)
        if winner[0] is not None:
            minPlayed = winner[0]['timePlayed'] / 60
            csPerMin = winner[1] / minPlayed
            scaling = 0 if csPerMin < 9 else max(1, min(4, csPerMin / 5))

            ret = []
            ret.append(winner[0]['summonerName'])
            ret.append(cardName)
            ret.append(f'Clean farm bro. {csPerMin:.2f} cs per minute')
            ret.append(basePriority * scaling)
            ret.append(winner[0]['championName'])
            return ret
        else:
            return ["", "", "", 0]


        #Remaining Card Ideas
        #abilities used
        #objectives stolen
        #penta kill
        #vision score


class CardManager:
    """
    Base Class for card manager
    Initialize with player name for cards
    Call getCards
    """
    def __init__(self, player = "Kabib Nurmagabob", region = "NA1", apiKey = API_KEY, homies = None):
        """
        Initialize with desired player, region, and if possible, API Key
        """
        self.player = player
        self.region = region
        self.key = apiKey
        if homies is None:
            homies = ['Mahat Magandalf', 'Dahlin', '4th Migo', 'Kabib Nurmagabob', 'Lacr3188', 'Eminems Sweater', 'GROBGOBGLOBGROD']
        self.homies = homies

    def getCards(self, numCards = 4):
        api = LolAPI(self.key, 'americas')

        homies_puuid = [api.getPUUID(homie, self.region) for homie in self.homies]
        puuid = api.getPUUID(self.player, self.region)          #get puuid of player of interest
        match_id = api.getMatchIdList(puuid, 1)                 #get match data of last match
        match = api.getMatchInfo(match_id[0])

        mCard = Card(match, homies_puuid)                       #create card object
        mCard.parseJson()
        mCard.splitTeamData()

        cardStack = []
        cardList = dir(mCard)                                   #get all functions in card class
        cardList[:] = [x for x in cardList if "getCard" in x]   #keep functions with getCard in the name, as these are card functions
        getCardsForGoodTeam = True

        for i in cardList:                                      #run all card functions
            func = getattr(mCard, i)
            card = func(3, getCardsForGoodTeam)     #3 is default priority for now
            cardStack.append((card[3], card))

        numCards = min(numCards, NUM_CARDS)

        if len(cardStack) <= numCards:
            return [x[1] for x in cardStack]
        else:
            cardStack.sort(key = lambda x: x[0], reverse = True)
            cardStack = cardStack[0:numCards]
            return [x[1] for x in cardStack]

if __name__ == '__main__':
    #example usage
    man = CardManager(player = 'Kabib Nurmagabob')
    ret = man.getCards(12)
    ret.sort(key = lambda x: x[3], reverse = True)
    print(*ret, sep = "\n")