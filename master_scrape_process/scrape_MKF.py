from os import stat
import time
import requests


def scrape_game_id(game_id, s_id=None):
    headers = {
        'authority': 'www.monkeyknifefight.com',
        'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
        'sec-ch-ua-platform': '"macOS"',
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'accept': '*/*',
        'origin': 'https://www.monkeyknifefight.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.monkeyknifefight.com/game/13/all_day',
        'accept-language': 'en-US,en;q=0.9,he;q=0.8',
        'cookie': 'ia_btag=a_2020b_71c_1457; _BEAMER_FIRST_VISIT_cBBfzadO13015=2021-10-09T14:25:27.996Z; PHPSESSID=k5n74eoa97i02u46he5jr87u54; _BEAMER_USER_ID_cBBfzadO13015=8f4c8be0-f902-4831-8c62-95cf80bda7e1; _BEAMER_FILTER_BY_URL_cBBfzadO13015=false; AWSALB=Mmvenby/vlB64I54bAs7pQhS2knK2WSe8WM+DockJHhVZuExIt9lzFh63t7ZUUV3JCNMcN1m1rPF0Vgl13b8+kr1mwHkKa/LawZ88/dxfB9RL9DSsAD4HnFBZnq2; AWSALBCORS=Mmvenby/vlB64I54bAs7pQhS2knK2WSe8WM+DockJHhVZuExIt9lzFh63t7ZUUV3JCNMcN1m1rPF0Vgl13b8+kr1mwHkKa/LawZ88/dxfB9RL9DSsAD4HnFBZnq2',
        'sec-gpc': '1',
    }

    if s_id != None:
        data = {
        'DATA': '{"idSport":"13","bAdShown":true,"filterOptions":{"iGameCodeGlobalId":"' + str(game_id) + '","szGameType":"","idGameType":"' + s_id + '","eLobbyType":"ALL"}}',
        'TOKEN': ''
        }
    else:
        data = {
        'DATA': '{"idSport":"13","bAdShown":true,"filterOptions":{"iGameCodeGlobalId":"' + str(game_id) + '","szGameType":"","idGameType":"","eLobbyType":"ALL"}}',
        'TOKEN': ''
        }

    time.sleep(0.2)
    response = requests.post('https://www.monkeyknifefight.com/api/v3.0.1/GET_LOBBY', headers=headers, data=data)
    # print(response.text)
    return response.json()


def query_mkf_lines():
    name_to_stat_to_line = {}
    all_ids = []
    result = scrape_game_id('0')
    for key, game in result['data']['sporting_events'].items():
        game_id = game['iGameCodeGlobalId']

        all_ids.append(game_id)

    for game_id in all_ids:
        result = scrape_game_id(game_id)    

        s_ids = []
        for game in result['data']['games']['lobby_data']['games']:
            if game['sty'] != "OVER/UNDER":
                continue

            if game['numTiers'] == '2':
                continue
            if game["eLobbyType"] != "FANTASY":
                continue

            s_id = str(game['id'])
            if not s_id in s_ids:
                s_ids.append(s_id)
            pass

        for s_id in s_ids:
            
            result2 = scrape_game_id(game_id, s_id)
            print(result2)
            if not 'matchups' in result2['data']['gamedata']:
                continue
            for matchup in result2['data']['gamedata']['matchups']:
                if "playerName" in matchup:
                    name = matchup["playerName"]
                    stat_name = matchup["szStatName"]
                    if stat_name == "Fantasy Points":
                        # import pdb; pdb.set_trace()
                        pass
                        
                    value = matchup["assertionValue"]
                    # print("{} - {}, {}, {}".format(game_id, name, stat_name, value))
                    if not name in name_to_stat_to_line:
                        name_to_stat_to_line[name] = {}

                    name_to_stat_to_line[name][stat_name] = value
                else:
                    continue
    
    return name_to_stat_to_line

if __name__ == "__main__":
    result = query_mkf_lines()
    print(result)