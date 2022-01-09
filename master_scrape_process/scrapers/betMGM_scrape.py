from os import link
import time
import datetime
from tabulate import tabulate
import json
import requests
from selenium import webdriver


def get_fixtures(driver, all_team_names):
    url = "https://sports.az.betmgm.com/"
    driver.get(url)

    team_keys = []
    for team_name in all_team_names:
        team_keys.append(team_name.strip().lower().replace(" ", "-"))

    time.sleep(5)

    found_nba_links = []

    links = driver.find_elements_by_css_selector('a')
    for link_element in links:
        link_url = link_element.get_attribute('href')
        for team_key in team_keys:
            if link_url != None and team_key in link_url:
                if link_url not in found_nba_links:
                    found_nba_links.append(link_url)
                break
        


    fixture_ids = []
    for l in found_nba_links:
        if "?" in l:
            l = l.split('?')[0]
        fixture_id = l.split('-')[-1]
        fixture_ids.append(fixture_id)
    return fixture_ids


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

import unidecode

def normalize_name(name):
    name = unidecode.unidecode(name)

    name = name.replace("  ", " ")
    name = name.replace("’", "'")
    parts = name.split(" ")
    if len(parts) > 2:
        return "{} {}".format(parts[0], parts[1]).strip()

    name = name.replace(".", "")

    return name.strip()
    

fixture_ids = None

def query_betMGM(driver):

    all_team_names = open('scrapers/team_names.txt', "r").readlines()
    # all_team_names = open('team_names.txt', "r").readlines()
    all_team_names = [a.strip() for a in all_team_names]
    global fixture_ids
    # if fGM(driver):
    if fixture_ids == None:
        fixture_ids = get_fixtures(driver, all_team_names)
        
    result = query(driver, fixture_ids, all_team_names)
    return result

def query(driver, fixtures, all_team_names):

    to_return = {}
    for fixture in fixtures:

        url = 'https://cds-api.az.betmgm.com/bettingoffer/fixture-view?x-bwin-accessid=N2Q4OGJjODYtODczMi00NjhhLWJlMWItOGY5MDUzMjYwNWM5&lang=en-us&country=US&userCountry=US&subdivision=US-New%20York&offerMapping=All&scoreboardMode=Full&fixtureIds={}&state=Latest&includePrecreatedBetBuilder=true&supportVirtual=false'.format(fixture)


        #import pdb; pdb.set_trace()
        driver.get(url)

        time.sleep(1.5)

        as_text = driver.find_element_by_tag_name('body').text

        as_json = json.loads(as_text)
        for game in as_json['fixture']['games']:
            name = game['name']['value']
            matched_key = None
            matched_name = None
            for key in line_keys.keys():
                if key in name:
                    name1 = name.replace(key, "")
                    first_word = name1.split(' ')[0]
                    if first_word == "the" or first_word == "be":
                        break
                    name1 = name1.split("(")[0].strip()
                    matched_key = key
                    matched_name = name1
                    matched_name = normalize_name(matched_name)
                    break

            if matched_name in all_team_names:
                continue
            
            # if matched_key == None:
            #     print(key)
            if matched_key != None:
                stat_key = line_keys[matched_key]
                # print("{} - {}".format(stat_key, name1))
                if not matched_name in to_return:
                    to_return[matched_name] = {}
                if not stat_key in to_return[matched_name]:
                    to_return[matched_name][stat_key] = {}

                option_1 = game['results'][0]
                option_2 = game['results'][1]
                odds1 = float(option_1['odds'])
                odds2 = float(option_2['odds'])

                line = option_1["name"]["value"]
                if not "Over " in line:
                    import pdb; pdb.set_trace()
                assert "Over " in line

                try:
                    line = line.replace(",", ".")
                    line = float(line.replace("Over ", ""))
                except:
                    print("Failed to parse: {}\n{}".format(line, game))
                    del to_return[matched_name][stat_key]
                    continue

                # import pdb; pdb.set_trace()

                odds1 = 1.0 / odds1
                odds2 = 1.0 / odds2

                odds_percentage = odds1 / (odds1  + odds2)
                original_line = float(line)
                line = float(line) + (float(odds_percentage) - 0.5) * 1.5
                assert abs(line - original_line) < 0.9
                to_return[matched_name][stat_key] = str(line)


    return to_return


if __name__ == "__main__":
    driver = webdriver.Chrome("../../master_scrape_process/chromedriver")

    

    result = query_betMGM(driver)
    print(result)