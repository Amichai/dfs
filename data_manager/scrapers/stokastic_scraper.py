import requests
import utils
from bs4 import BeautifulSoup


# cookies = {
#     'advanced_ads_pro_visitor_referrer': '%7B%22expires%22%3A1699232442%2C%22data%22%3A%22https%3A//www.google.com/%22%7D',
#     '_gcl_au': '1.1.1491631464.1667696442',
#     'wisepops': '%7B%22csd%22%3A1%2C%22popups%22%3A%7B%7D%2C%22sub%22%3A0%2C%22ucrn%22%3A23%2C%22cid%22%3A%2247155%22%2C%22v%22%3A4%2C%22bandit%22%3A%7B%22recos%22%3A%7B%7D%7D%7D',
#     '_fbp': 'fb.1.1667696442157.502392265',
#     'advanced_ads_browser_width': '1375',
#     'wisepops_activity_session': '%7B%22id%22%3A%220d32440f-fea8-40d0-bb1c-8f9fd3d027b0%22%2C%22start%22%3A1670675762437%7D',
#     '_gid': 'GA1.2.181410394.1670675763',
#     '_clck': '19bduop|1|f7a|0',
#     'advanced_ads_pro_server_info': '%7B%22conditions%22%3A%7B%22geo_targeting%22%3A%7B%22fb0761cc21%22%3A%7B%22data%22%3A%7B%22visitor_city%22%3A%22New%20Rochelle%22%2C%22visitor_region%22%3A%22New%20York%22%2C%22country_code%22%3A%22US%22%2C%22continent_code%22%3A%22NA%22%2C%22is_eu_state%22%3Afalse%2C%22current_lat%22%3A40.9163%2C%22current_lon%22%3A-73.7898%7D%2C%22time%22%3A1670675765%7D%7D%7D%2C%22vc_cache_reset%22%3A0%7D',
#     '__stripe_mid': '4fc4579c-b991-4dba-a624-eb6a2325e3849ca10d',
#     '__stripe_sid': '419d1382-19bd-4361-9ed9-6d92cbee11a270fdff',
#     'wordpress_test_cookie': 'WP+Cookie+check',
#     '_au_1d': 'AU1D-0100-001670678988-0DTM92XR-FTD0',
#     '_au_last_seen_pixels': 'eyJhcG4iOjE2NzA2Nzg5ODgsInR0ZCI6MTY3MDY3ODk4OCwicHViIjoxNjcwNjc4OTg4LCJ0YXBhZCI6MTY3MDY3ODk4OCwiYWR4IjoxNjcwNjc4OTg4LCJnb28iOjE2NzA2Nzg5ODgsIm1lZGlhbWF0aCI6MTY3MDY3ODk4OCwiYmVlcyI6MTY3MDY3ODk4OCwidGFib29sYSI6MTY3MDY3ODk4OCwicnViIjoxNjcwNjc4OTg4LCJzb24iOjE2NzA2Nzg5OTEsImFkbyI6MTY3MDY3ODk5MSwidW5ydWx5IjoxNjcwNjc4OTkxLCJwcG50IjoxNjcwNjc4OTkxLCJpbXByIjoxNjcwNjc4OTkxLCJzbWFydCI6MTY3MDY3ODk5MSwib3BlbngiOjE2NzA2Nzg5OTF9',
#     'wordpress_logged_in_ee248d429f08b2f1ef6087d0533242ab': 'aml2%7C1670851794%7CUoYsee39irbUMkc5eIaGgEnwX2V0mt03liXrSK9Hw7u%7C1dc1e57ca0998e5e8d54bfd383c7e033016ca21fe3545806831c45562f16801e',
#     'wisepops_visits': '%5B%222022-12-10T13%3A32%3A38.804Z%22%2C%222022-12-10T13%3A32%3A25.924Z%22%2C%222022-12-10T12%3A36%3A01.255Z%22%2C%222022-12-04T19%3A51%3A14.903Z%22%2C%222022-12-01T19%3A18%3A21.105Z%22%2C%222022-11-06T01%3A00%3A41.419Z%22%5D',
#     'advanced_ads_page_impressions': '%7B%22expires%22%3A1983056442%2C%22data%22%3A20%7D',
#     'wisepops_session': '%7B%22arrivalOnSite%22%3A%222022-12-10T13%3A32%3A38.804Z%22%2C%22mtime%22%3A1670679286696%2C%22pageviews%22%3A3%2C%22popups%22%3A%7B%7D%2C%22bars%22%3A%7B%7D%2C%22countdowns%22%3A%7B%7D%2C%22src%22%3A%22https%3A%2F%2Fdiscord.com%2F%22%2C%22utm%22%3A%7B%7D%2C%22testIp%22%3Anull%7D',
#     '_ga_FY84WPJ80Q': 'GS1.1.1670678940.6.1.1670679288.46.0.0',
#     '_clsk': '1fapjdd|1670679291907|9|1|f.clarity.ms/collect',
#     '_ga': 'GA1.2.1974118152.1667696442',
#     '_gat_UA-113468959-1': '1',
# }

