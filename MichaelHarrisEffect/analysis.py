import os
import csv
from pprint import pprint

years = [2023]

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
        self.playergamelogs = {}
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
                gtm = game['Gtm'].split(' ')[0] #Getting rid of parenthesis
                self.playergamelogs[gtm] = game
                if game['Tm'] == team: # They could have been traded mid season                
                    # Updates the field in the game dictionary based on team Game #
                    self.games[gtm]["PlayerContribution"] = game["Inngs"]
                
    def _stats(self, playergamelogs = dict()) -> str:
        """String representation of average in .xxx format given a dict of games"""
        if not playergamelogs:
            playergamelogs = self.playergamelogs
        pa = sum([int(x['PA']) for x in playergamelogs.values()])
        ab = sum([int(x['AB']) for x in playergamelogs.values()])
        h = sum([int(x['H']) for x in playergamelogs.values()])
        b2 = sum([int(x['2B']) for x in playergamelogs.values()])
        b3 = sum([int(x['3B']) for x in playergamelogs.values()])
        hr = sum([int(x['HR']) for x in playergamelogs.values()])
        xbh = b2 + b3 + hr
        b1 = h - xbh
        bb = sum([int(x['BB']) for x in playergamelogs.values()])
        sf = sum([int(x['SF']) for x in playergamelogs.values()])
        ibb = sum([int(x['IBB']) for x in playergamelogs.values()])
        hbp = sum([int(x['HBP']) for x in playergamelogs.values()])
        so = sum([int(x['SO'] )for x in playergamelogs.values()])
        avg = round(h / ab, 3)
        obp = round((h + bb + hbp)/(ab + bb + hbp + sf),3)
        slg = round((b1 + (b2*2) + (b3*3) + (hr*4))/ab, 3)
        ops = round(obp + slg,3)
        sop = round((so/ab)*100,2)
        return {
            "avg" : avg,
            "obp" : obp,
            "sopct" : avg,
            "slg" : slg,
            "ops" : ops
        }
               
    def whole_team_performance(self, otherplayer: str, exclude_month = "AAAAAAAAAAAAAAH") -> dict:
        """Compares some other player's performance when the primary player is/is not playing"""
        performance_with_player = {}
        performance_without_player = {}
        with open(self.filename_player(otherplayer, self.year)) as opfile:
            opgames = csv.DictReader(opfile)
            for gamelog in opgames:
                if not exclude_month in gamelog["Date"]:
                    gtm = gamelog['Gtm'].split(' ')[0] #Getting rid of parenthesis
                    if self.games[gtm]['PlayerContribution'] != "DNP": # They could have been traded mid season                
                        performance_with_player[gtm] = gamelog
                    else:
                        performance_without_player[gtm] = gamelog

        return {
            "withPlayer" : self._stats(performance_with_player),
            "withoutPlayer" : self._stats(performance_without_player)
        }
    
    def other_players_performance(self, otherplayer: str) -> dict:
        """Compares some other player's performance when the primary player is/is not playing"""
        performance_with_player = {}
        performance_without_player = {}
        with open(self.filename_player(otherplayer, self.year)) as opfile:
            opgames = csv.DictReader(opfile)
            for gamelog in opgames:
                gtm = gamelog['Gtm'].split(' ')[0] #Getting rid of parenthesis
                if self.games[gtm]['PlayerContribution'] != "DNP": # They could have been traded mid season                
                    performance_with_player[gtm] = gamelog
                elif gamelog['Tm'] == self.team:
                    performance_without_player[gtm] = gamelog
                else:
                    print(gamelog["Tm"])

        return {
            "withPlayer" : self._stats(performance_with_player),
            "withoutPlayer" : self._stats(performance_without_player)
        }
        
        
        

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
    stats = yd.other_players_performance("RonaldAcuna")
    print("Ronald Acuna playing with or without MH2")
    for n, stat in stats.items():
        print(f"{year} {n}")
        prstr = ""
        for k,v in stat.items():
            prstr += f"{k} {v} | "
        print(prstr)
    stats = yd.other_players_performance("MattOlson")
    print("Matt Olson playing with or without MH2")
    for n, stat in stats.items():
        print(f"{year} {n}")
        prstr = ""
        for k,v in stat.items():
            prstr += f"{k} {v} | "
        print(prstr)
    stats = yd.other_players_performance("AustinRiley")
    print("AustinRiley playing with or without MH2")
    for n, stat in stats.items():
        print(f"{year} {n}")
        prstr = ""
        for k,v in stat.items():
            prstr += f"{k} {v} | "
        print(prstr)
    stats = yd.whole_team_performance("WholeTeam")
    print("Whole Team playing with or without MH2")
    for n, stat in stats.items():
        print(f"{year} {n}")
        prstr = ""
        for k,v in stat.items():
            prstr += f"{k} {v} | "
        print(prstr)
    stats = yd.whole_team_performance("WholeTeam", "Jun")
    print("Whole Team playing with or without MH2 Excluding June")
    for n, stat in stats.items():
        print(f"{year} {n}")
        prstr = ""
        for k,v in stat.items():
            prstr += f"{k} {v} | "
        print(prstr)