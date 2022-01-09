

path = "pp_log.txt"

to_read = open(path, "r")

lines = to_read.readlines()

player_to_fdp = {}

current_player = None
for line in lines: 
    if line[:3] == " # ":
        # print(line)
        current_player = line.strip().strip(" # ")
        # print(current_player)

    if ("new stat" in line or "new: " in line) and "Fantasy Score" in line:
        parts = line.split(' ')
        name = "{} {}".format(parts[0], parts[1])
        val = parts[-1].strip()
        player_to_fdp[name] = val
        continue


    if "Fantasy Score" in line:
        val = line.split(' ')[-1].strip()
        player_to_fdp[current_player] = val
        pass

for player, fdp in player_to_fdp.items():
    print("{}, {}".format(player, fdp))
