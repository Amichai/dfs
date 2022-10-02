import math
from projection_providers.NASCAR_Projections import NASCAR_Projections
from Optimizer import NASCAR_Optimizer
import random
import datetime
import utils
import statistics
from ScrapeProcessManager import run
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
  slate_path = "FanDuel-NASCAR-2022 ET-09 ET-25 ET-80857-players-list.csv"
  template_path = "FanDuel-NASCAR-2022-09-25-80857-entries-upload-template.csv"
  teams_to_remove = []

  projections = NASCAR_Projections(download_folder + slate_path, "NASCAR")
  projections.print_slate()

  by_position = projections.players_by_position()

  player_id_to_name, _, _, name_to_player_id, first_line, entries, to_remove, player_id_to_fd_name = parse_upload_template(download_folder + template_path, [], '', 4)

  # print_optimizer_projections(by_position, name_to_player_id)

  entry_name_to_ct = {}
  for entry in entries:
    entry_name = entry[2]
    if not entry_name in entry_name_to_ct:
      entry_name_to_ct[entry_name] = 1
    else:
      entry_name_to_ct[entry_name] += 1


  rosters = []

  optimizer = NASCAR_Optimizer()

  rosters = optimizer.optimize_top_n(by_position, 120)

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
  