import math
import json
import uuid
from projection_providers.NBA_WNBA_Projections import NBA_WNBA_Projections, NBA_Projections_dk
import random
import datetime
import utils
import statistics
from ScrapeProcessManager import run
from Optimizer import FD_NBA_Optimizer, DK_NBA_Optimizer
import csv
import itertools
import hashlib

# produce a table of projections
# generate an ensemble of rosters
# produce a file to upload


def parse_upload_template(csv_template_file, exclude, sport, offset = 0, entry_filter=None):
    template_file_lines = open(csv_template_file, "r").readlines()
    entries = []
    name_to_player_id = {}
    name_to_salary = {}
    player_id_to_name = {}
    player_id_to_fd_name = {}
    name_to_team = {}
    players_to_remove = []

    first_line = template_file_lines[0]
    for line in template_file_lines[1:]:
        parts = line.split(',')
        entry_id = parts[0].strip('"').strip()
        contest_id = parts[1].strip('"').strip()
        contest_name = parts[2].strip('"').strip().strip('"')

        if '"' in contest_name:
          __import__('pdb').set_trace()

        if entry_id != '' or contest_id != '' or contest_name != '':
            if entry_filter == None or entry_filter in contest_name:
                entries.append((entry_id, contest_id, contest_name))


        # __import__('pdb').set_trace()
        
        if len(parts) < 14:
            continue
    
        name_id = parts[13 - offset].strip('"').split(':')

        name_and_id = parts[13 - offset].strip('"')

        if len(name_id) == 1:
            continue
        injury_status = parts[25 - offset]

        player_id = name_id[0]
        fd_name = name_id[1]
        team = parts[23 - offset]
        salary = parts[21 - offset]
        name = utils.normalize_name(fd_name)

        name_to_player_id[name] = player_id
        name_to_team[name] = team
        name_to_salary[name] = salary

        player_id_to_name[player_id] = name
        
        player_id_to_fd_name[player_id] = name_and_id
        
        if name in exclude:
            players_to_remove.append(name)
            continue
        
        if sport == "MLB" and parts[30 - offset].strip() != "P" and parts[29 - offset] == '0':
          print("{} not in batting order".format(name))
          # __import__('pdb').set_trace()
          continue
        
        if injury_status == 'O' or injury_status == "IL" or injury_status == "NA":
            # print("{} is OUT".format(name))
            players_to_remove.append(name)
            continue

    if len(player_id_to_name) == 0:
        # why??
        __import__('pdb').set_trace()

    return player_id_to_name, name_to_team, name_to_salary, name_to_player_id, first_line, entries, players_to_remove, player_id_to_fd_name

def get_name_to_player_objects(by_position):
  name_to_player_objects = {}
  for pos, players in by_position.items():
    for player in players:
      if not player.name in name_to_player_objects:
        name_to_player_objects[player.name] = []
      
      name_to_player_objects[player.name].append(player)

  return name_to_player_objects

def parse_existing_rosters(filepath):
  file = open(filepath)
  file_reader = csv.reader(file, delimiter=',', quotechar='"')
  entries = []
  first_line = True

  for parts in file_reader:
    if first_line:
      first_line = False
      continue
    player_ids = [a for a in parts]
    entries.append(player_ids)

  # TODO: potentially sort these by entry fee
  return entries

def filter_out_locked_teams(by_position, locked_teams):
  to_return = {}
  for pos, players in by_position.items():
    if not pos in to_return:
      to_return[pos] = []

    for player in players:
      if player.team in locked_teams:
        continue

      if player.value < 0.01:
        continue
      
      to_return[pos].append(player)
  
  return to_return

def construct_upload_template_file(rosters, first_line, entries, player_to_id, player_id_to_name, index_strings):
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

        # player_cells.reverse()
        cells += player_cells

        # if len(cells) != 12:
        #     __import__('pdb').set_trace()

        to_write = ','.join(['"{}"'.format(c) for c in cells])
        if index_strings != None:
          to_write += ",{}".format(index_strings[entry_idx])

        output_file.write(to_write + "\n")
        entry_idx += 1
        

    output_file.close()

def get_players_by_value(by_position, team_set):
  all_players = []
  all_names = []
  name_to_position = {}
  for pos, players in by_position.items():
    for player in players:
      team = player.team
      if team not in team_set:
        continue

      name = player.name

      if not name in name_to_position:
        name_to_position[name] = ()

      name_to_position[name] += (pos,)

      if name in all_names:
        continue
      
      all_names.append(name)
      adjusted_value = round(player.value / player.cost * 100, 2)
      all_players.append((player, adjusted_value))

  all_players_with_position = []
  for player in all_players:

    player += (name_to_position[player[0].name],)
    all_players_with_position.append(player)

  all_players_sorted = sorted(all_players_with_position, key=lambda a: a[1], reverse=True)
  return all_players_sorted
  

def is_roster_valid(roster):
  team_ct = {}
  for pl in roster.players:
    team = pl.team
    if not team in team_ct:
      team_ct[team] = 1
    else:
      team_ct[team] += 1

    if team_ct[team] == 5:
      return False
    
  return True


# TODO:
# team_to_opp = {'BOS': 'OKC', 'OKC': 'BOS', 'WAS': 'MIL', 'MIL': 'WAS', 'SAC': 'UTA', 'UTA': 'SAC'}

