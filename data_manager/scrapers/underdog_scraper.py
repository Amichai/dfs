import utils
import requests

class UnderdogScraper:
  def __init__(self, sport):
    self.sport = sport
    self.name = 'Underdog'

  def run(self):
    headers = {
        'authority': 'api.underdogfantasy.com',
        'accept': 'application/json',
        'accept-language': 'en-US,en;q=0.9',
        # 'authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJiNzc3ZDVjZi0yMWE1LTQ2ZDYtODMwZi1kOTA3ZGQzNGVmYmIiLCJzdWIiOiI4NjhjOGM3OS02NWVmLTQzNjktOWUzOS0xZjAyOTUzNzI3YmMiLCJzY3AiOiJ1c2VyIiwiYXVkIjpudWxsLCJpYXQiOjE2NjM2Nzg4NzUsImV4cCI6MTY2NjMwODYyMX0.63wmI6VOdKvvQ_V2jdmEHVgCUb1upncMywnqN64ZanE',
        'client-device-id': '46643284-b1f6-4ebd-ab18-6a17e6051518',
        'client-request-id': '174c7ff5-d35c-42b3-b419-aa42a2fdb000',
        'client-type': 'web',
        'client-version': '202209161743',
        'if-none-match': 'W/"3e8872284b7c98edc1ed9ae1aad0a61d"',
        'origin': 'https://underdogfantasy.com',
        'referer': 'https://underdogfantasy.com/',
        'referring-link': 'https://play.underdogfantasy.com/jkidd1084',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        'user-latitude': '40.9053191',
        'user-longitude': '-73.7857316',
    }

    response = requests.get('https://api.underdogfantasy.com/beta/v3/over_under_lines', headers=headers)

    as_json = response.json()

    appearances = as_json['appearances']
    appearance_id_to_game_id = {}
    for appearance in appearances:
      appearance_id_to_game_id[appearance['id']] = appearance['match_id']

    games = as_json["games"]
    game_id_to_sport_id = {}
    for game in games:
      game_id = game['id']
      sport_id = game['sport_id']
      game_id_to_sport_id[game_id] = sport_id


    lines = as_json['over_under_lines']
    name_to_projections = {}
    for line in lines:
      value = line['stat_value']

      stat = line['over_under']['appearance_stat']['display_stat']
      appearance_id = line['over_under']['appearance_stat']['appearance_id']

      game_id = appearance_id_to_game_id[appearance_id]
      if not game_id in game_id_to_sport_id:
        continue
      
      sport_id = game_id_to_sport_id[game_id]
      if sport_id != self.sport:
        continue

      title = line['over_under']['title']
      
      name = title.replace(" {} O/U".format(stat), "")
      name = utils.normalize_name(name)

      if not name in name_to_projections:
        name_to_projections[name] = {}
      
      name_to_projections[name][stat] = value

    return name_to_projections
