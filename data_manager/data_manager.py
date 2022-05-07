from calendar import c
import uuid
from tinydb import TinyDB, Query, where
import logging
import utils
import dateutil.parser



logging.basicConfig(filename='logs/{}.log'.format(utils.date_str()), filemode='a', format='%(message)s', level=logging.INFO)


# stores data in memory and disk
# supports queries
# supports diff


class DataManager:
  def __init__(self):
    name = "data_files/{}.json".format(utils.date_str())
    self.db = TinyDB(name)
    # open a database with the current date
    # self.db.insert({'type': 'apple', 'count': 7})
    # self.db.insert({'type': 'peach', 'count': 3})

  def write_projection(self, sport, scraperName, name, projections):
    parts = utils.full_date_str().split(' ')
    to_write = {}
    to_write['scraper'] = scraperName
    to_write['sport'] = sport
    to_write['_day'] = parts[0]
    to_write['_time'] = parts[1]
    to_write['_id'] = str(uuid.uuid4())
    to_write['name'] = name
    to_write['projections'] = projections

    logging.info(str(to_write))
    self.db.insert(to_write)

  def todays_rows(self, sport):
    return self.query('_day', utils.date_str(), 'sport', sport)

  def delete(self, key, value):
    self.db.remove(where(key) == value)
  
  def query_projection(self, sport, scraper, name):
    query = Query()
    rows = self.db.search((query['sport'] == sport) 
      & (query['scraper'] == scraper)
      & (query['_day'] == utils.date_str())
      & (query['name'] == name))

    if len(rows) == 0:
      return None

    rows_sorted = sorted(rows, key=lambda row: dateutil.parser.isoparse("{} {}".format(row['_day'], row['_time'])), reverse=True)
    
    return rows_sorted[0]['projections']


  def query(self, key1, value1, key2=None, value2=None):
    query = Query()
    if key2 == None or value2 == None:
      result = self.db.search(query[key1] == value1)
    else:
      result = self.db.search((query[key1] == value1) & (query[key2] == value2))
    return result

if __name__ == "__main__":
  dm = DataManager()
  result = dm.todays_rows('NBA')
  print(len(result))
  print(result)
  result = dm.todays_rows('MLB')
  print(len(result))
  print(result)
  result = dm.todays_rows('WNBA')
  print(len(result))
  print(result)
