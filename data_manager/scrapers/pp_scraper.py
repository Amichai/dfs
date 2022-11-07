import utils

known_sports = ["NBA", "MLB", "WNBA", "NFL", "NFLP", "MMA", "CFB", "NASCAR", "NHL", "CBB"]

class PPScraper:
  def __init__(self, sport):
    self.sport = sport
    self.name = 'PP'

    assert sport in known_sports

  def run(self):
    league_id = None
    if self.sport == "NBA":
      league_id = 7
    elif self.sport == "WNBA":
      league_id = 3
    elif self.sport == "NFL":
      league_id = 9
    elif self.sport == "MLB":
      league_id = 2
    elif self.sport == "NFLP":
      league_id = 44
    elif self.sport == "MMA":
      league_id = 12
    elif self.sport == "CFB":
      league_id = 15
    elif self.sport == "CBB":
      league_id = 20
    elif self.sport == "NASCAR":
      league_id = 4
    elif self.sport == "NHL":
      league_id = 8


    assert league_id != None
    url = 'https://api.prizepicks.com/projections?league_id={}&per_page=500&single_stat=false'.format(league_id)

    as_json = utils.get_with_selenium(url)

    assert as_json["meta"]["total_pages"] == 1

    data = as_json['data']
    included = as_json['included']

    id_to_name = {}
    player_ids = []
    for player in included:
        attr = player["attributes"]
        player_name = attr['name']
        player_name = utils.normalize_name(player_name)
        # team = attr['team']
        
        player_id = player['id']
        player_ids.append(player_id)
        id_to_name[player_id] = player_name

    name_to_projections = {}

    stats_from_promotions = []

    for projection in data:
        
        attr = projection['attributes']
        stat_type = attr['stat_type']
        # created_at = attr["created_at"]
        updated_at = attr["updated_at"]
        line_score = float(attr["line_score"])
        projection_type = attr["projection_type"]
        player_id = projection['relationships']['new_player']['data']['id']
        player_name = id_to_name[player_id]
        promotion_stat_key = "{}-{}".format(stat_type, player_name)
        if promotion_stat_key in stats_from_promotions:
            continue

        # flash_sale_line_score = attr['flash_sale_line_score']
        # if flash_sale_line_score != '' and flash_sale_line_score != None:
        #     line_score = flash_sale_line_score
        #     stats_from_promotions.append(promotion_stat_key)
        
        if not player_name in name_to_projections:
            name_to_projections[player_name] = {}

        name_to_projections[player_name][stat_type] = line_score
        
    return name_to_projections
