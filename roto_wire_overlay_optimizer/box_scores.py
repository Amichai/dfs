import datetime
import pandas as pd
from tabulate import tabulate

# https://www.bigdataball.com/nba-stats-central/
# pass: love4cgB

column_to_column_key = {
    "date": "Unnamed: 2",
    "name": "Unnamed: 4",
    "team": "Unnamed: 5",
    "opp": "Unnamed: 6",
    "starter": "Unnamed: 7",
    "minutes": "Unnamed: 9",
    "rest": "Unnamed: 11",
    "positions": "Unnamed: 13",
    "salary": "Unnamed: 16",
    "fdp": "Unnamed: 19",
    }

def get_team(query_team):

    abbr_file = open("team_names.txt")
    lines = abbr_file.readlines()
    abbr_dict = {}
    for line in lines:
        parts = line.split(',')
        abbr_name = parts[1].strip()
        abbr_dict[parts[1].strip()] = parts[0]
        pass

    inspection_team = abbr_dict[query_team]

    filename = "~/Downloads/season_data/10-{}-2021-nba-season-dfs-feed.xlsx".format(datetime.datetime.now().day - 1)


    dfs = pd.read_excel(filename, sheet_name=None)
    
    feed = dfs['NBA-DFS-SEASON-FEED']
    all_columns = feed.keys()

    team_to_date_to_rows = {}

    for index, row in feed.iterrows():
        if row['GAME INFORMATION'] != "NBA 2021-2022 Regular Season":
            continue

        date = row["Unnamed: 2"]
        name = row["Unnamed: 4"]
        team = row["Unnamed: 5"]
        opp = row["Unnamed: 6"]
        starter = row["Unnamed: 7"]
        minutes = row["Unnamed: 9"]
        rest = row["Unnamed: 11"]
        positions = row["Unnamed: 13"]
        salary = row["Unnamed: 16"]
        fdp = row["Unnamed: 19"]

        if team != inspection_team:
            continue

        if not query_team in team_to_date_to_rows:
            team_to_date_to_rows[query_team] = {}

        if not date in team_to_date_to_rows[query_team]:
            team_to_date_to_rows[query_team][date] = []

        team_to_date_to_rows[query_team][date].append((date, name, team, opp, starter, minutes, rest, positions, salary, fdp))
        
    return team_to_date_to_rows

        #print("{}, {}, {}, {}, {}, {}, {}, {}, {}, {}".format(date, name, team, opp, starter, minutes, rest, positions, salary, fdp))

def q(row, key, salary=None):
    if key == "val":
        fdp = q(row, "fdp")
        fd_salary = q(row, "salary")
        if salary != None:
            fd_salary = salary

        value = round(fdp * 100 / fd_salary, 2)
        if value < 0 and fdp > 0:
            import pdb; pdb.set_trace()
        return value
    if key == "salary":
        return float(row[column_to_column_key[key]])
    return row[column_to_column_key[key]]

