import math
from projection_providers.NBA_WNBA_Projections import NBA_WNBA_Projections, NBA_Projections_dk
import random
import datetime
import utils
import statistics
from ScrapeProcessManager import run
from Optimizer import FD_NBA_Optimizer, DK_NBA_Optimizer
import csv

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
            print("{} is OUT".format(name))
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

def optimize_slate_dk(slate_path, iter):
  projections = NBA_Projections_dk(download_folder + slate_path, "NBA")
  projections.print_slate()

  by_position = projections.players_by_position()
  optimizer = DK_NBA_Optimizer()

  # TODO
  # cj = [p for p in by_position['G'] if p.name == "Cory Joseph"][0]


  roster = optimizer.optimize(by_position, None, iter)
  print(roster)
  __import__('pdb').set_trace()
  pass


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
  player_id_to_name, _, _, name_to_player_id, first_line, entries, to_remove, player_id_to_fd_name = parse_upload_template(download_folder + template_path, [], '', 0)


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
  invalid_roster_ct = 1

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


def optimize_slate(slate_path, template_path, rosters_to_skip, iter, roster_filter=None, hedge_entry_name=None, hedge_entry_ct=0):
  projections = NBA_WNBA_Projections(download_folder + slate_path, "NBA")
  projections.print_slate()
  projections.validate_player_set()


  by_position = projections.players_by_position()


  # # assert False
  player_id_to_name, _, _, name_to_player_id, first_line, entries, to_remove, player_id_to_fd_name = parse_upload_template(download_folder + template_path, [], '', 0)


  entry_name_to_ct = {}
  for entry in entries:
    entry_name = entry[2]
    if not entry_name in entry_name_to_ct:
      entry_name_to_ct[entry_name] = 1
    else:
      entry_name_to_ct[entry_name] += 1


  rosters = []

  optimizer = FD_NBA_Optimizer()

  rosters = optimizer.optimize_top_n(by_position, 5000, iter=iter)

  rosters_sorted = sorted(rosters, key=lambda a:a.value, reverse=True)
  orig_rosters_sorted = rosters_sorted
  if roster_filter != None:
    rosters_sorted = [r for r in rosters_sorted if roster_filter(r)]

  SE_ROSTER_TAKE = 10

  for roster in rosters_sorted[:SE_ROSTER_TAKE]:
    print(roster)

  # print("SE PLAYER EXPOSURES:")
  # utils.print_player_exposures(rosters_sorted[:SE_ROSTER_TAKE])


  mme_rosters = rosters_sorted
  print("MME ROSTERS RESOLVED: {}".format(len(mme_rosters)))
  valid_mme_rosters = [r for r in mme_rosters if is_roster_valid(r)]
  mme_rosters = valid_mme_rosters

  if len(mme_rosters) < 151:
    __import__('pdb').set_trace()

  top_mme_rosters = mme_rosters[rosters_to_skip:151 + rosters_to_skip]

  print("MME PLAYER EXPOSURES:")
  player_to_ct = utils.print_player_exposures(top_mme_rosters)

  # hedge_rosters = generate_hedge_lineups(player_to_ct, by_position, optimizer, 100, iter=50000)
  hedge_rosters = None

  to_print = []
  index_strings = []
  # distribute best roster to the single entry, and the rest to the MME
  entry_name_to_take_idx = {}
  invalid_roster_ct = 1

  for entry in entries:
    entry_name = entry[2]
    entry_ct = entry_name_to_ct[entry_name]

    IS_HEDGE_ENTRY = entry_name == hedge_entry_name \
      and entry_name in entry_name_to_take_idx \
      and entry_name_to_take_idx[entry_name] > hedge_entry_ct

    if not entry_name in entry_name_to_take_idx:
      if entry_ct > 1 and not IS_HEDGE_ENTRY:
        entry_name_to_take_idx[entry_name] = 1
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
    elif entry_ct < SE_ROSTER_TAKE:
      idx = take_idx % len(rosters_sorted)
      roster_to_append = rosters_sorted[idx]
      if not is_roster_valid(roster_to_append):
        roster_to_append = rosters_sorted[idx + 1]
        assert is_roster_valid(roster_to_append)

      to_print.append(roster_to_append)
      index_strings.append(str(idx) + "_SE_{}".format(roster_to_append.value))
    else:
      idx = take_idx % len(top_mme_rosters)
      roster_to_append = top_mme_rosters[idx]
      assert is_roster_valid(roster_to_append)
      
      to_print.append(roster_to_append)
      index_strings.append(str(idx) + "_MME_{}".format(roster_to_append.value))
    
      entry_name_to_take_idx[entry_name] += 1

  construct_upload_template_file(to_print, first_line, entries, name_to_player_id, player_id_to_fd_name, index_strings)

  return mme_rosters


