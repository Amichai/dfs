from turtle import down
from library import *

import dk_random_optimizer
import fd_optimizer

download_folder = "/Users/amichailevy/Downloads/"


def crunch_dk_optimizer(projections_path):

  lines = open(download_folder + projections_path, "r").readlines()
  (start_time_to_teams, fd_path, dk_path) = load_start_times_and_slate_path("start_times2.txt")

  dk_players = get_dk_slate_players(download_folder + dk_path)

  dk_players_by_position = {}

  for line in lines[1:]:
    parts = line.split(',')
    name = parts[0].strip('"')
    name = normalize_name(name)
    projection = float(parts[1].strip('"'))
    

    player_info = dk_players[name]
    positions = player_info[1]
    price = player_info[2]
    team = player_info[3]

    all_player_positions = []
    for pos in positions.split("/"):
      for pos2 in dk_positions_mapper[pos]:
        if pos2 in all_player_positions:
          continue
        all_player_positions.append(pos2)

    for pos in all_player_positions:
      if not pos in dk_players_by_position:
        dk_players_by_position[pos] = []

      if projection == 0:
          continue
      
      if price != '':
          pl = dk_random_optimizer.Player(name, pos, price, team, projection, 0)
          dk_players_by_position[pos].append(pl)
      else: 
        __import__('pdb').set_trace()
        print("WARNING DK PLAYER NO PRICE: {}, {}, {}".format(name, price, projection))


  result = dk_random_optimizer.generate_unique_rosters(dk_players_by_position, 1)

  generate_dk_lineups_file(result, dk_players, "test1")


def get_players_by_position_dk(projections_path, dk_players):
  lines = open(download_folder + projections_path, "r").readlines()

  dk_players_by_position = {}

  for line in lines[1:]:
    parts = line.split(',')
    name = parts[0].strip('"')
    name = normalize_name(name)
    projection = float(parts[1].strip('"'))
    if projection == 0:
      continue
    if not name in dk_players:
      print("Missing from dk slate: {} - {}".format(name, projection))
      continue
    player_info = dk_players[name]
    positions = player_info[1]
    price = player_info[2]
    team = player_info[3]
    pos_conversion = {"SP": "P", "RP": "P"}
    for pos in positions.split("/"):
      if pos in pos_conversion:
        pos = pos_conversion[pos]
      if not pos in dk_players_by_position:

        dk_players_by_position[pos] = []

      if projection == 0:
          continue

      if price != '':
          pl = dk_random_optimizer.Player(name, pos, price, team, projection, 0)
          dk_players_by_position[pos].append(pl)
      else: 
        __import__('pdb').set_trace()
        print("WARNING DK PLAYER NO PRICE: {}, {}, {}".format(name, price, projection))
  return dk_players_by_position

def crunch_dk_mlb_optimizer_single_game(projections_path, dk_slate_path):
  dk_players = get_dk_slate_players(download_folder + dk_slate_path)
  dk_players_by_position = get_players_by_position_dk(projections_path, dk_players)
  all_players = []
  seen_names = []
  for pos, players in dk_players_by_position.items():
    for player in players:
      if player.name in seen_names:
        continue
      all_players.append(player)
      seen_names.append(player.name)
  
  
  result = dk_random_optimizer.optimize_roster_dk_showdown(all_players)

  generate_dk_lineups_file([result], dk_players, "test1", "mlb_single_game")
  pass



def crunch_dk_mlb_optimizer(projections_path, dk_slate_path):
  dk_players = get_dk_slate_players(download_folder + dk_slate_path)
  dk_players_by_position = get_players_by_position_dk(projections_path, dk_players)
  
  result = dk_random_optimizer.optimize_roster_for_sport(dk_players_by_position, "MLB")

  generate_dk_lineups_file([result], dk_players, "test1", "mlb")

