import time
import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd
from requests.api import head
from tabulate import tabulate



import sys
from pathlib import Path
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

# Additionally remove the current file's directory from sys.path
try:
    sys.path.remove(str(parent))
except ValueError: # Already removed
    pass



from roto_wire_overlay_optimizer import roto_wire_scrape

def get_player_projections(projection_file_name):
    to_read = open(projection_file_name)

    player_to_fp = {}

    lines = to_read.readlines()
    for line in lines:
        parts = line.split("|")
        if len(parts) < 4:
            continue
        if parts[3] == "Fantasy Score":
            player_name = parts[2]
            # player_name = player_name.replace(" III", "")
            # player_name = player_name.replace(" Jr.", "")
            if parts[4].strip() == "REMOVED":
                continue
            player_to_fp[player_name] = float(parts[4].strip())

    return player_to_fp


current_date = datetime.datetime.now()
projection_file_name = "money_line_scrape_{}_{}_{}.txt".format(current_date.month, current_date.day, current_date.year)

money_line_fdp_projections = get_player_projections(projection_file_name)

# https://www.bigdataball.com/nba-stats-central/
# pass: love4cgB


def match_name(name1, names_rw):
    name_parts = name1.split(' ')
    last_name = None
    if len(name_parts) == 2:
        last_name = name_parts[1]

    first_initial = name_parts[0][0]

    assert last_name != None

    candidates = []
    for (name, status) in names_rw:
        if name == name1:
            return name1

        if last_name in name and name[0] == first_initial:
            candidates.append(name1)

    if len(candidates) > 1:
        print("{}, {}, {}".format(name1, last_name, candidates))


    if len(candidates) == 1:
        return candidates[0]

    return None



(all_starters_rw, _, questionable_non_starters_rw, _) = roto_wire_scrape.scrape_lineups()


def get_fd_slate_players(fd_slate_file_name):
    all_players = {}
    salaries = open(fd_slate_file_name)
    lines = salaries.readlines()
    found_count = 0

    for line in lines[1:]:
        parts = line.split(',')
        full_name = parts[3]

        positions = parts[1]
        salary = parts[7]
        team = parts[9]
        status = parts[11]
        name = full_name
        all_players[name] = [name, positions, float(salary), team, status]
        
    return all_players

master_fd_slate_file = "salary_data/FanDuel-NBA-2021 ET-11 ET-02 ET-66298-players-list.csv"

all_fd_slate_players = get_fd_slate_players(master_fd_slate_file)

teams = []
for pl in all_fd_slate_players.values():
    team = pl[3]
    if not team in teams:
        teams.append(team)

print(teams)
matched_team_names = []

abbr_file = open("team_names.txt")
lines = abbr_file.readlines()
abbr_dict = {}
abbr_dict2 = {}
for line in lines:
    parts = line.split(',')
    abbr_name = parts[1].strip()
    abbr_dict[parts[1].strip()] = parts[0]
    abbr_dict2[parts[0]] = parts[1].strip()


for team in teams:
    matched_team_names.append(abbr_dict[team])
    # get_game_urls(team)
    #past game results

# matched_team_names += abbr_dict.values()

# import pdb; pdb.set_trace()


# https://www.bigdataball.com/nba-stats-central/
# pass: love4cgB

today = datetime.datetime.now()
yesterday = today - datetime.timedelta(days=1)

filename = "~/Downloads/season_data/{}-{}-{}-nba-season-dfs-feed.xlsx".format(yesterday.month, str(yesterday.day).zfill(2), yesterday.year)

dfs = pd.read_excel(filename, sheet_name=None)

feed = dfs['NBA-DFS-SEASON-FEED']
all_columns = feed.keys()

team_to_date_to_rows = {}

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

    if team not in matched_team_names:
        continue


    if not team in team_to_date_to_rows:
        team_to_date_to_rows[team] = {}

    if not date in team_to_date_to_rows[team]:
        team_to_date_to_rows[team][date] = []

    team_to_date_to_rows[team][date].append(row)

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

def get_salary(all_players, name, date):
    if not date in all_players[name]:
        return 0.0
    return q(all_players[name][date], "salary")



for team in matched_team_names:
    print("\nTEAM: {}".format(team))
    starter_str = "Starters: "
    starter_names_rw = []
    for pl in all_starters_rw:
        if pl[1] == abbr_dict2[team]:
            starter_str += "{} {}, ".format(pl[0], pl[2])
            starter_names_rw.append((pl[0], pl[2]))


    print(starter_str)

    bench_str = "Other: "
    other_names_rw = []
    for pl in questionable_non_starters_rw:
        if pl[1] == abbr_dict2[team]:
            bench_str += "{} {}, ".format(pl[0], pl[2])
            other_names_rw.append((pl[0], pl[2]))

    print(bench_str)

    all_dates = team_to_date_to_rows[team].keys()

    all_dates_sorted = sorted(all_dates)

    all_dates = all_dates_sorted[-3:]

    all_players = {}
    last_date = all_dates[-1]
    for date in all_dates:
        all_rows = team_to_date_to_rows[team][date]
        for row in all_rows:
            name = q(row, "name")

            if not name in all_players:
                all_players[name] = {}

            all_players[name][date] = row
    all_player_names = all_players.keys()


    # import pdb; pdb.set_trace()
    all_players_sorted = sorted(all_player_names, key=lambda name: get_salary(all_players, name, last_date), reverse=True)

    table_rows = []
    
    for pl in all_players_sorted:
        todays_price = 0
        todays_status = ""
        if pl in all_fd_slate_players:
            todays_price = all_fd_slate_players[pl][2]
            todays_status = all_fd_slate_players[pl][-1]

            
            # result = match_name(pl, starter_names_rw)
            # print("---")
            # print(result)
        table_row = []
        table_row.append(pl)
        val_sum = 0
        for date in all_dates:
            if not date in all_players[pl]:
                table_row += ["O", "", "", "", ""]

                continue

            fdp = round(q(all_players[pl][date], "fdp"), 2)
            minutes = q(all_players[pl][date], "minutes")
            salary = q(all_players[pl][date], "salary")

            starter = q(all_players[pl][date], "starter") == "Y"
            starter_str = ""
            if starter:
                starter_str = "S"

            if todays_price == 0:
                todays_price = salary
            val = q(all_players[pl][date], "val", todays_price)
            val_sum += val

            if isinstance(salary, float):
                try:
                    salary = int(salary)
                except:
                    salary = 0


            table_row += [starter_str, fdp, minutes, val, int(salary)]


        table_row[0] += '|{}'.format(round(val_sum / len(all_dates), 2))


        table_row.append(todays_price)
        table_row.append(todays_status)

        if pl in money_line_fdp_projections:
            
            table_row.append(money_line_fdp_projections[pl])
        else:
            table_row.append("")

        table_rows.append(table_row)
            

        # all_rows_sorted = sorted(all_rows, key=lambda row: q(row, "salary"))
        # starters = [row for row in all_rows_sorted if q(row, "starter") == "Y"]
        # bench = [row for row in all_rows_sorted if q(row, "starter") == "N"]



    headers = []

    for date in all_dates:
        date = date.replace("/2021", "")
        if len(headers) == 0:
            # headers.append("{} - {}".format(date, "Name"))
            headers.append("{}".format(date))
        else:
            headers.append("{}".format(date))
        headers.append("fdp")
        headers.append("minutes")
        headers.append("val")
        headers.append("salary")
    
    headers.append("cost")
    headers.append("status")
    headers.append("proj")


    print(tabulate(table_rows, headers=headers))
    # import pdb; pdb.set_trace()