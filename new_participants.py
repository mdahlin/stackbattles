import os
import json
import pickle as pkl
from secrets import API_KEY
from leagueapi import LolAPI
import datetime

#get list of directories in json directory
#load participant master list
#for json_name in participant directory load json
#graph['json_name'] = [participant['puuid'] for participant in match if ]
#load visited list
#bfs through graph to get visited list
#pickle visited

maindir = "./participant_jsons/"

participant_dirs = os.listdir(maindir)



#load participants.json this json must exist for code to work
#with open("participants.json", ) as json_file:
    #p_json = json.load(json_file)


def getParticipantData(ipuuid, data_dir, list_path, json_path):
    """takes a puuid and an api object from leagueapi and runs the getmatchIDList and getMatchInfo methods
    creates a subdirectory for matched pulled from the puuids history at the path specificed by data_dir
    and writes json files of participant data from those games.
    updates a match_list to include"""

    with open(json_path,) as json_file:
        p_json = json.load(json_file)

    with open(list_path,"rb") as pkl_file:
        match_list = pkl.load(pkl_file)

    api = LolAPI(API_KEY, 'americas')
    match_ids = api.getMatchIdList(ipuuid, 100)
    matches = []

    for match_id in match_ids:
        match = api.getMatchInfo(match_id)

        try:
            gameMode = match['info']['gameMode']
            if gameMode == 'ARAM':
                matches.append(match)
            else:
                continue
        except KeyError:
            continue


    d = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    mydir = "{data_dir}/{puuid}|{d}" .format(data_dir=data_dir, puuid=ipuuid, d=d)
    os.makedirs(mydir)
    participants = []
    for match in matches:
        game_id = match['metadata']['matchId']
        #only write match data if match is not found in match_list
        if game_id in match_list:
            continue
        else:
            #create a path to write participant data too
            path = "{mydir}/json_{puuid}_{game_id}.json" .format(mydir=mydir, puuid=ipuuid, game_id=game_id)
            #append the match id to the match list
            match_list.append(game_id)

            #write the participants json data to an out_file
            out_file = open(path, "w")
            json.dump(match['info']['participants'], out_file, indent = 6)
            out_file.close()

            #go through each participant in the match and append their puuid to the participants list to be added as the key value pair in participants json
            for participant in match['info']['participants']:
                if participant['puuid'] not in participants and participant['puuid'] != ipuuid:
                    participants.append(participant['puuid'])
    
    #update and store match list
    with open(list_path, "wb") as pkl_file:
        pkl.dump(match_list, pkl_file)
    
    #update and store participant json
    if ipuuid not in p_json.keys():
        p_json[ipuuid] = participants
    with open(json_path, "w") as json_file:
        json.dump(p_json, json_file)






