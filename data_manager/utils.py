import json
import datetime
from selenium import webdriver
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

# https://chromedriver.chromium.org/downloads
# xattr -d com.apple.quarantine <chromedriver>
def get_chrome_driver():
  return webdriver.Chrome("../master_scrape_process/chromedriver9")

def get_with_selenium(url):
  driver = get_chrome_driver()

  driver.get(url)
  as_text = driver.find_element_by_tag_name('body').text
  as_json = json.loads(as_text)
  driver.close()

  return as_json

def full_date_str():
    return str(datetime.datetime.now()).split('.')[0]

def date_str():
  return full_date_str().split(' ')[0]

def get_team_names():
  return open('team_names.txt', "r").readlines()

team_transform = {"NYK": "NY", "GSW": "GS", "PHX": "PHO", "SAS": "SA", "NOP": "NO"}
def normalize_team_name(team):
    if team in team_transform:
        return team_transform[team]

    return team
