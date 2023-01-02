import utils
import math
import statistics
import json
import csv
import itertools
from projection_providers.NBA_WNBA_Projections import NBA_WNBA_Projections, NBA_Projections_dk
# load up the projections
# come up with roster generation strategies
# (add actual point annotaitions as needed)
# max value + what percentage are over the money line?

# data_file = open('data_files/dfs_crunch_11_29_22.json', "r")
# data_file = open('data_files/dfs_crunch_11_28_22.json', "r")
# data_file = open('data_files/dfs_crunch_11_27_22.json', "r")

def method1(candidates):
  # filter out permutations, check the average score aganist the money line
  #money line -> 290
  actual_sum = 0

  max_actual = 0
  total_ct = 0
  best_roster = None
  seen_roster_keys = []
  idx = 0
  accepted_rosters = []
  for candidate in candidates:
    idx += 1
    cost = sum([r[0] for r in candidate])
    if cost > 60000:
      continue
    # if cost < 59990: # max this number as big as possible, but enough to sustain 150 rosters
    if cost < 59000: # max this number as big as possible, but enough to sustain 150 rosters
      continue

    if idx % 10000 == 0:
      print("{} - {}".format(idx, total_ct))

    names = [a[3] for a in candidate]
    roster_key = "{}|{}|{}|{}".format(names[0], names[1], names[2], sorted([names[3], names[4]]))
    if roster_key in seen_roster_keys:
      continue
    
    seen_roster_keys.append(roster_key)

    projected = round(candidate[0][1] * 2 + candidate[1][1] * 1.5 + \
            candidate[2][1] * 1.2 + candidate[3][1] + candidate[4][1], 2)

    # if projected < 220:
    if projected < 220:
      continue
    
    actual = round(candidate[0][2] * 2 + candidate[1][2] * 1.5 + \
            candidate[2][2] * 1.2 + candidate[3][2] + candidate[4][2], 2)

    # __import__('pdb').set_trace()
    # print("{}, {}, {}".format(cost, projected, actual))
    actual_sum += actual
    if actual > max_actual:
      max_actual = actual
      best_roster = candidate
    total_ct += 1
    accepted_rosters.append([candidate, projected, actual])


  ave_score = round(actual_sum / total_ct, 2)
  print("{}, {} ave score: {}".format(max_actual, total_ct, ave_score))
  print(best_roster)

  print("----")

  # sort by projected
  accepted_rosters_sorted = sorted(accepted_rosters, key=lambda a: a[1], reverse=True)
  top_150 = accepted_rosters_sorted[:150]
  # examine actual
  just_scores = [a[2] for a in top_150]

  print("max: {} ave: {}, median: {}".format(max(just_scores), statistics.mean(just_scores), statistics.median(just_scores)))


  # 11/29/22 parameters: projected floor = 220, cost floor = 57000
  #max: 316.02
  #money line -> 290

  #11/28/22 
  # max: 315.56
  # money line: 282/283

  
def method2(candidates):
  current_set = []
  seen_roster_keys = set()
  max_actual_val = 0
  optimal_roster = None
  for candidate in candidates:
    cost = sum([r[0] for r in candidate])
    if cost > 60000:
      continue
    
    names = [a[3] for a in candidate]
    roster_key = "{}|{}|{}|{}".format(names[0], names[1], names[2], sorted([names[3], names[4]]))
    if roster_key in seen_roster_keys:
      continue

    seen_roster_keys.add(roster_key)

    projected = round(candidate[0][1] * 2 + candidate[1][1] * 1.5 + \
            candidate[2][1] * 1.2 + candidate[3][1] + candidate[4][1], 2)

    actual = round(candidate[0][2] * 2 + candidate[1][2] * 1.5 + \
            candidate[2][2] * 1.2 + candidate[3][2] + candidate[4][2], 2)
    
    current_set.append([candidate, cost, projected, actual])

    if actual > max_actual_val:
      max_actual_val = actual
      optimal_roster = candidate
    
  is_take_by_cost = False
  while len(current_set) > 300:
    if is_take_by_cost:
      sorted_set = sorted(current_set, key=lambda a: a[1], reverse=True)
      is_take_by_cost = False
    else:
      sorted_set = sorted(current_set, key=lambda a: a[2], reverse=True)
      is_take_by_cost = True
    current_set = sorted_set[:math.floor(len(current_set) / 2)]
    # take top 50% by 
    print("{} - {}".format(len(current_set), is_take_by_cost))


  top_150 = current_set[:150]  

  just_scores = [a[3] for a in top_150]
  print("Optimal: {} max: {} ave: {}, median: {}".format(max_actual_val, max(just_scores), statistics.mean(just_scores), statistics.median(just_scores)))
  print("My opto: {}".format(just_scores[0]))


  # 11/29/22 parameters: projected floor = 220, cost floor = 57000
  #max: 316.02
  #money line -> 290

  #11/28/22 
  # max: 315.56
  # money line: 282/283

