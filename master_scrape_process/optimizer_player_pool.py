# -*- coding: UTF-8 -*-
from io import DEFAULT_BUFFER_SIZE
from os import stat
import json
import time
import requests
import sys
import datetime
from tabulate import tabulate
import pandas as pd
from yahoo_optimizer import random_optimizer
import fd_optimizer
import sd_salary_cap_optimizer
import dk_random_optimizer


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

# bulk entry
# prioritize by start time
# trigger player dependencies


# https://www.bigdataball.com/nba-stats-central/
# pass: love4cgB

# make it easier to get the files
# makre sure we're never missing any players
# player superdraft salary cap
# optimize for yahoo fd

name_transform = {"Guillermo Hernangomez": 'Willy Hernangomez', "Cam Thomas": "Cameron Thomas", "Moe Harkless": 'Maurice Harkless', 'Juancho Hernangómez':"Juancho Hernangomez", "Guillermo Hernangómez": 'Willy Hernangomez', 'Timothé Luwawu-Cabarrot': 'Timothe Luwawu-Cabarrot', 'Enes Kanter': 'Enes Freedom', 'Kenyon Martin Jr.': 'KJ Martin'}

def normalize_name(name):
    name = name.replace("  ", " ")
    name = name.replace("’", "'")
    name = name.replace(".", "")
    parts = name.split(" ")

    if len(parts) > 2:
        return "{} {}".format(parts[0], parts[1]).strip()

    if name in name_transform:
        return name_transform[name].strip()

    return name.strip()

team_transform = {"NYK": "NY", "GSW": "GS", "PHX": "PHO", "SAS": "SA", "NOP": "NO"}

def normalize_team_name(team):
    if team in team_transform:
        return team_transform[team]

    return team

def get_dk_price_projection(dk_price):
    max_price = 11500
    min_price = 3000
    dist = (max_price - dk_price)
    projection_factor = 1.0 + 0.2 * (dist / (max_price - min_price))
    projection = (dk_price / 200) * projection_factor
    return projection

def get_dk_dfs_player_pool(player_pool_filename):
    dfs = pd.read_excel(player_pool_filename, sheet_name=None)
    feed = dfs['Sheet1']

    max_price = 11500
    min_price = 3000

    player_names = feed["Player Pool"]
    positions = feed["Unnamed: 2"]
    prices = feed["Unnamed: 3"]
    teams = feed["Unnamed: 4"]
    is_core = feed["Core"]

    name_transform = {}
    # name_transform = {
    #     "Forkan Korkmaz": "Furkan Korkmaz"
    # }

    all_players = {}
    for i in range(len(player_names)):
        player_positions = positions[i]

        if isinstance(player_positions, float):
            print("{} - {}".format(player_positions, player_names[i]))
            continue


        is_player_core = is_core[i] == "X"
        if not is_player_core:
            continue

        

        name = normalize_name(player_names[i])
        
        if name in name_transform:
            name = name_transform[name]

        team = teams[i]
        team = normalize_team_name(team)

        price = prices[i]

        dist = (max_price - price) 

        projection_factor = 1.0 + 0.2 * (dist / (max_price - min_price))
        projection = (price / 200) * projection_factor

        # if "Lillard" in name:
        #     import pdb; pdb.set_trace()

        if is_player_core:
            projection_factor = 1.0 + 0.2 * (dist / (max_price - min_price))
            projection *= projection_factor

        player = [name, prices[i], team, is_player_core, projection]
        all_players[name] = player
    
    return all_players

def get_player_projections(projection_file_name):
    to_read = open(projection_file_name)

    player_to_fp = {}

    lines = to_read.readlines()
    for line in lines:
        parts = line.split("|")
        if len(parts) < 4 or parts[1] != "PP":
            continue
        if parts[4] == "Fantasy Score":
            player_name = normalize_name(parts[2])
            if parts[5].strip() == "REMOVED":
                player_to_fp[player_name] = "*" + str(player_to_fp[player_name]).strip("*")
                continue
            player_to_fp[player_name] = float(parts[5].strip())

    return player_to_fp

def get_player_projections_dk(projection_file_name):
    to_read = open(projection_file_name)

    # load up player stats
    #https://www.nba.com/stats/players/traditional/?PerMode=Totals&sort=PTS&dir=-1
    #https://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season=2021-22&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&TwoWay=0&VsConference=&VsDivision=&Weight=

    name_to_ast_rbd_ratio = {}
    stats_file = open("player_stats.json")
    as_str = stats_file.read()
    for row in json.loads(as_str)['resultSets'][0]['rowSet']:
        name = row[1]
        name = normalize_name(name)
        rbds = row[22]
        assts = row[23]
        if rbds + assts > 0:
            name_to_ast_rbd_ratio[name] = rbds / (assts + rbds)

    player_to_fp = {}
    player_to_stat_to_value = {}

    lines = to_read.readlines()
    for line in lines:
        parts = line.split("|")
        if len(parts) < 4 or parts[1] != "DK":
            continue

        player_name = normalize_name(parts[2]).strip()
        stat = parts[4]
        stat_val = parts[5]
        if "REMOVED" in stat_val:
            if stat in player_to_stat_to_value[player_name]:
                del player_to_stat_to_value[player_name][stat]
            continue
        value = float(stat_val.strip().split(' ')[0])
        if not player_name in player_to_stat_to_value:
            player_to_stat_to_value[player_name] = {}

        if not stat in player_to_stat_to_value[player_name]:
            player_to_stat_to_value[player_name][stat] = {}

        player_to_stat_to_value[player_name][stat] = value
    
    for player, stat_to_values in player_to_stat_to_value.items():

        if not player in name_to_ast_rbd_ratio:
            # print("DK PROJCETIONS MISSING: {}".format(player))
            continue
        rbds_to_assts_plus_rbds = name_to_ast_rbd_ratio[player]
        if not 'Points' in stat_to_values:
            continue
        
        pts = stat_to_values['Points']

        if not 'Points + Assists + Rebounds' in stat_to_values:
            continue

        PAR = stat_to_values['Points + Assists + Rebounds']
        AR = PAR - pts
        
        if not 'Steals + Blocks' in stat_to_values:
            continue

        SB = stat_to_values['Steals + Blocks']
        AR = PAR - pts
        factor = 1.2 * rbds_to_assts_plus_rbds + 1.5 * (1 - rbds_to_assts_plus_rbds)
        projected = pts + AR * factor + SB * 3

        player_to_fp[player] = projected

    return player_to_fp


