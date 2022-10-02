import math
from projection_providers.CFB_Projections import CFB_Projections
from Optimizer import CFB_Optimizer
import random
import datetime
import utils
import statistics
from ScrapeProcessManager import run
import csv
# produce a table of projections
# generate an ensemble of rosters
# produce a file to upload

def get_name_to_player_objects(by_position):
  name_to_player_objects = {}
  for pos, players in by_position.items():
    for player in players:
      if not player.name in name_to_player_objects:
        name_to_player_objects[player.name] = []
      
      name_to_player_objects[player.name].append(player)

  return name_to_player_objects

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


def construct_upload_template_file(rosters, first_line, entries, player_to_id, player_id_to_name):
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
    

if __name__ == "__main__":
  download_folder = "/Users/amichailevy/Downloads/"
  # slate_path = "FanDuel-CFB-2022 ET-09 ET-24 ET-80883-players-list.csv"
  template_path = "FanDuel-CFB-2022-09-30-81160-entries-upload-template.csv"
  teams_to_remove = []


  # REOPTIMIZATION - 
  start_times = "start_times.txt"
  (start_times, slate_path, _) = utils.load_start_times_and_slate_path(start_times)
  current_time = 1

  locked_teams = []
  for time, teams in start_times.items():
    if time < current_time:
      locked_teams += teams
  
  projections = CFB_Projections(download_folder + slate_path, "CFB")
  projections.print_slate()

  by_position = projections.players_by_position()
  name_to_players = get_name_to_player_objects(by_position)
  optimizer = CFB_Optimizer()

  
  # REOPTIMIZATION - 
  # by_position = filter_out_locked_teams(by_position, locked_teams)
  # current_rosters_path = "upload_template_2022-09-24 08_53_53_671447.csv"
  # existing_rosters = parse_existing_rosters(download_folder + current_rosters_path)


  entries = []
  player_id_to_name, _, _, name_to_player_id, first_line, entries, to_remove, player_id_to_fd_name = parse_upload_template(download_folder + template_path, [], '', 2)


  # for existing_roster in existing_rosters:
  #   players = existing_roster[3:]
  #   players2 = [p.split(':')[0] for p in players]
  #   players3 = [player_id_to_name[p] for p in players2]
  #   players4 = [name_to_players[p][0] for p in players3]
  #   players5 = []
  #   for p in players4:
  #     if p.team in locked_teams:
  #       players5.append(p)
  #     else:
  #       players5.append(None)

  #   result = optimizer.optimize(by_position, players5)
  
  # assert False


  # dfs_crunch_path = "DFSCRUNCH-DOWNLOAD-DATA-fd76041 (2).csv"
  # by_position = utils.load_crunch_dfs_projection(dfs_crunch_path, slate_path, download_folder)
  # all_teams = projections.all_teams
  

  # print_optimizer_projections(by_position, name_to_player_id)

  entry_name_to_ct = {}
  for entry in entries:
    entry_name = entry[2]
    if not entry_name in entry_name_to_ct:
      entry_name_to_ct[entry_name] = 1
    else:
      entry_name_to_ct[entry_name] += 1


  rosters = []

  rosters = optimizer.optimize_top_n(by_position, 120)
  # rosters = [result]

  rosters_sorted = sorted(rosters, key=lambda a:a.value, reverse=True)
  for roster in rosters_sorted:
    print(roster)

  print_player_exposures(rosters_sorted)

  to_print = []

  # distribute best roster to the single entry, and the rest to the MME
  take_idx = 0
  for entry in entries:
    entry_name = entry[2]
    entry_ct = entry_name_to_ct[entry_name]
    # if entry_ct == 1:
    #   to_print.append(rosters_sorted[0])
    # else:
    to_print.append(rosters_sorted[take_idx % len(rosters_sorted)])
    take_idx += 1

  construct_upload_template_file(to_print, first_line, entries, name_to_player_id, player_id_to_fd_name)
  # pick pairs and triples
  # filter out all other 

#
  