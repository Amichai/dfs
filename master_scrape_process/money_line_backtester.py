from os import set_inheritable
from optimizer_player_pool import normalize_name
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, DayLocator, MinuteLocator, HourLocator, AutoDateFormatter, AutoDateLocator
import pandas as pd
import datetime


def get_fd_points(player_name, target_date, feed):


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
        fdp = row["Unnamed: 19"]

        name = normalize_name(name)

        if name == player_name and date == target_date:
            return fdp
    print("Not found: {} - {}".format(name, target_date))
    return 0


# pick a day
# parse the money line data
# pick a random time of day
# get the money lines at that time
# who is closer?

# ---
# for each player
# for each projection
# at each change


money_line_path = "money_line_scrape_12_3_2021.txt"

input_file = open(money_line_path, "r")

by_player = {}

known_fdp = {}

today = datetime.datetime.now()
yesterday = today - datetime.timedelta(days=1)

filename = "~/Downloads/season_data/{}-{}-{}-nba-season-dfs-feed.xlsx".format(yesterday.month, str(yesterday.day).zfill(2), yesterday.year)

dfs = pd.read_excel(filename, sheet_name=None)
if 'NBA-DFS-SEASON-FEED' in dfs:
    feed = dfs['NBA-DFS-SEASON-FEED']
else:
    feed = dfs['NBA-DFS-SEASON']

lines = input_file.readlines()
seen_players = []
player_ct = 135
for line in lines:
    # if line_idx > 5000:
    #     break

    # line_idx += 1
    
    parts = line.split("|")
    if len(parts) < 4:
        continue
    date = parts[0]
    time = datetime.datetime.fromisoformat(date)
    site = parts[1]
    player_name = parts[2]
    name = normalize_name(player_name)

    if len(seen_players) < player_ct and name not in seen_players:
        seen_players.append(name)

    if name not in seen_players:
        continue

    team = parts[3]
    stat = parts[4]
    val = parts[5]
    
    team = None
    if site not in ["PP", "caesars-Projected", "betMGM-Projected", "DK-Projected", "Awesemo-Projected"]:
        continue

    if stat != "Fantasy Score":
        continue

    if name in known_fdp:
        fdp = known_fdp[name]
    else:
        fdp = get_fd_points(player_name, "12/03/2021", feed)
        known_fdp[name] = fdp

    if not name in by_player:
        by_player[name] = {"Actual": {}}

    if not site in by_player[name]:
        by_player[name][site] = {}

    by_player[name]["Actual"][time] = str(fdp)

    by_player[name][site][time] = val
    


for player, site_data in by_player.items():
    
    if not "PP" in site_data:
        continue
    pp_keys = sorted(site_data["PP"].keys())
    last_key = pp_keys[-1]
    offline_time = last_key - datetime.timedelta(minutes=5)

    all_time_keys = []
    for site, val_data in site_data.items():
        all_time_keys += val_data.keys()
        

    x_vals = []
    all_time_keys = sorted(all_time_keys)
    for val in all_time_keys:
        if val > offline_time:
            break

        x_vals.append(val)


    all_y_vals = []
    site_name = []
    site_data_keys_sorted = sorted(site_data.keys())
    for site in site_data_keys_sorted:
        val_data = site_data[site]
        site_name.append(site)
        y_vals = []
        current_val = 0
        for time_key in all_time_keys:
            if time_key > offline_time:
                break
            if time_key in val_data:
                new_val = val_data[time_key].strip()
                if new_val == "REMOVED":
                    current_val = 0

                else:
                    current_val = float(new_val)

            # x_vals.append(time_key)
            y_vals.append(current_val)

        all_y_vals.append(y_vals)
        # import pdb; pdb.set_trace()
        pass
    

    colors = ["black", "tab:blue", "tab:red", "tab:green", "tab:orange", "yellow"]
    plt.rc('font', size=12)
    fix, ax = plt.subplots(figsize=(10, 6))
    idx = 0
    for y_vals in all_y_vals:
        color = colors[idx]
        ax.plot(x_vals, y_vals, color=color, label=site_name[idx])

        idx += 1

    # Same as above
    ax.set_xlabel('Time')
    ax.set_ylabel('Projection')
    ax.set_title('{} proj'.format(player))
    ax.grid(True)
    ax.legend(loc='upper left')

    ax.xaxis.set_major_locator(HourLocator())
    ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))

    plt.show()



