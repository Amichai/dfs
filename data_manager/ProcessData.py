import data_manager
import time
import dateutil
from tinydb import TinyDB, Query, where


def arbitrage(name_to_site_to_stat):
  name_to_stat_to_site = {}
  # caesars to prize picks
  stat_name_mapper_pp_to_caesar = {
    'Strikeouts': 'Pitching Strikeouts',
    'Hits Allowed': 'Hits Allowed',
    'Walks Allowed': 'Walks Allowed',
    'Runs': 'Runs Scored',
    'Pitching Outs': 'Outs Recorded',
  }

  for name, site_to_stat in name_to_site_to_stat.items():
    name_to_stat_to_site[name] = {}
    for site, stats in site_to_stat.items():
      for stat, val in stats.items():
        if ":isActive" in stat:
          continue

        stat_normalized = stat
        if stat in stat_name_mapper_pp_to_caesar:
          stat_normalized = stat_name_mapper_pp_to_caesar[stat]

        if not stat_normalized in name_to_stat_to_site[name]:
          name_to_stat_to_site[name][stat_normalized] = {}

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

        name_to_stat_to_site[name][stat_normalized][site] = val_filtered

  for name, stat_to_site in name_to_stat_to_site.items():
    for stat, sites in stat_to_site.items():
      keys = sites.keys()
      if len(keys) > 1:
        print("{} - {}, {}".format(name, stat, sites))
        pp_vals = sites['PP']
        caesars_vals = sites['Caesars']
        for pp_val in pp_vals:
          pp_time = time.strptime(pp_val[1],":%H:%M:%S")
          for c_val in caesars_vals:
            c_time = time.strptime(pp_val[1],":%H:%M:%S")
            __import__('pdb').set_trace()

            pass

      pass


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

def process(dataManager):
  name_to_site_to_stat = {}
  all_names = []
  query = Query()
  results = dataManager.db.search((query['sport'] == "MLB"))

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
  pass