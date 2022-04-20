from os import link
from datetime import timedelta, date
import time
import datetime
from bs4.element import NamespacedAttribute
from tabulate import tabulate
import json
import requests
from selenium import webdriver
import dateutil.parser

# logging.basicConfig(filename='master_scraper.log', encoding='utf-8', level=logging.INFO)
# logger = logging.getLogger("Caesars")

def time_str():
    return str(datetime.datetime.now()).split('.')[0]

def assert_start_times_are_sorted(start_times):
    #dateutil.parser.isoparse('2022-03-30T02:00:00Z')
    times_parsed = [dateutil.parser.isoparse(a) for a in start_times]

    times_sorted = sorted(times_parsed)
    for i in range(len(times_sorted)):
        assert times_sorted[i] == times_parsed[i]


def normalize_name(name):
    name = name.replace("  ", " ")
    name = name.replace("’", "'")
    parts = name.split(" ")
    if len(parts) > 2:
        return "{} {}".format(parts[0], parts[1]).strip()

    name = name.replace(".", "")

    return name.strip()
    

def query_dfscrunch():
    result = query()
    return result

def query():
        
    cookies = {
        'pysTrafficSource': 'google.com',
        'pys_landing_page': 'https://www.dfscrunch.com/',
        '__stripe_mid': 'aff86e69-c10e-4f99-886b-1f5478285367d22a20',
        'wordpress_logged_in_83047575d15e8d1240c169eeadbad409': 'aml%7C1650483115%7CbVD35TrQPwoSDtEUn3GXx8KBa1VkFuXP4CmsKthx5VZ%7C8e91887b6e33e8ee81643be2bfcde1449d96917cf69fae5e51ca1785d800993b',
        '_gcl_au': '1.1.2065696358.1650310402',
        '__stripe_sid': 'db637670-2372-493e-b0a6-88c2510a9c176b9e70',
    }

    headers = {
        'authority': 'www.dfscrunch.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,he;q=0.8',
        # Requests sorts cookies= alphabetically
        # 'cookie': 'pysTrafficSource=google.com; pys_landing_page=https://www.dfscrunch.com/; __stripe_mid=aff86e69-c10e-4f99-886b-1f5478285367d22a20; wordpress_logged_in_83047575d15e8d1240c169eeadbad409=aml%7C1650483115%7CbVD35TrQPwoSDtEUn3GXx8KBa1VkFuXP4CmsKthx5VZ%7C8e91887b6e33e8ee81643be2bfcde1449d96917cf69fae5e51ca1785d800993b; _gcl_au=1.1.2065696358.1650310402; __stripe_sid=db637670-2372-493e-b0a6-88c2510a9c176b9e70',
        'referer': 'https://www.dfscrunch.com/tool/nba/fanduel',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
    }

    params = {
        'currentPage': '1',
        'pageSize': '20',
        'site': 'fanduel',
        'slate': 'fd74800',
    }
    to_return = {}
    all_players = []

    response = requests.get('https://www.dfscrunch.com/api/v1/nba/players/', headers=headers, params=params, cookies=cookies)
    all_players += response.json()
    print(len(all_players))

    for player in all_players:
        name = player['name']
        name = normalize_name(name)
        proj = player['pfp']
        to_return[name] = {"crunch_projected": proj}
        pass


    return to_return


if __name__ == "__main__":
    result = query_dfscrunch()
    print(result)