from data_manager import DataManager
from tabulate import tabulate
import utils
import csv

def get_fd_slate_players(fd_slate_file_path, exclude_injured_players=True):
  all_players = {}
  salaries = open(fd_slate_file_path)
  salaries_reader = csv.reader(salaries, delimiter=',', quotechar='"')
  first_line = True
  for parts in salaries_reader:
    if first_line:
      first_line = False
      continue

    full_name = utils.normalize_name(parts[3])

    positions = parts[1]
    salary = parts[7]
    status = parts[11]

    if status == "O" and exclude_injured_players:
        continue
    name = full_name

    all_players[name] = [name, positions, float(salary), '', status]

  return all_players

def parse_fantasy_score_from_projections(site, projections):
  if site == "PP" or "RotoWire":
    if "Fantasy Score" not in projections:
      return ''
    return projections["Fantasy Score"]

class NASCAR_Projections:
  def __init__(self, slate_path, sport):
    self.dm = DataManager(sport)
    self.sport = sport
    self.scrapers = ['PP', 'RotoWire']

    self.fd_players = get_fd_slate_players(slate_path, exclude_injured_players=False)


  def get_player_rows(self):
    all_rows = []

    for player, info in self.fd_players.items():
      position = info[1]
      cost = float(info[2])
      team = info[3]
      status = info[4]

      player_row = [player, team, position, cost, status]

      scraper_to_projections = {}

      for scraper in self.scrapers:

        projections = self.dm.query_projection(self.sport, scraper, player)
        scraper_to_projections[scraper] = projections

        projection = ''
        if projections != None:
          projection = parse_fantasy_score_from_projections(scraper, projections)
        player_row.append(projection)

      all_rows.append(player_row)

    return all_rows

  def players_by_position(self):
    by_position = {'FLEX': []}
    all_rows = self.get_player_rows()
    for row in all_rows:
      name = row[0]
      team = row[1]
      pos = row[2]
      cost = row[3]
      status = row[4]
      pp_proj = row[5]
      value = pp_proj

      if value == '':
        continue

      value = float(value)

      # TODO - figure this out
      # if value == 0:
      #   continue
      
      positions = pos.split('/')
      for position in positions:
        if not position in by_position:
          by_position[position] = []
        by_position[position].append(utils.Player(name, position, cost, team, value))

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
