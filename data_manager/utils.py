import json
import datetime
from selenium import webdriver
import unidecode
from name_mapper import name_mapper
import requests
from bs4 import BeautifulSoup


class Player:
    def __init__(self, name, position, cost, team, value, opp=None):
        self.name = name
        self.position = position
        self.cost = float(cost)
        self.team = team
        self.value = float(value)
        self.opp = opp
        self.value_per_dollar = self.value * 100 / self.cost

    def __repr__(self):
        return "{} - {} - {}".format(self.name, self.value, self.team)


class Roster:
  def __init__(self, players):
      self.players = players
      self.cost = sum([float(p.cost) for p in self.players])
      self.value = sum([float(p.value) for p in self.players])
      self.locked_indices = []

  def __repr__(self):
      return ",".join([p.name for p in self.players]) + " {} - {}".format(self.cost, self.value)

  def remaining_funds(self, max_cost):
      return max_cost - self.cost

  def replace(self, player, idx):
      self.players[idx] = player
      self.cost = sum([float(p.cost) for p in self.players])
      self.value = sum([float(p.value) for p in self.players])

  def at_position(self, position):
      return [p for p in self.players if p.position == position]

  def get_ids(self, id_mapping):
      ids = []
      for p in self.players:
          id = id_mapping[p.name]
          ids.append(id)

      ids.reverse()
      return ",".join(ids)


def normalize_name(name):
    name = unidecode.unidecode(name)
    name = name.replace("  ", " ")
    name = name.replace("’", "'")
    parts = name.split(" ")
    if len(parts) > 2:
        name = "{} {}".format(parts[0], parts[1]).strip()

    name = name.replace(".", "")
    if name in name_mapper:
        print("mapping: {}".format(name))
        name = name_mapper[name]

    return name.strip()

def get_request(url):
    r = requests.get(url)
    return r.json()

def get_request_beautiful_soup(url):
    r = requests.get(url)
    return BeautifulSoup(r.text, 'lxml')

# https://chromedriver.chromium.org/downloads
# xattr -d com.apple.quarantine <chromedriver>
def get_chrome_driver():
  return webdriver.Chrome("../master_scrape_process/chromedriver11")

def get_with_selenium(url):
  driver = get_chrome_driver()

  driver.get(url)
  as_text = driver.find_element_by_tag_name('body').text
  as_json = json.loads(as_text)
  driver.close()

  return as_json

def full_date_str():
    return str(datetime.datetime.now()).split('.')[0]

def date_str():
  return full_date_str().split(' ')[0]

def get_team_names():
  return open('team_names.txt', "r").readlines()

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
    opp_team = parts[10]
    team = normalize_team_name(team)
    status = parts[11]
    if status == "O" and exclude_injured_players:
        continue

    probablePitcher = parts[14]
    if positions == 'P' and probablePitcher != "Yes":
        continue

    name = full_name
    all_players[name] = [name, positions, float(salary), team, opp_team, status]
      
  return all_players


def load_crunch_dfs_projection(path, slate_path, download_folder):
    lines = open(download_folder + path, "r").readlines()

    fd_players = get_fd_slate_players(download_folder + slate_path, exclude_injured_players=False)

    by_position = {"UTIL": [], 'C/1B': []}

    for line in lines[1:]:
        parts = line.split(',')
        name = parts[0].strip('"')
        name = normalize_name(name)
        value = float(parts[1].strip('"'))
        if value == 0:
            continue
        if not name in fd_players:
            print("Missing from dk slate: {} - {}".format(name, value))
            continue
        player_info = fd_players[name]
        pos = player_info[1]
        cost = player_info[2]
        team = player_info[3]

        positions = pos.split('/')
        for position in positions:
            if not position in by_position:
                by_position[position] = []
            if position != 'P':
                by_position['UTIL'].append(Player(name, position, cost, team, value))
            if position == 'C' or position == '1B':
                by_position['C/1B'].append(Player(name, position, cost, team, value))
            else:
                by_position[position].append(Player(name, position, cost, team, value))

    __import__('pdb').set_trace()
    return by_position


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
        '4:05pm ET': 4.02,
        '4:25pm ET': 4.48,
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

#UNMODIFIED STATS: [ 'Pass+Rush+Rec TDs', 'Rec TDs', 'Rush TDs', 'Tackles+Ast']


