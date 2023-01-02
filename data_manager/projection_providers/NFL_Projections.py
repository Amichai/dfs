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
    opp = parts[10]
    opp = utils.normalize_team_name(opp)
    status = parts[11]
    if status == "O" and exclude_injured_players:
        continue
    name = full_name
    if positions == "D":
      name = team
    all_players[name] = [name, positions, float(salary), team, status, opp]

  return all_players

def parse_fantasy_score_from_projections(site, projections):
  if site == "PP" or site == 'NumberFire' or site == "DFSCrunch":
    if "Fantasy Score" not in projections:
      return ''
    return projections["Fantasy Score"]

team_to_defense_name = {
  "PIT": "Steelers DST",
  "SF": "49ers DST",
  "DEN": "Broncos DST",
  "CLE": "Browns DST",
  "LAR": "Rams DST",
  "BAL": "Ravens DST",
  "DAL": "Cowboys DST",
  "IND": "Colts DST",
  "TB": "Buccaneers DST",
  "CAR": "Panthers DST",
  "NYJ": "Jets DST",
  "MIA": "Dolphins DST",
  "NO": "Saints DST",
  "WAS": "Commanders DST",
  "CIN": "Bengals DST",
  "LV": "Raiders DST",
  "NE": "Patriots DST",
  "ARI": "Cardinals DST",
  "DET": "Lions DST",
  "HOU": "Texans DST",
  "ATL": "Falcons DST",
  "SEA": "Seahawks DST",
  "JAC": "Jaguars DST",
  "NYG": "Giants DST",
  "CHI": "Bears DST",
  "MIN": "Vikings DST",
  "BUF": "Bills DST",
  "LAC": "Chargers DST",
  "TEN": "Titans DST",
  "KC": "Chiefs DST",
  "GB": "Packers DST",
  "PHI": "Eagles DST",

   "Steelers": "Steelers DST",
"49ers": "49ers DST",
 "Broncos": "Broncos DST",
 "Browns": "Browns DST",
 "Rams": "Rams DST",
 "Ravens": "Ravens DST",
 "Cowboys": "Cowboys DST",
 "Colts": "Colts DST",
"Buccaneers": "Buccaneers DST",
 "Panthers": "Panthers DST",
 "Jets": "Jets DST",
 "Dolphins": "Dolphins DST",
"Saints": "Saints DST",
 "Commanders": "Commanders DST",
 "Bengals": "Bengals DST",
"Raiders": "Raiders DST",
"Patriots": "Patriots DST",
 "Cardinals": "Cardinals DST",
 "Lions": "Lions DST",
 "Texans": "Texans DST",
 "Falcons": "Falcons DST",
 "Seahawks": "Seahawks DST",
 "Jaguars": "Jaguars DST",
 "Giants": "Giants DST",
 "Bears": "Bears DST",
 "Vikings": "Vikings DST",
 "Bills": "Bills DST",
 "Chargers": "Chargers DST",
 "Titans": "Titans DST",
"Chiefs": "Chiefs DST",
"Packers": "Packers DST",
 "Eagles": "Eagles DST",
}

