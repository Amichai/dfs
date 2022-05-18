

def increment_index(indices, max_indices, inc_idx, locked_indices):
    while indices[inc_idx] == max_indices[inc_idx] - 1 or inc_idx in locked_indices:
        for i in range(len(indices) - inc_idx):
            idx_to_incr = inc_idx + i
            if idx_to_incr in locked_indices:
                pass
            else:
                indices[inc_idx + i] = 0
        inc_idx -= 1

    indices[inc_idx] += 1
    if inc_idx == 1:
        print("{}/{}".format(indices, max_indices))

    if inc_idx == 0:
        return None

all_positions = ["PG","SG", "SF", "PF", "C", "G", "F", "UTIL"]

def get_roster(indices, by_position, max_indices, locked_indices):
    to_return = []
    seen_names = []
    for i in range(len(all_positions)):
        pos = all_positions[i]
        player1 = by_position[pos][indices[i]]
        if player1.name in seen_names:
            result = increment_index(indices, max_indices, i, locked_indices)
            return None

        to_return.append(player1)
        seen_names.append(player1.name)


    roster = Roster(to_return)
    return roster

def exhaustive_optimizer(by_position, to_lock):
    max_indices = []
    for pos, players in by_position.items():
        max_indices.append(len(players))
    print(max_indices)
    indices = []
    indices_to_not_increment = []
    for i in range(len(all_positions)):
        pos = all_positions[i]
        was_lock = False
        for lock in to_lock:
            lock_position = lock[1]
            if lock_position == pos:
                indices.append(lock[2])
                indices_to_not_increment.append(i)
                was_lock = True

        if not was_lock:
            indices.append(0)

    assert len(indices) == 8
    best_roster = None
    best_roster_val = 0
    while True:
        inc_idx = len(indices) - 1
        
        roster = get_roster(indices, by_position, max_indices, indices_to_not_increment)
        if roster != None:
            if roster.value > best_roster_val and roster.cost <= 50000:
                best_roster_val = roster.value
                best_roster = roster
                print(roster)
            
            increment_index(indices, max_indices, inc_idx, indices_to_not_increment)

    # for each position
    # take best available player
    # when we run out of money, backtrack and take a cheaper
    pass


class Player:
    def __init__(self, name, position, cost, team, value):
        self.name = name
        self.position = position
        self.cost = float(cost)
        self.team = team
        self.value = float(value)
        self.value_per_dollar = self.value * 100 / self.cost

    def __repr__(self):
        # return "{} - {} - {} - {} - {} - {}".format(self.name, self.position, self.cost, self.team, self.value, self.value_per_dollar)
        return "{} - {}".format(self.name, self.value)
    
class Roster:
    def __init__(self, players):
        self.players = players
        self.cost = sum([float(p.cost) for p in self.players])
        self.value = sum([float(p.value) for p in self.players])
        self.locked_indices = []


    def lockPlayer(self, player):
        if player.position == "C":
            self.players[0] = player
            self.locked_indices.append(0)
        elif player.position == "PF":
            self.players[1] = player
            self.locked_indices.append(1)
        elif player.position == "SF":
            self.players[3] = player
            self.locked_indices.append(3)
        elif player.position == "SG":
            self.players[5] = player
            self.locked_indices.append(5)
        elif player.position == "PG":
            self.players[7] = player
            self.locked_indices.append(7)

    def __repr__(self):
        return ",".join([p.name for p in self.players]) + " {} - {}".format(self.cost, self.value)

    def remainingFunds(self):
        return 50000 - self.cost

    def relpace(self, player, idx):
        self.players[idx] = player
        self.cost = sum([float(p.cost) for p in self.players])
        self.value = sum([float(p.value) for p in self.players])

    def atPosition(self, position):
        return [p for p in self.players if p.position == position]

    def getIds(self, id_mapping):
        ids = []
        for p in self.players:
            id = id_mapping[p.name]
            ids.append(id)

        ids.reverse()
        return ",".join(ids)





to_read = open("money_line_scrape_10_21_12.txt")

player_to_fp = {}

lines = to_read.readlines()
for line in lines:
    parts = line.split("|")
    if len(parts) < 4:
        continue
    if parts[3] == "Fantasy Score":
        player_name = parts[2]
        player_name = player_name.replace(" III", "")
        player_to_fp[player_name] = float(parts[4].strip())




all_players = []
by_position = {}
for position in all_positions:
    by_position[position] = []
salaries = open("salary_data/DKSalaries_10_21_21.csv")
lines = salaries.readlines()
found_count = 0
for line in lines[1:]:
    # print(line)
    parts = line.split(',')
    name = parts[2]
    positions = parts[4].split("/")
    salary = parts[5]
    
    team = parts[7]
    

    if name in player_to_fp:
        
        value = player_to_fp[name]
        found_count += 1
        if value < 10 or name == "Jaren Jackson Jr." or name == "Jrue Holiday":
            print("Filtered out: {} - {}".format(name, value))
            continue

        for pos in positions:
            new_player = Player(name, pos, float(salary), team, value)

            by_position[pos].append(new_player)
    else:
        # print("Not found: {}".format(name))
        name_parts = name.split(' ')
        # for search_name in player_to_fp.keys():
        #     if name_parts[0] in search_name:
        #         print("CANDIDATE: {} - {}".format(name, search_name))


    # print("{} - {}".format(name, positions))

    # new_player = Player(1)
# assert len(player_to_fp) == found_count
# import pdb; pdb.set_trace()


names_to_lock = ["Jordan Nwora"]


to_lock = []
locked_positions = []
for name in names_to_lock:
    for pos, players in by_position.items():
        if pos in locked_positions:
            continue
        player_idx = 0
        player_matched = False
        for player in players:
            if name == player.name:
                to_lock.append((name, pos, player_idx))
                player_matched = True
                locked_positions.append(pos)
                break
            player_idx += 1
        if player_matched:
            break

print(to_lock)
exhaustive_optimizer(by_position, to_lock)