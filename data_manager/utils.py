import json
import datetime
from selenium import webdriver
import unidecode
from name_mapper import name_mapper
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
import csv

TODAYS_SLATE_ID_NBA = "85468"
TODAYS_SLATE_ID_NFL = "85186"

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
  return webdriver.Chrome("../master_scrape_process/chromedriver12")

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

team_transform = {"NYK": "NY", "GSW": "GS", "PHX": "PHO", "SAS": "SA", "NOP": "NO", 'JAX': 'JAC'}
def normalize_team_name(team):
    if team in team_transform:
        return team_transform[team]

    return team


# def get_fd_slate_players(fd_slate_file_path, exclude_injured_players=True):
#   all_players = {}
#   salaries = open(fd_slate_file_path)
#   lines = salaries.readlines()

#   for line in lines[1:]:
#     parts = line.split(',')
#     full_name = normalize_name(parts[3])

#     positions = parts[1]
#     salary = parts[7]
#     team = parts[9]
#     opp_team = parts[10]
#     team = normalize_team_name(team)
#     status = parts[11]
#     if status == "O" and exclude_injured_players:
#         continue

#     probablePitcher = parts[14]
#     if positions == 'P' and probablePitcher != "Yes":
#         continue

#     name = full_name
#     all_players[name] = [name, positions, float(salary), team, opp_team, status]
      
#   return all_players


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

def single_game_optimizer_many(by_position, ct, locks=None):
    all_players = []
    seen_names = []

    for _, players in by_position.items():
        for player in players:
            if player.name in seen_names:
                continue
            all_players.append(player)
            seen_names.append(player.name)
    
    player_ct = len(all_players)
    all_rosters = []

    roster_keys = set()
    for i1 in range(player_ct):
        p1 = all_players[i1]
        if locks != None and p1.name != locks[i1]:
            continue

        for i2 in range(player_ct):
            if i2 == i1:
                continue
            p2 = all_players[i2]

            if locks != None and p2.name != locks[i2]:
                continue


            for i3 in range(player_ct):
                if i3 == i1 or i3 == i2:
                    continue
                
                p3 = all_players[i3]
                if locks != None and p3.name != locks[i3]:
                    continue

                for i4 in range(player_ct):
                    if i4 == i1 or i4 == i2 or i4 == i3:
                        continue
                    
                    p4 = all_players[i4]
                    if locks != None and p4.name != locks[i4]:
                        continue

                    for i5 in range(player_ct):
                        if i5 == i1 or i5 == i2 or i5 == i3 or i5 == i4:
                            continue
                        
                        p5 = all_players[i5]

                        if locks != None and p5.name != locks[i5]:
                            continue
                        roster_set = [p1, p2, p3, p4, p5]
                        
                        total_cost = sum(pl.cost for pl in roster_set)
                        if total_cost > 60000 or total_cost <= 59000:
                            continue
                        
                        total_value = p1.value * 2 + p2.value * 1.5 +  p3.value * 1.2 + p4.value + p5.value

                        if all(x.team == roster_set[0].team for x in roster_set):
                            continue

                        roster_key = "|".join(sorted([a.name for a in roster_set])) + "|" + str(round(total_value, 1))
                        if roster_key in roster_keys:
                            continue

                        roster_keys.add(roster_key)
                        all_rosters.append((roster_set, total_value, total_cost))
    all_rosters_sorted = sorted(all_rosters, key=lambda a: a[1], reverse=True)
    to_return = all_rosters_sorted[:ct]
    for roster in to_return:
        print(roster)
        
    return to_return

DOWNLOAD_FOLDER = "/Users/amichailevy/Downloads/"


