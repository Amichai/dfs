import ast

player_val = """
Kevin Durant, 53
Giannis Antetokounmpo, 57
James Harden, 52
Khris Middleton, 37.5
Bruce Brown, 21.5
Jrue Holiday, 36.5
Anthony Davis, 47
Joe Harris, 21.5
Brook Lopez, 23
LaMarcus Aldridge, 23.5
Grayson Allen, 18
Stephen Curry, 52
LeBron James, 48.5
Draymond Green, 30.0
Russell Westbrook, 47.5
Andrew Wiggins, 28.0
Jordan Poole, 30
Carmelo Anthony, 20
Kevon Looney, 18.5
Kent Bazemore, 19
"""


scraped_players = ast.literal_eval(
    """[{'name': 'Giannis Antetokounmpo', 'val': 631.4447950139839, 'team': 'MIL', 'pos': 'PF/SF', 'cost': '11000'}, {'name': 'Kevin Durant', 'val': 369.54510908010207, 'team': 'BKN', 'pos': 'SF/PF', 'cost': '10800'}, {'name': 'James Harden', 'val': 347.4029229981242, 'team': 'BKN', 'pos': 'SG/PG', 'cost': '10600'}, {'name': 'LeBron James', 'val': 377.7282089080485, 'team': 'LAL', 'pos': 'SF/PF', 'cost': '10500'}, {'name': 'Anthony Davis', 'val': 267.0910282725898, 'team': 'LAL', 'pos': 'PF/C', 'cost': '10000'}, {'name': 'Stephen Curry', 'val': 449.30731175035265, 'team': 'GS', 'pos': 'PG', 'cost': '9800'}, {'name': 'Russell Westbrook', 'val': 411.61812641969937, 'team': 'LAL', 'pos': 'PG/SG', 'cost': '9500'}, {'name': 'Jrue Holiday', 'val': 165.67624828397234, 'team': 'MIL', 'pos': 'PG/SG', 'cost': '8500'}, {'name': 'Khris Middleton', 'val': 164.9167164114326, 'team': 'MIL', 'pos': 'SG/SF', 'cost': '7800'}, {'name': 'Andrew Wiggins', 'val': 30.533499879863214, 'team': 'GS', 'pos': 'SG/SF', 'cost': '7200'}, {'name': 'Draymond Green', 'val': 94.09632181546714, 'team': 'GS', 'pos': 'PF/C', 'cost': '7000'}, {'name': 'Brook Lopez', 'val': 31.955784108885002, 'team': 'MIL', 'pos': 'C', 'cost': '6000'}, {'name': 'Blake Griffin', 'val': 26.71925321079031, 'team': 'BKN', 'pos': 'PF/C', 'cost': '5200'}, {'name': 'Carmelo Anthony', 'val': 61.09406627999999, 'team': 'LAL', 'pos': 'SF/PF', 'cost': '5000'}, {'name': 'Bruce Brown Jr.', 'val': 36.453200674677916, 'team': 'BKN', 'pos': 'SG', 'cost': '4900'}, {'name': 'James Johnson', 'val': 1.47409489051968, 'team': 'BKN', 'pos': 'SF/PF', 'cost': '4900'}, {'name': 'Jordan Poole', 'val': 31.288026301737425, 'team': 'GS', 'pos': 'PG/SG', 'cost': '4900'}, {'name': 'Kent Bazemore', 'val': 34.299, 'team': 'LAL', 'pos': 'SF/SG', 'cost': '4700'}, {'name': 'Nicolas Claxton', 'val': 4.9875000049875, 'team': 'BKN', 'pos': 'C/PF', 'cost': '4600'}, {'name': 'Patty Mills', 'val': 13.205367068316, 'team': 'BKN', 'pos': 'SG/PG', 'cost': '4600'}, {'name': 'Otto Porter', 'val': 22.85364604149291, 'team': 'GS', 'pos': 'SF/PF', 'cost': '4400'}, {'name': 'Kendrick Nunn', 'val': 13.0624, 'team': 'LAL', 'pos': 'SG/PG', 'cost': '4400'}, {'name': 'Paul Millsap', 'val': 17.133899914330502, 'team': 'BKN', 'pos': 'PF/C', 'cost': '4300'}, {'name': 'Joe Harris', 'val': 31.378311880276286, 'team': 'BKN', 'pos': 'SG/SF', 'cost': '4300'}, {'name': 'Frank Mason III', 'val': 32.51819999999999, 'team': 'LAL', 'pos': 'PG', 'cost': '4200'}, {'name': 'Nemanja Bjelica', 'val': 9.510597239910021, 'team': 'GS', 'pos': 'PF', 'cost': '4100'}, {'name': 'LaMarcus Aldridge', 'val': 52.9958, 'team': 'BKN', 'pos': 'C/PF', 'cost': '4100'}, {'name': 'Malik Monk', 'val': 15.297893224971073, 'team': 'LAL', 'pos': 'SG', 'cost': '4000'}, {'name': 'Dwight Howard', 'val': 20.92294944890199, 'team': 'LAL', 'pos': 'C', 'cost': '4000'}, {'name': 'Damion Lee', 'val': 12.2192, 'team': 'GS', 'pos': 'SG/PG', 'cost': '4000'}, {'name': 'DeAndre Jordan', 'val': 0.3833128768536072, 'team': 'LAL', 'pos': 'C', 'cost': '4000'}, {'name': 'Rajon Rondo', 'val': 0.6641702118821154, 'team': 'LAL', 'pos': 'PG', 'cost': '4000'}, {'name': 'Andre Iguodala', 'val': 0.85008499149915, 'team': 'GS', 'pos': 'SF/SG', 'cost': '3900'}, {'name': 'Kevon Looney', 'val': 14.971950144782626, 'team': 'GS', 'pos': 'C/PF', 'cost': '3900'}, {'name': 'George Hill', 'val': 6.1764316912019295, 'team': 'MIL', 'pos': 'PG', 'cost': '3900'}, {'name': 'Pat Connaughton', 'val': 27.151658562600005, 'team': 'MIL', 'pos': 'SG/SF', 'cost': '3900'}, {'name': 'Grayson Allen', 'val': 12.27811032110175, 'team': 'MIL', 'pos': 'SG', 'cost': '3800'}, {'name': 'Moses Moody', 'val': 17.85206178231787, 'team': 'GS', 'pos': 'SG', 'cost': '3800'}, {'name': 'Gary Payton', 'val': 0.9987499999999999, 'team': 'GS', 'pos': 'SG', 'cost': '3600'}, {'name': 'Avery Bradley', 'val': 4.5359999773199995, 'team': 'GS', 'pos': 'SG', 'cost': '3600'}, {'name': 'Kessler Edwards', 'val': 1.91, 'team': 'BKN', 'pos': 'SF', 'cost': '3500'}, {'name': 'Thanasis Antetokounmpo', 'val': 10.9956, 'team': 'MIL', 'pos': 'SF/PF', 'cost': '3500'}, {'name': "Day'Ron Sharpe", 'val': 0.23, 'team': 'BKN', 'pos': 'PF', 'cost': '3500'}, {'name': 'Sandro Mamukelashvili', 'val': 8.98, 'team': 'MIL', 'pos': 'PF/C', 'cost': '3500'}, {'name': 'Jordan Nwora', 'val': 15.866038191899053, 'team': 'MIL', 'pos': 'PF', 'cost': '3500'}, {'name': 'Devontae Cacok', 'val': 1.3493623235370582, 'team': 'BKN', 'pos': 'PF/C', 'cost': '3500'}, {'name': 'Jordan Bell', 'val': 0.5139407349999999, 'team': 'GS', 'pos': 'PF', 'cost': '3500'}, {'name': 'Javin DeLaurier', 'val': 1, 'team': 'MIL', 'pos': 'PF', 'cost': '3500'}, {'name': 'Langston Galloway', 'val': 1.023, 'team': 'GS', 'pos': 'SG/SF', 'cost': '3500'}, {'name': 'Georgios Kalaitzakis', 'val': 1.62, 'team': 'MIL', 'pos': 'SF', 'cost': '3500'}, {'name': 'Jevon Carter', 'val': 1.7917895520525258, 'team': 'BKN', 'pos': 'PG/SG', 'cost': '3500'}, {'name': 'Tremont Waters', 'val': 0.324, 'team': 'MIL', 'pos': 'PG', 'cost': '3500'}, {'name': 'Chris Chiozza', 'val': 1.3499877999999998, 'team': 'GS', 'pos': 'PG', 'cost': '3500'}]
"""
)

player_to_val = {}

player_eval_lines = player_val.split('\n')
for line in player_eval_lines:
    parts = line.split(',')
    if len(parts) != 2:
        continue
    player_to_val[parts[0]] = float(parts[1])

to_remove = []

for player in scraped_players:
    if player["name"] in player_to_val:
        player["val"] = player_to_val[player["name"]]
    else:
        to_remove.append(player)
        print("Not found: {}".format(player))

for p in to_remove:
    scraped_players.remove(p)

print(scraped_players)