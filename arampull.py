import json
from secrets import API_KEY
from leagueapi import LolAPI
import datetime
import os
from new_participants import getParticipantData
from new_participants import updateParticipants
import pickle as pkl

"""code wont work unless maindir references the stackbattles directory, 
and a subdirectory labeled "participant_jsons" is present"""

maindir = "/mnt/c/Users/sydmb/Documents/stackbattles/"
match_path= "{maindir}match_list.pkl" .format(maindir=maindir)
json_path ="{maindir}participants.json" .format(maindir=maindir)

for key in p.keys():
    for puuid in p[key]:
        if puuid in p.keys():
            continue
        else:
            getParticipantData(puuid, maindir+"participant_jsons/",match_path)
            updateParticipants(os.listdir(maindir+"participant_jsons/"),json_path)
            print("Number of puuids used to pull match data: {c}" .format(c = len(p.keys())))
            break

