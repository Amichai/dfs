import math
from projection_providers.NFL_Projections import NFL_Projections, NFL_Projections_dk
from Optimizer import NFL_Optimizer
import random
import datetime
import utils
import statistics
from ScrapeProcessManager import run
from Optimizer import FD_WNBA_Optimizer
import csv

position_list = ["QB", "RB", "RB", "WR", "WR", "WR", "TE", "FLEX", "D"]

def consider_swap(idx1, idx2, team_to_start_time, players, name_to_positions):
  player1 = players[idx1]
  player2 = players[idx2]
  # player 1 is specific
  # player 1 is general
  # we want specific to be before the general
  if team_to_start_time[player1.team] > team_to_start_time[player2.team]:
    # make sure the swap is valid!
    positions = name_to_positions[player2.name]
    if any([p == position_list[idx1] for p in positions]):
      # execute swap
      players[idx2] = player1
      players[idx1] = player2
      pass
    # __import__('pdb').set_trace()
  pass

def optimize_roster_for_late_swap(roster, start_times, name_to_positions):
  team_to_start_time = {}
  for time, teams in start_times.items():
    for team in teams:
      team_to_start_time[team] = time

  players = roster.players

  consider_swap(0, 7, team_to_start_time, players, name_to_positions)
  consider_swap(1, 7, team_to_start_time, players, name_to_positions)
  consider_swap(2, 7, team_to_start_time, players, name_to_positions)
  consider_swap(3, 7, team_to_start_time, players, name_to_positions)
  consider_swap(4, 7, team_to_start_time, players, name_to_positions)
  consider_swap(5, 7, team_to_start_time, players, name_to_positions)
  consider_swap(6, 7, team_to_start_time, players, name_to_positions)


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

def get_name_to_player_objects(by_position):
  name_to_player_objects = {}
  for pos, players in by_position.items():
    for player in players:
      if not player.name in name_to_player_objects:
        name_to_player_objects[player.name] = []
      
      name_to_player_objects[player.name].append(player)

  return name_to_player_objects

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
        contest_name = parts[2].strip('"').strip()

        if entry_id != '' or contest_id != '' or contest_name != '':
            if entry_filter == None or entry_filter in contest_name:
                entries.append((entry_id, contest_id, contest_name))
        
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


        pos = parts[15]
        if pos == "D":
          # __import__('pdb').set_trace()
          name = team

        name_to_player_id[name] = player_id
        name_to_team[name] = team
        name_to_salary[name] = salary

        player_id_to_name[player_id] = name
        
        player_id_to_fd_name[player_id] = name_and_id
        
        if name in exclude:
            players_to_remove.append(name)
            continue

          
        if injury_status == 'O' or injury_status == "IL" or injury_status == "NA":
            print("{} is OUT".format(name))
            players_to_remove.append(name)
            continue

    if len(player_id_to_name) == 0:
        __import__('pdb').set_trace()

    return player_id_to_name, name_to_team, name_to_salary, name_to_player_id, first_line, entries, players_to_remove, player_id_to_fd_name


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

def print_player_exposures(rosters_sorted):
  player_to_ct = {}
  for roster in rosters_sorted:
    for player in roster.players:
      if not player.name in player_to_ct:
        player_to_ct[player.name] = 1
      else:
        player_to_ct[player.name] += 1

  player_to_ct_sorted = sorted(player_to_ct.items(), key=lambda a: a[1], reverse=True)
  print(player_to_ct_sorted)

def print_optimizer_projections(by_position, name_to_id):
  all_rows = []
  seen_names = []
  for pos, players in by_position.items():
    if pos == "FLEX":
      continue
    if pos == "D":
      pos = "DST"
    for player in players:
      name = player.name
      if name in seen_names:
        continue

      seen_names.append(name)
      proj = player.value
      player_id = name_to_id[name]
      all_rows.append([player_id, name, pos, player.team, proj, proj, 0, 100])

  timestamp = str(datetime.datetime.now())
  date = timestamp.replace('.', '_')
  date = date.replace(":", "_")
  with open("/Users/amichailevy/Downloads/projections_{}.csv".format(date), "x") as output:
    output.write("Id,Name,Position,Team,ProjPts,ProjOwn,MinExp,MaxExp\n")
    for row in all_rows:
      output.write(",".join([str(r) for r in row]) + '\n')
    

