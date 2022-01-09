import time
import datetime
from tabulate import tabulate
import json
import requests
from selenium import webdriver

def parse_game_stats(driver, url, all_keys):
    time.sleep(1)
    driver.get(url)
    time.sleep(1)
    all_svgs = driver.find_elements_by_css_selector('svg')
    is_first = True
    arrow_count = 0

    for svg in all_svgs:
        if svg.get_attribute('data-test-id') == "ArrowActionIcon":
            arrow_count += 1
            if is_first:
                is_first = False
                continue

            if arrow_count > 1:
                parent_element = svg.find_element_by_xpath('../../..')
                time.sleep(1.0)
                svg.click()

            time.sleep(0.3)
            category = parent_element.text
            if category == "Show less":
                category = "Player Pts + Ast"


            if arrow_count > 1:
                show_more_button = parent_element.find_element_by_xpath('../../..').find_elements_by_css_selector('span.x.h.fk')
                if len(show_more_button) > 0:
                    show_more_button[0].click()
                    time.sleep(0.3)


            key = ""
            key2 = ""
            lines = parent_element.find_element_by_xpath('../../..').text.split("\n")
            for i in range(len(lines)):
                line = lines[i]
                if line[0] in ["-", "+"]:
                    add(all_keys, category, key, key2, value=line)
                elif line[:2] in ["O ", "U "]:
                    key2 = line
                else:
                    key = line


def add(dict, *keys, value):
    if len(keys) == 1:
        key = keys[0]
        if key in dict:
            old_val = dict[key]
            if old_val != value:
                print("Change: {} {} -> {}".format(key, old_val, value))
        else:
            print("{} {}".format(key, value))
        dict[key] = value
    else:
        current_dict = dict
        for i in range(len(keys)):
            current_key = keys[i]
            if i == len(keys) - 1:
                if current_key in current_dict:
                    old_val = current_dict[current_key]
                    if old_val != value:
                        print("Change: {} {} -> {}".format(keys, old_val, value))
                else:
                    print("{} {}".format(keys, value))

                current_dict[current_key] = value
                continue

            if not current_key in current_dict:
                current_dict[current_key] = {}
            current_dict = current_dict[current_key]


def parse_NBA_page(driver, all_keys):
    url = 'https://az.sportsbook.fanduel.com/navigation/nba'
    driver.get(url)

    game_links = []

    all_link_elements =  driver.find_elements_by_css_selector('a')
    for link_element in all_link_elements:
        link_url = link_element.get_attribute('href')
        if "/basketball/" in link_url:
            if not link_url in game_links:
                game_links.append(link_url)

            as_str = link_element.find_element_by_xpath('..').text
            parts = as_str.split('\n')

            team1 = parts[0]
            team2 = parts[1]

            spread1 = parts[2]
            spread_odds1 = parts[3]
            money_odds1 = parts[4]
            total1 = parts[5]
            total_odds1 = parts[6]

            spread2 = parts[7]
            spread_odds2 = parts[8]
            money_odds2 = parts[9]
            total2 = parts[10]
            total_odds2 = parts[11]


            add(all_keys, "{} spread".format(team1), value="{},{}".format(spread1, spread_odds1))
            add(all_keys, "{} spread".format(team2), value="{},{}".format(spread2, spread_odds2))

            add(all_keys, "{} money".format(team1), value=money_odds1)
            add(all_keys, "{} money".format(team2), value=money_odds2)


            add(all_keys, "{} total".format(team1), value="{} {}".format(total1, total_odds1))
            add(all_keys, "{} total".format(team2), value="{} {}".format(total2, total_odds2))


    time.sleep(1.5)

    for game_link in game_links:
        game_link += "?tab=player-combos"
        print(game_link)
        parse_game_stats(driver, game_link, all_keys)



all_keys = {}

driver = webdriver.Chrome("../../master_scrape_process/chromedriver")
while True:
    parse_NBA_page(driver, all_keys)
    time.sleep(25)
# parse_game_stats(driver, "https://az.sportsbook.fanduel.com/basketball/nba/washington-wizards-@-cleveland-cavaliers-31058901?tab=player-combos", all_keys)
# parse_game_stats(driver, "https://az.sportsbook.fanduel.com/basketball/nba/new-york-knicks-@-philadelphia-76ers-31054986")