# headers = {
#     'authority': 'www.stokastic.com',
#     'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
#     'accept-language': 'en-US,en;q=0.9',
#     'cache-control': 'max-age=0',
#     # 'cookie': 'advanced_ads_pro_visitor_referrer=%7B%22expires%22%3A1699232442%2C%22data%22%3A%22https%3A//www.google.com/%22%7D; _gcl_au=1.1.1491631464.1667696442; wisepops=%7B%22csd%22%3A1%2C%22popups%22%3A%7B%7D%2C%22sub%22%3A0%2C%22ucrn%22%3A23%2C%22cid%22%3A%2247155%22%2C%22v%22%3A4%2C%22bandit%22%3A%7B%22recos%22%3A%7B%7D%7D%7D; _fbp=fb.1.1667696442157.502392265; advanced_ads_browser_width=1375; wisepops_activity_session=%7B%22id%22%3A%220d32440f-fea8-40d0-bb1c-8f9fd3d027b0%22%2C%22start%22%3A1670675762437%7D; _gid=GA1.2.181410394.1670675763; _clck=19bduop|1|f7a|0; advanced_ads_pro_server_info=%7B%22conditions%22%3A%7B%22geo_targeting%22%3A%7B%22fb0761cc21%22%3A%7B%22data%22%3A%7B%22visitor_city%22%3A%22New%20Rochelle%22%2C%22visitor_region%22%3A%22New%20York%22%2C%22country_code%22%3A%22US%22%2C%22continent_code%22%3A%22NA%22%2C%22is_eu_state%22%3Afalse%2C%22current_lat%22%3A40.9163%2C%22current_lon%22%3A-73.7898%7D%2C%22time%22%3A1670675765%7D%7D%7D%2C%22vc_cache_reset%22%3A0%7D; __stripe_mid=4fc4579c-b991-4dba-a624-eb6a2325e3849ca10d; __stripe_sid=419d1382-19bd-4361-9ed9-6d92cbee11a270fdff; wordpress_test_cookie=WP+Cookie+check; _au_1d=AU1D-0100-001670678988-0DTM92XR-FTD0; _au_last_seen_pixels=eyJhcG4iOjE2NzA2Nzg5ODgsInR0ZCI6MTY3MDY3ODk4OCwicHViIjoxNjcwNjc4OTg4LCJ0YXBhZCI6MTY3MDY3ODk4OCwiYWR4IjoxNjcwNjc4OTg4LCJnb28iOjE2NzA2Nzg5ODgsIm1lZGlhbWF0aCI6MTY3MDY3ODk4OCwiYmVlcyI6MTY3MDY3ODk4OCwidGFib29sYSI6MTY3MDY3ODk4OCwicnViIjoxNjcwNjc4OTg4LCJzb24iOjE2NzA2Nzg5OTEsImFkbyI6MTY3MDY3ODk5MSwidW5ydWx5IjoxNjcwNjc4OTkxLCJwcG50IjoxNjcwNjc4OTkxLCJpbXByIjoxNjcwNjc4OTkxLCJzbWFydCI6MTY3MDY3ODk5MSwib3BlbngiOjE2NzA2Nzg5OTF9; wordpress_logged_in_ee248d429f08b2f1ef6087d0533242ab=aml2%7C1670851794%7CUoYsee39irbUMkc5eIaGgEnwX2V0mt03liXrSK9Hw7u%7C1dc1e57ca0998e5e8d54bfd383c7e033016ca21fe3545806831c45562f16801e; wisepops_visits=%5B%222022-12-10T13%3A32%3A38.804Z%22%2C%222022-12-10T13%3A32%3A25.924Z%22%2C%222022-12-10T12%3A36%3A01.255Z%22%2C%222022-12-04T19%3A51%3A14.903Z%22%2C%222022-12-01T19%3A18%3A21.105Z%22%2C%222022-11-06T01%3A00%3A41.419Z%22%5D; advanced_ads_page_impressions=%7B%22expires%22%3A1983056442%2C%22data%22%3A20%7D; wisepops_session=%7B%22arrivalOnSite%22%3A%222022-12-10T13%3A32%3A38.804Z%22%2C%22mtime%22%3A1670679286696%2C%22pageviews%22%3A3%2C%22popups%22%3A%7B%7D%2C%22bars%22%3A%7B%7D%2C%22countdowns%22%3A%7B%7D%2C%22src%22%3A%22https%3A%2F%2Fdiscord.com%2F%22%2C%22utm%22%3A%7B%7D%2C%22testIp%22%3Anull%7D; _ga_FY84WPJ80Q=GS1.1.1670678940.6.1.1670679288.46.0.0; _clsk=1fapjdd|1670679291907|9|1|f.clarity.ms/collect; _ga=GA1.2.1974118152.1667696442; _gat_UA-113468959-1=1',
#     'referer': 'https://www.stokastic.com/thank-you-all/?membership=nba-weekly&transaction_id=689992&membership_id=10192&subscription_id=183205',
#     'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
#     'sec-ch-ua-mobile': '?0',
#     'sec-ch-ua-platform': '"macOS"',
#     'sec-fetch-dest': 'document',
#     'sec-fetch-mode': 'navigate',
#     'sec-fetch-site': 'same-origin',
#     'sec-fetch-user': '?1',
#     'upgrade-insecure-requests': '1',
#     'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
# }


