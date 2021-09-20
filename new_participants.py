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


def getParticipantData(ipuuid, data_dir):
    """takes a puuid and an api object from leagueapi and runs the getmatchIDList and getMatchInfo methods
    creates a subdirectory for matched pulled from the puuids history at the path specificed by data_dir
    and writes json files of participant data from those games."""


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
    for match in matches:
        game_id = match['metadata']['matchId']
        path = "{mydir}/json_{puuid}_{game_id}.json" .format(mydir=mydir, puuid=ipuuid, game_id=game_id)

        out_file = open(path, "w")
        json.dump(match['info']['participants'], out_file, indent = 6)
        out_file.close()

def updateParticipants(p_json, participant_dirs, json_path):
    
    #iterate through participant directories to get participant_dirs
    for participant_dir in participant_dirs:
        puuid = participant_dir.split("|")[0]
        participants =[]
        #iterate through each json for that participant
        for filename in os.listdir(os.path.join(maindir,participant_dir)):
            f=os.path.join(maindir,participant_dir,filename)
            if os.path.isfile(f):
                g = open(f, )
                game = json.load(g)

                #check if puuid is key or exists in previous games among pull
                for participant in game:
                    if participant['puuid'] not in participants and participant['puuid'] != puuid:
                        participants.append(participant['puuid'])
                    else:
                        continue
        #if puuid is not in the participant json add it with participants
        if puuid not in p_json.keys():
            p_json[puuid] = participants
            
    '''
    update json at json path with key value pair: 
    key = puuid used to pull data, 
    value is a list of all unique participants that played arams with puuid pulled
    '''
    with open(json_path,'w') as json_file:
        json.dump(p_json, json_file)






