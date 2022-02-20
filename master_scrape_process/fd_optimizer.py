from json.encoder import py_encode_basestring_ascii
import random
import json
import datetime
from re import L
import time

from pdb import set_trace

import pandas as pd
from hand_crafted_projections import read_projections


from requests.api import get


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

def increment_index(indices, max_indices, inc_idx, locked_indices):
    while indices[inc_idx] == max_indices[inc_idx] - 1 or inc_idx in locked_indices:
        for i in range(len(indices) - inc_idx):
            idx_to_incr = inc_idx + i
            if idx_to_incr in locked_indices:
                pass
            else:
                indices[inc_idx + i] = 0
        inc_idx -= 1

    indices[inc_idx] += 1

    if inc_idx == 1:
        print("{}/{}".format(indices, max_indices))

    if inc_idx == 0:
        return None

all_positions = ["C","PF", "SF", "SG", "PG"]


def random_elements(arr, count):
    if count > len(arr):
        assert False
    if count == len(arr):
        return arr

    to_return = []
    while True:
        idx = random.randint(0, len(arr) - 1)
        val = arr[idx]
        if not val in to_return:
            to_return.append(val)

        if len(to_return) == count:
            break

    return to_return

def random_element(arr):
    idx = random.randint(0, len(arr) - 1)
    return arr[idx]

def build_random_line_up(by_position):
    to_return = []
    to_return.append(random_element(by_position['C']))
    to_return += random_elements(by_position['PF'], 2)
    to_return += random_elements(by_position['SF'], 2)
    to_return += random_elements(by_position['SG'], 2)
    to_return += random_elements(by_position['PG'], 2)

    return Roster(to_return)


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
    if initial_cost <= 60000:
        # pick a random player
        # swap that player for the best player we can afford that brings more value
        while True:
            swap_idx = random.randint(0, 9)
            if swap_idx == 9:
                swap_idx = 0
            if swap_idx in roster.locked_indices:
                continue

            to_swap = roster.players[swap_idx]
            position = to_swap.position

            excluding = [p.name for p in roster.players]
            replacement = select_better_player(by_position[position], roster.remainingFunds() + to_swap.cost, excluding, to_swap.value)

            if replacement == None or to_swap.name == replacement.name:
                no_improvement_count += 1
            else:
                no_improvement_count = 0
                roster.relpace(replacement, swap_idx)

            if no_improvement_count > 20:
                return roster

    print(roster)
    return roster
    # assert False

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
        if random_lineup.get_cost() > 60000 or not random_lineup.is_valid:
            continue

        result = optimize_roster(random_lineup, by_position_copied)

        if result.get_cost() > 60000:
            print("WARNING INVALID ROSTER RETURNED")
            continue
        if result.value >= best_roster_val:
            best_roster = result
            best_roster_val = result.value
            print(result)


def get_roster(indices, player_pairs, max_indices, locked_indices):
    to_return = []
    seen_names = []
    total_cost = 0
    for i in range(len(all_positions)):
        pos = all_positions[i]
        player1 = player_pairs[pos][indices[i]][0]
        player2 = player_pairs[pos][indices[i]][1]
        if pos == "C":
            to_return.append(player1)
            seen_names.append(player1.name)
            total_cost += player1.cost
        else:
            if player1.name in seen_names or player2.name in seen_names or total_cost > 60000 - ((5 - i) * 12000):
                result = increment_index(indices, max_indices, i, locked_indices)
                # if result == None:
                #     assert False
                return None

            seen_names.append(player1.name)
            seen_names.append(player2.name)
            total_cost += player1.cost
            total_cost += player2.cost

            to_return.append(player1)
            to_return.append(player2)

    roster = Roster(to_return)
    return roster

def exhaustive_optimizer(by_position, to_lock):

    MIN_CONSIDERATION_VAL = 0

    player_pairs = {'C':[], 'PF': [], 'SF': [], 'SG': [], 'PG': []}
    for position in all_positions:
        seen_pairs = []
        available_players = by_position[position]

        if position == "C":
            for p in available_players:
                if p.value < MIN_CONSIDERATION_VAL:
                    continue
                player_pairs[position].append((p, None, p.cost, p.value))
        else:
            for i in range(len(available_players)):
                for j in range(len(available_players)):
                    if j <= i:
                        continue
                    p1 = available_players[i]
                    p2 = available_players[j]

                    seen_key = p1.name + p2.name
                    if seen_key in seen_pairs:
                        import pdb; pdb.set_trace()

                    seen_pairs.append(seen_key)

                    if p1.value < MIN_CONSIDERATION_VAL or p2.value < MIN_CONSIDERATION_VAL:
                        continue

                    player_pairs[position].append((p1, p2, p1.cost + p2.cost, p1.value + p2.value))





    max_indices = []

    for pos, players in player_pairs.items():
        max_indices.append(len(players))
    print(max_indices)
    indices = []
    indices_to_not_increment = []
    for i in range(len(all_positions)):
        pos = all_positions[i]
        was_lock = False
        for lock in to_lock:
            lock_position = lock[1]
            if lock_position == pos:
                indices.append(lock[2])
                indices_to_not_increment.append(i)
                was_lock = True

        if not was_lock:
            indices.append(0)

    assert len(indices) == 5
    best_roster = None
    best_roster_val = 0
    while True:
        inc_idx = len(indices) - 1

        roster = get_roster(indices, player_pairs, max_indices, indices_to_not_increment)
        if roster != None:
            if roster.value > best_roster_val and roster.cost <= 60000:
                best_roster_val = roster.value
                best_roster = roster
                print(roster)

            increment_index(indices, max_indices, inc_idx, indices_to_not_increment)

    # for each position
    # take best available player
    # when we run out of money, backtrack and take a cheaper
    pass


class Player:
    def __init__(self, name, position, cost, team, value, matchup):
        self.name = name
        self.position = position
        self.cost = float(cost)
        self.team = team
        self.value = float(value)
        self.value_per_dollar = self.value * 100 / self.cost
        self.matchup = matchup

    def __repr__(self):
        # return "{} - {} - {} - {} - {} - {}".format(self.name, self.position, self.cost, self.team, self.value, self.value_per_dollar)
        return self.name

