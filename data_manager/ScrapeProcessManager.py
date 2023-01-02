from projection_providers.NBA_WNBA_Projections import NBA_WNBA_Projections, NBA_Projections_dk
import datetime
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
from scrapers.fantasy_data_scraper import FantasyDataScraper
from scrapers.stokastic_scraper import StokasticScraper
import argparse
from ProcessData import process
import utils

def run(sport, count=None):
  dataManager = data_manager.DataManager(sport)

  (start_times, _, _, _) = utils.load_start_times_and_slate_path('start_times.txt')
  target_teams = sum(list(start_times.values()), [])
  period = 3
  # nfs = NumberFireScraper(sport)
  pps = PPScraper(sport)
  cs = CaesarsScraper(sport, True)
  uds = UnderdogScraper(sport)
  tfs = TFScraper(sport)
  # fantasyDataScraper = FantasyDataScraper(sport)
  stokastic = StokasticScraper(sport)

  # TODO:
  dfs_crunch_slate = {
    'CBB': 'dk77460',
    'NBA': 'fd' + utils.TODAYS_SLATE_ID_NBA,
    'NFL': 'fd' + utils.TODAYS_SLATE_ID_NFL,
  }

  dfsCrunch = DFSCrunchScraper(sport, dfs_crunch_slate[sport])

  scrapers_by_sport = {
    "NBA": [
      stokastic,
      cs,
      # dfsCrunch,
      pps,
      
      # tfs,
      # uds,
      # nfs, fantasyDataScraper, RotoWireScraper('NBA', '8799'),
    ],
    "WNBA": [dfsCrunch, pps],
    "MLB": [tfs, uds, pps, cs, ], # , DFSCrunchScraper('MLB')
    "NFL": [
      pps,
      dfsCrunch,
      # cs,
      # UnderdogScraper("NFL")], 
      # , TFScraper('NFL')
    ],
    "MMA": [CaesarsScraper("MMA", False), pps],
    "CFB": [pps, uds, cs],
    "CBB": [dfsCrunch, pps],
    "NASCAR": [RotoWireScraper('NASCAR', '192'), pps],
    "PGA": [cs],
    "NHL": [pps, CaesarsScraper("NHL", False)]
  }

  #TODO:
  # (start_times, _, _, _) = utils.load_start_times_and_slate_path('start_times.txt')
  # fd_slate_path = utils.most_recently_download_filepath('FanDuel-NBA-', utils.TODAYS_SLATE_ID_NBA, '-players-list', '.csv')
  # projections = NBA_WNBA_Projections(fd_slate_path, "NBA")
  # player_to_start_time = utils.get_player_name_to_start_time(start_times, projections)
  player_to_start_time = None

  scrapers = scrapers_by_sport[sport]

  if count != None:
    scrapers = scrapers[:int(count)]


  #TODO: Test that we see "write zero if we remove a player that hasn't started yet"
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
        dataManager.write_zeros(scraper.sport, scraper.name, result, player_to_start_time)
    # store result in memory
    # write result to disk (last updated)
    # print the diff
    # run queries on the data to find arbitrage

    # time.sleep(period)
    idx += 1



# Find Arbitrage
# Print the slate!
# pass in a slate, print all the players and their status and projections
# produce a projection log where we can observe meaningful changes
# track remove/non change/upadte/added operations!
# Store projections in memory but don't write to disk until later?

if __name__ == "__main__":
  now = datetime.datetime.now()
  current_hour = (now.hour - 12) + (now.minute / 60)
  current_hour = round(current_hour, 2)
  print("CURRENT TIME: {}".format(current_hour))
  parser = argparse.ArgumentParser()
  parser.add_argument('-s', '--sport', required=True)
  parser.add_argument('-c', '--count', required=False, default=None)
  args = vars(parser.parse_args())
  sport = args['sport']
  run(sport, args['count'])

  if sport == "NBA":
    fd_slate_path = utils.most_recently_download_filepath('FanDuel-NBA-', utils.TODAYS_SLATE_ID_NBA, '-players-list', '.csv')
    by_position = NBA_WNBA_Projections(fd_slate_path, "NBA").write_player_projections_to_db()


# fix writing zero
# i need to know how much projections are really changing
# I need to know which of these players are in my lineups
# I need to know if we are removing a player before lock