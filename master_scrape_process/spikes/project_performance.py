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


def collect_data(money_line_path, date):
    money_lines = get_money_line_values(money_line_path)
    player_results = get_player_results(date)

    x_val_players = []
    x_vals = []
    y_vals = []

    def add_feature(all_x_vals, all_lines, name):
        x1 = all_lines[name]
        all_x_vals.append(float(x1))

    def add_feature_pair(all_x_vals, all_lines, name1, name2):
        x1 = all_lines[name1]
        x2 = all_lines[name2]
        all_x_vals.append(float(x1) * float(x2))

    for player, all_lines in money_lines.items():
        all_x_vals = []
        try:
            add_feature(all_x_vals, all_lines, "Caesars-Points")
            add_feature(all_x_vals, all_lines, "Caesars-Assists")
            add_feature(all_x_vals, all_lines, "Caesars-Rebounds")
            add_feature(all_x_vals, all_lines, "Caesars-Blocks")
            add_feature(all_x_vals, all_lines, "Caesars-Steals")
            add_feature(all_x_vals, all_lines, "Caesars-Turnovers")

            # add_feature(all_x_vals, all_lines, "PP-Fantasy Score")

            # add_feature_pair(all_x_vals, all_lines, "Caesars-Points", "Caesars-Points")
            # add_feature_pair(all_x_vals, all_lines, "Caesars-Rebounds", "Caesars-Rebounds")
            # add_feature_pair(all_x_vals, all_lines, "Caesars-Points", "Caesars-Rebounds")

            

            # add_feature(all_x_vals, all_lines, "Caesars-3pt Field Goals")

            # add_feature(all_x_vals, all_lines, "Caesars-Points + Assists")
            # add_feature(all_x_vals, all_lines, "Caesars-Points + Rebounds")
            # add_feature(all_x_vals, all_lines, "caesars-Projected-Fantasy Score")
            # add_feature(all_x_vals, all_lines, "Caesars-Rebounds + Assists")
            # add_feature(all_x_vals, all_lines, "Caesars-Blocks + Steals")
            # add_feature(all_x_vals, all_lines, "Caesars-Points + Assists + Rebounds")

    #{'betMGM-rebounds + assists': '5.4658176943699734', 'betMGM-points': '14.5', 'betMGM-blocks': '0.107421875', 'betMGM-rebounds': '2.613874345549738', 'betMGM-steals': '0.6733668341708543', 'betMGM-steals + blocks': '1.287037037037037', 'betMGM-points + assists': '16.516042780748663', 'betMGM-points + rebounds': '17.5', 'betMGM-three-pointers': '2.5040322580645165', 'betMGM-assists': '2.358527131782946', 'betMGM-Projected-Fantasy Score': '23.52', 'PP-Points': '14.5', 'PP-3-PT Made': '2.5', 'PP-Fantasy Score': '22.0', 'Caesars-Points': '14.483957219251337', 'Caesars-Assists': '2.326354679802956', 'Caesars-Rebounds': '2.576771653543307', 'Caesars-Points + Assists': '16.516042780748663', 'Caesars-Points + Rebounds': '17.483957219251337', 'Caesars-Rebounds + Assists': '5.397286821705427', 'Caesars-Points + Assists + Rebounds': '19.45424403183024', 'Caesars-3pt Field Goals': '2.516042780748663', 'Caesars-Blocks': '0.1071428571428571', 'Caesars-Steals': '0.6736453201970444', 'Caesars-Blocks + Steals': '1.2921686746987953', 'Caesars-Turnovers': '1.3263546798029557', 'caesars-Projected-Fantasy Score': '22.97', 'MLE-Projected-Fantasy Score': '22.97'}

            y_val = player_results[player]
            # if y_val < 10:
            if y_val == 0:
                continue
        except:
            continue

        x_val_players.append(player)
        # x_vals.append([x1, x2, x3, x4, x5, x6, \
        # x7, x8, x9, x10])
        x_vals.append(all_x_vals)
        y_vals.append(y_val)

    return (x_vals, y_vals) 



if __name__ == "__main__":
    to_parse = [
        ("../money_line_scrapes/money_line_scrape_1_14_2022.txt", '01/14/2022'),
        ("../money_line_scrapes/money_line_scrape_1_13_2022.txt", '01/13/2022'),
        ("../money_line_scrapes/money_line_scrape_1_12_2022.txt", '01/12/2022'),
        ("../money_line_scrapes/money_line_scrape_1_11_2022.txt", '01/11/2022'),
        ("../money_line_scrapes/money_line_scrape_1_10_2022.txt", '01/10/2022'),
        ("../money_line_scrapes/money_line_scrape_1_9_2022.txt", '01/09/2022'),
        ("../money_line_scrapes/money_line_scrape_1_8_2022.txt", '01/08/2022'),
        ("../money_line_scrapes/money_line_scrape_1_7_2022.txt", '01/07/2022'),
        ("../money_line_scrapes/money_line_scrape_1_6_2022.txt", '01/06/2022'),
        ("../money_line_scrapes/money_line_scrape_1_5_2022.txt", '01/05/2022'),
        ("../money_line_scrapes/money_line_scrape_1_4_2022.txt", '01/04/2022'),
        ("../money_line_scrapes/money_line_scrape_1_3_2022.txt", '01/03/2022'),
        ("../money_line_scrapes/money_line_scrape_1_2_2022.txt", '01/02/2022'),
        
        
        ]

    x_vals = []
    y_vals = []
    for path, date in to_parse:
        x_vals1, y_vals1 = collect_data(path, date)
        x_vals += x_vals1
        y_vals += y_vals1




    model = linear_model.LinearRegression()

    print("Points,Assists,Rebounds,Blocks,Steals,Turnovers")
    
    model.fit(x_vals, y_vals)
    r_sq = model.score(x_vals, y_vals)
    print("Intercept: ", model.intercept_)
    print("Coefficients: \n", model.coef_)
    print('coefficient of determination:', r_sq)

    print("Data count: {}".format(len(x_vals)))

    # compare_result(model, x_vals, y_vals)
