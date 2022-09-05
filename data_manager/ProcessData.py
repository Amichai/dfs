from unittest import result
import argparse
import data_manager
import time
import dateutil
from tinydb import TinyDB, Query, where

def calculatePercentDifference(v1, v2):
  v1 = float(v1)
  v2 = float(v2)
  diff = v2 - v1
  if diff == 0:
    return 0

  return diff / (v1 + 0.01)

def arbitrage(name_to_site_to_stat):
  name_to_stat_to_site = {}

  for name, site_to_stat in name_to_site_to_stat.items():
    name_to_stat_to_site[name] = {}
    for site, stats in site_to_stat.items():

      for stat, val in stats.items():
        if ":isActive" in stat:
          continue
        
        if not stat in name_to_stat_to_site[name]:
          name_to_stat_to_site[name][stat] = {}

        val_filtered = val
        if site == "Caesars":
          is_active_key = stat + ":isActive"
          if is_active_key in stats:
            val_filtered = []
            is_active_results = stats[is_active_key]
            assert len(is_active_results) == len(val)
            for i in range(len(is_active_results)):
              if is_active_results[i][0] == True:
                val_filtered.append(val[i])

        name_to_stat_to_site[name][stat][site] = val_filtered


  results = []
  for name, stat_to_site in name_to_stat_to_site.items():
    for stat, sites in stat_to_site.items():
      stat_vals = []
      for site, vals in sites.items():
        try:
          stat_vals.append(float(vals[-1][0]))
        except:
          # This happens if :isActive = False on Caesars
          continue

      if len(stat_vals) <= 1:
        continue
      min_val = min(stat_vals)
      max_val = max(stat_vals)
      difference = round(calculatePercentDifference(min_val, max_val), 2)
      results.append([difference, name, stat, sites])

      # if len(keys) > 1:
      #   # print("{} - {}, {}".format(name, stat, sites))
      #   pp_vals = sites['PP']
      #   caesars_vals = sites['Caesars']
      #   for pp_val in pp_vals:
      #     pp_time = time.strptime(pp_val[1],"%H:%M:%S")
      #     for c_val in caesars_vals:
      #       c_time = time.strptime(c_val[1],"%H:%M:%S")
      #       time_diff = time.mktime(pp_time) - time.mktime(c_time)
      #       # print(time_diff)
      #       if abs(time_diff) < 120:
      #         difference = round(calculatePercentDifference(pp_val[0], c_val[0]), 2)
      #         # print("{} - {}: {} - {} = {}".format(name, stat, pp_val[0], c_val[0], difference))
      #         results.append([difference, pp_val[0], c_val[0], name, stat, pp_val[1]])

  results_sorted = sorted(results, key=lambda a: abs(a[0]), reverse=True)
  for result in results_sorted:
    print(result)
      

def findDiffs(name_to_site_to_stat):
  for name, site_to_stat in name_to_site_to_stat.items():
    for site, stats in site_to_stat.items():
      for stat, val in stats.items():
        if ":isActive" in stat:
          continue
        # print("{} - {}".format(stat, val))
        just_values = [v[0] for v in val]
        just_times = [v[1] for v in val]

        for i in range(len(just_values) - 1):
          v1 = float(just_values[i])
          v2 = float(just_values[i + 1])
          diff = v2 - v1
          if diff == 0:
            continue

          change = diff / (v1 + 0.01)

          # CHECK THE IS ACTIVE FLAG BEFORE CONTINUING? 
          # FILTER ON THE TIMES
          
          if abs(change) > 0.1:
            print("{} - {}".format(name, site))
            print("{} - {} = {}".format(stat, val, change))
    

# Internal to each scraper/stat look for difference
# across scrapers - arbitrage

def process(dataManager, sport):
  name_to_site_to_stat = {}
  all_names = []
  query = Query()
  results = dataManager.db.search((query['sport'] == sport))

  for result in results:
    name = result['name']
    site = result['scraper']
    time = result['_time']
    
    # print("{}, {}, {}".format(result['_time'], name, result['projections']))
    if not name in all_names:
      all_names.append(name)

    if not name in name_to_site_to_stat:
      name_to_site_to_stat[name] = {}
    
    if not site in name_to_site_to_stat[name]:
      name_to_site_to_stat[name][site] = {}

    projections = result['projections']
    for key, value in projections.items():
      if not key in name_to_site_to_stat[name][site]:
        name_to_site_to_stat[name][site][key] = []

      name_to_site_to_stat[name][site][key].append((value, time))
      
    # name_to_stat[name].append(result)
  # findDiffs(name_to_site_to_stat)
  arbitrage(name_to_site_to_stat)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sport', required=True)
    args = vars(parser.parse_args())
    sport = args['sport']
    dataManager = data_manager.DataManager(sport)
    process(dataManager, sport)