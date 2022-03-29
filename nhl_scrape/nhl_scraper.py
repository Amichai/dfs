
from os import path
import time
import sys
from pathlib import Path
import datetime
from turtle import pd

from caesers_nhl_scraper import query_betCaesars
from nhl_optimizer import optimize

from selenium import webdriver

def log(to_log, output_file):
    print(to_log)
    output_file.write(to_log + "\n")
    output_file.flush()

def normalize_name(name):
    name = name.replace("  ", " ")
    name = name.replace("’", "'")
    name = name.replace(".", "")
    parts = name.split(" ")

    if len(parts) > 2:
        return "{} {}".format(parts[0], parts[1]).strip()

    return name.strip()

def log_line(output_file, *params):
    as_arr = [time_str()]
    as_arr += params
    try:
        to_write = "|".join(as_arr)
        log(to_write, output_file)
        return to_write
    except:
        print(as_arr)
        import pdb; pdb.set_trace()
        return ""

def time_str():
    return str(datetime.datetime.now()).split('.')[0]

def get_fd_slate_players(fd_slate_file_name, exclude_injured_players=True):
    all_players = {}
    salaries = open(fd_slate_file_name)
    lines = salaries.readlines()
    found_count = 0

    for line in lines[1:]:
        parts = line.split(',')
        full_name = normalize_name(parts[3])

        positions = parts[1]
        salary = parts[7]
        team = parts[9]
        status = parts[11]
        # print(full_name)
        if status == "O" and exclude_injured_players:
            continue
        name = full_name
        all_players[name] = [name, positions, float(salary), team, status]
        
    return all_players

def get_player_prices(fd_slate_file):
    fd_players = get_fd_slate_players(fd_slate_file, False)
    
    return fd_players


def get_projections(site, driver):
    if site == "Caesars":
        return query_betCaesars(driver)
    

def get_player_team(player, player_to_team):
    if "-" in player:
        parts = player.split('-')
        if len(parts) == 2 and len(parts[1]) == 3:
            return parts[1]
    player_normalized = normalize_name(player)
    if player_normalized in player_to_team:
        return player_to_team[player_normalized]
    return ''


def print_projections(site, name, team, projections, output_file, fd_players):
    all_rows = []
    
    records_to_write = {}
    for stat_key, line_score in projections.items():
        all_rows.append((stat_key, line_score))
        log_line(output_file, site, name, team, stat_key, line_score)
        records_to_write["{}|{}|{}|{}".format(site, name, team, stat_key)] = line_score

    return records_to_write


def diff_projections(site, new_p, old_p, output_file, player_to_team, fd_players):
    new_players = new_p.keys()
    old_players = old_p.keys()

    for player in old_players:
        team = get_player_team(player, player_to_team)
        if not player in new_players:
            stats = old_p[player]
            for stat_key in stats.keys():
                log_line(output_file, site, player, team, stat_key, "REMOVED")

    for player in new_players:
        team = get_player_team(player, player_to_team)
        if not player in old_players:
            print_projections(site, player, team, new_p[player], output_file, fd_players)

        else:
            stats_new = new_p[player]

            if not player in old_p:
                continue
            stats_old = old_p[player]

            stats_new_keys = stats_new.keys()
            stats_old_keys = stats_old.keys()

            for stat_key in stats_old_keys:
                if not stat_key in stats_new_keys:
                    log_line(output_file, site, player, team, stat_key, "REMOVED")

            for stat_key in stats_new_keys:
                if not stat_key in stats_old_keys:
                    log_line(output_file, site, player, team, stat_key, stats_new[stat_key])
                else:
                    old_val = stats_old[stat_key]
                    new_val = stats_new[stat_key]
                    if old_val.strip() != new_val.strip():
                        try:
                            diff = round(float(new_val) - float(old_val), 2)
                            log_line(output_file, site, player, team, stat_key, new_val, "(diff: {})".format(diff))
                        except:
                            log_line(output_file, site, player, team, stat_key, new_val, "(old_val: {})".format(old_val))


def get_MLE_projections(sites):
    # {'Assists': '0.3585409252669039', 'Shots': '1.5457559681697612', 'Plus/Minus': '0.4270334928229665', 'Points': '0.44211822660098526'}
    mle_projections = {}
    goalie_projections = {}
    caesars = sites["Caesars"]
    for player, stats in caesars.items():
        stat_keys = stats.keys()
        if "Saves" in stat_keys:
            goalie_projections[player] = float(stats["Saves"]) * 0.8
            continue
        if not "Assists" in stat_keys or not "Shots" in stat_keys or not "Points" in stat_keys:
            continue

        assists = float(stats["Assists"])
        pts = float(stats["Points"])
        goals = pts - assists
        shots = float(stats["Shots"])

        fd_projection = assists * 8 + goals * 12 + shots * 1.6
        mle_projections[player] = fd_projection
        
    return (mle_projections, goalie_projections)


if __name__ == "__main__":
    # folder = "/Users/amichailevy/Downloads/spike_data/player_lists/"
    folder = "/Users/amichailevy/Downloads/player_lists/"

    #TODO 1- 2/20/21
    #specific slate
    fd_slate_file = folder + "FanDuel-NHL-2022 ET-03 ET-01 ET-72276-players-list.csv"
    
    # #master file
    # fd_slate_file = folder + "FanDuel-NHL-2022 ET-02 ET-27 ET-72151-players-list.csv"
    
    fd_players = get_player_prices(fd_slate_file)
    current_date = datetime.datetime.now()
    output_file_name = "scraper_logs/money_line_scrape_{}_{}_{}.txt".format(current_date.month, current_date.day, current_date.year)

    all_sites = ["Caesars"]
    sites = {}

    if not path.exists(output_file_name):
        output_file = open(output_file_name, "a")
    else:
        output_file = open(output_file_name, "r+")


    lines = output_file.readlines()
    for line in lines:
        parts = line.split("|")
        if len(parts) < 4:
            continue
        site = parts[1]
        if not site in sites:
            sites[site] = {}

        player_name = parts[2]
        if not player_name in sites[site]:
            sites[site][player_name] = {}
        val = parts[5].strip()
        if val == "REMOVED":
            if stat in sites[site][player_name]:
                del sites[site][player_name][stat]
            continue
        stat = parts[4]
        sites[site][player_name][stat] = str(val)

    period = 35
    driver = webdriver.Chrome("../master_scrape_process/chromedriver6")
    log("starting up! PERIOD: {}".format(period), output_file)


    player_to_team = {}
    for player, player_info in fd_players.items():
        player_to_team[player] = player_info[3]

    # __import__('pdb').set_trace()

    while True:
        for site in all_sites:
            
            # print("Name to status: {}".format(name_to_status))
            
            log("{} - scraping {}".format(time_str(), site), output_file)
            new_projections = get_projections(site, driver)
            if not site in sites:
                sites[site] = {}
            diff_projections(site, new_projections, sites[site], output_file, player_to_team, fd_players)
            
            sites[site] = new_projections

            # name_projection = []
            # for name, projection in mle_projections.items():
            #     name_projection.append((name, projection))

            # name_projection_sorted = sorted(name_projection, key=lambda a: a[1], reverse=True)
            # print(name_projection_sorted)

            





            time.sleep(period)