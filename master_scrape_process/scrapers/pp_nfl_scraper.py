import json
from selenium import webdriver


def nfl_pp_projections(driver):
    url = 'https://api.prizepicks.com/projections?league_id=9&per_page=500&single_stat=false'
    driver.get(url)

    as_text = driver.find_element_by_tag_name('body').text

    as_json = json.loads(as_text)

    assert as_json["meta"]["total_pages"] == 1

    data = as_json['data']
    included = as_json['included']

    id_to_name = {}
    player_ids = []
    for player in included:
        attr = player["attributes"]
        player_name = attr['name']
        # team = attr['team']
        created_at = attr["created_at"]
        updated_at = attr['updated_at']
        player_id = player['id']
        player_ids.append(player_id)
        id_to_name[player_id] = player_name

    name_to_projections = {}

    for projection in data:
        attr = projection['attributes']
        stat_type = attr['stat_type']
        created_at = attr["created_at"]
        updated_at = attr["updated_at"]
        line_score = attr["line_score"]
        projection_type = attr["projection_type"]

        player_id = projection['relationships']['new_player']['data']['id']
        player_name = id_to_name[player_id]
        if not player_name in name_to_projections:
            name_to_projections[player_name] = {}
        name_to_projections[player_name][stat_type] = line_score
        
    return name_to_projections


if __name__ == "__main__":
    driver = webdriver.Chrome("../../master_scrape_process/chromedriver")
    result = nfl_pp_projections(driver)
    print(result)