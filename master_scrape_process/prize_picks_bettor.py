from selenium import webdriver
import time


LONG_SLEEP = 0.9
SHORT_SLEEP = 0.1


def login(driver):
    url = "https://prizepicks.com/"
    driver.get(url)
    time.sleep(LONG_SLEEP)
    element = driver.find_element_by_css_selector('nav > a.nav-link-2')
    element.click()
    time.sleep(LONG_SLEEP)
    email_input = driver.find_element_by_css_selector('input#email-input')
    email_input.send_keys("amichaimlevy@gmail.com")

    password_input = driver.find_element_by_css_selector('input#password-input-field')
    password_input.send_keys("love4cgP1")
    password_input.submit()
    time.sleep(LONG_SLEEP)
    url = "https://app.prizepicks.com/"
    driver.get(url)
    time.sleep(LONG_SLEEP)


def main(driver, bets_to_take, bet_size=5):
    url = "https://app.prizepicks.com/"
    driver.get(url)
    time.sleep(LONG_SLEEP)

    for bet in bets_to_take:
        assert bet[1] == 'over' or bet[1] == "under"

    league_options = driver.find_elements_by_css_selector('div.league')
    for option in league_options:
        if option.text == "NBA":
            option.click()
            break

    time.sleep(SHORT_SLEEP)


    stat_options = driver.find_elements_by_css_selector('div.stat')
    for option in stat_options:
        if option.text == "Fantasy Score":
            option.click()
            break
    
    time.sleep(SHORT_SLEEP)

    players_to_select = [a[0] for a in bets_to_take]
    for to_select in players_to_select:

        all_players = driver.find_elements_by_css_selector('div.player')
        for player in all_players:
            if player.find_element_by_css_selector('div.name').text == to_select:
                player.click()
                break


    time.sleep(SHORT_SLEEP)

    entry_predictions = driver.find_elements_by_css_selector('div.entry-predictions > div.entry-prediction')
    for entry_prediction in entry_predictions:
        name = entry_prediction.find_element_by_css_selector('div.player > div.name').text
        projected_score = entry_prediction.find_element_by_css_selector('div.projected-score div.score').text

        for pl_bet in bets_to_take:
            bet_name = pl_bet[0]
            if bet_name == name:
                if pl_bet[1] == "over":
                    entry_prediction.find_element_by_css_selector('div.over-under > div.over').click()
                    break
                elif pl_bet[1] == "under":
                    entry_prediction.find_element_by_css_selector('div.over-under > div.under').click()
                    break

            print("{} {} - {}".format(name, pl_bet[1], projected_score))


    time.sleep(SHORT_SLEEP * 6)

    game_types = driver.find_elements_by_css_selector('div.game-types-container > div.game-type-card')
    for game_type in game_types:
        if "Power Play" in game_type.text:
            game_type.click()
            break

    time.sleep(SHORT_SLEEP)
    
    amt_input = driver.find_element_by_css_selector('div.entry-input-container > div.entry-input div.input-value-container > input')

    time.sleep(LONG_SLEEP)

    amt_input.clear()
    amt_input.send_keys(bet_size)
    
    time.sleep(SHORT_SLEEP)

    place_entry_btn = driver.find_element_by_css_selector('div.place-entry-button-container > button.primary')
    place_entry_btn.click()


    # navigate to the PP home page
    # find the two players, etc.
    pass


def file_watcher(driver):
    parsed_line_key = "------\n"
    while True:
        with open("bets_to_place.txt", "r+") as f:
            lines = f.readlines()
            not_parsed = []
            for line in lines:
                if line == parsed_line_key:
                    not_parsed = []
                else:
                    not_parsed.append(line)

            bet_size = 1
            if len(not_parsed) > 0:
                for line2 in not_parsed:
                    print(line2)
                    bet_parts = line2.split("|")
                    all_bets = []
                    for bet_part in bet_parts:
                        bet_part = bet_part.strip()
                        parts = bet_part.split(',')
                        if len(parts) == 1:
                            bet_size = float(parts[0].strip())
                            continue


                        name = parts[0].strip()
                        over_under = parts[1].strip()
                        if over_under == "o":
                            over_under = "over"
                        elif over_under == "u":
                            over_under = "under"
                        else:
                            print("Falied to parse: {}".format(line))
                        all_bets.append((name, over_under))

                    try:
                        main(driver, all_bets, bet_size)
                        print("SUCCESSFULLY PLACED BET: {}".format(all_bets))
                    except:
                        print("Failed to place BET: {}".format(all_bets))

                f.write("\n------\n")
        
        time.sleep(3)



if __name__ == "__main__":
    driver = webdriver.Chrome("../master_scrape_process/chromedriver")
    # main(driver, [
    #     ("Kyle Lowry", 'over'), 
    #     ("Jaren Jackson Jr.", 'under')]
    #     , 1)

    login(driver)
    file_watcher(driver)