from os import path
import datetime
import random


MAX_ROSTER_COST = 55000

def random_element(arr):
    idx = random.randint(0, len(arr) - 1)
    return arr[idx]

def random_elements(arr, count):
    if count > len(arr):
        assert False
    if count == len(arr):
        return arr

    to_return = []
    while True:
        idx = random.randint(0, len(arr) - 1)
        val = arr[idx]
        if not val in to_return:
            to_return.append(val)
        
        if len(to_return) == count:
            break

    return to_return


def select_better_player(players, max_cost, excluding, initial_value, mleProjections):
    better_players = []
    for p in players:
        if p[0] in excluding:
            continue

        p_value = mleProjections[p[0]]
        if p[2] <= max_cost and p_value > initial_value:
            better_players.append(p)

    if len(better_players) == 0:
        return None


    # import pdb; pdb.set_trace()
    return random_element(better_players)

class Roster:
    def __init__(self, mleProjections):
        self.G = []
        self.C = []
        self.W = []
        self.D = []
        self.Util = []
        self.cost = 0
        self.value = 0
        self.mleProjections = mleProjections
        self.players = None
        self.locked_indices = []

    def remainingFunds(self):
        return MAX_ROSTER_COST - self.cost
    
    def replace(self, player, idx):
        self.players[idx] = player
        self.updateCostAndValue()

    def __repr__(self):
        to_return = ",".join([p[0] for p in self.allPlayers()]) + " {} - {}".format(self.cost, self.value)
        return to_return

    def setPlayer(self, pos, fd_player):
        assert pos == "G"
        if pos == "G":
            assert len(self.G) == 0
            self.G.append(fd_player)

        self.updateCostAndValue()

    def allPlayers(self):
        if self.players == None:
            self.players = self.Util + self.D + self.W + self.C + self.G
        return self.players

    def updateCostAndValue(self):
        self.cost = 0
        self.value = 0

        for p in self.allPlayers():
            name = p[0]
            self.cost += p[2]
            if not name in self.mleProjections:
                continue
            self.value += self.mleProjections[name]
        

    def randomlyFillPlayerSlots(self, players_by_position):
        assert len(self.C) == 0
        assert len(self.W) == 0
        assert len(self.D) == 0
        assert len(self.Util) == 0

        self.C = random_elements(players_by_position['C'], 2)
        self.W = random_elements(players_by_position['W'], 2)
        self.D = random_elements(players_by_position['D'], 2)
        selected_names = []
        selected_names += [a[0] for a in self.C]
        selected_names += [a[0] for a in self.W]
        selected_names += [a[0] for a in self.D]

        for i in range(1000):
            if len(self.Util) > 1:
                break
            random_util = random_element(players_by_position['UTIL'])

            if random_util[0] in selected_names:
                continue

            self.Util.append(random_util)

        assert len(self.Util) == 2
        assert len(self.C) == 2
        assert len(self.W) == 2
        assert len(self.D) == 2
        # do we have enough players to choose from?

        self.updateCostAndValue()
        self.players = self.Util + self.D + self.W + self.C + self.G


def updateRoster(roster, by_position, mleProjections):
    initial_cost = roster.cost

    no_improvement_count = 0
    if initial_cost <= MAX_ROSTER_COST:
        # pick a random player
        # swap that player for the best player we can afford that brings more value
        while True:
            swap_idx = random.randint(0, 7)
            if swap_idx == 9:
                swap_idx = 0
            if swap_idx in roster.locked_indices:
                continue
            
            to_swap = roster.allPlayers()[swap_idx]
            position = to_swap[1]
            value = mleProjections[to_swap[0]]

            excluding = [p[0] for p in roster.allPlayers()]
            replacement = select_better_player(by_position[position], roster.remainingFunds() + to_swap[2], excluding, value, mleProjections)

            if replacement == None or to_swap[0] == replacement[0]:
                no_improvement_count += 1
            else:
                no_improvement_count = 0
                roster.replace(replacement, swap_idx)

            if no_improvement_count > 20:
                return roster

    # print(roster)
    return roster

def optimize_(mleProjections, playersByPosition, team_to_goalie, fd_players, team):
    # do this many times
    best_roster = None
    best_roster_val = 0
    # __import__('pdb').set_trace()
    print("----")
    for i in range(100000):
        roster = Roster(mleProjections)
        
        goalie_name = team_to_goalie[team][0]
        fd_player = fd_players[goalie_name]
        roster.setPlayer("G", fd_player)

        roster.randomlyFillPlayerSlots(playersByPosition)
        if roster.cost > MAX_ROSTER_COST:
            continue

        assert roster.cost <= MAX_ROSTER_COST

        assert len(roster.allPlayers()) == 9
        updateRoster(roster, playersByPosition, mleProjections)
        if roster.cost >= MAX_ROSTER_COST:
            continue
        
        if roster.value >= best_roster_val:
            best_roster = roster
            best_roster_val = roster.value
            print("RESULT: {}".format(roster))

    pass


