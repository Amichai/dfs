import requests
import utils
from bs4 import BeautifulSoup

import requests

headers = {
    'authority': 'www.stokastic.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'cookie': 'wisepops_activity_session=%7B%22id%22%3A%22f70ac129-e52e-4a23-ba9b-11f5fc8011cd%22%2C%22start%22%3A1672618551956%7D; advanced_ads_pro_visitor_referrer=%7B%22expires%22%3A1699232442%2C%22data%22%3A%22https%3A//www.google.com/%22%7D; _gcl_au=1.1.1491631464.1667696442; wisepops=%7B%22csd%22%3A1%2C%22popups%22%3A%7B%7D%2C%22sub%22%3A0%2C%22ucrn%22%3A23%2C%22cid%22%3A%2247155%22%2C%22v%22%3A4%2C%22bandit%22%3A%7B%22recos%22%3A%7B%7D%7D%7D; _fbp=fb.1.1667696442157.502392265; advanced_ads_pro_server_info=%7B%22conditions%22%3A%7B%22geo_targeting%22%3A%7B%22fb0761cc21%22%3A%7B%22data%22%3A%7B%22visitor_city%22%3A%22New%20Rochelle%22%2C%22visitor_region%22%3A%22New%20York%22%2C%22country_code%22%3A%22US%22%2C%22continent_code%22%3A%22NA%22%2C%22is_eu_state%22%3Afalse%2C%22current_lat%22%3A40.9163%2C%22current_lon%22%3A-73.7898%7D%2C%22time%22%3A1670675765%7D%7D%7D%2C%22vc_cache_reset%22%3A0%7D; __stripe_mid=4fc4579c-b991-4dba-a624-eb6a2325e3849ca10d; wordpress_test_cookie=WP+Cookie+check; _au_1d=AU1D-0100-001670678988-0DTM92XR-FTD0; _hp2_id.5711864=%7B%22userId%22%3A%223899547445236944%22%2C%22pageviewId%22%3A%22686799774779564%22%2C%22sessionId%22%3A%225181616089750261%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; advanced_ads_browser_width=1535; wisepops_visits=%5B%222023-01-02T00%3A15%3A51.468Z%22%2C%222022-12-30T23%3A50%3A49.285Z%22%2C%222022-12-30T15%3A43%3A51.168Z%22%2C%222022-12-30T02%3A26%3A29.784Z%22%2C%222022-12-27T15%3A33%3A58.987Z%22%2C%222022-12-23T00%3A46%3A28.602Z%22%2C%222022-12-22T03%3A15%3A44.600Z%22%2C%222022-12-16T23%3A54%3A00.809Z%22%2C%222022-12-16T23%3A46%3A08.681Z%22%2C%222022-12-16T23%3A45%3A53.101Z%22%5D; _gid=GA1.2.58472392.1672618552; _gat_UA-113468959-1=1; _clck=19bduop|1|f7x|0; _gat_gtag_UA_113468959_1=1; wisepops_activity_session=%7B%22id%22%3A%22bd3ed950-f829-4204-a336-62721b9274da%22%2C%22start%22%3A1672618554054%7D; _au_last_seen_pixels=eyJhcG4iOjE2NzI2MTg1NTQsInR0ZCI6MTY3MjYxODU1NCwicHViIjoxNjcyNjE4NTU0LCJ0YXBhZCI6MTY3MjYxODU1NCwiYWR4IjoxNjcyNjE4NTU0LCJnb28iOjE2NzI2MTg1NTQsIm1lZGlhbWF0aCI6MTY3MjYxODU1NCwiYmVlcyI6MTY3MjQ0NDI1NCwidGFib29sYSI6MTY3MjQ0NDI1NywicnViIjoxNjcyNDQ0MjU3LCJzb24iOjE2NzI2MTg1NTQsImFkbyI6MTY3MjQ0NDI1NywidW5ydWx5IjoxNjcyNDQ0MjU3LCJwcG50IjoxNjcyNjE4NTU0LCJpbXByIjoxNjcyNjE4NTU0LCJzbWFydCI6MTY3MjQ0NDI1NCwib3BlbngiOjE2NzI0NDQyNTd9; wordpress_logged_in_ee248d429f08b2f1ef6087d0533242ab=aml2%7C1672791356%7CmKHsxHVxmHpiuWEkMFiRhbGGNZDHJ6tJAUcLQP5yHUm%7C9a061a39ee80d2cff5ba6a11641a0326f3b7d882cd9092d570c7d409de78ad64; advanced_ads_page_impressions=%7B%22expires%22%3A1983056442%2C%22data%22%3A113%7D; wisepops_session=%7B%22arrivalOnSite%22%3A%222023-01-02T00%3A15%3A51.468Z%22%2C%22mtime%22%3A1672618558793%2C%22pageviews%22%3A3%2C%22popups%22%3A%7B%7D%2C%22bars%22%3A%7B%7D%2C%22countdowns%22%3A%7B%7D%2C%22src%22%3Anull%2C%22utm%22%3A%7B%7D%2C%22testIp%22%3Anull%7D; _ga_FY84WPJ80Q=GS1.1.1672618552.27.1.1672618559.53.0.0; _ga=GA1.2.1974118152.1667696442; _clsk=ep514c|1672618560128|3|1|j.clarity.ms/collect',
    'referer': 'https://www.stokastic.com/login2',
    'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
}

class StokasticScraper:
  def __init__(self, sport, target_teams=[]):
    self.target_teams = target_teams
    self.sport = sport
    self.name = "Stokastic"

  def parse_table(self, table, prefix=""):
    rows = table.select('tr')

    to_return = {}
    for row in rows:
      parts = [a.text for a in row.select('td')]

      if len(parts) < 4:
        continue
      team = parts[1]
      # if not team in self.target_teams:
      #   continue
      
      name = utils.normalize_name(parts[0])
      projection = float(parts[4])
      bust = float(parts[8])
      boom = float(parts[9])
      posProj = parts[10]
      try:
        posProj = round(float(posProj), 2)
      except:
        pass
      ownership = parts[11]
      optimal = parts[12]
      leverage = parts[13]
      if not name in to_return:
        to_return[name] = {}
      to_return[name][prefix + 'Fantasy Score'] = projection
      to_return[name][prefix + 'boom'] = boom
      to_return[name][prefix + 'bust'] = bust
      if posProj != '':
        to_return[name][prefix + 'posProj'] = posProj
      if ownership != '':
        to_return[name][prefix + 'ownership'] = ownership
      if optimal != '':
        to_return[name][prefix + 'optimal'] = optimal
      to_return[name][prefix + 'leverage'] = leverage

    return to_return

  def run(self):
    response = requests.get('https://www.stokastic.com/nba/boom-bust-probability/', headers=headers)

    bs = BeautifulSoup(response.text, 'lxml')
    dk_table = bs.select('table')[0]
    to_return1 = self.parse_table(dk_table, "dk_")

    fd_table = bs.select('table')[1]
    to_return2 = self.parse_table(fd_table)

    # missing_names1 = [a for a in to_return1.keys() if a not in list(to_return2.keys())]
    # missing_names2 = [a for a in to_return1.keys() if a not in list(to_return2.keys())]

    for name, stats in to_return2.items():
      if not name in to_return1:
        to_return1[name] = {}
      to_return1[name].update(stats)

    return to_return1
