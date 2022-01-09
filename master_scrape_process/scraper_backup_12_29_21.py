from os import path, write
import fd_optimizer
import pandas as pd
import time
import datetime
from requests.api import head
from tabulate import tabulate
import json
import requests
from selenium import webdriver
from scrapers.stat_hero_scrape import sh_query_prices
from scrapers.underdog_scrape import underdog_query_line
from scrapers.pp_nfl_scraper import nfl_pp_projections
from scrapers.dk_scrape import query_dk
from scrape_MKF import query_mkf_lines
from scrapers.hot_streak_scraper import query_hot_streak
from scrapers.awesome_scraper import query_awsemo
import scrapers.awsemo_NFL_scraper
import scrapers.betMGM_scrape
import scrapers.caesars_scraper
import scrapers.thrive_fantasy_scraper
import optimizer_player_pool
import uuid

from decimal import Decimal

access_key = "AKIAUA5DAUAXH2CQZ6YG"
secret_key = "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"

import boto3


import os
from twilio.rest import Client
# Find these values at https://twilio.com/user/account
# To set up environmental variables, see http://twil.io/secure
account_sid = "ACac202cee74dea922326b84721022a640"
auth_token = "5d5de5e0dab352d1d61a458ddeb8ec52"

client = Client(account_sid, auth_token)

session = boto3.Session(
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )

aws_timestream_client = session.client('timestream-write', region_name='us-east-1')


import sys
from pathlib import Path # if you haven't already done so
file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

# Additionally remove the current file's directory from sys.path
try:
    sys.path.remove(str(parent))
except ValueError: # Already removed
    pass

from roto_wire_overlay_optimizer.roto_wire_scrape import scrape_lineups

class DataTable:
    """Current state data storage"""
    def __init__(self, rows, headers):
        self.rows = rows
        self.headers = headers
        
        
    @staticmethod
    def diff(old_table, new_table, columns_to_not_diff=[], primary_key_idx=0, upload_row_to_dynamo=None):
        headers1 = old_table.headers
        headers2 = new_table.headers
        if headers1 == None:
            headers1 = headers2
            old_table.rows = []

        assert len(headers1) == len(headers2)
        for i in range(len(headers1)):
            assert headers1[i] == headers2[i]

        row_to_col_diff = {}
        idx = -1
        for row1 in new_table.rows:
            idx += 1
            row1_parts = [str(a) for a in row1]
            matched = False
            
            as_str = ",".join(row1_parts)
            for row2 in old_table.rows:
                row2_parts = [str(a) for a in row2]
                different_value_columns = {}
                if row1_parts[primary_key_idx] == row2_parts[primary_key_idx]:
                    for col_idx in range(len(row1_parts)):
                        if col_idx in columns_to_not_diff:
                            continue
                        if row1_parts[col_idx] != row2_parts[col_idx]:
                            different_value_columns[col_idx] = row2_parts[col_idx]



                if len(different_value_columns) > 0:
                    row_to_col_diff[idx] = different_value_columns


                as_str2 = ",".join(row2_parts)
                if as_str == as_str2:
                    matched = True
                    if idx in row_to_col_diff:
                        del row_to_col_diff[idx]
                    break

            if not matched and not idx in row_to_col_diff:
                row_to_col_diff[idx] = {0:''}


        
        if len(row_to_col_diff.keys()) > 0:
            rows_to_print = []
            for row in new_table.rows:
                rows_to_print.append(list(row))
            for row_idx, col_indices in row_to_col_diff.items():
                for col, old_val in col_indices.items():
                    rows_to_print[row_idx][col] = "{}({})".format(rows_to_print[row_idx][col], old_val)

                    if upload_row_to_dynamo != None:
                        upload_row_to_dynamo(rows_to_print[row_idx])

            as_str = tabulate(rows_to_print, new_table.headers)
            
            print(as_str)
            return as_str

        return None


def current_milli_time():
    return round(time.time() * 1000)

def create_money_line_movement_record(site, player, team, stat, new_val, old_val, diff):

    def convert_site_name(site_name):
        site_name_conversion = {"DK": "DraftKings", "MLE-Projected": "Money Line Edge"}
        if site_name in site_name_conversion:
            return site_name_conversion[site_name]

        return site_name


    def convert_stat_name(stat_name):
        site_name_conversion = {
        "assists": "Assists", "blocks": "Blocks", "points": "Points", "rebounds": "Rebounds", "steals": "Steals",

        "points + assists": "Points + Assists",
        "points + rebounds": "Points + Rebounds",
        "steals + blocks": "Steals + Blocks",
        "rebounds + assists": "Rebounds + Assists",
        "three-pointers": "Three-Pointers",


        
        "pts_rebs_asts": "Points + Rebounds + Assists",
        "pts_rebs": "Points + Rebounds",
        
        }
        if stat_name in site_name_conversion:
            return site_name_conversion[stat_name]

        return stat_name

    current_time = str(current_milli_time())
    site = convert_site_name(site)
    stat = convert_stat_name(stat)
    site_stat = "{} - {}".format(site, stat)

    dimensions = [
        # {'Name': 'Site', 'Value': site},
        {'Name': 'Name', 'Value': player},
        {'Name': 'Team', 'Value': team},
        {'Name': 'Stat', 'Value': site_stat},
        {'Name': 'Last Value', 'Value': old_val},
        {'Name': 'New Value', 'Value': new_val},
    ]

    record = {
        'Dimensions': dimensions,
        'MeasureName': "Difference",
        'MeasureValue': str(diff),
        'MeasureValueType': "DOUBLE",
        'Time': current_time
    }

    return record

def create_record(player, team, status, projected_value, fd_price, dk_price, yahoo_price, fd_value, dk_value, yahoo_value, prize_picks_projection, new_min, new_max):
    current_time = str(current_milli_time())
    if team == '':
        print("TEAM UNKNOWN: {} {}".format(player, projected_value))
        team = "-"
    if player == '' or projected_value == '':
        print("ERROR: CANNOT CREATE RECORD FOR: {} {} {}".format(player, team, projected_value))


    dimensions = [
        {'Name': 'Name', 'Value': player},
        {'Name': 'Team', 'Value': team},
        {'Name': 'Status', 'Value': status},
        {'Name': 'FanDuel Price', 'Value': fd_price},
        {'Name': 'DraftKings Price', 'Value': dk_price},
        # {'Name': 'Yahoo Price', 'Value': yahoo_price},
        {'Name': 'FanDuel Projected Value', 'Value': fd_value},
        {'Name': 'DraftKings Projected Value', 'Value': dk_value},
        # {'Name': 'Yahoo Projected Value', 'Value': yahoo_value},
        {'Name': 'PrizePicks Fantasy Score', 'Value': prize_picks_projection},
        {'Name': "Today's Projection Max", 'Value': new_max},
        {'Name': "Today's Projection Min", 'Value': new_min},

    ]

    record = {
        'Dimensions': dimensions,
        'MeasureName': "Projected Fantasy Score",
        'MeasureValue': str(projected_value),
        'MeasureValueType': "DOUBLE",
        'Time': current_time
    }

    return record