class Roster:
    def __init__(self, players):
        self.players = players
        self.cost = sum([float(p.cost) for p in self.players])
        self.value = sum([float(p.value) for p in self.players])
        self.locked_indices = []
        self.is_valid = len(players) == len(set(p.name for p in players))

    @staticmethod
    def FromPlayerString(player_string, by_position):
        player_names = player_string.split(',')
        player_positions = ["C", "PF", "PF", "SF", "SF", "SG", "SG", "PG", "PG"]
        player_list = []
        for i in range(9):
            name = player_names[i]
            pos = player_positions[i]
            player_set = by_position[pos]
            for player in player_set:
                if player.name == name:
                    player_list.append(player)
                    break

            
        return Roster(player_list)

    def get_cost(self):
        # return sum([float(p.cost) for p in self.players])
        return self.cost

    def lockPlayer(self, player):
        if player.position == "C":
            self.players[0] = player
            self.locked_indices.append(0)
        elif player.position == "PF":
            self.players[1] = player
            self.locked_indices.append(1)
        elif player.position == "SF":
            self.players[3] = player
            self.locked_indices.append(3)
        elif player.position == "SG":
            self.players[5] = player
            self.locked_indices.append(5)
        elif player.position == "PG":
            self.players[7] = player
            self.locked_indices.append(7)

    def __repr__(self):
        to_return = ",".join([p.name for p in self.players]) + " {} - {}".format(self.cost, self.value)
        return to_return

    def remainingFunds(self, max_cost=60000):
        return max_cost - self.get_cost()

    def relpace(self, player, idx):
        self.players[idx] = player
        self.cost = sum([float(p.cost) for p in self.players])
        self.value = sum([float(p.value) for p in self.players])

    def atPosition(self, position):
        return [p for p in self.players if p.position == position]

    def getIds(self, id_mapping):
        ids = []
        for p in self.players:
            id = id_mapping[p.name]
            ids.append(id)

        ids.reverse()
        return ",".join(ids)


def get_player_projections(projection_file_name):
    to_read = open(projection_file_name)

    player_to_fp = {}

    lines = to_read.readlines()
    for line in lines:
        parts = line.split("|")
        if len(parts) < 4:
            continue
        if parts[3] == "Fantasy Score":
            player_name = parts[2]
            player_name = player_name.replace(" III", "")
            player_name = player_name.replace(" Jr.", "")
            if parts[4].strip() == "REMOVED":
                continue
            player_to_fp[player_name] = float(parts[4].strip())

    return player_to_fp


def get_players_by_position(player_to_fp, fd_slate_file_name):
    
    by_position = {}
    for position in all_positions:
        by_position[position] = []

    salaries = open(fd_slate_file_name)
    # FanDuel-NBA-2021 ET-10 ET-23 ET-65760-players-list.csv
    lines = salaries.readlines()
    found_count = 0
    name_transform = {'Gary Payton II': 'Gary Payton'}

    for line in lines[1:]:
        parts = line.split(',')
        full_name = parts[3]

        positions = parts[1].split("/")
        salary = parts[7]
        team = parts[9]
        status = parts[11]
        if status == "O":
            continue

        if full_name in name_transform:
            full_name = name_transform[full_name]

        name = full_name

        if name in player_to_fp:

            # name = name.replace(" Jr.", "")
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

def optimize_full_roster(projection_file_name, fd_slate_file_name):
    
    player_to_fp = get_player_projections(projection_file_name)

    new_name_vals = {}
    current_date = datetime.datetime.now()
    player_to_fp = read_projections("past_permorance_{}_{}_{}.txt".format(current_date.month, current_date.day, str(current_date.year)[-2:]))

    for name, fp in player_to_fp.items():
        if " Jr." in name:
            new_name = name.replace(" Jr.", "")
            new_name_vals[new_name] = fp

        if " IV" in name:
            new_name = name.replace(" IV", "")
            new_name_vals[new_name] = fp
    # import pdb; pdb.set_trace()

    for name, fp in new_name_vals.items():
        player_to_fp[name] = fp
    by_position = get_players_by_position(player_to_fp, fd_slate_file_name)

    optimize_full_roster_(by_position)



def three_man_optimizer(all_players):
    best_val = 0
    best_roster = None
    player_ct = len(all_players)
    for i1 in range(player_ct):
        p1 = all_players[i1]

        for i2 in range(player_ct):
            if i2 == i1:
                continue

            p2 = all_players[i2]

            for i3 in range(player_ct):
                if i3 == i1 or i3 == i2:
                    continue
                
                p3 = all_players[i3]

                roster_set = [p1, p2, p3]
                
                total_cost = sum(pl.cost for pl in roster_set)
                if total_cost > 7:
                    continue

                if p1.team == p2.team and p2.team == p3.team:
                    continue
                
                total_value = p1.value * 2 + p2.value * 1.5 +  p3.value
                if total_value > best_val:
                    best_val = total_value
                    best_roster = roster_set

    return best_roster



def single_game_optimizer(all_players):
    best_val = 0
    best_roster = None
    player_ct = len(all_players)
    for i1 in range(player_ct):
        p1 = all_players[i1]

        for i2 in range(player_ct):
            if i2 == i1:
                continue

            p2 = all_players[i2]

            for i3 in range(player_ct):
                if i3 == i1 or i3 == i2:
                    continue
                
                p3 = all_players[i3]

                for i4 in range(player_ct):
                    if i4 == i1 or i4 == i2 or i4 == i3:
                        continue
                    
                    p4 = all_players[i4]

                    for i5 in range(player_ct):
                        if i5 == i1 or i5 == i2 or i5 == i3 or i5 == i4:
                            continue
                        
                        p5 = all_players[i5]
                        roster_set = [p1, p2, p3, p4, p5]
                        
                        total_cost = sum(pl.cost for pl in roster_set)
                        if total_cost > 60000:
                            continue
                        
                        total_value = p1.value * 2 + p2.value * 1.5 +  p3.value * 1.2 + p4.value + p5.value
                        if total_value > best_val:
                            best_val = total_value
                            best_roster = roster_set
                            # print("{} - {}, {}".format(best_roster, total_value, total_cost))


    return best_roster


def optimize_single_game(projection_file_name, fd_slate_file_name):
    player_to_fp = get_player_projections(projection_file_name)
    by_position = get_players_by_position(player_to_fp, fd_slate_file_name)


    new_name_vals = {}
    player_to_fp = read_projections("past_permorance_{}_{}_{}.txt".format(current_date.month, current_date.day, str(current_date.year)[-2:]))
    for name, fp in player_to_fp.items():
        if " Jr." in name:
            new_name = name.replace(" Jr.", "")
            new_name_vals[new_name] = fp

        if " IV" in name:
            new_name = name.replace(" IV", "")
            new_name_vals[new_name] = fp
    # import pdb; pdb.set_trace()

    for name, fp in new_name_vals.items():
        player_to_fp[name] = fp
    by_position = get_players_by_position(player_to_fp, fd_slate_file_name)




    all_players = []
    for position, players in by_position.items():
        for player in players:
            if not player in all_players:
                all_players.append(player)

    single_game_optimizer(all_players)



