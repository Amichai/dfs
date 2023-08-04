import requests
import utils
from bs4 import BeautifulSoup

import requests


headers = {
    'authority': 'www.stokastic.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    # 'cookie': 'wisepops_activity_session=%7B%22id%22%3A%2254b5882c-98b1-46e8-8409-adb42e23e1cc%22%2C%22start%22%3A1680391527247%7D; advanced_ads_pro_visitor_referrer=%7B%22expires%22%3A1699232442%2C%22data%22%3A%22https%3A//www.google.com/%22%7D; _fbp=fb.1.1667696442157.502392265; __stripe_mid=4fc4579c-b991-4dba-a624-eb6a2325e3849ca10d; wordpress_test_cookie=WP+Cookie+check; _au_1d=AU1D-0100-001670678988-0DTM92XR-FTD0; _li_dcdm_c=.stokastic.com; _lc2_fpi=8e31a32571c2--01gq6arb2mxpa85zcpk0e7b0ck; _gcl_au=1.1.614716584.1675555068; _au_last_seen_pixels=eyJhcG4iOjE2NzYzMzE3MjgsInR0ZCI6MTY3NjMzMTcyOCwicHViIjoxNjc2MzMxNzI4LCJ0YXBhZCI6MTY3NjMzMTcyOCwiYWR4IjoxNjc2MzMxNzI4LCJnb28iOjE2NzYzMzE3MjgsIm1lZGlhbWF0aCI6MTY3NjMzMTcyOCwiYmVlcyI6MTY3NTU1ODUxOCwidGFib29sYSI6MTY3NjA4MjYxNiwicnViIjoxNjc2MzMxNzI4LCJzb24iOjE2NzYzMzE3MjgsImFkbyI6MTY3NTU1ODUxOCwidW5ydWx5IjoxNjc1NTU4NTExLCJwcG50IjoxNjc1NzMxMzQ4LCJpbXByIjoxNjc2MDgyNjE2LCJzbWFydCI6MTY3NjMzMTcyOCwib3BlbngiOjE2NzU1NTg1MTF9; advanced_ads_page_impressions=%7B%22expires%22%3A1983056442%2C%22data%22%3A278%7D; wisepops=%7B%22csd%22%3A1%2C%22popups%22%3A%7B%22339272%22%3A%7B%22dc%22%3A1%2C%22d%22%3A1677629140849%7D%7D%2C%22sub%22%3A0%2C%22ucrn%22%3A23%2C%22cid%22%3A%2247155%22%2C%22v%22%3A4%2C%22bandit%22%3A%7B%22recos%22%3A%7B%7D%7D%7D; _gid=GA1.2.1878036011.1680391528; _clck=19bduop|1|fae|0; wisepops_activity_session=%7B%22id%22%3A%2219ea6625-697d-4ae1-87d2-6673c29bc601%22%2C%22start%22%3A1680391535254%7D; _hp2_ses_props.5711864=%7B%22r%22%3A%22https%3A%2F%2Fwww.stokastic.com%2Fnba%2Fboom-bust-probability%2F%22%2C%22ts%22%3A1680391535435%2C%22d%22%3A%22www.stokastic.com%22%2C%22h%22%3A%22%2Flogin2%22%7D; _hp2_id.5711864=%7B%22userId%22%3A%223899547445236944%22%2C%22pageviewId%22%3A%224829889900230730%22%2C%22sessionId%22%3A%228927777521769974%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; wordpress_logged_in_ee248d429f08b2f1ef6087d0533242ab=aml2%7C1680564345%7CXbZTHsfT7ZhWH8qmsbmOl9LcPSksn47Dj5BzxlzN3c9%7Caf063dbe72d4d1e3f29d31aae6cbb7737a28b0b5415528e256bfd6c0b8ddfad9; mepr_cancel_override_sub=183205; wisepops_visits=%5B%222023-04-01T23%3A32%3A14.296Z%22%2C%222023-04-01T23%3A32%3A12.801Z%22%2C%222023-04-01T23%3A25%3A53.851Z%22%2C%222023-04-01T23%3A25%3A26.977Z%22%2C%222023-03-02T19%3A40%3A18.076Z%22%2C%222023-03-01T00%3A05%3A38.844Z%22%2C%222023-02-27T23%3A59%3A18.811Z%22%2C%222023-02-26T22%3A48%3A13.629Z%22%2C%222023-02-25T23%3A49%3A17.016Z%22%2C%222023-02-23T23%3A53%3A55.650Z%22%5D; wisepops_session=%7B%22arrivalOnSite%22%3A%222023-04-01T23%3A32%3A14.296Z%22%2C%22mtime%22%3A1680391934315%2C%22pageviews%22%3A1%2C%22popups%22%3A%7B%7D%2C%22bars%22%3A%7B%7D%2C%22countdowns%22%3A%7B%7D%2C%22src%22%3Anull%2C%22utm%22%3A%7B%7D%2C%22testIp%22%3Anull%7D; _ga_FY84WPJ80Q=GS1.1.1680391527.99.1.1680391934.7.0.0; _clsk=rmw61s|1680391934934|10|1|p.clarity.ms/collect; _ga=GA1.2.1974118152.1667696442',
    'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
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
      if name == "Name":
        continue
      projection = float(parts[3])
      stddev = float(parts[4])
      ceiling = float(parts[5])
      floor = float(parts[6])
      # ownership = parts[11]
      optimal = parts[-2]
      # leverage = parts[13]


      if not name in to_return:
        to_return[name] = {}
      to_return[name][prefix + 'Fantasy Score'] = projection
      # to_return[name][prefix + 'boom'] = boom
      # to_return[name][prefix + 'bust'] = bust
      
      to_return[name][prefix + 'stddev'] = stddev
      to_return[name][prefix + 'ceiling'] = ceiling
      to_return[name][prefix + 'floor'] = floor

      # if posProj != '':
      #   to_return[name][prefix + 'posProj'] = posProj
      # if ownership != '':
      #   to_return[name][prefix + 'ownership'] = ownership
      if optimal != '':
        to_return[name][prefix + 'optimal'] = optimal
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

    # __import__('pdb').set_trace()

    # __import__('pdb'  ).set_trace()
    # dk_table = bs.select('table')[0]
    
    # to_return1 = parsing_function(dk_table, "dk_")


    fd_table = bs.select('table')[0]

    to_return2 = parsing_function(fd_table)

    # missing_names1 = [a for a in to_return1.keys() if a not in list(to_return2.keys())]
    # missing_names2 = [a for a in to_return1.keys() if a not in list(to_return2.keys())]

    # for name, stats in to_return2.items():
    #   if not name in to_return1:
    #     to_return1[name] = {}
    #   to_return1[name].update(stats)
    return to_return2
