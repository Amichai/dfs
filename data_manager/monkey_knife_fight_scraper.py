import requests
import utils
import data_manager

cookies = {
    'PHPSESSID': 'lgr431lnsv4nfno8fd3f5d15e5',
    '_gcl_au': '1.1.1574004890.1668032173',
    '_ga': 'GA1.2.1363385525.1668032173',
    '_gid': 'GA1.2.1897681832.1668032173',
    '_scid': '37681489-6168-4904-955b-60ffd512d9fe',
    '_rdt_uuid': '1668032173521.429e3893-a310-4184-9d35-e9429edf1aa7',
    '_fbp': 'fb.1.1668032173703.1226500747',
    '_tt_enable_cookie': '1',
    '_ttp': '48185ba6-4dcb-49de-8603-649144ab27eb',
    'hubspotutk': '51ac0cb3b8a46f5521064dc87e50ec8a',
    '__hssrc': '1',
    '_hjSessionUser_1470631': 'eyJpZCI6ImU2MDVmM2MwLWE5YzgtNWFkNS1iMThhLWQzZjAyMzFhZjFjMyIsImNyZWF0ZWQiOjE2NjgwMzIxNzM4MzksImV4aXN0aW5nIjp0cnVlfQ==',
    '_hjIncludedInSessionSample': '1',
    '_hjSession_1470631': 'eyJpZCI6IjU2MmU4YmI3LTQ0ZDAtNDQ5ZC05MmQwLTU2YzliNDZiYzI4NiIsImNyZWF0ZWQiOjE2NjgxMDc5NTE5NzEsImluU2FtcGxlIjp0cnVlfQ==',
    '_hjAbsoluteSessionInProgress': '1',
    '__hstc': '222275783.51ac0cb3b8a46f5521064dc87e50ec8a.1668032174692.1668036703879.1668107952224.3',
    '_uetsid': '1f46b3e0607c11eda5c5d1c31eaf1b6e',
    '_uetvid': 'f2d7bb1092b611ec97fc77bfac4e66df',
    '__hssc': '222275783.2.1668107952224',
    'AWSALB': 'V/v1ZHeIFiT/bhb3Mswugkx/NBkQ33H4nRw4QYpz+Y2Q/z+81MZPjXe2sfMDmBONFNqAawWoWpRWzbHUv/EiAMX2ShayO0ALwyRX+o5Drc0CXP9RfYlp9TN1oLTf',
    'AWSALBCORS': 'V/v1ZHeIFiT/bhb3Mswugkx/NBkQ33H4nRw4QYpz+Y2Q/z+81MZPjXe2sfMDmBONFNqAawWoWpRWzbHUv/EiAMX2ShayO0ALwyRX+o5Drc0CXP9RfYlp9TN1oLTf',
}

