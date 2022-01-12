import datetime
from json import dumps

import pandas as pd
from fd_optimizer import Player, generate_single_roster
from optimizer_player_pool import normalize_name
from optimizer_player_pool import get_fd_slate_players, load_start_times, load_season_data


# load a list of players, with expected performace vals, price, positions, start times
# Generate a ubiquity value for each player based on expected performance and start times
# generate unique rosters, at a particular roster price
#


def get_player_projections_caesars(projection_file_name):
    to_read = open(projection_file_name)
  
    player_to_fp = {}
    player_to_stat_to_value = {}

    lines = to_read.readlines()
    for line in lines:
        parts = line.split("|")
        if len(parts) < 4 or parts[1] != "MLE-Projected":
            continue

        player_name = normalize_name(parts[2]).strip()
        stat = parts[4]
        if stat != "Fantasy Score":
            continue
        
        stat_val = parts[5].strip()
        if stat_val == "REMOVED":
            continue

        value = float(stat_val)
        player_to_fp[player_name] = value

    return player_to_fp


current_date = datetime.datetime.now()
projection_file_name = "money_line_scrapes/money_line_scrape_{}_{}_{}.txt".format(current_date.month, current_date.day - 1, current_date.year)
caesars_fdp_projections = get_player_projections_caesars(projection_file_name)

path = "FanDuel-NBA-2022 ET-01 ET-10 ET-69990-players-list.csv"
download_folder = "/Users/amichailevy/Downloads/"
folder = download_folder + "player_lists/"
fd_slate = (folder + path, "full", "main")
fd_slate_file = fd_slate[0]
fd_players = get_fd_slate_players(fd_slate_file, exclude_injured_players=False)

name_to_fd = {}
season_data = load_season_data()
all_teams = season_data.keys()
date = '01/10/2022'
for team in all_teams:
    if not date in season_data[team]:
        continue
    
    rows = season_data[team][date]
    for row in rows:
        name = row[4]
        name = normalize_name(name)
        name_to_fd[name] = row[19]


start_time_to_teams = load_start_times("start_times.txt")


all_start_times = sorted(start_time_to_teams.keys())

team_to_start_time = {}
for start_time, teams in start_time_to_teams.items():
    for team in teams:
        team_to_start_time[team] = start_time

all_players = []
by_position = {}
for player, info in fd_players.items():
    if not player in name_to_fd:
        continue
    positions = info[1].split('/')
    for pos in positions:
        if not pos in by_position:
            by_position[pos] = []

        value = 0.0
        if player in caesars_fdp_projections:
            value = caesars_fdp_projections[player]

        cost = info[2]
        team = info[3]
        pl = Player(player, pos, cost, team, value, "")
        by_position[pos].append(pl)

        start_time_boost = round(all_start_times.index(team_to_start_time[team]) / (len(all_start_times) - 1), 2)
        

        ubiquity_value = round(value / cost * 10000, 2)
        ubiquity_value += start_time_boost
        all_players.append((pl, ubiquity_value))


seen_names = []
counter = 1

all_players_sorted = sorted(all_players, key=lambda a: a[1], reverse=True)
for res in all_players_sorted:
    name = res[0].name
    if not name in name_to_fd:
        print("Missing: {}".format(name))
        continue

    if name in seen_names:
        continue

    seen_names.append(name)
    fd = name_to_fd[name]
    print("{}: {} {} - {}".format(counter, res, res[0].value, fd))

    counter += 1

all_vals = []
for i in range(150):
    result = generate_single_roster(by_position, [], 10)
    print(result)
    actual_val = 0
    for player in result.players:
        actual_val += name_to_fd[player.name]
    # print(round(actual_val, 2))
    all_vals.append((round(actual_val, 2), result.value))

    # for each player calculate ubiquity reading

print(sorted(all_vals, key=lambda a:a[0], reverse=True))

__import__('pdb').set_trace()

