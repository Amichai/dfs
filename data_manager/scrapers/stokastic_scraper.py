import requests
import utils
from bs4 import BeautifulSoup

import requests

headers = {
    'authority': 'www.stokastic.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'cookie': 'wisepops_activity_session=%7B%22id%22%3A%22a728679b-4e9e-4cc3-9dca-1376c74569a2%22%2C%22start%22%3A1673656080334%7D; advanced_ads_pro_visitor_referrer=%7B%22expires%22%3A1699232442%2C%22data%22%3A%22https%3A//www.google.com/%22%7D; _gcl_au=1.1.1491631464.1667696442; wisepops=%7B%22csd%22%3A1%2C%22popups%22%3A%7B%7D%2C%22sub%22%3A0%2C%22ucrn%22%3A23%2C%22cid%22%3A%2247155%22%2C%22v%22%3A4%2C%22bandit%22%3A%7B%22recos%22%3A%7B%7D%7D%7D; _fbp=fb.1.1667696442157.502392265; __stripe_mid=4fc4579c-b991-4dba-a624-eb6a2325e3849ca10d; wordpress_test_cookie=WP+Cookie+check; _au_1d=AU1D-0100-001670678988-0DTM92XR-FTD0; _hp2_id.5711864=%7B%22userId%22%3A%223899547445236944%22%2C%22pageviewId%22%3A%22686799774779564%22%2C%22sessionId%22%3A%225181616089750261%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; advanced_ads_pro_server_info=%7B%22conditions%22%3A%7B%22geo_targeting%22%3A%7B%22fb0761cc21%22%3A%7B%22data%22%3A%7B%22visitor_city%22%3A%22New%20Rochelle%22%2C%22visitor_region%22%3A%22New%20York%22%2C%22country_code%22%3A%22US%22%2C%22continent_code%22%3A%22NA%22%2C%22is_eu_state%22%3Afalse%2C%22current_lat%22%3A40.9163%2C%22current_lon%22%3A-73.7898%7D%2C%22time%22%3A1673308050%7D%7D%7D%2C%22vc_cache_reset%22%3A0%7D; _gid=GA1.2.2001643962.1673623453; advanced_ads_browser_width=1728; _clck=19bduop|1|f89|0; wisepops_visits=%5B%222023-01-14T00%3A27%3A59.839Z%22%2C%222023-01-14T00%3A17%3A32.127Z%22%2C%222023-01-13T23%3A38%3A16.356Z%22%2C%222023-01-13T23%3A06%3A16.487Z%22%2C%222023-01-13T15%3A24%3A10.919Z%22%2C%222023-01-12T00%3A26%3A35.432Z%22%2C%222023-01-11T01%3A20%3A09.610Z%22%2C%222023-01-10T00%3A01%3A17.616Z%22%2C%222023-01-09T23%3A52%3A01.209Z%22%2C%222023-01-09T23%3A46%3A46.968Z%22%5D; _gat_UA-113468959-1=1; _gat_gtag_UA_113468959_1=1; wisepops_activity_session=%7B%22id%22%3A%22c92aeb92-3a55-4a4f-9e7d-840889e93108%22%2C%22start%22%3A1673656083916%7D; _au_last_seen_pixels=eyJhcG4iOjE2NzM2NTYwODQsInR0ZCI6MTY3MzY1NjA4NCwicHViIjoxNjczNjU2MDg0LCJ0YXBhZCI6MTY3MzY1NjA4NCwiYWR4IjoxNjczNjU2MDg0LCJnb28iOjE2NzM2NTYwODQsIm1lZGlhbWF0aCI6MTY3MzY1NjA4NCwiYmVlcyI6MTY3MzQ4MzE5OSwidGFib29sYSI6MTY3MzQ4MzIwNCwicnViIjoxNjczNjU2MDg0LCJzb24iOjE2NzM0ODMyMDQsImFkbyI6MTY3MzY1NjA4NCwidW5ydWx5IjoxNjczNDgzMTk5LCJwcG50IjoxNjczNjU2MDg0LCJpbXByIjoxNjczNDgzMjA0LCJzbWFydCI6MTY3MzQ4MzIwNCwib3BlbngiOjE2NzM0ODMyMDR9; wordpress_logged_in_ee248d429f08b2f1ef6087d0533242ab=aml2%7C1673828885%7CxERMwuTa6GDR0u9K3fJrZ29vK7EwAJpHNdZLtW6d73V%7C59190b249fbea1d9d1cab99ecd47178d7655896aa9e8b698c392fe94a380f7c8; _ga_FY84WPJ80Q=GS1.1.1673655452.41.1.1673656087.52.0.0; advanced_ads_page_impressions=%7B%22expires%22%3A1983056442%2C%22data%22%3A158%7D; wisepops_session=%7B%22arrivalOnSite%22%3A%222023-01-14T00%3A27%3A59.839Z%22%2C%22mtime%22%3A1673656087552%2C%22pageviews%22%3A3%2C%22popups%22%3A%7B%7D%2C%22bars%22%3A%7B%7D%2C%22countdowns%22%3A%7B%7D%2C%22src%22%3Anull%2C%22utm%22%3A%7B%7D%2C%22testIp%22%3Anull%7D; _ga=GA1.2.1974118152.1667696442; _clsk=s1mxa|1673656089529|4|1|j.clarity.ms/collect',
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
      # posProj = parts[10]
      try:
        posProj = round(float(posProj), 2)
      except:
        pass
      ownership = parts[11]
      optimal = parts[12]
      # leverage = parts[13]
      if not name in to_return:
        to_return[name] = {}
      to_return[name][prefix + 'Fantasy Score'] = projection
      # to_return[name][prefix + 'boom'] = boom
      # to_return[name][prefix + 'bust'] = bust
      # if posProj != '':
      #   to_return[name][prefix + 'posProj'] = posProj
      if ownership != '':
        to_return[name][prefix + 'ownership'] = ownership
      if optimal != '':
        to_return[name][prefix + 'optimal'] = optimal
      # to_return[name][prefix + 'leverage'] = leverage

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
