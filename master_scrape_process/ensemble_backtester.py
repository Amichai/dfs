from operator import itemgetter
from re import L
from turtle import fd, pd
from dateutil import parser
import dk_random_optimizer
import optimizer_player_pool
import fd_optimizer
import statistics
import math

import random

# from scraper import get_name_to_status

def generate_random_rosters_from_pool(pool, by_position):
    pool_names = [a.name for a in pool]
    generated_rosters = [] #unique

    for i in range(5000):
        by_position_filtered = {}
        for pos, players in by_position.items():
            if not pos in by_position_filtered:
                by_position_filtered[pos] = []
            for player in players:
                if player.name in pool_names:
                    player.value = random.uniform(0, 1)
                    by_position_filtered[pos].append(player)


        result = fd_optimizer.generate_single_roster(by_position_filtered, [], 2)
        if result != None:
            generated_rosters.append(result)


    generated_rosters_sorted = sorted(generated_rosters, key=lambda a: a.cost, reverse=True)
    result = generated_rosters_sorted[:50]
    return result


def get_actual_results(path):
    actual_results = {}
    results_path = "/Users/amichailevy/Downloads/linestar/" + path
    results_file = open(results_path, "r")
    lines = results_file.readlines()
    for line in lines[1:]:
        parts = line.split(',')
        name = parts[1]
        actual = parts[6]
        cost = float(parts[4])
        name = optimizer_player_pool.normalize_name(name)
        actual_results[name] = [actual, cost]
    return actual_results

def load_projections(projections_path, break_time=19):
    input_file = open(projections_path, "r")

    sites = {}

    player_to_val = {}

    lines = input_file.readlines()
    for line in lines:
        parts = line.split("|")
        if len(parts) < 4:
            continue
        site = parts[1]
        if not site in sites:
            sites[site] = {}

        team = parts[3]

        parsed_time = parser.parse(parts[0])
        if parsed_time.hour >= break_time:
            break

        player_name = parts[2]
        if not player_name in sites[site]:
            sites[site][player_name] = {}
        val = parts[5].strip()
        if val == "REMOVED":
            if stat in sites[site][player_name]:
                del sites[site][player_name][stat]
            continue
        stat = parts[4]
        sites[site][player_name][stat] = str(val)

        if site == "MLE-Projected":
            player_to_val[player_name] = str(val)

    return player_to_val


def optimal_roster_analysis():
    date = "3_25_2022"
    results_path = "salaries.Basketball.FanDuel.1697.17340.csv" # 3/25/22
    results = get_actual_results(results_path)

    

    projections_path = "money_line_scrapes/money_line_scrape_{}.txt".format(date)

    projections = load_projections(projections_path)

    name_projected_value_actual = []
    for name, projection in projections.items():
        actual = results[name][0]
        projected_val = float(projection) / results[name][1] * 100
        name_projected_value_actual.append([name, projected_val, actual])

    name_projected_value_actual_sorted = sorted(name_projected_value_actual, key=lambda a: a[1], reverse=True)

    for npv in name_projected_value_actual_sorted[:30]:
        print(npv)
    __import__('pdb').set_trace()


def parse_money_line_file(path, break_hour=19):
    input_file = open(path, "r")

    sites = {}

    player_to_val = {}

    lines = input_file.readlines()
    for line in lines:
        parts = line.split("|")
        if len(parts) < 4:
            continue
        site = parts[1]
        if not site in sites:
            sites[site] = {}

        team = parts[3]

        parsed_time = parser.parse(parts[0])
        if parsed_time.hour >= 19:
            break



        player_name = parts[2]
        if not player_name in sites[site]:
            sites[site][player_name] = {}
        val = parts[5].strip()
        if val == "REMOVED":
            if stat in sites[site][player_name]:
                del sites[site][player_name][stat]
            continue
        stat = parts[4]
        sites[site][player_name][stat] = str(val)

        if site == "MLE-Projected":
            player_to_val[player_name] = str(val)

    return player_to_val

