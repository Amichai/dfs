import requests
from selenium import webdriver
from datetime import timedelta, date
import dateutil.parser
import utils
import json
import time

class CaesarsScraper:
  def __init__(self, sport):
    self.sport = sport
    self.name = 'Caesars'

    assert sport == "NBA" or sport == "WNBA" or sport == "MLB"
    self.game_guids = None
    if sport == 'NBA' or sport == 'WNBA':
      self.sport_name = "basketball"
    elif sport == "MLB":
      self.sport_name = "baseball"
      

    self.driver = utils.get_chrome_driver()
    self.all_team_names = ["Atlanta Hawks","Boston Celtics","Brooklyn Nets","Charlotte Hornets","Chicago Bulls","Cleveland Cavaliers","Dallas Mavericks","Denver Nuggets","Detroit Pistons","Golden State Warriors","Houston Rockets","Indiana Pacers","Los Angeles Clippers","Los Angeles Lakers","Memphis Grizzlies","Miami Heat","Milwaukee Bucks","Minnesota Timberwolves","New Orleans Pelicans","New York Knicks","Oklahoma City Thunder","Orlando Magic","Philadelphia 76ers","Phoenix Suns","Portland Trail Blazers","Sacramento Kings","San Antonio Spurs","Toronto Raptors","Utah Jazz","Washington Wizards"]

  def _get_game_guids_today(self):
    url = "https://www.williamhill.com/us/az/bet/api/v3/sports/{}/events/schedule".format(self.sport_name)
    result = requests.get(url)
    as_json = result.json()

    all_sports = [a['name'] for a in as_json['competitions']]
    target_index = all_sports.index(self.sport)

    events = as_json['competitions'][target_index]['events']

    counter = 1
    all_start_times = []
    to_return = []
    for event in events:
        event_id = event["id"]
        name = event["name"]
        start_time = event["startTime"]
        start_time_parsed = dateutil.parser.isoparse(start_time)
        time_shifted = start_time_parsed - timedelta(hours=4)

        all_start_times.append(start_time)

        if time_shifted.day == date.today().day:
            counter += 1
            print("{} - {}, {}, {}".format(counter, name, time_shifted.strftime('%m/%d %H:%M'), event_id))
            to_return.append(event_id)

    return to_return

  def run(self):
    to_return = {}

    if self.game_guids == None:
      self.game_guids = self._get_game_guids_today()

    for guid in self.game_guids:
        url = 'https://www.williamhill.com/us/az/bet/api/v2/events/{}'.format(guid)

        self.driver.get(url)

        time.sleep(1.5)

        as_text = self.driver.find_element_by_tag_name('body').text

        as_json = json.loads(as_text)
        
        for market in as_json['markets']:
            selections = market['selections']
            name = market['name']

            is_active = market['active']

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

            name = name_parts[0].strip('|')
            if name in self.all_team_names:
              continue

            stat = name_parts[1].strip('|').replace('Total ', '')
            if stat == "3pt Field Goals":
              continue

            name = utils.normalize_name(name)

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
   
            line_adjusted = round(float(line) + (float(odds_percentage) - 0.5) * float(line), 3)

            to_return[name][stat] = str(line_adjusted)
            to_return[name]["{}:isActive".format(stat)] = is_active

    return to_return