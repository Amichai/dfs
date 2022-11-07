import requests
import utils

query_parameters = {
    'cookies': {
      'pys_start_session': 'true',
      '_gcl_au': '1.1.1267622578.1667136773',
      'pys_first_visit': 'true',
      'pysTrafficSource': 'google.com',
      'pys_landing_page': 'https://www.dfscrunch.com/',
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
      '_gid': 'GA1.2.249510560.1667602117',
      'pys_session_limit': 'true',
      '_gat_gtag_UA_170864106_1': '1',
      '__stripe_sid': '19c89a6a-355d-4acb-b91d-ed977907dc05789a77',
      '_gat': '1',
      '__insp_wid': '454073064',
      '__insp_nv': 'false',
      '__insp_targlpu': 'aHR0cHM6Ly93d3cuZGZzY3J1bmNoLmNvbS90b29sL25iYS9mYW5kdWVs',
      '__insp_targlpt': 'RmFuZHVlbCBOQkEgLSBERlMgQ3J1bmNoOiBUb3AgREZTIGxpbmV1cCBvcHRpbWl6ZXIgdG9vbA%3D%3D',
      '__insp_identity': 'YW1s',
      '__insp_norec_sess': 'true',
      '__insp_slim': '1667609280419',
  },

  'headers': {
    'authority': 'www.dfscrunch.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    # Requests sorts cookies= alphabetically
    # 'cookie': '_ga=GA1.2.533451439.1650313841; _fbp=fb.1.1650313840977.2069460979; __stripe_mid=8c13fafc-05bf-4035-b8ca-f4e6a813335fe77c3d; _gcl_au=1.1.1032849673.1650313862; __insp_uid=1926867235; _gid=GA1.2.558654011.1654118789; _gat=1; pys_landing_page=https://www.dfscrunch.com/register; _gat_gtag_UA_170864106_1=1; __stripe_sid=fdf3fe79-296e-4848-96fd-f0f30399ce4dd9f185; wordpress_logged_in_83047575d15e8d1240c169eeadbad409=aml%7C1655328398%7CibOk5nUqDbxZFeqSv30tn3VIcJgg6ccCVC5dWyzlRix%7Cd5ba5d9dd4cf75f17bac5b743637c704cffba4a9c9cd7070857d4a2f2293a451; __insp_wid=454073064; __insp_nv=false; __insp_targlpu=aHR0cHM6Ly93d3cuZGZzY3J1bmNoLmNvbS90b29sL21sYi9mYW5kdWVs; __insp_targlpt=RmFuZHVlbCBNTEIgLSBERlMgQ3J1bmNoOiBUb3AgREZTIGxpbmV1cCBvcHRpbWl6ZXIgdG9vbA%3D%3D; __insp_identity=YW1s; __insp_sid=2939320407; __insp_slim=1654118814067; __insp_pad=2',
    'referer': 'https://www.dfscrunch.com/tool/mlb/fanduel',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36',
  },
      
  'NBA': {
    'params': {
        'currentPage': '1',
        'pageSize': '20000',
        'site': 'fanduel',
        'slate': 'fd82909',
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
