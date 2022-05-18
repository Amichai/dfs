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
        '_ga': 'GA1.2.533451439.1650313841',
        '_fbp': 'fb.1.1650313840977.2069460979',
        '__stripe_mid': '8c13fafc-05bf-4035-b8ca-f4e6a813335fe77c3d',
        '_gcl_au': '1.1.1032849673.1650313862',
        '__insp_uid': '1926867235',
        '_gid': 'GA1.2.1536937254.1652386568',
        'wordpress_logged_in_83047575d15e8d1240c169eeadbad409': 'aml%7C1652559374%7CXPsbLu1Qlzk1pS2gcFaygw7xeZxA8Ghk5RZdDvdgsm0%7Ca5d647b1e18455fc43886ce3bd91ee9428ecd9500e53df138baa3999a960d3f6',
        '__insp_wid': '454073064',
        '__insp_nv': 'false',
        '__insp_targlpu': 'aHR0cHM6Ly93d3cuZGZzY3J1bmNoLmNvbS90b29sL21sYi9mYW5kdWVs',
        '__insp_targlpt': 'RmFuZHVlbCBNTEIgLSBERlMgQ3J1bmNoOiBUb3AgREZTIGxpbmV1cCBvcHRpbWl6ZXIgdG9vbA%3D%3D',
        '__insp_identity': 'YW1s',
        '__insp_sid': '2609592022',
        '__stripe_sid': '5332f7a4-3f23-4dfa-9274-8d51790d3edd88616c',
        '_gat': '1',
        '__insp_slim': '1652393980101',
        '__insp_pad': '3',
    }

    headers = {
        'authority': 'www.dfscrunch.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        # Requests sorts cookies= alphabetically
        # 'cookie': 'pysTrafficSource=google.com; _ga=GA1.2.533451439.1650313841; _fbp=fb.1.1650313840977.2069460979; __stripe_mid=8c13fafc-05bf-4035-b8ca-f4e6a813335fe77c3d; _gcl_au=1.1.1032849673.1650313862; __insp_uid=1926867235; _gid=GA1.2.1536937254.1652386568; wordpress_logged_in_83047575d15e8d1240c169eeadbad409=aml%7C1652559374%7CXPsbLu1Qlzk1pS2gcFaygw7xeZxA8Ghk5RZdDvdgsm0%7Ca5d647b1e18455fc43886ce3bd91ee9428ecd9500e53df138baa3999a960d3f6; __insp_wid=454073064; __insp_nv=false; __insp_targlpu=aHR0cHM6Ly93d3cuZGZzY3J1bmNoLmNvbS90b29sL21sYi9mYW5kdWVs; __insp_targlpt=RmFuZHVlbCBNTEIgLSBERlMgQ3J1bmNoOiBUb3AgREZTIGxpbmV1cCBvcHRpbWl6ZXIgdG9vbA%3D%3D; __insp_identity=YW1s; __insp_sid=2609592022; __stripe_sid=5332f7a4-3f23-4dfa-9274-8d51790d3edd88616c; _gat=1; __insp_slim=1652393980101; __insp_pad=3',
        'referer': 'https://www.dfscrunch.com/tool/nba/fanduel',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36',
    }

    params = {
        'currentPage': '1',
        'pageSize': '20',
        'site': 'fanduel',
        'slate': 'fd76021',
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