def is_roster_valid_dk(roster):
  team_ct = {}
  for pl in roster.players:
    team = pl.team
    # opp = pl.opp
    # opp = team_to_opp[team]
    opp = pl.opp

    # TODO:
    
    if not team in team_ct:
      team_ct[team] = 1
      team_ct[opp] = 1
    else:
      team_ct[team] += 1
      team_ct[opp] += 1
    
  # __import__('pdb').set_trace()
  
  return len(team_ct.keys()) > 2


dk_positions = ["PG", "SG", "SF", "PF", "C", "G", "F", "UTIL"]

def consider_swap(idx1, idx2, team_to_start_time, players, name_to_positions, locked_players):
  if locked_players != None and (locked_players[idx1] != '' or locked_players[idx2] != ''):
    return
  # if one of these players is locked (zero projection) abort the swap
  player1 = players[idx1]
  player2 = players[idx2]
  # player 1 is specific
  # player 1 is general
  # we want specific to be before the general
  if team_to_start_time[player1.team] > team_to_start_time[player2.team]:
    # make sure the swap is valid!
    positions = name_to_positions[player2.name]
    if any([p == dk_positions[idx1] for p in positions]):
      # execute swap
      players[idx2] = player1
      players[idx1] = player2
      pass
    # __import__('pdb').set_trace()
  pass

def optimize_dk_roster_for_late_swap(roster, start_times, name_to_positions, locked_players = None):
  team_to_start_time = {}
  for time, teams in start_times.items():
    for team in teams:
      team_to_start_time[team] = time

  players = roster.players

  consider_swap(0, 5, team_to_start_time, players, name_to_positions, locked_players)
  consider_swap(1, 5, team_to_start_time, players, name_to_positions, locked_players)
  consider_swap(2, 6, team_to_start_time, players, name_to_positions, locked_players)
  consider_swap(3, 6, team_to_start_time, players, name_to_positions, locked_players)
  consider_swap(0, 7, team_to_start_time, players, name_to_positions, locked_players)
  consider_swap(1, 7, team_to_start_time, players, name_to_positions, locked_players)
  consider_swap(2, 7, team_to_start_time, players, name_to_positions, locked_players)
  consider_swap(3, 7, team_to_start_time, players, name_to_positions, locked_players)
  consider_swap(4, 7, team_to_start_time, players, name_to_positions, locked_players)
  consider_swap(5, 7, team_to_start_time, players, name_to_positions, locked_players)
  consider_swap(6, 7, team_to_start_time, players, name_to_positions, locked_players)
  consider_swap(0, 5, team_to_start_time, players, name_to_positions, locked_players)
  consider_swap(1, 5, team_to_start_time, players, name_to_positions, locked_players)
  consider_swap(2, 6, team_to_start_time, players, name_to_positions, locked_players)
  consider_swap(3, 6, team_to_start_time, players, name_to_positions, locked_players)
  consider_swap(0, 7, team_to_start_time, players, name_to_positions, locked_players)


def generate_hedge_lineups(player_to_ct, by_position, optimizer, lineup_ct=20, iter=90000):
  
  hedge_projection_adjustments = {}
  max_ct = 0
  for _, ct in player_to_ct.items():
    if ct > max_ct:
      max_ct = ct
  for player, ct in player_to_ct.items():
    represenation = ct / max_ct
    to_subtract = represenation * 10
    factor = (100 - to_subtract) / 100
    hedge_projection_adjustments[player] = factor

  by_position_adjusted = {}
  for pos, players in by_position.items():
    if not pos in by_position_adjusted:
      by_position_adjusted[pos] = []
    for player in players:
      if player.name in hedge_projection_adjustments:
        by_position_adjusted[pos].append(utils.Player(player.name, player.position, player.cost, player.team, player.value * hedge_projection_adjustments[player.name], player.opp))
      else:
        by_position_adjusted[pos].append(player)
  
  rosters = optimizer.optimize_top_n(by_position_adjusted, lineup_ct, iter=iter)
  print("HEDGE ROSTER EXPOSURES")
  utils.print_player_exposures(rosters)
  return rosters

  

def optimize_slate_with_rosters(template_path, top_mme_rosters):
  player_id_to_name, _, _, name_to_player_id, first_line, entries, to_remove, player_id_to_fd_name = parse_upload_template(template_path, [], '', 0)


  entry_name_to_ct = {}
  for entry in entries:
    entry_name = entry[2]
    if not entry_name in entry_name_to_ct:
      entry_name_to_ct[entry_name] = 1
    else:
      entry_name_to_ct[entry_name] += 1


  to_print = []
  index_strings = []
  # distribute best roster to the single entry, and the rest to the MME
  entry_name_to_take_idx = {}

  for entry in entries:
    entry_name = entry[2]
    entry_ct = entry_name_to_ct[entry_name]

    if not entry_name in entry_name_to_take_idx:
      if entry_ct > 1:
        entry_name_to_take_idx[entry_name] = 1
      else:
        entry_name_to_take_idx[entry_name] = 0

    take_idx = entry_name_to_take_idx[entry_name]


    idx = take_idx % len(top_mme_rosters)
    roster_to_append = top_mme_rosters[idx]
    assert is_roster_valid(roster_to_append)
  
    to_print.append(roster_to_append)
    index_strings.append(str(idx) + "_MME_{}".format(roster_to_append.value))
    
    entry_name_to_take_idx[entry_name] += 1

  print("MME PLAYER EXPOSURES:")
  utils.print_player_exposures(top_mme_rosters)
  construct_upload_template_file(to_print, first_line, entries, name_to_player_id, player_id_to_fd_name, index_strings)