# ------------------------------------------------------------------------

def fanduelSingleGameAnalysis():
  data_file = open('data_files/dfs_crunch_11_29_22.json', "r")
  # data_file = open('data_files/dfs_crunch_11_28_22.json', "r") ### hit, missed cash
  # data_file = open('data_files/dfs_crunch_11_27_22.json', "r") ## -hit and hit cash
  # data_file = open('data_files/dfs_crunch_11_26_22.json', "r") # ---- missed!, miss cash
  # data_file = open('data_files/dfs_crunch_11_25_22.json', "r") # ----missed!, miss cash
  # data_file = open('data_files/dfs_crunch_11_23_22.json', "r") #---- misss, miss cash

  as_json = json.loads(data_file.read())

  names = []

  for row in as_json:
    name = row['name']
    if not 'UTIL' in name:
      continue

    # print(row)
    salary = float(row['salary'])
    projected = float(row['pfp'])
    if projected == 0:
      continue
    points = row['points']
    if points == None:
      points = 0

    actual_points = float(points)


    names.append([salary, projected, actual_points, name])


  candidates = itertools.permutations(names, 5)

  method2(candidates)

# fanduelSingleGameAnalysis()
def draftKingsShowDownAnalysis():
  # data_file = open('data_files/dfs_crunch_dk_11_30_22_1030.json', "r")
  #  -- https://www.draftkings.com/contest/gamecenter/137600934#/
  # data_file = open('data_files/dfs_crunch_dk_11_29_22_1000.json', "r")
  #  -- https://www.draftkings.com/contest/gamecenter/137556176#/
  # data_file = open('data_files/dfs_crunch_dk_11_28_22.json', "r")
  #  -- https://www.draftkings.com/contest/gamecenter/137490455#/
  # data_file = open('data_files/dfs_crunch_dk_11_27_22.json', "r")
  #  -- https://www.draftkings.com/contest/gamecenter/137378981#/
  # data_file = open('data_files/dfs_crunch_dk_11_26_22.json', "r")
  #  -- https://www.draftkings.com/contest/gamecenter/137378981#/

  data_file = open('data_files/dfs_crunch_dk_nfl_11_28_22.json', 'r')
  as_json = json.loads(data_file.read())

  names = []

  for row in as_json:
    name = row['name']
    if not 'UTIL' in name and not 'FLEX' in name:
      continue

    # print(row)
    salary = float(row['salary'])
    projected = float(row['pfp'])
    if projected == 0:
      continue
    points = row['points']
    if points == None:
      points = 0

    actual_points = float(points)

    names.append([salary, projected, actual_points, name])

  candidates = []

  for name in names:
    capt = name

    names_filtered = [n for n in names if n != capt]
    other_payers = itertools.combinations(names_filtered, 5)
    for sub_set in other_payers:
      candidates.append([capt] + list(sub_set))


  current_set = []
  seen_roster_keys = set()
  max_actual_val = 0
  optimal_roster = None
  print("CANDIDATE COUNT: {}".format(len(candidates)))
  idx = 0
  for candidate in candidates:
    cost = candidate[0][0] * 1.5 + candidate[1][0] + candidate[2][0] + candidate[3][0] + candidate[4][0] + candidate[5][0]
    idx += 1
    if idx % 100000 == 0:
      print(idx, len(current_set))
    if cost > 50000:
      continue
    
    names = [a[3] for a in candidate]
    roster_key = "{}|{}".format(names[0], sorted([names[1], names[2], names[3], names[4], names[5]]))
    if roster_key in seen_roster_keys:
      continue

    seen_roster_keys.add(roster_key)

    projected = round(candidate[0][1] * 1.5 + candidate[1][1] + \
            candidate[2][1] + candidate[3][1] + candidate[4][1] + candidate[5][1], 2)

    actual = round(candidate[0][2] * 1.5 + candidate[1][2] + \
            candidate[2][2] + candidate[3][2] + candidate[4][2] + candidate[5][2], 2)
    
    current_set.append([candidate, cost, projected, actual])

    if actual > max_actual_val:
      max_actual_val = actual
      optimal_roster = candidate
    
  is_take_by_cost = False
  while len(current_set) > 300:
    if is_take_by_cost:
      sorted_set = sorted(current_set, key=lambda a: a[1], reverse=True)
      is_take_by_cost = False
    else:
      sorted_set = sorted(current_set, key=lambda a: a[2], reverse=True)
      is_take_by_cost = True
    current_set = sorted_set[:math.floor(len(current_set) / 2)]
    # take top 50% by 
    print("{} - {}".format(len(current_set), is_take_by_cost))


  # top_150 = current_set[:150]
  top_150 = current_set[150:]

  just_scores = [a[3] for a in top_150]
  print(optimal_roster)
  print("Optimal: {} max: {} ave: {}, median: {}".format(max_actual_val, max(just_scores), statistics.mean(just_scores), statistics.median(just_scores)))
  print("My opto: {}".format(just_scores[0]))

  pass

