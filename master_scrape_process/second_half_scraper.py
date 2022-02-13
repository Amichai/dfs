from imp import lock_held
from re import S
import optimizer_player_pool
import json
from selenium import webdriver
import time
from tabulate import tabulate

game_guids = None

def get_game_guids(driver, all_team_names):
    url = "https://www.williamhill.com/us/az/bet/basketball/events/all"
    driver.get(url)

    team_keys = []
    for team_name in all_team_names:
        team_keys.append(team_name.strip().lower().replace(" ", "-"))

    # time.sleep(1)

    # arrow_elements = driver.find_elements_by_css_selector('.ArrowInCircleUp.expanded')
    # arrow_elements[0].click()
    # time.sleep(0.5)

    # arrow_elements = driver.find_elements_by_css_selector('.ArrowInCircleUp.unexpanded')
    # arrow_elements[1].click()

    time.sleep(1)

    short_sleep = 0.5
    for i in range(3):


        driver.execute_script("window.scrollTo(0, 0);")

        time.sleep(short_sleep)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 4.0);")

        time.sleep(short_sleep)


        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3.0);")

        time.sleep(short_sleep)


        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2.0);")

        time.sleep(short_sleep)


        driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 3 / 4.0);")

        time.sleep(short_sleep)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(short_sleep)

    found_nba_links = []

    links = driver.find_elements_by_css_selector('a')
    for link_element in links:
        link_url = link_element.get_attribute('href')
        for team_key in team_keys:
            if link_url != None and team_key in link_url:
                if link_url not in found_nba_links:
                    found_nba_links.append(link_url)
                break
        

    game_guids = []
    for l in found_nba_links:
        game_guids.append(l.split('/')[7])
        
    return game_guids


line_keys = {
"How many blocks will ": "blocks",
"How many assists will ": "assists",
"How many rebounds will ": "rebounds",
"How many three-pointers will ": "three-pointers",
"How many total points:  rebounds and assists will ": "points",
"How many total rebounds and assists will ": "rebounds + assists",
"How many total points and rebounds will ": "points + rebounds",
"How many total steals and blocks will ": "steals + blocks",
"How many steals will ": "steals",
"How many total points and assists will ": "points + assists",
"How many points will ": "points",
}


def query_betCaesars(driver, all_players):
    global game_guids

    all_team_names = open('scrapers/team_names.txt', "r").readlines()
    # all_team_names = open('team_names.txt', "r").readlines()

    if game_guids == None:
        game_guids = get_game_guids(driver, all_team_names)
        
    result = query(driver, game_guids, all_team_names, all_players)
    return result

def query(driver, game_guids, all_team_names, all_players):
    all_team_names = [a.strip() for a in all_team_names]
    to_return = {}
    for guid in game_guids:
        url = 'https://www.williamhill.com/us/az/bet/api/v2/events/{}'.format(guid)

        #import pdb; pdb.set_trace()
        driver.get(url)

        time.sleep(1.5)

        as_text = driver.find_element_by_tag_name('body').text

        as_json = json.loads(as_text)
        
        for market in as_json['markets']:
            selections = market['selections']
            name = market['name']
            if name == None:
                continue
            if "|Alternative " in name or "|Margin of " in name:
                continue

            if "Alternative" in str(market):
                __import__('pdb').set_trace()
                continue

            name_parts = market['name'].split('| |')
            if market['name'].count('|') == 2:
                continue
            if len(name_parts) == 1:
                continue
            
            if not " |Live|" in name:
                continue
            # import pdb; pdb.set_trace()
            name = name_parts[0].strip('|')
            if name in all_team_names:
                continue

            stat = name_parts[1].strip('|').replace('Total ', '')
            name = optimizer_player_pool.normalize_name(name)
            under_faction = None
            over_fraction = None
            for selection in selections:
                if selection['type'] == 'under':
                    under_faction = selection['price']['d']
                elif selection['type'] == 'over':
                    over_fraction = selection['price']['d']
            
            if under_faction == None and over_fraction == None:
                continue


            odds1 = over_fraction
            odds2 = under_faction

            odds1 = 1.0 / odds1
            odds2 = 1.0 / odds2

            odds_percentage = odds1 / (odds1  + odds2)

            if not name in to_return:
                to_return[name] = {}

            line = market['line']
            # __import__('pdb').set_trace()
            # line_adjusted = float(line) + (float(odds_percentage) - 0.5) * 1.5
            line_adjusted = float(line) + (float(odds_percentage) - 0.5) * float(line)

            if not name in all_players:
                # print("SKIPPING NAME: {}".format(name))
                continue

            if not stat in all_players[name]:
                # print("SKIPPING STAT: {}".format(stat))
                continue


            projected = line_adjusted - all_players[name][stat]
            

            # assert abs(line_adjusted - original_line) < 0.9
            to_return[name][stat] = projected
            # logger.info("{} {} {} {} {} {}".format(time_str(), name, stat, line, odds_percentage, line_adjusted))


    for player_name, stat_vals in to_return.items():
        if "Points" in stat_vals and "Assists" in stat_vals and "Rebounds" in stat_vals and "Steals" in stat_vals and "Blocks" in stat_vals and "Turnovers" in stat_vals:
            to_return[player_name]["Fantasy Score"] = stat_vals["Points"] + stat_vals["Rebounds"] * 1.2 + stat_vals["Assists"] * 1.5 + stat_vals["Steals"] * 3 + stat_vals["Blocks"] * 3 - stat_vals["Turnovers"]
            print("Found fantasy score for: {}".format(player_name))
    return to_return