def generate_top_n_rosters_sorted(by_position, roster_count, iter):
  optimizer = FD_NBA_Optimizer()
  rosters = optimizer.optimize_top_n(by_position, roster_count, iter=iter)

  rosters_sorted = sorted(rosters, key=lambda a:a.value, reverse=True)

  return rosters_sorted


def filter_top_mme_rosters(rosters_sorted, value_tolerance, to_take):
  assert rosters_sorted[0].value >= rosters_sorted[1].value 
  assert rosters_sorted[10].value >= rosters_sorted[11].value 
  assert rosters_sorted[20].value >= rosters_sorted[21].value 

  value_couttoff = rosters_sorted[0].value - value_tolerance
  filtered_rosters = [r for r in rosters_sorted if r.value > value_couttoff]
  player_exposures = utils.get_player_exposures(filtered_rosters)
  player_to_new_value = {}

  for player, ct in player_exposures.items():
    player_to_new_value[player] = 1 / ct

  print("input rosters: {} filtered: {}".format(len(rosters_sorted), len(filtered_rosters)))
  if len(filtered_rosters) < to_take:
    print("Not enough rosters to take: {}".format(to_take))
    __import__('pdb').set_trace()
    filtered_rosters = rosters_sorted[:to_take]
    player_exposures = utils.get_player_exposures(filtered_rosters)

  roster_and_new_value = []
  idx = 0
  for roster in filtered_rosters:

    new_roster_value = sum([player_to_new_value[pl.name] for pl in roster.players])
    roster_and_new_value.append((roster, new_roster_value, idx))
    idx += 1
      
  roster_and_new_value_sorted = sorted(roster_and_new_value, key=lambda a: a[1], reverse=True)
  # for roster_val in roster_and_new_value_sorted:
  #   print("{} - {}, {}".format(round(roster_val[1], 2), roster_val[2], roster_val[0].value))

  
  all_the_new_rosters = [r[0] for r in roster_and_new_value_sorted]
  to_return = all_the_new_rosters[:to_take]

  # utils.print_player_exposures(rosters_sorted[:to_take])
  # print("------------")
  # utils.print_player_exposures(to_return)


  return to_return

def optimize_slate_v2(slate_path, template_path, iter, value_tolerance=5.6, validate_player_set=True):
  projections = NBA_WNBA_Projections(slate_path, "NBA")
  projections.print_slate()
  if validate_player_set:
    projections.validate_player_set()

  by_position = projections.players_by_position()

  # utils.save_player_projections(by_position)

  all_rosters_sorted = generate_top_n_rosters_sorted(by_position, roster_count=5000, iter=iter)
  # all_rosters_sorted = generate_top_n_rosters_sorted(by_position, roster_count=5000, iter=120000)


  all_rosters_sorted = [a for a in all_rosters_sorted if is_roster_valid(a)]

  SE_ROSTER_TAKE = 20
  se_rosters = all_rosters_sorted[:SE_ROSTER_TAKE]
  
  mme_rosters = filter_top_mme_rosters(all_rosters_sorted, value_tolerance=value_tolerance, to_take=150)
  # mme_rosters = filter_top_mme_rosters(all_rosters_sorted, value_tolerance=9, to_take=150)
  print("MME ROSTER COUNT: {}".format(len(mme_rosters)))
  assert len(mme_rosters) == 150

  player_id_to_name, _, _, name_to_player_id, first_line, entries, to_remove, player_id_to_fd_name = parse_upload_template(template_path, [], '', 0)


  entry_name_to_ct = {}
  for entry in entries:
    entry_name = entry[2]
    if not entry_name in entry_name_to_ct:
      entry_name_to_ct[entry_name] = 1
    else:
      entry_name_to_ct[entry_name] += 1

  entry_name_to_take_idx = {}
  index_strings = []
  to_print = []

  for entry in entries:
    entry_name = entry[2]
    entry_ct = entry_name_to_ct[entry_name]

    if not entry_name in entry_name_to_take_idx:
      if entry_ct > 1:
        entry_name_to_take_idx[entry_name] = 1
      else:
        entry_name_to_take_idx[entry_name] = 0

    take_idx = entry_name_to_take_idx[entry_name]

    if entry_ct <= SE_ROSTER_TAKE:
      idx = take_idx % len(se_rosters)
      roster_to_append = se_rosters[idx]
      if not is_roster_valid(roster_to_append):
        roster_to_append = se_rosters[idx + 1]
        assert is_roster_valid(roster_to_append)

      to_print.append(roster_to_append)
      index_strings.append(str(idx) + "_SE_{}".format(roster_to_append.value))
    else:
      idx = take_idx % len(mme_rosters)
      roster_to_append = mme_rosters[idx]
      # assert is_roster_valid(roster_to_append)
      
      to_print.append(roster_to_append)
      index_strings.append(str(idx) + "_MME_{}".format(roster_to_append.value))
    
    entry_name_to_take_idx[entry_name] += 1

  utils.print_player_exposures(to_print)

  construct_upload_template_file(to_print, first_line, entries, name_to_player_id, player_id_to_fd_name, index_strings)

