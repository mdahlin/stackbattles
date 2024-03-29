import math
from re import match
from leagueapi import LolAPI
from secrets import API_KEY
from card_data import CardData

import json
import os.path
from os import path

SQUAD_PUUID = {
        "Dahlin": "t9OAf1XjFsvRN-_-ILbDp1gPifPu6w0_KJho9nrsZAe66MDVhCt3fHl1Bu6v-9gKi3NsExXaZKUzHA",
        "Fey": "J32tRlyYWYCGstSV5Yl9tGScPkh71qxPcs3ww5VWARcp6rwc4WZhsmX8rc93_0BRxPGcqdPArlHksw",
        "Gerry": "86xzwMQ5Yy6ZiURZ43r6zh3lFLAylGww_vitKdWueIPUKv8cT0bwwEoMDhF2g6FNCar-7E64HyEVFg",
        "Sam": "XL05a5R3GFwH-S9fZ23GWmL6CDqR6fUqZXdpXt0Lq9SItHuBVf0a9CtuWStkLFmGMjTAP6rbJSjWbw",
        "Micky": "dt_IdbEDHTu6PknDNU1O2pyZ0onzdocgHdlMFxlnS_f7ivTk2sPPnE86Nq2QmUO4cylPNQlKsX1cqQ",
        "Bently": "pULUbze4JrO3DfCfzt3S6OOOR6B30M-L6FxYmYvmmGWPLfdnocfZgyCTj1wIFsRYEw8xqM7ueHU4RA",
        "Colt": "cSaofF6nFtyJLzS3-q9EBfsgUlgjuTmKYReNZwKlVUdKpPt3YikfC8Oeta8rI8X0Vagwk_RM6ROJLw"
        }

