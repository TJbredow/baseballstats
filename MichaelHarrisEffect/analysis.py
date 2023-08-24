import os
import csv
from pprint import pprint

years = [2022, 2023]

class YearData:
    datapath = os.getenv("ANALYSIS_DATA_PATH",".")

    @classmethod
    def filename_team(cls, team: str, year: str) -> str:
        return f"{cls.datapath}/{team}{year}.csv"

    @classmethod 
    def filename_player(cls, player: str, year: str) -> str:
        return f"{cls.datapath}/{player}{year}.csv"
    
    def __str__(self) -> str:
        stats = self.simple_analysis()
        printstring = f"Year: {self.year}\nPlayer: {self.player}\nTeam:{self.team}\n"
        for k, v in stats.items():
            printstring += f"{k}: {v}\n"
        return printstring



    def __init__(self, team: str, player: str, year: str):
        """Ingests data from csvs into dictionaries for analysis"""
        self.games = {}
        self.team = team
        self.player = player
        self.year = year
        with open(self.filename_team(team, year),'r') as pfile:
            teamgames = csv.DictReader(pfile) #Takes the top line of the CSV as the keys
            for game in teamgames:
                self.games[game['Gm#']] = {
                    "Result" : game["W/L"][0], #Baseball reference puts W-wo for walkoffs, and I'm just cutting that off
                    "Runs" : int(game["R"]),
                    "RunsAgainst" : int(game["RA"]),
                    "PlayerContribution" : "DNP" 
                }
        with open(self.filename_player(player, year),'r') as pfile:
            playergames = csv.DictReader(pfile)
            for game in playergames:
                # it can be safely assumed that any game a player has been in, is contained within the team's games
                if game['Tm'] == team: # They could have been traded mid season                
                    gtm = game['Gtm'].split(' ')[0] #Getting rid of parenthesis
                    # Updates the field in the game dictionary based on team Game #
                    self.games[gtm]["PlayerContribution"] = game["Inngs"]
        appearances = {x["PlayerContribution"] for x in self.games.values()}
        # self.win_pcts = {
        #     appearance : win_pct(appearance) 
        # }
        

    def simple_analysis(self) -> dict:
        """Returns Python Dictionary of various basic stats. Just read the code"""
        games_played = []
        games_notplayed = []
        for game in self.games.values():
            if game["PlayerContribution"] == "DNP":
                games_notplayed.append(game)
            else:
                games_played.append(game)
        p = len(games_played)
        np = len(games_notplayed)
        stats = {
            "Games Played" : p,
            "Winpct GP" : round(sum(map(lambda x: x["Result"] == "W", games_played))/p*100,2),
            "Team Runs/Game GP": round(sum([x['Runs'] for x in games_played])/p,2),
            "Team Runs Against/Game GP": round(sum([x['RunsAgainst'] for x in games_played])/p,2),
            "Games Not Played" : np,
            "Winpct DNP" : round(sum(map(lambda x: x["Result"] == "W", games_notplayed))/np*100,2),
            "Team Runs/Game DNP": round(sum([x['Runs'] for x in games_notplayed])/np,2),
            "Team Runs Against/Game DNP": round(sum([x['RunsAgainst'] for x in games_notplayed])/np,2)
        }
        return stats

    def simple_analysis_tuple(self) -> tuple:
        """Returns Python Tuple of various basic stats. In the same order as the dictionary (Python3.7+)"""
        return tuple(x for x in self.simple_analysis().values())
        


for year in years:
    yd = YearData("ATL","MichaelHarris", year)
    print(yd)
