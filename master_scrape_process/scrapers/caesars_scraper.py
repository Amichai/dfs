from os import link
import logging
import time
import datetime
from bs4.element import NamespacedAttribute
from tabulate import tabulate
import json
import requests
from selenium import webdriver

# logging.basicConfig(filename='master_scraper.log', encoding='utf-8', level=logging.INFO)
# logger = logging.getLogger("Caesars")

def time_str():
    return str(datetime.datetime.now()).split('.')[0]

def get_game_guids(driver, all_team_names):
    url = "https://www.williamhill.com/us/az/bet/basketball/events/all"
    driver.get(url)

    team_keys = []
    for team_name in all_team_names:
        team_keys.append(team_name.strip().lower().replace(" ", "-"))

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


def normalize_name(name):
    name = name.replace("  ", " ")
    name = name.replace("’", "'")
    parts = name.split(" ")
    if len(parts) > 2:
        return "{} {}".format(parts[0], parts[1]).strip()

    name = name.replace(".", "")

    return name.strip()
    

game_guids = None

def query_betCaesars(driver):
    global game_guids

    all_team_names = open('scrapers/team_names.txt', "r").readlines()
    # all_team_names = open('team_names.txt', "r").readlines()

    if game_guids == None:
        game_guids = get_game_guids(driver, all_team_names)
        
    result = query(driver, game_guids, all_team_names)
    return result

def query(driver, game_guids, all_team_names):
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
            
            if " |Live|" in name:
                continue
            # import pdb; pdb.set_trace()
            name = name_parts[0].strip('|')
            if name in all_team_names:
                continue

            stat = name_parts[1].strip('|').replace('Total ', '')
            name = normalize_name(name)
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
            original_line = float(line)
            # __import__('pdb').set_trace()
            # line_adjusted = float(line) + (float(odds_percentage) - 0.5) * 1.5
            line_adjusted = float(line) + (float(odds_percentage) - 0.5) * float(line)

            #TODO - this needs to be projected into a new scraper with new fantasy score projections!
            # line = float(line) + (float(odds_percentage) - 0.5) * (float(line) / 2)


            # assert abs(line_adjusted - original_line) < 0.9
            to_return[name][stat] = str(line_adjusted)
            # logger.info("{} {} {} {} {} {}".format(time_str(), name, stat, line, odds_percentage, line_adjusted))


    return to_return


if __name__ == "__main__":
    driver = webdriver.Chrome("../../master_scrape_process/chromedriver6")

    

    result = query_betCaesars(driver)

    # result = query(driver, ["02c8dbaf-7a17-4efe-960a-dd256b819685"])
    print(result)