def load_start_times_and_slate_path(path):
    start_times = open(path, "r")
    lines = start_times.readlines()
    player_list = lines[0].strip()
    fd_slate_path = lines[1].strip()
    dk_slate_path = lines[2].strip()
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
        '7:15pm ET': 7.15, '7:45pm ET': 7.85,
        '8:00pm ET': 8, '8:30pm ET': 8.5, 
        '8:15pm ET': 8.15, '8:45pm ET': 8.85,
        '8:20pm ET': 8.2,
        '9:00pm ET': 9, '9:30pm ET': 9.5, 
        '9:15pm ET': 9.15, '9:45pm ET': 9.85,
        '10:00pm ET': 10, '10:30pm ET': 10.5, 
        '10:15pm ET': 10.15, '10:45pm ET': 10.85,
        '11:00pm ET': 11, '11:30pm ET': 11.5,
        '11:15pm ET': 11.15
    }

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

    return (time_to_teams, player_list, fd_slate_path, dk_slate_path)

#UNMODIFIED STATS: [ 'Pass+Rush+Rec TDs', 'Rec TDs', 'Rush TDs', 'Tackles+Ast']


stat_name_normalization = {
    # Thrive Fantasy
    'HITs': 'Hits',
    'RUNs': 'Runs Scored',
    'BASEs': 'Bases',
    'Total Bases': 'Bases',
    'Ks': 'Pitching Strikeouts',

    "HITs + RBIs + RUNs": "Hits + Runs + RBIs",
    "Hits+Runs+RBIS": "Hits + Runs + RBIs",


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

    "3-PT Made": "3-Pointers Made",
    'FT Made': 'Free Throws Made',


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

def get_player_exposures(rosters_sorted):
    player_to_ct = {}
    for roster in rosters_sorted:
        for player in roster.players:
            if not player.name in player_to_ct:
                player_to_ct[player.name] = 1
            else:
                player_to_ct[player.name] += 1
    
    return player_to_ct

def print_player_exposures(rosters_sorted, locked_teams=None):
    print("print player exposures")
    name_to_player = {}
    max_ct = 0
    player_to_ct = {}
    for roster in rosters_sorted:
        for player in roster.players:
            if not player.name in player_to_ct:
                player_to_ct[player.name] = 1
                name_to_player[player.name] = player
                if max_ct == 0:
                    max_ct = 1
            else:
                player_to_ct[player.name] += 1
                new_ct = player_to_ct[player.name]
                if new_ct > max_ct:
                    max_ct = new_ct




    player_to_ct_sorted = sorted(player_to_ct.items(), key=lambda a: a[1], reverse=True)
    print(player_to_ct_sorted)

    rows = []
    for player_name, ct in player_to_ct.items():
        pl = name_to_player[player_name]
        if pl.value == 0:
            continue
        if locked_teams != None and pl.team in locked_teams:
            continue
        rows.append([player_name, ct, pl.team, round(pl.value, 2)])

    rows_sorted = sorted(rows, key=lambda a: a[1], reverse=True)
    idx = 1
    rows_sorted_with_idx = []
    for row in rows_sorted:
        new_row = [idx] + row
        rows_sorted_with_idx.append(new_row)
        idx += 1
    print(tabulate(rows_sorted_with_idx, headers=["idx", "name", "ct", "team", "value"]))

    print("CORE!!")
    for player_name, ct in player_to_ct.items():
        if ct == 0:
            continue
        exposure = round(ct / max_ct, 1)
        if exposure >= 0.8:
            player = name_to_player[player_name]
            print("{}, {} - {} ({})".format(player.name, player.team, round(player.value, 2), round(player.value_per_dollar, 2)))

    return player_to_ct

def print_roster_time_distribution(rosters, start_times):
    team_to_start_time = {}
    start_time_to_start_idx = {}

    all_start_times = sorted(list(start_times.keys()))
    for i in range(len(all_start_times)):
        start_time_to_start_idx[all_start_times[i]] = i

    start_idx_to_ct = {}

    for time, teams in start_times.items():
        for team in teams:
            team_to_start_time[team] = time
    for roster in rosters:
        for player in roster.players:
            team = player.team
            start_time = team_to_start_time[team]
            start_idx = start_time_to_start_idx[start_time]
            if not start_time in start_idx_to_ct:
                start_idx_to_ct[start_time] = player.value
            else:
                start_idx_to_ct[start_time] += player.value
    
    start_idx_to_ct_sorted = sorted(start_idx_to_ct.items(), key=lambda a: a[0])
    for start_idx_ct in start_idx_to_ct_sorted:
        val = start_idx_ct[1]
        val = round(val / 1000, 1)
        print("{} - {}".format(start_idx_ct[0], val))

def print_roster_variation(rosters):
    key_to_ct = {}
    for roster in rosters:
        if isinstance(roster, list):
            names1 = [p.name for p in roster[0].players]
        else:
            names1 = [p.name for p in roster.players]
        roster_key = ",".join(sorted(names1))
        if not roster_key in key_to_ct:
            key_to_ct[roster_key] = 1
        else:
            key_to_ct[roster_key] += 1
    
    just_cts = key_to_ct.values()
    to_return = sorted(just_cts, reverse=True)
    print(to_return)
    return to_return


def parse_projection_from_caesars_lines(lines):
    if not "Points" in lines:
        return
    pts = float(lines['Points'])
    if not 'Rebounds' in lines:
        return
    rbds = float(lines['Rebounds'])
    if not 'Assists' in lines:
        return
    asts = float(lines['Assists'])
    if not 'Blocks' in lines:
        return
    blks = float(lines['Blocks'])
    if not 'Steals' in lines:
        return
    stls = float(lines['Steals'])
    turnovers = float(lines["Turnovers"])
    projected = pts + rbds * 1.2 + asts * 1.5 + blks * 3 + stls * 3 - (turnovers / 3.0)

    a1 = False
    a2 = False
    a3 = False
    a4 = False
    a5 = False

    if "Points:isActive" in lines:
        a1 = lines["Points:isActive"]
    
    if "Assists:isActive" in lines:
        a2 = lines["Assists:isActive"]
    
    if "Rebounds:isActive" in lines:
        a3 = lines["Rebounds:isActive"]
    
    if "Blocks:isActive" in lines:
        a4 = lines["Blocks:isActive"]

    if "Steals:isActive" in lines:
        a5 = lines["Steals:isActive"]

    total = [a1, a2, a3, a4, a5]
    activity = len([a for a in total if a])

    return [round(projected, 2), activity]

def get_dk_slate_players(dk_slate_path, is_showdown=False):
    all_players = {}
    #'SG/SF,Rodney Hood (20071564),Rodney Hood,20071564,SG/SF/F/G/UTIL,3000,MIL@PHI 11/09/2021 07:30PM ET,MIL,8.88\n'
    all_lines = open(dk_slate_path,  encoding="ISO-8859-1").readlines()
    for line in all_lines[1:]:
        parts = line.split(",")
        positions = parts[0]
        name = normalize_name(parts[2])
        salary = parts[5]
        game_info = parts[6]
        team = parts[7]
        team = normalize_team_name(team)

        roster_position = parts[4]
        if is_showdown and roster_position == "CPT":
            continue

        both_teams = game_info.split(' ')[0].split('@')
        if team == both_teams[0]:
            opp = both_teams[1]
        else:
            opp = both_teams[0]

        player_id = parts[3]
        all_players[name] = [name, positions, float(salary), team, player_id, opp]

    return all_players

def get_dk_slate_game_info(dk_slate_path):
    game_infos = []
    seen_games = []
    all_lines = open(dk_slate_path,  encoding="ISO-8859-1").readlines()
    for line in all_lines[1:]:
        parts = line.split(",")
        game_info = parts[6]
        start_time = game_info.split(' ')[2]
        if not game_info in seen_games:
            game_infos.append((game_info, start_time))
            seen_games.append(game_info)

    game_infos_sorted = sorted(game_infos, key=lambda a: a[1])
    to_return = [a[0] for a in game_infos_sorted]

    return to_return

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
        if status == "O" and exclude_injured_players:
            continue
        name = full_name
        fd_player_id = parts[0]
        all_players[name] = [name, positions, float(salary), team, status, fd_player_id]
        
    return all_players

def construct_dk_output_single_game(rosters, name_to_player_id, entries_path, file_suffix = '', sport= "NBA", should_sort_by_entry_fee=True):
    file = open(entries_path)
    file_reader = csv.reader(file, delimiter=',', quotechar='"')
    prefix_cells = []
    first_line = True
    for cells in file_reader:
        if first_line:
            first_line = False
            continue
        
        if cells[0] == '':
            continue
        row_prefix = [cells[0], cells[1], cells[2], cells[3]]
        prefix_cells.append(row_prefix)
        
    # prices = [float(a[3][1:]) for a in prefix_cells]
    if should_sort_by_entry_fee:
        prefix_cells = sorted(prefix_cells, key=lambda a: float(a[3][1:]), reverse=True)
    timestamp = str(datetime.datetime.now())
    date = timestamp.replace('.', '_')
    date = date.replace(":", "_")

    output_file = open("/Users/amichailevy/Downloads/DK_upload_template_single_game_{}_{}.csv".format(date, file_suffix), "x")
    
    if sport == "NFL":
        first_line = "Entry ID,Contest Name,Contest ID,Entry Fee,CPT,FLEX,FLEX,FLEX,FLEX,FLEX\n"
    else:
        first_line = "Entry ID,Contest Name,Contest ID,Entry Fee,CPT,UTIL,UTIL,UTIL,UTIL,UTIL\n"

    output_file.write(first_line)
    
    idx = 0
    for roster in rosters:
        if idx > len(prefix_cells) - 1:
            break
        cells = prefix_cells[idx]
        if cells[0] == '':
            continue
        for player in roster:
            player_id = name_to_player_id[player.name]
            cells.append(player_id)
        idx += 1
        roster_val = candidate_value(roster)
        cells.append(str(roster_val))
        active_player_ct = len([a for a in roster if a != 0])
        val_per_player = roster_val / active_player_ct
        total_cost = sum([a.value for a in roster if a != 0])
        cost_per_player = total_cost / active_player_ct
        cells.append(str(round(val_per_player / cost_per_player * 100, 2)))
        cells.append(str(candidate_cost(roster)))

        output_file.write(",".join(cells) + "\n")

    output_file.close()

    return idx

def construct_dk_output_template(rosters, name_to_player_id, entries_path, file_suffix = '', sport= "NBA", should_sort_by_entry_fee=True):

    file = open(entries_path)
    file_reader = csv.reader(file, delimiter=',', quotechar='"')
    prefix_cells = []
    first_line = True
    for cells in file_reader:
        if first_line:
            first_line = False
            continue
        
        if cells[0] == '':
            continue
        row_prefix = [cells[0], cells[1], cells[2], cells[3]]
        prefix_cells.append(row_prefix)
        
    # prices = [float(a[3][1:]) for a in prefix_cells]
    if should_sort_by_entry_fee:
        prefix_cells = sorted(prefix_cells, key=lambda a: float(a[3][1:]), reverse=True)
    timestamp = str(datetime.datetime.now())
    date = timestamp.replace('.', '_')
    date = date.replace(":", "_")

    output_file = open("/Users/amichailevy/Downloads/DK_upload_template_{}_{}.csv".format(date, file_suffix), "x")
    
    first_line = "Entry ID,Contest Name,Contest ID,Entry Fee,PG,SG,SF,PF,C,G,F,UTIL\n"
    if sport == "NFL":
        first_line = "Entry ID,Contest Name,Contest ID,Entry Fee,QB,RB,RB,WR,WR,WR,TE,FLEX,DST\n"
    output_file.write(first_line)
    
    idx = 0
    for roster in rosters:
        if idx > len(prefix_cells) - 1:
            break
        cells = prefix_cells[idx]
        if cells[0] == '':
            continue
        if isinstance(roster, list):
            idx += 1
            continue
        for player in roster.players:
            player_id = name_to_player_id[player.name]
            cells.append(player_id)
        idx += 1
        cells.append(str(roster.value))
        active_player_ct = len([a for a in roster.players if a != 0])
        val_per_player = roster.value / active_player_ct
        total_cost = sum([a.value for a in roster.players if a != 0])
        cost_per_player = total_cost / active_player_ct
        # __import__('pdb').set_trace()
        cells.append(str(val_per_player / cost_per_player * 100))

        output_file.write(",".join(cells) + "\n")

    output_file.close()

    return idx

def construct_dk_showdown_output_template(rosters, name_to_player_id, entries_path, file_suffix = '', sport= "NBA"):
    file = open(entries_path)
    file_reader = csv.reader(file, delimiter=',', quotechar='"')
    prefix_cells = []
    first_line = True
    for cells in file_reader:
        if first_line:
            first_line = False
            continue

        row_prefix = [cells[0], cells[1], cells[2], cells[3]]
        prefix_cells.append(row_prefix)


    timestamp = str(datetime.datetime.now())
    date = timestamp.replace('.', '_')
    date = date.replace(":", "_")

    output_file = open("/Users/amichailevy/Downloads/DK_showdown_upload_template_{}_{}.csv".format(date, file_suffix), "x")
    
    first_line = "Entry ID,Contest Name,Contest ID,Entry Fee,CPT,UTIL,UTIL,UTIL,UTIL,UTIL\n"

    output_file.write(first_line)
    
    idx = 0
    for roster in rosters:
        cells = prefix_cells[idx]
        if cells[0] == '':
            continue
        for player in roster[0]:
            player_id = name_to_player_id[player]
            cells.append(player_id)
        idx += 1
        cells.append(str(roster[2]))
        

        output_file.write(",".join(cells) + "\n")

    output_file.close()

    return idx

def get_player_name_to_start_time(start_times, projections):
    name_to_team = projections.get_name_to_team()
    team_to_time = {}

    for st_time, teams in start_times.items():
        for team in teams:
            team_to_time[team] = st_time

    player_to_start_time = {}
    for name, team in name_to_team.items():
        player_to_start_time[name] = team_to_time[team]

    return player_to_start_time


import os
def most_recently_download_filepath(*name_contains):
    most_recent_path = None
    most_recent_timestamp = 0
    # assign directory
    directory = DOWNLOAD_FOLDER
    
    # iterate over files in
    # that directory
    for filename in os.listdir(directory):
        if not all([a in filename for a in name_contains]):
            continue
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            modified = os.path.getmtime(f)
            if most_recent_path == None or modified > most_recent_timestamp:
                most_recent_path = f
                most_recent_timestamp = modified

    # TODO print the time difference (how long ago this was added) and assert it's within a reasonable range
    print("MOST RECENT: {} ({})".format(most_recent_path, round(most_recent_timestamp)))
    if most_recent_path == None:
        print(name_contains)
        __import__('pdb').set_trace()
    assert most_recent_path != None
    return most_recent_path

import boto3
from decimal import Decimal
def write_to_db(table_name, to_write):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    to_write = json.loads(json.dumps(to_write), parse_float=Decimal)
    try:
        result = table.put_item(
          Item=to_write
        )
        print("UPLOADED TO TABLE: {}!".format(table_name))
    except Exception as err:
        print("Error:", err)

def candidate_value(candidate):
    return candidate[0].value * 1.5 + candidate[1].value + candidate[2].value + candidate[3].value + candidate[4].value + candidate[5].value

def candidate_cost(candidate):
    return candidate[0].cost * 1.5 + candidate[1].cost + candidate[2].cost + candidate[3].cost + candidate[4].cost + candidate[5].cost