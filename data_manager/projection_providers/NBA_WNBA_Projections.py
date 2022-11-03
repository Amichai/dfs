from data_manager import DataManager
from tabulate import tabulate
import utils

def get_dk_slate_players(dk_slate_path):
  all_players = {}
  #'SG/SF,Rodney Hood (20071564),Rodney Hood,20071564,SG/SF/F/G/UTIL,3000,MIL@PHI 11/09/2021 07:30PM ET,MIL,8.88\n'
  all_lines = open(dk_slate_path,  encoding="ISO-8859-1").readlines()
  for line in all_lines[1:]:
      parts = line.split(",")
      positions = parts[0]
      name = utils.normalize_name(parts[2])
      salary = parts[5]
      game_info = parts[6]
      team = parts[7]
      team = utils.normalize_team_name(team)

      player_id = parts[3]
      all_players[name] = [name, positions, float(salary), team, player_id]

  return all_players

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

def parse_fantasy_score_from_projections(site, projections):
  if site == "NumberFire":
    if "Fantasy Score" not in projections:
      return ''

    return round(float(projections["Fantasy Score"]) * 0.95, 2)
  
  if site == "FantasyData":
    if "Fantasy Score" not in projections:
      return ''

    return round(float(projections["Fantasy Score"]) * 0.95, 2)

  if site == "RotoWire":
    if "Fantasy Score" not in projections:
      return ''

    return projections["Fantasy Score"]

  elif site == "PP":
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

  a1 = False
  a2 = False
  a3 = False
  a4 = False
  a5 = False

  if "Points:isActive" in caesars_projection:
    a1 = caesars_projection["Points:isActive"]
  
  if "Assists:isActive" in caesars_projection:
    a2 = caesars_projection["Assists:isActive"]
  
  if "Rebounds:isActive" in caesars_projection:
    a3 = caesars_projection["Rebounds:isActive"]
  
  if "Blocks:isActive" in caesars_projection:
    a4 = caesars_projection["Blocks:isActive"]

  if "Steals:isActive" in caesars_projection:
    a5 = caesars_projection["Steals:isActive"]

  total = [a1, a2, a3, a4, a5]
  return len([a for a in total if a])
  

class NBA_Projections_dk:
  def __init__(self, slate_path, sport):
    self.dm = DataManager(sport)
    self.sport = sport
    self.scrapers = ['PP', 'Caesars', 'NumberFire', "FantasyData"]
    
    self.dk_players = get_dk_slate_players(slate_path)

  def get_player_rows(self):
    all_rows = []

    for player, info in self.dk_players.items():
      position = info[1]
      cost = float(info[2])
      team = info[3]

      player_row = [player, team, position, cost]

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

  def players_by_position(self, exclude_zero_value=False):
    by_position = {'UTIL': []}
    all_rows = self.get_player_rows()
    for row in all_rows:
      name = row[0]
      team = row[1]
      pos = row[2]
      cost = row[3]
      pp_proj = row[4]
      caesars_proj = row[5]
      numberfire_proj = row[6]
      fantasy_data_proj = row[7]
      caesars_is_active = row[8]

      value = 0
      if int(caesars_is_active) >= 3:
        value = caesars_proj
      elif pp_proj != '':
        value = pp_proj
      else:
        # TODO VALIDATE THIS CHANGE!
        value = fantasy_data_proj

      if value == '':
        continue

      value = float(value)

      if exclude_zero_value and value == 0:
        continue
      
      position_mapper = {'PG' : 'G', 'SG': 'G', 'SF': 'F', 'PF' : 'F'}
      positions = pos.split('/')
      for position in positions:
        if not position in by_position:
          by_position[position] = []
        by_position[position].append(utils.Player(name, position, cost, team, value))
        by_position['UTIL'].append(utils.Player(name, position, cost, team, value))
        if position in position_mapper:
          mapped_position = position_mapper[position]
          if not mapped_position in by_position:
            by_position[mapped_position] = []
          by_position[mapped_position].append(utils.Player(name, position, cost, team, value))


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
      print(tabulate(rows_sorted, headers=["player", "team", "pos", "cost"] + self.scrapers + ["act."]))


class NBA_WNBA_Projections:
  def __init__(self, slate_path, sport):
    self.dm = DataManager(sport)
    self.sport = sport
    self.scrapers = ['DFSCrunch', 'PP', 'Caesars', 'RotoWire', 'NumberFire', "FantasyData"]

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

      player_row.append(parse_caesaers_projection_activity_metric(scraper_to_projections["Caesars"]))

      all_rows.append(player_row)

    return all_rows

  def players_by_position(self, exclude_zero_value=False):
    by_position = {}
    all_rows = self.get_player_rows()
    for row in all_rows:
      name = row[0]
      team = row[1]
      pos = row[2]
      cost = row[3]
      status = row[4]
      dfs_crunch = row[5]
      pp_proj = row[6]
      caesars_proj = row[7]
      rotowire_proj = row[8]
      numberfire_proj = row[9]
      fantasy_data_proj = row[10]
      caesars_is_active = row[11]

      value = 0
      if int(caesars_is_active) >= 3:
        value = caesars_proj
      elif pp_proj != '':
        value = pp_proj
      else:
        value = fantasy_data_proj

      if value == '':
        continue

      value = float(value)

      if exclude_zero_value and value == 0:
        continue
      
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