def get_player_projections_awesemo(projection_file_name):
    to_read = open(projection_file_name)
  
    player_to_fp = {}
    player_to_stat_to_value = {}

    lines = to_read.readlines()
    for line in lines:
        parts = line.split("|")
        if len(parts) < 4 or parts[1] != "Awesemo":
            continue

        player_name = normalize_name(parts[2]).strip()
        stat = parts[4]
        stat_val = parts[5]
        if "REMOVED" in stat_val:
            if stat in player_to_stat_to_value[player_name]:
                del player_to_stat_to_value[player_name][stat]
            continue
        value = float(stat_val.strip().split(' ')[0])
        if not player_name in player_to_stat_to_value:
            player_to_stat_to_value[player_name] = {}

        if not stat in player_to_stat_to_value[player_name]:
            player_to_stat_to_value[player_name][stat] = {}

        player_to_stat_to_value[player_name][stat] = value
    
    for player, stat_to_values in player_to_stat_to_value.items():
        if not "Points" in stat_to_values:
            continue
        pts = stat_to_values['Points']
        if not 'Rebounds' in stat_to_values:
            continue
        rbds = stat_to_values['Rebounds']
        if not 'Assists' in stat_to_values:
            continue
        asts = stat_to_values['Assists']
        if not 'Blocks' in stat_to_values:
            continue
        blks = stat_to_values['Blocks']
        stls = stat_to_values['Steals']

        projected = pts + rbds * 1.2 + asts * 1.5 + blks * 3 + stls * 3
        player_to_fp[player] = projected

    return player_to_fp


def get_player_projections_betMGM(projection_file_name):
    to_read = open(projection_file_name)
  
    player_to_fp = {}
    player_to_stat_to_value = {}

    lines = to_read.readlines()
    for line in lines:
        parts = line.split("|")
        if len(parts) < 4 or parts[1] != "betMGM":
            continue

        player_name = normalize_name(parts[2]).strip()
        stat = parts[4]
        stat_val = parts[5]
        if "REMOVED" in stat_val:
            if stat in player_to_stat_to_value[player_name]:
                del player_to_stat_to_value[player_name][stat]
            continue
        value = float(stat_val.strip().split(' ')[0])
        if not player_name in player_to_stat_to_value:
            player_to_stat_to_value[player_name] = {}

        if not stat in player_to_stat_to_value[player_name]:
            player_to_stat_to_value[player_name][stat] = {}

        player_to_stat_to_value[player_name][stat] = value
    
    for player, stat_to_values in player_to_stat_to_value.items():
        if not "points" in stat_to_values:
            continue
        pts = stat_to_values['points']
        if not 'rebounds' in stat_to_values:
            continue
        rbds = stat_to_values['rebounds']
        if not 'assists' in stat_to_values:
            continue
        asts = stat_to_values['assists']
        if not 'blocks' in stat_to_values:
            continue
        blks = stat_to_values['blocks']
        if not 'steals' in stat_to_values:
            continue
        stls = stat_to_values['steals']

        projected = pts + rbds * 1.2 + asts * 1.5 + blks * 3 + stls * 3
        player_to_fp[player] = projected

    return player_to_fp

def get_player_projections_caesars(projection_file_name):
    to_read = open(projection_file_name)
  
    player_to_fp = {}
    player_to_stat_to_value = {}

    lines = to_read.readlines()
    for line in lines:
        parts = line.split("|")
        if len(parts) < 4 or parts[1] != "Caesars":
            continue

        player_name = normalize_name(parts[2]).strip()
        stat = parts[4]
        stat_val = parts[5]
        if "REMOVED" in stat_val:
            if stat in player_to_stat_to_value[player_name]:
                del player_to_stat_to_value[player_name][stat]
            continue
        value = float(stat_val)
        if not player_name in player_to_stat_to_value:
            player_to_stat_to_value[player_name] = {}

        if not stat in player_to_stat_to_value[player_name]:
            player_to_stat_to_value[player_name][stat] = {}

        player_to_stat_to_value[player_name][stat] = value
    
    for player, stat_to_values in player_to_stat_to_value.items():
        if not "Points" in stat_to_values:
            continue
        pts = stat_to_values['Points']
        if not 'Rebounds' in stat_to_values:
            continue
        rbds = stat_to_values['Rebounds']
        if not 'Assists' in stat_to_values:
            continue
        asts = stat_to_values['Assists']
        if not 'Blocks' in stat_to_values:
            continue
        blks = stat_to_values['Blocks']
        if not 'Steals' in stat_to_values:
            continue
        stls = stat_to_values['Steals']

        projected = pts + rbds * 1.2 + asts * 1.5 + blks * 3 + stls * 3
        player_to_fp[player] = projected

    return player_to_fp


