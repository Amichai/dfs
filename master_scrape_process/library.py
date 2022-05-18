import datetime
import unidecode
import json
from selenium import webdriver
import scrapers.caesars_scraper

dk_positions_mapper = {"PG": ["PG", "G", "UTIL"], "SG": ["SG", "G", "UTIL"], "SF": ["SF", "F", "UTIL"], "PF": ["PF", "F", "UTIL"], "C": ["C", "UTIL"]}

name_transform = {"Guillermo Hernangomez": 'Willy Hernangomez', "Cam Thomas": "Cameron Thomas", "Moe Harkless": 'Maurice Harkless', 'Juancho Hernangómez':"Juancho Hernangomez", "Guillermo Hernangómez": 'Willy Hernangomez', 'Timothé Luwawu-Cabarrot': 'Timothe Luwawu-Cabarrot', 'Enes Kanter': 'Enes Freedom', 'Kenyon Martin Jr.': 'KJ Martin', 'Nic Claxton': 'Nicolas Claxton', 'Kenyon Martin': 'KJ Martin', "Nah'Shon Hyland": 'Bones Hyland'}

def normalize_name(name):
    name = name.replace("  ", " ")
    name = name.replace("’", "'")
    name = name.replace(".", "")
    name = unidecode.unidecode(name)

    parts = name.split(" ")


    if name == 'Kenyon Martin Jr':
        return "KJ Martin"

    if len(parts) > 2:
        return "{} {}".format(parts[0], parts[1]).strip()

    if name in name_transform:
        return name_transform[name].strip()

    return name.strip()


def load_start_times_and_slate_path(path):
    start_times = open(path, "r")
    lines = start_times.readlines()
    fd_slate_path = lines[0].strip()
    dk_slate_path = lines[1].strip()
    first_team = None
    second_team = None
    time_conversion = {
        '12:00pm ET': 0, '12:30pm ET': 0.5,
        '1:00pm ET': 1, '1:30pm ET': 1.5,
        '2:00pm ET': 2, '2:30pm ET': 2.5,
        '3:00pm ET': 3, '3:30pm ET': 3.5,
        '4:00pm ET': 4, '4:30pm ET': 4.5,
        '5:00pm ET': 5, '5:30pm ET': 5.5,
        '6:00pm ET': 6, '6:30pm ET': 6.5, 
        '7:00pm ET': 7, '7:30pm ET': 7.5, 
        '8:00pm ET': 8, '8:30pm ET': 8.5, 
        '9:00pm ET': 9, '9:30pm ET': 9.5, 
        '10:00pm ET': 10, '10:30pm ET': 10.5, 
        '11:00pm ET': 11, '11:30pm ET': 11.5}

    time_to_teams = {}
    for line in lines[2:]:
        line = line.strip().strip('\n')

        if line == "":
            continue

        if line[0].isdigit():
            time_key = time_conversion[line]
            if not time_key in time_to_teams:
                time_to_teams[time_key] = []
            time_to_teams[time_key] += [first_team, second_team]
            continue

        if line[0] == '@':
            # second team
            second_team = line.strip('@')
            continue

        first_team = line

    return (time_to_teams, fd_slate_path, dk_slate_path)

team_transform = {"NYK": "NY", "GSW": "GS", "PHX": "PHO", "SAS": "SA", "NOP": "NO"}

def normalize_team_name(team):
    if team in team_transform:
        return team_transform[team]

    return team


def get_fd_slate_players(fd_slate_file_path, exclude_injured_players=True):
    all_players = {}
    salaries = open(fd_slate_file_path)
    lines = salaries.readlines()

    for line in lines[1:]:
        parts = line.split(',')
        full_name = normalize_name(parts[3])

        positions = parts[1]
        salary = parts[7]
        team = parts[9]
        team = normalize_team_name(team)
        status = parts[11]
        # print(full_name)
        if status == "O" and exclude_injured_players:
            continue
        name = full_name
        all_players[name] = [name, positions, float(salary), team, status]
        
    return all_players


def get_dk_slate_players(dk_slate_file_name):
    all_players = {}
    #'SG/SF,Rodney Hood (20071564),Rodney Hood,20071564,SG/SF/F/G/UTIL,3000,MIL@PHI 11/09/2021 07:30PM ET,MIL,8.88\n'
    all_lines = open(dk_slate_file_name,  encoding="ISO-8859-1").readlines()
    for line in all_lines[1:]:
        parts = line.split(",")
        positions = parts[0]
        name = normalize_name(parts[2])
        salary = parts[5]
        game_info = parts[6]
        team = parts[7]
        team = normalize_team_name(team)

        player_id = parts[3]
        all_players[name] = [name, positions, float(salary), team, player_id]

    return all_players

