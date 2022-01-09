import requests


def query_TF():
    headers = {
        'authority': 'api.thrivefantasy.com',
        'access-control-allow-origin': '*',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        'token': 'eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJhbWwiLCJhdWRpZW5jZSI6IklPUyIsInBhc3MiOiIkMmEkMTAkM1hmdWtVNWhlZ0d1a00xZG5PSjV4dW9uY2JJTXh1d3J1a0ZOYm5wVU4yWnhIZk9Pa0NpdU8iLCJjcmVhdGVkIjoxNjQwNDQwNzM2MTIwLCJleHAiOjE2NDEwNDU1MzZ9.sKJkg95BL442Wh9LHnVZ4a3jmRxp8qwONuBSEx_Wt8vIWqO4fAdfiMpsJdrn5vHKkfsMfSDKfoUk34dcFuckNQ',
        'sec-ch-ua-platform': '"macOS"',
        'content-type': 'application/json',
        'accept': '*/*',
        'origin': 'https://www.thrivefantasy.com',
        'sec-fetch-site': 'same-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.thrivefantasy.com/',
        'accept-language': 'en-US,en;q=0.9,he;q=0.8',
        'sec-gpc': '1',
    }


    data = '{"currentPage":1,"currentSize":1000,"half":0,"Latitude":"40.9053143","Longitude":"-73.7857122"}'

    response = requests.post('https://api.thrivefantasy.com/houseProp/upcomingHouseProps', headers=headers, data=data)
    as_json = response.json()

    to_return = {}

    if as_json['response']['pagination']['totalPages'] > 1:
        print("WE NEED PAGINATION")
        import pdb; pdb.set_trace()


    for market in as_json['response']['data']:
        contest_prop = market['contestProp']
        line = contest_prop['propValue']
        name = "{} {}".format(contest_prop['player1']['firstName'], contest_prop['player1']['lastName'])

        if contest_prop['player1']['leagueType'] != 'NBA':
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