def get_fd_slate_players(fd_slate_file_name, exclude_injured_players=True):
    all_players = {}
    salaries = open(fd_slate_file_name)
    lines = salaries.readlines()
    found_count = 0

    for line in lines[1:]:
        parts = line.split(',')
        full_name = normalize_name(parts[3])

        positions = parts[1]
        salary = parts[7]
        team = parts[9]
        team = normalize_team_name(team)
        status = parts[11]
        # print(full_name)
        if status == "O" and exclude_injured_players:
            continue
        name = full_name
        all_players[name] = [name, positions, float(salary), team, status]
        
    return all_players

def get_dk_slate_players(dk_slate_file_name):
    all_players = {}
    #'SG/SF,Rodney Hood (20071564),Rodney Hood,20071564,SG/SF/F/G/UTIL,3000,MIL@PHI 11/09/2021 07:30PM ET,MIL,8.88\n'
    all_lines = open(dk_slate_file_name).readlines()
    for line in all_lines[1:]:
        parts = line.split(",")
        positions = parts[0]
        name = normalize_name(parts[2])
        salary = parts[5]
        game_info = parts[6]
        team = parts[7]
        team = normalize_team_name(team)

        player_id = parts[3]
        all_players[name] = [name, positions, float(salary), team, player_id]

    return all_players


def get_sd_slate_players(sd_slate_file_name):
    all_players = {}
    sd_file = open(sd_slate_file_name, "r")
    lines = sd_file.readlines()
    for line in lines[1:]:
        parts = line.split(",")
        pos = parts[0].strip('"')
        team = parts[7].strip('"')
        team = normalize_team_name(team)
        name = normalize_name(parts[2].strip('"'))
        mult = float(parts[5].strip('"'))
        player_id = float(parts[3].strip('"'))

        if name in all_players:
            all_players[name][1] += "/" + pos
        else:
            all_players[name] = [name, pos, mult, team, player_id]

    return all_players
        

def get_sd_salary_cap_slate_players(sd_salary_cap_slate_file_name):
    all_players = {}
    sd_file = open(sd_salary_cap_slate_file_name, "r")
    lines = sd_file.readlines()
    for line in lines[1:]:
        parts = line.split(",")
        name = parts[2].strip('"')
        name = normalize_name(name)
        positions = parts[1].strip('"')
        team = parts[7].strip('"')
        team = normalize_team_name(team)
        salary = parts[5].strip('"')
        all_players[name] = [name, positions, float(salary), team]
        
    return all_players


def get_yahoo_slate_players(yahoo_slate_file_name):
    offset = -2
    all_players = {}
    yahoo_file = open(yahoo_slate_file_name, "r")
    lines = yahoo_file.readlines()
    first_line = lines[0]
    parts = first_line.split(",")
    # for part in parts:
    #     print("{} - {}".format(idx, part))
    #     idx += 1
    for line in lines[1:]:
        parts = line.split(",")
        if parts[12 + offset] == '" "' or parts[13 + offset] == '" "':
            continue
        name = "{} {}".format(parts[13 + offset], parts[14 + offset])
        name = normalize_name(name)
        position = parts[16 + offset]
        team = parts[17 + offset]
        team = normalize_team_name(team)
        salary = parts[21 + offset]
        try:
            all_players[name] = [name, position, float(salary), team]
        except:
            import pdb; pdb.set_trace()
        
    return all_players

def get_all_games(dk_slate_file_name):
    all_games = []
    all_lines = open(dk_slate_file_name).readlines()
    for line in all_lines[1:]:
        parts = line.split(",")
        game_info = parts[6]
        if not game_info in all_games:
            all_games.append(game_info)

    return all_games

def get_all_games_fd(fd_slate_file_name):
    all_games = []
    all_lines = open(fd_slate_file_name).readlines()

    for line in all_lines[1:]:
        parts = line.split(",")
        game_info = parts[8]
        if not game_info in all_games:
            all_games.append(game_info)

    return all_games

def load_season_data(all_teams=None):

    matched_team_names = []

    if all_teams != None:
        for team in all_teams:
            team = normalize_team_name(team)
            matched_team_names.append(team_abbr_dict[team])

    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)

    filename = "~/Downloads/season_data/{}-{}-{}-nba-season-dfs-feed.xlsx".format(str(yesterday.month).zfill(2), str(yesterday.day).zfill(2), yesterday.year)

    dfs = pd.read_excel(filename, sheet_name=None)
    if 'NBA-DFS-SEASON-FEED' in dfs:
        feed = dfs['NBA-DFS-SEASON-FEED']
    else:
        feed = dfs['NBA-DFS-SEASON']
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
        team = normalize_team_name(team)
        opp = row["Unnamed: 6"]
        starter = row["Unnamed: 7"]
        minutes = row["Unnamed: 9"]
        rest = row["Unnamed: 11"]
        positions = row["Unnamed: 13"]
        salary = row["Unnamed: 16"]
        fdp = row["Unnamed: 19"]

        if len(matched_team_names) > 0 and team not in matched_team_names:
            continue


        if not team in team_to_date_to_rows:
            team_to_date_to_rows[team] = {}

        if not date in team_to_date_to_rows[team]:
            team_to_date_to_rows[team][date] = []

        team_to_date_to_rows[team][date].append(row)


    team_to_date_to_rows_new = {}
    for team, date_to_rows in team_to_date_to_rows.items():
        all_past_dates = date_to_rows.keys()
        all_past_dates_sorted = sorted(all_past_dates, reverse=True)

        date_to_rows_new = {}
        for date in all_past_dates:
            if date in all_past_dates_sorted:
                date_to_rows_new[date] = date_to_rows[date]
        
        team_to_date_to_rows_new[team] = date_to_rows_new

    return team_to_date_to_rows_new


