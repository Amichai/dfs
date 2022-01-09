import datetime
from os import path

def load_projections():
    current_date = datetime.datetime.now()
    output_file_name = "money_line_scrape_{}_{}_{}.txt".format(current_date.month, current_date.day, current_date.year)

    output_file = open(output_file_name, "r")

    sites = {}

    lines = output_file.readlines()
    for line in lines:
        parts = line.split("|")
        if len(parts) < 4:
            continue
        site = parts[1]
        if not site in sites:
            sites[site] = {}

        player_name = parts[2]
        if not player_name in sites[site]:
            sites[site][player_name] = {}
        val = parts[5].strip()
        if val == "REMOVED":
            if stat in sites[site][player_name]:
                del sites[site][player_name][stat]
            continue
        stat = parts[4]
        sites[site][player_name][stat] = str(val)

    return sites


# get the teams
# get the projections for each team

slate_string = """
T. Herro

J. Brunson

D. Garland

PROJECTED

124.3 ‒ 124.1

STARTS IN: 00:04:37:54

M. Brogdon

C. Paul

D. Fox
"""

lines = slate_string.split('\n')
all_players = []
for line in lines:
    line = line.strip()
    if line == '':
        continue

    if "FLEX" in line or "PROJECTED" in line:
        continue

    if any(char.isdigit() for char in line):
        continue

    all_players.append(line)

team_size = int(len(all_players) / 2)
team1 = all_players[:team_size]
team2 = all_players[team_size:]

def get_player_val(search_name, dict):
    for name, val in dict.items():
        if name == search_name:
            return float(val['Fantasy Score'])


    candidates = []
    parts = search_name.split(' ')
    for name, val in dict.items():
        if name[0] == parts[0][0] and parts[1] in name:
            candidates.append((name, val['Fantasy Score']))
    
    if len(candidates) != 1:
        __import__('pdb').set_trace()

    if isinstance(candidates[0][1], type(dict)):
        __import__('pdb').set_trace()

    # __import__('pdb').set_trace()
    return float(candidates[0][1])



sites = load_projections()

player_to_projection = {}
for player in all_players:
    caesars = sites["caesars-Projected"]
    player_to_projection[player] = get_player_val(player, caesars)

team1_score = sum([player_to_projection[a] for a in team1])
team2_score = sum([player_to_projection[a] for a in team2])

print("{} - {}".format(team1, team1_score))
print("{} - {}".format(team2, team2_score))

__import__('pdb').set_trace()