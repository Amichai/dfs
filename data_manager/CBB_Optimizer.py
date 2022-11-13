from data_manager import DataManager
import utils
from Optimizer import DK_CBB_Optimizer
from table import Table

PRE_KEY = 'Points + Rebounds + Assists'
FANTASY_SCORE_KEY = 'Fantasy Score'





# convert PRE to fantasy score
# convert FD FS to DK FS


# PRE to fantasy score:
# 1.1864x + 0.6151

# FD basketball to DK basketball
# 1.0557x - 0.9654
# ----
# read the DK slate file
# for each player, print the price and the available projections

def convert_fd_fantasy_score_to_dk(fantasy_score):
  return 1.0557 * fantasy_score - 0.9654

def convert_pre_to_fantasy_score(pre):
  return 1.1864 * pre + 0.6151

def get_player_projections(name, dm):
  to_return = {}
  projections = dm.query_projection("CBB", "PP", name)

  if projections != None and FANTASY_SCORE_KEY in projections:
    fantasy_score = projections[FANTASY_SCORE_KEY]
    to_return["pp_fs"] = fantasy_score
    to_return["pp_fs_DK"] = convert_fd_fantasy_score_to_dk(fantasy_score)
  if projections != None and PRE_KEY in projections:
    pre = projections[PRE_KEY]
    to_return["pp_pre"] = pre
    fantasy_score = convert_pre_to_fantasy_score(pre)
    to_return["pp_pre_fs"] = fantasy_score
    to_return["pp_pre_fs_DK"] = convert_fd_fantasy_score_to_dk(fantasy_score)

  projections = dm.query_projection("CBB", "DFSCrunch", name)
  if FANTASY_SCORE_KEY in projections:
    to_return["dfc_fs"] = float(projections[FANTASY_SCORE_KEY])

  to_return['value'] = to_return["dfc_fs"] * 0.94
  if 'pp_pre_fs_DK'in to_return:
    to_return['value'] = to_return['pp_pre_fs_DK']
  if 'pp_fs_DK'in to_return:
    to_return['value'] = to_return['pp_fs_DK']

  return to_return

def get_slate_players(path):
  by_positions = {'G': [], 'F': [], 'UTIL': []}
  players = utils.get_dk_slate_players(path)
  game_infos = utils.get_dk_slate_game_info(path)
  for info in game_infos:
    print(info)

  team_to_players = {}

  for player, info in players.items():
    team = info[3]
    if not team in team_to_players:
      team_to_players[team] = []

    team_to_players[team].append(info)

  dm = DataManager("CBB")

  for team, players in team_to_players.items():
    table = Table(["name", "pos", "price", "pp_fs_DK", "pp_pre_fs_DK", "dfc_fs", "value"])
    print("****{}****".format(team))
    for player in players:
      name = player[0]
      pos = player[1]
      price = player[2]
      projections = get_player_projections(name, dm)
      row_to_add = {**projections, **{ 'name': name, 'pos': pos, 'price': price }}
      table.add_row(row_to_add)

      position_split = pos.split('/')
      for pos in position_split:
        by_positions[pos].append(utils.Player(name, pos, price, team, projections['value']))
      by_positions['UTIL'].append(utils.Player(name, pos, price, team, projections['value']))

    table.print('price')

  return by_positions

def get_players_by_position():
  pass

def opitimize():
  pass

if __name__ == "__main__":
  download_folder = "/Users/amichailevy/Downloads/"
  slate_file = "DKSalaries (1).csv"

  by_position = get_slate_players(download_folder + slate_file)

  optimizer = DK_CBB_Optimizer()
  iter = 300000
  roster = optimizer.optimize(by_position, None, iter)
  print(roster) # 211.657
  # (rosters, best_roster) = optimizer.optimize_top_n_diverse(by_position, 4, value_tolerance=4, iter=iter)
  # for roster in rosters:
  #   print(roster)
  assert False


  dm = DataManager("CBB")

  results = dm.todays_rows('CBB')

  name_to_pre = {}
  name_to_fantasy_score = {}


  all_names = []

  for result in results:
    if result["scraper"] != "PP":
      continue

    name = result['name']
    all_names.append(name)
    projections = result['projections']

    if PRE_KEY in projections:
      name_to_pre[name] = projections[PRE_KEY]

    if FANTASY_SCORE_KEY in projections:
      name_to_fantasy_score[name] = projections[FANTASY_SCORE_KEY]

  for name in all_names:

    if name in name_to_pre and name in name_to_fantasy_score:
      print("{}, {}, {}".format(name, name_to_pre[name], name_to_fantasy_score[name]))