def diff_money_lines(sites, all_money_lines_remote_state, player_to_team, fd_players):
    # site, player, stat, value
    all_records_to_write = []
    all_money_lines_new = {}
    sites_to_inspect = ["Caesars", "betMGM", "DK", "TF", "MLE-Projected", "Underdog"]
    for site, player_stats in sites.items():
        if site not in sites_to_inspect:
            continue

        if not site in all_money_lines_new:
            all_money_lines_new[site] = {}

        for player, stats in player_stats.items():
            if not player in all_money_lines_new[site]:
                all_money_lines_new[site][player] = {}

            for stat, new_value in stats.items():
                old_val = query_dict(all_money_lines_remote_state, site, player, stat)
                team = get_player_team(player, player_to_team)
       
                if team == '':
                    continue
                if old_val != None:
                    #diff = round(float(new_val) - float(old_val), 2)
                    diff = round(float(new_value) - float(old_val), 2)

                    if abs(diff) >= 0.6:
                        new_record = create_money_line_movement_record(site, player, team, stat, str(new_value), str(old_val), str(diff))
                        all_records_to_write.append(new_record)
                        pass
                    pass
                else:
                    # new_record = create_money_line_movement_record(site, player, team, stat, "-", str(new_value), str(0.0))
                    # all_records_to_write.append(new_record)
                    pass

                all_money_lines_new[site][player][stat] = new_value
    
    if len(all_records_to_write) > 0:
        print("Writing {} diff records".format(len(all_records_to_write)))
        write_records(all_records_to_write, "ProjectionMovementLog")
    return all_money_lines_new

def write_to_timeseries(sites, timeseries_remote_state, player_to_team, dk_players, fd_players):

    new_timeseries_remote_state = {}
    all_records_to_write = []
    # site, player, stat, value
    for site, player_stats in sites.items():
        if site != "MLE-Projected":
            continue

        for player, stats in player_stats.items():
            team = get_player_team(player, player_to_team)
            for stat, projected_value in stats.items():
                prize_picks_projection = query_dict(sites, "PP", player, "Fantasy Score")
                if prize_picks_projection == None:
                    prize_picks_projection = "-"
                
                if projected_value == "REMOVED":
                    continue

                projected_value = float(projected_value)
                fd_price = "-"
                fd_value = "-"
                if player in fd_players:
                    fd_price = fd_players[player][2]
                    fd_value = round(projected_value / (fd_price / 1000), 2)


                dk_price = "-"
                dk_value = "-"
                if player in dk_players:
                    dk_price = dk_players[player][2]
                    dk_value = round(projected_value / (dk_price / 1000), 2)


                yahoo_price = "-"
                yahoo_value = "-"

                # if player in yahoo_players:
                #     yahoo_price = yahoo_players[player][2]
                #     yahoo_value = round(projected_value / yahoo_price, 2)


                # projected_value = round(float(projected_value), 2)
        
                # to_upload = {
                #     "Name": player,
                #     "Team": team,
                #     "Projected Value": projected_value,
                #     "FanDuel Price": fd_price,
                #     "DraftKings Price": dk_price,
                #     "Yahoo Price": yahoo_price,
                #     "FanDuel Value": fd_value,
                #     "DraftKings Value": dk_value,
                #     "Yahoo Value": yahoo_value,
                #     "Prize Picks Fantasy Point Line": prize_picks_projection,
                #     "Daily Min Projection": 0,
                #     "Daily Max Projection": 0,
                #     }

                old_value = None
                if player in timeseries_remote_state:
                    old_value = timeseries_remote_state[player]


                status  = ' '
                if player in fd_players:
                    status = fd_players[player][4]

                if status == '':
                    status = ' '

                to_upload = [player, team, projected_value, fd_price, dk_price, yahoo_price, fd_value, dk_value, yahoo_value, prize_picks_projection, 0,0, status]

                new_min = projected_value
                new_max = projected_value

                to_upload[10] = new_min
                to_upload[11] = new_max

                if old_value != None:
                    assert len(old_value) == len(to_upload)

                    is_same = True
                    for i in range(len(old_value)):
                        if i == 10 or i == 11:
                            continue # don't compare daily min max vals
                        if old_value[i] != to_upload[i]:
                            print(old_value)
                            print(to_upload)
                            is_same = False
                            break


                    if is_same:
                        new_timeseries_remote_state[player] = to_upload
                        continue


                    # if we got here then the record is different
                    new_min = old_value[10]
                    new_max = old_value[11]
                    if new_min != new_max:
                        __import__('pdb').set_trace()


                    if projected_value > new_max:
                        new_max = projected_value

                    if projected_value < new_min:
                        new_min = projected_value

                #update min max value, upload row!
                new_record = create_record(player, team, status, str(projected_value), str(fd_price), str(dk_price), str(yahoo_price), str(fd_value), str(dk_value), str(yahoo_value), str(prize_picks_projection), str(new_min), str(new_max))

                old_projection = ''
                if old_value != None:
                    old_projection = old_value[2]
                # # print("{} - old: {} - new: {}".format(player, old_projection, projected_value))

                all_records_to_write.append(new_record)

                new_timeseries_remote_state[player] = [player, team, projected_value, fd_price, dk_price, yahoo_price, fd_value, dk_value, yahoo_value, prize_picks_projection, new_min, new_max, status]
    
    # if len(all_records_to_write) > 0:
    #     print(len(all_records_to_write))
    #     __import__('pdb').set_trace()

    write_records(all_records_to_write, "PlayerProjections")

    return new_timeseries_remote_state
    # player projections - all players
    # name, team, projected fp, fd price, yahoo price, fd value, yahoo value, prize picks fp projection, prize picks projection diff, [dk price, dk value], min fp projection, max fp projection, last fp performance, last update

    # big movers log
    # name, time, team, stat, site, new stat val, difference
    # lines that have been taken down?
    # this should probably happen in the actual stat diff function


    # other potential options - player-pool/team coverage
    #     open arbitrage

def write_records(records_to_write, table_name):
    start_idx = 0
    while True:
        if start_idx >= len(records_to_write):
            break
        to_write = records_to_write[start_idx:start_idx + 100]
        _write_records(to_write, table_name)
        start_idx += 100


def _write_records(to_write, table_name):
    if len(to_write) == 0:
        return

    print("WRITE RECORDS: {}".format(len(to_write)))
    DATABASE_NAME = "MoneyLineEdge"

    try:
        result = aws_timestream_client.write_records(DatabaseName=DATABASE_NAME, TableName=table_name,
                                            Records=to_write, CommonAttributes={})
        print("WriteRecords Status: [%s]" % result['ResponseMetadata']['HTTPStatusCode'])
    except aws_timestream_client.exceptions.RejectedRecordsException as err:
        print("RejectedRecords: ", err)
        for rr in err.response["RejectedRecords"]:
            print("Rejected Index " + str(rr["RecordIndex"]) + ": " + rr["Reason"])
        print("Other records were written successfully. ")
    except Exception as err:
        print("Error:", err)
    pass


projection_table = None
write_count = 0

arbitrage_table = None

