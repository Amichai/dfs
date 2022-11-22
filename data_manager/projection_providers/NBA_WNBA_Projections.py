from data_manager import DataManager
from decimal import Decimal
import json
import datetime
import boto3

import random
from table import Table
from tabulate import tabulate
import utils

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
    self.scrapers = ['PP', 'Caesars', 'NumberFire', "FantasyData", "DFSCrunch"]
    
    self.dk_players = utils.get_dk_slate_players(slate_path)
    self.name_to_player_id = {}

  def get_player_rows(self):
    all_rows = []

    for player, info in self.dk_players.items():
      position = info[1]
      cost = float(info[2])
      team = info[3]
      self.name_to_player_id[player] = info[4]

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
      dfs_crunch_proj = row[8]
      caesars_is_active = row[-1]

      value = 0
      if int(caesars_is_active) >= 3:
        value = caesars_proj
      elif pp_proj != '':
        value = pp_proj
      else:
        # TODO VALIDATE THIS CHANGE!
        value = dfs_crunch_proj

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

    self.fd_players = utils.get_fd_slate_players(slate_path, exclude_injured_players=False)

  def validate_player_set(self):
    # return
    # for each player that we have a projection in the database for, make sure we have a corresponding player
    all_players = self.all_players()
    all_player_names = [p.name for p in all_players]
    for scraper in self.scrapers:
      all_projections = self.dm.query_all_projections(self.sport, scraper)
      if all_projections == None:
        continue
      names = all_projections.keys()
      for name in names:
        if not name in all_player_names:
          # pass
          projection_values = list(all_projections[name]['projections'].values())
          all_zero = all([x == 0 for x in projection_values])
          if not all_zero:
            # __import__('pdb').set_trace()
            print("PLAYER WITH PROJECTION NOT FOUND in slate: {} - {}".format(name, all_projections[name]))


  def write_player_projections_to_db(self):
    all_rows = []
  
    for player, info in self.fd_players.items():
      cost = float(info[2])
      player_row = [info[0], info[1], cost, info[3], info[5]]
      projection = ''
      site = "dfsc"
      
      projections = self.dm.query_projection(self.sport, "DFSCrunch", player)
      if projections != None:
        projection = parse_fantasy_score_from_projections("DFSCrunch", projections)

      projections = self.dm.query_projection(self.sport, "PP", player)
      if projections != None:
        pp_proj = parse_fantasy_score_from_projections("PP", projections)
        if pp_proj != '':
          projection = pp_proj
          site = "pp"
      
      # caesars
      projections = self.dm.query_projection(self.sport, "Caesars", player)
      if projections != None:
        caesars_proj = parse_fantasy_score_from_projections("Caesars", projections)
        activity_metric = parse_caesaers_projection_activity_metric(projections)
        if activity_metric >= 3:
          projection = caesars_proj
          site = "caesars"

      projection = float(projection)
      if projection != '' and projection > 17:
        if site == "dfsc":
          # salt the dfsc projection
          projection += random.uniform(0, 0.4) - 0.25
          projection = round(projection, 2)
        if site == "PP":
          projection += random.uniform(0, 0.22) - 0.11
          projection = round(projection, 2)


        player_row.append(projection)
        all_rows.append(player_row)
    
    dynamodb = boto3.resource('dynamodb')
    projections = dynamodb.Table('MLE_Projections')
    timestamp = str(datetime.datetime.now())
    date = timestamp.split(' ')[0]
    to_write = {
        'Date': date,
        'date-site-slateid': '{}-{}-{}'.format(date, 'fd', utils.TODAYS_SLATE_ID_NBA),
        'timestamp': timestamp,
        'site': 'fd',
        'projections': json.dumps(all_rows)
    }
    to_write = json.loads(json.dumps(to_write), parse_float=Decimal)
    try:
        result = projections.put_item(
          Item=to_write
        )
        print("UPLOADED PROJECTIONS!")
    except Exception as err:
        print("Error:", err)


    return all_rows

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

  def all_players(self):
    by_position = self.players_by_position()
    all_players = []
    all_names = []
    for pos, players in by_position.items():
      for player in players:
        name = player.name
        if name in all_names:
          continue

        all_names.append(name)
        all_players.append(player)


    return all_players


  def name_to_player(self):
    all_players = self.all_players()
    name_to_player = {}
    for player in all_players:
      name_to_player[player.name] = player

    return name_to_player


  def get_name_to_team(self):
    name_to_team = {}
    all_rows = self.get_player_rows()
    for row in all_rows:
      name = row[0]
      team = row[1]
      name_to_team[name] = team

    return name_to_team


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
        value = dfs_crunch

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
