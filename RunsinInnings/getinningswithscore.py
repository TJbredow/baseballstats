import requests
from pprint import pprint

# 
host = "https://statsapi.mlb.com"

def get_game_list_links(team_name: str, year: str) -> list:
    """Returns a list of all the links of games, and whether they were home or not"""
    res = requests.get(f"{host}/api/v1/teams")
    linklist = []
    r = res.json()
    for team in r['teams']:
        if team['name'] == team_name:
            id = team['id']
    
    res = requests.get(f"{host}/api/v1/teams/{id}/stats?stats=gamelog&group=hitting&season={year}")
    r2 = res.json()
    for game in r2['stats'][0]['splits']:
        linklist.append((game['game']['link'], game['isHome']))
    return linklist

def get_inning_data(game_path: str, home_away: bool):
    """Returns only the inning data of the team in question, home or away"""
    if home_away:
        ha = "home"
    else:
        ha = "away"
    
    res = requests.get(f"{host}{game_path}")
    gamedata = res.json()
    innings = gamedata['liveData']['linescore']['innings']
    teaminnings = []
    for inning in innings:
        teaminnings.append(inning[ha])
    return teaminnings

#Analysis
games = get_game_list_links("Los Angeles Dodgers", "2023")
total_innings = 0
innings_w_score = 0
total_runs = 0 #Just to ensure it's right

for game in games:
    inns_data = get_inning_data(game[0],game[1])
    for inn in inns_data:
        try:
            runs = inn['runs']
            total_innings += 1
            if runs:
                innings_w_score += 1
            total_runs += runs
        except KeyError: # Bottom of 9th inning wasn't played
            pass

print("Total Innings", total_innings)
print("Innings With at least one Run", innings_w_score)
print("Total Runs", total_runs)