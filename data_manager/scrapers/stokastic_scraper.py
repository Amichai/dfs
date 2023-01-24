import requests
import utils
from bs4 import BeautifulSoup

import requests

headers = {
    'authority': 'www.stokastic.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'cookie': 'wisepops_activity_session=%7B%22id%22%3A%229db38fd3-6732-4bb7-b130-5f31367bb8c0%22%2C%22start%22%3A1674518490816%7D; advanced_ads_pro_visitor_referrer=%7B%22expires%22%3A1699232442%2C%22data%22%3A%22https%3A//www.google.com/%22%7D; _gcl_au=1.1.1491631464.1667696442; wisepops=%7B%22csd%22%3A1%2C%22popups%22%3A%7B%7D%2C%22sub%22%3A0%2C%22ucrn%22%3A23%2C%22cid%22%3A%2247155%22%2C%22v%22%3A4%2C%22bandit%22%3A%7B%22recos%22%3A%7B%7D%7D%7D; _fbp=fb.1.1667696442157.502392265; __stripe_mid=4fc4579c-b991-4dba-a624-eb6a2325e3849ca10d; wordpress_test_cookie=WP+Cookie+check; _au_1d=AU1D-0100-001670678988-0DTM92XR-FTD0; _hp2_id.5711864=%7B%22userId%22%3A%223899547445236944%22%2C%22pageviewId%22%3A%22686799774779564%22%2C%22sessionId%22%3A%225181616089750261%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; advanced_ads_pro_server_info=%7B%22conditions%22%3A%7B%22geo_targeting%22%3A%7B%22fb0761cc21%22%3A%7B%22data%22%3A%7B%22visitor_city%22%3A%22New%20Rochelle%22%2C%22visitor_region%22%3A%22New%20York%22%2C%22country_code%22%3A%22US%22%2C%22continent_code%22%3A%22NA%22%2C%22is_eu_state%22%3Afalse%2C%22current_lat%22%3A40.9163%2C%22current_lon%22%3A-73.7898%7D%2C%22time%22%3A1673308050%7D%7D%7D%2C%22vc_cache_reset%22%3A0%7D; _gess=true; _geps=true; _li_dcdm_c=.stokastic.com; _lc2_fpi=8e31a32571c2--01gq6arb2mxpa85zcpk0e7b0ck; advanced_ads_browser_width=1373; _gid=GA1.2.1603736397.1674518491; _clck=19bduop|1|f8j|0; wisepops_activity_session=%7B%22id%22%3A%2223166777-3f3a-48db-8f44-398c607f9f45%22%2C%22start%22%3A1674518497320%7D; _au_last_seen_pixels=eyJhcG4iOjE2NzQ1MTg0OTgsInR0ZCI6MTY3NDUxODQ5OCwicHViIjoxNjc0NTE4NDk4LCJ0YXBhZCI6MTY3NDUxODQ5OCwiYWR4IjoxNjc0NTE4NDk4LCJnb28iOjE2NzQ1MTg0OTgsIm1lZGlhbWF0aCI6MTY3NDM0OTAxOSwiYmVlcyI6MTY3NDUxODQ5OCwidGFib29sYSI6MTY3NDM0OTAxNSwicnViIjoxNjc0NTE4NDk4LCJzb24iOjE2NzQzNDkwMTksImFkbyI6MTY3NDM0OTAxNSwidW5ydWx5IjoxNjc0MzQ5MDE5LCJwcG50IjoxNjc0NTE4NDk4LCJpbXByIjoxNjc0MzQ5MDE5LCJzbWFydCI6MTY3NDUxODQ5OCwib3BlbngiOjE2NzQzNDkwMTl9; wordpress_logged_in_ee248d429f08b2f1ef6087d0533242ab=aml2%7C1674691299%7CSPIIJqwwru3t7fOuMTThO9m0bRJ9YcQB8UJplTW0ylp%7C24e0b809e2d7872ffe23a4bedab76391ae76844546fae318a401b12bc2194ab9; advanced_ads_page_impressions=%7B%22expires%22%3A1983056442%2C%22data%22%3A207%7D; wisepops_visits=%5B%222023-01-24T00%3A46%3A23.920Z%22%2C%222023-01-24T00%3A01%3A30.561Z%22%2C%222023-01-22T00%3A56%3A49.416Z%22%2C%222023-01-20T23%3A08%3A17.078Z%22%2C%222023-01-20T00%3A54%3A23.477Z%22%2C%222023-01-18T14%3A42%3A14.189Z%22%2C%222023-01-18T00%3A52%3A01.102Z%22%2C%222023-01-17T23%3A51%3A21.089Z%22%2C%222023-01-17T23%3A50%3A30.272Z%22%2C%222023-01-14T00%3A27%3A59.839Z%22%5D; wisepops_session=%7B%22arrivalOnSite%22%3A%222023-01-24T00%3A46%3A23.920Z%22%2C%22mtime%22%3A1674521184246%2C%22pageviews%22%3A1%2C%22popups%22%3A%7B%7D%2C%22bars%22%3A%7B%7D%2C%22countdowns%22%3A%7B%7D%2C%22src%22%3Anull%2C%22utm%22%3A%7B%7D%2C%22testIp%22%3Anull%7D; _gat_UA-113468959-1=1; _ga_FY84WPJ80Q=GS1.1.1674521184.54.0.1674521184.60.0.0; _ga=GA1.2.1974118152.1667696442; _clsk=fdo7nx|1674521185748|1|1|i.clarity.ms/collect; _gat_gtag_UA_113468959_1=1',
    'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
}