def sort_all_entries(entries):
  se_entries = []
  mme_entries = []

  for entry in entries:
    name = entry[2]
    if "Single Entry" in name or "Entries Max" in name or "H2H vs" in name:
      se_entries.append(entry)
    else:
      pot_size = name.split('(')[1].split(' to ')[0].strip('$K')
      mme_entries.append([entry, float(pot_size)])

    pass

  mme_sorted = sorted(mme_entries, key=lambda a: a[1], reverse=True)
  se_entries = sorted(se_entries)

  to_return = [a[0] for a in mme_sorted] + se_entries
  return to_return

def optimize_slate(slate_path, template_path, rosters_to_skip, iter, roster_filter=None, hedge_entry_name=None, hedge_entry_ct=0):
  projections = NBA_WNBA_Projections(slate_path, "NBA")
  projections.print_slate()

  #TODO:
  # projections.validate_player_set()

  by_position = projections.players_by_position()

  player_id_to_name, _, _, name_to_player_id, first_line, entries, to_remove, player_id_to_fd_name = parse_upload_template(template_path, [], '', 0)

  random.shuffle(entries)

  entries = sort_all_entries(entries)

  # __import__('pdb').set_trace()

  entry_name_to_ct = {}
  for entry in entries:
    entry_name = entry[2]
    if not entry_name in entry_name_to_ct:
      entry_name_to_ct[entry_name] = 1
    else:
      entry_name_to_ct[entry_name] += 1


  rosters = []

  optimizer = FD_NBA_Optimizer()
  # optimizer.optimize(by_position, None, iter)

  # TODO
  rosters = optimizer.optimize_top_n(by_position, 500, iter=iter)
  # rosters = optimizer.optimize_top_n(by_position, 2, iter=iter)

  rosters_sorted = sorted(rosters, key=lambda a:a.value, reverse=True)
  rosters_sorted = [r for r in rosters_sorted if is_roster_valid(r)]
  if roster_filter != None:
    rosters_sorted = [r for r in rosters_sorted if roster_filter(r)]

  SE_ROSTER_TAKE = 20

  # for roster in rosters_sorted[:SE_ROSTER_TAKE]:
  #   print(roster)


  mme_rosters = rosters_sorted
  print("MME ROSTERS RESOLVED: {}".format(len(mme_rosters)))
  valid_mme_rosters = [r for r in mme_rosters if is_roster_valid(r)]
  mme_rosters = valid_mme_rosters

  if len(mme_rosters) < len(entries):
    __import__('pdb').set_trace()

  top_mme_rosters = mme_rosters[:len(entries)]

  # hedge_rosters = generate_hedge_lineups(player_to_ct, by_position, optimizer, 100, iter=50000)
  hedge_rosters = None

  to_print = []
  index_strings = []
  # distribute best roster to the single entry, and the rest to the MME
  entry_name_to_take_idx = {}
  invalid_roster_ct = 1

  mme_entry_take_idx = 0

  for entry in entries:
    entry_name = entry[2]
    entry_ct = entry_name_to_ct[entry_name]

    IS_HEDGE_ENTRY = entry_name == hedge_entry_name \
      and entry_name in entry_name_to_take_idx \
      and entry_name_to_take_idx[entry_name] > hedge_entry_ct

    if not entry_name in entry_name_to_take_idx:
      if entry_ct > 1 and not IS_HEDGE_ENTRY:
        entry_name_to_take_idx[entry_name] = 0
      else:
        entry_name_to_take_idx[entry_name] = 0

    take_idx = entry_name_to_take_idx[entry_name]

    if IS_HEDGE_ENTRY:
      idx = (take_idx - hedge_entry_ct) % len(rosters_sorted)
      roster_to_append = hedge_rosters[idx]
      assert is_roster_valid(roster_to_append)

      to_print.append(roster_to_append)
      index_strings.append(str(idx) + "_HEDGE_{}".format(roster_to_append.value))

      entry_name_to_take_idx[entry_name] += 1
    elif entry_ct <= SE_ROSTER_TAKE:
      idx = take_idx % len(rosters_sorted)
      roster_to_append = rosters_sorted[idx]
      if not is_roster_valid(roster_to_append):
        roster_to_append = rosters_sorted[idx + 1]
        assert is_roster_valid(roster_to_append)

      to_print.append(roster_to_append)
      index_strings.append(str(idx) + "_SE_{}".format(roster_to_append.value))

      entry_name_to_take_idx[entry_name] += 1
    else:
      idx = mme_entry_take_idx % len(top_mme_rosters)
      # idx = take_idx % len(top_mme_rosters)
      mme_entry_take_idx += 1
      roster_to_append = top_mme_rosters[idx]
      assert is_roster_valid(roster_to_append)
      
      to_print.append(roster_to_append)
      index_strings.append(str(idx) + "_MME_{}".format(roster_to_append.value))
    
      entry_name_to_take_idx[entry_name] += 1

  print("PLAYER EXPOSURES:")
  player_to_ct = utils.print_player_exposures(to_print)
  construct_upload_template_file(to_print, first_line, entries, name_to_player_id, player_id_to_fd_name, index_strings)
  utils.print_roster_time_distribution(to_print, start_times)

  for roster in mme_rosters[:10]:
    print(roster)

  return mme_rosters