def is_roster_valid_fd(roster):
  team_ct = {}
  for player in roster.players:
    # if player.position == "D":
    #   continue
    team = player.team
    if not team in team_ct:
      team_ct[team] = 1
    else:
      team_ct[team] += 1
    
  max_ct = max(list(team_ct.values()))
  # __import__('pdb').set_trace()
  return max_ct < 5

def is_roster_stacked(roster):
  qb_team = roster.players[0].team
  def_opp = roster.players[8].opp

  rb_and_wr_teams = []
  off_teams = []
  for player in roster.players:
    if player.position == "D":
      continue

    if player.position == "WR" or player.position == "RB":
      rb_and_wr_teams.append(player.team)

    if not player.team in off_teams:
      off_teams.append(player.team)
  
  qb_has_stack = qb_team in rb_and_wr_teams
  defense_not_opposed = def_opp not in off_teams
  
  # qb needs 1 wr or rb on the same team
  # defense opp can't contain any off teams
  return qb_has_stack and defense_not_opposed

def optimize_slate(slate_path, template_path, iter):
  projections = NFL_Projections(slate_path, "NFL")
  projections.print_slate()

  by_position = projections.players_by_position()

  player_id_to_name, _, _, name_to_player_id, first_line, entries, to_remove, player_id_to_fd_name = parse_upload_template(template_path, [], '', 0)

  entry_name_to_ct = {}
  for entry in entries:
    entry_name = entry[2]
    if not entry_name in entry_name_to_ct:
      entry_name_to_ct[entry_name] = 1
    else:
      entry_name_to_ct[entry_name] += 1


  rosters = []

  optimizer = NFL_Optimizer()
  name_to_positions = {}
  for pos, players in by_position.items():
    for player in players:
      name = player.name
      if not name in name_to_positions:
        name_to_positions[name] = []
      name_to_positions[name].append(pos)

  rosters = optimizer.optimize_top_n(by_position, 1000, iter)
  before_ct = len(rosters)
  rosters = [r for r in rosters if is_roster_stacked(r)]

  print("Before: {} after fiter: {}".format(before_ct, len(rosters)))
  before_ct = len(rosters)
  rosters = [r for r in rosters if is_roster_valid_fd(r)]
  print("Before validity check: {} after validity check: {}".format(before_ct, len(rosters)))

  rosters_sorted = sorted(rosters, key=lambda a:a.value, reverse=True)
  for roster in rosters_sorted:
    optimize_roster_for_late_swap(roster, start_times, name_to_positions)
    # print(roster)

  print_player_exposures(rosters_sorted)

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

    # entry_ct = entry_name_to_ct[entry_name]
    # if entry_ct == 1:
    #   to_print.append(rosters_sorted[0])
    # else:
    idx = take_idx % len(rosters_sorted)
    roster_to_append = rosters_sorted[idx]
    to_print.append(roster_to_append)
    index_strings.append(str(idx) + "_MME_{}".format(roster_to_append.value))
    entry_name_to_take_idx[entry_name] += 1

  construct_upload_template_file(to_print, first_line, entries, name_to_player_id, player_id_to_fd_name, index_strings)