def draftKingsShowDownAnalysis_lastNight():
  dk_slate_path = utils.most_recently_download_filepath('DKSalaries', '(', ')', '.csv')
  dk_entries_path = utils.most_recently_download_filepath('DKEntries', '(', ')', '.csv')
  projections = NBA_Projections_dk(dk_slate_path, "NBA", "2022-12-27")

  data_file = open('data_files/dfs_crunch_dk_12_27_22_1000.json', "r")
  as_json = json.loads(data_file.read())

  names_to_actual = {}

  for row in as_json:
    name = row['name']
    if not 'UTIL' in name:
      continue

    name = utils.normalize_name(name)
    points = row['points']
    if points == None:
      points = 0

    actual_points = float(points)
    names_to_actual[name] = actual_points

  by_position = projections.players_by_position()

  player_pool_all = by_position['UTIL']
  player_pool = []
  seen_names = []
  for player in player_pool_all:
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
  max_cpt_ct = 25
  capt_to_ct = {}
  for roster in sorted_by_value:
    cpt = roster[0].name
    if not cpt in capt_to_ct:
      capt_to_ct[cpt] = 1
    else:
      capt_to_ct[cpt] += 1

    if capt_to_ct[cpt] > max_cpt_ct:
      continue

    filtered_lineups.append(roster)
    if len(filtered_lineups) == 150:
      break

  
  max_val = 0
  over_the_line = 0
  idx = 0
  # play the first 50 and then 200-300
  # for roster in sorted_by_value[100:2600]:
  for roster in filtered_lineups:
  # for roster in sorted_by_value[:150]:
    actual_val = names_to_actual[roster[0].name] * 1.5
    for player in roster[1:]:
      actual_val += names_to_actual[player.name]
    cost = utils.candidate_cost(roster)
    # print("{} - {}".format(roster, actual_val))
    # print("{}, {}, {}".format(idx, actual_val, cost))
    print("{}, {}".format(idx, actual_val))
    # print("{}, {}".format(cost, actual_val))
    idx += 1
    if actual_val > max_val:
      max_val = actual_val

    if actual_val > 224.5:
      over_the_line += 1

  # print(by_position)
  print("MAX: {} OVER: {}".format(max_val, over_the_line))
  # __import__('pdb').set_trace()
# $43 TO MAX

# draftKingsShowDownAnalysis()
draftKingsShowDownAnalysis_lastNight()

# how many different captains should I be targeting? 
# how long do we see linear results? 