def optimize_three_man_challenge(projection_file_name, fd_slate_file_name):
    player_to_fp = get_player_projections(projection_file_name)
    by_position = get_players_by_position(player_to_fp, fd_slate_file_name)


    new_name_vals = {}
    player_to_fp = read_projections("past_permorance_{}_{}_{}.txt".format(current_date.month, current_date.day, current_date.year[-2:]))
    for name, fp in player_to_fp.items():
        if " Jr." in name:
            new_name = name.replace(" Jr.", "")
            new_name_vals[new_name] = fp

        if " IV" in name:
            new_name = name.replace(" IV", "")
            new_name_vals[new_name] = fp
    # import pdb; pdb.set_trace()

    for name, fp in new_name_vals.items():
        player_to_fp[name] = fp
    by_position = get_players_by_position(player_to_fp, fd_slate_file_name)




    all_players = []
    for position, players in by_position.items():
        for player in players:
            if not player in all_players:
                all_players.append(player)

    
    best_val = 0
    best_roster = None
    player_ct = len(all_players)
    for i1 in range(player_ct):
        p1 = all_players[i1]

        for i2 in range(player_ct):
            if i2 == i1:
                continue

            p2 = all_players[i2]

            for i3 in range(player_ct):
                if i3 == i1 or i3 == i2:
                    continue
                
                p3 = all_players[i3]

        
                roster_set = [p1, p2, p3]
                
                total_cost = sum(pl.cost for pl in roster_set)
                if total_cost > 7:
                    continue
                
                total_value = p1.value * 2 + p2.value * 1.5 +  p3.value 
                if total_value > best_val:
                    best_val = total_value
                    best_roster = roster_set
                    print("{} - {}, {}".format(best_roster, total_value, total_cost))



def generate_n_rosters(by_position, n, iter_count=1000000):
    # names_to_exclude = [p.name for p in players_to_exclude]
    all_rosters = []

    roster_keys = []

    random.seed(time.time())
    for i in range(iter_count):
        random_lineup = build_random_line_up(by_position)

        if random_lineup.cost > 60000 or not random_lineup.is_valid:
            continue
        
        result = optimize_roster(random_lineup, by_position)

        team_to_count = {}
        for player in result.players:
            if not player.team in team_to_count:
                team_to_count[player.team] = 1
            else:
                team_to_count[player.team] += 1

        is_roster_valid = True
        for team, ct in team_to_count.items():
            if ct > 4:
                is_roster_valid = False

        if not is_roster_valid:
            continue


        all_names = [a.name for a in result.players]
        all_names_sorted = sorted(all_names)
        roster_key = ",".join(all_names_sorted)
        if not roster_key in roster_keys:
            all_rosters.append(result)
            roster_keys.append(roster_key)
        # if roster_count > 50:
        #     break
    all_rosters_sorted = sorted(all_rosters, key=lambda a: a.value, reverse=True)
    __import__('pdb').set_trace()
    return all_rosters_sorted[:n]


def generate_n_best_rosters(by_position, players_to_exclude, iter_count=1000000, seed_roster=None, to_take=1):
    names_to_exclude = players_to_exclude
    if seed_roster != None:
        names_to_exclude += [a.name for a in seed_roster if a != '']

    by_position_exclusive = {}
    for pos, players in by_position.items():
        by_position_exclusive[pos] = []
        for pl in players:
            if pl.name in names_to_exclude:
                continue

            by_position_exclusive[pos].append(pl)
    by_position = by_position_exclusive

    seen_roster_keys = []
    seen_rosters = []

    random.seed(time.time())
    for i in range(iter_count):
        to_remove = None
        by_position_copied = {}
        for pos, players in by_position.items():
            if to_remove in players:
                players_new = list(players)

                players_new.remove(to_remove)
                by_position_copied[pos] = players_new
            else:
                by_position_copied[pos] = players

        if to_remove == None:
            by_position_copied = by_position

        random_lineup = build_random_line_up(by_position_copied)

        is_full_locked = False
        if seed_roster != None:
            is_full_locked = True
            for i in range(9):
                pl = seed_roster[i]
                if pl != '' and pl != None:
                    random_lineup.relpace(pl, i)
                    random_lineup.locked_indices.append(i)
                else:
                    is_full_locked = False


        if is_full_locked:
            print("ROSTER FULLY LOCKED")
            return random_lineup

        if random_lineup.cost > 60000 or not random_lineup.is_valid:
            continue
        
        result = optimize_roster(random_lineup, by_position_copied)

        team_to_count = {}
        for player in result.players:
            if not player.team in team_to_count:
                team_to_count[player.team] = 1
            else:
                team_to_count[player.team] += 1

        is_roster_valid = True
        for team, ct in team_to_count.items():
            if ct > 4:
                is_roster_valid = False

        if not is_roster_valid:
            continue

        all_names = [a.name for a in result.players]
        all_names_sorted = sorted(all_names)
        roster_key = ",".join(all_names_sorted)
        if roster_key in seen_roster_keys:
            continue

        seen_roster_keys.append(roster_key)
        seen_rosters.append(result)
    
    to_return = sorted(seen_rosters, key=lambda a: a.value, reverse=True)[:to_take]
    return to_return


def generate_single_roster(by_position, players_to_exclude, iter_count=1000000, seed_roster=None):
    names_to_exclude = players_to_exclude
    if seed_roster != None:
        names_to_exclude += [a.name for a in seed_roster if a != '']

    by_position_exclusive = {}
    for pos, players in by_position.items():
        by_position_exclusive[pos] = []
        for pl in players:
            if pl.name in names_to_exclude:
                continue

            by_position_exclusive[pos].append(pl)
    by_position = by_position_exclusive
    best_roster = None
    best_roster_val = 0

    random.seed(time.time())
    for i in range(iter_count):
        to_remove = None
        if best_roster != None:
            to_remove = random_element(best_roster.players)

        by_position_copied = {}
        for pos, players in by_position.items():
            if to_remove in players:
                players_new = list(players)

                players_new.remove(to_remove)
                by_position_copied[pos] = players_new
            else:
                by_position_copied[pos] = players

        if to_remove == None:
            by_position_copied = by_position


        # __import__('pdb').set_trace()
        random_lineup = build_random_line_up(by_position_copied)
        #If the above line is throwing:
        # random_lineup = build_random_line_up(by_position)


        is_full_locked = False
        if seed_roster != None:
            # seed_roster.reverse()
            is_full_locked = True
            for i in range(9):
                pl = seed_roster[i]
                if pl != '' and pl != None:
                    random_lineup.relpace(pl, i)
                    random_lineup.locked_indices.append(i)
                else:
                    is_full_locked = False


        if is_full_locked:
            print("ROSTER FULLY LOCKED")
            return random_lineup

        if random_lineup.cost > 60000 or not random_lineup.is_valid:
            continue
        
        # print("Initial:")
        # print(random_lineup)
        result = optimize_roster(random_lineup, by_position_copied)

        team_to_count = {}
        for player in result.players:
            if not player.team in team_to_count:
                team_to_count[player.team] = 1
            else:
                team_to_count[player.team] += 1

        is_roster_valid = True
        for team, ct in team_to_count.items():
            if ct > 4:
                is_roster_valid = False

        if not is_roster_valid:
            continue

        if result.value > best_roster_val:
            best_roster = result
            if result.value >= best_roster_val:
                best_roster_val = result.value

            all_names = [a.name for a in best_roster.players]
            all_names_sorted = sorted(all_names)
            roster_key = ",".join(all_names_sorted)
            # if roster_count > 50:
            #     break
            print(best_roster)

    return best_roster