def reoptimize_slate(slate_path, current_rosters_path, current_time, start_times, allow_duplicate_rosters=False):
  player_id_to_name, _, _, name_to_player_id, first_line, entries, to_remove, player_id_to_fd_name = parse_upload_template(current_rosters_path, [], '', 0)

  locked_teams = []
  for time, teams in start_times.items():
    if time < current_time:
      locked_teams += teams
  
  projections = NFL_Projections(slate_path, "NFL")
  projections.print_slate()

  by_position = projections.players_by_position(exclude_zero_value=False)
  name_to_players = get_name_to_player_objects(by_position)
  optimizer = NFL_Optimizer()

  by_position = filter_out_locked_teams(by_position, locked_teams)
  existing_rosters = parse_existing_rosters(current_rosters_path)
  seen_roster_strings = []
  seen_roster_string_to_optimized_roster = {}

  roster_idx = 0
  all_results = []
  for existing_roster in existing_rosters:
    print("ROSTER: {}".format(roster_idx))
    roster_idx += 1
    players = existing_roster[3:12]
    if players[0] == '':
      continue

    players2 = [p.split(':')[0] for p in players]
    roster_string = ",".join(players2)

    if roster_string in seen_roster_strings:
      result = seen_roster_string_to_optimized_roster[roster_string]
      all_results.append(result)
      continue

    seen_roster_strings.append(roster_string)
    # __import__('pdb').set_trace()
    players3 = []
    for p in players:
      if not p in player_id_to_name:
        __import__('pdb').set_trace()

      players3.append(player_id_to_name[p])
    players4 = [name_to_players[p][0] for p in players3]
    players5 = []
    initial_roster = []
    for p in players4:
      if p.team in locked_teams:
        players5.append(p)
      else:
        players5.append(None)
      initial_roster.append(p.name)

    result = optimizer.optimize(by_position, players5, 2000)
    seen_roster_string_to_optimized_roster[roster_string] = result

    ##TEST CODE

    names1 = [p.name for p in result.players]
    roster1_key = ",".join(sorted(names1))

    is_se_roster_or_h2h = "Single Entry" in existing_roster[2] or "Entries Max" in existing_roster[2] or "H2H vs" in existing_roster[2]
    if is_se_roster_or_h2h:
      print("IS SE ROSTER or H2H!")

    has_dead_player = any([a.value < 2.0 and a.team not in locked_teams for a in result.players])

    if roster1_key in seen_roster_strings \
        and not allow_duplicate_rosters \
        and not is_se_roster_or_h2h \
        and not has_dead_player:
      # don't change the result!
      print("initial roster unchanged! {}")
      all_results.append(utils.Roster(players4))
    else:
      seen_roster_strings.append(roster1_key)

      roster2_key = ",".join(sorted(initial_roster))
      if roster1_key != roster2_key:
        print("LOCKED PLAYERS: {}".format(players5))


        print("INITIAL ROSTER:\n{}".format(initial_roster))
        print(result)

      all_results.append(result)

    ##END TEST CODE

    # print(result)
  
    # all_results.append(result)

  utils.print_player_exposures(all_results)

  construct_upload_template_file(all_results, first_line, entries, name_to_player_id, player_id_to_fd_name)


def reoptimize_slate_dk(slate_path, entries_path, current_time, start_times):
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
    first_ten_cells = cells[:13]
    entries.append(first_ten_cells)

  projections = NFL_Projections_dk(slate_path, "NFL")
  projections.print_slate()
  locked_teams = []
  for time, teams in start_times.items():
    if time < current_time:
      locked_teams += teams

  by_position_unfiltered = projections.players_by_position(exclude_zero_value=False)
  by_position = filter_out_locked_teams(by_position_unfiltered, locked_teams)

  name_to_player = {}
  seen_player_names = []

  for pos, players in by_position_unfiltered.items():
    for player in players:
      name = player.name
      if not name in seen_player_names:
        name_to_player[name] = player
        seen_player_names.append(name)

  optimized_roster_keys = []
  
  to_print = []
  optimizer = NFL_Optimizer(50000)

  for entry in entries:
    players = entry[4:13]

    locked_players = []
    for player in players:
      if "(LOCKED)" in player:
        name_stripped = utils.normalize_name(player.split('(')[0].strip())

        locked_players.append(name_to_player[name_stripped])
      else:
        locked_players.append('')

    optimized = optimizer.optimize(by_position, locked_players, 1800)
    if isinstance(optimized, list):
      names1 = [p.name for p in  optimized[0].players]
    else:
      names1 = [p.name for p in optimized.players]
    roster1_key = ",".join(sorted(names1))
    if not roster1_key in optimized_roster_keys:
      to_print.append(optimized)
      optimized_roster_keys.append(roster1_key)
    else:
      print("SKIPPING COLLIDED ROSTER!")
      roster_names = [utils.normalize_name(a.split('(')[0].strip()) for a in players]
      roster_players = [name_to_player[a] for a in roster_names]
      to_print.append(utils.Roster(roster_players))

    # to_print.append(optimized)

  # utils.print_player_exposures(to_print)
  # print(utils.print_roster_variation(to_print))
  utils.construct_dk_output_template(to_print, projections.name_to_player_id, entries_path, sport="NFL")

  utils.print_roster_variation(to_print)
  # utils.print_player_exposures(to_print)

