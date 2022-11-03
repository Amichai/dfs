from dictdiffer import diff
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
  def __init__(self, sport, day=None):
    if day == None:
      day = utils.date_str()
    self.day = day
    name = "data_files/{}_{}.json".format(day, sport)
    self.db = TinyDB(name)

  def write_projection(self, sport, scraper_name, name, projections):
    new_id = str(uuid.uuid4())
    parts = utils.full_date_str().split(' ')
    to_write = {}
    to_write['scraper'] = scraper_name
    to_write['sport'] = sport
    to_write['_day'] = parts[0]
    to_write['_time'] = parts[1]
    to_write['_id'] = new_id
    to_write['name'] = name
    to_write['projections'] = projections

    previous_value = self.query_projection(sport, scraper_name, name)
    differences = list(diff(previous_value, projections))

    # if sport == "NBA" and scraper_name == "Caesars":
    #   old_projection = utils.parse_projection_from_caesars_lines(previous_value)
    #   new_projection = utils.parse_projection_from_caesars_lines(projections)
    #   proj1 = old_projection[0]
    #   proj2 = new_projection[0]
    #   activity1 = old_projection[1]
    #   activity2 = new_projection[1]
    #   if proj1 != proj2 or activity1 != activity2:
    #     print("{}, {}, {}".format(sport, scraper_name, name))
    #     print("OLD: {}".format(old_projection))
    #     print("NEW: {}".format(new_projection))

    if len(differences) > 0:
      self.db.insert(to_write)
      for difference in differences:
        to_log = "{}|{}|{}|{}|{}|".format(new_id, sport, scraper_name, name, difference, parts[1])
        logging.info(to_log)

        if difference[0] != 'change':
          print(to_log)
          continue
        
        (v1, v2) = difference[2]
        if difference[0] == 'change' and v1 != None and v2 != None and not isinstance(v1, bool):
          v1 = float(v1)
          v2 = float(v2)
          change = utils.percentChange(v1, v2)
          if abs(change) > 0.1:
            print(to_log + "  % Diff: {}".format(round(change, 2)))
        


    else:
      row = self.query_row(sport, scraper_name, name)
      row_id = row['_id']

      query = Query()
      self.db.update({'updated': parts[1]}, 
        query['_id'] == row_id)
      
  def write_zeros(self, sport, scraper_name, results):
    all_player_projections = self.query_all_projections(sport, scraper_name)
    for name, row in all_player_projections.items():
      if name not in results:
        # __import__('pdb').set_trace()
        # if row["projections"]['Fantasy Score'] == 0:
        #   continue
        # print("WRITING ZERO: {}".format(name))
        projections = row['projections']
        new_projections = {}
        for stat, val in projections.items():
          new_projections[stat] = 0
        self.write_projection(sport, scraper_name, name, new_projections)

  def query_all_projections(self, sport, scraper):
    query = Query()
    rows = self.db.search((query['sport'] == sport) 
      & (query['scraper'] == scraper)
      & (query['_day'] == self.day))

    if len(rows) == 0:
      return None
    
    name_to_rows = {}
    for row in rows:
      name = row['name']
      if not name in name_to_rows:
        name_to_rows[name] = row
      elif name in name_to_rows:
        old_row = name_to_rows[name]
        d_new = "{} {}".format(row['_day'], row['_time'])
        d_old = "{} {}".format(old_row['_day'], old_row['_time'])
        parsed_new = dateutil.parser.isoparse(d_new)
        parsed_old = dateutil.parser.isoparse(d_old)

        if parsed_new > parsed_old:
          name_to_rows[name] = row

    return name_to_rows

  def todays_rows(self, sport):
    return self.query('_day', utils.date_str(), 'sport', sport)

  def delete(self, key, value):
    self.db.remove(where(key) == value)

  def query_row(self, sport, scraper, name):
    query = Query()
    rows = self.db.search((query['sport'] == sport) 
      & (query['scraper'] == scraper)
      & (query['_day'] == self.day)
      & (query['name'] == name))

    if len(rows) == 0:
      return None

    rows_sorted = sorted(rows, key=lambda row: dateutil.parser.isoparse("{} {}".format(row['_day'], row['_time'])), reverse=True)
    return rows_sorted[0]

  
  def query_projection(self, sport, scraper, name):
    row = self.query_row(sport, scraper, name)
    if row == None:
      return None
    
    return row['projections']


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
