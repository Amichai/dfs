import requests
import datetime


def normalize_name(name):
    name = name.replace("  ", " ")
    name = name.replace("’", "'")
    parts = name.split(" ")
    if len(parts) > 2:
        return "{} {}".format(parts[0], parts[1]).strip()

    name = name.replace(".", "")

    return name.strip()


def query_awsemo():
    now = datetime.datetime.now()
    to_return = {}
    year = now.year
    month = now.month
    day = now.day
    url = "https://app-api-os-prod.azurewebsites.net/api/odds/ecommerce?leagueCode=NBA&startDate={}-{}-{}T00:00:00-05:00&endDate={}-{}-{}T23:59:59-05:00&state=NJ".format(year, month, day, year, month, day)
    response = requests.get(url)
    as_json = response.json()
    for bet in as_json:
        if "awesemoProj" in bet:
            league = bet["leagueCode"]
            name = bet["participantName"]
            stat = bet["offerName"]
            if bet["awesemoProj"] == None:
                continue
            
            name = normalize_name(name)
            proj = bet["awesemoProj"].split(' ')[0]

            if not name in to_return:
                to_return[name] = {}

            if not stat in to_return[name]:
                to_return[name][stat] = {}
            to_return[name][stat] = proj


    return to_return


if __name__ == "__main__":
    query_awsemo()