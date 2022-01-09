import time
import datetime
from tabulate import tabulate
import json
import requests
from selenium import webdriver

def query_dk():
    headers = {
        'authority': 'sportsbook.draftkings.com',
        'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
        'sec-ch-ua-platform': '"macOS"',
        'accept': '*/*',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://sportsbook.draftkings.com/leagues/basketball/88670846?category=player-props&subcategory=pts,-reb-',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': '_csrf=cf320b62-e5d9-4986-a49d-e98487825cc7; STIDN=eyJDIjoxMjIzNTQ4NTIzLCJTIjoyMzA0OTE1NzYyNSwiU1MiOjI0MDI2MDU2NDM5LCJWIjoxMjE3MTA2MTcxOSwiTCI6MSwiRSI6IjIwMjEtMTAtMjJUMTU6MDc6MzAuNzI3NjcyOFoiLCJTRSI6IlVTLURLIiwiVUEiOiJRc1MyRm0xaUNTMkJzTUNNb2h2d2xlVHlBTkEyRXFKRmtSb1FNZmhMREdNPSIsIkRLIjoiNzFkZjkwMWItNjFiMC00ZWExLWIyMWYtMTEzOWU1OTBlYWU1IiwiREkiOiI2NWJlZjcyMC02MjZlLTQyMDEtOWUxNC1hYTZiOWY5YTJjNTMiLCJERCI6NzQ3MjcwMjE5Nn0=; STH=fbd510a9563ba130341a1bbc38cee4fd3d98bf0343f40eedb5366c731be3bef9; _abck=48E71C9E6ED004A41B3AE1502694E136~-1~YAAQkpcwFxtGDqZ8AQAAR31vqAYUA/jVrxoPk1jFK69kDxrPWESb8/4rVDimVOWb/BuGrDqwmUCp123XwcgEqS5JdScuszc6iyQPA9Gda6jy3DSLa8TE8yd7+4hGfAPhEGM1GbfelGwXoYiiwiqBDbzhtn4iqBFQ9hRmKaUbFpsQKXEvkhEhzhpusEEdFGwRNXyezqYukyb6hhKpKJd58XFnmnYUZFOXdz1olNU2xcDLgYtYwuh1NJwpR0/Bm3WCFo/DGKx3i+qea3vNmenBchbg/5QSuUgswVxWdMHTsfzNypCebpqgzbqekVVGTaOgezl5iNQGVzoj2vq+HC/D2hLSanfCKSN7CJU44kCdgqvxdtgtVPIq6evC8xEnWzQs~-1~-1~-1; ak_bmsc=93B3275295ACD598586EBD8CB64C11E6~000000000000000000000000000000~YAAQkpcwFxxGDqZ8AQAAR31vqA1RwwMP2smWHT/m8s7w3sVBZA8LXncrkvSj+z+lKB4DShHUkSHGG8PCnqc63/chg5SSVbuCwWKnGhylA29ESDV3t4HMAS9CGIRS/eTx1TJgJXeBfSXQwFQBKI3yLPoa4Wv8/nzZATYepWpCtXDW+1+3MTQOVbLEq9OvZjRAQId6VTh2KkD7LpNlMnrCRT8XUWOf9P4OGnqR6Kt5Aan9S9ToxTIoifi3zWLTAwvUSo2XbiHyk6OXPDL1Rqy0oylHqiyT6wusYHf4xkqn9QVD9SfLVlePuToO6JiC4jkxco6sQjn8o3Eo+yBcZaNYYQv+VI7x6PNRrrVfNEXJIYjHBUC00O3zQY+pbXsnu8uBALGvR46WnujfYcBv8r0=; bm_sz=DFE5FDE7B133456669A18AEEF9D6E608~YAAQkpcwFx1GDqZ8AQAAR31vqA1XblTdT9QnYa/y4LP3nIttDAw8xGBKYpQB/EQ0RvvRuUuvge3QPr9IPcby/GcKIgUBw0R6FZzxf7mciHywy6Mc+MCnM36WAc6apNeRtS/zM6kjqQCi7bDZ/Yci699io4oziULiXKv54Rz2dy3zwPh2EA69uVde2uF4+X5Ppd3gUD9WywOxATS9lC8L+e3qGxdOdUoxKtZZM12uQlpHU7BgHB69LvF88vHWJElrJn/k3e4J0jIGx0Qvp0HB6HGyVkfp8QWTUJ1hwksAIfi8I34jHAec~3421766~3294518; _gcl_au=1.1.1143077212.1634913452; _gid=GA1.2.366897724.1634913452; _gat_UA-28146424-9=1; _gat_UA-28146424-14=1; _rdt_uuid=1634913451852.2ecec51e-7bee-4b4e-b3c6-50776887a2f6; _ga=GA1.2.1835386360.1634913452; clientDateOffset=240; notice_behavior=none; hgg=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2aWQiOiIxMjE3MTA2MTcxOSIsImRrZS02MCI6IjI4NSIsImRraC0xMjYiOiI4MzNUZF9ZSiIsImRrZS0xMjYiOiIwIiwiZGtlLTE0NCI6IjQzMSIsImRrZS0xNDkiOiIzMzczIiwiZGtlLTE1MCI6IjU2NyIsImRrZS0xNTEiOiI0NTciLCJka2UtMTUyIjoiNDU4IiwiZGtlLTE1MyI6IjQ1OSIsImRrZS0xNTQiOiI0NjAiLCJka2UtMTU1IjoiNDYxIiwiZGtlLTE1NiI6IjQ2MiIsImRrZS0xNzkiOiI1NjkiLCJka2UtMjA0IjoiNzEwIiwiZGtlLTIxOSI6IjIyNDYiLCJka2UtMjIxIjoiODEzIiwiZGtoLTIyOSI6IklsTmhDMDZTIiwiZGtlLTIyOSI6IjAiLCJka2UtMjMwIjoiODU3IiwiZGtlLTI4OCI6IjExMjgiLCJka2UtMzAwIjoiMTE4OCIsImRrZS0zMTgiOiIxMjYwIiwiZGtlLTM0NSI6IjEzNTMiLCJka2UtMzQ2IjoiMTM1NiIsImRraC0zOTQiOiJDZlhBaHpkTyIsImRrZS0zOTQiOiIwIiwiZGtoLTQwOCI6IllkYVZSbURaIiwiZGtlLTQwOCI6IjAiLCJka2UtNDE2IjoiMTY0OSIsImRrZS00MTgiOiIxNjUxIiwiZGtlLTQxOSI6IjE2NTIiLCJka2UtNDIwIjoiMTY1MyIsImRrZS00MjEiOiIxNjU0IiwiZGtlLTQyMiI6IjE2NTUiLCJka2UtNDI5IjoiMTcwNSIsImRrZS01NTAiOiIyMzE4IiwiZGtlLTU2NyI6IjIzODciLCJka2UtNTY4IjoiMjM5MCIsImRraC01ODgiOiJ4b0hRaGhaZyIsImRrZS01ODgiOiIwIiwiZGtlLTYzNiI6IjI2OTEiLCJka2UtNzAwIjoiMjk5MiIsImRrZS03MzkiOiIzMTQwIiwiZGtlLTc1NyI6IjMyMTIiLCJka2gtNzY4IjoiVVpHYzBySHgiLCJka2UtNzY4IjoiMCIsImRrZS03OTAiOiIzMzQ4IiwiZGtlLTc5NCI6IjMzNjQiLCJka2UtODA0IjoiMzQxMSIsImRrZS04MDYiOiIzNDI2IiwiZGtlLTgwNyI6IjM0MzciLCJka2UtODI0IjoiMzUxMSIsImRrZS04MjUiOiIzNTE0IiwiZGtlLTgzNCI6IjM1NTciLCJka2UtODM2IjoiMzU3MCIsImRrZS04NjUiOiIzNjk1IiwiZGtlLTg3MyI6IjM3NDEiLCJka2UtODc2IjoiMzc1MiIsImRrZS04NzciOiIzNzU2IiwiZGtlLTg4MCI6IjM3NjYiLCJka2UtODgxIjoiMzc3MCIsImRrZS04ODIiOiIzNzczIiwiZGtoLTg5NSI6IjJ6MERZU0MyIiwiZGtlLTg5NSI6IjAiLCJka2UtOTAzIjoiMzg0OCIsImRrZS05MDQiOiIzODUyIiwiZGtlLTkwNyI6IjM4NjMiLCJka2UtOTE3IjoiMzkxMyIsImRrZS05MTgiOiIzOTE3IiwiZGtlLTkyNCI6IjM5NDIiLCJka2UtOTM4IjoiNDAwNCIsImRrZS05NDciOiI0MDQyIiwiZGtlLTk0OCI6IjQwNDUiLCJka2UtOTQ5IjoiNDA0OSIsImRrZS05NzUiOiI0MTY4IiwiZGtlLTk3NiI6IjQxNzEiLCJka2UtOTgwIjoiNDE4NyIsImRrZS05ODciOiI0MjE2IiwiZGtlLTk4OCI6IjQyMjEiLCJka2UtOTkxIjoiNDIzNCIsImRrZS05OTMiOiI0MjQwIiwiZGtlLTk5NiI6IjQyNTAiLCJka2UtOTk3IjoiNDI1MyIsImRrZS0xMDAxIjoiNDI3MyIsImRrZS0xMDAyIjoiNDI3NiIsImRrZS0xMDAzIjoiNDI3OSIsImRraC0xMDA1IjoiZHJZbmhVRTEiLCJka2UtMTAwNSI6IjAiLCJka2UtMTAwOCI6IjQzMDUiLCJka2UtMTAxOCI6IjQzNTAiLCJka2UtMTA1MSI6IjQ0NzkiLCJka2UtMTA1NyI6IjQ1MDYiLCJka2UtMTA1OCI6IjQ1MDgiLCJka2UtMTA2MSI6IjQ1MjciLCJuYmYiOjE2MzQ5MTM0NTIsImV4cCI6MTYzNDkxMzc1MiwiaWF0IjoxNjM0OTEzNDUyLCJpc3MiOiJkayJ9.fCIoqkrjSCgLHZaCF0d9pBltFrEmjY-h8bdc1RvWuuc; ab.storage.deviceId.b543cb99-2762-451f-9b3e-91b2b1538a42=%7B%22g%22%3A%2295e8d2c7-8396-38cd-f663-8bc03000ac8b%22%2C%22c%22%3A1634913452816%2C%22l%22%3A1634913452816%7D; _uetsid=9773eb30334511ec94358d19709be832; _uetvid=97741dc0334511ec8216b1903af27dd6; _tq_id.TV-54368172-1.fee2=021e5bd18387e5df.1634913453.0.1634913453..; ab.storage.sessionId.b543cb99-2762-451f-9b3e-91b2b1538a42=%7B%22g%22%3A%22e95d4744-9efa-9c1c-86ff-59e270f054d1%22%2C%22e%22%3A1634915252888%2C%22c%22%3A1634913452813%2C%22l%22%3A1634913452888%7D; _dpm_ses.16f4=*; _dpm_id.16f4=51042e44-22a6-42ce-840e-b993ac9dc740.1634913453.1.1634913453.1634913453.813dc24c-d1f9-4232-8154-22043f6bc131; _scid=6c80bc65-d0d0-41c0-962d-deef27b15751; _hjid=1a0df955-077a-49ac-ae1d-15728eb2f3a8; _hjFirstSeen=1; _hjAbsoluteSessionInProgress=0; __qca=P0-1267508163-1634913453379; _ga_QG8WHJSQMJ=GS1.1.1634913451.1.1.1634913453.0; _fbp=fb.1.1634913453995.1993644731; gatsby-siteExp=US-NY-SB; networkType=fios; STE="2021-10-22T15:07:39.3781836Z"; bm_sv=B00DD361395196AD4B681FF3F8DDA5EF~00MSF2SIT0Cmki9Go6NNlPB6ZZJjMWQU57TiCO6ib0fAmfgK/oSjjo2AkCAIrnKFK5U1KiKxFDXqvrVruMmh7i3wvnsw+XkG5dwZTAgY+mpRpFcw4560OL3gwpKWaNikXTI9h5EklEaRXS0qmA20A7qG3WQgchVmqA9t2R8d3Wg=; quickStartWelcomeModalHidden=1',
    }

    params = (
        ('format', 'json'),
    )
    to_return = {}

    target_categories = [5585, 5586, 5587]
    target_category_labels = [" Shots On Goal", " Points", " Assists"]

    for i in range(len(target_categories)):
        target_category = target_categories[i]
        target_category_label = target_category_labels[i]
        time.sleep(0.5)

        response = requests.get('https://sportsbook.draftkings.com//sites/US-SB/api/v4/eventgroups/88670853/categories/550/subcategories/{}'.format(target_category), headers=headers, params=params)

        as_json = response.json()
        categories = as_json['eventGroup']['offerCategories']
        selected_category = None
        for category in categories:
            if category["offerCategoryId"] == 550:
                selected_category = category
                break

        selected_subcategory = None
        for subcategory in selected_category["offerSubcategoryDescriptors"]:
            if subcategory["subcategoryId"] == target_category:
                selected_subcategory = subcategory
                break


        for offer in selected_subcategory['offerSubcategory']['offers']:
            for sub_offer in offer:
                for outcome in sub_offer["outcomes"]:
                    outcome_label = outcome["label"]
                    line = outcome["line"]
                    odds = outcome["oddsDecimal"]
                    if not target_category_label in sub_offer['label']:
                        import pdb; pdb.set_trace()

                    name = sub_offer['label'].replace(target_category_label, '')

                    if outcome_label == "Over":
                        outcome_label = "o"
                    elif outcome_label == "Under":
                        outcome_label = "u"
                    if not name in to_return:
                        to_return[name] = {}
                    # import pdb; pdb.set_trace()

                    
                    category = target_category_label.strip()
                    if not category in to_return[name]:
                        to_return[name][category] = "{} {}".format(line, odds)
                        # to_return[name][category] = "{}{} {}".format(outcome_label, line, odds)
                    else: 
                        over_odds = float(to_return[name][category].split(' ')[1])
                        under_odds = float(odds)
                        odds_percentage = over_odds / (over_odds + under_odds)
                        to_return[name][category] = " {} {}".format(line, odds_percentage)



        #NB. Original query string below. It seems impossible to parse and
        #reproduce query strings 100% accurately so the one below is given
        #in case the reproduced version is not "correct".
        # response = requests.get('https://sportsbook.draftkings.com//sites/US-SB/api/v4/eventgroups/88670846/categories/583/subcategories/5001?format=json', headers=headers)
    return to_return


# driver = webdriver.Chrome("../master_scrape_process/chromedriver")

# cookies_file = open("draftkings.com_cookies.txt", "r")
# lines = cookies_file.readlines()
# dictionaries = []
# for line in lines:
#     cookies_dict = {}
#     parts = line.split('	')
#     cookies_dict["name"] = parts[5]
#     cookies_dict["value"] = parts[6].strip()
#     cookies_dict["domain"] = parts[0]

#     if parts[0] != '.draftkings.com':
#         continue
#     dictionaries.append(cookies_dict)

if __name__ == "__main__":
    result = query_dk()

    print(result)