def get_locked_players_key(players):
  to_return = ""
  for player in players:
    if player != None:
      to_return += player.name

    to_return += "|"

  return to_return

def reoptimize_slate_fd(slate_path, current_rosters_path, current_time, start_times, allow_duplicate_rosters=False):
  player_id_to_name, _, _, name_to_player_id, first_line, entries, to_remove, player_id_to_fd_name = parse_upload_template(current_rosters_path, [], '', 0)

  # entries = sort_all_entries(entries)

  locked_teams = []
  for time, teams in start_times.items():
    if time < current_time:
      locked_teams += teams
  
  projections = NBA_WNBA_Projections(slate_path, "NBA")
  projections.print_slate()

  by_position = projections.players_by_position(exclude_zero_value=False)
  name_to_players = get_name_to_player_objects(by_position)

  optimizer = FD_NBA_Optimizer()

  by_position = filter_out_locked_teams(by_position, locked_teams)
  existing_rosters = parse_existing_rosters(current_rosters_path)
  existing_rosters = [a for a in existing_rosters if a[0] != '']
  seen_roster_keys = []
  seen_roster_string_to_optimized_roster = {}

  locked_players_to_top_n_optimized = {}

  roster_idx = 0
  all_results = []
  annotations = []

  for existing_roster in existing_rosters:
    print("ROSTER: {}".format(roster_idx))
    roster_idx += 1
    players = existing_roster[3:12]
    if len(players) == 0:
      print("Did you forget to set this roster??")
      __import__('pdb').set_trace()
      continue

    if players[0] == '':  
      continue

    roster_string = ",".join(players)

    if roster_string in seen_roster_string_to_optimized_roster:
      result = seen_roster_string_to_optimized_roster[roster_string]

      all_results.append(result)
      annotations.append(' - ')
      continue

    players3 = []
    for p in players:
      if ':' in p:
        p = p.split(':')[0]
      if not p in player_id_to_name:
        __import__('pdb').set_trace()

      players3.append(player_id_to_name[p])

    players4 = [name_to_players[p][0] for p in players3]
    players5 = []
    initial_roster = []
    lock_ct = 0
    for p in players4:
      if p.team in locked_teams:
        players5.append(p)
        lock_ct += 1
      else:
        players5.append(None)
      initial_roster.append(p.name)

    is_se_roster_or_h2h = "Single Entry" in existing_roster[2] or "Entries Max" in existing_roster[2] or "H2H vs" in existing_roster[2]

    if lock_ct != 9:

      locked_players_key = get_locked_players_key(players5)


      # todo: this will be optimize_top_n
      # iterate over the n results and take the first one not seen already (within range)
      # result = optimizer.optimize(by_position, players5, int(1750), is_roster_valid)
      if not locked_players_key in locked_players_to_top_n_optimized:
        candidate_rosters = optimizer.optimize_top_n(by_position, 120, int(4050), players5, is_roster_valid)
        # TODO:
        # candidate_rosters = optimizer.optimize_top_n(by_position, 120, int(8050), players5, is_roster_valid)
        locked_players_to_top_n_optimized[locked_players_key] = candidate_rosters
      else:
        candidate_rosters = locked_players_to_top_n_optimized[locked_players_key]

      result = candidate_rosters[0] 
      
      top_val = result.value
      candidate_rosters_filtered = [a for a in candidate_rosters if a.value >= top_val - 10]
      if not is_se_roster_or_h2h:
        counter = 0
        for roster in candidate_rosters_filtered:
          names1 = [p.name for p in roster.players]
          candidate_roster_key = ",".join(sorted(names1))
          if not candidate_roster_key in seen_roster_keys:
            result = roster
            print("TAKING CANDIDATE ROSTER: {}".format(counter))
            break

          counter += 1
          # else:
          #   __import__('pdb').set_trace()
          
    else:
      result = utils.Roster(players4)

    try:
      names1 = [p.name for p in result.players]
      optimized_roster_key = ",".join(sorted(names1))

      if is_se_roster_or_h2h:
        print("IS SE ROSTER or H2H!")

      has_dead_player = any([a.value < 12.0 and a.team not in locked_teams for a in players4])

      if optimized_roster_key in seen_roster_keys \
          and not allow_duplicate_rosters \
          and not is_se_roster_or_h2h \
          and not has_dead_player:
        # don't change the result!
        print("initial roster unchanged! {}")
        original_roster_result = utils.Roster(players4)
        all_results.append(original_roster_result)
        seen_roster_string_to_optimized_roster[roster_string] = original_roster_result

        annotations.append("UNCHANGED")
      else:
        seen_roster_keys.append(optimized_roster_key)
        initial_roster_key = ",".join(sorted(initial_roster))
        is_improvement = True
        if optimized_roster_key != initial_roster_key:
          print("LOCKED PLAYERS: {}".format(players5))


          print("INITIAL ROSTER:\n{}".format(initial_roster))

          initial_value = round(sum([name_to_players[a][0].value for a in initial_roster]), 2)
          new_value = result.value
          diff = new_value - initial_value
          if diff != 0:
            print("OLD VAL {} NEW VAL: {} = {}".format(initial_value, new_value, diff))

          # if diff < 0:
          #   __import__('pdb').set_trace()

          if diff >= 0:
            print(result)
            # if abs(diff) > 20:
            #   __import__('pdb').set_trace()
          else:
            is_improvement = False
        # else:

        #   print("NO CHANGE {} - {}".format(result, initial_roster))
        if is_improvement:
          initial_value = round(sum([name_to_players[a][0].value for a in initial_roster]), 2)
          new_value = result.value
          diff = new_value - initial_value
          annotations.append("reopt - {} - {} diff: {}".format(lock_ct, new_value, diff))
          all_results.append(result)
          seen_roster_string_to_optimized_roster[roster_string] = result
        else:
          print("NO IMPROVEMENT SKIPPING")
          original_roster_result = utils.Roster(players4)
          all_results.append(original_roster_result)
          seen_roster_string_to_optimized_roster[roster_string] = original_roster_result
          annotations.append("UNCHANGED")
    except Exception as exception:
      print(exception)
      __import__('pdb').set_trace()

  total_roster_val = sum([a.value for a in all_results])
  utils.print_player_exposures(all_results, locked_teams)
  variation = utils.print_roster_variation(all_results)
  print(variation)
  
  # variation = utils.print_roster_variation(existing_rosters)
  # print(variation)
  print("TOTAL ROSTER VAL: {}".format(total_roster_val))

  construct_upload_template_file(all_results, first_line, entries, name_to_player_id, player_id_to_fd_name, annotations)

  utils.print_roster_time_distribution(all_results, start_times)


