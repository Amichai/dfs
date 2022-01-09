import datetime
import requests



def sh_query_prices():
    current_date = datetime.datetime.now()
    url = 'https://stathero-api-256801.appspot.com/nba/rivals/{}/{}/{}'.format(current_date.year, current_date.month, current_date.day)
    print(url)
    response = requests.get(url)

    name_to_price = {}
    for game in response.json()['games']:
        home = game["home_team"]
        for player in home["players"]:
            name = "{} {}".format(player["first_name"], player["last_name"])
            price = float(player['price'])
            projection = float(player["projection"])
            if not name in name_to_price:
                name_to_price[name] = {}

            name_to_price[name]["price"] = str(price)
            name_to_price[name]["projection"] = str(round(projection, 2))
        away = game["away_team"]
        for player in away["players"]:
            name = "{} {}".format(player["first_name"], player["last_name"])
            if not name in name_to_price:
                name_to_price[name] = {}

            price = float(player['price'])
            projection = float(player["projection"])
            name_to_price[name]["price"] = str(price)
            name_to_price[name]["projection"] = str(round(projection, 2))

    return name_to_price

if __name__ == "__main__":
    sh_query_prices()