import requests

cookies = {
    'wisepops_activity_session': '%7B%22id%22%3A%22667101b9-ab37-46ca-ad34-d5fb234bb273%22%2C%22start%22%3A1670700393665%7D',
    'advanced_ads_pro_visitor_referrer': '%7B%22expires%22%3A1699232442%2C%22data%22%3A%22https%3A//www.google.com/%22%7D',
    '_gcl_au': '1.1.1491631464.1667696442',
    'wisepops': '%7B%22csd%22%3A1%2C%22popups%22%3A%7B%7D%2C%22sub%22%3A0%2C%22ucrn%22%3A23%2C%22cid%22%3A%2247155%22%2C%22v%22%3A4%2C%22bandit%22%3A%7B%22recos%22%3A%7B%7D%7D%7D',
    '_fbp': 'fb.1.1667696442157.502392265',
    'wisepops_activity_session': '%7B%22id%22%3A%220d32440f-fea8-40d0-bb1c-8f9fd3d027b0%22%2C%22start%22%3A1670675762437%7D',
    '_gid': 'GA1.2.181410394.1670675763',
    '_clck': '19bduop|1|f7a|0',
    'advanced_ads_pro_server_info': '%7B%22conditions%22%3A%7B%22geo_targeting%22%3A%7B%22fb0761cc21%22%3A%7B%22data%22%3A%7B%22visitor_city%22%3A%22New%20Rochelle%22%2C%22visitor_region%22%3A%22New%20York%22%2C%22country_code%22%3A%22US%22%2C%22continent_code%22%3A%22NA%22%2C%22is_eu_state%22%3Afalse%2C%22current_lat%22%3A40.9163%2C%22current_lon%22%3A-73.7898%7D%2C%22time%22%3A1670675765%7D%7D%7D%2C%22vc_cache_reset%22%3A0%7D',
    '__stripe_mid': '4fc4579c-b991-4dba-a624-eb6a2325e3849ca10d',
    'wordpress_test_cookie': 'WP+Cookie+check',
    '_au_1d': 'AU1D-0100-001670678988-0DTM92XR-FTD0',
    '_au_last_seen_pixels': 'eyJhcG4iOjE2NzA2Nzg5ODgsInR0ZCI6MTY3MDY3ODk4OCwicHViIjoxNjcwNjc4OTg4LCJ0YXBhZCI6MTY3MDY3ODk4OCwiYWR4IjoxNjcwNjc4OTg4LCJnb28iOjE2NzA2Nzg5ODgsIm1lZGlhbWF0aCI6MTY3MDY3ODk4OCwiYmVlcyI6MTY3MDY3ODk4OCwidGFib29sYSI6MTY3MDY3ODk4OCwicnViIjoxNjcwNjc4OTg4LCJzb24iOjE2NzA2Nzg5OTEsImFkbyI6MTY3MDY3ODk5MSwidW5ydWx5IjoxNjcwNjc4OTkxLCJwcG50IjoxNjcwNjc4OTkxLCJpbXByIjoxNjcwNjc4OTkxLCJzbWFydCI6MTY3MDY3ODk5MSwib3BlbngiOjE2NzA2Nzg5OTF9',
    'wordpress_logged_in_ee248d429f08b2f1ef6087d0533242ab': 'aml2%7C1670851794%7CUoYsee39irbUMkc5eIaGgEnwX2V0mt03liXrSK9Hw7u%7C1dc1e57ca0998e5e8d54bfd383c7e033016ca21fe3545806831c45562f16801e',
    'wisepops_visits': '%5B%222022-12-10T13%3A41%3A39.905Z%22%2C%222022-12-10T13%3A41%3A24.184Z%22%2C%222022-12-10T13%3A32%3A38.804Z%22%2C%222022-12-10T13%3A32%3A25.924Z%22%2C%222022-12-10T12%3A36%3A01.255Z%22%2C%222022-12-04T19%3A51%3A14.903Z%22%2C%222022-12-01T19%3A18%3A21.105Z%22%2C%222022-11-06T01%3A00%3A41.419Z%22%5D',
    'advanced_ads_browser_width': '1372',
    '_hp2_id.5711864': '%7B%22userId%22%3A%223899547445236944%22%2C%22pageviewId%22%3A%22686799774779564%22%2C%22sessionId%22%3A%225181616089750261%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D',
    'advanced_ads_page_impressions': '%7B%22expires%22%3A1983056442%2C%22data%22%3A34%7D',
    'wisepops_session': '%7B%22arrivalOnSite%22%3A%222022-12-10T17%3A10%3A01.969Z%22%2C%22mtime%22%3A1670700430902%2C%22pageviews%22%3A10%2C%22popups%22%3A%7B%7D%2C%22bars%22%3A%7B%7D%2C%22countdowns%22%3A%7B%7D%2C%22src%22%3Anull%2C%22utm%22%3A%7B%7D%2C%22testIp%22%3Anull%7D',
    '_ga': 'GA1.2.1974118152.1667696442',
    '_ga_FY84WPJ80Q': 'GS1.1.1670699827.8.1.1670700717.60.0.0',
    '_clsk': '1hemqew|1670700717550|4|1|f.clarity.ms/collect',
}