def q(row, key, salary=None):
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

all_starters_rw = []
questionable_non_starters_rw = []

# (all_starters_rw, _, questionable_non_starters_rw, _) = roto_wire_scrape.scrape_lineups()
# for each game
# print every player playing in that game

dk_positions_mapper = {"PG": ["PG", "G", "UTIL"], "SG": ["SG", "G", "UTIL"], "SF": ["SF", "F", "UTIL"], "PF": ["PF", "F", "UTIL"], "C": ["C", "UTIL"]}

def get_all_teams():
    all_teams = []
    for game in all_games:
        matchup = game.split(' ')[0]
        teams = matchup.split("@")
        for team in teams:
            all_teams.append(team)
    return all_teams

def get_slate_to_team_to_players(dK_players, yahoo_players):
    slate_to_team_to_players = {}
    for game in all_games:
        slate_to_team_to_players[game] = {}
        matchup = game.split(' ')[0]
        teams = matchup.split("@")
        
        for team in teams:
            team = normalize_team_name(team)
            player_slate_info = {}
            slate_to_team_to_players[game][team] = player_slate_info
            for name, player in fd_players.items():
                name_normalized = normalize_name(name)
                if player[3] == team:
                    assert name_normalized not in player_slate_info
                    player_slate_info[name_normalized] = [name_normalized, player[3], player[1], player[2]]
            
            for name, player in dk_players.items():
                name_normalized = normalize_name(name)
                if player[3] == team:
                    if not name_normalized in player_slate_info:
                        player_slate_info[name_normalized] = [name_normalized, player[3], 0, 0]
                    
                    player_slate_info[name_normalized] += [dk_players[name][1], dk_players[name][2]]

            for name, player in sd_players.items():
                if player[3] == team:
                    if not name in sd_players or name not in player_slate_info:
                        if name in fd_players:
                            import pdb; pdb.set_trace()
                        assert name not in fd_players
                        continue

                    player_slate_info[name] += [sd_players[name][1], sd_players[name][2]]

            for name, player in yahoo_players.items():
                name_normalized = normalize_name(name)
                if player[3] == team:
                    if not name in yahoo_players or name not in player_slate_info:
                        if name in yahoo_players:
                            import pdb; pdb.set_trace()
                        assert name not in yahoo_players
                        continue
                    
                    player_slate_info[name] += [yahoo_players[name][1], yahoo_players[name][2]]


            # for name, player in sd_salary_cap_players.items():
            #     if player[3] == team:
            #         if not name in sd_salary_cap_players or name not in sd_salary_cap_players:
            #             if name in sd_salary_cap_players:
            #                 import pdb; pdb.set_trace()
            #             assert name not in sd_salary_cap_players
            #             continue
                    
            #         try:
            #             player_slate_info[name] += [sd_salary_cap_players[name][1], sd_salary_cap_players[name][2]]
            #         except:
            #             print("Nmae not found: {}".format(name))
            #             continue


    return slate_to_team_to_players

def get_player_past_game_stats(player_name, team, season_data, fd_price, dk_price, sd_factor, fd_positions, dk_positions, sd_positions, yahoo_position, player_pool_projection):
    to_return = []
    team = team_abbr_dict[team]
    team = normalize_team_name(team)
    dates = season_data[team].keys()
    dates_sorted = sorted(dates)
    l1 = dates_sorted[-1]
    l3 = dates_sorted[-3:]
    l5 = dates_sorted[-5:]


    total_minutes = 0
    total_fdp = 0
    status_string = ""
    max_fdp = 0
    for date in l3:
        game_rows = season_data[team][date]
        matched_rows = [a for a in game_rows if q(a, "name") == player_name]
        assert len(matched_rows) <= 1
        if len(matched_rows) == 0:
            
            status_string += "O"
            continue

        matched_row = matched_rows[0]
        played_minutes = q(matched_row, "minutes")
        status = "O"
        if q(matched_row, "starter") == "Y":
            status = "S"
        elif played_minutes > 0:
            status = "B"

        total_minutes += played_minutes
        status_string += status
        fdp = q(matched_row, "fdp")
        if fdp > max_fdp:
            max_fdp = fdp
        total_fdp += fdp
    
    fdp_per_minute = 0
    if total_minutes == 0:
        assert total_fdp == 0
    else:
        fdp_per_minute = round(total_fdp / float(total_minutes), 2)

    to_return += ["{},{},{},{}".format(fd_positions, dk_positions, sd_positions, yahoo_position), round(total_minutes / 3.0, 2), round(total_fdp / 3.0, 2), max_fdp, fdp_per_minute, status_string, fd_price, dk_price, sd_factor, player_pool_projection]

    
    
    return to_return

dk_players_by_position = {}
fd_players_by_position = {}
sd_players_by_position = {}
sd_salary_cap_by_position = {}
yahoo_players_by_position = {}


def get_val_from_row(new_row):
    # dk_proj = new_row[10]
    # if isinstance(dk_proj, float):
    #     return dk_proj

    val = new_row[14]
    if not (isinstance(val, float) or isinstance(val, int)):
        val = new_row[13]
        if not (isinstance(val, float) or isinstance(val, int)):
            val = new_row[12]
            if not (isinstance(val, float) or isinstance(val, int)):
                val = new_row[10]
                if not (isinstance(val, float) or isinstance(val, int)):
                    return 0.0

    return val