def filter_by_position(by_position, selector):
    by_position_new = {}
    for pos, players in by_position.items():
        new_players = [p for p in players if selector(p)]
        by_position_new[pos] = new_players

    return by_position_new

def modify_roster(by_position, input_roster, locked_teams):
    by_position_new = filter_by_position(by_position, lambda a: a.team not in locked_teams)
    print(input_roster)
    input_roster = Roster.FromPlayerString(input_roster, by_position)


    seen_rosters = []

    best_roster = None
    best_roster_val = 0

    roster_count = 0

    random.seed(time.time())
    for i in range(1000000):
        result = optimize_roster(input_roster, by_position_new)
        import pdb; pdb.set_trace()

        if result.value >= best_roster_val - 0.5:
        # if result.cost >= min_roster_cost:
        # if result.value >= 56800.0:
            best_roster = result
            if result.value >= best_roster_val:
                best_roster_val = result.value

            all_names = [a.name for a in best_roster.players]
            all_names_sorted = sorted(all_names)
            roster_key = ",".join(all_names_sorted)
            if roster_key in seen_rosters:
                continue

            seen_rosters.append(roster_key)
            print(best_roster)
            roster_count += 1


    import pdb; pdb.set_trace()


def generate_roster_for_single_game(by_position, to_exclude):
    all_player_names = []
    all_players = []
    by_position_exclusive = {}
    for pos, players in by_position.items():
        by_position_exclusive[pos] = []
        for pl in players:
            if pl.name in to_exclude:
                continue

            if not pl.name in all_player_names:
                all_players.append(pl)

    return single_game_optimizer(all_players)

def generate_roster_quiet(by_position):
    best_roster = None
    best_roster_val = 0

    random.seed(time.time())
    for i in range(100000):
        to_remove = None
        if best_roster != None:
            to_remove = random_element(best_roster.players)

        by_position_copied = {}
        for pos, players in by_position.items():
            if to_remove in players:
                players_new = list(players)

                players_new.remove(to_remove)
                by_position_copied[pos] = players_new
            else:
                by_position_copied[pos] = players

        if to_remove == None:
            by_position_copied = by_position

        random_lineup = build_random_line_up(by_position_copied)
        if random_lineup.cost > 60000 or not random_lineup.is_valid:
            continue

        result = optimize_roster(random_lineup, by_position_copied)
        
        # team_to_count = {}
        # for player in result.players:
        #     if not player.team in team_to_count:
        #         team_to_count[player.team] = 1
        #     else:
        #         team_to_count[player.team] += 1

        # is_roster_valid = True
        # for team, ct in team_to_count.items():
        #     if ct > 4:
        #         is_roster_valid = False

        # if not is_roster_valid:
        #     continue

        # __import__('pdb').set_trace()


        if result.value > best_roster_val:
            best_roster = result
            if result.value >= best_roster_val:
                best_roster_val = result.value

    return best_roster


def boost_matchup(by_position, matchup, boost_factor=1.2):
    to_return = {}
    for pos, players in by_position.items():
        if not pos in to_return:
            to_return[pos] = []

        for player in players:
            if player.matchup == matchup:
                player2 = Player(player.name, player.position, player.cost, player.team, player.value * boost_factor, player.matchup)
                
                to_return[pos].append(player2)
            else:
                to_return[pos].append(player)
        

    return to_return


def boost_player(by_position, player_name, boost_factor=1.2):
    to_return = {}
    for pos, players in by_position.items():
        if not pos in to_return:
            to_return[pos] = []

        for player in players:
            if player.name == player_name:
                player2 = Player(player.name, player.position, player.cost, player.team, player.value * boost_factor, player.matchup)
                
                to_return[pos].append(player2)
            else:
                to_return[pos].append(player)
        

    return to_return

def exclude_matchup(by_position, matchup):
    to_return = {}
    for pos, players in by_position.items():
        if not pos in to_return:
            to_return[pos] = []

        for player in players:
            if player.matchup == matchup:
                continue
            else:
                to_return[pos].append(player)

    return to_return



def filter_player_pool_on_matchups(by_position, matchups):
    to_return = {}
    for pos, players in by_position.items():
        if not pos in to_return:
            to_return[pos] = []

        for player in players:
            if player.matchup in matchups:
                to_return[pos].append(player)
        

    return to_return

def validate_results(rosters, seed_rosters):
    roster_key_to_count = {}
    for roster in rosters:
        players = roster.players
        players_sorted = sorted([a.name for a in players])
        roster_key = ",".join(players_sorted)
        if not roster_key in roster_key_to_count:
            roster_key_to_count[roster_key] = 1
        else:
            roster_key_to_count[roster_key] += 1
        pass
    print("Roster distrbution: " + str(roster_key_to_count.values()))
    if seed_rosters != None:
        for i in range(len(seed_rosters)):
            seed_roster = seed_rosters[i]
            roster = rosters[i]
            for j in range(9):
                if seed_roster[j] != '':
                    if seed_roster[j].name != roster.players[j].name:
                        __import__('pdb').set_trace()
                    assert seed_roster[j].name == roster.players[j].name

def construct_upload_template_file(rosters, first_line, entries, player_to_id, seed_rosters, excluded, player_id_to_name):

    # how are these rosters distrbuted?
    # am I preserving the my locks
    # for entry in entries:
    #     pass

    # __import__('pdb').set_trace()
    validate_results(rosters, seed_rosters)

    # __import__('pdb').set_trace()

    timestamp = str(datetime.datetime.now())
    date = timestamp.replace('.', '_')
    date = date.replace(":", "_")
    output_file = open("/Users/amichailevy/Downloads/upload_template_{}.csv".format(date), "x")
    output_file.write(first_line)
    entry_idx = 0
    for entry in entries:
        cells = [entry[0], entry[1], entry[2].strip('"')]
        if entry_idx >= len(rosters):
            break
        roster = rosters[entry_idx]
        players = roster.players
        player_cells = []
        for player in players:
            player_id = player_to_id[player.name]

            player_name = player_id_to_name[player_id]

            player_cells.append(player_name)
            # player_cells.append(player_id)

            # player_cells.append(excluded[entry_idx])

        player_cells.reverse()
        cells += player_cells

        if len(cells) != 12:
            __import__('pdb').set_trace()

        to_write = ','.join(['"{}"'.format(c) for c in cells]) 

        output_file.write(to_write + "\n")
        entry_idx += 1
        

    output_file.close()
    pass


def load_current_lineups(path, player_id_to_name):
    file = open(path, "r")
    lines = file.readlines()
    rosters = []
    for line in lines[1:]:
        parts = line.split(',')
        if parts[0].strip('"') == '':
            break
        players = parts[3:12]
        for player in players:
            if not player.strip().strip('"') in player_id_to_name:
                __import__('pdb').set_trace()

        players = [player_id_to_name[pl.strip().strip('"')] for pl in players]
        rosters.append(players)

    return rosters


