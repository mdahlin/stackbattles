import json
from secrets import API_KEY
from leagueapi import LolAPI
import datetime
import os
from new_participants import getParticipantData
from new_participants import updateParticipants

"""code wont work unless maindir references the stackbattles directory, 
and a subdirectory labeled "participant_jsons" is present"""

maindir = "/mnt/c/Users/sydmb/Documents/stackbattles/"

with open("{maindir}participants.json" .format(maindir=maindir), ) as json_file:
    p = json.load(json_file)

for key in p.keys():
    for puuid in p[key]:
        if puuid in p.keys():
            continue
        else:
            getParticipantData(puuid, maindir+"participant_jsons/")
            updateParticipants(p, os.listdir(maindir+"participant_jsons/"))
            print("Number of puuids used to pull match data: {c}" .format(c = len(p.keys())))
            break

