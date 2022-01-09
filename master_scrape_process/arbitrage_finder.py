import datetime
import pandas as pd

def query(dict, key):
    if key in dict:
        return dict[key]
    return ''

def analysis1():
    current_date = datetime.datetime.now()
    file_name = "money_line_scrape_{}_{}_{}.txt".format(current_date.month, current_date.day, current_date.year)

    input_file = open(file_name, "r")

    by_player = {}
    player_to_team = {}

    lines = input_file.readlines()
    for line in lines:
        parts = line.split("|")
        if len(parts) < 4:
            continue
        date = parts[0]
        site = parts[1]
        player_name = parts[2]
        team = None
        if site not in ["PP", "Underdog", "HotStreak"]:
            continue

        if site == "HotStreak":
            name_parts = player_name.split('-')
            player_name = name_parts[0]
            team = name_parts[1]

            player_to_team[player_name] = team

        if not player_name in by_player:
            by_player[player_name] = {}
        
        val = parts[4].strip()
        stat = parts[3]

        stat_key = "{}-{}".format(site, stat)
        by_player[player_name][stat_key] = val


    for player, stat_keys in by_player.items():
        team = ""
        if player in player_to_team:
            team = player_to_team[player]
        


        
        PP_fp1 = query(stat_keys, "PP-Fantasy Score")
        PP_pts = query(stat_keys, "PP-Points")
        HS_pts= query(stat_keys, "HotStreak-points")
        UD_pts = query(stat_keys, "Underdog-points")
        # print("Points = {}, {}, {}".format(PP_pts, HS_pts, UD_pts))

        UD_pts_rbds_asts = ''
        PP_pts_rbds_asts = ''
        HS_pts_rbds_asts = ''
        HS_fp = ''

        UD_pts_rbds_asts = query(stat_keys, "Underdog-pts_rebs_asts")

        HS_asts = query(stat_keys, "HotStreak-assists")
        HS_rbds = query(stat_keys, "HotStreak-rebounds")
        if HS_asts != '' and HS_rbds != '' and HS_pts != '':
            HS_pts_rbds_asts = float(HS_pts) + float(HS_rbds) + float(HS_asts)
            HS_fp = float(HS_pts) + float(HS_rbds) * 1.2 + float(HS_asts) * 1.5

        PP_asts = query(stat_keys, "PP-Assists")
        PP_rbds = query(stat_keys, "PP-Rebounds")
        PP_fp2 = 0
        if PP_pts != '' and PP_asts != '' and PP_rbds != '':
            PP_pts_rbds_asts = float(PP_pts) + float(PP_rbds) + float(PP_asts)
            PP_fp2 = float(PP_pts) + float(PP_rbds) * 1.2 + float(PP_asts) * 1.5

        if PP_fp1 != '' and PP_fp2 != '' and float(PP_fp2) > float(PP_fp1):
        # if HS_fp != '' and PP_fp != '' and float(HS_fp) >= float(PP_fp):
        # if PP_fp != '' and PP_fp != '' and float(HS_fp) >= float(PP_fp):

            print("- {} - {}".format(player, team))

            print("FP = {}, {} diff = {}".format(PP_fp1, PP_fp2, round(float(PP_fp2) - float(PP_fp1), 2)))
            # print("FP = pp{}, hs{}".format(PP_fp1, HS_fp))
            # print("Points = pp{}, hs{}, ud{}".format(PP_pts, HS_pts, UD_pts))
            # print("PTS, RBDS, ASTS = pp{}, hs{}, ud{}".format(PP_pts_rbds_asts, HS_pts_rbds_asts, UD_pts_rbds_asts))

        # for stat, val in stat_keys.items():

        #     print("{} - {}".format(stat, val))


def normalize_name(name):
    name = name.replace("  ", " ")
    name = name.replace("’", "'")
    parts = name.split(" ")
    if len(parts) > 2:
        return "{} {}".format(parts[0], parts[1])

    name = name.replace(".", "")
    name = name.strip()
    
    return name

def get_player_to_team():
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)

    filename = "~/Downloads/season_data/{}-{}-{}-nba-season-dfs-feed.xlsx".format(yesterday.month, str(yesterday.day).zfill(2), yesterday.year)

    dfs = pd.read_excel(filename, sheet_name=None)

    feed = dfs['NBA-DFS-SEASON-FEED']
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

        name = normalize_name(row["Unnamed: 4"])
        team = row["Unnamed: 5"]
        player_to_team[name] = team
    return player_to_team