LEADERBOARD_FILENAME = "highscores.json"

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
            pData['totalHealsOnTeammates'] = p['totalHealsOnTeammates']
            pData['totalDamageShieldedOnTeammates'] = p['totalDamageShieldedOnTeammates']
            pData['pentaKills'] = p['pentaKills']
            pData['firstBloodKill'] = p['firstBloodKill']
            pData['totalDamageTaken'] = p['totalDamageTaken']
            pData["neutralMinionsKilled"] = p['neutralMinionsKilled']
            pData['win'] = p['win']

            if p['perks']['styles'][0]['selections'][0]['perk'] == 8128:
                pData['DH Damage'] = p['perks']['styles'][0]['selections'][0]['var1']
                pData['DH Stacks'] = p['perks']['styles'][0]['selections'][0]['var2']
            else:
                pData['DH Stacks'] = None
                pData['DH Damage'] = None 

            if p['perks']['styles'][0]['selections'][0]['perk'] == 8351:
                pData['Glacial Reduced'] = p['perks']['styles'][0]['selections'][0]['var2']
            else:
                pData['Glacial Reduced'] = None

            if p['perks']['styles'][0]['selections'][0]['perk'] == 8369:
                pData['FS Damage'] = p['perks']['styles'][0]['selections'][0]['var1']
                pData['FS Gold'] = p['perks']['styles'][0]['selections'][0]['var2']
            else:
                pData['FS Damage'] = None
                pData['FS Gold'] = None
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
            [5] - winning statistic for leaderboard
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
            ret.append(winner[1])
            return ret
        else:
            return ["", cardName, "", 0, "", 0]

    def getCardGlacial(self, basePriority, getCardForGoodTeam = True):
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
            [5] - winning statistic for leaderboard
        """

        cardName = "Sauce Master"
        statName = 'Glacial Reduced'

        winner = self.getNPlaceStatWinner(statName, 0, getCardForGoodTeam)
        second = self.getNPlaceStatWinner(statName, 1, getCardForGoodTeam)
  
        if winner[0] is not None:
            dif = winner[1] - second[1]
            if dif == 0:
                if winner[0]['totalDamageDealtToChampions'] < second[0]['totalDamageDealtToChampions']:
                    t = winner
                    winner = second
                    second = t
                    
            scaling = max(1, min(3, dif / max(1000, winner[1]))) if winner[1] > 0 else 0
            if self.matchJson['info']['gameMode'] == 'ARAM':        #always show stack card in aram
                scaling = 99

            ret = []
            ret.append(winner[0]['summonerName'])
            ret.append(cardName)
            ret.append(str(winner[1]) + " damage reduced. (+" + str(dif) + ")")
            ret.append(basePriority * scaling)
            ret.append(winner[0]['championName'])
            ret.append(winner[1])
            return ret
        else:
            return ["", cardName, "", 0, "", 0]

    def getCardFirstStrike(self, basePriority, getCardForGoodTeam = True):
        """
        basePriority : initial priority value to be scaled by card data
        getCardForGoodTeam : true if get card for homies team, false for enemy team

        Description:
        Get the player with the most money gained form First Strike
        Scale priority based off of difference between winner and second place
        Return priority 0 if no winner

        return a list with format:
            [0] - summoner name
            [1] - card name
            [2] - card text
            [3] - card priority
            [4] - summoner champion
            [5] - winning statistic for leaderboard
        """

        cardName = "Money Maker"
        winner = self.getNPlaceStatWinner("FS Gold", 0, getCardForGoodTeam)

        if winner[0] is not None:
            money = winner[1]
            scaling = 0 if winner[1] < 300 else max(1, min(4, money / 600))
            if self.matchJson['info']['gameMode'] == 'ARAM':        #always show stack card in aram
                scaling = 100

            ret = []
            ret.append(winner[0]['summonerName'])
            ret.append(cardName)
            ret.append(str(winner[1]) + " First Stike gold.")
            ret.append(basePriority * scaling)
            ret.append(winner[0]['championName'])
            ret.append(winner[1])
            return ret
        else:
            return ["", cardName, "", 0, "", 0]

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
            [5] - winning statistic for leaderboard
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
            ret.append(percentMitigated)
            return ret
        else:
            return ["", cardName, "", 0, "", 0]

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
            [5] - winning statistic for leaderboard
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
            ret.append(highestPercent)
            return ret
        else:
            return ["", cardName, "", 0, "", 0]
        
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
            [5] - winning statistic for leaderboard
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
        scaling = 0 if lowestPercent > 20 else min(1, max(3, 25 / lowestPercent))
        if winner is not None:
            ret = []
            ret.append(winner['summonerName'])
            ret.append(cardName)
            ret.append(f'Only {lowestPercent:.2f}% of total damage dealt to champions')
            ret.append(basePriority * scaling)
            ret.append(winner['championName'])
            ret.append(lowestPercent)
            return ret
        else:
            return ["", cardName, "", 0, "", 0]

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
            [5] - winning statistic for leaderboard
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
            ret.append(maxDeathDiff)
            return ret
        else:
            return ["", cardName, "", 0, "", 0]

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
            [5] - winning statistic for leaderboard
        """
        cardName = "The CC Lord"
        statName = "timeCCingOthers"
        winner = self.getNPlaceStatWinner(statName, 0, getCardForGoodTeam)
        if winner[0] is not None:
            ccScore = winner[1] / (winner[0]['timePlayed'] / 60)
            scaling = 0 if ccScore < 4 else max(1, min(4, ccScore / 3))

            ret = []
            ret.append(winner[0]['summonerName'])
            ret.append(cardName)
            ret.append(f'{ccScore:.2f} CC score per minute')
            ret.append(basePriority * scaling)
            ret.append(winner[0]['championName'])
            ret.append(ccScore)
            return ret
        else:
            return ["", cardName, "", 0, "", 0]

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
            [5] - winning statistic for leaderboard
        """
        cardName = "Big Money"
        statName = "goldEarned"
        winner = self.getNPlaceStatWinner(statName, 0, getCardForGoodTeam)
        if winner[0] is not None:
            goldEarnedPercent = winner[2]*100
            scaling = 0 if goldEarnedPercent < 25 else max(1, min(4, goldEarnedPercent / 15))

            ret = []
            ret.append(winner[0]['summonerName'])
            ret.append(cardName)
            ret.append(f'Earned {goldEarnedPercent:.2f}% of the teams gold')
            ret.append(basePriority * scaling)
            ret.append(winner[0]['championName'])
            ret.append(goldEarnedPercent)
            return ret
        else:
            return ["", cardName, "", 0, "", 0]

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
            [5] - winning statistic for leaderboard
        """
        cardName = "The Duke of Damage"
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
            ret.append(damagePercent)
            return ret
        else:
            return ["", cardName, "", 0, "", 0]


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
            [5] - winning statistic for leaderboard
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
            ret.append(biggestCrit)
            return ret
        else:
            return ["", cardName, "", 0, "", 0]


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
            [5] - winning statistic for leaderboard
        """
        cardName = "Tower Toppler"
        maxBuildingDamage = 0
        teamBuildingDamage = 1 #Avoid dividing by zero. Yes it really happened.
        winner = None
        teamData = self.goodTeamStats if getCardForGoodTeam else self.badTeamStats
        for player in teamData:
            pBuildingDamage = player['damageDealtToBuildings'] + player['damageDealtToTurrets']
            teamBuildingDamage += pBuildingDamage
            if pBuildingDamage > maxBuildingDamage:
                maxBuildingDamage = pBuildingDamage
                winner = player
            
        damagePercentage = ((maxBuildingDamage + 1) / teamBuildingDamage) * 100
        scaling = 0 if damagePercentage < 75 else max(1, min(3, damagePercentage / 30))
        if winner is not None:
            ret = []
            ret.append(winner['summonerName'])
            ret.append(cardName)
            ret.append(f'Dealt {damagePercentage:.2f}% of the teams damage to structures')
            ret.append(basePriority * scaling)
            ret.append(winner['championName'])
            ret.append(damagePercentage)
            return ret
        else:
            return ["", cardName, "", 0, "", 0]

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
            [5] - winning statistic for leaderboard
        """
        cardName = "I did no dAmage!"
        statName = "totalDamageDealtToChampions"
        winner = self.getNPlaceStatWinner(statName, 4, getCardForGoodTeam)
        if winner[0] is not None:
            noDamage = winner[1]
            noDamagePercent = winner[2] * 100
            scaling = 0 if noDamagePercent > 14 else max(1, min(4, 10 / max(1, noDamagePercent)))

            ret = []
            ret.append(winner[0]['summonerName'])
            ret.append(cardName)
            ret.append(f'Only {noDamage} damage. ({noDamagePercent:.2f}% of teams damage. noob)')
            ret.append(basePriority * scaling)
            ret.append(winner[0]['championName'])
            ret.append(noDamagePercent)
            return ret
        else:
            return ["", cardName, "", 0, "", 0]

    def getCardCSWinner(self, basePriority, getCardForGoodTeam = True):
        """
        basePriority : initial priority value to be scaled by card data
        getCardForGoodTeam : true if get card for homies team, false for enemy team

        Description: 
        CS per minute above 9

        return a list with format:
            [0] - summoner name
            [1] - card name
            [2] - card text
            [3] - card priority
            [4] - summoner champion
            [5] - winning statistic for leaderboard
        """
        cardName = "Farming Queen"
        statName = "totalMinionsKilled"
        winner = self.getNPlaceStatWinner(statName, 0, getCardForGoodTeam)
        if winner[0] is not None:
            minPlayed = winner[0]['timePlayed'] / 60
            csPerMin = (winner[1] + winner[0]['neutralMinionsKilled']) / minPlayed
            scaling = 0 if csPerMin < 9 else max(1, min(4, csPerMin / 5))

            ret = []
            ret.append(winner[0]['summonerName'])
            ret.append(cardName)
            ret.append(f'Clean farm bro. {csPerMin:.2f} cs per minute')
            ret.append(basePriority * scaling)
            ret.append(winner[0]['championName'])
            ret.append(csPerMin)
            return ret
        else:
            return ["", cardName, "", 0, "", 0]

    def getCardKillParticipation(self, basePriority, getCardForGoodTeam = True):
        """
        basePriority : initial priority value to be scaled by card data
        getCardForGoodTeam : true if get card for homies team, false for enemy team

        Description: 
        Kill participation above 90%

        return a list with format:
            [0] - summoner name
            [1] - card name
            [2] - card text
            [3] - card priority
            [4] - summoner champion
            [5] - winning statistic for leaderboard
        """
        cardName = "The Guy"
        winner = None
        kpWinner = 0
        teamData = self.goodTeamStats if getCardForGoodTeam else self.badTeamStats
        teamKills = 0
        for player in teamData:
            teamKills += player['kills']
        
        for player in teamData:
            pKP = (player['kills'] + player['assists']) / teamKills
            if pKP > kpWinner:
                kpWinner = pKP
                winner = player

        scaling = 0 if kpWinner < .9 else max(1, min(3, kpWinner / .35))
        if winner is not None:
            ret = []
            ret.append(winner['summonerName'])
            ret.append(cardName)
            ret.append(f'{kpWinner*100:.2f}% kill participation.')
            ret.append(basePriority * scaling)
            ret.append(winner['championName'])
            ret.append(kpWinner)
            return ret
        else:
            return ["", cardName, "", 0, "", 0]

    def getCardBigHeals(self, basePriority, getCardForGoodTeam = True):
        """
        basePriority : initial priority value to be scaled by card data
        getCardForGoodTeam : true if get card for homies team, false for enemy team

        Description: 
        Lots of healing

        return a list with format:
            [0] - summoner name
            [1] - card name
            [2] - card text
            [3] - card priority
            [4] - summoner champion
            [5] - winning statistic for leaderboard
        """
        cardName = "Notice me"
        statName = "totalHealsOnTeammates"
        statName2 = "totalDamageShieldedOnTeammates"
        winner = self.getNPlaceStatWinner(statName, 0, getCardForGoodTeam)
        if winner[0] is not None:
            healing = winner[1] + winner[0]['totalDamageShieldedOnTeammates']
            scaling = 0 if healing < 10000 else max(1, min(4, healing / 10000))

            ret = []
            ret.append(winner[0]['summonerName'])
            ret.append(cardName)
            ret.append(f'Thank me l8er. {healing} healing on teammates')
            ret.append(basePriority * scaling)
            ret.append(winner[0]['championName'])
            ret.append(healing)
            return ret
        else:
            return ["", cardName, "", 0, "", 0]

    def getCardPentakill(self, basePriority, getCardForGoodTeam = True):
        """
        basePriority : initial priority value to be scaled by card data
        getCardForGoodTeam : true if get card for homies team, false for enemy team

        Description: 
        Got a penta

        return a list with format:
            [0] - summoner name
            [1] - card name
            [2] - card text
            [3] - card priority
            [4] - summoner champion
            [5] - winning statistic for leaderboard
        """
        cardName = "Pentakill!"
        statName = "pentaKills"
        winner = self.getNPlaceStatWinner(statName, 0, getCardForGoodTeam)
        if winner[0] is not None and winner[1] > 0:
            scaling = 3

            ret = []
            ret.append(winner[0]['summonerName'])
            ret.append(cardName)
            ret.append(f'haha die trash')
            ret.append(basePriority * scaling)
            ret.append(winner[0]['championName'])
            ret.append(winner[1])
            return ret
        else:
            return ["", cardName, "", 0, "", 0]

        
    def getCardFirstBlood(self, basePriority, getCardForGoodTeam = True):
        """
        basePriority : initial priority value to be scaled by card data
        getCardForGoodTeam : true if get card for homies team, false for enemy team

        Description: 
        Got a penta

        return a list with format:
            [0] - summoner name
            [1] - card name
            [2] - card text
            [3] - card priority
            [4] - summoner champion
            [5] - winning statistic for leaderboard
        """
        cardName = "First Blood!"
        statName = "firstBloodKill"
        winner = None
        teamData = self.goodTeamStats if getCardForGoodTeam else self.badTeamStats
        for player in teamData:
            if player[statName] == True:
                winner = player
        
        if winner is not None:
            scaling = 0.5

            ret = []
            ret.append(winner['summonerName'])
            ret.append(cardName)
            ret.append(f'quick pop')
            ret.append(basePriority * scaling)
            ret.append(winner['championName'])
            ret.append(1)
            return ret
        else:
            return ["", cardName, "", 0, "", 0]

    def getCardBystander(self, basePriority, getCardForGoodTeam = True):
        """
        basePriority : initial priority value to be scaled by card data
        getCardForGoodTeam : true if get card for homies team, false for enemy team

        Description: 
        Got a penta

        return a list with format:
            [0] - summoner name
            [1] - card name
            [2] - card text
            [3] - card priority
            [4] - summoner champion
            [5] - winning statistic for leaderboard
        """
        cardName = "Innocent Bystander"
        statName = "totalDamageDealtToChampions"
        loserDealt = self.getNPlaceStatWinner(statName, 4, getCardForGoodTeam)
        statName = "totalDamageTaken"
        loserTaken = self.getNPlaceStatWinner(statName, 4, getCardForGoodTeam)

        if loserDealt[0]['summonerName'] == loserTaken[0]['summonerName']:
            scaling = 0.5

            ret = []
            ret.append(loserDealt[0]['summonerName'])
            ret.append(cardName)
            ret.append(f'Least damage dealt ({loserDealt[2] * 100:.2f}% of team) AND least damage taken ({loserTaken[2] * 100:.2f}% of team)')
            ret.append(basePriority * scaling)
            ret.append(loserDealt[0]['championName'])
            ret.append(loserTaken[2]*100 + loserDealt[2]*100)
            return ret
        else:
            return ["", cardName, "", 0, "", 0]

    def getCardMostKills(self, basePriority, getCardForGoodTeam = True):
        """
        basePriority : initial priority value to be scaled by card data
        getCardForGoodTeam : true if get card for homies team, false for enemy team

        Description: 
        Got a penta

        return a list with format:
            [0] - summoner name
            [1] - card name
            [2] - card text
            [3] - card priority
            [4] - summoner champion
            [5] - winning statistic for leaderboard
        """
        cardName = "Killtacular"
        statName = "kills"
        winner = None
        winner = self.getNPlaceStatWinner(statName, 0, getCardForGoodTeam)

        if winner is not None:
            ret = []
            deaths = winner[0]['deaths']
            assists = winner[0]['assists']
            kills = winner[1]
            scaling = 0 if kills < 25 else max(3, kills / 6)
            ret.append(winner[0]['summonerName'])
            ret.append(cardName)
            ret.append(f'{kills} kills at ({winner[1]}/{deaths}/{assists})')
            ret.append(basePriority * scaling)
            ret.append(winner[0]['championName'])
            ret.append(winner[0])
            return ret
        else:
            return ["", cardName, "", 0, "", 0]

    # def getCardWeirdFormula(self, basePriority, getCardForGoodTeam = True):
    #     """
    #     basePriority : initial priority value to be scaled by card data
    #     getCardForGoodTeam : true if get card for homies team, false for enemy team

    #     Description: 
    #     Get the player with the highest percentage of their damage dealt as true damage
    #     Scale priority based off of winners percent of true damage dealt
    #     Return priority 0 if winners percentage of true damage dealt is less than 25%

    #     return a list with format:
    #         [0] - summoner name
    #         [1] - card name
    #         [2] - card text
    #         [3] - card priority
    #         [4] - summoner champion
    #         [5] - winning statistic for leaderboard
    #     """

    #     cardName = "No counterplay"
    #     highestPercent = 0
    #     winner = None
    #     teamData = self.goodTeamStats if getCardForGoodTeam else self.badTeamStats
    #     for dmg in teamData:
    #         totalDamage = dmg['magicDamageDealtToChampions'] + dmg['physicalDamageDealtToChampions'] + dmg['trueDamageDealtToChampions']
    #         trueDamage = dmg['trueDamageDealtToChampions']
    #         percentTrue = trueDamage / totalDamage
    #         if(percentTrue > highestPercent):
    #             highestPercent = percentTrue
    #             winner = dmg

    #     highestPercent *= 100
    #     scaling = 0 if highestPercent < 25 else min(1, max(3, highestPercent / 20))
    #     if winner is not None:
    #         ret = []
    #         ret.append(winner['summonerName'])
    #         ret.append(cardName)
    #         ret.append(f'{highestPercent:.2f}% of damage dealt as true damage')
    #         ret.append(basePriority * scaling)
    #         ret.append(winner['championName'])
    #         ret.append(highestPercent)
    #         return ret
    #     else:
    #         return ["", cardName, "", 0, "", 0]

    def isVictory(self, getWinForGoodTeam = True):
        team = self.goodTeamStats if getWinForGoodTeam else self.badTeamStats
        if team is not None:
            return team[0]['win']
        
        #Remaining Card Ideas
        #abilities used
        #objectives stolen
        #vision score
        #zero damage to structures