def write_arbitrage(site, player, team, stat_key, value, site_names, site_values, diff):
    assert len(site_names) == len(site_values)

    global arbitrage_table, write_count
    if arbitrage_table == None:
        dynamodb = boto3.resource('dynamodb')
        arbitrage_table = dynamodb.Table('SiteToSiteArbitrage')
    
    timestamp = str(datetime.datetime.now())
    date = timestamp.split(' ')[0]

    
    to_write = {
        'Date': date,
        'Site-Stat-Player': '{}-{}-{}'.format(site, stat_key, player),
        'timestamp': timestamp,
        'site': site,
        'value': round(value, 2),
        'player': player,
        'team': team,
        'stat': stat_key,
        'diff': round(diff, 2),
        'absolute_diff': abs(round(diff, 2))
    }

    for i in range(len(site_names)):
        site_name = site_names[i]
        site_value = round(site_values[i], 2)

        to_write[site_name] = site_value


    to_write = json.loads(json.dumps(to_write), parse_float=Decimal)

    try:
        result = arbitrage_table.put_item(
            Item=to_write
            )

        write_count += 1
    except Exception as err:
        print("Error:", err)

    if write_count % 10 == 0:
        print("WRITING: {} - {}\n{}".format(write_count, to_write, result))

def write_projection(site, player, team, stat_key, value):
    return
    if value == "REMOVED":
        return

    global projection_table, write_count
    if projection_table == None:
        dynamodb = boto3.resource('dynamodb')
        projection_table = dynamodb.Table('PrizePicksValue')


    timestamp = str(datetime.datetime.now())
    date = timestamp.split(' ')[0]
    
    to_write = {
        'Date': date,
        'Site-Stat-Name': '{}-{}-{}'.format(site, stat_key, player),
        'timestamp': timestamp,
        'site': site,
        'player': player,
        'team': team,
        'stat': stat_key,
        'value': value
    }

    try:
        result = projection_table.put_item(
            Item=to_write
            )

        write_count += 1
    except Exception as err:
        print("Error:", err)

    if write_count % 100 == 0:
        print("{} - {}\n{}".format(write_count, to_write, result))


last_value_before_remove = {}

def log(to_log, output_file):
    print(to_log)
    output_file.write(to_log + "\n")
    output_file.flush()


def get_PP_projections(driver):
    
    url = 'https://api.prizepicks.com/projections?league_id=7&per_page=500&single_stat=false'
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
        player_name = optimizer_player_pool.normalize_name(player_name)
        # team = attr['team']
        
        player_id = player['id']
        player_ids.append(player_id)
        id_to_name[player_id] = player_name

    name_to_projections = {}

    stats_from_promotions = []

    for projection in data:
        attr = projection['attributes']
        stat_type = attr['stat_type']
        created_at = attr["created_at"]
        updated_at = attr["updated_at"]
        line_score = attr["line_score"]
        projection_type = attr["projection_type"]
        player_id = projection['relationships']['new_player']['data']['id']
        player_name = id_to_name[player_id]
        promotion_stat_key = "{}-{}".format(stat_type, player_name)
        if promotion_stat_key in stats_from_promotions:
            continue

        # flash_sale_line_score = attr['flash_sale_line_score']
        # if flash_sale_line_score != '' and flash_sale_line_score != None:
        #     line_score = flash_sale_line_score
        #     stats_from_promotions.append(promotion_stat_key)
        
        if not player_name in name_to_projections:
            name_to_projections[player_name] = {}

        name_to_projections[player_name][stat_type] = line_score
        
    return name_to_projections

def print_projections(site, name, team, projections, output_file):
    all_rows = []
    
    records_to_write = {}
    for stat_key, line_score in projections.items():
        all_rows.append((stat_key, line_score))
        log_line(output_file, site, name, team, stat_key, line_score)
        write_projection(site, name, team, stat_key, line_score)

        records_to_write["{}|{}|{}|{}".format(site, name, team, stat_key)] = line_score

    return records_to_write

def save_last_value_before_remove(site, player, stats):
    if not site in last_value_before_remove:
        last_value_before_remove[site] = {}

    if not player in last_value_before_remove[site]:
        last_value_before_remove[site][player] = stats

def query_last_value_before_remove(site, player, stat):
    if site in last_value_before_remove and player in last_value_before_remove[site] and stat in last_value_before_remove[site][player]:
        return last_value_before_remove[site][player][stat]

    return ''


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

missing_player_lookup = {}

def get_player_team(player, player_to_team):
    if "-" in player:
        parts = player.split('-')
        if len(parts) == 2 and len(parts[1]) == 3:
            return parts[1]
    player_normalized = optimizer_player_pool.normalize_name(player)
    if player_normalized in player_to_team:
        return player_to_team[player_normalized]

    if player_normalized in missing_player_lookup:
        return missing_player_lookup[player_normalized]
    return ''



def diff_projections(site, new_p, old_p, output_file, player_to_team):
    new_players = new_p.keys()
    old_players = old_p.keys()

    for player in old_players:
        team = get_player_team(player, player_to_team)
        if not player in new_players:
            stats = old_p[player]
            save_last_value_before_remove(site, player, stats)
            for stat_key in stats.keys():
                log_line(output_file, site, player, team, stat_key, "REMOVED")
                write_projection(site, player, team, stat_key, "REMOVED")

    for player in new_players:
        team = get_player_team(player, player_to_team)
        if not player in old_players:
            print_projections(site, player, team, new_p[player], output_file)

        else:
            stats_new = new_p[player]

            if not player in old_p:
                continue
            stats_old = old_p[player]

            stats_new_keys = stats_new.keys()
            stats_old_keys = stats_old.keys()

            save_last_value_before_remove(site, player, stats_old)

            for stat_key in stats_old_keys:
                if not stat_key in stats_new_keys:
                    log_line(output_file, site, player, team, stat_key, "REMOVED")
                    write_projection(site, player, team, stat_key, "REMOVED")

            for stat_key in stats_new_keys:
                if not stat_key in stats_old_keys:
                    last_val_before_remove = query_last_value_before_remove(site, player, stat_key)
                    write_projection(site, player, team, stat_key, stats_new[stat_key])
                    if last_val_before_remove != '':
                        log_line(output_file, site, player, team, stat_key, stats_new[stat_key], "(cached: {})".format(last_val_before_remove))
                    else:
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
                        finally:
                            write_projection(site, player, team, stat_key, new_val)

def get_projections(site, driver):
    if site == "PP":
        return get_PP_projections(driver)
    elif site == "StatHero":
        return sh_query_prices()
    elif site == "RW":
        (_, _, _, rw_info) = scrape_lineups()
        return rw_info
    elif site == "Underdog":
        return underdog_query_line()
    elif site == "MKF":
        return query_mkf_lines()
    elif site == "PP-NFL":
        return nfl_pp_projections(driver)
    elif site == "Underdog-NFL":
        return underdog_query_line(is_NFL=True)
    elif site == "HotStreak":
        return query_hot_streak()
    elif site == "DK":
        return query_dk()
    elif site == "Awesemo":
        return query_awsemo()
    elif site == "Awesemo-NFL":
        return scrapers.awsemo_NFL_scraper.query_awsemo()
    elif site == "betMGM":
        return scrapers.betMGM_scrape.query_betMGM(driver)
    elif site == "Caesars":
        return scrapers.caesars_scraper.query_betCaesars(driver)
    elif site == "TF":
        return scrapers.thrive_fantasy_scraper.query_TF()



