from secrets import CHAMPIONS
import os
import pickle as pkl
import json
import pandas as pd
import numpy as np



maindir = "/mnt/c/Users/sydmb/Documents/stackbattles/participant_jsons"

#create a column for each champion for each team

blue_cols = {} #this will be teamid=100
red_cols =  {}   #this will be teamid=200
wins = [] #will by the dependent variable will be wins for teamiD 100
for champion in CHAMPIONS:
    blue_cols[champion + "_100"]= []
    red_cols[champion + "_200"] = []

#track total # of champions successfully appended
red_count=0
blue_count=0
err_count = 0

for subdir, dirs, files in os.walk(maindir):
    for f in files:
        with open(os.path.join(subdir, f),) as json_file:
            p_json = json.load(json_file, encoding = 'latin-1')

        #determine which champions were in the game

        #append 1s for champions that were in the game and zeros for champions that weren't
        c_ingame = []
        for participant in p_json:
            champion = "{champion}_{teamId}" .format(champion = participant["championName"], teamId = str(participant["teamId"]))
            c_ingame.append(champion)
            if participant["teamId"] == 100:
                win = int(participant["win"])

        r = 0
        b = 0
        for key in blue_cols.keys():
            if key in c_ingame:
                blue_cols[key].append(1)
                b+=1
            else:
                blue_cols[key].append(0)
        for key in red_cols.keys():
            if key in c_ingame:
                red_cols[key].append(1)
                r+=1
            else:
                red_cols[key].append(0)

        #update dependent variable
        wins.append(win)

        #update total counts
        red_count+=r
        blue_count+=b
        err_count+= 10-r-b


print("SUCCESS")
print("red champions appended: {red_count}" .format(red_count=red_count))
print("blue champions appended: {blue_count}" .format(blue_count = blue_count))
print("encountered {errs} errors" .format(errs=err_count))
print("{wins} games seen" .format(wins=len(wins)))
        

red = pd.DataFrame.from_dict(red_cols)
blue = pd.DataFrame.from_dict(blue_cols)

data = pd.concat([red, blue], axis =1)
data["wins"] = wins
print(data.describe())
print(red.describe())
print(blue.describe())

with open("./model_data.pkl", "wb") as pkl_file:
    pkl.dump(data, pkl_file)

          


#iterate through each data pull directory and read in the data
#format desired data as a df


#seperate dependent and independent variables

#train test split for the data


