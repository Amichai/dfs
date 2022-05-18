import json
import ast
import time
import random
import dk_random_optimizer
import fd_optimizer
from library import *
from selenium import webdriver
import optimizer_player_pool
import scrapers.crunch_scraper_wnba


# pp_projections = """
# {'NaLyssa Smith': {'Points': 12.5, 'Pts+Rebs+Asts': 18.5, 'Rebounds': 4.5}, 'Elena Delle': {'Rebounds': 5.5, 'Pts+Rebs+Asts': 23.5, 'Points': 17.5}, 'Kelsey Mitchell': {'Rebounds': 2.5, 'Points': 14.5, 'Assists': 2.5, 'Pts+Rebs+Asts': 19.5}, 'Myisha Hines-Allen': {'Points': 12.5, 'Pts+Rebs+Asts': 20.5, 'Rebounds': 5.5, 'Assists': 2.5}, 'Queen Egbo': {'Points': 8.5, 'Pts+Rebs+Asts': 16.0, 'Rebounds': 7.0}, 'Ariel Atkins': {'Pts+Rebs+Asts': 19.5, 'Rebounds': 2.5, 'Points': 14.5, 'Assists': 2.5}, 'Natasha Cloud': {'Rebounds': 3.5, 'Points': 9.5, 'Assists': 6.5, 'Pts+Rebs+Asts': 19.5}, 'Liz Cambage': {'Points': 13.5, 'Pts+Rebs+Asts': 23.5, 'Rebounds': 8.5}, 'Courtney Vandersloot': {'Assists': 8.5, 'Points': 10.5, 'Rebounds': 3.5, 'Pts+Rebs+Asts': 22.5}, 'Nneka Ogwumike': {'Points': 12.5, 'Rebounds': 5.5, 'Pts+Rebs+Asts': 18.5}, 'Candace Parker': {'Assists': 3.5, 'Pts+Rebs+Asts': 25.5, 'Points': 13.5, 'Rebounds': 8.5}, "A'ja Wilson": {'Rebounds': 8.5, 'Points': 18.5, 'Pts+Rebs+Asts': 28.5, 'Assists': 1.5}, 'Tina Charles': {'Rebounds': 8.5, 'Pts+Rebs+Asts': 28.5, 'Points': 19.5}, 'Dearica Hamby': {'Rebounds': 6.5, 'Pts+Rebs+Asts': 20.5, 'Points': 12.5}, 'Skylar Diggins-Smith': {'Pts+Rebs+Asts': 20.5, 'Assists': 4.0, 'Points': 14.5}, 'Kelsey Plum': {'Points': 14.5, 'Pts+Rebs+Asts': 20.5, 'Rebounds': 2.5, 'Assists': 3.5}, 'Diana Taurasi': {'Pts+Rebs+Asts': 22.5, 'Rebounds': 3.5, 'Assists': 5.0, 'Points': 13.5}, 'Breanna Stewart': {'Assists': 2.5, 'Pts+Rebs+Asts': 30.5, 'Points': 19.5, 'Rebounds': 8.5}, 'Sylvia Fowles': {'Points': 15.5, 'Rebounds': 9.5, 'Pts+Rebs+Asts': 25.5}, 'Jewell Loyd': {'Assists': 3.5, 'Points': 16.5, 'Rebounds': 3.5, 'Pts+Rebs+Asts': 23.5}, 'Aerial Powers': {'Pts+Rebs+Asts': 19.5, 'Points': 13.5}, 'Sue Bird': {'Pts+Rebs+Asts': 16.5, 'Assists': 4.5, 'Rebounds': 2.0, 'Points': 9.5}, 'Natalie Achonwa': {'Points': 7.5, 'Pts+Rebs+Asts': 12.5, 'Rebounds': 3.5}}
# """

def random_element(arr):
    idx = random.randint(0, len(arr) - 1)
    return arr[idx]