headers = {
    'authority': 'www.stokastic.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    # 'cookie': 'wisepops_activity_session=%7B%22id%22%3A%22667101b9-ab37-46ca-ad34-d5fb234bb273%22%2C%22start%22%3A1670700393665%7D; advanced_ads_pro_visitor_referrer=%7B%22expires%22%3A1699232442%2C%22data%22%3A%22https%3A//www.google.com/%22%7D; _gcl_au=1.1.1491631464.1667696442; wisepops=%7B%22csd%22%3A1%2C%22popups%22%3A%7B%7D%2C%22sub%22%3A0%2C%22ucrn%22%3A23%2C%22cid%22%3A%2247155%22%2C%22v%22%3A4%2C%22bandit%22%3A%7B%22recos%22%3A%7B%7D%7D%7D; _fbp=fb.1.1667696442157.502392265; wisepops_activity_session=%7B%22id%22%3A%220d32440f-fea8-40d0-bb1c-8f9fd3d027b0%22%2C%22start%22%3A1670675762437%7D; _gid=GA1.2.181410394.1670675763; _clck=19bduop|1|f7a|0; advanced_ads_pro_server_info=%7B%22conditions%22%3A%7B%22geo_targeting%22%3A%7B%22fb0761cc21%22%3A%7B%22data%22%3A%7B%22visitor_city%22%3A%22New%20Rochelle%22%2C%22visitor_region%22%3A%22New%20York%22%2C%22country_code%22%3A%22US%22%2C%22continent_code%22%3A%22NA%22%2C%22is_eu_state%22%3Afalse%2C%22current_lat%22%3A40.9163%2C%22current_lon%22%3A-73.7898%7D%2C%22time%22%3A1670675765%7D%7D%7D%2C%22vc_cache_reset%22%3A0%7D; __stripe_mid=4fc4579c-b991-4dba-a624-eb6a2325e3849ca10d; wordpress_test_cookie=WP+Cookie+check; _au_1d=AU1D-0100-001670678988-0DTM92XR-FTD0; _au_last_seen_pixels=eyJhcG4iOjE2NzA2Nzg5ODgsInR0ZCI6MTY3MDY3ODk4OCwicHViIjoxNjcwNjc4OTg4LCJ0YXBhZCI6MTY3MDY3ODk4OCwiYWR4IjoxNjcwNjc4OTg4LCJnb28iOjE2NzA2Nzg5ODgsIm1lZGlhbWF0aCI6MTY3MDY3ODk4OCwiYmVlcyI6MTY3MDY3ODk4OCwidGFib29sYSI6MTY3MDY3ODk4OCwicnViIjoxNjcwNjc4OTg4LCJzb24iOjE2NzA2Nzg5OTEsImFkbyI6MTY3MDY3ODk5MSwidW5ydWx5IjoxNjcwNjc4OTkxLCJwcG50IjoxNjcwNjc4OTkxLCJpbXByIjoxNjcwNjc4OTkxLCJzbWFydCI6MTY3MDY3ODk5MSwib3BlbngiOjE2NzA2Nzg5OTF9; wordpress_logged_in_ee248d429f08b2f1ef6087d0533242ab=aml2%7C1670851794%7CUoYsee39irbUMkc5eIaGgEnwX2V0mt03liXrSK9Hw7u%7C1dc1e57ca0998e5e8d54bfd383c7e033016ca21fe3545806831c45562f16801e; wisepops_visits=%5B%222022-12-10T13%3A41%3A39.905Z%22%2C%222022-12-10T13%3A41%3A24.184Z%22%2C%222022-12-10T13%3A32%3A38.804Z%22%2C%222022-12-10T13%3A32%3A25.924Z%22%2C%222022-12-10T12%3A36%3A01.255Z%22%2C%222022-12-04T19%3A51%3A14.903Z%22%2C%222022-12-01T19%3A18%3A21.105Z%22%2C%222022-11-06T01%3A00%3A41.419Z%22%5D; advanced_ads_browser_width=1372; _hp2_id.5711864=%7B%22userId%22%3A%223899547445236944%22%2C%22pageviewId%22%3A%22686799774779564%22%2C%22sessionId%22%3A%225181616089750261%22%2C%22identity%22%3Anull%2C%22trackerVersion%22%3A%224.0%22%7D; advanced_ads_page_impressions=%7B%22expires%22%3A1983056442%2C%22data%22%3A34%7D; wisepops_session=%7B%22arrivalOnSite%22%3A%222022-12-10T17%3A10%3A01.969Z%22%2C%22mtime%22%3A1670700430902%2C%22pageviews%22%3A10%2C%22popups%22%3A%7B%7D%2C%22bars%22%3A%7B%7D%2C%22countdowns%22%3A%7B%7D%2C%22src%22%3Anull%2C%22utm%22%3A%7B%7D%2C%22testIp%22%3Anull%7D; _ga=GA1.2.1974118152.1667696442; _ga_FY84WPJ80Q=GS1.1.1670699827.8.1.1670700717.60.0.0; _clsk=1hemqew|1670700717550|4|1|f.clarity.ms/collect',
    'referer': 'https://www.stokastic.com/nba/nba-data-central/',
    'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
}


class StokasticScraper:
  def __init__(self, sport, target_teams=[]):
    self.target_teams = target_teams
    self.sport = sport
    self.name = "Stokastic"

  def run(self):
    response = requests.get('https://www.stokastic.com/nba/boom-bust-probability/', cookies=cookies, headers=headers)

    bs = BeautifulSoup(response.text, 'lxml')
    fd_table = bs.select('table')[1]
    rows = fd_table.select('tr')

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
      to_return[name]['Fantasy Score'] = projection
      to_return[name]['boom'] = boom
      to_return[name]['bust'] = bust
      if posProj != '':
        to_return[name]['posProj'] = posProj
      if ownership != '':
        to_return[name]['ownership'] = ownership
      if optimal != '':
        to_return[name]['optimal'] = optimal
      to_return[name]['leverage'] = leverage

    return to_return