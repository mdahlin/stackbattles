class CardData:

    def __init__(self, cards, isWin, matchType, matchTime):
        self.cards = cards
        self.isWin = isWin
        self.matchType = matchType
        self.matchTime = matchTime
    
    def __str__(self):
        self.cards.sort(key=lambda x: x[3], reverse=True)
        gameModeString = self.matchType + " (" + self.matchTime + ")" + " - "
        winLoss = "Victory!" if self.isWin  else "Defeat"
        string = gameModeString + winLoss + "\n"
        for card in self.cards:
            string += '{0} - {4} | **{1}** - {2}'.format(*card)
            string += '\n'
        return string

    def getIsWin(self):
        return self.isWin