def consume_row_by_position(new_row, team, team_to_start_time_idx, team_matchup):
    # sd_salary cap
    # sd_pos = new_row[1].split(',')[2]
    # sd_pos = "unknown"

    # if not sd_pos in sd_salary_cap_by_position:
    #     sd_salary_cap_by_position[sd_pos] = []

    # # import pdb; pdb.set_trace()
    
    # name = new_row[0]
    # factor = new_row[9]

    # cost1 = new_row[10]
    # cost2 = new_row[11]
    # val = 0



    # if isinstance(cost1, float) and isinstance(cost2, float):
    #     val = (cost1 + cost2) / 2
    # elif isinstance(cost1, float):
    #     val = cost1
    # elif isinstance(cost2, float):
    #     val = cost2
    
    # if not name in sd_salary_cap_players:
    #     print("not found: {}".format(name))    
    # else:
    #     price = sd_salary_cap_players[name][2]
    #     pl = [name, sd_pos, price, team, val]
    #     if val > 0:
    #         sd_salary_cap_by_position[sd_pos].append(pl)

    # Yahoo
    positions_mapper = {"PG": ["PG", "G", "UTIL"], "SG": ["SG", "G", "UTIL"], "SF": ["SF", "F", "UTIL"], "PF": ["PF", "F", "UTIL"], "C": ["C", "UTIL"]}
    pos_root = new_row[1].split(',')[3]
    if pos_root != "":
        all_positions = positions_mapper[pos_root]
        for pos in all_positions:
            if not pos in yahoo_players_by_position:
                yahoo_players_by_position[pos] = []
            
            name = new_row[0]

            price = yahoo_players[name][2]
            
            val = get_val_from_row(new_row)
            if val == 0.0:
                continue
            
            pl = dk_random_optimizer.Player(name, pos, price, team, val)
            yahoo_players_by_position[pos].append(pl) 

    # SD
    sd_pos = new_row[1].split(',')[2]

    if not sd_pos in sd_players_by_position:
        sd_players_by_position[sd_pos] = []
    
    name = new_row[0]
    factor = new_row[9]

    val = get_val_from_row(new_row)
    
    val *= factor
    pl = [name, sd_pos, team, val]
    sd_players_by_position[sd_pos].append(pl)

    # FD
    fd_pos = new_row[1].split(',')[0]
    for pos in fd_pos.split("/"):
        if not pos in fd_players_by_position:
            fd_players_by_position[pos] = []
        
        name = new_row[0]
        price = new_row[7]

        val = get_val_from_row(new_row)

        if val == 0:
            continue

        pl = dk_random_optimizer.Player(name, pos, price, team, val, game_start_slot=0, matchup=team_matchup)
        fd_players_by_position[pos].append(pl)



    # DK
    dk_pos = new_row[1].split(',')[1]
    all_positions = []
    for pos in dk_pos.split("/"):
        try:
            more_pos = dk_positions_mapper[pos]
        except:
            continue
            import pdb; pdb.set_trace()
        for pos2 in more_pos:
            if not pos2 in all_positions:
                all_positions.append(pos2)

    for pos in all_positions:
        if not pos in dk_players_by_position:
            dk_players_by_position[pos] = []
        
        name = new_row[0]

        price = new_row[8]

        val = get_val_from_row(new_row)

        if val == 0:
            continue
        
        if price > 0:
            pl = dk_random_optimizer.Player(name, pos, price, team, val, team_to_start_time_idx[team])
            dk_players_by_position[pos].append(pl)
        else: 
            print("WARNING DK PLAYER NO PRICE: {}, {}, {}".format(name, price, val))


def print_all_player_projections(projections):
    name_team_val = []
    for player, data in dk_players.items():
        if not player in projections:
            continue
        proj = round(float(projections[player]), 2)
        name_team_val.append([player, data[3], proj, data[2], round(proj / float(data[2]) * 1000, 2)])
    
    name_team_val_sorted = sorted(name_team_val, key=lambda a: a[4], reverse=True)
    as_str = tabulate(name_team_val_sorted, headers=["name", "team", "projection", "price", "value"])
    print(as_str)
    __import__('pdb').set_trace()


