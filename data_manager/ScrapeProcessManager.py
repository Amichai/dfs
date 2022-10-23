from ast import parse
from email import parser
import time
from datetime import timedelta, date
import data_manager
from scrapers.caesars_scraper import CaesarsScraper
from scrapers.pp_scraper import PPScraper
from scrapers.dfs_crunch_scraper import DFSCrunchScraper
from scrapers.thrive_fantasy_scraper import TFScraper
from scrapers.underdog_scraper import UnderdogScraper
from scrapers.rotowire_scraper import RotoWireScraper
from scrapers.numberfire_scraper import NumberFireScraper
import argparse
from ProcessData import process
import utils


def run(sport, count=None):
  dataManager = data_manager.DataManager(sport)
  period = 3
  scrapers_by_sport = {
    "NBA": [
        PPScraper('NBA'),
        NumberFireScraper('NBA'),
        CaesarsScraper('NBA'),
        # TFScraper('NBA'),
        # UnderdogScraper("NBA"),
        # RotoWireScraper('NBA', '8799'),
      ], #DFSCrunchScraper('NBA')
    "WNBA": [DFSCrunchScraper('WNBA'), PPScraper('WNBA')],
    "MLB": [TFScraper('MLB'), UnderdogScraper("MLB"), PPScraper('MLB'), CaesarsScraper('MLB'), ], # , DFSCrunchScraper('MLB')
    "NFL": [PPScraper('NFL'), RotoWireScraper('NFL', '3636'), CaesarsScraper('NFL', True), UnderdogScraper("NFL")], # , TFScraper('NFL')
    "MMA": [CaesarsScraper("MMA", False), PPScraper("MMA")],
    "CFB": [PPScraper('CFB'), UnderdogScraper("CFB"), CaesarsScraper('CFB', True)],
    "NASCAR": [RotoWireScraper('NASCAR', '192'), PPScraper("NASCAR")],
    "PGA": [CaesarsScraper('PGA')],
    "NHL": [PPScraper("NHL"), CaesarsScraper("NHL", False)]
  }

  scrapers = scrapers_by_sport[sport]
  if count != None:
    scrapers = scrapers[:int(count)]

  scraper_ct = len(scrapers)
  idx = 0
  for i in range(scraper_ct):
    scraper = scrapers[idx % scraper_ct]
    result = scraper.run()

    result = utils.normalize_stat_name(result)

    for name, stats in result.items():
      dataManager.write_projection(scraper.sport, scraper.name, name, stats)

      # for stat, val in stats.items():
      #   print("{}, {}, {}".format(name, stat, val))

    if len(result.keys()) > 0:
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
  parser = argparse.ArgumentParser()
  parser.add_argument('-s', '--sport', required=True)
  parser.add_argument('-c', '--count', required=False, default=None)
  args = vars(parser.parse_args())
  run(args['sport'], args['count'])


  # dataManager = data_manager.DataManager()
  # process(dataManager)