def parse_upload_template(csv_template_file, exclude):
    template_file_lines = open(csv_template_file, "r").readlines()
    entries = []
    name_to_player_id = {}
    name_to_salary = {}
    player_id_to_name = {}
    player_id_to_fd_name = {}
    name_to_team = {}
    players_to_remove = []

    name_conversion = {"Nic Claxton": "Nicolas Claxton"}

    first_line = template_file_lines[0]
    for line in template_file_lines[1:]:
        parts = line.split(',')
        entry_id = parts[0].strip('"').strip()
        contest_id = parts[1].strip('"').strip()
        contest_name = parts[2].strip('"').strip()


        if entry_id != '' or contest_id != '' or contest_name != '':
            entries.append((entry_id, contest_id, contest_name))

        if len(parts) < 14:
            continue
        
    
        name_id = parts[13].strip('"').split(':')

        name_and_id = parts[13].strip('"')
        if len(name_id) == 1:
            continue
        
        injury_status = parts[25]

        player_id = name_id[0]
        fd_name = name_id[1]
        team = parts[23]
        salary = parts[21]
        if fd_name in name_conversion:
            fd_name = name_conversion[fd_name]
        name = normalize_name(fd_name)

        name_to_player_id[name] = player_id
        name_to_team[name] = team
        name_to_salary[name] = salary

        player_id_to_name[player_id] = name
        
        player_id_to_fd_name[player_id] = name_and_id
        
        if name in exclude:
            players_to_remove.append(name)
            continue

        if injury_status == 'O':
            print("{} is OUT".format(name))
            players_to_remove.append(name)
            continue

    return player_id_to_name, name_to_team, name_to_salary, name_to_player_id, first_line, entries, players_to_remove, player_id_to_fd_name


def print_lineups(lineups):
    __import__('pdb').set_trace()

def regenerate_MME_ensemble(by_position, csv_template_file, start_time_to_teams, current_time, exlcude):
    locked_teams = []

    for start_time, teams in start_time_to_teams.items():
        if current_time >= start_time:
            locked_teams += teams

    all_matchups = []
    idx = 0
    for _ in range(len(locked_teams)):
        if idx >= len(locked_teams):
            break
        all_matchups.append("{}@{}".format(locked_teams[idx], locked_teams[idx + 1]))
        idx += 2

    for pos, players in by_position.items():
        for player in players:
            matchup = player.matchup
            if not matchup in all_matchups:
                if not matchup in all_matchups:
                    all_matchups.append(matchup)


    player_id_to_name, name_to_team, name_to_salary, _, _, _, players_to_remove, _ = parse_upload_template(csv_template_file, exlcude)

    by_position2 = {}
    for pos, players in by_position.items():
        by_position2[pos] = []
        for player in players:
            if player.name in players_to_remove:
                continue
            by_position2[pos].append(player)

    by_position = by_position2


    current_lineups = load_current_lineups(csv_template_file, player_id_to_name)

    seed_rosters = []
    for lineup in current_lineups:
        starting_lineup = []
        for lp in lineup:
            team = name_to_team[lp]
            salary = name_to_salary[lp]
            if team in locked_teams:
                player = Player(lp, '', salary, team, 0, '')
                starting_lineup.append(player)
            else:
                starting_lineup.append('')

        starting_lineup.reverse()
        print(starting_lineup)
        seed_rosters.append(starting_lineup)

    by_position_filtered_on_locked_teams = {}
    for pos, players in by_position.items():
        if not pos in by_position_filtered_on_locked_teams:
            by_position_filtered_on_locked_teams[pos] = []

        for player in players:
            if not player.team in locked_teams:
                by_position_filtered_on_locked_teams[pos].append(player)
            else:
                print("Filtered out: {} {}".format(player, player.team))
        
    generate_MME_ensemble(by_position_filtered_on_locked_teams, csv_template_file, start_time_to_teams, all_matchups, seed_rosters)

def serialize_player_pool(player_pool):
    dict_to_serialize = {}
    for pos, players in player_pool.items():
        dict_to_serialize[pos] = []
        for player in players:
            dict_to_serialize[pos].append({"name": player.name, "position": player.position, "value": player.value, "cost": player.cost, "team": player.team})

    return json.dumps(dict_to_serialize)


def generate_optimal_roster_plus_9_exclusive(all_results, seed_rosters, by_position, iter_count_long, iter_count_short):
    seed_roster = None
    if seed_rosters != None:
        seed_roster = seed_rosters[len(all_results)]

    result = generate_unique_rosters(by_position, 1, [], iter_count_long, seed_roster)
    all_results.append(result[0])

    players = result[0].players
    for pl in players:
        if seed_rosters != None and len(all_results) >= len(seed_rosters):
            return
        seed_roster = None
        if seed_rosters != None:
            seed_roster = seed_rosters[len(all_results)]
        result = generate_unique_rosters(by_position, 1, [pl.name], iter_count_short, seed_roster)
        all_results.append(result[0])
        print("{} RESULT: {}".format(len(all_results), result))


def exclude_every_pair_of_players(player_list, all_results, seed_rosters, by_position, iter_count_short):
    for i in range(len(player_list)):
        for j in range(len(player_list)):
            if j <= i:
                continue

            pl1 = player_list[i]
            pl2 = player_list[j]


            seed_roster = None
            if seed_rosters != None:
                seed_roster = seed_rosters[len(all_results)]
            result = generate_unique_rosters(by_position, 1, [pl1.name, pl2.name], iter_count_short, seed_roster)
            all_results.append(result[0])
            print("{} RESULT: {}".format(len(all_results), result))
            
    pass


# n_C_2 n = number of matchups
def boost_each_matchup_pair(all_results, seed_rosters, by_position, iter_count_short, all_matchups):
    matchup_count = len(all_matchups)
    for i in range(matchup_count):
        for j in range(matchup_count):
            if j <= i:
                continue
            matchup1 = all_matchups[i]
            matchup2 = all_matchups[j]

            by_position_filtered1 = boost_matchup(by_position, matchup1, 1.33)
            by_position_filtered = boost_matchup(by_position_filtered1, matchup2, 1.33)

            seed_roster = None
            if seed_rosters != None:
                seed_roster = seed_rosters[len(all_results)]

            result = generate_unique_rosters(by_position_filtered, 1, [], iter_count_short, seed_roster)
            all_results.append(result[0])

            print("{}, {}".format(matchup1, matchup2))
            print("{} RESULT: {}".format(len(all_results), result))

# n
def boost_each_matchup(all_results, seed_rosters, by_position, iter_count_short, all_matchups):
    for matchup in all_matchups:
        by_position_filtered = boost_matchup(by_position, matchup, 1.2)
        
        seed_roster = None
        if seed_rosters != None:
            seed_roster = seed_rosters[len(all_results)]

        result = generate_unique_rosters(by_position_filtered, 1, [], iter_count_short, seed_roster)
        all_results.append(result[0])

        print("boosted: {}".format(matchup))
        print("{} RESULT: {}".format(len(all_results), result))

