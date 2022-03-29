from pandas.core.base import DataError, PandasObject
import numpy as np
import pandas as pd
import datetime

import matplotlib.pyplot as plt
import matplotlib




# parse slate

# construct a data frame with the columns:
# name, team, 

def get_correlation(x, y):
    result = np.corrcoef(x, y)
    # if result[0, 1] != result[1, 0]:
    #     import pdb; pdb.set_trace()
    return result[0, 1]


name_transform = {"Guillermo Hernangomez": 'Willy Hernangomez', "Cam Thomas": "Cameron Thomas", "Moe Harkless": 'Maurice Harkless', 'Juancho Hernangómez':"Juancho Hernangomez", "Guillermo Hernangómez": 'Willy Hernangomez', 'Timothé Luwawu-Cabarrot': 'Timothe Luwawu-Cabarrot', "Nah'Shon Hyland": 'Bones Hyland'}


team_transform = {"NYK": "NY", "GSW": "GS", "PHX": "PHO", "SAS": "SA", "NOP": "NO"}

def normalize_team_name(team):
    if team in team_transform:
        return team_transform[team]

    return team

def normalize_name(name):
    parts = name.split(" ")
    if len(parts) > 2:
        return "{} {}".format(parts[0], parts[1])

    name = name.replace(".", "")
    if name in name_transform:
        return name_transform[name]

    return name


def get_fd_slate_players(fd_slate_file_name):
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
        name = full_name
        all_players[name] = [name, positions, float(salary), team, status]
        
    return all_players


def get_slate_to_team_to_players(all_games, fd_players):
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

    return slate_to_team_to_players

def get_all_games(dk_slate_file_name):
    all_games = []
    all_lines = open(dk_slate_file_name).readlines()
    for line in all_lines[1:]:
        parts = line.split(",")
        game_info = parts[6]
        if not game_info in all_games:
            all_games.append(game_info)

    return all_games

def get_all_teams():
    all_teams = []
    for game in all_games:
        matchup = game.split(' ')[0]
        teams = matchup.split("@")
        for team in teams:
            all_teams.append(team)
    return all_teams

def load_season_data(all_teams):
    abbr_file = open("team_names.txt")
    lines = abbr_file.readlines()
    team_abbr_dict = {}
    team_abbr_dict2 = {}
    for line in lines:
        parts = line.split(',')
        abbr_name = parts[1].strip()
        team_abbr_dict[parts[1].strip()] = parts[0]
        team_abbr_dict2[parts[0]] = parts[1].strip()

    matched_team_names = []

    for team in all_teams:
        team = normalize_team_name(team)
        matched_team_names.append(team_abbr_dict[team])

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
        team = normalize_team_name(team)
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


def filter_rows_on_players(players, season_data):
    date_to_rows = {}
    for key1 in season_data.keys():
        for key2 in season_data[key1].keys():
            for row in season_data[key1][key2]:
                name = normalize_name(row[4])
                if not name in players:
                    continue
                
                date = row[2]

                if not date in date_to_rows:
                    date_to_rows[date] = []

                date_to_rows[date].append(row)
            
    return date_to_rows

def plot_heat_map(team, players, data):
    
    # vegetables = ["cucumber", "tomato", "lettuce", "asparagus",
    #             "potato", "wheat", "barley"]
    # farmers = ["Farmer Joe", "Upland Bros.", "Smith Gardening",
    #         "Agrifun", "Organiculture", "BioGoods Ltd.", "Cornylee Corp."]

    # harvest = np.array([[0.8, 2.4, 2.5, 3.9, 0.0, 4.0, 0.0],
    #                     [2.4, 0.0, 4.0, 1.0, 2.7, 0.0, 0.0],
    #                     [1.1, 2.4, 0.8, 4.3, 1.9, 4.4, 0.0],
    #                     [0.6, 0.0, 0.3, 0.0, 3.1, 0.0, 0.0],
    #                     [0.7, 1.7, 0.6, 2.6, 2.2, 6.2, 0.0],
    #                     [1.3, 1.2, 0.0, 0.0, 0.0, 3.2, 5.1],
    #                     [0.1, 2.0, 0.0, 1.4, 0.0, 1.9, 6.3]])


    fig, ax = plt.subplots()
    im = ax.imshow(data)

    # Show all ticks and label them with the respective list entries
    ax.set_xticks(np.arange(len(players)), labels=players)
    ax.set_yticks(np.arange(len(players)), labels=players)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
            rotation_mode="anchor")

    # Loop over data dimensions and create text annotations.
    for i in range(len(players)):
        for j in range(len(players)):
            text = ax.text(j, i, data[i, j],
                        ha="center", va="center", color="w")

    ax.set_title("Player Player Correlation - {}".format(team))
    fig.tight_layout()
    plt.show()

