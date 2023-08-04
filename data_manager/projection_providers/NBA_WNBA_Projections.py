from data_manager import DataManager
from decimal import Decimal
import json
import datetime
import boto3

import random
from table import Table
from tabulate import tabulate
import utils

def round_off(val):
  # return round(val, 2)
  return round(val * 2) / 2

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

  elif site == "DFSCrunch" or site == "Stokastic":
    if not "Fantasy Score" in projections:
      return ''
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

    turnovers = 0
    if 'Turnovers' in projections:
      turnovers = float(projections["Turnovers"])

    projected = pts + rbds * 1.2 + asts * 1.5 + blks * 3 + stls * 3 - (turnovers / 3.0)
    to_return = round(projected, 2)
    if to_return == None:
      __import__('pdb').set_trace()

    return round(projected, 2)
    # return round_off(projected)

def parse_fantasy_score_from_projections_dk(site, projections):
  if site == "Stokastic":
    return projections["dk_Fantasy Score"]
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
        if 'Blocks + Steals' in projections:
          __import__('pdb').set_trace()
          stls = float(projections['Blocks + Steals'] - blks)
        else:
          return
    else: 
      stls = float(projections['Steals'])
    turnovers = float(projections["Turnovers"])
    projected = pts + rbds * 1.25 + asts * 1.5 + blks * 2 + stls * 2 - (turnovers / 6.0) + 1.8
    return round(projected, 2)
    # return round_off(projected)

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
  def __init__(self, slate_path, sport, day=None):
    self.dm = DataManager(sport, day)
    self.sport = sport
    self.scrapers = ['Caesars', "Stokastic"]
    
    self.dk_players = utils.get_dk_slate_players(slate_path)
    self.name_to_player_id = {}
    self.player_id_to_name = {}

  def get_player_rows(self):
    all_rows = []

    for player, info in self.dk_players.items():
      position = info[1]
      cost = float(info[2])
      team = info[3]
      self.name_to_player_id[player] = info[4]
      self.player_id_to_name[info[4]] = player

      player_row = [player, team, position, cost]

      scraper_to_projections = {}

      for scraper in self.scrapers:
        projections = self.dm.query_projection(self.sport, scraper, player)
        scraper_to_projections[scraper] = projections
        projection = ''
        if projections != None:
          projection = parse_fantasy_score_from_projections_dk(scraper, projections)

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
      caesars_proj = row[4]
      stokastic_proj = row[5]
      caesars_is_active = row[-1]

      value = 0
      if int(caesars_is_active) >= 4:
        value = caesars_proj
      else:
        # TODO VALIDATE THIS CHANGE!
        value = stokastic_proj

      if value == '':
        value = 0
        # continue
      
      if value == None:
        __import__('pdb').set_trace()

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
  def __init__(self, slate_path, sport, date=None):
    self.dm = DataManager(sport, date)
    self.sport = sport
    self.scrapers = ['DFSCrunch', 'PP', 'Caesars', "Stokastic"]

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


  def filter_out_low_value_players(self, all_rows):
    to_return = all_rows
    all_value_per_dollars = sorted([(row[5] / row[2] ) for row in all_rows], reverse=True)
    cuttof_idx = 65
    if len(all_value_per_dollars) > cuttof_idx:
      cuttoff = all_value_per_dollars[cuttof_idx - 1]
      to_return = [row for row in all_rows if row[5] / row[2] >= cuttoff]

    return to_return

    

  def write_player_projections_to_db(self):
    all_rows = []
  
    for player, info in self.fd_players.items():
      cost = float(info[2])

      player_row = [info[0], info[1], cost, info[3], info[5]]
      projection = ''
      site = "Stokastic"
      
      projections = self.dm.query_projection(self.sport, "Stokastic", player)
      if projections != None:
        projection = parse_fantasy_score_from_projections("Stokastic", projections)

      projections = self.dm.query_projection(self.sport, "PP", player)
      if projections != None:
        pp_proj = parse_fantasy_score_from_projections("PP", projections)
        if pp_proj != '' and pp_proj != 0:
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

      # TODO: automate the setting of this parameter
      if projection == '' or projection < 14:
        continue

      projection = float(projection)
      if site == "Stokastic":
        projection = round(projection * 2) / 2
      
      player_row.append(projection)
      all_rows.append(player_row)
    
    # all_rows = self.filter_out_low_value_players(all_rows)
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

  # def get_optimal_ownership_stokastic()

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


  def players_by_position(self, exclude_zero_value=False, proj_adjust={}):
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
      stokastic = row[8]
      caesars_is_active = row[9]

      projection_source = ''

      value = 0
      if int(caesars_is_active) >= 4:
        value = caesars_proj
        projection_source = "Caesars"
      elif pp_proj != '' and pp_proj != 0:
        value = pp_proj
        projection_source = "PP"
      else:
        value = stokastic
        projection_source = "Stokastic"
        # if stokastic != '':
        # else: 
        #   value = dfs_crunch
      
      # __import__('pdb').set_trace()

      # if "Ayton" in name:
      #   __import__('pdb').set_trace()

      if value == '':
        value = 0
        # continue

      if value == None:
        print("{} - NO PROJECTION: {}".format(projection_source, name))
        # __import__('pdb').set_trace()
        continue

      value = float(value)

      # if projection_source == "Stokastic":
      #   value *= 0.97

      optimal_ownership = 0
      ceiling = 0
      stddev = 0
      stokastic_projection = self.dm.query_projection(self.sport, "Stokastic", name)
      if stokastic_projection != None and 'optimal' in stokastic_projection:
        optimal_ownership = float(stokastic_projection['optimal'])
        ceiling = float(stokastic_projection['ceiling'])
        stddev = float(stokastic_projection['stddev'])

      # if optimal_ownership < 1.0 and optimal_ownership != 0:
      # #  and projection_source == "Stokastic":
      #   continue


      # if projection_source == "Stokastic":
      #   continue
      # __import__('pdb').set_trace()
      if name in proj_adjust:
        value *= proj_adjust[name]

      # less_than_5 = min(0, optimal_ownership - 5)
      # value += less_than_5

      if exclude_zero_value and value == 0:
        continue

      positions = pos.split('/')
      for position in positions:
        if not position in by_position:
          by_position[position] = []
        by_position[position].append(utils.Player(name, position, cost, team, value, projection_source="{}, {}, {} - {}".format(optimal_ownership, ceiling, stddev, projection_source)))

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
