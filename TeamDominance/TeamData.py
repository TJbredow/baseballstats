from pprint import pprint
import json
import os

import requests

host = "https://statsapi.mlb.com"
crdir = os.path.dirname(os.path.abspath(__file__))

def get_all_mlb_teams():
    with open(f"{crdir}/teammap.json","r") as file:
        return json.loads(file.read())

def get_id_team_map() -> dict:
    with open(f"{crdir}/teammap.json","r") as file:
        data = json.loads(file.read())
    ids = {}
    for team in data.values():
        ids[team['id']] = team
    return ids

def get_all_mlb_teams_write():
    res = requests.get(f"{host}/api/v1/teams")
    teams = res.json()
    allteams = {}
    for team in teams['teams']:
        # Fuzzy search on the name, but only in NL/AL
        if team['league'].get('id') in [103, 104]:
            vals =  {
                "abbreviation" : team['abbreviation'],
                "name" : team['name'],
                "id" : team['id'],
                "teamName" : team['teamName'],
                "locationName" : team['locationName']
            }
            allteams[team['abbreviation']] = vals
    with open("teammap.json","w") as file:
        file.write(json.dumps(allteams, indent=2))

class Team:
    @classmethod
    def find_id(cls, team_name: str) -> int:
        res = requests.get(f"{host}/api/v1/teams")
        teams = res.json()
        for team in teams['teams']:
            # Fuzzy search on the name, but only in NL/AL
            if team_name.lower() in team['name'].lower() and team['league'].get('id') in [103, 104]:
                return {
                    "name" : team['name'],
                    "abbreviation" : team['abbreviation'],
                    "id" : team['id'],
                    "teamName" : team['teamName'],
                    "locationName" : team['locationName']
                }

    def __init__(self, team_name: str):
        teams = get_all_mlb_teams()
        teamdata = teams.get(team_name)
        if not teamdata:
            teamdata = self.find_id(team_name)
        self.id = teamdata['id']
        self.name = teamdata['name']
        self.teamName = teamdata['teamName']
        self.locationName = teamdata['locationName']
        self.abbreviation = teamdata['abbreviation']
    
    def get_games_season(self, year: int) -> list:
        if os.path.isfile(f"{crdir}/datacache/{self.id}{year}.json"):
            with open(f"{crdir}/datacache/{self.id}{year}.json", "r") as file:
                data = json.loads(file.read())
                return data
        else:
            res = requests.get(f"{host}/api/v1/teams/{self.id}/stats?stats=gamelog&group=hitting&season={year}")
            res2 = requests.get(f"{host}/api/v1/teams/{self.id}/stats?stats=gamelog&group=pitching&season={year}")
            data = res.json()
            data2 = res2.json()
            try: 
                games = data["stats"][0]["splits"]
                games2 = data2["stats"][0]["splits"]
            except KeyError:
                print(self.name, "didn't exist in", year)
                with open(f"{crdir}/datacache/{self.id}{year}.json", "w") as file:
                    file.write("[]")
                return []
            alldata = []
            for i , val in enumerate(games):
                alldata.append({
                    "hitting" : val,
                    "pitching" : games2[i]
                })
            with open(f"{crdir}/datacache/{self.id}{year}.json", "w") as file:
                file.write(json.dumps(alldata))
            return alldata
        
    def get_game_list_links(self, year: int) -> list:
        """Returns a list of all the links of games, and whether they were home or not"""
        linklist = []
        res = requests.get(f"{host}/api/v1/teams/{self.id}/stats?stats=gamelog&group=hitting&season={year}")
        r2 = res.json()
        for game in r2['stats'][0]['splits']:
            linklist.append((game['game']['link'], game['isHome']))
        return linklist