if __name__ == "__main__":
    # x = np.arange(10, 20)
    # y = np.array([2, 1, 4, 5, 8, 12, 18, 25, 96, 48])
    # get_correlation(x, y)

    # import pdb; pdb.set_trace()

    # for each pair of teammates
    # for every game they both played, get the list of:
    # minutes, fantasy points, minutes %, fantasy points % fantasy points per minute

    download_folder = "/Users/amichailevy/Downloads/"
    folder = download_folder + "player_lists/"
    fd_slate_file = folder + "FanDuel-NBA-2021 ET-11 ET-17 ET-67138-players-list.csv"

    fd_players = get_fd_slate_players(fd_slate_file)

    dk_slate_file = folder + "DKSalaries_11_17_21.csv"

    all_games = get_all_games(dk_slate_file)
    result = get_slate_to_team_to_players(all_games, fd_players)
    all_teams = get_all_teams()
    season_data = load_season_data(all_teams)



    team_to_player_to_player_to_correlation = {}

    for slate, team_to_players in result.items():
        for team, players in team_to_players.items():
            if not team in team_to_player_to_player_to_correlation:
                team_to_player_to_player_to_correlation[team] = {}

            player_names = list(players.keys())
            for i in range(len(player_names)):
                for j in range(len(player_names)):
                    if j <= i:
                        continue

                    player1 = player_names[i]
                    player2 = player_names[j]

                    if not player1 in team_to_player_to_player_to_correlation[team]:
                        team_to_player_to_player_to_correlation[team][player1] = {}


                    if not player2 in team_to_player_to_player_to_correlation[team]:
                        team_to_player_to_player_to_correlation[team][player2] = {}

                    

                    date_to_rows = filter_rows_on_players([player1, player2], season_data)
                    
                    x_vals = []
                    y_vals = []

                    for date, rows in date_to_rows.items():
                        if len(rows) != 2:
                            continue

                        for row in rows:
                            name = normalize_name(row[4])
                            if name == player1:
                                x_vals.append(row[10])
                            elif name == player2:
                                y_vals.append(row[10])

                    assert len(x_vals) == len(y_vals)

                    if len(x_vals) > 3:
                        result = get_correlation(x_vals, y_vals)
                        team_to_player_to_player_to_correlation[team][player1][player2] = result
                        team_to_player_to_player_to_correlation[team][player2][player1] = result



    target_team = ""
    for team, correlations in team_to_player_to_player_to_correlation.items():
        print("TEAM: {}".format(team))
        # if team != target_team:
        #     continue
        player_list1 = correlations.keys()
        to_remove = []
        for player1 in player_list1:
            player_to_val = correlations[player1]
            should_remove = True
            for val in player_to_val.values():
                if val != 0.0:
                    should_remove = False
                    break

            if should_remove:
                to_remove.append(player1)
            


        player_list = []
        for pl in player_list1:
            if pl not in to_remove:
                player_list.append(pl)

        row_count = len(player_list)
        matrix = np.zeros((row_count, row_count))
        print("," + ",".join(player_list))
        idx1 = 0
        for player1 in player_list:
            row = [player1]
            player_to_val = correlations[player1]
            idx2 = 0
            for player2 in player_list:
                if player2 in player_to_val:
                    row.append(str(player_to_val[player2]))
                    matrix[idx1, idx2] = round(player_to_val[player2], 1)
                else:
                    row.append(str(0))

                idx2 += 1
            print(",".join(row))
            idx1 += 1
            pass

        plot_heat_map(team, player_list, matrix)