def print_rosters_and_projections(excluded_players, slate_name=""):
    current_date = datetime.datetime.now()
    projection_file_name = "money_line_scrape_{}_{}_{}.txt".format(current_date.month, current_date.day, current_date.year)
    pp_fdp_projections = get_player_projections(projection_file_name)
    dk_fdp_projections = get_player_projections_dk(projection_file_name)
    awesemo_fdp_projections = get_player_projections_awesemo(projection_file_name)
    betMGM_fdp_projections = get_player_projections_betMGM(projection_file_name)

    caesars_fdp_projections = get_player_projections_caesars(projection_file_name)
    # print_all_player_projections(caesars_fdp_projections)
    output_file = open("money_line_scrapes/projections_{}_{}_{}_{}.txt".format(current_date.month, current_date.day, current_date.year, slate_name), "w")
    # __import__('pdb').set_trace()
    matched_projection_count = 0
    all_start_times = []
    team_to_start_time = {}
    team_to_start_time_idx = {}
    for slate in slate_to_team_to_players.keys():
        slate_parts = slate.split(' ')
        teams = slate_parts[0].split('@')
        start_time = ''
        if len(slate_parts) > 1:
            start_time = slate_parts[2]
        for team in teams:
            team = normalize_team_name(team)
            team_to_start_time[team] = start_time
        if not start_time in all_start_times:
            all_start_times.append(start_time)

    all_start_times_sorted = sorted(all_start_times)
    for team, start_time in team_to_start_time.items():
        idx = all_start_times_sorted.index(start_time)
        team_to_start_time_idx[team] = idx

    for slate, slate_data in slate_to_team_to_players.items():
        print(slate)
        
        for team, player_data in slate_data.items():
            output_file.write("\nTEAM: {}\n".format(team))
            print("\nTEAM: {}".format(team))
            starter_str = "Starters: "
            starter_names_rw = []
            for pl in all_starters_rw:
                if pl[1] == team:
                    starter_str += "{} {}, ".format(pl[0], pl[2])
                    starter_names_rw.append((pl[0], pl[2]))


            print(starter_str)
            output_file.write(starter_str + "\n")

            bench_str = "Other: "
            other_names_rw = []
            for pl in questionable_non_starters_rw:
                if pl[1] == team:
                    bench_str += "{} {}, ".format(pl[0], pl[2])
                    other_names_rw.append((pl[0], pl[2]))

            print(bench_str)

            all_rows = []
            for player, player_data in player_data.items():
                fd_price = player_data[3]
                dk_price = 0
                if len(player_data) > 5:
                    dk_price = player_data[5]
                sd_factor = 0
                if player in sd_players:
                    sd_factor = sd_players[player][2]
                
                fd_positions = ''
                dk_positions = ''
                sd_positions = ''
                yahoo_positions = ''
                if player in fd_players:
                    fd_positions = fd_players[player][1]

                if player in dk_players:
                    dk_positions = dk_players[player][1]
                
                if player in sd_players:
                    sd_positions = sd_players[player][1]

                if player in yahoo_players:
                    yahoo_positions = yahoo_players[player][1]

                if fd_price == 0:
                    continue

                
                player_pool_projection = ''
                if player in dk_dfs_player_pool:
                    player_pool_projection = round(dk_dfs_player_pool[player][-1], 2)

                game_stats = get_player_past_game_stats(player, player_data[1], season_data, fd_price, dk_price, sd_factor, fd_positions, dk_positions, sd_positions, yahoo_positions, player_pool_projection)

                normalized_name = normalize_name(player)
                pp_projection = ""
                if normalized_name in pp_fdp_projections:
                    pp_projection = pp_fdp_projections[normalized_name]
                    matched_projection_count += 1

                if normalized_name in fd_players and fd_players[normalized_name][4].strip() == "O":
                    pp_projection = "0"

                if normalized_name in excluded_players:
                    pp_projection = 0.0

                game_stats.append(pp_projection)
                
                #-------
                dk_projection = ""
                if normalized_name in dk_fdp_projections:
                    dk_projection = round(dk_fdp_projections[normalized_name], 2)

                if normalized_name in excluded_players:
                    dk_projection = 0.0

                game_stats.append(dk_projection)


                #-------
                betMGM_projection = ""
                if normalized_name in betMGM_fdp_projections:
                    betMGM_projection = round(betMGM_fdp_projections[normalized_name], 2)

                if normalized_name in excluded_players:
                    betMGM_projection = 0.0

                game_stats.append(betMGM_projection)



                #-------
                caesars_projection = ""
                if normalized_name in caesars_fdp_projections:
                    caesars_projection = round(caesars_fdp_projections[normalized_name], 2)

                if normalized_name in excluded_players:
                    caesars_projection = 0.0

                game_stats.append(caesars_projection)

                # #-------
                # awesemo_projection = ""
                # if normalized_name in awesemo_fdp_projections:
                #     awesemo_projection = round(awesemo_fdp_projections[normalized_name], 2)

                # if normalized_name in excluded_players:
                #     awesemo_projection = 0.0

                # game_stats.append(awesemo_projection)

                new_row = [player]
                new_row += game_stats
                all_rows.append(new_row)
                consume_row_by_position(new_row, team, team_to_start_time_idx, slate)
                
            as_str = tabulate(all_rows, headers=["name", "fd,dk,sd pos", "ave min", "ave fp", "max fp", "fp/min", "L3", "fdp", "dkp", "SD", "DK DFS", "PP proj.", "DK Proj", "betMGM", "caesars"])
            output_file.write(as_str + "\n\n")
            print(as_str)

    arbitrage_rows = []
    ##search for arbitrage:
    ARBITRAGE_CUTTOFF = 5
    for name, projection in pp_fdp_projections.items():
        if not isinstance(projection, float):
            continue

        if name in dk_fdp_projections and name in awesemo_fdp_projections:
            v1 = round(dk_fdp_projections[name], 2)
            v2 = round(awesemo_fdp_projections[name], 2)
            diff1 = round(v1 - projection, 2)
            diff2 = round(v2 - projection, 2)
            if abs(diff1) > 3 or abs(diff2) > ARBITRAGE_CUTTOFF:
                # print("{} - pp: {} dk: {} awesome: {} = {}, {}".format(name, projection, v1, v2, diff1, diff2))
                arbitrage_rows.append([name, projection, v1, v2, diff1, diff2])

            continue
        
        if name in dk_fdp_projections:
            v1 = round(dk_fdp_projections[name], 2)
            diff1 = round(v1 - projection, 2)
            if abs(diff1) > ARBITRAGE_CUTTOFF:
                # print("{} - pp: {} dk: {} = {}".format(name, projection, v1, diff1))
                arbitrage_rows.append([name, projection, v1, 0, diff1, 0])

        if name in awesemo_fdp_projections:
            v2 = round(awesemo_fdp_projections[name], 2)
            diff2 = round(v2 - projection, 2)
            if abs(diff2) > ARBITRAGE_CUTTOFF:
                # print("{} - pp: {} awesemo: {} = {}".format(name, projection, v2, diff2))
                arbitrage_rows.append([name, projection, 0, v2, 0, diff2])



    arbitrage_rows_sorted = sorted(arbitrage_rows, key=lambda a: min(a[4], a[5]), reverse=True)
    print(["Name", "PP proj", "DK proj", "Awesemo proj", "diff1", 'diff2'])
    for row in arbitrage_rows_sorted:
        print(row)
            # pp_fdp_projections = get_player_projections(projection_file_name)   
            # dk_fdp_projections = get_player_projections_dk(projection_file_name)
            # awesemo_fdp_projections = get_player_projections_awesemo(projection_file_name)


