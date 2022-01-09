import time
import requests


def underdog_query_line(is_NFL=False):

    url = "https://api.underdogfantasy.com/beta/v2/over_under_lines"
    time.sleep(0.5)
    response = requests.get(url)

    to_return = {}

    as_json = response.json()

    player_id_to_name = {}
    for player in as_json["players"]:
        player_id = player["id"]

        target_sport_id = "NBA"
        if is_NFL:
            target_sport_id = "NFL"

        if player["sport_id"] != target_sport_id:
            continue

        player_id_to_name[player_id] = "{} {}".format(player["first_name"], player["last_name"])

    appearance_id_to_player_id = {}
    for appearance in as_json["appearances"]:
        appearance_id = appearance["id"]
        player_id = appearance["player_id"]
        if not player_id in player_id_to_name:
            continue

        appearance_id_to_player_id[appearance_id] = player_id



    for ou_line in as_json["over_under_lines"]:
        appearance_id = ou_line['over_under']['appearance_stat']['appearance_id']
        if not appearance_id in appearance_id_to_player_id:
            continue

        stat_value = ou_line["stat_value"]
        if ou_line['status'] != "active":
            continue


        stat = ou_line['over_under']['appearance_stat']['stat']
        player_id = appearance_id_to_player_id[appearance_id]
        player_name = player_id_to_name[player_id]

        if not player_name in to_return:
            to_return[player_name] = {}
        to_return[player_name][stat] = stat_value
    return to_return


# underdog_query_line()