stat_name_normalization = {
    # Thrive Fantasy
    'HITs': 'Hits',
    'RUNs': 'Runs Scored',
    'BASEs': 'Bases',
    'Ks': 'Pitching Strikeouts',
    'Pass YDS': 'Passing Yards',
    'Pass Yards': 'Passing Yards',
    'Rush YDS': 'Rushing Yards',
    'Rush Yards': 'Rushing Yards',
    'Rec YDS': 'Receiving Yards',
    'Rec Yards': 'Receiving Yards',
    'Pass YDS + Rush YDS': 'Pass+Rush Yards',
    'Pass+Rush Yds': 'Pass+Rush Yards',
    'Rush YDS + Rec YDS': 'Rush+Rec Yards',
    'Rush+Rec Yds': 'Rush+Rec Yards',
    
    'REC': 'Receptions',
    'INT': 'Interceptions',

    'Rushing + Receiving Yards': 'Rush+Rec Yards',
    'Pass TDs': 'Passing Touchdowns',
    "Pass TD's": 'Passing Touchdowns',
    'Rush TDs': 'Rushing Touchdowns',
    "Rush TD's": 'Rushing Touchdowns',
    'Rushing TDs': 'Rushing Touchdowns',
    "Rushing TD's": 'Rushing Touchdowns',
    'Rush Attempts': 'Rushing Attempts',
    'Pass Attempts': 'Passing Attempts',
    'FG Made': 'Made Field Goals',
    'Pass Completions': 'Passing Completions',
    'CMP': 'Passing Completions',

    'Tackles+Ast': 'Defensive Tackles + Assists',

    # PP
    'Strikeouts': 'Pitching Strikeouts',
    'Hits Allowed': 'Hits Allowed',
    'Walks Allowed': 'Walks Allowed',
    'Runs': 'Runs Scored',
    'Pitching Outs': 'Outs Recorded',
    'Pitch Count': 'Pitches Thrown',
    'Hitter Fantasy Score': 'Fantasy Points',
    'Pitcher Fantasy Score': 'Fantasy Points',

    'Shots': 'Shots On Goal',
    'Saves': 'Goalie Saves',

    'Pass+Rush+Rec TDs': 'Total TDs',

    'PTS': 'Points',
    'ASTS': 'Assists',
    'PTS + ASTS': 'Points + Assists',
    'PTS + REBS': 'Points + Rebounds',
    'REBS': 'Rebounds',
    'PTS + REBS + ASTS': 'Points + Rebounds + Assists',
    'Points + Assists + Rebounds': 'Points + Rebounds + Assists',
    'Pts + Rebs + Asts': 'Points + Rebounds + Assists',
    'REBS + ASTS': 'Rebounds + Assists',
    'BLKS': 'Blocks',
    'BLKS + STLS': 'Blocks + Steals',
    'STLS': 'Steals',

    'Pts+Rebs': 'Points + Rebounds',
    'Pts+Asts': 'Points + Assists',
    'Rebs+Asts': 'Rebounds + Assists',
    'Blks+Stls':'Blocks + Steals',
    'Pts+Rebs+Asts': 'Points + Rebounds + Assists',
    'Blocked Shots': 'Blocks',


    #UNMODIFIED STATS: ['Turnovers', '3-PT Made', 'Pts+Rebs', 'Rebs+Asts', 'Pts+Asts', 'Blks+Stls', 'Pts+Rebs+Asts', 'Fantasy Score', 'Blocked Shots']

}

def normalize_stat_name(scraper_results):
    mapping_values = list(stat_name_normalization.values())
    mapping_keys = list(stat_name_normalization.keys())
    unmodified_stats = []

    results_new = {}
    for player, stats in scraper_results.items():
        results_new[player] = {}
        for stat, val in stats.items():
            if stat in stat_name_normalization:
                stat = stat_name_normalization[stat]

            if ':isActive' in stat:
                stat_prefix = stat.replace(':isActive', '')
                if stat_prefix in stat_name_normalization:
                    stat = stat_name_normalization[stat_prefix] + ':isActive'
            
            if stat not in mapping_values and stat not in mapping_keys and stat not in unmodified_stats and ':isActive' not in stat:
                unmodified_stats.append(stat)


            results_new[player][stat] = val

    print("UNMODIFIED STATS: {}".format(unmodified_stats))
    return results_new


def percentChange(v1, v2):
    diff = v2 - v1
    if diff == 0:
        return 0

    return diff / (v1 + 0.01)

def print_player_exposures(rosters_sorted):
  player_to_ct = {}
  for roster in rosters_sorted:
    for player in roster.players:
      if not player.name in player_to_ct:
        player_to_ct[player.name] = 1
      else:
        player_to_ct[player.name] += 1

  player_to_ct_sorted = sorted(player_to_ct.items(), key=lambda a: a[1], reverse=True)
  print(player_to_ct_sorted)