def single_game_optimizer(slate_path, template_path):
  player_id_to_name, _, _, name_to_player_id, first_line, entries, to_remove, player_id_to_fd_name = parse_upload_template(template_path, [], '', 4)

  projections = NBA_WNBA_Projections(slate_path, "NBA")

  projections.print_slate()

  by_position = projections.players_by_position()

  all_results = utils.single_game_optimizer_many(by_position, 10)

  roster_distribution = [(0,6), (1,3), (0, 1), (2,1), (3,1), (4,1), (0,1)]

  all_rosters = []
  annotations = []
  for (idx, ct) in roster_distribution:
    for i in range(ct):
      roster = all_results[idx]
      all_rosters.append(utils.Roster(roster[0]))
      annotations.append("{}_{}".format(idx, roster[1]))

  # all_results_rosters = [utils.Roster(result[0]) for result in all_results]

  construct_upload_template_file(all_rosters, first_line, entries, name_to_player_id, player_id_to_fd_name, annotations)

def reoptimize_slate_dk(slate_path, entries_path, current_time, start_times, allow_duplicate_rosters=False):
  file = open(entries_path)
  file_reader = csv.reader(file, delimiter=',', quotechar='"')
  entries = []
  first_line = True
  for cells in file_reader:
    if first_line:
      first_line = False
      continue

    if cells[0] == '':
      break
    first_ten_cells = cells[:12]
    entries.append(first_ten_cells)

  projections = NBA_Projections_dk(slate_path, "NBA")
  projections.print_slate()
  locked_teams = []
  for time, teams in start_times.items():
    if time < current_time:
      locked_teams += teams

  by_position_unfiltered = projections.players_by_position()

  name_to_positions = {}
  for pos, players in by_position_unfiltered.items():
    for player in players:
      name = player.name
      if not name in name_to_positions:
        name_to_positions[name] = []
      name_to_positions[name].append(pos)

  by_position = filter_out_locked_teams(by_position_unfiltered, locked_teams)

  name_to_player = {}
  for player in by_position_unfiltered['UTIL']:
    name_to_player[player.name] = player

  optimized_roster_keys = []
  
  to_print = []
  all_locked_players = []
  optimizer = DK_NBA_Optimizer()
  for entry in entries:
    players = entry[4:12]

    locked_players = []
    original_roster_names = []
    for player in players:
      name_stripped = utils.normalize_name(player.split('(')[0].strip())
      original_roster_names.append(name_stripped)
      if "(LOCKED)" in player:
        locked_players.append(name_to_player[name_stripped])
      else:
        locked_players.append('')

    all_locked_players.append(locked_players)
    # optimized = optimizer.optimize(by_position, locked_players, 1900)
    optimize_top_n = optimizer.optimize_top_n(by_position, 50, locked_players, 4200)
    # TODO:
    # optimize_top_n = optimizer.optimize_top_n(by_position, 50, locked_players, 8200)
    matched_roster = False
    for i in range(len(optimize_top_n)):
      optimized = optimize_top_n[i]
      if isinstance(optimized, list):
        names1 = [p.name for p in  optimized[0].players]
      else:
        names1 = [p.name for p in optimized.players]
      roster1_key = ",".join(sorted(names1))
      if not roster1_key in optimized_roster_keys or allow_duplicate_rosters:
        
        initial_value = round(sum([name_to_player[a].value for a in original_roster_names]), 2)

        new_val = round(optimized.value, 2)
        diff_val = new_val - initial_value
        if diff_val != 0:
          print("OLD VAL {} NEW VAL: {} = {}".format(initial_value, new_val, diff_val))
        # if diff_val < -5:
          # __import__('pdb').set_trace()
        if diff_val > 0:
          print("TAKING ROSTER INDEX: {} - {}\n{}\ninitial: {}".format(i, roster1_key, optimized, players))

          to_print.append(optimized)
          optimized_roster_keys.append(roster1_key)
          matched_roster = True
        else:
          print("NO IMPROVEMENT SKIPPING")
          original_roster = utils.Roster([name_to_player[a] for a in original_roster_names])
          to_print.append(original_roster)
          matched_roster = True
          pass
        

        break

    if not matched_roster:
      to_print.append(optimize_top_n[0])

    # to_print.append(optimized)

  roster_idx = 0
  for roster in to_print:
    # this needs to work for reopto by respecting locked players
    # __import__('pdb').set_trace()
    locked_players = all_locked_players[roster_idx]
    optimize_dk_roster_for_late_swap(roster, start_times, name_to_positions, locked_players)
    roster_idx += 1

  # utils.print_player_exposures(to_print)
  utils.construct_dk_output_template(to_print, projections.name_to_player_id, entries_path, should_sort_by_entry_fee=False)
  print(utils.print_roster_variation(to_print))
  utils.print_player_exposures(to_print)
  utils.print_roster_time_distribution(to_print, start_times)

