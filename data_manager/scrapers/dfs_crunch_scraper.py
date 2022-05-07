import requests
import utils

query_parameters = {
  'cookies': {
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
        '__insp_slim': '1651875617074',
        '__insp_pad': '3',
    },

  'headers': {
        'authority': 'www.dfscrunch.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        # Requests sorts cookies= alphabetically
        # 'cookie': 'pysTrafficSource=google.com; _ga=GA1.2.533451439.1650313841; _fbp=fb.1.1650313840977.2069460979; __stripe_mid=8c13fafc-05bf-4035-b8ca-f4e6a813335fe77c3d; _gcl_au=1.1.1032849673.1650313862; __insp_uid=1926867235; _gid=GA1.2.186266203.1651499023; pys_landing_page=https://www.dfscrunch.com/register/; wordpress_logged_in_83047575d15e8d1240c169eeadbad409=aml%7C1651960324%7ChgHHwuU3eZhIeVpGWS1cInwcy7aFE6mcPKpjtfjbq7y%7C058952b331b57b16a85739c8d1579041f93098da77607ce395fe253e0296976b; __insp_wid=454073064; __insp_nv=false; __insp_targlpu=aHR0cHM6Ly93d3cuZGZzY3J1bmNoLmNvbS90b29sL25iYS9mYW5kdWVs; __insp_targlpt=RmFuZHVlbCBOQkEgLSBERlMgQ3J1bmNoOiBUb3AgREZTIGxpbmV1cCBvcHRpbWl6ZXIgdG9vbA%3D%3D; __insp_identity=YW1s; __insp_sid=2563656178; __stripe_sid=ba39b776-8954-415b-a6c4-f2ebc447717bd17c24; _gat=1; __insp_slim=1651875617074; __insp_pad=3',
        'referer': 'https://www.dfscrunch.com/tool/nba/fanduel',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36',
    },
    
  'NBA': {
    'params': {
        'currentPage': '1',
        'pageSize': '20',
        'site': 'fanduel',
        'slate': 'fd75769',
    },
    'url': 'https://www.dfscrunch.com/api/v1/nba/players/'
  },

  'WNBA': {
    'params': {
      'currentPage': '1',
      'pageSize': '20',
      'site': 'fanduel',
      'slate': 'fd75774',
    },
    'url': 'https://www.dfscrunch.com/api/v1/wnba/players'
  },
  
  'MLB': {
    'params': {
      'currentPage': '1',
      'pageSize': '20',
      'position': 'P',
      'site': 'fanduel',
      'slate': 'fd75778',
    },
    'url':'https://www.dfscrunch.com/api/v1/mlb/players/'
  }
}




class DFSCrunchScraper:
  def __init__(self, sport):
    self.sport = sport
    assert sport == "NBA" or sport == "MLB" or sport == "WNBA"
    self.name = 'DFSCrunch'

  def run(self):
    to_return = {}
    all_players = []
    url = query_parameters[self.sport]['url']
    params = query_parameters[self.sport]['params']
    headers = query_parameters['headers']
    cookies = query_parameters['cookies']

    response = requests.get(url, headers=headers, params=params, cookies=cookies)
    all_players += response.json()
    print("Players: {}".format(len(all_players)))

    for player in all_players:
        name = player['name']
        name = utils.normalize_name(name)
        proj = player['pfp']
        to_return[name] = {"Fantasy Score": proj}


    return to_return
