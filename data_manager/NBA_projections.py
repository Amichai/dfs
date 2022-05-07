from data_manager import DataManager
from tabulate import tabulate
import utils

def get_fd_slate_players(fd_slate_file_path, exclude_injured_players=True):
  all_players = {}
  salaries = open(fd_slate_file_path)
  lines = salaries.readlines()

  for line in lines[1:]:
      parts = line.split(',')
      full_name = utils.normalize_name(parts[3])

      positions = parts[1]
      salary = parts[7]
      team = parts[9]
      team = utils.normalize_team_name(team)
      status = parts[11]
      if status == "O" and exclude_injured_players:
          continue
      name = full_name
      all_players[name] = [name, positions, float(salary), team, status]
      
  return all_players

def parse_fantasy_score_from_projections(sport, site, projections):
  if site == "PP":
    if "Fantasy Score" not in projections:
      return ''
    return projections["Fantasy Score"]
  elif site == "DFSCrunch":
    return projections["Fantasy Score"]
  elif site == "Caesars":
    if not "Points" in projections:
        return
    pts = float(projections['Points'])
    if not 'Rebounds' in projections:
        return
    rbds = float(projections['Rebounds'])
    if not 'Assists' in projections:
        return
    asts = float(projections['Assists'])
    if not 'Blocks' in projections:
        return
    blks = float(projections['Blocks'])
    if not 'Steals' in projections:
        return
    stls = float(projections['Steals'])
    turnovers = float(projections["Turnovers"])
    projected = pts + rbds * 1.2 + asts * 1.5 + blks * 3 + stls * 3 - (turnovers / 3.0)
    return round(projected, 2)

def parse_caesaers_projection_activity_metric(caesars_projection):
  if caesars_projection == None:
    return 0
  a1 = caesars_projection["Points:isActive"]
  a2 = caesars_projection["Assists:isActive"]
  a3 = caesars_projection["Rebounds:isActive"]
  a4 = caesars_projection["Blocks:isActive"]
  a5 = caesars_projection["Steals:isActive"]

  total = [a1, a2, a3, a4, a5]
  return len([a for a in total if a])

class NBAProjections:
  def __init__(self, slate_path):
    self.dm = DataManager()
    self.sport = 'NBA'
    self.scrapers = ['DFSCrunch', 'PP', 'Caesars']

    self.fd_players = get_fd_slate_players(slate_path, exclude_injured_players=False)

  def print_slate(self):
    team_to_players = {}

    for player, info in self.fd_players.items():
      position = info[1]
      cost = float(info[2])
      team = info[3]
      status = info[4]

      player_row = [player, position, cost, status]

      scraper_to_projections = {}


      for scraper in self.scrapers:
        projections = self.dm.query_projection(self.sport, scraper, player)
        scraper_to_projections[scraper] = projections
        projection = ''
        if projections != None:
          projection = parse_fantasy_score_from_projections(self.sport, scraper, projections)
        player_row.append(projection)


      player_row.append(parse_caesaers_projection_activity_metric(scraper_to_projections["Caesars"]))
      if not team in team_to_players:
        team_to_players[team] = []

      team_to_players[team].append(player_row)

    for team, rows in team_to_players.items():
      print("TEAM: {}".format(team))

      rows_sorted = sorted(rows, key=lambda a: a[2], reverse=True)
      print(tabulate(rows_sorted, headers=["player", "pos", "cost", "status"] + self.scrapers + ["act."]))
