
import datetime
import requests
from hand_crafted_projections import read_projections



current_date = datetime.datetime.now()
url = 'https://stathero-api-256801.appspot.com/nba/rivals/{}/{}/{}'.format(current_date.year, current_date.month, current_date.day)

response = requests.get(url)


name_to_price2 = {}
for game in response.json()['games']:
    home = game["home_team"]
    for player in home["players"]:
        name = "{} {}".format(player["first_name"], player["last_name"])
        price = float(player['price'])
        name_to_price2[name] = price
    away = game["away_team"]
    for player in away["players"]:
        name = "{} {}".format(player["first_name"], player["last_name"])
        price = float(player['price'])
        name_to_price2[name] = price


projections = read_projections("past_permorance_{}_{}_21.txt".format(current_date.month, current_date.day))

name_to_proj_price = {}

for name, proj in projections.items():
    name = name.replace(" Jr.", "")
    if not name in name_to_price2:
        print("STAT HERO IS MISSING: {}".format(name))
        continue
    # if name == "CJ McCollum":
    #     continue
    price = name_to_price2[name]
    name_to_proj_price[name] = (proj, price)


best_roster = None
best_val = 0

all_names = list(name_to_proj_price.keys())
name_count = len(all_names)
for i1 in range(name_count):
    for i2 in range(name_count):
        if i2 <= i1:
            continue
        for i3 in range(name_count):
            if i3 <= i2:
                continue
            
            name1 = all_names[i1]
            name2 = all_names[i2]
            name3 = all_names[i3]

            cost1 = name_to_proj_price[name1][1]
            cost2 = name_to_proj_price[name2][1]
            cost3 = name_to_proj_price[name3][1]

            val1 = name_to_proj_price[name1][0]
            val2 = name_to_proj_price[name2][0]
            val3 = name_to_proj_price[name3][0]

            total_cost = cost1 + cost2 + cost3
            if total_cost > 34000:
                continue

            roster = [name1, name2, name3]

            val = (val1 + val2 + val3)
            if val >= best_val:
                best_val = val
                best_roster = [name1, name2, name3]

                print("{} - {}, {}".format(best_roster, best_val, total_cost))


