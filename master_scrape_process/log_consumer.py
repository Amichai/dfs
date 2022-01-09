

log_path = "money_line_scrape_12_31_2021.txt"




class DynamoDBTableData:
    def __init__(self, args):
        pass


player_projections = DynamoDBTableData()
big_moves = DynamoDBTableData()
open_arbitrage = DynamoDBTableData()

def consume(line):
    parts = line.split("|")
    time = parts[0]
    site = parts[1]
    name = parts[2]
    team = parts[3]
    stat = parts[4]
    value = parts[5]
    pass

log_file = open(log_path, "r")
log_lines = log_file.readlines()
for line in log_lines[:30]:
    consume(line)
    print(line)



# three tables:
# player projections [daily min and max]
# biggest movers
# open arbitrage [PP, Underdog, Thrive Fantasy]


# read the remote state
# maintain local state
# diff each line against local state
# write to remote if necessary
