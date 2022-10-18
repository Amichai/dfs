import utils

class RotoWireScraper:
  def __init__(self, sport, slateId):
    self.sport = sport
    self.name = 'RotoWire'
    self.slateId = slateId
    if self.sport == "NBA":
      self.query_url = "https://www.rotowire.com/daily/tables/optimizer-nba.php?siteID=2&slateID={}&projSource=RotoWire".format(slateId)
    elif self.sport == "NFL":
      self.query_url = 'https://www.rotowire.com/daily/tables/optimizer-nfl.php?siteID=2&slateID={}&projSource=RotoWire&oshipSource=RotoWire'.format(slateId)
    elif self.sport == "NASCAR":
      self.query_url = 'https://www.rotowire.com/daily/tables/optimizer-nas.php?projections=&siteID=2&slateID={}'.format(slateId)
    else:
      print("unknown sport")
      assert False
      

    # assert sport in known_sports

  def run(self):
    

    as_json = utils.get_request(self.query_url)
    name_to_projections = {}
    
    for player in as_json:
      id = player['id']
      playerId = player['playerID']
      name = player['player']
      name = utils.normalize_name(name)
      status = player['injury']
      projection = player['proj_points']
      projection_ceiling = player['proj_ceiling']


      if not name in name_to_projections:
        name_to_projections[name] = {}

      name_to_projections[name]['Fantasy Score'] = projection
      name_to_projections[name]['projection_ceiling'] = projection_ceiling
      # name_to_projections[name]['status'] = status
        
    return name_to_projections
