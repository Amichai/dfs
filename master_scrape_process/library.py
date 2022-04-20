


name_transform = {"Guillermo Hernangomez": 'Willy Hernangomez', "Cam Thomas": "Cameron Thomas", "Moe Harkless": 'Maurice Harkless', 'Juancho Hernangómez':"Juancho Hernangomez", "Guillermo Hernangómez": 'Willy Hernangomez', 'Timothé Luwawu-Cabarrot': 'Timothe Luwawu-Cabarrot', 'Enes Kanter': 'Enes Freedom', 'Kenyon Martin Jr.': 'KJ Martin', 'Nic Claxton': 'Nicolas Claxton', 'Kenyon Martin': 'KJ Martin', "Nah'Shon Hyland": 'Bones Hyland'}

def normalize_name(name):
    name = name.replace("  ", " ")
    name = name.replace("’", "'")
    name = name.replace(".", "")
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
  slate_path = lines[0].strip()
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
  for line in lines[1:]:
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

  return (time_to_teams, slate_path)

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