def get_player_to_team():
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)

    abbr_file = open("team_names.txt")
    lines = abbr_file.readlines()
    team_abbr_dict = {}
    team_abbr_dict2 = {}
    for line in lines:
        parts = line.split(',')
        abbr_name = parts[1].strip()
        team_abbr_dict[parts[1].strip()] = parts[0]
        team_abbr_dict2[parts[0]] = parts[1].strip()


    # filename = "~/Downloads/season_data/{}-{}-{}-nba-season-dfs-feed.xlsx".format(12, 16, 2021)

    filename = "~/Downloads/season_data/{}-{}-{}-nba-season-dfs-feed.xlsx".format(yesterday.month, str(yesterday.day).zfill(2), yesterday.year)

    dfs = pd.read_excel(filename, sheet_name=None)
    if 'NBA-DFS-SEASON-FEED' in dfs:
        feed = dfs['NBA-DFS-SEASON-FEED']
    else:
        feed = dfs['NBA-DFS-SEASON']
    all_columns = feed.keys()

    team_to_date_to_rows = {}

    player_to_team = {}

    column_to_column_key = {
        "date": "Unnamed: 2",
        "name": "Unnamed: 4",
        "team": "Unnamed: 5",
        "opp": "Unnamed: 6",
        "starter": "Unnamed: 7",
        "minutes": "Unnamed: 9",
        "rest": "Unnamed: 11",
        "positions": "Unnamed: 13",
        "salary": "Unnamed: 16",
        "fdp": "Unnamed: 19",
        }

    for index, row in feed.iterrows():
        if row['GAME INFORMATION'] != "NBA 2021-2022 Regular Season":
            continue

        name = optimizer_player_pool.normalize_name(row["Unnamed: 4"])
        team = row["Unnamed: 5"]

        team = team_abbr_dict2[team]

        player_to_team[name] = team
    return player_to_team
        

def time_str():
    return str(datetime.datetime.now()).split('.')[0]

def rows_to_str(rows):
    to_return = ""
    for row in rows:
        as_str = "|".join([str(a) for a in row])
        to_return += as_str + ","

    return to_return


def get_player_projections_dk(sites):
    # load up player stats
    #https://www.nba.com/stats/players/traditional/?PerMode=Totals&sort=PTS&dir=-1
    #https://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season=2021-22&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&TwoWay=0&VsConference=&VsDivision=&Weight=

    if not "DK" in sites:
        return {}

    name_to_ast_rbd_ratio = {}
    stats_file = open("player_stats.json")
    as_str = stats_file.read()
    for row in json.loads(as_str)['resultSets'][0]['rowSet']:
        name = row[1]
        name = optimizer_player_pool.normalize_name(name)

        rbds = row[22]
        assts = row[23]
        if rbds + assts > 0:
            name_to_ast_rbd_ratio[name] = rbds / (assts + rbds)

    player_to_fp = {}
    player_to_stat_to_value = {}



    for name, stats in sites["DK"].items():
        player_name = optimizer_player_pool.normalize_name(name)
        for stat, val in stats.items():
            if val == "REMOVED":
                continue
            try:
                value = float(val)
            except:
                continue
            if not player_name in player_to_stat_to_value:
                player_to_stat_to_value[player_name] = {}

            if not stat in player_to_stat_to_value[player_name]:
                player_to_stat_to_value[player_name][stat] = {}

            player_to_stat_to_value[player_name][stat] = value
        
        for player, stat_to_values in player_to_stat_to_value.items():
            if not player in name_to_ast_rbd_ratio:
                # print("DK PROJCETIONS MISSING: {}".format(player))
                continue
            rbds_to_assts_plus_rbds = name_to_ast_rbd_ratio[player]
            if not 'Points' in stat_to_values:
                continue
            
            pts = stat_to_values['Points']

            if not 'Points + Assists + Rebounds' in stat_to_values:
                continue

            PAR = stat_to_values['Points + Assists + Rebounds']
            AR = PAR - pts
            
            if not 'Steals + Blocks' in stat_to_values:
                continue

            SB = stat_to_values['Steals + Blocks']
            AR = PAR - pts
            factor = 1.2 * rbds_to_assts_plus_rbds + 1.5 * (1 - rbds_to_assts_plus_rbds)
            projected = pts + AR * factor + SB * 3

            player_to_fp[player] = projected

    return player_to_fp

def get_site_to_pt_rbd_ast_projections(sites, selected_sites):
    to_return = {}
    for site in selected_sites:
        to_return[site] = {}

    for site in sites.keys():
        if site not in selected_sites:
            continue
        if site == "Awesemo":
            for player, stats in sites[site].items():
                if "Points" in stats and "Assists" in stats and "Rebounds" in stats:
                    pts = float(stats["Points"])
                    asts = float(stats["Assists"])
                    rbds = float(stats["Rebounds"])
                    to_return[site][player] = pts + asts + rbds
        elif site == "DK":
            for player, stats in sites[site].items():
                if "Points + Assists + Rebounds" in stats:
                    to_return[site][player] = float(stats["Points + Assists + Rebounds"])
        elif site == "betMGM":
            for player, stats in sites[site].items():
                if "points" in stats and "points + assists" in stats and "points + rebounds" in stats:
                    pts = float(stats["points"])
                    pts_asts = float(stats["points + assists"])
                    pts_rbds = float(stats["points + rebounds"])
                    to_return[site][player] = pts_asts + pts_rbds - pts
        elif site == "PP":
            for player, stats in sites[site].items():
                if "Points" in stats and "Assists" in stats and "Rebounds" in stats:
                    pts = float(stats["Points"])
                    asts = float(stats["Assists"])
                    rbds = float(stats["Rebounds"])
                    to_return[site][player] = pts + asts + rbds
        elif site == "HotStreak":
            for player, stats in sites[site].items():
                if "points" in stats and "assists" in stats and "rebounds" in stats:
                    pts = float(stats["points"])
                    asts = float(stats["assists"])
                    rbds = float(stats["rebounds"])
                    to_return[site][player] = pts + asts + rbds
        elif site == "Underdog":
            for player, stats in sites[site].items():
                if "pts_rebs_asts" in stats:
                    to_return[site][player] = float(stats["pts_rebs_asts"])
        elif site == "Caesars":
            for player, stats in sites[site].items():
                if "Points + Assists + Rebounds" in stats:
                    to_return[site][player] = float(stats["Points + Assists + Rebounds"])

    return to_return




def get_player_projections_awesemo(sites):
    player_to_fp = {}
    player_to_stat_to_value = {}
    if not "Awesemo" in sites:
        return {}
    for name, stats in sites["Awesemo"].items():
        player_name = optimizer_player_pool.normalize_name(name).strip()
        for stat, val in stats.items():
            if val == "REMOVED":
                continue
            value = float(val)
            if not player_name in player_to_stat_to_value:
                player_to_stat_to_value[player_name] = {}

            if not stat in player_to_stat_to_value[player_name]:
                player_to_stat_to_value[player_name][stat] = {}

            player_to_stat_to_value[player_name][stat] = value
    
    for player, stat_to_values in player_to_stat_to_value.items():
        if not "Points" in stat_to_values:
            continue
        pts = stat_to_values['Points']
        if not 'Rebounds' in stat_to_values:
            continue
        rbds = stat_to_values['Rebounds']
        if not 'Assists' in stat_to_values:
            continue
        asts = stat_to_values['Assists']
        if not 'Blocks' in stat_to_values:
            continue
        blks = stat_to_values['Blocks']
        if not 'Steals' in stat_to_values:
            continue
        stls = stat_to_values['Steals']

        projected = pts + rbds * 1.2 + asts * 1.5 + blks * 3 + stls * 3
        player_to_fp[player] = projected

    return player_to_fp

