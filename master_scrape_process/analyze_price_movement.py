import pandas as pd
from dk_random_optimizer import generate_rosters, Player
from dk_random_optimizer import scrape_money_lines, RosterEvaluator


from os import path



def get_player_pool_from_money_line_scrape(filepath):
    # acceptable_stats = ["Underdog-points"]
    acceptable_stats = ["PP-Fantasy Score"]
    # acceptable_stats = ["PP-Fantasy Score", "Underdog-points", "PP-Points", "Underdog-pts_rebs_asts", "PP-Assists"]
    file = open(filepath, "r")

    lines = file.readlines()

    name_to_prices = {}

    for line in lines:
        parts = line.split('|')
        if len(parts) < 4:
            continue
        site = parts[1]
        if site != "PP" and site != "Underdog":
            continue

        name = parts[2]
        if not name in name_to_prices:
            name_to_prices[name] = {}

        stat = site + "-" + parts[3]

        if stat not in acceptable_stats:
            continue
        if not stat in name_to_prices[name]:
            name_to_prices[name][stat] = []

        if 'REMOVED' in parts[4]:
            continue
        val = float(parts[4].strip())
        print(line.strip())

        name_to_prices[name][stat].append(val)

    player_pool = []
    for name, stat_to_vals in name_to_prices.items():
        for stat, vals in stat_to_vals.items():
            if len(vals) < 2:
                continue

            val_sum = vals[-1] - vals[0]

            # print("{} - {} - {} = {}".format(name, stat, vals, val_sum))

            if val_sum >= 1.0 and not name in player_pool:
                player_pool.append(name)

    print(player_pool)

    return player_pool


def load_dk_results(results_file, target_date, player_pool):
    dfs = pd.read_excel(results_file, sheet_name=None)

    feed = dfs['NBA-DFS-DAILY-FEED']

    all_players = []

    for index, row in feed.iterrows():
        if row['GAME INFORMATION'] != "NBA 2021-2022 Regular Season":
            continue
        
        date = row["Unnamed: 2"]

        if date != target_date:
            continue

        name = row["Unnamed: 4"]
        team = row["Unnamed: 5"]
        opp = row["Unnamed: 6"]
        starter = row["Unnamed: 7"]
        minutes = row["Unnamed: 9"]
        rest = row["Unnamed: 11"]
        positions = row["POSITION"]
        salary = row["SALARY ($)"]
        fdp = row["FANTASY POINTS SCORED"]
        if not name in player_pool:
            continue

        player = (name, positions, salary, fdp)
        all_players.append(player)

    total_cost = 0
    total_value = 0
    for player in all_players:
        total_cost += player[2]
        total_value += player[3]

    effectiveness = round(total_value * 100 / total_cost, 2)
    print("POOL EFFECTIVENESS: {}".format(effectiveness))

    return all_players


def get_player_pool_by_position(all_players, player_pool):
    print(len(all_players))
    print(len(player_pool))
    if len(all_players) != len(player_pool):
        import pdb; pdb.set_trace()
    print(all_players)
    # assert len(all_players) == len(player_pool)

    positions_mapper = {"PG": ["PG", "G", "UTIL"], "SG": ["SG", "G", "UTIL"], "SF": ["SF", "F", "UTIL"], "PF": ["PF", "F", "UTIL"], "C": ["C", "UTIL"]}

    all_positions = ["PG", "SG", "SF", "PF", "C", "G", "F", "UTIL"]
    by_position = {}
    for pos in all_positions:
        by_position[pos] = []

    for player in all_players:
        positions = player[1].split("/")
        for pos in positions:
            position_slots = positions_mapper[pos]
            for pos_slot in position_slots:
                pl = Player(player[0], pos_slot, player[2], "NA", player[2])
                all_names = [a.name for a in by_position[pos_slot]]
                if not pl.name in all_names:
                    by_position[pos_slot].append(pl)


    print(by_position)
    return by_position


def evaluate_player_pool(all_players):

    pass

# results_file = "/Users/amichailevy/Downloads/11-03-2021-nba-season-dfs-feed.xlsx"



past_runs = {
    "11/3": (
            117394654,
            15,
            "/Users/amichailevy/Downloads/contest-standings-117394654_11_3.csv", 
            "/Users/amichailevy/Downloads/11-03-2021-nba-daily-dfs-feed.xlsx",
            "money_line_scrape_11_3_2021.txt",
            "11/03/2021"
    ),
    "11/4": (
            117487697,
            15,
            "/Users/amichailevy/Downloads/contest-standings-117487697_11_4.csv", 
            "/Users/amichailevy/Downloads/11-04-2021-nba-daily-dfs-feed.xlsx",
            "money_line_scrape_11_4_2021.txt",
            "11/04/2021"
    ),
    "11/5": (
            117487697,
            -1,
            "", 
            "/Users/amichailevy/Downloads/11-05-2021-nba-daily-dfs-feed.xlsx",
            "money_line_scrape_11_5_2021.txt",
            "11/05/2021"
    ),
    "11/7": (
            117713954,
            15,
            "contest-standings-117713954_11_7.csv",
            "11-07-2021-nba-daily-dfs-feed.xlsx",
            "money_line_scrape_11_7_2021.txt",
            "11/07/2021",
    ),
}


(contest_id, buy_in, rosters_filepath, results_file, filepath, date) = past_runs["11/7"]

rosters_filepath = "/Users/amichailevy/Downloads/contest_standings/" + rosters_filepath
results_file = "/Users/amichailevy/Downloads/season_data/" + results_file

# month = 11
# # day = 3

# day = 3
# rosters_filepath = "/Users/amichailevy/Downloads/contest-standings-117394654_11_3.csv"
# # rosters_filepath = "/Users/amichailevy/Downloads/contest-standings-117487697_11_4.csv"

# results_file = "/Users/amichailevy/Downloads/{}-{}-2021-nba-daily-dfs-feed.xlsx".format(month, str(day).zfill(2))
# filepath = "money_line_scrape_{}_{}_2021.txt".format(month, day)
# date = "{}/{}/2021".format(month, str(day).zfill(2))
# contest_id = 117394654
# buy_in = 15


# filepath = "money_line_scrape_11_4_2021.txt"
# date = "11/04/2021"

# https://www.bigdataball.com/nba-stats-central/
# filepath = "money_line_scrape_11_2_2021.txt"
# results_file = "/Users/amichailevy/Downloads/11-02-2021-nba-daily-dfs-feed.xlsx"
# contest_id = 117317680
# rosters_filepath = "/Users/amichailevy/Downloads/contest-standings-117317680_11_2.csv"
# buy_in = 15



# filepath = "money_line_scrape_11_4_2021.txt"
# date = "11/04/2021"

# contest_id = 117037146
# rosters_filepath = "/Users/amichailevy/Downloads/contest-standings-117037146_10_30.csv"
# buy_in = 15


player_pool = get_player_pool_from_money_line_scrape(filepath)
all_players = load_dk_results(results_file, date, player_pool)
by_position = get_player_pool_by_position(all_players, player_pool)

payouts = scrape_money_lines(contest_id)
evaluator = RosterEvaluator(buy_in, rosters_filepath, payouts)

generate_rosters(by_position, evaluator)