def crunch_dk_el_optimizer(projections_path, dk_slate_path):
  lines = open(download_folder + projections_path, "r").readlines()
  dk_players = get_dk_slate_players(download_folder + dk_slate_path)

  dk_players_by_position = {"UTIL": []}

  for line in lines[1:]:
    parts = line.split(',')
    name = parts[0].strip('"')
    name = normalize_name(name)
    projection = float(parts[1].strip('"'))
    if projection == 0:
      continue
    if not name in dk_players:
      print("Missing from dk slate: {} - {}".format(name, projection))
      continue
    player_info = dk_players[name]
    positions = player_info[1]
    price = player_info[2]
    team = player_info[3]

    for pos in positions.split("/"):
      if not pos in dk_players_by_position:

        dk_players_by_position[pos] = []

      if projection == 0:
          continue

      if price != '':
          pl = dk_random_optimizer.Player(name, pos, price, team, projection, 0)
          dk_players_by_position[pos].append(pl)
          
          pl = dk_random_optimizer.Player(name, pos, price, team, projection, 0)
          dk_players_by_position["UTIL"].append(pl)
      else: 
        __import__('pdb').set_trace()
        print("WARNING DK PLAYER NO PRICE: {}, {}, {}".format(name, price, projection))

  result = dk_random_optimizer.optimize_roster_for_sport(dk_players_by_position, "EL")

  generate_dk_lineups_file([result], dk_players, "test1", "el")


def crunch_dk_epl_optimizer(projections_path, dk_slate_path):
  lines = open(download_folder + projections_path, "r").readlines()
  dk_players = get_dk_slate_players(download_folder + dk_slate_path)

  dk_players_by_position = {"UTIL": []}

  for line in lines[1:]:
    parts = line.split(',')
    name = parts[0].strip('"')
    name = normalize_name(name)
    projection = float(parts[1].strip('"'))
    if projection == 0:
      continue
    if not name in dk_players:
      print("Missing from dk slate: {} - {}".format(name, projection))
      continue
    player_info = dk_players[name]
    positions = player_info[1]
    price = player_info[2]
    team = player_info[3]

    for pos in positions.split("/"):
      if not pos in dk_players_by_position:

        dk_players_by_position[pos] = []

      if projection == 0:
          continue

      if price != '':
          pl = dk_random_optimizer.Player(name, pos, price, team, projection, 0)
          dk_players_by_position[pos].append(pl)
          
          pl = dk_random_optimizer.Player(name, pos, price, team, projection, 0)
          dk_players_by_position["UTIL"].append(pl)
      else: 
        __import__('pdb').set_trace()
        print("WARNING DK PLAYER NO PRICE: {}, {}, {}".format(name, price, projection))

  result = dk_random_optimizer.optimize_roster_for_sport(dk_players_by_position, "EPL")

  generate_dk_lineups_file([result], dk_players, "test1", "epl")

def crunch_dk_PGA_optimizer(projections_path, dk_slate_path):
  lines = open(download_folder + projections_path, "r").readlines()
  dk_players = get_dk_slate_players(download_folder + dk_slate_path)

  dk_players_by_position = {}

  for line in lines[1:]:
    parts = line.split(',')
    name = parts[0].strip('"')
    name = normalize_name(name)
    projection = float(parts[1].strip('"'))
    if projection == 0:
      continue
    if not name in dk_players:
      print("Missing from dk slate: {} - {}".format(name, projection))
      continue
    player_info = dk_players[name]
    positions = player_info[1]
    price = player_info[2]
    team = player_info[3]

    for pos in positions.split("/"):
      if not pos in dk_players_by_position:

        dk_players_by_position[pos] = []

      if projection == 0:
          continue

      if price != '':
          pl = dk_random_optimizer.Player(name, pos, price, team, projection, 0)
          dk_players_by_position[pos].append(pl)
          
      else: 
        __import__('pdb').set_trace()
        print("WARNING DK PLAYER NO PRICE: {}, {}, {}".format(name, price, projection))

  result = dk_random_optimizer.optimize_roster_for_sport(dk_players_by_position, "PGA", 30000)

  generate_dk_lineups_file([result], dk_players, "test1", "PGA")

def nba_single_game_optimizer(by_position, fd_slate_path):
  seen_names = []
  all_players = []
  for pos, players in by_position.items():
      for player in players:
          player_name = player.name
          if not player_name in seen_names:
              all_players.append(player)
              seen_names.append(player_name)

  player_projections = {}
  for player in all_players:
    player_projections[player.name] = player.value

  fd_players = get_fd_slate_players(download_folder + fd_slate_path)
  to_exclude = []

  all_players = []
  for player, player_info in fd_players.items():
    if player in to_exclude:
      continue
    if player not in player_projections:
      continue
    fd_player = dk_random_optimizer.Player(player, player_info[1], player_info[2], player_info[3], player_projections[player], 0)
    all_players.append(fd_player)

  result = fd_optimizer.single_game_optimizer(all_players)
  print(result)
  for r in result:
    print("{} - {}".format(r, r.value))

  return result

