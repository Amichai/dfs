import json
import datetime
from selenium import webdriver
import unidecode


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
      return "{} {}".format(parts[0], parts[1]).strip()

  name = name.replace(".", "")

  return name.strip()

# https://chromedriver.chromium.org/downloads
# xattr -d com.apple.quarantine <chromedriver>
def get_chrome_driver():
  return webdriver.Chrome("../master_scrape_process/chromedriver10")

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
