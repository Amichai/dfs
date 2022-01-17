

f = open("../master_scraper.log", "r")
lines = f.readlines()


name_to_stat_to_line = {}
#['INFO:Caesars:2022-01-16', '10:52:48', 'Jalen', 'Smith', 'Points', '6.5', '0.5199999999999999', '6.53\n']
#['INFO:Caesars:2022-01-16', '10:52:48', 'Jae', 'Crowder', 'Points', '+', 'Assists', '10.5', '0.5199999999999999', '10.53\n']

for line in lines:
    parts = line.split(' ')

    name = "{} {}".format(parts[2], parts[3])
    stat = " ".join(parts[4:-3])
    money_line = parts[-3]
    odds = parts[-2]

    if not name in name_to_stat_to_line:
        name_to_stat_to_line[name] = {}
    adjusted_line = float(money_line) + (float(odds) - 0.5) * (float(money_line) / 2.0)
    # adjusted_line = float(money_line) + (float(odds) - 0.5) * 1.5


    if stat in name_to_stat_to_line[name] and name_to_stat_to_line[name][stat][0] != money_line:
        a = round(name_to_stat_to_line[name][stat][2], 2)
        b = round(adjusted_line, 2)
        print("{} {} = {}".format(a, b, round(abs(a - b), 5)))
        # __import__('pdb').set_trace()
        pass
    
    name_to_stat_to_line[name][stat] = (money_line, odds, adjusted_line)