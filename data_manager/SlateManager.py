import math
from NBA_WNBA_Projections import NBA_WNBA_Projections
from MLB_projections import MLBProjections
from Optimizer import FD_NBA_Optimizer, MLB_Optimizer
import random
import datetime
import utils
import statistics
from ScrapeProcessManager import run
# produce a table of projections
# generate an ensemble of rosters
# produce a file to upload


def parse_upload_template(csv_template_file, exclude, sport, offset = 0, entry_filter=None):
    template_file_lines = open(csv_template_file, "r").readlines()
    entries = []
    name_to_player_id = {}
    name_to_salary = {}
    player_id_to_name = {}
    player_id_to_fd_name = {}
    name_to_team = {}
    players_to_remove = []

    first_line = template_file_lines[0]
    for line in template_file_lines[1:]:
        parts = line.split(',')
        entry_id = parts[0].strip('"').strip()
        contest_id = parts[1].strip('"').strip()
        contest_name = parts[2].strip('"').strip()

        if entry_id != '' or contest_id != '' or contest_name != '':
            if entry_filter == None or entry_filter in contest_name:
                entries.append((entry_id, contest_id, contest_name))

        if len(parts) < 14:
            continue
    
        name_id = parts[13 - offset].strip('"').split(':')

        name_and_id = parts[13 - offset].strip('"')
        if len(name_id) == 1:
            continue
        injury_status = parts[25 - offset]

        player_id = name_id[0]
        fd_name = name_id[1]
        team = parts[23 - offset]
        salary = parts[21 - offset]
        name = utils.normalize_name(fd_name)

        name_to_player_id[name] = player_id
        name_to_team[name] = team
        name_to_salary[name] = salary

        player_id_to_name[player_id] = name
        
        player_id_to_fd_name[player_id] = name_and_id
        
        if name in exclude:
            players_to_remove.append(name)
            continue

        if sport == "MLB" and parts[30 - offset].strip() != "P" and parts[29 - offset] == '0':
          print("{} not in batting order".format(name))
          # __import__('pdb').set_trace()
          continue
        
        if injury_status == 'O' or injury_status == "IL" or injury_status == "NA":
            print("{} is OUT".format(name))
            players_to_remove.append(name)
            continue

    if len(player_id_to_name) == 0:
        # why??
        __import__('pdb').set_trace()

    return player_id_to_name, name_to_team, name_to_salary, name_to_player_id, first_line, entries, players_to_remove, player_id_to_fd_name


def construct_upload_template_file(rosters, first_line, entries, player_to_id, player_id_to_name):
    timestamp = str(datetime.datetime.now())
    date = timestamp.replace('.', '_')
    date = date.replace(":", "_")
    output_file = open("/Users/amichailevy/Downloads/upload_template_{}.csv".format(date), "x")
    output_file.write(first_line)
    entry_idx = 0
    for entry in entries:
        cells = [entry[0], entry[1], entry[2].strip('"')]
        if entry_idx >= len(rosters):
            break
        roster = rosters[entry_idx]
        players = roster.players
        player_cells = []
        for player in players:
            player_id = player_to_id[player.name]

            player_name = player_id_to_name[player_id]

            player_cells.append(player_name)

        # player_cells.reverse()
        cells += player_cells

        if len(cells) != 12:
            __import__('pdb').set_trace()

        to_write = ','.join(['"{}"'.format(c) for c in cells]) 

        output_file.write(to_write + "\n")
        entry_idx += 1
        

    output_file.close()



