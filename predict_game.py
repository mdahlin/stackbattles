from secrets import CHAMPIONS
import pandas as pd
import pickle as pkl

maindir = "/mnt/c/Users/sydmb/Documents/stackbattles/participant_jsons"

#create a column for each champion for each team

blue_cols = {} #this will be teamid=100
red_cols =  {}   #this will be teamid=200
wins = [] #will by the dependent variable will be wins for teamiD 100
for champion in CHAMPIONS:
    blue_cols[champion + "_100"]= []
    red_cols[champion + "_200"] = []

c_100 = []
c_200 = []


def getChampions(team_list, champion_list, team_name):
    while len(team_list) <5:
        print("Enter a new champion name on {team_name} team:" .format(team_name = team_name))
        c = str(input())

        if c in champion_list:
            team_list.append(c)
        else:
            print("Champion: {c} not found. Below is a list of all champions." .format(c=c))
            print(CHAMPIONS)
    print("Team Updated!")
    return team_list

c_100 = getChampions(c_100, CHAMPIONS, "your")
c_200 = getChampions(c_200, CHAMPIONS, "their")

c_100 = [champion+"_"+"100" for champion in c_100]
c_200 = [champion+"_"+"200" for champion in c_200]

for key in blue_cols.keys():
    if key in c_100:
        blue_cols[key].append(1)
    else:
        blue_cols[key].append(0)

for key in red_cols.keys():
    if key in c_200:
        red_cols[key].append(1)
    else:
        red_cols[key].append(0)

blue = pd.DataFrame.from_dict(blue_cols)
red = pd.DataFrame.from_dict(red_cols)

x_test = pd.concat([red,blue], axis =1)

with open("./xgb_model.pkl", "rb") as pkl_file:
    xgb_model = pkl.load(pkl_file)

probability = xgb_model.predict_proba(x_test)*100

print("You are {p}% likely to win this game" .format(p=probability[0][1]))