class Optimizer:
    def __init__(self, max_cost, positions_to_fill):
        self.max_cost = max_cost
        self.positions_to_fill = positions_to_fill


    def select_better_player(self, players, max_cost, excluding, initial_value):
        better_players = []
        for p in players:
            if p.name in excluding:
                continue
            if p.cost <= max_cost and p.value > initial_value:
                better_players.append(p)

        if len(better_players) == 0:
            return None


    def optimize_roster(self, roster, by_position):
        initial_cost = roster.cost

        no_improvement_count = 0
        if initial_cost <= self.max_cost:
            # pick a random player
            # swap that player for the best player we can afford that brings more value
            while True:
                swap_idx = random.randint(0, len(roster.players) - 1)
                
                if swap_idx in roster.locked_indices:
                    continue

                try:
                    to_swap = roster.players[swap_idx]
                except:
                    import pdb; pdb.set_trace()
                position = to_swap.position

                excluding = [p.name for p in roster.players]

                replacement = self.select_better_player(by_position[position], roster.remainingFunds() + to_swap.cost, excluding, to_swap.value)

                if replacement == None or to_swap.name == replacement.name:
                    no_improvement_count += 1
                else:
                    no_improvement_count = 0
                    roster.relpace(replacement, swap_idx)

                if no_improvement_count > 20:
                    return roster

        print(roster)
        assert False

    def random_lineup(self):
        to_return = []
        for pos in self.positions_to_fill:
            to_return.append(random_element(by_position[pos]))

        return dk_random_optimizer.Roster(to_return)


    def optimize(self, by_position, iter_count = 600000):
        best_roster = None
        best_roster_val = 0

        random.seed(time.time())
        
        for i in range(iter_count):
            if i % 50000 == 0:
                print(i)
            to_remove = None
            if best_roster != None:
                to_remove = random_element(best_roster.players)

            by_position_copied = {}
            for pos, players in by_position.items():
                if to_remove in players:
                    players_new = list(players)

                    players_new.remove(to_remove)
                    by_position_copied[pos] = players_new
                else:
                    by_position_copied[pos] = players

            if to_remove == None:
                by_position_copied = by_position

            random_lineup = self.random_lineup()
                
            if random_lineup.cost > self.max_cost or not random_lineup.is_valid:
                continue


            result = self.optimize_roster(random_lineup, by_position_copied)
            if result.value > best_roster_val:
                best_roster = result
                if result.value >= best_roster_val:
                    best_roster_val = result.value

                all_names = [a.name for a in best_roster.players]
                all_names_sorted = sorted(all_names)
                roster_key = ",".join(all_names_sorted)
                # if roster_count > 50:
                #     break

                #TODO: PUT THIS BACK IN AND TROUBLESHOOT
                # best_roster = optimize_roster_by_start_time(by_position_copied, best_roster)
                # later games get laters slots
                # earlier games get earlier slots
                print("B: {}\n".format(best_roster))

        return best_roster
        


def get_PP_projections(driver):


    
    url = 'https://api.prizepicks.com/projections?league_id=3&per_page=500&single_stat=false'
    driver.get(url)

    as_text = driver.find_element_by_tag_name('body').text

    as_json = json.loads(as_text)

    assert as_json["meta"]["total_pages"] == 1

    data = as_json['data']
    included = as_json['included']

    id_to_name = {}
    player_ids = []
    for player in included:
        attr = player["attributes"]
        player_name = attr['name']
        player_name = optimizer_player_pool.normalize_name(player_name)
        # team = attr['team']
        
        player_id = player['id']
        player_ids.append(player_id)
        id_to_name[player_id] = player_name

    name_to_projections = {}

    stats_from_promotions = []

    for projection in data:
        
        attr = projection['attributes']
        stat_type = attr['stat_type']
        # created_at = attr["created_at"]
        updated_at = attr["updated_at"]
        line_score = float(attr["line_score"])
        projection_type = attr["projection_type"]
        player_id = projection['relationships']['new_player']['data']['id']
        player_name = id_to_name[player_id]
        promotion_stat_key = "{}-{}".format(stat_type, player_name)
        if promotion_stat_key in stats_from_promotions:
            continue

        # flash_sale_line_score = attr['flash_sale_line_score']
        # if flash_sale_line_score != '' and flash_sale_line_score != None:
        #     line_score = flash_sale_line_score
        #     stats_from_promotions.append(promotion_stat_key)
        
        if not player_name in name_to_projections:
            name_to_projections[player_name] = {}

        name_to_projections[player_name][stat_type] = line_score
        
    return name_to_projections


driver = webdriver.Chrome("../master_scrape_process/chromedriver9")
result = get_PP_projections(driver)
print(result)

driver.close()

# result = ast.literal_eval(pp_projections)
player_projections = {}

for player, stats in result.items():
    if not "Fantasy Score" in stats:
        print("Skipping: {}".format(player))
        continue
    projection = stats["Fantasy Score"]
    player_projections[player] = projection


crunch_projections = scrapers.crunch_scraper_wnba.query()
# __import__('pdb').set_trace()

for player, stats in crunch_projections.items():
    if player not in player_projections:
        player_projections[player] = stats['crunch_projected']
    else:
        print("{} PP: {} - crunch: {}".format(player, player_projections[player], stats['crunch_projected']))

path = "FanDuel-WNBA-2022 ET-05 ET-06 ET-75628-players-list.csv"
download_folder = "/Users/amichailevy/Downloads/"

fd_players = get_fd_slate_players(download_folder + path)

by_position = {"G": [], "F": []}
all_players = []
for player, player_info in fd_players.items():
    if player not in player_projections:
        continue

    position = player_info[1]
    fd_player = dk_random_optimizer.Player(player, position, player_info[2], player_info[3], player_projections[player], 0)
    all_players.append(fd_player)
    by_position[position].append(fd_player)

# result = fd_optimizer.single_game_optimizer(all_players)


optimizer = Optimizer(40000, ["G", "G", "G", "F", "F", "F", "F"])

result = optimizer.optimize(by_position)


__import__('pdb').set_trace()
