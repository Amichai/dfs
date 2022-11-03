import utils

class NumberFireScraper:
  def __init__(self, sport):
    self.sport = sport
    self.name = 'NumberFire'
    if self.sport == "NBA":
      self.query_url = 'https://www.numberfire.com/nba/daily-fantasy/daily-basketball-projections'
    elif self.sport == "NFL":
      self.query_url = 'https://www.numberfire.com/nfl/daily-fantasy/daily-football-projections'
    else:
      __import__('pdb').set_trace()
      print("unknown sport")
      assert False
      

    # assert sport in known_sports

  def run(self):
    soup = utils.get_request_beautiful_soup(self.query_url)
    all_rows = soup.select('tr')

    name_to_projections = {}
    
    for row in all_rows:

      cells = row.select('td')
      if len(cells) < 11:
        continue

      name = cells[0].select('a')[1].text.strip()
      name = utils.normalize_name(name)
      projection = cells[1].text.strip()

      if not name in name_to_projections:
        name_to_projections[name] = {}

      name_to_projections[name]['Fantasy Score'] = projection
    
    return name_to_projections