headers = {
    'authority': 'www.monkeyknifefight.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
    # Requests sorts cookies= alphabetically
    # 'cookie': 'PHPSESSID=lgr431lnsv4nfno8fd3f5d15e5; _gcl_au=1.1.1574004890.1668032173; _ga=GA1.2.1363385525.1668032173; _gid=GA1.2.1897681832.1668032173; _scid=37681489-6168-4904-955b-60ffd512d9fe; _rdt_uuid=1668032173521.429e3893-a310-4184-9d35-e9429edf1aa7; _fbp=fb.1.1668032173703.1226500747; _tt_enable_cookie=1; _ttp=48185ba6-4dcb-49de-8603-649144ab27eb; hubspotutk=51ac0cb3b8a46f5521064dc87e50ec8a; __hssrc=1; _hjSessionUser_1470631=eyJpZCI6ImU2MDVmM2MwLWE5YzgtNWFkNS1iMThhLWQzZjAyMzFhZjFjMyIsImNyZWF0ZWQiOjE2NjgwMzIxNzM4MzksImV4aXN0aW5nIjp0cnVlfQ==; _hjIncludedInSessionSample=1; _hjSession_1470631=eyJpZCI6IjU2MmU4YmI3LTQ0ZDAtNDQ5ZC05MmQwLTU2YzliNDZiYzI4NiIsImNyZWF0ZWQiOjE2NjgxMDc5NTE5NzEsImluU2FtcGxlIjp0cnVlfQ==; _hjAbsoluteSessionInProgress=1; __hstc=222275783.51ac0cb3b8a46f5521064dc87e50ec8a.1668032174692.1668036703879.1668107952224.3; _uetsid=1f46b3e0607c11eda5c5d1c31eaf1b6e; _uetvid=f2d7bb1092b611ec97fc77bfac4e66df; __hssc=222275783.2.1668107952224; AWSALB=V/v1ZHeIFiT/bhb3Mswugkx/NBkQ33H4nRw4QYpz+Y2Q/z+81MZPjXe2sfMDmBONFNqAawWoWpRWzbHUv/EiAMX2ShayO0ALwyRX+o5Drc0CXP9RfYlp9TN1oLTf; AWSALBCORS=V/v1ZHeIFiT/bhb3Mswugkx/NBkQ33H4nRw4QYpz+Y2Q/z+81MZPjXe2sfMDmBONFNqAawWoWpRWzbHUv/EiAMX2ShayO0ALwyRX+o5Drc0CXP9RfYlp9TN1oLTf',
    'origin': 'https://www.monkeyknifefight.com',
    'referer': 'https://www.monkeyknifefight.com/game/13/all_day',
    'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
}

data = {
    'DATA': '{"idSport":"13","szDescriptor":"all day"}',
    'TOKEN': '88870f656fd1a63323d0040f1f580dd8',
}

response = requests.post('https://www.monkeyknifefight.com/api/v3.0.2/GET_LOBBY', cookies=cookies, headers=headers, data=data)

as_json = response.json()

assert as_json['status'] == 'ok'

ml = as_json['data']['lobby_data']['games']['ml']
rf = as_json['data']['lobby_data']['games']['rf']

dataManager = data_manager.DataManager('NBA')


for matchup in ml:
  availableLines = matchup['matchups']
  multiplier = matchup['poMultiplier']
  need_to_win = matchup['need_to_win']
  total_diff = 0
  print("PARLAY! ------ {}x - {}/{}".format(multiplier, need_to_win, len(availableLines)))
  for line in availableLines:
    name = utils.normalize_name(line['playerName'])
    stat = line['szStatName']
    lineVal = float(line['assertionValue'])

    projections = dataManager.query_projection('NBA', 'Caesars', name)


    reference_val = None
    if stat == "Points" or stat == "Rebounds" or stat == "Assists":
      if projections[stat + ":isActive"] == True:
        reference_val = float(projections[stat])
      else:
        reference_val = lineVal
    elif stat == "Fantasy Points":
      caesars_fs = utils.parse_projection_from_caesars_lines(projections)
      if caesars_fs[1] > 3:
        reference_val = caesars_fs[0]
      else:
        reference_val = lineVal
    elif stat == "Three Pointers Made":
      reference_val = lineVal
    elif stat == "Steals and Blocks":
      if projections["Blocks + Steals:isActive"] == True:
        reference_val = float(projections['Blocks + Steals'])
      else:
        reference_val = lineVal



    percent_diff = utils.percentChange(lineVal, reference_val)
    print("{}, {}, {} -> {} = {}".format(name, stat, lineVal, reference_val, round(percent_diff, 2)))
    total_diff += abs(percent_diff)
  
  print("TOTAL DIFF: {}".format(round(total_diff, 2)))

  pass


#2/2 -> 3.5x     A  0.875
#3/3 -> 5x       B  0.625
#4/4 -> 10x      B  0.625
#5/5 -> 20x      B  0.625
#6/6 -> 40x      B  0.625
#8/8 -> 125x     C  0.488
#10/10 -> 500x   C  0.488

#2/3 -> 2x       1.0
#2/3 -> 1.7x     0.85
#3/4 -> 2.5x     0.7812