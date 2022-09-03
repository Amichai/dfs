from ast import parse
from email import parser
import time
import data_manager
from scrapers.caesars_scraper import CaesarsScraper
from scrapers.pp_scraper import PPScraper
from scrapers.dfs_crunch_scraper import DFSCrunchScraper
import argparse
from ProcessData import process


def run(sport):
  dataManager = data_manager.DataManager()
  period = 3
  scrapers_by_sport = {
    "NBA": [DFSCrunchScraper('NBA'), PPScraper('NBA'), CaesarsScraper('NBA')],
    "WNBA": [DFSCrunchScraper('WNBA'), PPScraper('WNBA')],
    "MLB": [DFSCrunchScraper('MLB'), PPScraper('MLB')],
    # "MLB": [DFSCrunchScraper('MLB')],
    "MLB": [PPScraper('MLB'), CaesarsScraper('MLB')],
    # "NFL": [PPScraper('NFLP')],
    # "NFL": [PPScraper('NFL'), CaesarsScraper('NFL')],
    "NFL": [CaesarsScraper('NFL')],
  }

  scrapers = scrapers_by_sport[sport]

  scraper_ct = len(scrapers)
  idx = 0
  for i in range(scraper_ct):
    scraper = scrapers[idx % scraper_ct]
    result = scraper.run()
    # print(result)

    # __import__('pdb').set_trace()
    for name, stats in result.items():
      dataManager.write_projection(scraper.sport, scraper.name, name, stats)

      # for stat, val in stats.items():
      #   print("{}, {}, {}".format(name, stat, val))


    dataManager.write_zeros(scraper.sport, scraper.name, result)
    # store result in memory
    # write result to disk (last updated)
    # print the diff
    # run queries on the data to find arbitrage

    time.sleep(period)
    idx += 1



# Find Arbitrage
# Print the slate!
# pass in a slate, print all the players and their status and projections
# produce a projection log where we can observe meaningful changes
# track remove/non change/upadte/added operations!
# Store projections in memory but don't write to disk until later?

if __name__ == "__main__":
  dataManager = data_manager.DataManager()
  process(dataManager)

  # parser = argparse.ArgumentParser()
  # parser.add_argument('-s', '--sport', required=True)
  # args = vars(parser.parse_args())
  # run(args['sport'])