# n_C_2 n = number of matchups
def exclude_each_match_pair(all_results, seed_rosters, by_position, iter_count_short, all_matchups):
    matchup_count = len(all_matchups)
    for i in range(matchup_count):
        for j in range(matchup_count):
            if j <= i:
                continue
            matchup1 = all_matchups[i]
            matchup2 = all_matchups[j]

            by_position_filtered1 = exclude_matchup(by_position, matchup1)
            by_position_filtered = exclude_matchup(by_position_filtered1, matchup2)

            seed_roster = None
            if seed_rosters != None:
                seed_roster = seed_rosters[len(all_results)]

            result = generate_unique_rosters(by_position_filtered, 1, [], iter_count_short, seed_roster)
            all_results.append(result[0])

            print("{}, {}".format(matchup1, matchup2))
            print("{} RESULT: {}".format(len(all_results), result))

def filter_on_matchup_pair(all_results, seed_rosters, by_position, iter_count_short, all_matchups):
    matchup_count = len(all_matchups)
    for i in range(matchup_count):
        for j in range(matchup_count):
            if j <= i:
                continue
            matchup1 = all_matchups[i]
            matchup2 = all_matchups[j]

            by_position_filtered = filter_player_pool_on_matchups(by_position, [matchup1, matchup2])

            seed_roster = None
            if seed_rosters != None:
                seed_roster = seed_rosters[len(all_results)]

            result = generate_unique_rosters(by_position_filtered, 1, [], iter_count_short, seed_roster)
            all_results.append(result[0])

            print("{}, {}".format(matchup1, matchup2))
            print("{} RESULT: {}".format(len(all_results), result))

    pass


def generate_rosters_3(by_position, iter_count_fast, iter_count_slow, seed_rosters, all_matchups, start_time_to_matchup, entries):
    seed_roster1 = None
    seed_roster2 = None
    seed_roster3 = None
    if seed_rosters != None:
        seed_roster1 = seed_rosters[0]
        seed_roster2 = seed_rosters[1]
        seed_roster3 = seed_rosters[2]

    # generate_roster_25(by_position, iter_count_slow, seed_rosters, entries)
    # __import__('pdb').set_trace()
    
    result1 = generate_unique_rosters(by_position, 1, [], iter_count_slow, seed_roster1)
    players_sorted = sorted(result1[0].players, key=lambda a: a.cost, reverse=True)
    print("Exclude: {}".format(players_sorted[0].name))
    result2 = generate_unique_rosters(by_position, 1, [players_sorted[0].name], iter_count_slow, seed_roster2)
    print("Exclude: {}".format(players_sorted[1].name))
    result3 = generate_unique_rosters(by_position, 1, [players_sorted[1].name], iter_count_slow, seed_roster3)
    

    return [result1[0], result2[0], result3[0]]


def to_roster_key(roster):
    return "|".join(sorted([a.name for a in roster.players]))

def get_top_20_players_by_value_sorted_by_price(by_position):
    seen_names = []
    all_players = []
    for pos, players in by_position.items():
        for player in players:
            if not player.name in seen_names:
                all_players.append(player)
                seen_names.append(player.name)

    all_players_sorted_by_value = sorted(all_players, key=lambda a: a.value / a.cost, reverse=True)[:20]
    to_return =  sorted(all_players_sorted_by_value, key=lambda a: a.cost, reverse=True)

    return to_return


def generate_best_roster(by_position, iter_count_slow, seed_rosters, entries):
    entry_id_to_count = {}
    for entry in entries:
        entry_id = entry[1]
        if not entry_id in entry_id_to_count:
            entry_id_to_count[entry_id] = 0
        entry_id_to_count[entry_id] += 1

    max_take_count = max(entry_id_to_count.values())

    if seed_rosters != None:
        pass

    # __import__('pdb').set_trace()

    entry_id_to_roster_list = {}
    to_return = []
    if seed_rosters == None:
        results = generate_n_best_rosters(by_position, [], iter_count_slow, seed_roster=None, to_take=max_take_count)

        best_roster_value = results[0].value

        seen_entry_ids = []
        for entry in entries:
            entry_id = entry[1]
            if entry_id in seen_entry_ids:
                continue

            entry_rosters = []
            seen_entry_ids.append(entry_id)
            count = entry_id_to_count[entry_id]
            print("{} {}".format(entry_id, count))
            for i in range(count):
                to_append = results[i]
                if best_roster_value - to_append.value > 10:
                    entry_rosters.append(results[0])
                else:
                    entry_rosters.append(to_append)

            entry_id_to_roster_list[entry_id] = entry_rosters
            
        for entry in entries:
            entry_id = entry[1]
            to_return.append(entry_id_to_roster_list[entry_id].pop())

    else:
        seed_roster_string_to_result = {}
        # map entry_id + seed_roster combo to resolved roster
        # check that map, to see if we need a modification?
        # ---
        # generate_n_best_rosters to separate n rosters with the same entry id and the same seed roster
        entry_idx = 0
        for entry in entries:
            print("----{}".format(entry_idx))
            seed_roster = seed_rosters[entry_idx]
            seed_roster_string = ""
            for a in seed_roster:
                if a == "":
                    seed_roster_string += ","
                else:
                    seed_roster_string += a.name + ","
            # __import__('pdb').set_trace()
            # if len(seed_roster_string_to_result.keys()) > 10:
            #     __import__('pdb').set_trace()
            if seed_roster_string in seed_roster_string_to_result:
                matched_roster = seed_roster_string_to_result[seed_roster_string]
                
                to_return.append(Roster(list(matched_roster.players)))
                entry_idx += 1
                continue

            result1 = generate_single_roster(by_position, [], iter_count_slow, seed_roster=seed_roster)
            seed_roster_string_to_result[seed_roster_string] = result1
            to_return.append(result1)

            entry_idx += 1
            pass
        
    # __import__('pdb').set_trace()
    return (to_return, [])