def backtester1(date, results_path, fd_slate_path):
    path = "money_line_scrapes/money_line_scrape_{}.txt".format(date)
    
    player_to_val = parse_money_line_file(path, 19)

    # (start_time_to_teams, path) = optimizer_player_pool.load_start_times_and_slate_path("start_times2.txt")
    path = fd_slate_path

    download_folder = "/Users/amichailevy/Downloads/"

    folder = download_folder + "player_lists/"

    fd_slate = (folder + path, "full", "main")


    fd_slate_file = fd_slate[0]

    fd_players = optimizer_player_pool.get_fd_slate_players(fd_slate_file, exclude_injured_players=False)

    by_position = {}

    for name, player_info in fd_players.items():
        pos_str = player_info[1]

        pos_parts = pos_str.split('/')

        price = player_info[2]
        team = player_info[3]
        status = player_info[4]
        if status == "O":
            continue
        
        if not name in player_to_val:
            print("NOT FOUND: {}".format(name))
            continue
        val = player_to_val[name]
        for pos in pos_parts:
            if not pos in by_position:
                by_position[pos] = []
            pl = dk_random_optimizer.Player(name, pos, price, team, val)
            by_position[pos].append(pl)


    actual_results = get_actual_results(results_path)
    # actual_results = [a[0] for a in actual_results]
    for player, result_cost in actual_results.items():
        actual_results[player] = result_cost[0]

    def get_roster_value(roster):
        total_val = 0
        for player in roster.players:
            total_val += float(actual_results[player.name])

        return total_val

    iter_count = int(80000 / 1)

    all_players = []
    all_player_names = []
    for pos, players in by_position.items():
        for player in players:
            if player.name in all_player_names:
                continue

            all_player_names.append(player.name)
            all_players.append(player)

    players_sorted_by_value = sorted(all_players, key=lambda a: a.value / a.cost, reverse=True)
    for player in players_sorted_by_value[:140]:
        print("{} - {}".format(player.name, player.value / player.cost * 100))

    entries = []
    for i in range(50):
        entries.append(('a', 'b', 'c'))


    # by_position = fd_optimizer.remove_players_from_player_pool(by_position, ["Luka Doncic"])
    (generated_rosters, _) = fd_optimizer.generate_best_roster(by_position, iter_count, iter_count, None, entries)
    # generated_rosters = generate_random_rosters_from_pool(players_sorted_by_value[:30], by_position)

    fd_optimizer.validate_results(generated_rosters, None, actual_results)

    all_roster_vals = [get_roster_value(roster) for roster in generated_rosters]

    max_val = max(all_roster_vals)
    mean = statistics.mean(all_roster_vals)
    median = statistics.median(all_roster_vals)
    roster_ct = len(all_roster_vals)

    print("Count: {}, max: {}, mean: {}, median: {}".format(len(all_roster_vals), max_val, mean, median))

diff_by_bucket = []
for i in range(10):
    diff_by_bucket.append([])

def test_line_accuracy(date, results_path):
    path = "money_line_scrapes/money_line_scrape_{}.txt".format(date)
    
    player_results = get_actual_results(results_path)
    player_to_val = parse_money_line_file(path, 19)

    over_ct = 0
    under_ct = 0
    over_sum = 0
    under_sum = 0
    predicted_actual = []



    for player, actual in player_results.items():
        actual = float(actual[0])
        if actual < 1:
            continue
        if not player in player_to_val:
            # if actual > 0:
            #     print("Missing: {} - {}".format(player, actual))
            continue
        predicted = player_to_val[player]
        predicted = float(predicted)


        # if predicted < 35:
        #     continue
        # if predicted > 25:
        #     continue
        diff = actual - float(predicted)
        bucket_idx = math.floor(predicted / 10)
        diff_by_bucket[bucket_idx].append(diff)

        if diff > 0:
            over_ct += 1
            over_sum += diff
        if diff < 0:
            under_ct += 1
            under_sum += abs(diff)
        predicted_actual.append((predicted, actual, diff))


    predicted_actual_sorted = sorted(predicted_actual, key=lambda a: a[0])
    # for r in predicted_actual_sorted:
    #     print("{}, {}".format(r[0], r[1]))
    print("over ct: {} - under ct: {}".format(over_ct, under_ct))
    print("over sum: {} - under sum: {}".format(over_sum, under_sum))
    # for each day
    # for each player (random time?)
    # What is the diff between the actual and the predicted line
    # how does the average and SD change with the magnitude of the line?
    # volatility of the line?
    pass

# optimal_roster_analysis()
# backtester1("3_25_2022", "salaries.Basketball.FanDuel.1697.17340.csv")
test_line_accuracy("3_25_2022", "salaries.Basketball.FanDuel.1697.17340.csv")
test_line_accuracy("3_24_2022", "salaries.Basketball.FanDuel.1696.17318.csv")
test_line_accuracy("3_23_2022", "salaries.Basketball.FanDuel.1695.17298.csv")
test_line_accuracy("3_22_2022", "salaries.Basketball.FanDuel.1694.17288.csv")
test_line_accuracy("3_21_2022", "salaries.Basketball.FanDuel.1693.17273.csv")
test_line_accuracy("3_18_2022", "salaries.Basketball.FanDuel.1690.17208.csv")
test_line_accuracy("3_17_2022", "salaries.Basketball.FanDuel.1689.17201.csv")


idx = 1
for bucket in diff_by_bucket:
    if len(bucket) < 3:
        print(bucket)
        __import__('pdb').set_trace()
    print("{}: {} - mean: {}, median: {}, sd: {}".format(idx, len(bucket), statistics.mean(bucket), statistics.median(bucket), statistics.stdev(bucket)))
    idx += 1