def generate_dk_lineups_file(rosters, dk_players, name):
    output_file = open("/Users/amichailevy/Downloads/lineups_{}_{}.csv".format(datetime.datetime.now().strftime('%Y%m%d-%H%M%S'), name), "w")
    output_file.write("PG,SG,SF,PF,C,G,F,UTIL\n")
    for roster in rosters:
        all_ids = []
        for player in roster.players:
            name = player.name
            player_id = dk_players[name][4]
            all_ids.append(player_id)
            
        output_file.write(",".join(all_ids) + "\n")
    output_file.close()

def generate_sd_lineups_file(rosters, sd_players, template_filename):
    template_file = open(template_filename, "r")
    template_file_lines = template_file.readlines()

    entry_ids = []
    contest_names = []
    for line in template_file_lines[1:]:
        parts = line.split(",")
        first_cell = parts[0].strip('"')
        if first_cell == "":
            break
        entry_ids.append(first_cell)
        contest_names.append(parts[1].strip('"'))

    assert len(entry_ids) == len(rosters)
    output_file = open("/Users/amichailevy/Downloads/SD_lineups_{}.csv".format(datetime.datetime.now().strftime('%Y%m%d-%H%M%S')), "w")
    output_file.write("EntryID,Contest Name,G,G,G,F,F,F,C\n")
    for i in range(len(entry_ids)):
        to_write = []
        to_write.append(entry_ids[i])
        to_write.append(contest_names[i])
        roster = rosters[i]
        for player in roster:
            player_id = str(int(sd_players[player[0]][4]))
            to_write.append(player_id)


        output_file.write(",".join(to_write) + "\n")

    output_file.close()

def generate_sd_lineups():
    # TODO: manually exclude used players to get more diverse lineups
    all_sd_players = []
    for pos, players in sd_players_by_position.items():
        all_sd_players += players


    players_sorted = sorted(all_sd_players, key=lambda a: a[3], reverse=True)
    for pl in players_sorted:
        if pl[3] < 1:
            continue
        print(pl)


    roster_count = 10

    sd_positions = ["G", "G", "G", "F","F", "F", "C"]

    roster_set = []
    roster_set_keys = []

    VAL_DELTA = 0.96

    while True:
        players_sorted = sorted(all_sd_players, key=lambda a: a[3], reverse=True)
        current_roster = []
        current_roster_names = []
        for inspection_pos in sd_positions:
            for player in players_sorted:
                pl_name = player[0]
                if pl_name in current_roster_names:
                    continue
                pl_pos = player[1]
                if inspection_pos in pl_pos:
                    current_roster.append(player)
                    current_roster_names.append(pl_name)
                    break
                pass
        
        roster_key = ",".join(current_roster_names)
        if roster_key in roster_set_keys:
            for player in current_roster:
                player[3] *= VAL_DELTA

        else:
            roster_set.append(current_roster)
            roster_set_keys.append(roster_key)
            if len(roster_set) >= roster_count:
                break

    for roster in roster_set_keys:
        print(roster)

    # generate_sd_lineups_file(roster_set, sd_players, "/Users/amichailevy/Downloads/SD-NBA-Main-Multiplier-lineuptemplate.csv")


def adjust_players_by_position(by_position, new_player_val, team_adjustment):
    matched_names = []
    for pos, players in by_position.items():
        for player in players:
            if player.name in new_player_val:
                player.val = new_player_val[player.name]
                matched_names.append(player.name)

            if player.team in team_adjustment:
                player.val *= team_adjustment[player.team]

    for name in new_player_val.keys():
        if not name in matched_names:
            player_info = dk_players[name]
            positions = player_info[1]
            price = player_info[2]
            team = player_info[3]
            all_positions = []
            for pos in positions.split("/"):
                try:
                    more_pos = dk_positions_mapper[pos]
                except:
                    import pdb; pdb.set_trace()
                for pos2 in more_pos:
                    if not pos2 in all_positions:
                        all_positions.append(pos2)

            for pos in all_positions:
                val = new_player_val[name]
                pl = dk_random_optimizer.Player(name, pos, price, team, val)
                dk_players_by_position[pos].append(pl)


def fd_optimize(file_path, slate_name, slate_type, locks=[], excludes=[]):
    download_folder = "/Users/amichailevy/Downloads/"
    folder = download_folder + "player_lists/"
    
    #main
    fd_slate = (folder + file_path, slate_type, slate_name)



    fd_slate_file = fd_slate[0]
    fd_players = get_fd_slate_players(fd_slate_file)

    excluded_players = []
    
    print_rosters_and_projections(excluded_players, slate_name)

    if fd_slate[1] == 'single':
        result = fd_optimizer.generate_roster_for_single_game(fd_players_by_position, to_exclude=[])
    elif fd_slate[1] == 'full':
        resolved_rosters = fd_optimizer.generate_unique_rosters(fd_players_by_position, 1)
    else:
        assert False


