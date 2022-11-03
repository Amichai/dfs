import requests
import utils


class TFScraper:
    def __init__(self, sport):
        self.sport = sport
        self.name = "TF"

    def run(self):
        headers = {
            'authority': 'api.thrivefantasy.com',
            'access-control-allow-origin': '*',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36',
            'token': 'eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJhbWwiLCJhdWRpZW5jZSI6IklPUyIsInBhc3MiOiIkMmEkMTAkTUdyR2FQbzhvZW91aEwuSnRjeWtBdWMzVVk1d1RNeFNtVm1XbmJyUDdpR1YzejhRb3V5MTIiLCJjcmVhdGVkIjoxNjY3NDIzNDQzMDg3LCJleHAiOjE2NjgwMjgyNDN9.3LLa1ZaWbSkynSHb0sEWK5z2BGHvjYybQXnC4uO0Q8L2gKDbrII9sqaoJTROI23NqXw7-V7nr7H5L3FUOCJkSA',
            'sec-ch-ua-platform': '"macOS"',
            'content-type': 'application/json',
            'accept': '*/*',
            'origin': 'https://www.thrivefantasy.com',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://www.thrivefantasy.com/',
            'accept-language': 'en-US,en;q=0.9,he;q=0.8',
        }



        data = '{"currentPage":1,"currentSize":1000,"half":0,"Latitude":"40.9053143","Longitude":"-73.7857122"}'

        response = requests.post('https://api.thrivefantasy.com/houseProp/upcomingHouseProps', headers=headers, data=data)

        try:
            as_json = response.json()
        except:
            __import__('pdb').set_trace()

        to_return = {}

        # __import__('pdb').set_trace()

        if as_json['response']['pagination']['totalPages'] > 1:
            print("WE NEED PAGINATION")
            import pdb; pdb.set_trace()


        for market in as_json['response']['data']:
            contest_prop = market['contestProp']
            line = contest_prop['propValue']
            name = "{} {}".format(contest_prop['player1']['firstName'], contest_prop['player1']['lastName'])
            name = utils.normalize_name(name)

            if contest_prop['player1']['leagueType'] != self.sport:
                continue

            if not name in to_return:
                to_return[name] = {}

            team = contest_prop['player1']['teamAbbr']

            prop_name = " + ".join(contest_prop['player1']["propParameters"])


            to_return[name][prop_name] = str(line)
        
        return to_return

if __name__ == "__main__":
    result = query_TF()
    print(result)