class NFL_Projections:
  def __init__(self, slate_path, sport, player_adjustments = {}):
    self.dm = DataManager(sport)
    self.sport = sport
    self.scrapers = ['PP', 'DFSCrunch']
    self.player_adjustments = player_adjustments
    self.fd_players = get_fd_slate_players(slate_path, exclude_injured_players=False)
    
  def get_player_rows(self):
    all_rows = []

    for player, info in self.fd_players.items():
      position = info[1]
      cost = float(info[2])
      team = info[3]
      status = info[4]
      opp = info[5]

      player_row = [player, team, position, cost, status, opp]

      scraper_to_projections = {}

      for scraper in self.scrapers:
        # print(" -- {}".format(player))
        if position == "D":
          if not player in team_to_defense_name:
            # print("----{} - {}".format(team, player))
            continue

          player = team_to_defense_name[player]
          # print("- {}".format(team))

        projections = self.dm.query_projection(self.sport, scraper, player)
        scraper_to_projections[scraper] = projections

        if position == "D" and projections == None:
          __import__('pdb').set_trace()

        projection = ''
        if projections != None:
          projection = parse_fantasy_score_from_projections(scraper, projections)
        player_row.append(projection)

      all_rows.append(player_row)

    return all_rows

  def players_by_position(self, exclude_zero_value = True):
    by_position = {'FLEX': []}
    all_rows = self.get_player_rows()
    for row in all_rows:
      name = row[0]
      team = row[1]
      pos = row[2]
      cost = row[3]
      status = row[4]
      opp = row[5]
      pp_proj = row[6]
      dfscrunch_proj = ''

      if len(row) > 7:
        dfscrunch_proj = row[7]
      
      if pp_proj != '' and pp_proj != 0:
        value = pp_proj
      else:
        value = dfscrunch_proj

      if not value:
        value = pp_proj

      if name in self.player_adjustments:
        new_value = value * self.player_adjustments[name]
        print("{} ADJUSTED: {} -> {}".format(name, value, new_value))
        value = new_value


      if value == '':
        continue

      value = float(value)

      if exclude_zero_value and value == 0:
        continue
      
      positions = pos.split('/')
      for position in positions:
        if not position in by_position:
          by_position[position] = []
        by_position[position].append(utils.Player(name, position, cost, team, value, opp))

        if pos != "D" and pos != "QB":
          by_position["FLEX"].append(utils.Player(name, position, cost, team, value, opp))



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
      print(tabulate(rows_sorted, headers=["player", "team", "pos", "cost", "status", "opp"] + self.scrapers + ["act."]))

class NFL_Projections_dk:
  def __init__(self, slate_path, sport, player_adjustments = {}):
    self.dm = DataManager(sport)
    self.sport = sport
    self.scrapers = ['PP', 'DFSCrunch']
    self.player_adjustments = player_adjustments
    self.dk_players = utils.get_dk_slate_players(slate_path)
    self.name_to_player_id = {}

  def get_player_rows(self):
    all_rows = []

    for player, info in self.dk_players.items():
      position = info[1]
      if position == "DST":
        position = "D"
      cost = float(info[2])
      team = info[3]
      self.name_to_player_id[player] = info[4]
      opp = info[5]

      player_row = [player, team, position, cost, opp]
      scraper_to_projections = {}

      for scraper in self.scrapers:
        if position == "D":
          if not player in team_to_defense_name:
            pass
          else:
            player = team_to_defense_name[player]
            # __import__('pdb').set_trace()

            # print("----{} - {}".format(team, player))
            # continue

          # print("- {}".format(team))

        projections = self.dm.query_projection(self.sport, scraper, player)
        scraper_to_projections[scraper] = projections



        # if position == "D" and projections == None:
        #   __import__('pdb').set_trace()

        projection = ''
        if projections != None:
          projection = parse_fantasy_score_from_projections(scraper, projections)
        player_row.append(projection)

      all_rows.append(player_row)

    return all_rows

  def players_by_position(self, exclude_zero_value = True):
    by_position = {'FLEX': []}
    all_rows = self.get_player_rows()
    for row in all_rows:
      name = row[0]
      team = row[1]
      pos = row[2]
      cost = row[3]
      opp = row[4]
      pp_proj = row[5]
      dfscrunch_proj = ''

      if len(row) > 6:
        dfscrunch_proj = row[6]
      
      if pp_proj != '' and pp_proj != 0:
        value = pp_proj
      else:
        value = dfscrunch_proj

      if not value:
        value = pp_proj

      if name in self.player_adjustments:
        new_value = value * self.player_adjustments[name]
        print("{} ADJUSTED: {} -> {}".format(name, value, new_value))
        value = new_value

      positions = pos.split('/')

      if value == '':
        continue

      value = float(value)

      if exclude_zero_value and value == 0:
        continue
      
      for position in positions:
        if not position in by_position:
          by_position[position] = []
        by_position[position].append(utils.Player(name, position, cost, team, value, opp))

        if pos != "D" and pos != "QB":
          by_position["FLEX"].append(utils.Player(name, position, cost, team, value, opp))


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
      print(tabulate(rows_sorted, headers=["player", "team", "pos", "cost", "opp"] + self.scrapers + ["act."]))