if __name__ == "__main__":
    download_folder = "/Users/amichailevy/Downloads/"
    folder = download_folder + "player_lists/"
    # ------
    dk_slate_file = folder + "DKSalaries_12_28_21.csv"

    
    
    #main - TODO: 1 - 1/8/21
    path = "FanDuel-NBA-2022 ET-01 ET-08 ET-69912-players-list.csv"

    fd_slate = (folder + path, "full", "main")
    

    # sd_slate_file = folder + "SD-111321-NBA-Main-Multiplier-playerlist.csv"
    # sd_salary_cap_slate_file = folder + "SD-111521-NBA-Main-Salary-playerlist.csv"
    yahoo_slate_file = folder + "Yahoo_DF_contest_lineups_insert_template_11_20_21.csv"
    player_pool_path = download_folder + "DK_DFS_player_pools/UPDATED NBA 12.6.xlsx"


    fd_slate_file = fd_slate[0]
    fd_players = get_fd_slate_players(fd_slate_file, exclude_injured_players=False)
    dk_players = get_dk_slate_players(dk_slate_file)
    # dk_players = {}
    
    # sd_players = get_sd_slate_players(sd_slate_file)
    sd_players = {}
    # yahoo_players = get_yahoo_slate_players(yahoo_slate_file)
    yahoo_players = {}
    # sd_salary_cap_players = get_sd_salary_cap_slate_players(sd_salary_cap_slate_file)
    sd_salary_cap_players = {}

    dk_dfs_player_pool = get_dk_dfs_player_pool(player_pool_path)
    # dk_dfs_player_pool = {}
    # all_games = get_all_games(dk_slate_file)
    all_games = get_all_games_fd(fd_slate_file)

    abbr_file = open("team_names.txt")
    lines = abbr_file.readlines()
    team_abbr_dict = {}
    team_abbr_dict2 = {}
    for line in lines:
        parts = line.split(',')
        abbr_name = parts[1].strip()
        team_abbr_dict[parts[1].strip()] = parts[0]
        team_abbr_dict2[parts[0]] = parts[1].strip()

    all_teams = get_all_teams()
    slate_to_team_to_players = get_slate_to_team_to_players(dk_players, yahoo_players)
    season_data = load_season_data(all_teams)
    assert len(season_data.keys()) % 2 == 0

    excluded_players = []
    
    print_rosters_and_projections(excluded_players, fd_slate[2])

    
    # fd_optimizer.modify_roster(fd_players_by_position, "Bobby Portis,Tony Bradley,Pascal Siakam,Scottie Barnes,Khris Middleton,Jalen Brunson,Josh Giddey,Terry Rozier,LaMelo Ball", [])

    # check the current time
    # pass in a starting roster
    # adjustment_dict = {"Troy Brown": 40}
    # adjust_players_by_position(dk_players_by_position, adjustment_dict, {})
    # roster_str = "Josh Giddey,Jalen Suggs,DeAndre' Bembry,Giannis Antetokounmpo,Myles Turner,Dejounte Murray,Georges Niang,Steven Adams"
    # dk_random_optimizer.modify_existing_roster(dk_players_by_position, roster_str, locked_teams=["BKN", "OKC", "ATL", "ORL", "MIL", "PHX", "SAS"])

    # dk_players_by_position['UTIL'].append(dk_random_optimizer.Player("Luka Garza", 'UTIL', 3000, "", 100))
    # resolved_rosters = dk_random_optimizer.generate_unique_rosters(dk_players_by_position, 1)
    # generate_dk_lineups_file(resolved_rosters, dk_players, "main")

    __import__('pdb').set_trace()
    # assert False
    print("-----")
    # TODO 2 - 1/8/21
    start_time_to_teams = {
        7: ["UTA", "IND", "ORL", "DET", "MIL", "CHA"],
        7.5: ["NY", "BOS"],
        9: ["MIA", "PHO"]
    }


    # # TODO 3 - 1/8/21
    # upload_template_path = "/Users/amichailevy/Downloads/FanDuel-NBA-2022-01-08-69912-entries-upload-template.csv"
    # fd_optimizer.generate_MME_ensemble(fd_players_by_position, upload_template_path, start_time_to_teams)
    # assert False

    # TODO 4 - 1/8/21
    current_time = 7.6
    
    # TODO 5 - 1/8/21
    to_re_optimize = "/Users/amichailevy/Downloads/FanDuel-NBA-2022-01-08-69912-entries-upload-template (2).csv"
    fd_optimizer.regenerate_MME_ensemble(fd_players_by_position, to_re_optimize, start_time_to_teams, current_time)
    
    assert False

    print("----\n------\n------\n-------\n")


    if fd_slate[1] == 'single':
        result = fd_optimizer.generate_roster_for_single_game(fd_players_by_position, to_exclude=[])
        print(result)
    elif fd_slate[1] == 'full':
        resolved_rosters = fd_optimizer.generate_unique_rosters(fd_players_by_position, 1, [])
        # resolved_rosters = fd_optimizer.generate_unique_rosters(fd_players_by_position, 1, [])
    elif fd_slate[1] == 'three':
        seen_names = []
        all_players = []
        for pos, players in fd_players_by_position.items():
            for player in players:
                player_name = player.name
                if not player_name in seen_names:
                    all_players.append(player)
                    seen_names.append(player_name)
        result = fd_optimizer.three_man_optimizer(all_players)
        print(result)
    else:
        assert False
    # random_optimizer(yahoo_players_by_position)
    # print("-----")



    # all_players = sd_salary_cap_by_position['unknown']

    # all_players_sorted = sorted(all_players, key=lambda a: a[4], reverse=True)

    # for pl in all_players_sorted:
    #     print(pl)


    # sd_salary_cap_optimizer.random_optimizer(sd_salary_cap_by_position)
    # generate_sd_lineups()


    # if matched_projection_count != len(money_line_fdp_projections):
    #     import pdb; pdb.set_trace()
