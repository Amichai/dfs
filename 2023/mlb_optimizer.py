from dfs_crunch_scraper import DFSCrunchScraper

slate_id = 91577

path = '/Users/amichailevy/Downloads/DFSCRUNCH-DOWNLOAD-DATA-fd{}.csv'.format(slate_id)

scraper = DFSCrunchScraper('MLB', slate_id)
result = scraper.run()

by_position = {}

for (name, player) in result.items():
  position = player['position']
  pass


print(result)