def analysis2(player_to_team):
    current_date = datetime.datetime.now()
    file_name = "money_line_scrape_{}_{}_{}.txt".format(current_date.month, current_date.day, current_date.year)

    input_file = open(file_name, "r")
    
    all_lines = []


    lines = input_file.readlines()
    for line in lines:
        line = line.strip()
        parts = line.split("|")
        if len(parts) < 4:
            continue
        date = parts[0]
        site = parts[1]
        player_name = parts[2]
        team = None
        if site not in ["PP", "Underdog", "HotStreak", "DK"]:
            continue

        all_lines.append(parts)

    for line in all_lines:
        time = line[0]
        site = line[1]
        name = line[2]
        stat = line[3]
        value = line[4]


        if site == "HotStreak":
            name_parts = name.split('-')
            if len(name_parts) == 3:
                name_parts[0] = "{}-{}".format(name_parts[0], name_parts[1])
                name_parts[1] = name_parts[2]

            player_name = normalize_name(name_parts[0])
            team = name_parts[1]
            line[2] = player_name
        else:
            line[2] = normalize_name(name)


    team_to_players_to_stats = {}
    missing_names = []
    for line in all_lines:
        time = line[0]
        site = line[1]
        name = line[2]
        if not name in player_to_team and not name in missing_names:
            missing_names.append(name)

        team = player_to_team[name]
        stat = line[3]
        value = line[4]
    
        if not team in team_to_players_to_stats:
            team_to_players_to_stats[team] = {}

        if not name in team_to_players_to_stats[team]:
            team_to_players_to_stats[team][name] = {}

        if not site in team_to_players_to_stats[team][name]:
            team_to_players_to_stats[team][name][site] = {}

        if not stat in team_to_players_to_stats[team][name][site]:
            team_to_players_to_stats[team][name][site][stat] = []

        team_to_players_to_stats[team][name][site][stat].append(value)

        

        
    print(missing_names)
    for team, d1 in team_to_players_to_stats.items():
        print("\n\n----{}----".format(team))
        for player, d2 in d1.items():
            print("--{}".format(player))
            for site, d3 in d2.items():
                for stat, vals in d3.items():
                    print("{}|{} - {}".format(site, stat, vals))


def analysis3(player_to_team):
    current_date = datetime.datetime.now()
    file_name = "money_line_scrape_{}_{}_{}.txt".format(current_date.month, current_date.day, current_date.year)

    input_file = open(file_name, "r")
    
    all_lines = []

    lines = input_file.readlines()
    for line in lines:
        line = line.strip()
        parts = line.split("|")
        if len(parts) < 4:
            continue
        date = parts[0]
        site = parts[1]
        player_name = parts[2]
        team = None
        if site not in ["PP", "Underdog", "HotStreak", "DK", "Awesemo"]:
            continue

        all_lines.append(parts)

    for line in all_lines:
        time = line[0]
        site = line[1]
        name = line[2]
        stat = line[3]
        value = line[4]


        if site == "HotStreak":
            name_parts = name.split('-')
            if len(name_parts) == 3:
                name_parts[0] = "{}-{}".format(name_parts[0], name_parts[1])
                name_parts[1] = name_parts[2]

            player_name = normalize_name(name_parts[0])
            team = name_parts[1]
            line[2] = player_name
        else:
            line[2] = normalize_name(name)

    team_to_player_stat_site_vals = {}
    missing_names = []
    for line in all_lines:
        time = line[0]
        site = line[1]
        name = line[2]
        if not name in player_to_team and not name in missing_names:
            missing_names.append(name)

        team = player_to_team[name]
        stat = line[3].capitalize()
        value = line[4]
    
        if not team in team_to_player_stat_site_vals:
            team_to_player_stat_site_vals[team] = {}

        if not name in team_to_player_stat_site_vals[team]:
            team_to_player_stat_site_vals[team][name] = {}

        if not stat in team_to_player_stat_site_vals[team][name]:
            team_to_player_stat_site_vals[team][name][stat] = {}

        if not site in team_to_player_stat_site_vals[team][name][stat]:
            team_to_player_stat_site_vals[team][name][stat][site] = []

        if site == "DK" and not "REMOVED" in value:
            value = float(value.strip().split(' ')[0])

        if site == "HotStreak" and not "REMOVED" in value:
            value = float(value.strip().split(' ')[0])

        team_to_player_stat_site_vals[team][name][stat][site].append(value)

        
    if len(missing_names) > 0:
        import pdb; pdb.set_trace()


    for team, d1 in team_to_player_stat_site_vals.items():
        for player, d2 in d1.items():
            #awesemo first
            if not ("Steals" in d2 and "Blocks" in d2 and "Rebounds" in d2 and "Points" in d2 and "Assists" in d2):
                continue
            
            pts = (d2["Points"]["Awesemo"][-1])
            rbds = (d2["Rebounds"]["Awesemo"][-1])
            asts = (d2["Assists"]["Awesemo"][-1])
            blks = (d2["Blocks"]["Awesemo"][-1])
            stls = (d2["Steals"]["Awesemo"][-1])

            as_list = [pts, rbds, asts, blks, stls]
            if "REMOVED" in as_list:
                continue

            pts = float(pts)
            rbds = float(rbds)
            asts = float(asts)
            blks = float(blks)
            stls = float(stls)

            projected = pts + rbds * 1.2 + asts * 1.5 + blks * 3 + stls * 3
            if not "Fantasy score" in d2:
                d2["Fantasy score"] = {}
            d2["Fantasy score"]["Awesemo"] = [projected]

    stats_to_skip = ["Points + assists + rebounds", "Steals + blocks", "Assists", "Steals"]

    for team, d1 in team_to_player_stat_site_vals.items():
        if team == "Dallas" or team == "LA Clippers":
            continue
        print("\n\n----{}----".format(team))
        for player, d2 in d1.items():
            print("--{}".format(player))
            for stat, site_vals in d2.items():
                if stat in stats_to_skip:
                    continue
                if len(site_vals.keys()) < 2:
                    continue
                print("-{}".format(stat))

                val_set = []
                for site, vals in site_vals.items():
                    print("{}| {}".format(site, vals))
                    last_val = vals[-1]
                    if last_val != "REMOVED":
                        val_set.append(float(last_val))

                if len(val_set) > 0:
                    vals_sorted = sorted(val_set)
                    range = vals_sorted[0] - vals_sorted[-1]
                    if abs(range) >= 3:
                        print("****\n\n")


