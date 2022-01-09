import datetime
from os import path
from types import FrameType

from optimizer_player_pool import normalize_name

from selenium import webdriver
import time
import requests

from tabulate import tabulate


# url = "https://www.draftkings.com/contest/exportfullstandingscsv/120679810"

# driver = webdriver.Chrome("../master_scrape_process/chromedriver")
# driver.get(url)

# __import__('pdb').set_trace()

def get_PP_projection(player, player_to_money_line):
    if not player in player_to_money_line:
        return None
    pp_money_line = player_to_money_line[player]
    return pp_money_line

    # return 35

def main():
    root = "/Users/amichailevy/Downloads/"
    dk_player_list_path = "player_lists/DKSalaries_12_27_21.csv" #12/19/21
    # dk_player_list_path = "DKSalaries (9).csv"
    dk_ownership_percentage_path = "contest-standings-121457261 3.csv"

    player_to_team = {}
    player_to_start_time = {}
    start_time_to_player = {}

    player_to_salary = {}
    with open(root + dk_player_list_path, "r") as file:
        lines = file.readlines()
        for line in lines[1:]:
            parts = line.split(',')
            pos = parts[0]
            name = parts[2]
            name = normalize_name(name)
            salary = parts[5]
            team = parts[7]
            player_to_salary[name] = salary
            player_to_team[name] = team
            start_time = parts[6].split(' ')[2]
            player_to_start_time[name] = start_time
            if not start_time in start_time_to_player:
                start_time_to_player[start_time] = []
            start_time_to_player[start_time].append(name)

    all_times = list(start_time_to_player.keys())
    target_time = None
    target_time_diff = None
    for time in all_times:
        inspection_time = datetime.datetime.strptime(time,'%H:%MPM').time()
        current_time = datetime.datetime.now().time()
        if current_time < inspection_time:
            if target_time == None:
                target_time = inspection_time
                # __import__('pdb').set_trace()
                # target_time_diff = inspection_time - current_time

    player_pool = None
    player_pool = start_time_to_player["07:00PM"]
    # __import__('pdb').set_trace()

    
    # __import__('pdb').set_trace()
    player_to_ownership_percentage = {}
    with open(root + dk_ownership_percentage_path, "r") as file:
        lines = file.readlines()
        for line in lines[1:]:
            parts = line.split(',')
            if len(parts) < 10:
                break
            name = parts[7]
            name = normalize_name(name)
            ownership = parts[9]
            player_to_ownership_percentage[name] = ownership.strip('%')

    current_date = datetime.datetime.now()
    money_line_scrape_path = "money_line_scrape_{}_{}_{}.txt".format(current_date.month, current_date.day, current_date.year)
    money_line_scrape_file = open(money_line_scrape_path, "r")

    player_to_money_line = {}

    lines = money_line_scrape_file.readlines()
    for line in lines:
        parts = line.split("|")
        if len(parts) < 4:
            continue
        site = parts[1]
        if site != "PP":
            continue
        stat = parts[4]
        if stat != "Fantasy Score":
            continue
        
        player_name = parts[2]
        
        val = parts[5].strip()
        if val == "REMOVED":
            if player_name in player_to_money_line:
                del player_to_money_line[player_name]
            continue
        
        player_to_money_line[player_name] = val

    all_rows = []


    for player, ownership in player_to_ownership_percentage.items():
        # print("--{}".format(player))
        player = normalize_name(player)
        if float(ownership) > 2:
            # get his price
            if not player in player_to_salary:
                print("Missing: {}".format(player))
                continue
            salary = player_to_salary[player]
            salary_projected_output = float(salary) / 200
            pp_money_line = get_PP_projection(player, player_to_money_line)
            if pp_money_line == None:
                # __import__('pdb').set_trace()
                continue

            # print("{} - {} - money line: {}, projected: {} = {}".format(player, team, pp_money_line, salary_projected_output, float(salary_projected_output) -  float(pp_money_line)))


            team = ''
            if player in player_to_team:
                team = player_to_team[player]
            if float(salary_projected_output) >= float(pp_money_line):
                # print("OVER: {} {}% - {} - money line: {}, projected: {}".format(player, ownership, team, pp_money_line, salary_projected_output))

                all_rows.append(["OVER", player, team, "{}%".format(ownership), pp_money_line, salary_projected_output])
            

            # __import__('pdb').set_trace()

    for player, salary in player_to_salary.items():
        player = normalize_name(player)
        # if player not in player_pool:
        #     continue

        ownership = 0
        if player in player_to_ownership_percentage:
            ownership = player_to_ownership_percentage[player]

        if float(ownership) > 5.9:
            continue

        pp_money_line = get_PP_projection(player, player_to_money_line)
        if pp_money_line == None:
            continue

        team = ''
        if player in player_to_team:
            team = player_to_team[player]


        salary = player_to_salary[player]
        salary_projected_output = float(salary) / 200
        
        if float(pp_money_line) >= float(salary_projected_output):
            # print("UNDER: {} - {}% {} - money line: {} projected {}".format(player, ownership, team, pp_money_line, salary_projected_output))
            all_rows.append(["UNDER", player, team, "{}%".format(ownership), pp_money_line, salary_projected_output])

    # EVERY CANDIDATE PLAYER THAT'S NOT WELL OWNED AND WHOSE PP VALUE IMPLIES A POSITIVE SCORE

    # __import__('pdb').set_trace()

    # for each well owned player
    # get a pt projection from the score
    # adjust this pt projection with ownership percentage

    # compare this to the PP fantasy point projection

    #7:30pm - 12/22/21
    #https://www.draftkings.com/draft/contest/121113252
    #https://www.draftkings.com/contest/gamecenter/121113252


    # find under bets.
    # Automatically scrape the slate files
    # automaticall place bets on prize picks - only FP(3)

    result = tabulate(all_rows, headers=["O/U", "Name", "Team", "Own %", "PP Line", "Projected"])
    print(result)

if __name__ == "__main__":
    main()



#https://www.draftkings.com/draft/contest/121216027# - $555 MME saturday

#https://www.draftkings.com/draft/contest/120113923 - $15 MME Saturday
#https://www.draftkings.com/contest/gamecenter/120113923

#https://www.draftkings.com/draft/contest/121336420 - 15 MME Sunday 6pm
#https://www.draftkings.com/contest/gamecenter/121336420


#https://www.draftkings.com/draft/contest/121316824 - 10 MME single game 3:30pm
# #https://www.draftkings.com/contest/gamecenter/121316824
# DKSalaries (4).csv



#https://www.draftkings.com/draft/contest/121457261 - 12/27/21 15 MME
#https://www.draftkings.com/contest/gamecenter/121457261
# https://www.draftkings.com/draft/contest/121440419 - tiers


#https://www.draftkings.com/draft/contest/121502514 - 12/28/21 15 MME
#https://www.draftkings.com/contest/gamecenter/121502514


# https://www.draftkings.com/draft/contest/121620527 - 12/30/21 15 MME

#https://www.draftkings.com/draft/contest/121658906 - 12/31/21 early slate 15 MME