def generate_rosters_by_exclusion(by_position, iter_count_slow, iter_count_fast, seed_rosters, entries):
    to_return = []
    roster_keys = []
    excluded = []

    seed_roster = None
    if seed_rosters != None:
        seed_roster = seed_rosters[len(to_return)]
    
    print("First roster!")
    result1 = generate_single_roster(by_position, [], iter_count_slow, seed_roster=seed_roster)
    to_return.append(result1)
    roster_keys.append(to_roster_key(result1))
    excluded.append('')


    sorted_players = sorted(result1.players, key=lambda a: a.cost, reverse=True)
    # sorted_players = get_top_20_players_by_value_sorted_by_price(by_position)
    print("SORTED PLAYERS: {}".format(sorted_players))
    # roster_key, roster, excludes
    # for each new roster - if we have seen this roster key, add a random new exclude (from the colided roster) and continue
    for i in range(len(entries) - 1):
        print("RESOLVED ENTRIRES: {}".format(len(to_return)))
        as_binary = "{0:b}".format(513 + i)[::-1]
        to_exclude = []
        random.seed(i)
        for digit_idx in range(len(sorted_players)):
            # CUTTOFF = 0.79

            # to_exclude.append(sorted_players[i].name)
            break

            # break
            # if as_binary[digit_idx] == '1':
            # if as_binary[digit_idx] == '0':
            # if random.uniform(0, 1) > CUTTOFF:
            #     print("Exclude: {}".format(sorted_players[digit_idx]))
            #     to_exclude.append(sorted_players[digit_idx].name)


        seed_roster = None
        if seed_rosters != None:
            seed_roster = seed_rosters[len(to_return)]


        # print("boosted: {}".format(locked_center))
        # by_position2 = boost_player(by_position, locked_center, 10)
        by_position2 = by_position


        result = generate_single_roster(by_position2, to_exclude, iter_count_fast, seed_roster=seed_roster)

        roster_key = to_roster_key(result)


        if roster_key in roster_keys:
            print("ROSTER KEY COLLISION: {}\n{}".format(len(roster_keys), roster_key))
            match_index = roster_keys.index(roster_key)
            names = roster_keys[match_index].split("|")
            for i in range(50):
                new_exclude = random_element(names)
                print("i idx: {} {}".format(i, new_exclude))
                if not new_exclude in to_exclude and (seed_roster == None or not new_exclude in seed_roster):
                    to_exclude.append(new_exclude)
                    result2 = generate_single_roster(by_position, to_exclude, iter_count_fast, seed_roster=seed_roster)
                    # untested
                    roster_key = to_roster_key(result2)
                    if roster_key in roster_keys:
                        continue


                    result = result2
                    break
                
        #         __import__('pdb').set_trace()

        to_return.append(result)
        if roster_key in roster_keys:
            __import__('pdb').set_trace()

        assert roster_key not in roster_keys
        roster_keys.append(roster_key)
        excluded.append("|".join(to_exclude))

            
        print("---")
    return (to_return, excluded)


def generate_rosters_strategic(by_position, iter_count_fast, iter_count_slow, seed_rosters, all_matchups, start_time_to_matchup, entries):

    generated_rosters = []

    random_rosters_to_generate = 20

    for i in range(random_rosters_to_generate):
        seed_roster = None
        if seed_rosters != None:
            seed_roster = seed_rosters[i]

        result = None
        for i in range(20):
            result = generate_single_roster(by_position, [], 7, seed_roster)
            if result != None:
                break

        generated_rosters.append(result)

    # __import__('pdb').set_trace()
    generated_ct = len(generated_rosters)
    assert entries[generated_ct -1][2] == entries[0][2]
    # assert entries[generated_ct -1][2] != entries[generated_ct][2]

    if seed_rosters != None:
        seed_rosters = seed_rosters[random_rosters_to_generate:]

    generated_rosters += generate_roster_ensemble(by_position, iter_count_fast, iter_count_slow, seed_rosters, all_matchups, start_time_to_matchup)

    # rosters_to_generate = len(entries)

    assert len(generated_rosters) == len(entries)
    # for roster in generated_rosters:
    #     print(roster)
    
    # all_results = []
    # while len(all_results) < rosters_to_generate:
    #     all_results += list(generated_rosters)

    # return all_results[:rosters_to_generate]

    return generated_rosters

def generate_roster_ensemble_exhaustive(by_position, seed_rosters):


    if seed_rosters != None:
        seed_rosters_sorted = sorted(seed_rosters, key=lambda a: len([b for b in a if b != ""]), reverse=True)

        # generate each of these rosters 1 by 1 and add them to our pool of unique keys

    unique_rosters = []
    result = generate_n_rosters(by_position, 1000, 100000)



    # generate the n best rosters
    pass

def generate_roster_ensemble(by_position, iter_count_short, iter_count_long, seed_rosters, all_matchups, start_time_to_matchup):
    # last_six_matchups =  all_matchups[-6:]
    last_five_matchups = all_matchups[-5:]
    print("last five matchups")
    print(last_five_matchups)
    # if seed_rosters != None, then we don't want to generate more than we have
    all_results = []

    # 10 rosters
    generate_optimal_roster_plus_9_exclusive(all_results, seed_rosters, by_position, iter_count_long, iter_count_short)


    by_position_filtered = filter_player_pool_on_matchups(by_position, last_five_matchups)


    generate_optimal_roster_plus_9_exclusive(all_results, seed_rosters, by_position_filtered, iter_count_long, iter_count_short)


    for i in range(len(all_results)):
        result = all_results[i]
        if i == 0:
            print("Optimal - {}".format(result))
        elif i < 10:
            to_exclude = all_results[0].players[i - 1]
            print("Exclude: {} - {}".format(to_exclude, result))
        elif i == 10:
            print("Optimal - {}".format(result))
        else:
            to_exclude = all_results[10].players[i - 11]
            print("Exclude: {} - {}".format(to_exclude, result))
            


    # __import__('pdb').set_trace()
    
    # #5
    # boost_each_matchup(all_results, seed_rosters, by_position, iter_count_short, all_matchups)
    
    # TODO
    

    # #10
    # boost_each_matchup_pair(all_results, seed_rosters, by_position, iter_count_short, last_six_matchups)


    # for i in range(len(all_results)):
    #     to_print = all_results[i]
    #     if i == 0:
    #         print("Optimal - {}".format(to_print))
    #     elif i < 10:
    #         # __import__('pdb').set_trace()
    #         to_exclude = all_results[0].players[i - 1]
    #         print("Exclude: {} - {}".format(to_exclude, to_print))
    #     else:
    #         counter = 0
    #         for idx1 in range(len(all_matchups)):
    #             for idx2 in range(len(all_matchups)):
    #                 if idx1 <= idx2:
    #                     continue
    #                 to_print = all_results[i + counter]
    #                 boosted = "Boosted: {} - {}".format(last_six_matchups[idx1], last_six_matchups[idx2])
    #                 print("{} - {}".format(boosted, to_print))
    #                 counter += 1

    #         break

    # __import__('pdb').set_trace()


    # __import__('pdb').set_trace()
    # player_list = all_results[0].players



    # exclude_every_pair_of_players(player_list, all_results, seed_rosters, by_position, iter_count_short)
    # # 5C2 = 10
    # boost_each_matchup_pair(all_results, seed_rosters, by_position, iter_count_short, all_matchups)


    # eight_and_10_matchups = start_time_to_matchup[8]
    # ten_matchups = start_time_to_matchup[10]
    # eight_and_10_matchups += ten_matchups
    # #20
    # eight_and_10_player_pool = filter_player_pool_on_matchups(by_position, eight_and_10_matchups)

    # generate_optimal_roster_plus_9_exclusive(all_results, seed_rosters, eight_and_10_player_pool, iter_count_long, iter_count_short)
    
    # #30
    # ten_player_pool = filter_player_pool_on_matchups(by_position, ten_matchups)
    # generate_optimal_roster_plus_9_exclusive(all_results, seed_rosters, ten_player_pool, iter_count_long, iter_count_short)
    
    # #41
    # boost_each_matchup(all_results, seed_rosters, by_position, iter_count_short, all_matchups)
    
    # #51
    # boost_each_matchup_pair(all_results, seed_rosters, eight_and_10_player_pool, iter_count_short, eight_and_10_matchups)

    # # 5C2 = 10
    # exclude_each_match_pair(all_results, seed_rosters, by_position, iter_count_short, all_matchups)
    

    # filter_on_matchup_pair()

    return all_results

