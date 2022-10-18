import math
from projection_providers.NBA_WNBA_Projections import NBA_WNBA_Projections
import random
import datetime
import utils
import statistics
from ScrapeProcessManager import run
from Optimizer import FD_NBA_Optimizer
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
  

def optimize_slate(slate_path, template_path):
  projections = NBA_WNBA_Projections(download_folder + slate_path, "NBA")
  projections.print_slate()

  by_position = projections.players_by_position()


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

  rosters = optimizer.optimize_top_n(by_position, 5000)

  rosters_sorted = sorted(rosters, key=lambda a:a.value, reverse=True)
  SE_ROSTER_TAKE = 10

  for roster in rosters_sorted[:SE_ROSTER_TAKE]:
    print(roster)

  print("SE PLAYER EXPOSURES:")
  utils.print_player_exposures(rosters_sorted[:SE_ROSTER_TAKE])

  # TODO: MME EARLY SLATE LOCK-IN
  early_slate_teams = ["PHI", "BOS"]
  mme_rosters = []
  early_slate_ids = []
  for roster in rosters_sorted:
    roster_id = ""
    seen_positions = []
    for pl in roster.players:
      if not pl.team in early_slate_teams:
        continue
      roster_id += pl.name + pl.position + "|"
    
      if pl.position in seen_positions:
        roster_id = ""
        break
      seen_positions.append(pl.position)

    if roster_id != "" and not roster_id in early_slate_ids:
      early_slate_ids.append(roster_id)
      mme_rosters.append(roster)
    
  print("MME ROSTERS RESOLVED: {}".format(len(mme_rosters)))
  if len(mme_rosters) < 151:
    __import__('pdb').set_trace()

  top_mme_rosters = mme_rosters[:151]
  print("MME PLAYER EXPOSURES:")
  utils.print_player_exposures(top_mme_rosters)

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

    if entry_ct < SE_ROSTER_TAKE:
      idx = take_idx % len(rosters_sorted)
      to_print.append(rosters_sorted[idx])
      index_strings.append(str(idx) + "_SE")
    else:
      idx = take_idx % len(top_mme_rosters)
      to_print.append(top_mme_rosters[idx])
      index_strings.append(str(idx) + "_MME")
    
    entry_name_to_take_idx[entry_name] += 1

  construct_upload_template_file(to_print, first_line, entries, name_to_player_id, player_id_to_fd_name, index_strings)



def reoptimize_slate(slate_path, current_rosters_path, current_time):
  player_id_to_name, _, _, name_to_player_id, first_line, entries, to_remove, player_id_to_fd_name = parse_upload_template(download_folder + current_rosters_path, [], '', 0)

  start_times = "start_times.txt"
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

  for existing_roster in existing_rosters:
    players = existing_roster[3:12]
    roster_string = ",".join(players)

    if roster_string in seen_roster_strings:
      continue

    seen_roster_strings.append(roster_string)
    players3 = [player_id_to_name[p] for p in players]
    players4 = [name_to_players[p][0] for p in players3]
    players5 = []
    initial_roster = []
    for p in players4:
      if p.team in locked_teams:
        players5.append(p)
      else:
        players5.append(None)
      initial_roster.append(p.name)


    result = optimizer.optimize(by_position, players5)

    print("INITIAL ROSTER:\n{}".format(initial_roster))
    print(result)


if __name__ == "__main__":
  download_folder = "/Users/amichailevy/Downloads/"
  slate_path = "FanDuel-NBA-2022 ET-10 ET-18 ET-81576-players-list.csv"
  template_path = "FanDuel-NBA-2022-10-18-81576-entries-upload-template (1).csv"


  optimize_slate(slate_path, template_path)

  # reoptimize_slate(slate_path, "FanDuel-NBA-2022-10-12-81712-entries-upload-template (6).csv", 9.6)
  assert False

  teams_to_remove = []
  start_times = "start_times.txt" # TODO

  start_times = utils.load_start_times_and_slate_path(start_times)
  # __import__('pdb').set_trace()



  # projections = MLBProjections(download_folder + slate_path)
  
  # pick pairs and triples
  # filter out all other 

#
  