def get_PP_projections_2H(driver):
    url = 'https://api.prizepicks.com/projections?league_id=80&per_page=500&single_stat=false'
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
        created_at = attr["created_at"]
        updated_at = attr["updated_at"]
        line_score = attr["line_score"]
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


def extract_stats_from_json(players):
    to_return = {}
    for player in players:
        name = player["name"]
        stats = player["statistics"]

        assists = stats["assists"]
        blocks = stats["blocks"]
        points = stats["points"]
        rebounds = stats["reboundsTotal"]
        steals = stats["steals"]
        turnovers = stats["turnovers"]
        fantasy_score = points + rebounds * 1.2 + assists * 1.5 + blocks * 3 + steals * 3 - turnovers
        to_return[name] = {"Points": points, "Rebounds": rebounds, "Assists": assists, "Blocks": blocks, "Steals": steals, "Turnovers": turnovers, "Fantasy Score": fantasy_score}

    return to_return



if __name__ == "__main__":
    driver = webdriver.Chrome("../master_scrape_process/chromedriver6")
    url = "https://www.nba.com/"
    driver.get(url)

    seen_urls = []
    for link in driver.find_elements_by_tag_name('a'):
        url = link.get_attribute('href')
        if url in seen_urls:
            continue
        if url != None and "box-score#box-score" in url:
            print(url)
            seen_urls.append(url)

    # seen_urls.append("https://www.nba.com/game/bos-vs-orl-0022100806/box-score#box-score")

    player_to_game = {}
    all_players = {}
    for url in seen_urls:
        time.sleep(0.4)
        url = url.replace("/box-score#box-score", "")
        url_parts = url.split('-')
        game_id = url_parts[-1]
        # game_name = 
        url = "https://cdn.nba.com/static/json/liveData/boxscore/boxscore_{}.json".format(game_id)
        driver.get(url)
        as_text = driver.find_element_by_tag_name('body').text

        as_json = json.loads(as_text)
        players1 = as_json['game']['homeTeam']['players']
        players2 = as_json['game']['awayTeam']['players']
        dict1 = extract_stats_from_json(players1)
        dict2 = extract_stats_from_json(players2)
        
        all_players.update(dict1)
        all_players.update(dict2)
        # for player_name in all_players.keys():
        #     player_to_game[player_name] = gam

    projected_stats_remaining = query_betCaesars(driver, all_players)
    # negative values should be read as 0 remaining
    prize_pick_lines = get_PP_projections_2H(driver)

    all_rows = []
    for player, stats in prize_pick_lines.items():
        if player in projected_stats_remaining:
            projected_stats = projected_stats_remaining[player]
            for stat, val in stats.items():
                val = round(float(val), 2)
                if stat in projected_stats:
                    projected_val = round(float(projected_stats[stat]), 2)
                    # print("{}, {}, {}, {} diff: {}".format(player, stat, val, projected_val, round(projected_val - val, 2)))
                    all_rows.append([player, stat, val, projected_val, round(projected_val - val, 2)])


    all_rows_sorted = sorted(all_rows, key=lambda a: abs(a[4]), reverse=True)
    print(tabulate(all_rows_sorted, headers=["name", "stat", "PP", "Caesars", "Diff"]))
