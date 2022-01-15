import datetime
from json import dumps
from tabulate import tabulate

import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))


import pandas as pd
from fd_optimizer import Player, generate_single_roster
from optimizer_player_pool import normalize_name
from optimizer_player_pool import get_fd_slate_players, load_start_times, load_season_data


def get_money_line_values(path):
    to_read = open(path, "r")

    player_to_stat_to_value = {}
    lines = to_read.readlines()
    for line in lines:
        parts = line.split('|')
        if len(parts) < 4:
            continue

        player_name = normalize_name(parts[2]).strip()

        site = parts[1]
        stat = parts[4]

        stat_val = parts[5].strip()
        if stat_val == "REMOVED":
            continue

        try:
            value = float(stat_val)
        except:
            continue

        if not player_name in player_to_stat_to_value:
            player_to_stat_to_value[player_name] = {}

        stat_key = "{}-{}".format(site, stat)
        player_to_stat_to_value[player_name][stat_key] = stat_val
    return player_to_stat_to_value


def get_player_results(date):
    name_to_fd = {}
    season_data = load_season_data()
    all_teams = season_data.keys()
    for team in all_teams:
        if not date in season_data[team]:
            continue
        
        rows = season_data[team][date]
        for row in rows:
            name = row[4]
            name = normalize_name(name)
            name_to_fd[name] = row[19]

    return name_to_fd


from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score

def compare_result(model, x_vals, y_vals):
    predicted = model.predict(x_vals)

    rows = []
    total_diff1 = 0
    total_diff2 = 0

    total_diff1_sq = 0
    total_diff2_sq = 0
    for i in range(len(x_vals)):
        y_predicted1 = predicted[i]

        vector = x_vals[i]
        y_predicted2 = vector[0] + vector[1] * 1.5 + vector[2] * 1.2 + vector[3] * 3 + vector[4] * 3 - vector[5]

        y_actual = y_vals[i]
        diff1 = abs(y_predicted1 - y_actual)
        diff2 = abs(y_predicted2 - y_actual)
        rows.append([y_predicted1, y_predicted2, y_actual, diff1, diff2])

        total_diff1 += diff1
        total_diff2 += diff2

        total_diff1_sq += diff1 * diff1
        total_diff2_sq += diff2 * diff2

    # print(tabulate(rows, headers=["model projection", "naive projection", "actual", "diff1", "diff2"]))
    print("row count: {}".format(len(x_vals)))

    print("model diff {}".format(round(total_diff1, 2)))
    print("naive diff {}".format(round(total_diff2, 2)))

    print("model diff sq {}".format(round(total_diff1_sq, 2)))
    print("naive diff sq {}".format(round(total_diff2_sq, 2)))
    import pdb; pdb.set_trace()
    pass


if __name__ == "__main__":
    money_lines = get_money_line_values("../money_line_scrapes/money_line_scrape_1_11_2022.txt")

    player_results = get_player_results('01/11/2022')

    model = linear_model.LinearRegression()

    x_val_players = []
    x_vals = []
    y_vals = []
    all_players = money_lines.keys()
    for player, all_lines in money_lines.items():
        try:
            x1 = all_lines["Caesars-Points"]
            x2 = all_lines["Caesars-Assists"]
            x3 = all_lines["Caesars-Rebounds"]
            x4 = all_lines["Caesars-Blocks"]
            x5 = all_lines["Caesars-Steals"]
            x6 = all_lines["Caesars-Turnovers"]
            # x7 = all_lines['Caesars-Points + Assists']
            # x8 = all_lines['Caesars-Points + Rebounds']
            # x9 = all_lines['Caesars-Rebounds + Assists']
            # x10 = all_lines['Caesars-3pt Field Goals']

            y_val = player_results[player]
            if y_val < 5:
                continue
        except:
            continue

        x_val_players.append(player)
        # x_vals.append([x1, x2, x3, x4, x5, x6, \
        # x7, x8, x9, x10])
        x_vals.append([float(a) for a in [x1, x2, x3, x4, x5, x6]])
        y_vals.append(y_val)
    

    model.fit(x_vals, y_vals)
    r_sq = model.score(x_vals, y_vals)
    print("Intercept: ", model.intercept_)
    print("Coefficients: \n", model.coef_)
    print('coefficient of determination:', r_sq)

    compare_result(model, x_vals, y_vals)