def get_player_projections_Caesars(sites):
    player_to_fp = {}
    player_to_stat_to_value = {}
    if not "Caesars" in sites:
        return {}
    for name, stats in sites["Caesars"].items():
        player_name = optimizer_player_pool.normalize_name(name).strip()
        for stat, val in stats.items():
            if val == "REMOVED":
                continue
            value = float(val)
            if not player_name in player_to_stat_to_value:
                player_to_stat_to_value[player_name] = {}

            if not stat in player_to_stat_to_value[player_name]:
                player_to_stat_to_value[player_name][stat] = {}

            player_to_stat_to_value[player_name][stat] = value
    
    for player, stat_to_values in player_to_stat_to_value.items():
        if not "Points" in stat_to_values:
            continue
        pts = stat_to_values['Points']
        if not 'Rebounds' in stat_to_values:
            continue
        rbds = stat_to_values['Rebounds']
        if not 'Assists' in stat_to_values:
            continue
        asts = stat_to_values['Assists']
        if not 'Blocks' in stat_to_values:
            continue
        blks = stat_to_values['Blocks']
        if not 'Steals' in stat_to_values:
            continue
        stls = stat_to_values['Steals']
        turnovers = stat_to_values["Turnovers"]
        

        projected = pts + rbds * 1.2 + asts * 1.5 + blks * 3 + stls * 3 - turnovers
        player_to_fp[player] = projected
    
    return player_to_fp

def get_player_projections_betMGM(sites):
    player_to_fp = {}
    player_to_stat_to_value = {}
    if not "betMGM" in sites:
        return {}
    for name, stats in sites["betMGM"].items():
        player_name = optimizer_player_pool.normalize_name(name).strip()
        for stat, val in stats.items():
            if val == "REMOVED":
                continue
            value = float(val)
            if not player_name in player_to_stat_to_value:
                player_to_stat_to_value[player_name] = {}

            if not stat in player_to_stat_to_value[player_name]:
                player_to_stat_to_value[player_name][stat] = {}

            player_to_stat_to_value[player_name][stat] = value
    
    for player, stat_to_values in player_to_stat_to_value.items():
        if not "points" in stat_to_values:
            continue
        pts = stat_to_values['points']
        if not 'rebounds' in stat_to_values:
            continue
        rbds = stat_to_values['rebounds']
        if not 'assists' in stat_to_values:
            continue
        asts = stat_to_values['assists']
        if not 'blocks' in stat_to_values:
            continue
        blks = stat_to_values['blocks']
        if not 'steals' in stat_to_values:
            continue
        stls = stat_to_values['steals']

        projected = pts + rbds * 1.2 + asts * 1.5 + blks * 3 + stls * 3
        player_to_fp[player] = projected

    return player_to_fp

def look_for_stat_arbitrage(old_table_rows, sites):
    # all_sites = ["PP", "betMGM", "Awesemo", "HotStreak", "Underdog", "DK", "Caesars"]
    all_sites = ["TF", "PP", "Caesars", "Underdog"]
    site_to_proj = get_site_to_pt_rbd_ast_projections(sites, all_sites)
    player_to_site_to_val = {}
    for site, projections in site_to_proj.items():
        for player, val in projections.items():
            if not player in player_to_site_to_val:
                player_to_site_to_val[player] = {}

            player_to_site_to_val[player][site] = val
    
    # all_sites = sites.keys()
    rows_to_print = []
    for player, site_to_val in player_to_site_to_val.items():
        new_row = [player]
        if len(site_to_val.keys()) < 2:
            continue

        max_val = None
        min_val = None
        for site in all_sites:
            val = ""
            if site in site_to_val:
                val = round(float(site_to_val[site]), 2)
            new_row.append(val)

            if val != '':
                val = float(val)
                if max_val == None or val > max_val:
                    max_val = val
                if min_val == None or val < min_val:
                    min_val = val

        val_range = max_val - min_val
        if val_range < 3:
            continue

        new_row.append(val_range)

        rows_to_print.append(new_row)

    rows_sorted = sorted(rows_to_print, key=lambda a: a[-1], reverse=True)
    headers = ["name"]
    headers += all_sites
    headers.append("range")
    as_str = tabulate(rows_sorted, headers=headers)
    as_str2 = tabulate(old_table_rows, headers=headers)
    if as_str2 != as_str:
        print(as_str)
    return rows_sorted


def produce_MLE_projections(sites):
    # dk_projections = sites["DK-Projected"]
    # betMGM_projections = sites["betMGM-Projected"]
    caesars_projections = sites["caesars-Projected"]

    player_to_MLE_projection = {}
    for player, stats in caesars_projections.items():
        fantasy_score = stats["Fantasy Score"]
        if fantasy_score == "REMOVED":
            continue
        fantasy_score = float(fantasy_score)
        player_to_MLE_projection[player] = fantasy_score

    # for player, stats in betMGM_projections.items():
    #     if player in player_to_MLE_projection:
    #         continue
    #     fantasy_score = stats["Fantasy Score"]
    #     if fantasy_score == "REMOVED":
    #         continue
    #     fantasy_score = float(fantasy_score)
    #     player_to_MLE_projection[player] = fantasy_score

    # for player, stats in dk_projections.items():
    #     if player in player_to_MLE_projection:
    #         continue
    #     fantasy_score = stats["Fantasy Score"]
    #     if fantasy_score == "REMOVED":
    #         continue
    #     fantasy_score = float(fantasy_score)
    #     player_to_MLE_projection[player] = fantasy_score
    

    site = "MLE-Projected"
    MLE_new_projections = {}
    for name, projection in player_to_MLE_projection.items():
        if not name in MLE_new_projections:
            MLE_new_projections[name] = {}
        MLE_new_projections[name]["Fantasy Score"] = str(round(projection, 2))
    old_projections = {}
    if site in sites:
        old_projections = sites[site]
    sites[site] = MLE_new_projections
    diff_projections(site, MLE_new_projections, old_projections, output_file, player_to_team)