def nfl_lines_analysis():
    file_name = "money_line_scrape_11_21_2021.txt"
    input_file = open(file_name, "r")
    

    name_to_stat_to_site_to_line = {}

    all_lines = []

    lines = input_file.readlines()
    for line in lines:
        line = line.strip()
        parts = line.split("|")
        if len(parts) < 4:
            continue
        date = parts[0]
        site = parts[1]
        player_name = parts[2]
        team = None
        if site not in ["PP-NFL", "Awesemo-NFL"]:
            continue

        all_lines.append(parts)

    for line in all_lines:
        time = line[0]
        site = line[1]
        name = line[2]
        stat = line[3]
        value = line[4]
        # if site == "Awesemo-NFL" or site == "PP-NFL":
        #     print(line)

        if not name in name_to_stat_to_site_to_line:
            name_to_stat_to_site_to_line[name] = {}

        if not stat in name_to_stat_to_site_to_line[name]:
            name_to_stat_to_site_to_line[name][stat] = {}
        


        if value == "REMOVED" and len(name_to_stat_to_site_to_line[name][stat].keys()) > 1:
            print("{} - {} | {}".format(name, stat, name_to_stat_to_site_to_line[name][stat]))
            # import pdb; pdb.set_trace()
        
        
        if not site in name_to_stat_to_site_to_line[name][stat]:
            if value == "REMOVED":
                del name_to_stat_to_site_to_line[name][stat][site]
            else:
                name_to_stat_to_site_to_line[name][stat][site] = value




def NBA_historical_analysis():
    file_name = "money_line_scrape_11_20_2021.txt"
    input_file = open(file_name, "r")
    

    name_to_stat_to_site_to_line = {}

    all_lines = []

    lines = input_file.readlines()
    for line in lines:
        line = line.strip()
        parts = line.split("|")
        if len(parts) < 4:
            continue
        date = parts[0]
        site = parts[1]
        player_name = parts[2]
        team = None
        if site not in ["PP", "Awesemo"]:
            continue

        all_lines.append(parts)

    for line in all_lines:
        time = line[0]
        site = line[1]
        name = line[2]
        stat = line[3]
        value = line[4]

        if not name in name_to_stat_to_site_to_line:
            name_to_stat_to_site_to_line[name] = {}

        if not stat in name_to_stat_to_site_to_line[name]:
            name_to_stat_to_site_to_line[name][stat] = {}
        
        d2 = name_to_stat_to_site_to_line[name]

        if stat == "Fantasy score":
            import pdb; pdb.set_trace()

        if value == "REMOVED" and len(name_to_stat_to_site_to_line[name][stat].keys()) > 1:

            if stat == "Fantasy score":
                import pdb; pdb.set_trace()

            awesemo = float(name_to_stat_to_site_to_line[name][stat]["Awesemo"])
            pp = float(name_to_stat_to_site_to_line[name][stat]["PP"])
            if abs(awesemo - pp) >= 3:
                print("{} - {} | {}".format(name, stat, name_to_stat_to_site_to_line[name][stat]))
            # import pdb; pdb.set_trace()
        
        
        if not site in name_to_stat_to_site_to_line[name][stat]:
            if value == "REMOVED":
                del name_to_stat_to_site_to_line[name][stat][site]
            else:
                name_to_stat_to_site_to_line[name][stat][site] = value



        if ("Steals" in d2 and "Blocks" in d2 and "Rebounds" in d2 and "Points" in d2 and "Assists" in d2):
            try:
                pts = (d2["Points"]["Awesemo"])
                rbds = (d2["Rebounds"]["Awesemo"])
                asts = (d2["Assists"]["Awesemo"])
                blks = (d2["Blocks"]["Awesemo"])
                stls = (d2["Steals"]["Awesemo"])

                as_list = [pts, rbds, asts, blks, stls]
                if not "REMOVED" in as_list:
                    pts = float(pts)
                    rbds = float(rbds)
                    asts = float(asts)
                    blks = float(blks)
                    stls = float(stls)

                    projected = pts + rbds * 1.2 + asts * 1.5 + blks * 3 + stls * 3
                    if not "Fantasy score" in d2:
                        d2["Fantasy score"] = {}
                    d2["Fantasy Score"]["Awesemo"] = projected
            except:
                continue





if __name__ == "__main__":
    # player_to_team = get_player_to_team()
    # analysis3(player_to_team)
    # nfl_lines_analysis()
    NBA_historical_analysis()