def nba_single_game_optimizer_many(by_position, fd_slate_path, ct, to_exclude=[]):
  seen_names = []
  all_players = []
  for pos, players in by_position.items():
      for player in players:
          player_name = player.name
          if not player_name in seen_names:
              all_players.append(player)
              seen_names.append(player_name)

  player_projections = {}
  for player in all_players:
    player_projections[player.name] = player.value

  fd_players = get_fd_slate_players(download_folder + fd_slate_path)

  all_players = []
  for player, player_info in fd_players.items():
    if player not in player_projections:
      continue
    if player in to_exclude:
      continue
    fd_player = dk_random_optimizer.Player(player, player_info[1], player_info[2], player_info[3], player_projections[player], 0)
    all_players.append(fd_player)

  result = fd_optimizer.single_game_optimizer_many(all_players, ct)
  return result


def construct_upload_file_fanduel(template_path, rosters):
  player_id_to_name, _, _, name_to_player_id, first_line, entries, _, player_id_to_fd_name = fd_optimizer.parse_upload_template(download_folder + template_path, [], 4)
  # __import__('pdb').set_trace()
  fd_optimizer.construct_upload_template_file_single_game(rosters, first_line, entries, name_to_player_id, player_id_to_fd_name)
  pass

def _nba_single_game_optimizer(projections_path, fd_slate_path, caesars_projections):

  fd_players = get_fd_slate_players(download_folder + fd_slate_path)

  player_projections = get_dfs_cruncher_slate_projections(download_folder + projections_path)

  player_projections.update(caesars_projections)

  all_players = []
  for player, player_info in fd_players.items():
    fd_player = dk_random_optimizer.Player(player, player_info[1], player_info[2], player_info[3], player_projections[player], 0)
    all_players.append(fd_player)

  result = fd_optimizer.single_game_optimizer(all_players)
  print(result)
  for r in result:
    print("{} - {}".format(r, r.value))
  __import__('pdb').set_trace()


if __name__ == "__main__":

  # results = scrape_caesars_money_lines()
  # caesars_projections = produce_projections_from_caesars_scrape(results)
  # fd_slate_path = "FanDuel-NBA-2022 ET-04 ET-25 ET-75208-players-list.csv"
  # # redownload this!
  # projections_path = "DFSCRUNCH-DOWNLOAD-DATA-fd75203 (2).csv"
  # _nba_single_game_optimizer(projections_path, fd_slate_path, caesars_projections)

  # projections_path = "DFSCRUNCH-DOWNLOAD-DATA-dk67556 (2).csv"
  # dk_slate_path = "DKSalaries_mlb_4_21_22.csv"

  #NBA - 7pm
  # projections_path = "DFSCRUNCH-DOWNLOAD-DATA-dk67328 (3).csv"
  # crunch_dk_optimizer(projections_path)

  # MLB - 1:40 pm
  projections_path = "DFSCRUNCH-DOWNLOAD-DATA-dk68020 (1).csv"
  dk_slate_path = "DKSalaries_MLB_4_30_22_1010.csv"
  crunch_dk_mlb_optimizer_single_game(projections_path, dk_slate_path)

  # projections_path = "DFSCRUNCH-DOWNLOAD-DATA-dk67180 (3).csv"
  # dk_slate_path = "DKSalaries_4_20_22_EL.csv"
  # crunch_dk_el_optimizer(projections_path, dk_slate_path)


  # projections_path = "DFSCRUNCH-DOWNLOAD-DATA-dk66964 (3).csv"
  # dk_slate_path = "DKSalaries_4_20_22_EPL.csv"
  # crunch_dk_epl_optimizer(projections_path, dk_slate_path)


  # projections_path = "DFSCRUNCH-DOWNLOAD-DATA-dk67383.csv"
  # dk_slate_path = "DKSalaries_PGA_4_21_22.csv"
  # crunch_dk_PGA_optimizer(projections_path, dk_slate_path)