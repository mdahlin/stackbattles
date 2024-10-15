import json
from secrets import API_KEY
from leagueapi import LolAPI
import datetime
import os
from new_participants import getParticipantData
import pickle as pkl
import time

"""code wont work unless maindir references the stackbattles directory, 
and a subdirectory labeled "participant_jsons" is present"""

maindir = "/mnt/c/Users/sydmb/Documents/stackbattles/"
match_path= "{maindir}match_list.pkl" .format(maindir=maindir)
json_path ="{maindir}participants.json" .format(maindir=maindir)

with open(json_path, ) as p_file:
    p = json.load(p_file)

for key in p.keys():
    for puuid in p[key]:
        if puuid in p.keys():
            continue
        else:
            getParticipantData(puuid, maindir+"participant_jsons/",match_path, json_path)
            with open(json_path,) as u_file:
                u = json.load(u_file)
            print("Number of puuids used to pull match data: {c}" .format(c = len(u.keys())))
            time.sleep(180)
            

