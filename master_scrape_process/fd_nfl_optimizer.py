import datetime


def normalize_name(name):
    name_transform = {"Eli Mitchell": "Elijah Mitchell"}
    name = name.replace("  ", " ")
    name = name.replace("’", "'")
    parts = name.split(" ")
    if len(parts) > 2:
        return "{} {}".format(parts[0], parts[1])

    name = name.replace(".", "")
    if name in name_transform:
        return name_transform[name]

    return name

def get_all_players(player_to_fp, fd_slate_file_name):
    salaries = open(fd_slate_file_name)
    lines = salaries.readlines()
    found_count = 0
    all_players = []

    for line in lines[1:]:
        parts = line.split(',')
        full_name = parts[3]

        positions = parts[1].split("/")
        salary = parts[7]
        team = parts[9]
        status = parts[11]
        if status == "O":
            continue

        name = normalize_name(full_name)
        
        if name in player_to_fp:
            value = player_to_fp[name]
            found_count += 1

            
            for pos in positions:
                new_player = [name, pos, float(salary), team, value, round(value * 1000 / float(salary), 2)]
                all_players.append(new_player)

        else:
            print("Not found: {}".format(name))
            # name_parts = name.split(' ')
            # for search_name in player_to_fp.keys():
            #     if name_parts[0] in search_name:
            #         print("CANDIDATE: {} - {}".format(name, search_name))
            pass


        # print("{} - {}".format(name, positions))

        # new_player = Player(1)

    print(len(player_to_fp))
    print(found_count)
    import pdb; pdb.set_trace()
    # assert len(player_to_fp) == found_count
    # import pdb; pdb.set_trace()

    return all_players



today = datetime.datetime.now()

filepath = "money_line_scrape_{}_{}_2021.txt".format(today.month, today.day)

to_read = open(filepath)

player_to_fp = {}

lines = to_read.readlines()
for line in lines:
    parts = line.split("|")
    if len(parts) < 4:
        continue


    if parts[1]  == "PP-NFL" and parts[3] == "Fantasy Score":
        player_name = parts[2]
        player_name = normalize_name(player_name)
        if parts[4].strip() == "REMOVED":
            del player_to_fp[player_name]
            continue
        else:
            player_to_fp[player_name] = float(parts[4].strip())


print(player_to_fp)


path = "/Users/amichailevy/Downloads/player_lists/FanDuel-NFL-2021 ET-11 ET-21 ET-67063-players-list.csv"

result = get_all_players(player_to_fp, path)
print(result)

sorted_by_value = sorted(result, key=lambda a: a[5], reverse=True)

for a in sorted_by_value:
    print(a)
