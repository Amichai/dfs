

from os import link
import time
import datetime
from tabulate import tabulate
import json
import requests
from selenium import webdriver


def get_game_guids(driver):
    url = "https://www.williamhill.com/us/az/bet/hockey/events/all"
    driver.get(url)

    all_team_names = open('nhl_team_names.txt', "r").readlines()
    # all_team_names = open('team_names.txt', "r").readlines()

    team_keys = []
    for team_name in all_team_names:
        team_keys.append(team_name.strip().lower().replace(" ", "-"))


    time.sleep(1)
    for i in range(3):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(1)

    found_nhl_links = []

    links = driver.find_elements_by_css_selector('a')
    for link_element in links:
        link_url = link_element.get_attribute('href')

        print(link_url)
        for team_key in team_keys:
            if link_url != None and team_key in link_url:
                if link_url not in found_nhl_links:
                    found_nhl_links.append(link_url)
                break
        
    game_guids = []
    for l in found_nhl_links:
        game_guids.append(l.split('/')[7])
        
    return game_guids

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
    # if fGM(driver):
    if game_guids == None:
        game_guids = get_game_guids(driver)
        
    result = query(driver, game_guids)
    return result

def query(driver, game_guids):
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
            name_parts = market['name'].split('| |')
            if market['name'].count('|') == 2:
                continue
            if len(name_parts) == 1:
                continue
            name = name_parts[0].strip('|')
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
            line = float(line) + (float(odds_percentage) - 0.5) * 1.5
            assert abs(line - original_line) < 0.9
            to_return[name][stat] = str(line)


    return to_return


if __name__ == "__main__":
    driver = webdriver.Chrome("../../master_scrape_process/chromedriver")

    

    result = query_betCaesars(driver)

    # result = query(driver, ["02c8dbaf-7a17-4efe-960a-dd256b819685"])
    print(result)