def optimize_slate_dk(slate_path, iter, entries_path, start_times):
  # 
  projections = NBA_Projections_dk(slate_path, "NBA")
  projections.print_slate()

  by_position = projections.players_by_position()

  optimizer = DK_NBA_Optimizer()

  name_to_positions = {}
  for pos, players in by_position.items():
    for player in players:
      name = player.name
      if not name in name_to_positions:
        name_to_positions[name] = []
      name_to_positions[name].append(pos)

  # TODO: THIS IS A DANGEROUS MAGIC NUMBER THAT RESULTS IN DEEAD ENTRIES!
  rosters = optimizer.optimize_top_n(by_position, 151, locked_players=None, iter=iter)

  rosters = [r for r in rosters if is_roster_valid_dk(r)]
  # for roster in rosters:
  #   optimize_dk_roster_for_late_swap(roster, start_times)
  #   print(roster)
  
  # utils.construct_dk_output_template(rosters, projections.name_to_player_id, entries_path, "ls_unopt")

  for roster in rosters:
    optimize_dk_roster_for_late_swap(roster, start_times, name_to_positions)
  
  for roster in rosters[:10]:
    print(roster)

  roster_count = utils.construct_dk_output_template(rosters, projections.name_to_player_id, entries_path, "ls_opt")

  utils.print_player_exposures(rosters[:roster_count])
  utils.print_roster_time_distribution(rosters, start_times)
  


##########################################################################################################
##########################################################################################################
##########################################################################################################

def showdown_roster_cost(roster, player_data):
  cpt = roster[0]
  utils = roster[1:]
  return player_data[cpt][2] * 1.5 + sum([player_data[a][2] for a in utils])


def generate_showdown_lineups(showdown_slate_path):
  
  player_data = utils.get_dk_slate_players(utils.DOWNLOAD_FOLDER + showdown_slate_path)
  projections = NBA_Projections_dk(utils.DOWNLOAD_FOLDER + showdown_slate_path, "NBA")
  projection_names = projections.players_by_position()['UTIL']
  name_to_projections = {}
  for projection in projection_names:
    name_to_projections[projection.name] = projection.value

  names = player_data.keys()
  candidates = []
  for name in names:
    capt = name

    names_filtered = [n for n in names if n != capt]
    other_payers = itertools.combinations(names_filtered, 5)
    for sub_set in other_payers:
      candidates.append([capt] + list(sub_set))
  
  current_set = []
  seen_roster_keys = set()
  idx = 0
  for candidate in candidates:
    idx += 1 
    if idx % 1000000 == 0:
      print("{} {}".format(idx, len(current_set)))

    cost = showdown_roster_cost(candidate, player_data)
    if cost > 50000:
      continue
    if cost < 49000:
      continue

    roster_key = "{}|{}".format(candidate[0], sorted([candidate[1], candidate[2], candidate[3], candidate[4], candidate[5]]))
    if roster_key in seen_roster_keys:
      continue

    seen_roster_keys.add(roster_key)

    projected = name_to_projections[candidate[0]] * 1.5 + name_to_projections[candidate[1]] + \
       + name_to_projections[candidate[2]]  + name_to_projections[candidate[3]] + \
         + name_to_projections[candidate[4]]  + name_to_projections[candidate[5]]

    projected = round(projected, 2)
    current_set.append([candidate, cost, projected])

  current_set_sorted = sorted(current_set, key=lambda a: a[2], reverse=True)
  to_upload = current_set_sorted[:60]
  # utils.construct_dk_showdown_output_template(to_upload, projections.name_to_player_id, utils.DOWNLOAD_FOLDER + upload_template_path)

  timestamp = str(datetime.datetime.now())
  date = timestamp.split(' ')[0]
  site = "dk"
  slate = "78980"
  id = str(uuid.uuid4()).split('-')[0]

  rosters_string = json.dumps(to_upload)
  hash_object = hashlib.md5(bytes(rosters_string, 'utf-8'))

  utils.write_to_db('MLE_Lineups', {
    'date-site-slateid-id': "{}_{}_{}_{}".format(date, site, slate, id),
    'date': date,
    'slate': slate,
    'timestamp': timestamp,
    'rosters': rosters_string,
    'name_to_player_id': json.dumps(projections.name_to_player_id),
    'hash': hash_object.hexdigest()
  })
  # write these projections to s3