def look_for_fantasy_point_arbitrage(old_table, sites, output_file, player_to_team):
    awesemo_fdp_projections = get_player_projections_awesemo(sites)

    betMGM_fdp_projections = get_player_projections_betMGM(sites)

    caesars_fdp_projections = get_player_projections_Caesars(sites)
    
    pp_fdp_projections = {}
    if "PP" in sites:
        for name, stats in sites["PP"].items():
            if "Fantasy Score" in stats:
                if stats["Fantasy Score"] == "REMOVED":
                    continue
                pp_fdp_projections[name] = float(stats["Fantasy Score"])


    dk_fdp_projections = get_player_projections_dk(sites)
    old_table_names = []
    if old_table.rows != None:
        old_table_names = [a[0] for a in old_table.rows]

    arbitrage_rows = []
    ##search for arbitrage:
    ARBITRAGE_CUTTOFF = 3.3
    for name, projection in pp_fdp_projections.items():
        if not isinstance(projection, float):
            continue

        diff1 = 0
        diff2 = 0
        diff3 = 0
        diff4 = 0
        v1 = 0
        v2 = 0 
        v3 = 0
        v4 = 0

        # if name in dk_fdp_projections:
        #     v1 = round(dk_fdp_projections[name], 2)
        #     diff1 = round(v1 - projection, 2)

        # if name in awesemo_fdp_projections:
        #     v2 = round(awesemo_fdp_projections[name], 2)
        #     diff2 = round(v2 - projection, 2)

        if name in betMGM_fdp_projections:
            v3 = round(betMGM_fdp_projections[name], 2)
            diff3 = round(v3 - projection, 2)

        if name in caesars_fdp_projections:
            v4 = round(caesars_fdp_projections[name], 2)
            diff4 = round(v4 - projection, 2)

        if abs(diff3) > ARBITRAGE_CUTTOFF or abs(diff4) > ARBITRAGE_CUTTOFF or name in old_table_names:
            team = get_player_team(name, player_to_team)
            arbitrage_rows.append([name, team, projection, diff3, diff4])



    site = "DK-Projected"
    dk_new_projections = {}
    for name, projection in dk_fdp_projections.items():
        if not name in dk_new_projections:
            dk_new_projections[name] = {}
        dk_new_projections[name]["Fantasy Score"] = str(round(projection, 2))

    old_projections = {}
    if site in sites:
        old_projections = sites[site]
    sites[site] = dk_new_projections
    diff_projections(site, dk_new_projections, old_projections, output_file, player_to_team)



    site = "Awesemo-Projected"
    awesemo_new_projections = {}
    for name, projection in awesemo_fdp_projections.items():
        if not name in awesemo_new_projections:
            awesemo_new_projections[name] = {}
        awesemo_new_projections[name]["Fantasy Score"] = str(round(projection, 2))

    old_projections = {}
    if site in sites:
        old_projections = sites[site]
    sites[site] = awesemo_new_projections
    diff_projections(site, awesemo_new_projections, old_projections, output_file, player_to_team)

    site = "betMGM-Projected"
    betMGM_new_projections = {}
    for name, projection in betMGM_fdp_projections.items():
        if not name in betMGM_new_projections:
            betMGM_new_projections[name] = {}
        betMGM_new_projections[name]["Fantasy Score"] = str(round(projection, 2))

    old_projections = {}
    if site in sites:
        old_projections = sites[site]
    sites[site] = betMGM_new_projections
    diff_projections(site, betMGM_new_projections, old_projections, output_file, player_to_team)


    site = "caesars-Projected"
    caesars_new_projections = {}
    for name, projection in caesars_fdp_projections.items():
        if not name in caesars_new_projections:
            caesars_new_projections[name] = {}
        caesars_new_projections[name]["Fantasy Score"] = str(round(projection, 2))
    old_projections = {}
    if site in sites:
        old_projections = sites[site]
    sites[site] = caesars_new_projections
    diff_projections(site, caesars_new_projections, old_projections, output_file, player_to_team)

    #MONEY LINE EDGE PROJECTIONS – aggregate of known projections
    produce_MLE_projections(sites)
    
    arbitrage_rows_sorted = sorted(arbitrage_rows, key=lambda a: max(abs(a[3]), abs(a[4])), reverse=True)
    new_table = DataTable(arbitrage_rows_sorted, ["name", "team", "PP proj", "betMGM diff", "caesars diff"])

    def write_row_to_dynamo(row):
        write_arbitrage("PP", row[0], row[1], "Fantasy Score", row[2], ["Caesars"], [row[2] + row[4]], row[4])
        pass

    diff_result = DataTable.diff(old_table, new_table, columns_to_not_diff=[], primary_key_idx=0, upload_row_to_dynamo=write_row_to_dynamo)
    # if diff_result != None:
    #     client.api.account.messages.create(
    #         to="+15166607159",
    #         from_="+14582374359",
    #         body=diff_result)
    
    return new_table

def query_dict(dict, *keys):
    current_dict = dict
    for key in keys:
        if key in current_dict:
            current_dict = current_dict[key]

        else:
            return None
    return current_dict


def write_to_dict(dict, *keys):
    current_dict = dict
    for key in keys[:-2]:
        if not key in current_dict:
            current_dict[key] = {}
            current_dict = current_dict[key]
        else:
            current_dict = current_dict[key]
    current_dict[keys[-2]] = keys[-1]


TF_stat_key_to_betMGM_and_Caesars_stat_key = {
    "REBS": {"betMGM": "rebounds", 
            "Caesars": "Rebounds"},
    "PTS": {"betMGM": "points", 
            "Caesars": "Points"},
    "ASTS": {"betMGM": "assists", 
            "Caesars": "Assists"},
    "PTS + ASTS": {"betMGM": "points + assists", 
                    "Caesars": "Points + Assists"},
    "REBS + ASTS": {"betMGM": "rebounds + assists", 
                    "Caesars": "Rebounds + Assists"},
    "PTS + REBS + ASTS": {"betMGM": "points + assists + rebounds", 
                        "Caesars": "Points + Assists + Rebounds"},
    "PTS + REBS": {"betMGM": "points + rebounds", 
                    "Caesars": "Points + Rebounds"},
}

def thrive_fantasy_arbitrage(sites, old_table, player_to_team):
    if not "TF" in sites:
        return
    arbitrage_rows = []
    CUTOFF = 0.5

    old_table_names = []

    if old_table == None:
        print("OLD TABLE IS NONE")
        return DataTable(None, None)
    
    if old_table.rows != None:
        old_table_names = [a[0] for a in old_table.rows]

    #TODO: do the same thing for underdog, MKF
    #
    for player_name, stats in sites["TF"].items():
        team = get_player_team(player_name, player_to_team)
        for stat, val in stats.items():
            new_row = [player_name, team, stat, val]
            mgm_val = query_dict(sites, "betMGM", player_name, TF_stat_key_to_betMGM_and_Caesars_stat_key[stat]["betMGM"])
            caesars_val = query_dict(sites, "Caesars", player_name, TF_stat_key_to_betMGM_and_Caesars_stat_key[stat]["Caesars"])

            mgm_diff = 0
            if mgm_val != None:
                mgm_diff = round(float(mgm_val) - float(val), 2)

            caesars_diff = 0
            if caesars_val != None:
                caesars_diff = round(float(caesars_val) - float(val), 2)
            new_row += [mgm_diff, caesars_diff]


            if abs(caesars_diff) < CUTOFF and abs(mgm_diff) < CUTOFF and player_name not in old_table_names:
                continue

            arbitrage_rows.append(new_row)

    arbitrage_rows_sorted = sorted(arbitrage_rows, key=lambda a: max(abs(a[4]), abs(a[5])), reverse=True)
    new_table = DataTable(arbitrage_rows_sorted, ["name", "team", "stat", "TF", "betMGM diff", "caesars diff"])

    def write_row_to_dynamo(row):
        #  write_arbitrage(site, player, team, stat_key, value, site_names, site_values, diff):
        write_arbitrage("TF", row[0], row[1], row[2], row[3], ["BetMGM", "Caesars"], [row[3] + row[4], row[3] + row[5]], max(row[4], row[5]))

    if old_table != None:
        DataTable.diff(old_table, new_table, columns_to_not_diff=[], primary_key_idx=0, upload_row_to_dynamo=write_row_to_dynamo)

    return new_table


