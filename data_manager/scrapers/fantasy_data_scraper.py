import utils
import json
import requests

cookies = {
    '_ga': 'GA1.2.541165235.1667065536',
    '_gid': 'GA1.2.960933076.1667065536',
    '_omappvp': '2wuX8coiTlPdTYLV3SrgHGuVZ19PU7tOu6CWgpkdEz9LVBRAzGLKq4wfHtNUVyYkapDziPRbgp7rnsHryH26alOzTYTeF5nH',
    'usprivacy': '1---',
    '_pbjs_userid_consent_data': '3524755945110770',
    '_cioanonid': '53a054a6-e80c-c739-7709-021c41ff9544',
    '__gads': 'ID=a041101f8e5b908a:T=1667065538:S=ALNI_MajBsAswtpp4jKPSjAdLXqiL8s2pw',
    '__gpi': 'UID=000009cfe65319ab:T=1667065538:RT=1667065538:S=ALNI_MaWicOHYMuU3x7WM-I3HCby60kz0A',
    '__adroll_fpc': '46d41c62e88bb2e267c1e15314bb8837-1667065540836',
    '_fbp': 'fb.1.1667065541436.1264983436',
    '_lr_env_src_ats': 'false',
    'cto_bundle': '93pvy19OdVhuT21RQlJ4SG1QaThuSEd5elZWNWRSWFFUeVR2cm5HeTg4b3lBTHNoWXJEQjF5WThZSWduZzVWZE9Bd3dMbmN0MW9aTUQ3a1p0aiUyRkZmZTZZVzRwdnUxUGdRNWFWbm1FZk5DcSUyRk1RSCUyRjA5UmZaZGIzYmFxQzFOaldPRTlBSVZ4WU9EUlQlMkZidEJjQzc2M2k4OXhKdFh0OVk4UGElMkJZcG9TYTZiMkNNaThRblNQOFBxNVRMZnpWZnVERmglMkZuJTJGR3hmNmdwdGRLRUFubmQxbUR2aGl1WFElM0QlM0Q',
    'cto_bidid': '98k49V9mYVdLdTdrV2ROOG0lMkZNYTJWZnN2RTJEaVNvcmN0ZXdsZWhZTnlZS3BYajMlMkZnMzFjUEZOOVRGb0xhME0yNVBJWWMzYjVpTzlZaTdVWHNGUVNZM09LJTJGeDFKUEJlJTJGTXZOWjdQU1FhRmwwSlFxNFdvSnZPckVSN0JnVzYlMkZ1RmMlMkJ6Q0pJYWVkQzQ4WmVDTm0lMkYyYWJsb2FOUSUzRCUzRA',
    '_ss_form_36d045e2-68e7-4992-8962-254f0898faa2': '1',
    'ASP.NET_SessionId': 'un030faftcmvsfuehobdi1jm',
    'ks03ndsapqq84662kglvmcya009273nhdkwsn': '88006548-2c39-4452-8e5d-44a467baadd4',
    '_cioid': '87962',
    'cto_bundle': 'g9zpp19OdVhuT21RQlJ4SG1QaThuSEd5elZiWTc5eSUyRkp0ZGNQTCUyRno4UkxLZnRzJTJCM0tuSGglMkZMeXVpTDI2Yml5WVhxNFQzUDREJTJGYSUyQlglMkZBdVNKZWt2aExINkczckJQQkE5V3VyYTA4SXh2MU1zdCUyQiUyRkxBNENWU1hjTUVIaEM1blhmR0taYTJvSUwzdWZYVmdIVU41QVpiNTBGd3F3T0YzdmRPcW5XTGVHRFhuQXlJZWFlYVdMQVYlMkZQZFFFM043QkVWM2NBcE40WXV0MW9wcHMwMDNaajBoa2pnc3clM0QlM0Q',
    '_gat_gtag_UA_43845809_1': '1',
    '__adblocker': 'false',
    '__ar_v4': '2YUP7TATPFC7XD6D2GIARW%3A20221028%3A60%7CZUS4OCBXGBDWLCGQSOCSQN%3A20221028%3A60%7CNHFCO3TELVGCHHJD5FHXVD%3A20221028%3A60',
    'mp_e1c710649cc8ff18c0c4d5d58433be69_mixpanel': '%7B%22distinct_id%22%3A%2087962%2C%22%24device_id%22%3A%20%2218424d95e231b75-044416efc2bfdf-19525635-1d73c0-18424d95e241bf5%22%2C%22%24initial_referrer%22%3A%20%22%24direct%22%2C%22%24initial_referring_domain%22%3A%20%22%24direct%22%2C%22__mps%22%3A%20%7B%7D%2C%22__mpso%22%3A%20%7B%7D%2C%22__mpus%22%3A%20%7B%7D%2C%22__mpa%22%3A%20%7B%7D%2C%22__mpu%22%3A%20%7B%7D%2C%22__mpr%22%3A%20%5B%5D%2C%22__mpap%22%3A%20%5B%5D%2C%22%24user_id%22%3A%2087962%7D',
}

headers = {
    'authority': 'fantasydata.com',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://fantasydata.com',
    'referer': 'https://fantasydata.com/nba/fantasy-basketball-projections?scope=2&season=2023&seasontype=1&conference=1&date=10-29-2022',
    'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
}

date_parts = utils.date_str().split('-')

data = {
    'sort': 'FantasyPoints-desc',
    'pageSize': '500',
    'group': '',
    'filter': '',
    'filters.scope': '2',
    'filters.subscope': '',
    'filters.season': '2023',
    'filters.seasontype': '1',
    'filters.team': '',
    'filters.conference': '1',
    'filters.position': '',
    'filters.searchtext': '',
    'filters.scoringsystem': '',
    'filters.exportType': '',
    # 'filters.date': '10-30-2022',
    'filters.date': '{}-{}-{}'.format(date_parts[1], date_parts[2], date_parts[0]),
    'filters.dfsoperator': '',
    'filters.dfsslateid': '',
    'filters.dfsslategameid': '',
    'filters.dfsrosterslot': '',
    'filters.showfavs': '',
    'filters.teamkey': '',
    'filters.oddsstate': '',
    'filters.showall': '',
}

class FantasyDataScraper:
  def __init__(self, sport):
    self.sport = sport
    assert sport == "NBA"
    self.name = 'FantasyData'

  # https://fantasydata.com/nba/optimizer/fanduel

  def run(self):
      to_return = {}

      response = requests.post('https://fantasydata.com/NBA_Projections/Projections_Read', cookies=cookies, headers=headers, data=data)

      players = response.json()['Data']
      
      for player in players:
        name = player['Name']
        name = utils.normalize_name(name)
        proj = player['FantasyPointsFanDuel']
        to_return[name] = {"Fantasy Score": proj}
      
      return to_return