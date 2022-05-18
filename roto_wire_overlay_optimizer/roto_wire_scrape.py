from pdb import Pdb
import requests
from selenium import webdriver
import time
from bs4 import BeautifulSoup

from master_scrape_process.fd_optimizer import normalize_name



all_teams = []
def scrape_lineups():
    gtd_statuses = ["25%", "50%", "75%", "O"]
    questionable_starters = []
    questionable_bench = []

    status_mapping = {
        "Very Likely To Play": "",
        "Very Unlikely To Play": "O",
        "Unlikely To Play": "25%",
        "Toss Up To Play": "50%",
        "Likely To Play": "75%",
    }

    url = "https://www.rotowire.com/basketball/nba-lineups.php"
    time.sleep(0.3)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    all_starters = []
    all_the_information = {}

    games = soup.select('.lineup.is-nba')
    for game in games:
        game_time = game.select('.lineup__time')[0].text
        if len(game.select('.lineup__teams > a')) == 0:
            continue
        team1 = game.select('.lineup__teams > a')[0].text.strip()
        team2 = game.select('.lineup__teams > a')[1].text.strip()

        all_teams.append(team1)
        all_teams.append(team2)

        if len(game.select('div.heading')) > 0 and "POSTPONED" in game.select('div.heading')[0].text:
            continue

        team1_record = game.select('.lineup__wl')[0].text
        team2_record = game.select('.lineup__wl')[1].text

        # lineup1_status = game.select('.lineup__status')[0].text.strip()
        # lineup2_status = game.select('.lineup__status')[1].text.strip()
        lineup_list1 = game.select('.lineup__list')[0]
        
        lineup_list2 = game.select('.lineup__list')[1]

        lineup1_players = lineup_list1.select('.lineup__player')
        lineup2_players = lineup_list2.select('.lineup__player')

        money_line = game.select('.lineup__extra')[0].select('.lineup__odds')[0].select('.composite')[0].text
        spread = game.select('.lineup__extra')[0].select('.lineup__odds')[0].select('.composite')[1].text
        over_under = game.select('.lineup__extra')[0].select('.lineup__odds')[0].select('.composite')[2].text

        if len(money_line.split(' ')) > 1:
            odds = float(money_line.split(' ')[1])
            if odds < 0:
                implied_probability = (-1*(odds)) / (-1*(odds) + 100)
            else:
                implied_probability = 100.0 / (odds + 100)
            implied_probability = round(implied_probability, 2)
            to_print = "line: {} ({}%), spread: {}, o/u: {}".format(money_line, implied_probability, spread, over_under)
            team_key = "{}-{}".format(team1, team2)
            if not team_key in all_the_information:
                all_the_information[team_key] = {}
            all_the_information[team_key]['line'] = "{} ({}%)".format(money_line, implied_probability)
            all_the_information[team_key]['spread'] = spread
            all_the_information[team_key]['o/u'] = over_under
        else:
            print("UNABLE TO PARSE MONEY LINE")
            print(money_line)

        lineups = [lineup1_players, lineup2_players]
        teams = [team1, team2]
        records = [team1_record, team2_record]
        idx = 0
        for lineup in lineups:
            current_team = teams[idx]
            is_starter = True
            seen_names = []

            idx += 1

            player_count = 0
            for player in lineup:
                if player_count == 5:
                    is_starter = False
                player_count += 1

                player_link = player.select('a')[0]
                name =  player_link['title']
                player_key = normalize_name(name)
                
                player_status = ""
                status = player['title']
                if is_starter:
                    player_status += "S "
                else:
                    player_status += "B "

                if status in status_mapping:
                    status = status_mapping[status]

                player_status += status
                if not player_key in all_the_information:
                    all_the_information[player_key] = {}
                    all_the_information[player_key]["status"] = player_status

                
                pos = player.select('.lineup__pos')[0].text

                if is_starter:
                    all_starters.append((name, current_team, status))
                if name in seen_names:
                    continue

                seen_names.append(name)
                url = player_link['href']
                

                if is_starter and status in gtd_statuses:
                    questionable_starters.append((name, current_team, status))
                if not is_starter and status in gtd_statuses:
                    questionable_bench.append((name, current_team, status))

    return (all_starters, questionable_starters, questionable_bench, all_the_information)


def scrape_depth_chart():

    time.sleep(0.2)
    driver = webdriver.Chrome("../master_scrape_process/chromedriver")
    url = "https://www.rotowire.com/basketball/depth-charts.php"
    driver.get(url)

    cookies_file = open("rotowire.com_cookies.txt", "r")
    lines = cookies_file.readlines()
    for line in lines:
        cookies_dict = {}
        parts = line.split('	')
        name = parts[5]
        value = parts[6].strip()
        domain = parts[0]

        driver.add_cookie({"name": name, "value": value, "domain": domain})


    time.sleep(0.2)
    
    driver.get(url)

    teams = driver.find_elements_by_class_name('depth-charts__block')
    for team in teams:
        team_name = team.find_elements_by_class_name('depth-charts__team-name')[0].text
        print(team_name)

        positions = team.find_elements_by_class_name('depth-charts__pos')
        for position in positions:
            pos_name = position.find_elements_by_class_name("depth-charts__pos-head")[0].text
            print("-- {} --".format(pos_name))

            names = position.find_elements_by_css_selector('li')
            for name_wrapper in names:
                name = name_wrapper.find_element_by_css_selector('a').text
                status = name_wrapper.find_elements_by_css_selector('.depth-charts__inj')
                if len(status) > 0:
                    print("{} - {}".format(name, status[0].text))
                else:
                    print(name)

            import pdb; pdb.set_trace()

        # team.select('.depth-charts__pos')


    import pdb; pdb.set_trace()
    pass

# scrape_depth_chart()
# scrape_lineups()

# to_print = "["
# for team in all_teams:
#     to_print += "'{}',".format(team)

# to_print += "]"
# print(to_print)

# which teams are missing staters that played the last game
# how much money is missing
# How to read GTD?