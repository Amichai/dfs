from secrets import token_hex
import utils

copied_lines = open('PGA_copied_lines.txt', "r").readlines()

import itertools

def best_roster(name_to_line, name_to_salary):
  all_names = name_to_line.keys()

  result = itertools.combinations(all_names, 6)

  best_rosters = []

  best_val = 1e9

  for r in result:
    cost = sum([name_to_salary[name] for name in r])

    if cost > 60000:
      continue

    value = sum(name_to_line[name] for name in r)

    if value <= best_val:
      # print((r, value, cost))
      best_val = value


      best_rosters.append((r, value, cost))

  best_rosters_sorted = sorted(best_rosters, key=lambda a: a[1], reverse=True)
  return best_rosters_sorted


directory = "/Users/amichailevy/Downloads/"
all_players = utils.get_fd_slate_players(directory + 'FanDuel-PGA-2022 ET-10 ET-12 ET-81688-players-list.csv')

name_to_salary = {}
for player, player_info in all_players.items():
  name_to_salary[player] = player_info[2]

names = []
lines = []

for i in range(len(copied_lines)):
  if i % 3 == 0:
    names.append(copied_lines[i].strip())
  if i % 3 == 2:
    lines.append(float(copied_lines[i].strip()))

assert len(names) == len(lines)

player_to_value = {}

name_transform = {
  "Cam Davis": "Cameron Davis",
  "Si Woo Kim": "Si Woo",
  "KH Lee":"Kyoung-Hoon Lee",
  'J.T. Poston': "JT Poston",
  'J.J. Spaun': 'JJ Spaun',
  'Byeong Hun An':'Byeong Hun',
  'SH Kim':'Seonghyeon Kim',
  'Xue-wen Luo': 'Xue-Wen Luo'
}


to_exclude = []
# to_exclude = ['Xander Schauffele', 'Sungjae Im']

for i in range(len(names)):
  name = names[i]
  name = utils.normalize_name(name)
  if name in name_transform:
    name = name_transform[name]

  if name in to_exclude:
    continue

  value = lines[i]

  if value >= 15000:
    continue

  player_to_value[name] = value

rosters_sorted = best_roster(player_to_value, name_to_salary)

print(rosters_sorted[0])
