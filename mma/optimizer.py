
directory = "/Users/amichailevy/Downloads/"


def parse_entries():
  entries_filename = "DKEntries (1).csv"
  entries_lines = open(directory + entries_filename, "r").readlines()

  entries = []

  for line in entries_lines[1:]:
    parts = line.split(',')
    
    entry_id = parts[0]
    if entry_id == '':
      continue
    entry_name = parts[1]
    contest_id = parts[2]
    entry_fee = parts[3]

    entries.append([entry_id, entry_name, contest_id, entry_fee])

  entries.reverse()

  return entries


def parse_salaries():
  salaries_filename = "DKSalaries_mma1.csv"
  salaries_lines = open(directory + salaries_filename, "r").readlines()

  name_mappings = {
    'Heili Alatengheili': 'Heili Alateng',
    'Li Jingliang': 'Jingliang Li',
  }

  name_to_salary = {}
  name_to_id = {}
  for line in salaries_lines[1:]:
    parts = line.split(',')
    name = parts[2]
    salary = float(parts[5])


    if name in name_mappings:
      name = name_mappings[name]

    name_to_salary[name] = salary
    name_to_id[name] = parts[3]

  return name_to_salary, name_to_id

name_to_salary, name_to_id = parse_salaries()

entries = parse_entries()

def parse_name_to_value():
  copied_lines = open('copied_lines.txt', "r").readlines()

  fighter1_names = []
  fighter2_names = []
  fighter1_lines = []
  fighter2_lines = []


  line_number = 0
  for line in copied_lines:
    line = line.strip()
    if (line_number - 2) % 9 == 0:
      fighter1_names.append(line)
    if (line_number - 3) % 9 == 0:
      fighter2_names.append(line)
    
    if (line_number - 6) % 9 == 0:
      fighter1_lines.append(line)
    if (line_number - 8) % 9 == 0:
      fighter2_lines.append(line)
    
    # print(9 % line_number - 3)
    line_number += 1

  fighter_to_opp = {}

  name_to_line = {}
  for i in range(len(fighter1_names)):
    name1 = fighter1_names[i]
    line1 = fighter1_lines[i]
    name2 = fighter2_names[i]
    line2 = fighter2_lines[i]

    fighter_to_opp[name1] = name2
    fighter_to_opp[name2] = name1

    if not name1 in name_to_salary:
      __import__('pdb').set_trace()
    if not name2 in name_to_salary:
      __import__('pdb').set_trace()

    name_to_line[name1] = float(line1)
    name_to_line[name2] = float(line2)

  print(name_to_line)

  return name_to_line, fighter_to_opp

name_to_line, fighter_to_opp = parse_name_to_value()

def parse_name_to_value_pp():
  pp_values = open('prize_picks_lines.txt', "r").readlines()

  fighter_names = []
  fighter_values = []


  line_number = 0
  for line in pp_values:
    line = line.strip()
    if (line_number - 1) % 7 == 0:
      fighter_names.append(line)
    if (line_number - 5) % 7 == 0:
      fighter_values.append(line)
  
    
    # print(9 % line_number - 3)
    line_number += 1

  to_return = {}
  for i in range(len(fighter_names)):
    to_return[fighter_names[i]] = float(fighter_values[i])

  return to_return

parsed_values = parse_name_to_value_pp()


import itertools

def best_roster(name_to_line):
  all_names = name_to_line.keys()

  result = itertools.combinations(all_names, 6)

  best_rosters = []

  for r in result:
    cost = sum([name_to_salary[name] for name in r])
    is_valid = True
    for fighter in r:
      opp = fighter_to_opp[fighter]
      if opp in r:
        is_valid = False
        break

    if not is_valid:
      continue

    if cost > 50000:
      continue

    value = sum(name_to_line[name] for name in r)
    # if value < -1000:
    best_rosters.append((r, value, cost))

  best_rosters_sorted = sorted(best_rosters, key=lambda a: a[1], reverse=True)
  return best_rosters_sorted

# best_rosters_sorted = best_roster(name_to_line)
best_rosters_sorted = best_roster(parsed_values)

print(best_rosters_sorted[0])

assert False

def write_all_rosters():
  file = open(directory + "all_rosters.csv", "w")
  file.write("F,F,F,F,F,F\n")

  for roster in best_rosters_sorted[:150]:
    print(roster)
    player_ids = [name_to_id[name] for name in roster[0]]
    row = ",".join(player_ids) + "\n"

    file.write(row)

  file.close()

# write_all_rosters()
# assert False

file = open(directory + "upload_file2.csv", "w")


file.write("Entry ID,Contest Name,Contest ID,Entry Fee,F,F,F,F,F,F\n")

rosters_to_write = best_rosters_sorted[:150]

__import__('pdb').set_trace()

entry_ct = 0
for entry in entries:
  roster = rosters_to_write[entry_ct % 150]
  print("{} - {}, {}".format(roster[0], roster[1], roster[2]))

  player_ids = [name_to_id[name] for name in roster[0]]

  entry_info = "{},{},{},{},".format(entry[0], entry[1], entry[2], entry[3])
  row = entry_info + ",".join(player_ids) + "\n"

  file.write(row)


  entry_ct += 1
  pass
  

file.close()
#----



# question - what percentage of the field took daniel rodriguez?