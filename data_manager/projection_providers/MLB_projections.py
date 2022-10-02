from data_manager import DataManager
from tabulate import tabulate
import utils




def parse_fantasy_score_from_projections(site, projections):
  if site == "PP":
    if 'Hitter Fantasy Score' in projections:
      return projections['Hitter Fantasy Score']

    if 'Pitcher Fantasy Score' in projections:
      return projections['Pitcher Fantasy Score']

    return ''
  elif site == "DFSCrunch":
    return projections["Fantasy Score"]
  elif site == "Caesars":
    return 0

def parse_caesaers_projection_activity_metric(caesars_projection):
  return 0


class MLBProjections:
  def __init__(self, slate_path):
    self.dm = DataManager()
    self.sport = 'MLB'
    self.scrapers = ['DFSCrunch', 'PP', 'Caesars']

    self.fd_players = utils.get_fd_slate_players(slate_path, exclude_injured_players=False)
    self.all_teams = []
    for player, info in self.fd_players.items():
      team = info[3]
      if team not in self.all_teams:
        self.all_teams.append(team)
        

  def get_player_rows(self):
    all_rows = []

    for player, info in self.fd_players.items():
      position = info[1]
      cost = float(info[2])
      team = info[3]
      opp_team = info[4]
      status = info[5]
      player_row = [player, team, opp_team, position, cost, status]

      scraper_to_projections = {}

      for scraper in self.scrapers:
        projections = self.dm.query_projection(self.sport, scraper, player)
        scraper_to_projections[scraper] = projections
        projection = ''
        if projections != None:
          projection = parse_fantasy_score_from_projections(scraper, projections)
        player_row.append(projection)

      player_row.append(parse_caesaers_projection_activity_metric(scraper_to_projections["Caesars"]))

      all_rows.append(player_row)

    return all_rows

  def players_by_position(self):
    by_position = {"UTIL": [], 'C/1B': []}
    all_rows = self.get_player_rows()
    for row in all_rows:
      name = row[0]
      team = row[1]
      opp = row[2]
      pos = row[3]
      cost = row[4]
      status = row[5]
      dfs_crunch = row[6]
      pp_proj = row[7]
      caesars_proj = row[8]
      caesars_is_active = row[9]

      value = dfs_crunch
      if value == '':
        continue

      value = float(value)

      if value == 0:
        continue

      positions = pos.split('/')
      for position in positions:
        if not position in by_position:
          by_position[position] = []
        if position != 'P':
          by_position['UTIL'].append(utils.Player(name, position, cost, team, value, opp))
        if position == 'C' or position == '1B':
          by_position['C/1B'].append(utils.Player(name, position, cost, team, value, opp))
        else:
          by_position[position].append(utils.Player(name, position, cost, team, value, opp))

    return by_position

  def print_slate(self):
    team_to_players = {}

    all_rows = self.get_player_rows()
    for player_row in all_rows:
      team = player_row[1]

      if not team in team_to_players:
        team_to_players[team] = []

      team_to_players[team].append(player_row)

    for team, rows in team_to_players.items():
      print("TEAM: {}".format(team))

      rows_sorted = sorted(rows, key=lambda a: a[3], reverse=True)
      print(tabulate(rows_sorted, headers=["player", "team", "pos", "cost", "status"] + self.scrapers + ["act."]))