def get_fd_slate_players(fd_slate_file_name):
    all_players = {}
    salaries = open(fd_slate_file_name)
    lines = salaries.readlines()
    found_count = 0

    for line in lines[1:]:
        parts = line.split(',')
        full_name = optimizer_player_pool.normalize_name(parts[3])

        positions = parts[1]
        salary = parts[7]
        team = parts[9]
        team = optimizer_player_pool.normalize_team_name(team)
        status = parts[11]
        if status == "O":
            continue
        name = full_name
        all_players[name] = [name, positions, float(salary), team, status]
        
    return all_players


def get_player_val(name, sites):
    site_order = ["caesars-Projected", "betMGM-Projected", "DK-Projected"]
    val = None
    for site in site_order:
        if not site in sites:
            continue

        val = query_dict(sites, site, name, "Fantasy Score")
        if val != None:
            return val
    
    return None


def generate_lineups(sites, generated_lineups):
    print("generate lineups")
    headers = ["slate", "lineup", "value", "cost"]
    rows = []
    if sites == None:
        return
    download_folder = "/Users/amichailevy/Downloads/"
    folder = download_folder + "player_lists/"
    with open("lineups_to_generate.txt", "r+") as lineups_file:
        lines = lineups_file.readlines()
        for line in lines[1:]:
            if line[0] == "#":
                continue
            parts = line.split('|')
            slate_name = parts[0]
            file_name = parts[1]
            slate_type = parts[2]
            includes = parts[3]
            excludes = parts[4].split(',')
            excludes = [ex.strip() for ex in excludes]
            fd_players_by_position = {}
            seen_names = []

            missing_player_names = []
            missing_players = []

            all_players = []
            fd_player_pool = get_fd_slate_players(folder + file_name)
            for player_name, player_info in fd_player_pool.items():
                if player_name in excludes:
                    continue
                positions = player_info[1]
                fd_pos = positions.split(',')[0]

                for pos in fd_pos.split("/"):
                    if not pos in fd_players_by_position:
                        fd_players_by_position[pos] = []
                    
                    price = player_info[2]

                    val = get_player_val(player_name, sites)
                    team = player_info[3]

                    if val == None:
                        if not player_name in missing_player_names:
                            missing_players.append((player_name, price))
                            missing_player_names.append(player_name)

                        continue

                    pl = fd_optimizer.Player(player_name, pos, price, team, val)
                    fd_players_by_position[pos].append(pl)

                    if not player_name in seen_names:
                        all_players.append(pl)
                        seen_names.append(player_name)

            if slate_type == 'single':
                result = fd_optimizer.single_game_optimizer(all_players)
                if result != None:
                    total_value = sum([p.value for p in result])
                    total_cost = sum([p.cost for p in result])
                    print("{} - {}, {}".format(result, total_value, total_cost))
            elif slate_type == 'full':
                result = fd_optimizer.generate_roster_quiet(fd_players_by_position)
                if result != None:
                    total_value = result.value
                    total_cost = result.cost
                    print(result)
            elif slate_type == "three":
                result = fd_optimizer.three_man_optimizer(all_players)
                if result != None:
                    total_value = sum([p.value for p in result])
                    total_cost = sum([p.cost for p in result])
                    print("{} - {}, {}".format(result, total_value, total_cost))
            else:
                assert False
            
            if result == None:
                continue

            missing_players_sorted = sorted(missing_players, key=lambda a: a[1], reverse=True)
            print(slate_name)
            print(missing_players_sorted)

            new_row = [slate_name, str(result), round(total_value, 2), total_cost]
            rows.append(new_row)

    new_table = DataTable(rows, headers)
    DataTable.diff(generated_lineups, new_table, columns_to_not_diff=[1])
    return new_table


# preserve remote state so we don't overwrite with duplicates
# handle REMOVED stats
def parse_arbitrage_to_write(site, stat, player, team, site_to_value):
    if not site in site_to_value:
        return

    value = float(site_to_value[site])
    sites = []
    vals = []

    max_diff_val = None
    max_diff_abs = None

    if "Caesars" in site_to_value:
        caesars_val = site_to_value["Caesars"]
        if caesars_val != None:
            sites.append("Caesars")
            caesars_val = float(caesars_val)
            vals.append(caesars_val)
            diff = caesars_val - value
            if max_diff_abs == None or abs(diff) > max_diff_abs:
                max_diff_abs = abs(diff)
                max_diff_val = diff

    if "betMGM" in site_to_value:
        betMGM_val = site_to_value["betMGM"]
        if betMGM_val != None:
            sites.append("BetMGM")
            betMGM_val = float(betMGM_val)
            vals.append(betMGM_val)
            diff = betMGM_val - value
            if max_diff_abs == None or abs(diff) > max_diff_abs:
                max_diff_abs = abs(diff)
                max_diff_val = diff

    if "DK" in site_to_value:
        dk_val = site_to_value["DK"]
        if dk_val != None:
            sites.append("Draft Kings")
            dk_val = float(dk_val)
            vals.append(dk_val)
            diff = dk_val - value
            if max_diff_abs == None or abs(diff) > max_diff_abs:
                max_diff_abs = abs(diff)
                max_diff_val = diff

    if max_diff_val == None:
        return
        
    write_arbitrage(site, player, team, stat, value, sites, vals, max_diff_val)

