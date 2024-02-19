from secrets import API_KEY, TOKEN
from cards_msg_discord import getCardsString, updateWinLossStreak
from leagueapi import  LolAPI
from cards import CardManager, SQUAD_PUUID, getLastNMatchIds
from card_data import CardData

if __name__ == '__main__':
    # manager to make the getCards call
    man = CardManager(player_puuid=SQUAD_PUUID["Dahlin"])
    lol_api = LolAPI(API_KEY, "americas")
    old_matches = getLastNMatchIds(SQUAD_PUUID.values(), 10, lol_api)
    streak = 0
    match_id = list(old_matches)[0]
    cardData = man.getCards(match_id, 5)
    streak = updateWinLossStreak(cardData.getIsWin(), streak)
    card_string = getCardsString(cardData, streak)
    print("----------------------------------------------------------------------------------------------")
    print(card_string)
    print("----------------------------------------------------------------------------------------------")
    match_id = list(old_matches)[1]
    cardData = man.getCards(match_id, 5)
    streak = updateWinLossStreak(cardData.getIsWin(), streak)
    card_string = getCardsString(cardData, streak)
    print(card_string)
    print("----------------------------------------------------------------------------------------------")
    match_id = list(old_matches)[2]
    cardData = man.getCards(match_id, 5)
    streak = updateWinLossStreak(cardData.getIsWin(), streak)
    card_string = getCardsString(cardData, streak)
    print(card_string)