import requests
# import utils

query_parameters = {
    'cookies': {
      '_gcl_au': '1.1.1744680549.1687791418',
      '_gid': 'GA1.2.1015664375.1687791418',
      '__stripe_mid': 'bca93eba-ca86-4fbb-8aeb-d25e13b5f882d3d909',
      '__insp_wid': '454073064',
      '__insp_nv': 'true',
      '__insp_targlpu': 'aHR0cHM6Ly93d3cuZGZzY3J1bmNoLmNvbS90b29sL25iYS9mYW5kdWVs',
      '__insp_targlpt': 'RmFuZHVlbCBOQkEgLSBERlMgQ3J1bmNoOiBUb3AgREZTIGxpbmV1cCBvcHRpbWl6ZXIgdG9vbA%3D%3D',
      '__insp_identity': 'YW1s',
      '__insp_sid': '1146553789',
      '__insp_uid': '2668394760',
      'wordpress_test_cookie': 'WP%20Cookie%20check',
      '_ga': 'GA1.2.543296803.1687791418',
      'wordpress_logged_in_83047575d15e8d1240c169eeadbad409': 'aml%7C1690383672%7CwmE7PP3u4H704DSp5nVbwyMQ6eeKipcD8ki4QFmQZjG%7Ca7a0625db5cc2e8c0c61b6826c1102078dc2eb111371164e281c241320fff6b7',
      'pys_advanced_form_data': '%7B%22first_name%22%3A%22Amichai%22%2C%22last_name%22%3A%22Levy%22%2C%22email%22%3A%22amichaimlevy%40gmail.com%22%2C%22phone%22%3A%22%22%7D',
      '__stripe_sid': '29ffffde-389e-4be2-bc78-c5b580aafcc7ac232a',
      '_gat': '1',
      '_ga_828EVXX1Q3': 'GS1.2.1687794118.2.1.1687795517.0.0.0',
      '__insp_slim': '1687795517929',
      '__insp_pad': '11',
    },

    'headers':{
      'authority': 'www.dfscrunch.com',
      'accept': '*/*',
      'accept-language': 'en-US,en;q=0.9',
      # 'cookie': '_gcl_au=1.1.1744680549.1687791418; _gid=GA1.2.1015664375.1687791418; __stripe_mid=bca93eba-ca86-4fbb-8aeb-d25e13b5f882d3d909; __insp_wid=454073064; __insp_nv=true; __insp_targlpu=aHR0cHM6Ly93d3cuZGZzY3J1bmNoLmNvbS90b29sL25iYS9mYW5kdWVs; __insp_targlpt=RmFuZHVlbCBOQkEgLSBERlMgQ3J1bmNoOiBUb3AgREZTIGxpbmV1cCBvcHRpbWl6ZXIgdG9vbA%3D%3D; __insp_identity=YW1s; __insp_sid=1146553789; __insp_uid=2668394760; wordpress_test_cookie=WP%20Cookie%20check; _ga=GA1.2.543296803.1687791418; wordpress_logged_in_83047575d15e8d1240c169eeadbad409=aml%7C1690383672%7CwmE7PP3u4H704DSp5nVbwyMQ6eeKipcD8ki4QFmQZjG%7Ca7a0625db5cc2e8c0c61b6826c1102078dc2eb111371164e281c241320fff6b7; pys_advanced_form_data=%7B%22first_name%22%3A%22Amichai%22%2C%22last_name%22%3A%22Levy%22%2C%22email%22%3A%22amichaimlevy%40gmail.com%22%2C%22phone%22%3A%22%22%7D; __stripe_sid=29ffffde-389e-4be2-bc78-c5b580aafcc7ac232a; _gat=1; _ga_828EVXX1Q3=GS1.2.1687794118.2.1.1687795517.0.0.0; __insp_slim=1687795517929; __insp_pad=11',
      'referer': 'https://www.dfscrunch.com/tool/mlb/fanduel',
      'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
      'sec-ch-ua-mobile': '?0',
      'sec-ch-ua-platform': '"macOS"',
      'sec-fetch-dest': 'empty',
      'sec-fetch-mode': 'cors',
      'sec-fetch-site': 'same-origin',
      'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
  },
      
  'NBA': {
    'params': {
        'currentPage': '1',
        'pageSize': '20000',
        'site': 'fanduel',
    },
    'url': 'https://www.dfscrunch.com/api/v1/nba/players/'
  },

  'NFL': {
    'params': {
        'currentPage': '1',
        'pageSize': '20000',
        'site': 'fanduel',
    },
    'url': 'https://www.dfscrunch.com/api/v1/nfl/players/'
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
      'slate': 'fd76886',
    },
    'url':'https://www.dfscrunch.com/api/v1/mlb/players/'
  },
  
  'CBB': {
    'params': {
      'currentPage': '1',
      'pageSize': '20',
      'site': 'draftkings',
    },
    'url':' https://www.dfscrunch.com/api/v1/cbb/players'
  },
}


class DFSCrunchScraper:
  def __init__(self, sport, slate):
    self.sport = sport
    assert sport == "NBA" or sport == "MLB" or sport == "WNBA" or sport == "CBB" or sport == "NFL"
    self.name = 'DFSCrunch'
    self.slate = slate

  def run(self):
    to_return = {}
    all_players = []
    url = query_parameters[self.sport]['url']
    params = query_parameters[self.sport]['params']

    params['slate'] = 'fd' + str(self.slate)

    headers = query_parameters['headers']
    cookies = query_parameters['cookies']

    response = requests.get(url, headers=headers, params=params, cookies=cookies)

    print(response)

    all_players += response.json()
    print("Players: {}".format(len(all_players)))

    for player in all_players:
        name = player['name']
        # name = utils.normalize_name(name)
        # proj = player['pfp']
        to_return[name] = player


    return to_return