def optimize_for_single_game_dk(slate_path, template_path, max_cpt_exposure):
  projections = NBA_Projections_dk(slate_path, "NBA")
  projections.print_slate()

  by_position = projections.players_by_position()
  player_pool_all = by_position['UTIL']
  player_pool = []
  seen_names = []
  for player in player_pool_all:
    # if not player.team in teams:
    #   continue
    if player.name in seen_names:
      continue
    seen_names.append(player.name)
    player_pool.append(player)


  player_pool = [a for a in player_pool if a.value > 4]

  for p in player_pool:
    p.value = round(p.value * 2) / 2

  candidates = []

  print("size:")
  print(len(player_pool))

  for name in player_pool:
    capt = name

    names_filtered = [n for n in player_pool if n != capt]
    other_payers = itertools.combinations(names_filtered, 5)
    for sub_set in other_payers:
      candidate = [capt] + list(sub_set)

      total_cost = candidate[0].cost * 1.5 + candidate[1].cost + candidate[2].cost + candidate[3].cost + candidate[4].cost + candidate[5].cost
      if total_cost > 50000:
        continue
      candidates.append(candidate)
  
  sorted_by_value = sorted(candidates, key=lambda a: utils.candidate_value(a), reverse=True)
  filtered_lineups = []
  capt_to_ct = {}
  for roster in sorted_by_value:
    cpt = roster[0].name
    if not cpt in capt_to_ct:
      capt_to_ct[cpt] = 1
    else:
      capt_to_ct[cpt] += 1

    if capt_to_ct[cpt] > max_cpt_exposure:
      continue

    filtered_lineups.append(roster)
    if len(filtered_lineups) == 150:
      break


  for roster in filtered_lineups[:15]:
    print(roster)

  # __import__('pdb').set_trace()

  roster_ct = utils.construct_dk_output_single_game(filtered_lineups, projections.name_to_player_id, template_path, "ls_opt", "NBA")
  # return to_print

if __name__ == "__main__":
  # showdown_slate_path = "DK_78980.csv"
  # generate_showdown_lineups(showdown_slate_path)
  # assert False

  (start_times, _, _, _) = utils.load_start_times_and_slate_path('start_times.txt')

  # express_slate_id = "84682"
  # fd_slate_path = utils.most_recently_download_filepath('FanDuel-NBA-', express_slate_id, '-players-list', '.csv')
  # template_path = utils.most_recently_download_filepath('FanDuel-NBA-', express_slate_id, '-entries-upload-template', '.csv')
  # # all_rosters = optimize_slate(fd_slate_path, template_path, 0, iter=80000)
  
  # reoptimize_slate_fd(fd_slate_path, template_path, current_time, start_times, allow_duplicate_rosters=False)
  # # assert False


  #(start_times, slate_path, template_path, dk_slate_path)
  slate_id = utils.TODAYS_SLATE_ID_NBA
  
  now = datetime.datetime.now()
  current_time = (now.hour - 12) + (now.minute / 60)
  current_time = round(current_time, 2)
  print("CURRENT TIME: {}".format(current_time))
  
  fd_slate_path = utils.most_recently_download_filepath('FanDuel-NBA-', slate_id, '-players-list', '.csv')
  template_path = utils.most_recently_download_filepath('FanDuel-NBA-', slate_id, '-entries-upload-template', '.csv')
  dk_slate_path = utils.most_recently_download_filepath('DKSalaries', '(', ')', '.csv')
  dk_entries_path = utils.most_recently_download_filepath('DKEntries', '(', ')', '.csv')

  # # 25 seems optimal for 150 mme
  # optimize_for_single_game_dk(dk_slate_path, dk_entries_path, 10)

  # assert False
  
  # TODO - do we still want SE rosters to be unique from MME rosters?
  # TODO: I'm explicitly mapping team to opponent for DK roster validation :facepalm:
  
  if current_time < min(start_times.keys()):
    iter = 70000
    all_rosters = optimize_slate(fd_slate_path, template_path, 0, iter)
    iter = int(iter * 0.85)
    all_rosters = optimize_slate_dk(dk_slate_path, iter, dk_entries_path, start_times)
  else:
    # current_time = 9.6
    reoptimize_slate_fd(fd_slate_path, template_path, current_time, start_times, allow_duplicate_rosters=False)
    reoptimize_slate_dk(dk_slate_path, dk_entries_path, current_time, start_times, allow_duplicate_rosters=False)

  # assert False

  

  assert False

  

# properly sort players for dk lineups - FOR REOPTIMIZATION
# we need much better logging around our scraper - who is in, out etc

