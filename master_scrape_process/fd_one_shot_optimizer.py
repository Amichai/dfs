# -*- coding: UTF-8 -*-
from difflib import IS_LINE_JUNK
from io import DEFAULT_BUFFER_SIZE
from os import stat
import json
import time
from pkg_resources import FileMetadata
import requests
import sys
import datetime
from tabulate import tabulate
import pandas as pd
from yahoo_optimizer import random_optimizer
import fd_optimizer
import sd_salary_cap_optimizer
import dk_random_optimizer

import scrapers.caesars_scraper
from selenium import webdriver

from pathlib import Path

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

# Additionally remove the current file's directory from sys.path
try:
    sys.path.remove(str(parent))
except ValueError: # Already removed
    pass

from roto_wire_overlay_optimizer import roto_wire_scrape

# import optimizer_player_pool

if __name__ == "__main__":
    folder = "/Users/amichailevy/Downloads/player_lists/"
    # (start_time_to_teams, fd_slate_file, dk_slate_file) = optimizer_player_pool.load_start_times_and_slate_path("start_times2.txt")
    # fd_slate_file = folder + fd_slate_file


    driver = webdriver.Chrome("../master_scrape_process/chromedriver7")
    scrapers.caesars_scraper.query_betCaesars(driver)
    __import__('pdb').set_trace()
    pass