def arbitrage_finder(sites, old_table, player_to_team):
    stat_to_player_to_site_to_value = {"Points": {}, "Rebounds": {}, "Assists": {}}
    to_consider = ["PP", "DK", "Caesars", "betMGM", "Underdog", "TF"]

    # points 
    for site, site_data in sites.items():
        if not site in to_consider:
            continue

        if site == "PP":
            for name, stat_value in site_data.items():
                for stat, value in stat_value.items():
                    if stat == "Points":
                        write_to_dict(stat_to_player_to_site_to_value, "Points", name, site, value)
                    elif stat == "Rebounds":
                        write_to_dict(stat_to_player_to_site_to_value, "Rebounds", name, site, value)
                    elif stat == "Assists":
                        write_to_dict(stat_to_player_to_site_to_value, "Assists", name, site, value)

        elif site == "DK":
            for name, stat_value in site_data.items():
                for stat, value in stat_value.items():
                    if stat == "Points":
                        write_to_dict(stat_to_player_to_site_to_value, "Points", name, site, value)

        elif site == "Caesars":
            for name, stat_value in site_data.items():
                for stat, value in stat_value.items():
                    if stat == "Points":
                        write_to_dict(stat_to_player_to_site_to_value, "Points", name, site, value)
                    elif stat == "Rebounds":
                        write_to_dict(stat_to_player_to_site_to_value, "Rebounds", name, site, value)
                    elif stat == "Assists":
                        write_to_dict(stat_to_player_to_site_to_value, "Assists", name, site, value)
        elif site == "betMGM":
            for name, stat_value in site_data.items():
                for stat, value in stat_value.items():
                    if stat == "points":
                        write_to_dict(stat_to_player_to_site_to_value, "Points", name, site, value)
                    elif stat == "rebounds":
                        write_to_dict(stat_to_player_to_site_to_value, "Rebounds", name, site, value)
                    elif stat == "assists":
                        write_to_dict(stat_to_player_to_site_to_value, "Assists", name, site, value)
        elif site == "Underdog":
            for name, stat_value in site_data.items():
                for stat, value in stat_value.items():
                    if stat == "points":
                        write_to_dict(stat_to_player_to_site_to_value, "Points", name, site, value)
                    elif stat == "rebounds":
                        write_to_dict(stat_to_player_to_site_to_value, "Rebounds", name, site, value)
                    elif stat == "assists":
                        write_to_dict(stat_to_player_to_site_to_value, "Assists", name, site, value)
        elif site == "TF":
            for name, stat_value in site_data.items():
                for stat, value in stat_value.items():
                    if stat == "PTS":
                        write_to_dict(stat_to_player_to_site_to_value, "Points", name, site, value)
                    elif stat == "REBS":
                        write_to_dict(stat_to_player_to_site_to_value, "Rebounds", name, site, value)
                    elif stat == "ASTS":
                        write_to_dict(stat_to_player_to_site_to_value, "Assists", name, site, value)
        

    
    #'Site-Stat-Player'
    # Assuming PP
    # for every site, for every stat, for every player, pp val, betMGM val, caesars val
    # 

    all_rows = []
    for stat, player_to_site_to_value in stat_to_player_to_site_to_value.items():
        for player, site_to_value in player_to_site_to_value.items():
            team = None
            if player in player_to_team:
                team = player_to_team[player]

            row = [stat]
            max_val = None
            min_val = None
            for site, value in site_to_value.items():
                value = float(value)
                if max_val == None or value > max_val:
                    max_val = value
                if min_val == None or value < min_val:
                    min_val = value

            if abs(max_val - min_val) > 0.9:
                row.append(player)
                for site in to_consider:
                    val = ""
                    if site in site_to_value:
                        val = round(float(site_to_value[site]), 2)
                    row.append(val)
                diff = round(max_val - min_val, 2)
                row.append(diff)
                all_rows.append(row)

            # if team != None:
            #     # parse_arbitrage_to_write(site, player, team, stat, site_to_value):
            #     if "PP" in site_to_value and ("Caesars" in site_to_value or "betMGM" in site_to_value or "DK" in site_to_value):
            #         parse_arbitrage_to_write("PP", stat, player, team, site_to_value)

            #     if "TF" in site_to_value and ("Caesars" in site_to_value or "betMGM" in site_to_value or "DK" in site_to_value):
            #         parse_arbitrage_to_write("TF", stat, player, team, site_to_value)

            #     if "Underdog" in site_to_value and ("Caesars" in site_to_value or "betMGM" in site_to_value or "DK" in site_to_value):
            #         parse_arbitrage_to_write("Underdog", stat, player, team, site_to_value)


    # look for PP arbitrage

    # write_arbitrage(site, player, team, stat_key, site_names, site_values)

    headers = ["Stat", "Name"]
    headers += to_consider
    headers.append("Diff")

    all_rows = sorted(all_rows, key=lambda a: a[8], reverse=True)

    new_table = DataTable(all_rows, headers)
    if old_table != None:
        DataTable.diff(old_table, new_table, columns_to_not_diff=[], primary_key_idx=1)

    return new_table
    
            
def get_player_prices(dk_slate_file, fd_slate_file):
    dk_players = optimizer_player_pool.get_dk_slate_players(dk_slate_file)
    fd_players = optimizer_player_pool.get_fd_slate_players(fd_slate_file, False)
    # yahoo_players = optimizer_player_pool.get_yahoo_slate_players(yahoo_slate_file)
    yahoo_players = {}
    
    return (dk_players, fd_players, yahoo_players)


def test_table():
    old_table = DataTable([["-", "A1","",""], ["-", "A2","",""], ["-", "A3","",""]], ["-", "A", "B", "C"])
    new_table = DataTable([["-", "A1","5","2"], ["-", "A2","6",""], ["-", "A3","","3"]], ["-", "A", "B", "C"])
    DataTable.diff(old_table, new_table, [], 1)
    pass


if __name__ == "__main__":

    # test_table()

    folder = "/Users/amichailevy/Downloads/player_lists/"
    dk_slate_file = folder + "DKSalaries_12_29_21.csv"
    fd_slate_file = folder + "FanDuel-NBA-2021 ET-12 ET-29 ET-69397-players-list.csv"
    
    (dk_players, fd_players, yahoo_players) = get_player_prices(dk_slate_file, fd_slate_file)

    current_date = datetime.datetime.now()
    output_file_name = "money_line_scrape_{}_{}_{}.txt".format(current_date.month, current_date.day, current_date.year)


    # all_sites = ["PP", "RW", "Underdog", "HotStreak", "DK", "Awesemo"]
    # all_sites = ["PP", "RW", "DK", "Awesemo", "betMGM"]
    # all_sites = ["betMGM", "Underdog", "HotStreak", "PP", "RW", "DK", "Awesemo", "Caesars"]

    all_sites = ["betMGM", "TF", "PP", "RW", "Caesars", "Underdog"]
    # all_sites = ["betMGM", "PP", "Caesars", "DK"]



    if not path.exists(output_file_name):
        output_file = open(output_file_name, "a")
    else:
        output_file = open(output_file_name, "r+")

    sites = {}

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


    driver = webdriver.Chrome("../master_scrape_process/chromedriver")

    period = 28
    log("starting up! PERIOD: {}".format(period), output_file)

    player_to_team = {}
    for player, player_info in fd_players.items():
        player_to_team[player] = player_info[3]

    for player, player_info in dk_players.items():
        if player in player_to_team:
            continue
        player_to_team[player] = player_info[3]

    fp_arbitrage_rows_sorted = DataTable(None, None)

    generated_lineups = DataTable(None, None)
    thrive_fantasy_table = DataTable(None, None)
    stat_arbitrage_table = DataTable(None, None)

    stat_rows_sorted = []

    timeseries_remote_state = {}
    all_current_money_lines_remote_state = {}

    while True:
        for site in all_sites:

            
            log("{} - scraping {}".format(time_str(), site), output_file)
            new_projections = get_projections(site, driver)
            # try:
            # except:
            #     __import__('pdb').set_trace()
            #     continue
            if not site in sites:
                sites[site] = {}
            diff_projections(site, new_projections, sites[site], output_file, player_to_team)
            
            sites[site] = new_projections

            fp_arbitrage_rows_sorted = look_for_fantasy_point_arbitrage(fp_arbitrage_rows_sorted, sites, output_file, player_to_team)


            stat_rows_sorted = look_for_stat_arbitrage(stat_rows_sorted, sites)
            thrive_fantasy_table = thrive_fantasy_arbitrage(sites, thrive_fantasy_table, player_to_team)

            stat_arbitrage_table = arbitrage_finder(sites, stat_arbitrage_table, player_to_team)

            # all_current_money_lines_remote_state = diff_money_lines(sites, all_current_money_lines_remote_state, player_to_team, fd_players)

            time.sleep(period)

        generated_lineups = generate_lineups(sites, generated_lineups)
            

