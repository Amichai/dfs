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
    'pys_landing_page': 'https://www.dfscrunch.com/register/',
    '_gid': 'GA1.2.149284961.1652739773',
    'wordpress_logged_in_83047575d15e8d1240c169eeadbad409': 'aml%7C1653950790%7CEdyF76Dpz00Gaqmh4oAfGSM3Tf0dvAxbCwXGZjYrXxw%7C72e44912bc35ab3b5b09e3fc86bdf16d865b820de7f04e100ec6e3b2fdfe4dce',
    '__insp_wid': '454073064',
    '__insp_nv': 'false',
    '__insp_targlpu': 'aHR0cHM6Ly93d3cuZGZzY3J1bmNoLmNvbS90b29sL21sYi9mYW5kdWVs',
    '__insp_targlpt': 'RmFuZHVlbCBNTEIgLSBERlMgQ3J1bmNoOiBUb3AgREZTIGxpbmV1cCBvcHRpbWl6ZXIgdG9vbA%3D%3D',
    '__insp_identity': 'YW1s',
    '__insp_sid': '2177171373',
    '__stripe_sid': 'b7c46d39-c6c8-4e26-b052-37f5c2b33773e2e946',
    '_gat': '1',
    '__insp_slim': '1652824340768',
    '__insp_pad': '3',
  },

  'headers': {
    'authority': 'www.dfscrunch.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    # Requests sorts cookies= alphabetically
    # 'cookie': 'pysTrafficSource=google.com; _ga=GA1.2.533451439.1650313841; _fbp=fb.1.1650313840977.2069460979; __stripe_mid=8c13fafc-05bf-4035-b8ca-f4e6a813335fe77c3d; _gcl_au=1.1.1032849673.1650313862; __insp_uid=1926867235; pys_landing_page=https://www.dfscrunch.com/register/; _gid=GA1.2.149284961.1652739773; wordpress_logged_in_83047575d15e8d1240c169eeadbad409=aml%7C1653950790%7CEdyF76Dpz00Gaqmh4oAfGSM3Tf0dvAxbCwXGZjYrXxw%7C72e44912bc35ab3b5b09e3fc86bdf16d865b820de7f04e100ec6e3b2fdfe4dce; __insp_wid=454073064; __insp_nv=false; __insp_targlpu=aHR0cHM6Ly93d3cuZGZzY3J1bmNoLmNvbS90b29sL21sYi9mYW5kdWVs; __insp_targlpt=RmFuZHVlbCBNTEIgLSBERlMgQ3J1bmNoOiBUb3AgREZTIGxpbmV1cCBvcHRpbWl6ZXIgdG9vbA%3D%3D; __insp_identity=YW1s; __insp_sid=2177171373; __stripe_sid=b7c46d39-c6c8-4e26-b052-37f5c2b33773e2e946; _gat=1; __insp_slim=1652824340768; __insp_pad=3',
    'referer': 'https://www.dfscrunch.com/tool/mlb/fanduel',
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
      'slate': 'fd76281',
    },
    'url': 'https://www.dfscrunch.com/api/v1/wnba/players'
  },
  
  'MLB': {
    'params': {
      'currentPage': '1',
      'pageSize': '20',
      'site': 'fanduel',
      'slate': 'fd76281',
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
        if player['batting_order'] == None:
          continue
        # if "Luplow" in name:
        # print(player)
        to_return[name] = {"Fantasy Score": proj}


    return to_return