#[380.7, 376.7, 372.1, 369.1, 369.1, 367.1, 366.6, 365.2, 364.4, 360.7, 358.6, 358.4, 358.1, 355.3, 354.4, 353.7, 352.7, 351.3, 351.1, 350.5, 349.9, 349.5, 349.1, 347.0, 346.4, 345.8, 344.1, 344.1, 344.1, 343.1, 342.6, 342.4, 342.1, 340.7, 340.0, 339.9, 339.5, 337.7, 336.4, 335.3, 334.8, 334.4, 334.3, 334.2, 333.5, 331.8, 331.2, 331.0, 330.4, 330.0, 329.5, 329.5, 329.4, 328.4, 328.2, 328.2, 328.1, 328.1, 327.8, 327.0, 326.4, 326.3, 326.0, 325.4, 324.7, 324.5, 324.3, 323.3, 322.7, 322.6, 322.6, 322.6, 322.5, 322.0, 321.9, 321.9, 321.7, 321.5, 321.1, 319.9, 319.8, 319.3, 319.2, 319.0, 317.7, 317.0, 316.0, 315.8, 314.4, 313.6, 312.4, 312.3, 312.2, 312.1, 311.8, 311.4, 310.8, 310.4, 310.3, 309.8, 309.8, 308.3, 308.0, 307.6, 306.9, 306.4, 306.3, 305.4, 304.2, 304.0, 304.0, 303.9, 303.7, 303.5, 302.5, 302.1, 301.9, 301.3, 300.5, 300.4, 300.1, 299.6, 299.6, 298.2, 297.0, 296.6, 296.3, 294.2, 294.2, 293.1, 293.0, 290.2, 289.8, 289.7, 288.2, 285.6, 283.3, 281.6, 280.9, 280.8, 279.4, 277.8, 275.0, 273.6, 273.5, 270.7, 265.8, 263.8, 262.2, 259.1] - iter 10

#[380.5, 376.4, 371.3, 370.3, 361.1, 360.5, 360.0, 357.9, 357.0, 356.0, 354.4, 353.2, 353.1, 349.9, 349.9, 349.7, 349.7, 349.7, 349.7, 349.7, 349.2, 349.1, 349.0, 348.9, 348.9, 348.0, 348.0, 347.8, 347.8, 345.8, 344.6, 344.5, 344.2, 344.2, 344.1, 344.1, 344.1, 344.1, 344.1, 344.1, 343.9, 343.4, 342.8, 342.7, 342.0, 341.8, 340.9, 340.4, 340.3, 339.4, 339.4, 339.4, 338.9, 338.8, 338.8, 338.8, 338.8, 338.5, 338.5, 338.5, 337.9, 337.4, 337.4, 337.4, 335.9, 335.9, 335.3, 335.3, 334.3, 334.1, 333.6, 332.5, 332.3, 331.7, 331.7, 330.2, 330.0, 329.4, 329.0, 328.4, 328.1, 327.7, 327.3, 326.5, 326.5, 326.4, 324.7, 324.5, 324.5, 324.5, 323.8, 322.6, 322.6, 322.3, 322.3, 322.2, 321.6, 321.6, 321.0, 320.9, 320.2, 319.9, 318.4, 317.9, 316.9, 316.9, 316.9, 316.8, 316.7, 316.7, 316.6, 316.1, 315.0, 314.0, 314.0, 314.0, 313.6, 313.6, 313.4, 313.0, 312.4, 311.1, 311.1, 310.8, 310.5, 310.4, 309.5, 308.7, 307.8, 306.6, 306.0, 305.9, 305.8, 303.8, 303.2, 301.8, 301.8, 300.4, 298.7, 298.7, 298.7, 298.6, 295.7, 293.4, 291.9, 291.1, 290.8, 288.5, 287.0, 274.1] - iter 100

#[361.1, 361.1, 361.1, 360.5, 357.9, 357.9, 353.3, 353.3, 353.3, 353.3, 353.3, 353.3, 353.3, 353.3, 353.3, 352.2, 349.9, 349.9, 349.9, 349.9, 349.9, 349.9, 349.7, 349.7, 349.7, 349.7, 349.7, 349.7, 349.7, 349.7, 349.7, 349.7, 349.7, 349.7, 349.7, 349.7, 348.9, 348.9, 348.9, 346.4, 346.4, 345.1, 344.2, 344.1, 344.1, 344.1, 344.1, 344.1, 344.1, 344.1, 344.1, 344.1, 344.1, 344.1, 344.1, 344.1, 344.1, 344.1, 344.1, 344.1, 344.1, 344.1, 344.1, 344.1, 344.1, 344.1, 344.1, 344.1, 344.1, 344.1, 344.1, 344.1, 343.2, 342.1, 342.0, 342.0, 342.0, 342.0, 342.0, 342.0, 342.0, 338.8, 338.8, 338.8, 338.8, 338.8, 338.8, 338.8, 338.8, 338.8, 338.5, 338.5, 338.5, 338.5, 338.5, 338.5, 334.0, 334.0, 332.5, 332.5, 332.5, 332.5, 332.5, 331.0, 327.7, 327.7, 327.7, 325.5, 325.5, 324.5, 324.5, 324.5, 322.5, 322.3, 320.9, 320.9, 320.9, 320.2, 320.2, 320.2, 320.2, 320.2, 320.2, 320.2, 320.2, 320.2, 320.2, 319.9, 319.9, 319.9, 319.9, 319.9, 316.8, 315.1, 315.1, 314.6, 314.6, 314.0, 314.0, 314.0, 314.0, 314.0, 314.0, 313.6, 313.6, 313.6, 309.3, 308.8, 298.7, 295.7] - iter 1000