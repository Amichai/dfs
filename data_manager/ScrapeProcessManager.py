import time
import data_manager
from scrapers.caesars_scraper import CaesarsScraper
from scrapers.pp_scraper import PPScraper
from scrapers.dfs_crunch_scraper import DFSCrunchScraper

dataManager = data_manager.DataManager()
period = 2
scrapers_by_sport = {
  "NBA": [DFSCrunchScraper('NBA'), PPScraper('NBA'), CaesarsScraper('NBA')],
  "WNBA": [DFSCrunchScraper('WNBA'), PPScraper('WNBA')],
  "MLB": [DFSCrunchScraper('MLB'), PPScraper('MLB'), CaesarsScraper('MLB')],
}

scrapers = scrapers_by_sport['NBA']

scraper_ct = len(scrapers)
idx = 0
for i in range(scraper_ct):
  scraper = scrapers[idx % scraper_ct]
  result = scraper.run()
  print(result)
  for name, stats in result.items():
    dataManager.write_projection(scraper.sport, scraper.name, name, stats)

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