def optimize_slate_dk(slate_path, iter, entries_path, start_times):
  projections = NFL_Projections_dk(slate_path, "NFL", player_adjustments={})
  projections.print_slate()

  by_position = projections.players_by_position()

  optimizer = NFL_Optimizer(50000)

  name_to_positions = {}
  for pos, players in by_position.items():
    for player in players:
      name = player.name
      if not name in name_to_positions:
        name_to_positions[name] = []
      name_to_positions[name].append(pos)

  # TODO: THIS IS A DANGEROUS MAGIC NUMBER THAT RESULTS IN DEEAD ENTRIES!
  rosters = optimizer.optimize_top_n(by_position, 1000, iter)
  before_ct = len(rosters)
  rosters = [r for r in rosters if is_roster_stacked(r)]

  print("Before: {} after fiter: {}".format(before_ct, len(rosters)))

  # rosters = [r for r in rosters if is_roster_valid_dk(r)]
  # for roster in rosters:
  #   optimize_dk_roster_for_late_swap(roster, start_times)
  #   print(roster)
  
  # utils.construct_dk_output_template(rosters, projections.name_to_player_id, entries_path, "ls_unopt")

  for roster in rosters:
    optimize_roster_for_late_swap(roster, start_times, name_to_positions)
    # print(roster)

  utils.construct_dk_output_template(rosters, projections.name_to_player_id, entries_path, "ls_opt", "NFL")
  



if __name__ == "__main__":
  # download_folder = "/Users/amichailevy/Downloads/"
  # slate_path = "FanDuel-NFL-2022 ET-10 ET-23 ET-81947-players-list.csv"
  # template_path = "FanDuel-NFL-2022-10-23-81947-entries-upload-template.csv"

  # optimize_slate(slate_path, template_path)

  # # reoptimize_slate(slate_path, "FanDuel-NFL-2022-10-23-81947-entries-upload-template (2).csv", 3.1)


  # assert False
  
    slate_id = utils.TODAYS_SLATE_ID_NFL
    (start_times, _, _, _) = utils.load_start_times_and_slate_path('start_times_NFL.txt')


    fd_slate_path = utils.most_recently_download_filepath('FanDuel-NFL-', slate_id, '-players-list', '.csv')
    template_path = utils.most_recently_download_filepath('FanDuel-NFL-', slate_id, '-entries-upload-template', '.csv')
    dk_slate_path = utils.most_recently_download_filepath('DKSalaries', '(', ')', '.csv')
    dk_entries_path = utils.most_recently_download_filepath('DKEntries', '(', ')', '.csv')
    
    # ##FIRST PASS
    # all_rosters = optimize_slate(fd_slate_path, template_path, iter=35000)
    # all_rosters = optimize_slate_dk(dk_slate_path, 35000, dk_entries_path, start_times)

    current_time = 1.2
    reoptimize_slate(fd_slate_path, template_path, current_time, start_times)
    reoptimize_slate_dk(dk_slate_path, dk_entries_path, current_time, start_times)


# stacking -
# QB must be paired with at least one WR/RB
# no offense against my own defense