if __name__ == "__main__":
  run("MLB")

  download_folder = "/Users/amichailevy/Downloads/"
  slate_path = "FanDuel-MLB-2022 ET-05 ET-17 ET-76281-players-list.csv"
  template_path = "FanDuel-MLB-2022-05-17-76281-entries-upload-template.csv"


  projections = MLBProjections(download_folder + slate_path)
  projections.print_slate()

  by_position = projections.players_by_position()

  # dfs_crunch_path = "DFSCRUNCH-DOWNLOAD-DATA-fd76041 (2).csv"
  # by_position = utils.load_crunch_dfs_projection(dfs_crunch_path, slate_path, download_folder)
  all_teams = projections.all_teams


  player_id_to_name, _, _, name_to_player_id, first_line, entries, to_remove, player_id_to_fd_name = parse_upload_template(download_folder + template_path, [], '') #MLB


  entry_name_to_ct = {}
  for entry in entries:
    entry_name = entry[2]
    if not entry_name in entry_name_to_ct:
      entry_name_to_ct[entry_name] = 1
    else:
      entry_name_to_ct[entry_name] += 1

  rosters = []

  seen_team_keys = []
  # to_remove += ["Pavin Smith", "Jazz Chisholm", "Rougned Odor", "Yan Gomes", "Dylan Moore", "Brendan Rodgers", "Paul DeJong", "Austin Slater", "Randal Grichuk", "Frank Schwindel"]
  count = 0

  top_pitchers = sorted(by_position['P'], key=lambda a: a.value, reverse=True)[:3]
  pitcher_pool = []
  pitcher_pool += [top_pitchers[0]] * 10
  pitcher_pool += [top_pitchers[1]] * 6
  pitcher_pool += [top_pitchers[2]] * 4

  team_to_batters = {}
  for pos, players in by_position.items():
    if pos == "P":
      continue
    for player in players:
      team = player.team
      if not team in team_to_batters:
        team_to_batters[team] = []
      
      existing_names = [a.name for a in team_to_batters[team]]
      if player.name in existing_names:
        continue
      team_to_batters[team].append(player)

  team_to_ave_hitter_output = []
  for team, players in team_to_batters.items():
    ave_output = statistics.mean([a.value for a in players])
    team_to_ave_hitter_output.append((team, ave_output))
  
  team_to_ave_hitter_output_sorted = sorted(team_to_ave_hitter_output, key=lambda a: a[1], reverse=True)
  teams = [a[0] for a in team_to_ave_hitter_output_sorted]
  # __import__('pdb').set_trace()
  #TODO find a better way of dohing this?
  # teams = teams[:math.ceil(len(teams) / 2)]
  teams = teams[:10]

  team_selection_pool = []
  team_idx = len(teams)
  for team in teams:
    team_selection_pool += [team] * team_idx

    team_idx -= 1


  # 50 entries
  # plan 3 pictures
  # for each pitcher - 20 team combinations
  # select random teams - but not if they're playing against this pitcher!
  # don't hit against my pitcher

  while len(rosters) < len(entries):
    pitcher = random.sample(pitcher_pool, 1)[0]
    top_3_teams = random.sample(team_selection_pool, 3)
    count = 0
    while len(top_3_teams) != len(set(top_3_teams)) or pitcher.opp in top_3_teams:
      top_3_teams = random.sample(team_selection_pool, 3)
      count += 1
      if count > 50:
        __import__('pdb').set_trace()

    accepted_teams = top_3_teams
    team_key = "|".join(sorted(accepted_teams))
    if team_key in seen_team_keys:
      continue

    seen_team_keys.append(team_key)

    print("LOCKING PITCHER: {}".format(pitcher))
    print("Accepted teams: {}".format(accepted_teams))
    assert pitcher.opp not in accepted_teams

    by_position_new = {}
    for position, players in by_position.items():
      by_position_new[position] = []
      for player in players:
        if not player.team in accepted_teams and position != "P":
          continue

        if player.name in to_remove:
          continue
        by_position_new[position].append(player)
    
    optimizer = MLB_Optimizer()
    seed_roster = [pitcher] + [""] * 8
    # __import__('pdb').set_trace()
    # iter_count = 9500
    # iter_count = 11000
    iter_count = 8300
    result = optimizer.optimize(by_position_new, iter_count=iter_count, seed_roster=seed_roster)
    if result == None:
      print("Null roster skipping.")
      continue
    for pl in result.players:
      print(pl)

    team_ct = {}
    for player in result.players:
      if player.position == "P":
        continue
      pl_team = player.team
      if not pl_team in team_ct:
        team_ct[pl_team] = 1
      else:
        team_ct[pl_team] += 1

    if result.players[0].opp in accepted_teams:
      print("SKIPPING BECAUSE OF PITCHER MATCHUP!")
      # we locked the pitcher so this shouldn't happen
      __import__('pdb').set_trace()
      continue

    if max(team_ct.values()) > 4:
      print("SKIPPING!")
      assert False

    rosters.append(result) 

    print("ROSTER COUNT: {}".format(len(rosters)))

    count += 1

  rosters_sorted = sorted(rosters, key=lambda a:a.value, reverse=True)[:len(entries)]
  to_print = []
  # distribute best roster to the single entry, and the rest to the MME
  take_idx = 0
  for entry in entries[:len(rosters_sorted)]:
    entry_name = entry[2]
    entry_ct = entry_name_to_ct[entry_name]
    if entry_ct == 1:
      to_print.append(rosters_sorted[0])
    else:
      to_print.append(rosters_sorted[take_idx])
      take_idx += 1

  construct_upload_template_file(to_print, first_line, entries, name_to_player_id, player_id_to_fd_name)
    
  # pick pairs and triples
  # filter out all other 

#
  