def optimize(mleProjections, goalie_projections, fd_players, winning_teams):
    team_to_goalie = {}
    for goalie_name, goalie_projections in goalie_projections.items():
        if not goalie_name in fd_players:
            continue
        team = fd_players[goalie_name][3]
        if team in team_to_goalie:
            current_goalie_projections = team_to_goalie[team][1]
            if goalie_projections > current_goalie_projections:
                team_to_goalie[team] = (goalie_name, goalie_projections)
            continue

        assert team not in team_to_goalie
        team_to_goalie[team] = (goalie_name, goalie_projections)

    players_by_position = {"UTIL": []}
    for name, fd_player in fd_players.items():
        pos = fd_player[1]
        if name not in mleProjections:
            continue

        if not pos in players_by_position:
            players_by_position[pos] = []

        players_by_position[pos].append(fd_player)
        players_by_position["UTIL"].append(fd_player)
    for team in winning_teams:
        #lock the goalie
        print(team)
        
        optimize_(mleProjections, players_by_position, team_to_goalie, fd_players, team)



def normalize_name(name):
    name = name.replace("  ", " ")
    name = name.replace("’", "'")
    name = name.replace(".", "")
    parts = name.split(" ")

    if len(parts) > 2:
        return "{} {}".format(parts[0], parts[1]).strip()

    return name.strip()

def get_fd_slate_players(fd_slate_file_name, exclude_injured_players=True):
    all_players = {}
    salaries = open(fd_slate_file_name)
    lines = salaries.readlines()
    found_count = 0

    for line in lines[1:]:
        parts = line.split(',')
        full_name = normalize_name(parts[3])

        positions = parts[1]
        salary = parts[7]
        team = parts[9]
        status = parts[11]
        # print(full_name)
        if status == "O" and exclude_injured_players:
            continue
        name = full_name
        all_players[name] = [name, positions, float(salary), team, status]
        
    return all_players

def get_MLE_projections(sites):
    mle_projections = {}
    goalie_projections = {}
    caesars = sites["Caesars"]
    for player, stats in caesars.items():
        stat_keys = stats.keys()
        if "Saves" in stat_keys:
            goalie_projections[player] = float(stats["Saves"]) * 0.8
            continue
        if not "Assists" in stat_keys or not "Shots" in stat_keys or not "Points" in stat_keys:
            continue

        assists = float(stats["Assists"])
        pts = float(stats["Points"])
        goals = pts - assists
        shots = float(stats["Shots"])

        fd_projection = assists * 8 + goals * 12 + shots * 1.6
        mle_projections[player] = fd_projection
        
    return (mle_projections, goalie_projections)

def get_player_prices(fd_slate_file):
    fd_players = get_fd_slate_players(fd_slate_file, False)
    
    return fd_players


if __name__ == "__main__":
    folder = "/Users/amichailevy/Downloads/player_lists/"

    #TODO 1- 3/1/22
    fd_slate_file = folder + "FanDuel-NHL-2022 ET-03 ET-01 ET-72276-players-list.csv"
    
    fd_players = get_player_prices(fd_slate_file)

    all_sites = ["Caesars"]
    sites = {}


    current_date = datetime.datetime.now()
    output_file_name = "scraper_logs/money_line_scrape_{}_{}_{}.txt".format(current_date.month, current_date.day, current_date.year)

    if not path.exists(output_file_name):
        output_file = open(output_file_name, "a")
    else:
        output_file = open(output_file_name, "r+")

    # TODO: 3
    players_to_ignore = ["Oscar Klefbom", "William Carrier"]

    lines = output_file.readlines()
    for line in lines:
        parts = line.split("|")
        if len(parts) < 4:
            continue
        site = parts[1]
        if not site in sites:
            sites[site] = {}

        player_name = parts[2]
        if player_name in players_to_ignore:
            continue

        if not player_name in sites[site]:
            sites[site][player_name] = {}
        val = parts[5].strip()
        if val == "REMOVED":
            if stat in sites[site][player_name]:
                del sites[site][player_name][stat]
            continue
        stat = parts[4]
        sites[site][player_name][stat] = str(val)


    (mle_projections, goalie_projections) = get_MLE_projections(sites)
    # TODO: #2 - 
    # optimize(mle_projections, goalie_projections, fd_players, ["COL"])
    optimize(mle_projections, goalie_projections, fd_players, ["TB"])
    