def get_fd_slate_players(dk_slate_file_name):
    all_players = {}
    #'SG/SF,Rodney Hood (20071564),Rodney Hood,20071564,SG/SF/F/G/UTIL,3000,MIL@PHI 11/09/2021 07:30PM ET,MIL,8.88\n'
    all_lines = open(dk_slate_file_name,  encoding="ISO-8859-1").readlines()
    for line in all_lines[1:]:
        parts = line.split(",")
        positions = parts[1]
        name = normalize_name(parts[3])
        salary = parts[7]
        game_info = parts[8]
        team = parts[9]
        team = normalize_team_name(team)

        player_id = parts[0]
        all_players[name] = [name, positions, float(salary), team, player_id]

    return all_players

def output_file_path(name):
  return open("/Users/amichailevy/Downloads/lineups_{}_{}.csv".format(datetime.datetime.now().strftime('%Y%m%d-%H%M%S'), name), "w")

def get_output_headers(sport):
  if sport == "nba":
    return "PG,SG,SF,PF,C,G,F,UTIL\n"
  elif sport == "mlb":
    return "P,P,C,1B,2B,3B,SS,OF,OF,OF\n"
  elif sport == "mlb_single_game":
    return "CPT,UTIL,UTIL,UTIL,UTIL,UTIL\n"
  elif sport == "el":
    return "G,G,F,F,F,UTIL\n"
  elif sport == "epl":
     return "F,F,M,M,D,D,GK,UTIL\n"
  elif sport == "PGA":
     return "G,G,G,G,G,G\n"
  pass

def generate_dk_lineups_file(rosters, dk_players, name, sport):
    output_file = output_file_path(name)
    output_file.write(get_output_headers(sport))
    for roster in rosters:
        all_ids = []
        for player in roster.players:
            name = player.name
            player_id = dk_players[name][4]
            all_ids.append(player_id)
            
        output_file.write(",".join(all_ids) + "\n")
    output_file.close()

def generate_lineups_file_from_dfs_cruncher_response(response, name, sport):
  output_file = output_file_path(name)

  output_file.write(get_output_headers(sport))
  as_json = json.loads(response)
  roster = as_json["roster"]
  players = roster['players']
  all_ids = []
  for player in players:
    player_id = player['id']
    all_ids.append(player_id)
        
  output_file.write(",".join(all_ids) + "\n")
  output_file.close()

  pass

def get_dfs_cruncher_slate_projections(path):
    lines = open(path, "r").readlines()
    name_to_projection = {}

    for line in lines[1:]:
        parts = line.split(',')
        name = parts[0].strip('"')
        name = normalize_name(name)
        projection = float(parts[1].strip('"'))
        # if projection == 0:
        #     continue

        name_to_projection[name] = projection

    return name_to_projection


def produce_projections_from_caesars_scrape(caesars_fdp_projections):
    player_to_fp = {}
    player_to_stat_to_value = {}

    for name, stats in caesars_fdp_projections.items():
        player_name = normalize_name(name).strip()
        for stat, val in stats.items():
            if val == "REMOVED":
                continue
            value = float(val)
            if not player_name in player_to_stat_to_value:
                player_to_stat_to_value[player_name] = {}

            if not stat in player_to_stat_to_value[player_name]:
                player_to_stat_to_value[player_name][stat] = {}

            player_to_stat_to_value[player_name][stat] = value
    
    for player, stat_to_values in player_to_stat_to_value.items():
        if not "Points" in stat_to_values:
            continue
        pts = stat_to_values['Points']
        if not 'Rebounds' in stat_to_values:
            continue
        rbds = stat_to_values['Rebounds']
        if not 'Assists' in stat_to_values:
            continue
        asts = stat_to_values['Assists']
        if not 'Blocks' in stat_to_values:
            continue
        blks = stat_to_values['Blocks']
        if not 'Steals' in stat_to_values:
            continue
        stls = stat_to_values['Steals']
        turnovers = stat_to_values["Turnovers"]

        projected = pts + rbds * 1.2 + asts * 1.5 + blks * 3 + stls * 3 - (turnovers / 3.0)

        player_to_fp[player] = projected
    
    return player_to_fp
        

def scrape_caesars_money_lines():
    driver = webdriver.Chrome("../master_scrape_process/chromedriver7")
    results = scrapers.caesars_scraper.query_betCaesars(driver)
    driver.close()
    return results
    

class Player:
    def __init__(self, name, position, cost, team, value, game_start_slot=0, matchup=''):
        self.name = name
        self.position = position
        self.cost = float(cost)
        self.team = team
        self.value = float(value)
        self.value_per_dollar = self.value * 100 / self.cost
        self.game_start_slot = game_start_slot
        self.matchup = matchup

    def __repr__(self):
        # return "{} - {} - {} - {} - {} - {}".format(self.name, self.position, self.cost, self.team, self.value, self.value_per_dollar)
        return self.name