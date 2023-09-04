import requests
from pprint import pprint

from TeamData import Team, get_id_team_map, get_all_mlb_teams


teammap = get_id_team_map()

def get_sweeps(team: Team, year: int):
    sweeps = []
    games = team.get_games_season(year)
    opponents = {}
    for game in games:
        try:
            runsFor = game['hitting']['stat']['runs']
        except KeyError:
            print(game['pitching'])
            runsFor = 0
        try:
            runsAgainst = game['pitching']['stat']['runs']
        except:
            print(game['pitching'])
            runsAgainst = 0
        if game['pitching']['isWin']:
            win = 1
        else:
            win = 0 
        try:
            opponents[game['hitting']['opponent']['id']]['wins'] += win
            opponents[game['hitting']['opponent']['id']]['totalGames'] += 1
            opponents[game['hitting']['opponent']['id']]['runsFor'] += runsFor
            opponents[game['hitting']['opponent']['id']]['runsAgainst'] += runsAgainst
        except KeyError:
            opponents[game['hitting']['opponent']['id']]  = {
                "id" : game['hitting']['opponent']['id'],
                "wins" : win ,
                "totalGames" : 1,
                "runsFor" : runsFor,
                "runsAgainst" : runsAgainst
            }
    
    for opponent in opponents.values():
        if opponent['wins'] == opponent['totalGames']:
            sweeps.append(opponent)
    return sweeps

allteams = get_all_mlb_teams()
all_sweeps = []
for teamname in allteams:
    team = Team(teamname)
    # add all years together, but only include 6 games or more
    for i in range(1905, 2024):
        print(i)
        schweeps = get_sweeps(team, i)
        for sweep in schweeps:
            if sweep['totalGames'] > 5:
                sweep['year'] = i
                sweep['runDiff'] = sweep['runsFor'] - sweep['runsAgainst']
                sweep['team'] = team.abbreviation
                sweep['diffpergame'] = sweep['runDiff'] / sweep['totalGames']
                all_sweeps.append(sweep)

print("year", "for", "agn", "w", 'rf', 'ra', 'r', "df/g")
for yearsweep in all_sweeps:
    print(yearsweep['year'], yearsweep['team'], teammap[yearsweep['id']]['abbreviation'], yearsweep['wins'], yearsweep['runsFor'], yearsweep['runsAgainst'], yearsweep['runDiff'], yearsweep['diffpergame'])