def print_lineup_csv(csv_upload_file, csv_template_file):
    player_id_to_name, _, _, name_to_player_id, first_line, entries, _ = parse_upload_template(csv_template_file)
    lines = open(csv_upload_file, "r").readlines()
    for line in lines[1:]:
        players = line.split(',')[3:]
        roster_players = []
        for player in players:
            name = player_id_to_name[player.strip().strip('"')]
            roster_players.append(name)

        print(",".join(roster_players))


    __import__('pdb').set_trace()


def remove_players_from_player_pool(by_position, players_to_remove, overrides={}):
    to_return = {}
    for pos, players in by_position.items():
        to_return[pos] = []
        print(players)
        for player in players:
            if player.name in players_to_remove:
                print("REMOVING: {}".format(player.name))
                continue

            if player.name in overrides:
                player.value = overrides[player.name]

            to_return[pos].append(player)
    return to_return

def generate_MME_ensemble(by_position, csv_template_file, start_time_to_teams, all_matchups=None, seed_rosters=None):
    if all_matchups == None:
        all_matchups = []
        for pos, players in by_position.items():
            for player in players:
                matchup = player.matchup
                if not matchup in all_matchups:
                    all_matchups.append(matchup)

    # parse the file to load pre-existing rosters.
    # lock players in those rosters based on the time.
    # optimize with the player locks in place
    start_times_file = open("start_times2.txt", "r")
    lines = start_times_file.readlines()
    start_times = []
    team1_team2_start = []
    for line in lines:
        line = line.strip()
        if line == '':
            continue

        team1_team2_start.append(line.strip('@'))
        if len(team1_team2_start) == 3:
            start_times.append(team1_team2_start)
            team1_team2_start = []

    team_to_start_time = {}

    for start_time in start_times:
        team1 = start_time[0]
        team2 = start_time[1]
        team_to_start_time[team1] = start_time[2]
        team_to_start_time[team2] = start_time[2]

    player_id_to_name, _, _, name_to_player_id, first_line, entries, players_to_remove, player_id_to_fd_name = parse_upload_template(csv_template_file, [])

    # overrides = {"Talen Horton-Tucker": 19}

    by_position = remove_players_from_player_pool(by_position, players_to_remove)
    # parse this file
    # get all the games I'm exposed to
    # get player id mapping
    #only optimize the rosters that are starting now
    # master the art of re-optimizing
    
    iter_count_slow = int(80000 / 1)
    iter_count_fast = int(50000 / 3)
    all_results = []

    matchup_to_start_time = {}
    start_time_to_matchup = {}
    for start_time, teams in start_time_to_teams.items():
        slate = ""
        start_time_to_matchup[start_time] = []
        for team in teams:
            if slate == "":
                slate += team
            else:
                slate += "@{}".format(team)
                start_time_to_matchup[start_time].append(slate)
                matchup_to_start_time[slate] = start_time
                slate = ""
            pass


    # generate_roster_ensemble_exhaustive(by_position, seed_rosters)
    # matchups_sorted = sorted(all_matchups, key=lambda a: matchup_to_start_time[a])

    #entries
    #[(entry_id, contest_id, contest_name)]

    # __import__('pdb').set_trace()

    # if len(entries) == 3:
    #     generated_rosters = generate_rosters_3(by_position, iter_count_fast, iter_count_slow, seed_rosters, matchups_sorted, start_time_to_matchup, entries)
    # elif len(entries) == 25:
    #     pass
    # else:
    #     generated_rosters = generate_rosters_strategic(by_position, iter_count_fast, iter_count_slow, seed_rosters, matchups_sorted, start_time_to_matchup, entries)
    
    (generated_rosters, excluded) = generate_best_roster(by_position, iter_count_slow, seed_rosters, entries)
    # (generated_rosters, excluded) = generate_rosters_by_exclusion(by_position, iter_count_slow, iter_count_fast, seed_rosters, entries)


    print("RESOLVED ROSTERS:\n----------\n")

    for roster in generated_rosters:
        print(roster)

    # __import__('pdb').set_trace()

    construct_upload_template_file(generated_rosters, first_line, entries, name_to_player_id, seed_rosters, excluded, player_id_to_fd_name)


def generate_unique_rosters(by_position, ct, players_to_exclude=[], iter_count=1000000, seed_roster=None):
   
    resovled_rosters =[]
    for i in range(ct):
        print("{}---------------{}".format(i + 1, i + 1))
        best_roster1 = generate_single_roster(by_position, players_to_exclude, iter_count=iter_count, seed_roster=seed_roster)

        players_to_exclude += best_roster1.players
        resovled_rosters.append(best_roster1)
    
    return resovled_rosters

def generate_rosters(by_position, evaluator):
    seen_rosters = []

    best_roster = None
    best_roster_val = 0

    roster_count = 0

    random.seed(time.time())
    for i in range(10000000):
        to_remove = None
        if best_roster != None:
            to_remove = random_element(best_roster.players)

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
        if random_lineup.cost > 60000 or not random_lineup.is_valid:
            continue


        result = optimize_roster(random_lineup, by_position_copied)

        if result.value >= best_roster_val - 0.5:
        # if result.cost >= min_roster_cost:
        # if result.value >= 56800.0:
            best_roster = result
            if result.value >= best_roster_val:
                best_roster_val = result.value

            all_names = [a.name for a in best_roster.players]
            all_names_sorted = sorted(all_names)
            roster_key = ",".join(all_names_sorted)
            if roster_key in seen_rosters:
                continue

            seen_rosters.append(roster_key)
            if evaluator != None:
                evaluator.Eval(result)

            # if roster_count > 50:
            #     break
            print(best_roster)
            roster_count += 1



if __name__ == "__main__":
    current_date = datetime.datetime.now()
    projection_file_name = "money_line_scrape_{}_{}_{}.txt".format(current_date.month, current_date.day, current_date.year)
    # player_data_file_name = "salary_data–FanDuel-NBA-2021 ET-10 ET-28 ET-66075-players-list.csv"
    # player_data_file_name = "salary_data/FanDuel-NBA-2021 ET-10 ET-28 ET-66078-players-list.csv"
    player_data_file_name = "salary_data/FanDuel-NBA-2021 ET-11 ET-02 ET-66298-players-list.csv"



    # single slate:
    # player_data_file_name = "salary_data/FanDuel-NBA-2021 ET-11 ET-01 ET-66261-players-list.csv"
    # optimize_three_man_challenge(projection_file_name, player_data_file_name)

   #

    #

    # optimize_single_game(projection_file_name, player_data_file_name)


    optimize_full_roster(projection_file_name, player_data_file_name)

