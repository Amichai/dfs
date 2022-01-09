import datetime
import random
import time
from fd_optimizer import get_player_projections
from fd_optimizer import Player, Roster


all_positions = ["PG", "SG", "G", "SF", "PF", "F", "C", "UTIL"]

def get_players_by_position(player_to_fp, fd_slate_file_name):
    
    by_position = {}
    for position in all_positions:
        by_position[position] = []

    salaries = open(fd_slate_file_name)
    # FanDuel-NBA-2021 ET-10 ET-23 ET-65760-players-list.csv
    lines = salaries.readlines()
    found_count = 0
    name_transform = {}

    positions_mapper = {"PG": ["PG", "G", "UTIL"], "SG": ["SG", "G", "UTIL"], "SF": ["SF", "F", "UTIL"], "PF": ["PF", "F", "UTIL"], "C": ["C", "UTIL"]}

    for line in lines[8:]:
        # import pdb; pdb.set_trace()
        parts = line.split(',')
        first_name = line.split(",")[13]
        last_name = line.split(",")[14]
        position = line.split(",")[16]
        team = line.split(",")[17]
        salary = line.split(",")[21]
        status = line.split(",")[23]
        
        full_name = "{} {}".format(first_name, last_name)

        positions = positions_mapper[position]
        
        if status == "INJ":
            continue

        if full_name in name_transform:
            full_name = name_transform[full_name]

        name = full_name

        if name in player_to_fp:
            value = player_to_fp[name]
            found_count += 1

            # if name == "Jonas Valanciunas":
            #     continue

            # if value < 25 or (value * 1000 / float(salary) < 4.4):
            #     print("Filtered out: {} - {}, {}".format(name, value, value * 1000 / float(salary)))
            #     continue

            for pos in positions:
                new_player = Player(name, pos, float(salary), team, value)

                by_position[pos].append(new_player)
        else:
            print("Not found: {}".format(name))
            # name_parts = name.split(' ')
            # for search_name in player_to_fp.keys():
            #     if name_parts[0] in search_name:
            #         print("CANDIDATE: {} - {}".format(name, search_name))
            pass


        # print("{} - {}".format(name, positions))

        # new_player = Player(1)

    print(len(player_to_fp))
    print(found_count)
    # assert len(player_to_fp) == found_count
    # import pdb; pdb.set_trace()

    return by_position


def build_random_line_up(by_position):
    to_return = []
    to_return.append(random_element(by_position['PG']))
    to_return.append(random_element(by_position['SG']))
    to_return.append(random_element(by_position['G']))
    to_return.append(random_element(by_position['SF']))
    to_return.append(random_element(by_position['PF']))
    to_return.append(random_element(by_position['F']))
    to_return.append(random_element(by_position['C']))
    to_return.append(random_element(by_position['UTIL']))
    
    return Roster(to_return)


def random_element(arr):
    idx = random.randint(0, len(arr) - 1)
    return arr[idx]


def select_better_player(players, max_cost, excluding, initial_value):
    better_players = []
    for p in players:
        if p.name in excluding:
            continue
        if p.cost <= max_cost and p.value > initial_value:
            better_players.append(p)

    if len(better_players) == 0:
        return None


    # import pdb; pdb.set_trace()
    return random_element(better_players)

def optimize_roster(roster, by_position):
    initial_cost = roster.cost

    no_improvement_count = 0
    if initial_cost <= 80000:
        # pick a random player
        # swap that player for the best player we can afford that brings more value
        while True:
            swap_idx = random.randint(0, 7)
            if swap_idx in roster.locked_indices:
                assert False
                continue


            to_swap = roster.players[swap_idx]
            position = to_swap.position

            excluding = [p.name for p in roster.players]

            replacement = select_better_player(by_position[position], roster.remainingFunds(80000) + to_swap.cost, excluding, to_swap.value)

            if replacement == None or to_swap.name == replacement.name:
                no_improvement_count += 1
            else:
                no_improvement_count = 0
                roster.relpace(replacement, swap_idx)

            if no_improvement_count > 20:
                return roster


    print(roster)
    assert False

def random_optimizer(by_position):
    best_roster = None
    best_roster_val = 0

    random.seed(time.time())
    for i in range(10000000):
        to_remove = None
        if best_roster != None:
            to_remove = random_element(best_roster.players)
            # import pdb; pdb.set_trace()
            # TODO REMOVE THIS GUY FROM THE RUNNING


        by_position_copied = {}
        for pos, players in by_position.items():
            if to_remove in players:
                players_new = list(players)

                players_new.remove(to_remove)
                by_position_copied[pos] = players_new
            else:
                by_position_copied[pos] = players
            pass

        if to_remove == None:
            by_position_copied = by_position


        random_lineup = build_random_line_up(by_position_copied)
        if random_lineup.cost > 80000 or not random_lineup.is_valid:
            continue

        result = optimize_roster(random_lineup, by_position_copied)
        if result.value >= best_roster_val:
            best_roster = result
            best_roster_val = result.value
            print(result)


def optimize_full_roster_(by_position):
    all_centers = by_position["C"]
    sorted_by_val = sorted(all_centers, key=lambda a: a.value / float(a.cost), reverse=True)
    by_position["C"] = sorted_by_val

    # import pdb; pdb.set_trace()

    # # names_to_lock = ["Spencer Dinwiddie", "Fred VanVleet"]
    # names_to_lock = [sorted_by_val[0].name]
    names_to_lock = []


    to_lock = []
    locked_positions = []
    for name in names_to_lock:
        for pos, players in by_position.items():
            if pos in locked_positions:
                continue
            player_idx = 0
            player_matched = False
            for player in players:
                if name == player.name:
                    to_lock.append((name, pos, player_idx))
                    player_matched = True
                    locked_positions.append(pos)
                    break
                player_idx += 1
            if player_matched:
                break

    # import pdb; pdb.set_trace()
    print(to_lock)
    # exhaustive_optimizer(by_position, to_lock)
    random_optimizer(by_position)



def optimize_single_game(projection_file_name, fd_slate_file_name):
    player_to_fp = get_player_projections(projection_file_name)
    by_position = get_players_by_position(player_to_fp, fd_slate_file_name)

    all_players = []
    for position, players in by_position.items():
        for player in players:
            if not player in all_players:
                all_players.append(player)


    optimize_full_roster_(by_position)
    # single_game_optimizer(all_players)


# current_date = datetime.datetime.now()
# projection_file_name = "money_line_scrape_{}_{}_{}.txt".format(current_date.month, current_date.day, current_date.year)
# player_data_file_name = "salary_data/Yahoo_DF_contest_lineups_update_template.csv"

# optimize_single_game(projection_file_name, player_data_file_name)