class StokasticScraper:
  def __init__(self, sport, target_teams=[]):
    self.target_teams = target_teams
    self.sport = sport
    self.name = "Stokastic"

  def parse_table_NFL(self, table, prefix=""):
    rows = table.select('tr')

    to_return = {}
    for row in rows:
      parts = [a.text for a in row.select('td')]

      if len(parts) < 4:
        continue
        

      name = utils.normalize_name(parts[0])
      team = parts[3]
      projection = float(parts[1])
      if not name in to_return:
        to_return[name] = {}
      to_return[name][prefix + 'Fantasy Score'] = projection
    
    return to_return

  def parse_table_NBA(self, table, prefix=""):
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
      # bust = float(parts[8])
      # boom = float(parts[9])
      # posProj = parts[10]
      # try:
      #   posProj = round(float(posProj), 2)
      # except:
      #   pass
      # ownership = parts[11]
      # optimal = parts[12]
      # leverage = parts[13]
      if not name in to_return:
        to_return[name] = {}
      to_return[name][prefix + 'Fantasy Score'] = projection
      # to_return[name][prefix + 'boom'] = boom
      # to_return[name][prefix + 'bust'] = bust
      # if posProj != '':
      #   to_return[name][prefix + 'posProj'] = posProj
      # if ownership != '':
      #   to_return[name][prefix + 'ownership'] = ownership
      # if optimal != '':
      #   to_return[name][prefix + 'optimal'] = optimal
      # to_return[name][prefix + 'leverage'] = leverage

    return to_return

  def run(self):
    if self.sport == "NBA":
      url = 'https://www.stokastic.com/nba/boom-bust-probability/'
      parsing_function = self.parse_table_NBA
    elif self.sport == "NFL":
      url = 'https://www.stokastic.com/nfl/nfl-dfs-projections/'
      parsing_function = self.parse_table_NFL

    response = requests.get(url, headers=headers)
    bs = BeautifulSoup(response.text, 'lxml')
    dk_table = bs.select('table')[0]
    
    to_return1 = parsing_function(dk_table, "dk_")

    fd_table = bs.select('table')[1]

    to_return2 = parsing_function(fd_table)

    # missing_names1 = [a for a in to_return1.keys() if a not in list(to_return2.keys())]
    # missing_names2 = [a for a in to_return1.keys() if a not in list(to_return2.keys())]

    for name, stats in to_return2.items():
      if not name in to_return1:
        to_return1[name] = {}
      to_return1[name].update(stats)

    return to_return1
