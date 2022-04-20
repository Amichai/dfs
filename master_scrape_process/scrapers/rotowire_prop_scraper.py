
from selenium import webdriver

import time

def scroll_page(driver):
    time.sleep(1)

    short_sleep = 0.5
    for i in range(3):


        driver.execute_script("window.scrollTo(0, 0);")

        time.sleep(short_sleep)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 4.0);")

        time.sleep(short_sleep)


        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 3.0);")

        time.sleep(short_sleep)


        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2.0);")

        time.sleep(short_sleep)


        driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 3 / 4.0);")

        time.sleep(short_sleep)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(short_sleep)


def scrape_page(driver):
    table_ids = ["props-pts", "props-reb", "props-ast", "props-threes", "props-blk", "props-stl"]
    for table_id in table_ids:
        table = driver.find_element_by_id(table_id)
        __import__('pdb').set_trace()




if __name__ == "__main__":
    driver = webdriver.Chrome("../../master_scrape_process/chromedriver8")

    url = "https://www.rotowire.com/betting/nba/player-props.php"
    driver.get(url)

    scroll_page(driver)
    scrape_page(driver)
