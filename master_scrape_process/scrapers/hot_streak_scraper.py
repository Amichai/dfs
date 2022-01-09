import requests
import time



def query_game(game_id, to_return):
    
    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'sec-ch-ua-platform': '"macOS"',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Origin': 'https://app.hotstreak.gg',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://app.hotstreak.gg/',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    data = '{"query":"query game($id: ID!) { game(id: $id) {\\n        __typename\\nid\\nbroadcastChannel\\nclock\\nelapsed\\nevent\\nmarketsCount\\n... on FootballGame {\\n\\n__typename\\nid\\ncurrentDrive {\\n\\n__typename\\nid\\ncurrentPlay {\\n\\n__typename\\nid\\ndistance\\ndown\\nlocation {\\n\\n__typename\\nid\\n\\n}\\nyardLine\\n\\n}\\npossession {\\n\\n__typename\\nid\\n\\n}\\n\\n}\\n\\n}\\nleagueId\\nmarkets {\\n\\n__typename\\nid\\naffinity\\ndurations\\nlines\\noptions\\nprobabilities\\n\\n}\\nopponents {\\n\\n__typename\\nid\\ndesignation\\ngameId\\nparticipants {\\n\\n__typename\\nid\\nplayer {\\n\\n__typename\\nid\\nfirstName\\nheadshotUrl\\nlastName\\nnumber\\nposition\\n\\n}\\nposition\\nopponentId\\n\\n}\\nteam {\\n\\n__typename\\nid\\nmarket\\nname\\nshortName\\n\\n}\\n\\n}\\nperiod\\nscheduledAt\\nscores\\nstatus\\n\\n      } }","variables":{"id":"' + game_id + '"}}'

    time.sleep(0.5)
    response = requests.post('https://ft-api-production.herokuapp.com/graphql', headers=headers, data=data)

    as_json = response.json()
    player_id_to_name = {}
    
    for opponent in as_json['data']['game']['opponents']:
        team_name = opponent['team']['shortName']
        for participant in opponent['participants']:
            first_name = participant['player']["firstName"]
            last_name = participant['player']["lastName"]
            id = participant['id']
            player_id_to_name[id] = "{} {}".format(first_name, last_name)


    markets = as_json['data']['game']['markets']
    for market in markets:
        market_id = market['id']
        parts = market_id.split(',')
        stat = parts[1]
        if stat == "stocks":
            return

    for market in markets:
        market_id = market['id']
        parts = market_id.split(',')
        player_id = parts[0]
        stat = parts[1]
        player_name = player_id_to_name[player_id]
        lines = market['lines']

        # import pdb; pdb.set_trace()
        if len(lines) != 1:
            continue
        assert len(lines) == 1
        line = lines[0]

        if not player_name in to_return:
            to_return[player_name] = {}
        
        original_line = float(line)
        odds_percentage = market['probabilities'][0]
        line = float(line) + (float(odds_percentage) - 0.5) * 1.5
        assert abs(line - original_line) < 0.9
        to_return[player_name][stat] = str(line)


def query_hot_streak():

    to_return = {}
    headers = {
        'Connection': 'keep-alive',
        'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'sec-ch-ua-platform': '"macOS"',
        'Content-Type': 'application/json',
        'Accept': '*/*',
        'Origin': 'https://app.hotstreak.gg',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://app.hotstreak.gg/',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    data = '{"query":"query leagues { leagues {\\n        __typename\\nid\\nalias\\nbroadcastChannel\\ngames {\\n\\n__typename\\nid\\nbroadcastChannel\\nclock\\nevent\\nleagueId\\nopponents {\\n\\n__typename\\nid\\ndesignation\\nteam {\\n\\n__typename\\nid\\nmarket\\nname\\nshortName\\n\\n}\\n\\n}\\nperiod\\nscheduledAt\\nscores\\nstatus\\nmarketsCount\\n\\n}\\n\\n      } }","variables":{}}'

    response = requests.post('https://ft-api-production.herokuapp.com/graphql', headers=headers, data=data)
    game_ids = []
    
    as_json = response.json()

    for league in as_json['data']['leagues']:
        if league['alias'] != "NBA":
            continue

        for game in league['games']:
            game_id = game['id']
            if game_id in game_ids:
                continue

            game_ids.append(game_id)


            query_game(game_id, to_return)

    return to_return

    
if __name__ == "__main__":
    query_hot_streak()