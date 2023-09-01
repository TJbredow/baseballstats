import csv


hrs = {
}
with open("WholeTeam2023.csv") as file:
    teamdata = csv.DictReader(file)


    for game in teamdata:
        month = game['Date'].split(" ")[0]
        hr = int(game['HR'])
        try:
            hrs[month] += hr
        except KeyError:
            hrs[month] = hr

for k, v in hrs.items():
    print(k, v)