def getLastNMatchIds(puuids: list, n_matches: int, api: LolAPI) -> set:
    match_ids = [api.getMatchIdList(puuid, n_matches)
                 for puuid in puuids]
    # flatten out list and turn into a set
    match_ids = set([match_id for sublist in match_ids
                     for match_id in sublist])
    return match_ids

lol_api = LolAPI(API_KEY, "americas")
old_matches = getLastNMatchIds(SQUAD_PUUID.values(), 10, lol_api)


class CardManager:
    """
    Base Class for card manager
    Initialize with player name for cards
    Call getCards
    """
    def __init__(self, player_puuid = SQUAD_PUUID["Fey"],
            apiKey = API_KEY, homies_puuid = None):
        """
        Initialize with desired player, region, and if possible, API Key
        """
        self.player_puuid = player_puuid
        self.key = apiKey
        if homies_puuid is None:
            homies_puuid = list(SQUAD_PUUID.values())
        self.homies = homies_puuid
        self.leaderboard = {}

    #need to refactor all the leaderboard disgusting nonsense
    def readLeaderboard(self):
        with open(LEADERBOARD_FILENAME) as json_file:
            highscores = json.load(json_file)
            self.leaderboard = highscores['cards']

    def initLeaderboard(self, cardlist):
        data = {}
        data['cards'] = []
        for card in cardlist:
            data['cards'].append({
                card[1][1] : {
                'playername' : card[1][0],
                'playerchampion' : card[1][4],
                'statvalue' : card[1][5]
                }
            })
        with open(LEADERBOARD_FILENAME, 'w') as outfile:
            json.dump(data, outfile)
    
    def updateLeaderboard(self, cardlist):
        for stat in self.leaderboard:
            for card in cardlist:
                cardname = card[1][1]
                data = stat.get(cardname)
                if data is not None:
                    if cardname == "The PvE Player" or cardname == "I did no dAmage!" or cardname == "Innocent Bystander":
                        if stat[cardname]['statvalue'] > card[1][5]:
                            stat[cardname]['playername'] = card[1][0]
                            stat[cardname]['playerchampion'] = card[1][4]
                            stat[cardname]['statvalue'] = card[1][5]
                            card[1][2] += " - New Highscore!"
                    else:
                        if stat[cardname]['statvalue'] < card[1][5]:
                            stat[cardname]['playername'] = card[1][0]
                            stat[cardname]['playerchampion'] = card[1][4]
                            stat[cardname]['statvalue'] = card[1][5]
                            card[1][2] += " - New Highscore!"
            

    def writeLeaderboard(self):
        data = {}
        data['cards'] = []
        for p in self.leaderboard:
            cardname = list(p)[0]
            data['cards'].append({
                cardname : {
                'playername' : p[cardname]['playername'],
                'playerchampion' : p[cardname]['playerchampion'],
                'statvalue' : p[cardname]['statvalue']
            }})
        with open(LEADERBOARD_FILENAME, 'w') as outfile:
            json.dump(data, outfile)

    def getLeaderboard(self):
        return self.leaderboard
    
    def getLastNMatchIds(self, N):
        # not used anymore after other changes
        api = LolAPI(self.key, 'americas')
        puuid = self.player_puuid
        match_ids = api.getMatchIdList(puuid, N)
        return match_ids
            
    def getCards(self, match_id, numCards=4, enemyTeam = False):
        api = LolAPI(self.key, 'americas')

        homies_puuid = self.homies
        match = api.getMatchInfo(match_id)
        matchType = match['info']['gameMode']
        matchTime = match['info']['gameDuration']
        matchTimeString = '{:d}:{:02d}'.format(math.floor(matchTime / 60), matchTime % 60)

        mCard = Card(match, homies_puuid)                       #create card object 
        mCard.parseJson()
        mCard.splitTeamData()

        cardStack = []
        cardList = dir(mCard)                                   #get all functions in card class
        cardList[:] = [x for x in cardList if "getCard" in x]   #keep functions with getCard in the name, as these are card functions
        getCardsForGoodTeam = not enemyTeam
        needLeaderboardInit = not path.exists(LEADERBOARD_FILENAME)

        for i in cardList:                                      #run all card functions
            func = getattr(mCard, i)
            try:
                card = func(3, getCardsForGoodTeam)     #3 is default priority for now    
                if card[3] > 0 or needLeaderboardInit:
                    cardStack.append((card[3], card))
            except ZeroDivisionError:
                print(card[3])

        if needLeaderboardInit:
            self.initLeaderboard(cardStack)
            for card in cardStack:
                if card[1][3] == 0:
                    del card
        else:
            self.readLeaderboard()
            self.updateLeaderboard(cardStack)
            self.writeLeaderboard()


        isWin = mCard.isVictory()
        numCards = min(numCards, len(cardList))

        if len(cardStack) <= numCards:
            return CardData([x[1] for x in cardStack], isWin, matchType, matchTimeString)

        else:
            cardStack.sort(key = lambda x: x[0], reverse = True)
            cardStack = cardStack[0:numCards]
            return CardData([x[1] for x in cardStack], isWin, matchType, matchTimeString)

if __name__ == '__main__':
    #example usage
    man = CardManager(player_puuid=SQUAD_PUUID["Fey"])
    last_matches = [lol_api.getMatchIdList(puuid, 1)
    for puuid in SQUAD_PUUID.values()]
    last_match = min(last_matches)
    cards, isWin = man.getCards(last_match[0], 5)
