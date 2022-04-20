# -*- coding: utf-8 -*-

import os
import sys
from numpy import sort
from tabulate import tabulate

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from fd_optimizer import Player, generate_single_roster
from optimizer_player_pool import normalize_name
from optimizer_player_pool import get_fd_slate_players, load_start_times, load_season_data

file1 = open("/Users/amichailevy/Downloads/table-data (4).csv", "r")
lines = file1.readlines()
season_data = load_season_data()
day = 19
name_to_fd = {}
name_to_price = {}
all_teams = season_data.keys()
date = '01/{}/2022'.format(day)
for team in all_teams:
    if not date in season_data[team]:
        continue
    
    rows = season_data[team][date]
    for row in rows:
        name = row[4]
        name = normalize_name(name)
        name_to_fd[name] = row[19]
        name_to_price[name] = (row[15], row[16]) # draftkings fd

# __import__('pdb').set_trace()

all_rows = []
for line in lines[1:]:
    parts = line.split(',')
    name = parts[2]
    team = parts[1]
    projection = parts[0]
    if not name in name_to_fd:
        continue
    actual = name_to_fd[name]
    (dk_price, fd_price) = name_to_price[name]
    fd_value = round(actual / (float(fd_price) / 100), 2)
    projected_value = round(float(projection) / (float(fd_price) / 100), 2)
    all_rows.append([name, team, projection, actual, fd_price, projected_value, fd_value])

all_rows_sorted = sorted(all_rows, key=lambda a: a[5], reverse=True)

print(tabulate(all_rows_sorted, headers=["name", "team", "MLE proj", "Actual", "FD Price", "Projected Value", "Value"]))