import requests
import utils

query_parameters = {
    'cookies': {
    'pys_start_session': 'true',
    '_gcl_au': '1.1.1267622578.1667136773',
    'last_pys_landing_page': 'https://www.dfscrunch.com/',
    '_ga': 'GA1.2.698555203.1667136774',
    '_fbp': 'fb.1.1667136773620.1727448397',
    '__stripe_mid': '45055897-96ba-46bb-8cf3-16a336af06f4a6381a',
    'tk_ai': 'jetpack%3AmEAM9XamI7PIqp4FV%2FE35%2FLQ',
    'wordpress_test_cookie': 'WP%20Cookie%20check',
    'wp_lang': 'en_US',
    'pys_advanced_form_data': '%7B%22first_name%22%3A%22Amichai%22%2C%22last_name%22%3A%22Levy%22%2C%22email%22%3A%22amichaimlevy%40gmail.com%22%2C%22phone%22%3A%22%22%7D',
    'wordpress_logged_in_83047575d15e8d1240c169eeadbad409': 'aml%7C1669732768%7C90qDxLDxsDkZNv7prwHzOV9aak7TZmEJCQaPMrDPCF9%7Cd100684bfb5a00da8ac002ff191ab92d95642eb11d34ff6256fdb91f0eed67ac',
    'last_pysTrafficSource': 'direct',
    '__insp_uid': '1266658190',
    'pys_first_visit': 'true',
    'pysTrafficSource': 'direct',
    'pys_landing_page': 'https://www.dfscrunch.com/',
    '_gid': 'GA1.2.1209811197.1667782476',
    'csrftoken': 'ZhLA3MIT5rPn4cbe1Rk1gAQo3Y6KdhFvaHIZL7CoWtHOy1LSrXJrggALMyvxs1Ru',
    '__insp_wid': '454073064',
    '__insp_nv': 'false',
    '__insp_targlpu': 'aHR0cHM6Ly93d3cuZGZzY3J1bmNoLmNvbS90b29sL25iYS9mYW5kdWVs',
    '__insp_targlpt': 'RmFuZHVlbCBOQkEgLSBERlMgQ3J1bmNoOiBUb3AgREZTIGxpbmV1cCBvcHRpbWl6ZXIgdG9vbA%3D%3D',
    '__insp_identity': 'YW1s',
    '__insp_sid': '810662779',
    'pys_session_limit': 'true',
    '__stripe_sid': 'c03da41e-cabf-4c40-a008-c20d3c47fda30c921b',
    '_gat_gtag_UA_170864106_1': '1',
    '_gat': '1',
    '__insp_slim': '1668125262932',
    '__insp_pad': '9',
  },

  'headers': {
    'authority': 'www.dfscrunch.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    # Requests sorts cookies= alphabetically
    # 'cookie': 'pys_start_session=true; _gcl_au=1.1.1267622578.1667136773; last_pys_landing_page=https://www.dfscrunch.com/; _ga=GA1.2.698555203.1667136774; _fbp=fb.1.1667136773620.1727448397; __stripe_mid=45055897-96ba-46bb-8cf3-16a336af06f4a6381a; tk_ai=jetpack%3AmEAM9XamI7PIqp4FV%2FE35%2FLQ; wordpress_test_cookie=WP%20Cookie%20check; wp_lang=en_US; pys_advanced_form_data=%7B%22first_name%22%3A%22Amichai%22%2C%22last_name%22%3A%22Levy%22%2C%22email%22%3A%22amichaimlevy%40gmail.com%22%2C%22phone%22%3A%22%22%7D; wordpress_logged_in_83047575d15e8d1240c169eeadbad409=aml%7C1669732768%7C90qDxLDxsDkZNv7prwHzOV9aak7TZmEJCQaPMrDPCF9%7Cd100684bfb5a00da8ac002ff191ab92d95642eb11d34ff6256fdb91f0eed67ac; last_pysTrafficSource=direct; __insp_uid=1266658190; pys_first_visit=true; pysTrafficSource=direct; pys_landing_page=https://www.dfscrunch.com/; _gid=GA1.2.1209811197.1667782476; csrftoken=ZhLA3MIT5rPn4cbe1Rk1gAQo3Y6KdhFvaHIZL7CoWtHOy1LSrXJrggALMyvxs1Ru; __insp_wid=454073064; __insp_nv=false; __insp_targlpu=aHR0cHM6Ly93d3cuZGZzY3J1bmNoLmNvbS90b29sL25iYS9mYW5kdWVs; __insp_targlpt=RmFuZHVlbCBOQkEgLSBERlMgQ3J1bmNoOiBUb3AgREZTIGxpbmV1cCBvcHRpbWl6ZXIgdG9vbA%3D%3D; __insp_identity=YW1s; __insp_sid=810662779; pys_session_limit=true; __stripe_sid=c03da41e-cabf-4c40-a008-c20d3c47fda30c921b; _gat_gtag_UA_170864106_1=1; _gat=1; __insp_slim=1668125262932; __insp_pad=9',
    'referer': 'https://www.dfscrunch.com/tool/nba/fanduel',
    'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
  },
      
  'NBA': {
    'params': {
        'currentPage': '1',
        'pageSize': '20000',
        'site': 'fanduel',
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
    assert sport == "NBA" or sport == "MLB" or sport == "WNBA" or sport == "CBB"
    self.name = 'DFSCrunch'
    self.slate = slate

  def run(self):
    to_return = {}
    all_players = []
    url = query_parameters[self.sport]['url']
    params = query_parameters[self.sport]['params']

    params['slate'] = self.slate
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
