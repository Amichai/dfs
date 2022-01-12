from roto_wire_overlay_optimizer.roto_wire_scrape import scrape_lineups
import roto_wire_scrape
import box_scores
import ast

def match_name(name1, names):
    name_parts = name1.split(' ')
    last_name = None
    if len(name_parts) == 2:
        last_name = name_parts[1]

    first_initial = name_parts[0][0]

    assert last_name != None

    candidates = []
    for name in names:
        if name == name1:
            return name

        if last_name in name and name[0] == first_initial:
            candidates.append(name)

    if len(candidates) > 1:
        print("{}, {}, {}".format(name1, last_name, candidates))


    if len(candidates) == 1:
        return candidates[0]

    return None

SCRAPE_ENABLED = False


if __name__ == "__main__":
    if not SCRAPE_ENABLED:
        rw_all_starters = ast.literal_eval("""[('LaMelo Ball', 'CHA', ''), ('Kelly Oubre', 'CHA', ''), ('G. Hayward', 'CHA', ''), ('Miles Bridges', 'CHA', ''), ('Mason Plumlee', 'CHA', ''), ('Cole Anthony', 'ORL', ''), ('Jalen Suggs', 'ORL', ''), ('Franz Wagner', 'ORL', ''), ('W. Carter', 'ORL', ''), ('Mo Bamba', 'ORL', ''), ('S. Dinwiddie', 'WAS', ''), ('Bradley Beal', 'WAS', ''), ('K. Caldwell-Pope', 'WAS', ''), ('Kyle Kuzma', 'WAS', ''), ('D. Gafford', 'WAS', ''), ('Marcus Smart', 'BOS', ''), ('Jaylen Brown', 'BOS', ''), ('Jayson Tatum', 'BOS', ''), ('Al Horford', 'BOS', '75%'), ('R. Williams', 'BOS', ''), ('Trae Young', 'ATL', ''), ('B. Bogdanovic', 'ATL', ''), ('D. Hunter', 'ATL', '75%'), ('John Collins', 'ATL', ''), ('Clint Capela', 'ATL', ''), ('D. Graham', 'NOP', ''), ('N. Alexander-Walker', 'NOP', ''), ('Josh Hart', 'NOP', '50%'), ('B. Ingram', 'NOP', ''), ('J. Valanciunas', 'NOP', ''), ('Kyle Lowry', 'MIA', ''), ('D. Robinson', 'MIA', ''), ('Jimmy Butler', 'MIA', ''), ('P.J. Tucker', 'MIA', ''), ('Bam Adebayo', 'MIA', ''), ('James Harden', 'BKN', ''), ('Joe Harris', 'BKN', ''), ('Kevin Durant', 'BKN', ''), ('Bruce Brown', 'BKN', ''), ('Blake Griffin', 'BKN', ''), ('M. Brogdon', 'IND', ''), ('Chris Duarte', 'IND', ''), ('J. Holiday', 'IND', ''), ('D. Sabonis', 'IND', ''), ('Myles Turner', 'IND', ''), ('Fred VanVleet', 'TOR', ''), ('Gary Trent', 'TOR', ''), ('OG Anunoby', 'TOR', ''), ('S. Barnes', 'TOR', ''), ('P. Achiuwa', 'TOR', ''), ('D. Russell', 'MIN', ''), ('A. Edwards', 'MIN', ''), ('J. McDaniels', 'MIN', ''), ('Josh Okogie', 'MIN', ''), ('K. Towns', 'MIN', ''), ('George Hill', 'MIL', ''), ('Grayson Allen', 'MIL', ''), ('K. Middleton', 'MIL', ''), ('G. Antetokounmpo', 'MIL', ''), ('T. Antetokounmpo', 'MIL', ''), ('R. Westbrook', 'LAL', ''), ('Kent Bazemore', 'LAL', ''), ('L. James', 'LAL', '50%'), ('A. Davis', 'LAL', '50%'), ('D. Jordan', 'LAL', ''), ('S. Gilgeous-Alexander', 'OKC', ''), ('Luguentz Dort', 'OKC', ''), ('Josh Giddey', 'OKC', ''), ('Darius Bazley', 'OKC', ''), ('D. Favors', 'OKC', ''), ("De'Aaron Fox", 'SAC', ''), ('T. Haliburton', 'SAC', ''), ('H. Barnes', 'SAC', ''), ('M. Harkless', 'SAC', ''), ('R. Holmes', 'SAC', ''), ('Chris Paul', 'PHX', ''), ('Devin Booker', 'PHX', ''), ('Mikal Bridges', 'PHX', ''), ('Jae Crowder', 'PHX', ''), ('Deandre Ayton', 'PHX', ''), ('Ja Morant', 'MEM', ''), ('D. Melton', 'MEM', ''), ('Desmond Bane', 'MEM', ''), ('Jaren Jackson', 'MEM', ''), ('Steven Adams', 'MEM', ''), ('D. Lillard', 'POR', ''), ('CJ McCollum', 'POR', ''), ('N. Powell', 'POR', '50%'), ('R. Covington', 'POR', ''), ('Jusuf Nurkic', 'POR', ''), ('D. Garland', 'CLE', ''), ('Collin Sexton', 'CLE', ''), ('L. Markkanen', 'CLE', ''), ('Evan Mobley', 'CLE', ''), ('Jarrett Allen', 'CLE', ''), ('R. Jackson', 'LAC', ''), ('Eric Bledsoe', 'LAC', ''), ('Paul George', 'LAC', ''), ('Nicolas Batum', 'LAC', ''), ('Ivica Zubac', 'LAC', '')]""")

        questionable_non_starting = ast.literal_eval("""[('T. Rozier', 'CHA', '25%'), ('P. Washington', 'CHA', 'O'), ('M. Carter-Williams', 'ORL', 'O'), ('M. Fultz', 'ORL', 'O'), ('J. Isaac', 'ORL', 'O'), ('E. Moore', 'ORL', 'O'), ('C. Okeke', 'ORL', 'O'), ('Raul Neto', 'WAS', '50%'), ('T. Bryant', 'WAS', 'O'), ('A. Gill', 'WAS', 'O'), ('R. Hachimura', 'WAS', 'O'), ('C. Winston', 'WAS', 'O'), ('R. Langford', 'BOS', '50%'), ('D. Gallinari', 'ATL', '50%'), ('L. Williams', 'ATL', '50%'), ('O. Okongwu', 'ATL', 'O'), ('Z. Williamson', 'NOP', 'O'), ('V. Oladipo', 'MIA', 'O'), ('K. Irving', 'BKN', 'O'), ('C. LeVert', 'IND', '50%'), ('K. Martin', 'IND', '50%'), ('T. Warren', 'IND', 'O'), ('P. Siakam', 'TOR', 'O'), ('Y. Watanabe', 'TOR', 'O'), ('S. Ojeleye', 'MIL', '75%'), ('B. Portis', 'MIL', '75%'), ('D. DiVincenzo', 'MIL', 'O'), ('J. Holiday', 'MIL', 'O'), ('B. Lopez', 'MIL', 'O'), ('T. Ariza', 'LAL', 'O'), ('T. Horton-Tucker', 'LAL', 'O'), ('K. Nunn', 'LAL', 'O'), ('C. Payne', 'PHX', 'O'), ('D. Saric', 'PHX', 'O'), ('D. Brooks', 'MEM', 'O'), ('Tony Snell', 'POR', 'O'), ('I. Okoro', 'CLE', '25%'), ('K. Johnson', 'LAC', '50%'), ('S. Ibaka', 'LAC', 'O'), ('K. Leonard', 'LAC', 'O'), ('M. Morris', 'LAC', 'O'), ('J. Preston', 'LAC', 'O')]""")
    else:
        (rw_all_starters, questionable_starters, questionable_non_starting) = roto_wire_scrape.scrape_lineups()


    rw_all_questionable_and_out = []

    for pl in rw_all_starters:
        if pl[2] != '':
            rw_all_questionable_and_out.append(pl)
        

    for pl in questionable_non_starting:
        if pl[2] != '':
            rw_all_questionable_and_out.append(pl)


    # Next - who is newly missing or newly added to the lineup??


    # for every playing starter, did you play the last game? 
    #   if not, this is excess money
    #   if yes,
    #       # did he start? yes - continue, no -flag new starter
    # for out, did you play the last game
    #   if not, continue
    #   if yes, this is missing money

    # for every quetionable – entertain both options
    all_teams = []
    for starter in rw_all_starters:
        team = starter[1]
        if not team in all_teams:
            all_teams.append(team)



    name_to_current_status = {}

    for team in all_teams:
        name_to_current_status[team] = {}
        RW_starters = [st for st in rw_all_starters if st[1] == team]

        RW_questionable_and_out = [st for st in rw_all_questionable_and_out if st[1] == team]

        result = box_scores.get_team(team)
        last_date = sorted(result[team].keys())[-1]
        
        last_starters = [a for a in result[team][last_date] if a[4] == 'Y']
        last_date_names = [a[1] for a in result[team][last_date]]
        assert len(last_starters) == 5


        for rw_out in RW_questionable_and_out:
            rw_out_name = rw_out[0]
            status = rw_out[2]
            
            # did this guy play the last game?
            matched_name = match_name(rw_out_name, last_date_names)

            if matched_name == None:
                continue
            else:
                last_game_row = [a for a in result[team][last_date] if a[1] == matched_name][0]
                minutes = last_game_row[5]
                fdp = last_game_row[9]
                status_str = "{} - {} - missing money {} min, {} fdp".format(rw_out_name, status, minutes, fdp)
                print(status_str)
                assert matched_name not in name_to_current_status[team]
                name_to_current_status[team][matched_name] = status_str

        for rw_starter in RW_starters:
            rw_starter_name = rw_starter[0]
            status = rw_starter[2]


            # did this guy play the last game?
            matched_name = match_name(rw_starter_name, last_date_names)
            # print(matched_name)

            if matched_name == None:
                # this is a new starter. He didn't play last game at all.
                # this is excess money and this team should be avoided
                status_str = "{} is a new starter {}".format(rw_starter_name, status)
                print(status_str)

                assert rw_starter_name not in name_to_current_status[team]
                name_to_current_status[team][rw_starter_name] = status_str
            else:
                # this guy played last game
                last_game_row = [a for a in result[team][last_date] if a[1] == matched_name][0]
                minutes = last_game_row[5]
                fdp = last_game_row[9]
                if last_game_row[4] == "N":
                    status_str = "{} off the bench - {} min, {} fdp".format(rw_starter_name, minutes, fdp)
                    print(status_str)
                    assert rw_starter_name not in name_to_current_status[team]
                    name_to_current_status[team][rw_starter_name] = status_str
                    # this is a new starter - worth considering
                    # a previous starter is obviously missing, but who?
                    pass
                else:
                    # he started last game
                    if status == "50%" or status == "75%" or status == "25%":
                        # keep an eye on this guy. if he ends up not playing we're missing money
                        # who's up next?????

                        assert matched_name in name_to_current_status[team]
                        # status_str = "{} is potentially missing {} - missing money".format(rw_starter_name, status)
                        # print(status_str)
                        # assert matched_name not in name_to_current_status
                        # name_to_current_status[matched_name] = status_str
                        # import pdb; pdb.set_trace()




        
    print(name_to_current_status)