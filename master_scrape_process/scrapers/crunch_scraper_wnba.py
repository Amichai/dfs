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
        '_gid': 'GA1.2.186266203.1651499023',
        'pys_landing_page': 'https://www.dfscrunch.com/register/',
        'wordpress_logged_in_83047575d15e8d1240c169eeadbad409': 'aml%7C1651960324%7ChgHHwuU3eZhIeVpGWS1cInwcy7aFE6mcPKpjtfjbq7y%7C058952b331b57b16a85739c8d1579041f93098da77607ce395fe253e0296976b',
        '__insp_wid': '454073064',
        '__insp_nv': 'false',
        '__insp_targlpu': 'aHR0cHM6Ly93d3cuZGZzY3J1bmNoLmNvbS90b29sL25iYS9mYW5kdWVs',
        '__insp_targlpt': 'RmFuZHVlbCBOQkEgLSBERlMgQ3J1bmNoOiBUb3AgREZTIGxpbmV1cCBvcHRpbWl6ZXIgdG9vbA%3D%3D',
        '__insp_identity': 'YW1s',
        '__insp_sid': '2563656178',
        '__stripe_sid': 'ba39b776-8954-415b-a6c4-f2ebc447717bd17c24',
        '_gat': '1',
        '__insp_slim': '1651876399086',
        '__insp_pad': '6',
    }

    headers = {
        'authority': 'www.dfscrunch.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        # Requests sorts cookies= alphabetically
        # 'cookie': 'pysTrafficSource=google.com; _ga=GA1.2.533451439.1650313841; _fbp=fb.1.1650313840977.2069460979; __stripe_mid=8c13fafc-05bf-4035-b8ca-f4e6a813335fe77c3d; _gcl_au=1.1.1032849673.1650313862; __insp_uid=1926867235; _gid=GA1.2.186266203.1651499023; pys_landing_page=https://www.dfscrunch.com/register/; wordpress_logged_in_83047575d15e8d1240c169eeadbad409=aml%7C1651960324%7ChgHHwuU3eZhIeVpGWS1cInwcy7aFE6mcPKpjtfjbq7y%7C058952b331b57b16a85739c8d1579041f93098da77607ce395fe253e0296976b; __insp_wid=454073064; __insp_nv=false; __insp_targlpu=aHR0cHM6Ly93d3cuZGZzY3J1bmNoLmNvbS90b29sL25iYS9mYW5kdWVs; __insp_targlpt=RmFuZHVlbCBOQkEgLSBERlMgQ3J1bmNoOiBUb3AgREZTIGxpbmV1cCBvcHRpbWl6ZXIgdG9vbA%3D%3D; __insp_identity=YW1s; __insp_sid=2563656178; __stripe_sid=ba39b776-8954-415b-a6c4-f2ebc447717bd17c24; _gat=1; __insp_slim=1651876399086; __insp_pad=6',
        'referer': 'https://www.dfscrunch.com/tool/wnba/fanduel',
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
        'slate': 'fd75628',
    }

    to_return = {}
    all_players = []

    response = requests.get('https://www.dfscrunch.com/api/v1/wnba/players/', params=params, cookies=cookies, headers=headers)

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