def reoptimize_slate(slate_path, current_rosters_path, current_time, start_times, allow_duplicate_rosters=False):
  player_id_to_name, _, _, name_to_player_id, first_line, entries, to_remove, player_id_to_fd_name = parse_upload_template(download_folder + current_rosters_path, [], '', 0)

  start_times = utils.load_start_times_and_slate_path(start_times)[0]
  locked_teams = []
  for time, teams in start_times.items():
    if time < current_time:
      locked_teams += teams
  
  projections = NBA_WNBA_Projections(download_folder + slate_path, "NBA")
  projections.print_slate()

  by_position = projections.players_by_position(exclude_zero_value=False)
  name_to_players = get_name_to_player_objects(by_position)
  optimizer = FD_NBA_Optimizer()

  by_position = filter_out_locked_teams(by_position, locked_teams)
  existing_rosters = parse_existing_rosters(download_folder + current_rosters_path)
  seen_roster_strings = []
  seen_roster_string_to_optimized_roster = {}

  resolve_roster_keys = []

  roster_idx = 0
  all_results = []
  for existing_roster in existing_rosters:
    print("ROSTER: {}".format(roster_idx))
    roster_idx += 1
    players = existing_roster[3:12]
    if players[0] == '':
      continue

    roster_string = ",".join(players)

    if roster_string in seen_roster_strings:
      result = seen_roster_string_to_optimized_roster[roster_string]
      all_results.append(result)
      continue

    seen_roster_strings.append(roster_string)
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


    if lock_ct != 9:
      result = optimizer.optimize(by_position, players5, int(5000))
      # result = optimizer.optimize(by_position, players5, int(600))

    else:
      result = utils.Roster(players4)
    
    seen_roster_string_to_optimized_roster[roster_string] = result
    try:
      names1 = [p.name for p in result.players]
      roster1_key = ",".join(sorted(names1))

      is_se_roster = "Single Entry" in existing_roster[2] or "Entries Max" in existing_roster[2]
      if is_se_roster:
        print("IS SE ROSTER!")

      if roster1_key in seen_roster_strings and not allow_duplicate_rosters and not is_se_roster:
          # don't change the result
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
    except:
      __import__('pdb').set_trace()

  utils.print_player_exposures(all_results, locked_teams)
  variation = utils.print_roster_variation(all_results)
  print(variation)
  
  # variation = utils.print_roster_variation(existing_rosters)
  # print(variation)
  

  construct_upload_template_file(all_results, first_line, entries, name_to_player_id, player_id_to_fd_name, None)


def single_game_optimizer():
  download_folder = "/Users/amichailevy/Downloads/"
  slate_path = "FanDuel-NBA-2022 ET-10 ET-29 ET-82506-players-list.csv"
  template_path = "FanDuel-NBA-2022-10-29-82506-entries-upload-template.csv"
  player_id_to_name, _, _, name_to_player_id, first_line, entries, to_remove, player_id_to_fd_name = parse_upload_template(download_folder + template_path, [], '', 4)

  projections = NBA_WNBA_Projections(download_folder + slate_path, "NBA")

  projections.print_slate()

  by_position = projections.players_by_position()

  all_results = utils.single_game_optimizer_many(by_position, 4)

  all_results_rosters = [utils.Roster(result[0]) for result in all_results]

  construct_upload_template_file(all_results_rosters * 1000, first_line, entries, name_to_player_id, player_id_to_fd_name, None)


if __name__ == "__main__":
  download_folder = "/Users/amichailevy/Downloads/"
  # template_path = "FanDuel-NBA-2022-11-01-82625-entries-upload-template.csv"

  # slate_path = "FanDuel-NBA-2022 ET-11 ET-01 ET-82625-players-list.csv"
  # all_rosters = optimize_slate(slate_path, template_path, 0, iter=120000, roster_filter=None, hedge_entry_name="", hedge_entry_ct = 0)


  # assert False
  # single_game_optimizer()

  
  # all_rosters = optimize_slate(slate_path, template_path, 155, iter=90000, roster_filter=None, hedge_entry_name="", hedge_entry_ct = 0)
  # all_rosters = optimize_slate(slate_path, template_path, 0, 1000)



  # dk_slate_path = "DKSalaries (1).csv"
  
  # all_rosters = optimize_slate_dk(dk_slate_path, 200000)

  # optimize_slate(slate_path, template_path2, 0, 100000)

  # slate_path = "FanDuel-NBA-2022 ET-11 ET-04 ET-82790-players-list.csv"
  # template_path = "FanDuel-NBA-2022-11-04-82790-entries-upload-template.csv"

  # # TODO CONSIDER SORTING ENTRIES BY ENTRY FEE BEFORE REOPTIMIZING


  slate_path = "FanDuel-NBA-2022 ET-11 ET-06 ET-82909-players-list.csv"
  template_path = "FanDuel-NBA-2022-11-06-82909-entries-upload-template (1).csv"
  # all_rosters = optimize_slate(slate_path, template_path, 0, iter=150000)
  reoptimize_slate(slate_path, "FanDuel-NBA-2022-11-06-82909-entries-upload-template (2).csv", 9.6, "start_times.txt", False)


  assert False

# validate player name matching!