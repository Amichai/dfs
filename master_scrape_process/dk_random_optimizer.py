import random
from types import resolve_bases
from bs4 import BeautifulStoneSoup
import requests
import time

class Player:
    def __init__(self, name, position, cost, team, value, game_start_slot=0, matchup=''):
        self.name = name
        self.position = position
        self.cost = float(cost)
        self.team = team
        self.value = float(value)
        self.value_per_dollar = self.value * 100 / self.cost
        self.game_start_slot = game_start_slot
        self.matchup = matchup

    def __repr__(self):
        # return "{} - {} - {} - {} - {} - {}".format(self.name, self.position, self.cost, self.team, self.value, self.value_per_dollar)
        return self.name

class Roster:
    def __init__(self, players):
        self.players = players
        self.cost = sum([float(p.cost) for p in self.players])
        self.value = sum([float(p.value) for p in self.players])
        self.locked_indices = []
        self.is_valid = len(players) == len(set(p.name for p in players))

    def __repr__(self):
        return ",".join([p.name for p in self.players]) + " {} - {}".format(self.cost, self.value)

    def remainingFunds(self, max_cost):
        return max_cost - self.cost

    def relpace(self, player, idx):
        self.players[idx] = player
        self.cost = sum([float(p.cost) for p in self.players])
        self.value = sum([float(p.value) for p in self.players])

    def atPosition(self, position):
        return [p for p in self.players if p.position == position]

    def getIds(self, id_mapping):
        ids = []
        for p in self.players:
            id = id_mapping[p.name]
            ids.append(id)

        ids.reverse()
        return ",".join(ids)


def random_element(arr):
    idx = random.randint(0, len(arr) - 1)
    return arr[idx]


def select_better_player(players, max_cost, excluding, initial_value):
    better_players = []
    for p in players:
        if p.name in excluding:
            continue
        if p.cost <= max_cost and p.value > initial_value:
            better_players.append(p)

    if len(better_players) == 0:
        return None

    return random_element(better_players)

def optimize_roster(roster, by_position):
    initial_cost = roster.cost

    no_improvement_count = 0
    if initial_cost <= 50000:
        # pick a random player
        # swap that player for the best player we can afford that brings more value
        while True:
            swap_idx = random.randint(0, len(roster.players) - 1)
            
            if swap_idx in roster.locked_indices:
                continue

            try:
                to_swap = roster.players[swap_idx]
            except:
                import pdb; pdb.set_trace()
            position = to_swap.position

            excluding = [p.name for p in roster.players]

            replacement = select_better_player(by_position[position], roster.remainingFunds() + to_swap.cost, excluding, to_swap.value)

            if replacement == None or to_swap.name == replacement.name:
                no_improvement_count += 1
            else:
                no_improvement_count = 0
                roster.relpace(replacement, swap_idx)

            if no_improvement_count > 20:
                return roster


    print(roster)
    assert False

def optimize_roster_dk_showdown(all_players):
    best_val = 0
    best_roster = None

    class TempRoster:
        def __init__(self, players):
            self.players = players

    player_ct = len(all_players)
    for i1 in range(player_ct):
        p1 = all_players[i1]

        for i2 in range(player_ct):
            if i2 == i1:
                continue

            p2 = all_players[i2]

            for i3 in range(player_ct):
                if i3 <= i2 or i3 == i1:
                    continue

                p3 = all_players[i3]

                for i4 in range(player_ct):
                    if i4 <= i3 or i4 == i1:
                        continue

                    p4 = all_players[i4]

                    for i5 in range(player_ct):
                        if i5 <= i4 or i5 == i1:
                            continue
                        p5 = all_players[i5]

                        for i6 in range(player_ct):
                            if i6 <= i5 or i5 == i1:
                                continue

                            p6 = all_players[i6]

                            roster = [p1, p2, p3, p4, p5, p6]
                            total_cost = 0
                            total_value = 0
                            for i in range(6):
                                if i == 0:
                                    total_cost += roster[0].cost * 1.5
                                    total_value += roster[0].value * 1.5
                                else:
                                    total_cost += roster[i].cost
                                    total_value += roster[i].value



                            if total_cost >= 50000:
                                continue

                            if total_value > best_val:
                                best_val = total_value
                                best_roster = roster
                                print(roster)
                                print("Cost: {}, val: {}".format(total_cost, total_value))


    return TempRoster(best_roster)


def optimize_roster_for_sport(by_position, sport, iter_count = 120000):
    best_roster = None
    best_roster_val = 0

    random.seed(time.time())
    
    for i in range(iter_count):
        if i % 50000 == 0:
            print(i)
        to_remove = None
        if best_roster != None:
            to_remove = random_element(best_roster.players)

        by_position_copied = {}
        for pos, players in by_position.items():
            if to_remove in players:
                players_new = list(players)

                players_new.remove(to_remove)
                by_position_copied[pos] = players_new
            else:
                by_position_copied[pos] = players

        if to_remove == None:
            by_position_copied = by_position

        random_lineup = None
        if sport == "MLB":
            random_lineup = build_random_MLB_line_up(by_position_copied)
        elif sport == "EL":
            random_lineup = build_random_EL_line_up(by_position_copied)
        elif sport == "EPL":
            random_lineup = build_random_EPL_line_up(by_position_copied)
        elif sport == "PGA":
            random_lineup = build_random_PGA_line_up(by_position_copied)
            pass
            
        if random_lineup.cost > 50000 or not random_lineup.is_valid:
            continue


        result = optimize_roster(random_lineup, by_position_copied)
        if result.value > best_roster_val:
            best_roster = result
            if result.value >= best_roster_val:
                best_roster_val = result.value

            all_names = [a.name for a in best_roster.players]
            all_names_sorted = sorted(all_names)
            roster_key = ",".join(all_names_sorted)
            # if roster_count > 50:
            #     break

            #TODO: PUT THIS BACK IN AND TROUBLESHOOT
            # best_roster = optimize_roster_by_start_time(by_position_copied, best_roster)
            # later games get laters slots
            # earlier games get earlier slots
            print("B: {}\n".format(best_roster))

    return best_roster

all_positions = ["PG", "SG", "SF", "PF", "C", "G", "F", "UTIL"]


def build_random_line_up(by_position):
    to_return = []
    for pos in all_positions:
        pass
        to_return.append(random_element(by_position[pos]))

    return Roster(to_return)


mlb_positions = ["P", "P", "C", "1B", "2B", "3B", "SS", "OF", "OF", "OF"]

def build_random_MLB_line_up(by_position):
    to_return = []
    for pos in mlb_positions:
        to_return.append(random_element(by_position[pos]))

    return Roster(to_return)


el_positions = ["G", "G", "F", "F", "F", "UTIL"]

def build_random_EL_line_up(by_position):
    to_return = []
    for pos in el_positions:
        to_return.append(random_element(by_position[pos]))

    return Roster(to_return)


epl_positions = ["F", "F", "M", "M", "D", "D", "GK", "UTIL"]
def build_random_EPL_line_up(by_position):
    to_return = []
    for pos in epl_positions:
        to_return.append(random_element(by_position[pos]))

    return Roster(to_return)

PGA_positions = ["G", "G", "G", "G", "G", "G",]
def build_random_PGA_line_up(by_position):
    to_return = []
    for pos in PGA_positions:
        to_return.append(random_element(by_position[pos]))

    return Roster(to_return)




def optimize_roster_by_start_time(by_position, roster):
    player_names = []

    for player in roster.players:
        player_names.append(player.name)


    max_slot_idx = float(max(p.game_start_slot for p in roster.players))

    by_position_filtered = {}
    for pos, players in by_position.items():
        if not pos in by_position_filtered:
            by_position_filtered[pos] = []
        for player in players:
            if player.name in player_names:
                slot_idx = player.game_start_slot
                slot_pos = slot_idx / max_slot_idx

                position_idx = all_positions.index(pos)
                pos_pos = position_idx / 7.0

                pos_diff = abs(pos_pos - slot_pos)

                new_player = Player(player.name, pos, player.cost, player.team, player.value + (1.0 / (pos_diff + 1)), player.game_start_slot)
                by_position_filtered[pos].append(new_player)
                
            pass
    
    best_roster = roster
    best_val = 0
    for i in range(10000):
        random_lineup = build_random_line_up(by_position_filtered)
        if random_lineup.is_valid:
            result = optimize_roster(random_lineup, by_position_filtered)

            if result.value > best_val:
                best_val = result.value
                best_roster = result
            
    return best_roster


def generate_single_roster(by_position, players_to_exclude):
    # names_to_exclude = [p.name for p in players_to_exclude]
    names_to_exclude = players_to_exclude
    by_position_exclusive = {}
    for pos, players in by_position.items():
        by_position_exclusive[pos] = []
        for pl in players:
            if pl.name in names_to_exclude:
                continue

            by_position_exclusive[pos].append(pl)
    by_position = by_position_exclusive
    best_roster = None
    best_roster_val = 0

    random.seed(time.time())
    
    for i in range(100000):
        if i % 50000 == 0:
            print(i)
        to_remove = None
        if best_roster != None:
            to_remove = random_element(best_roster.players)

        by_position_copied = {}
        for pos, players in by_position.items():
            if to_remove in players:
                players_new = list(players)

                players_new.remove(to_remove)
                by_position_copied[pos] = players_new
            else:
                by_position_copied[pos] = players

        if to_remove == None:
            by_position_copied = by_position

        random_lineup = build_random_line_up(by_position_copied)
        if random_lineup.cost > 50000 or not random_lineup.is_valid:
            continue


        result = optimize_roster(random_lineup, by_position_copied)
        if result.value > best_roster_val:
            best_roster = result
            if result.value >= best_roster_val:
                best_roster_val = result.value

            all_names = [a.name for a in best_roster.players]
            all_names_sorted = sorted(all_names)
            roster_key = ",".join(all_names_sorted)
            # if roster_count > 50:
            #     break

            #TODO: PUT THIS BACK IN AND TROUBLESHOOT
            # best_roster = optimize_roster_by_start_time(by_position_copied, best_roster)
            # later games get laters slots
            # earlier games get earlier slots
            print("B: {}\n".format(best_roster))

    return best_roster


def modify_existing_roster(by_position, roster_str, locked_teams):
    roster_names = roster_str.split(',')
    roster_players = []

    assert len(roster_names) == len(all_positions)
    locked_indices = []

    player_idx = 0
    for position in all_positions:
        players = by_position[position]
        for player in players:
            if player.name == roster_names[player_idx]:
                roster_players.append(player)

                if player.team in locked_teams:
                    locked_indices.append(player_idx)

                # continue

        player_idx += 1

    print(roster_str)
    print(roster_players)
    assert len(roster_players) == len(all_positions)
    

    # copy the original roster
    # best_result = None
    best_val = 0
    for _ in range(1000000):
        for i in range(len(roster_players)):
            pos = all_positions[i]
            if i in locked_indices:
                continue

        
            # roster_players[i] = random_element(by_position[pos])
            roster_players[i] = Player("--", pos, 2900, "", 0)


        # import pdb; pdb.set_trace()
        roster = Roster(roster_players)
        roster.locked_indices = locked_indices
        if roster.cost > 50000:
            continue

        result = optimize_roster(roster, by_position)
        if result.value > best_val:
            best_val = result.value

            result = optimize_roster_by_start_time(by_position, result)
            print(result)



def generate_unique_rosters(by_position, ct):
    players_to_exclude = []
    resovled_rosters =[]
    for i in range(ct):
        print("{}---------------{}".format(i + 1, i + 1))
        best_roster1 = generate_single_roster(by_position, players_to_exclude)
        players_to_exclude += best_roster1.players

        resovled_rosters.append(best_roster1)
    
    return resovled_rosters


# # actual_value_file_path = "contest-standings-117244352.csv"
# # 11/31
# # actual_value_file_path = "contest-standings-117036435_10_30.csv"
# actual_value_file_path = "contest-standings-116961696_10_29.csv"

def generate_rosters(by_position, evaluator):
    seen_rosters = []

    best_roster = None
    best_roster_val = 0

    roster_count = 0

    random.seed(time.time())
    for i in range(10000000):
        to_remove = None
        if best_roster != None:
            to_remove = random_element(best_roster.players)

        by_position_copied = {}
        for pos, players in by_position.items():
            if to_remove in players:
                players_new = list(players)

                players_new.remove(to_remove)
                by_position_copied[pos] = players_new
            else:
                by_position_copied[pos] = players
            pass

        if to_remove == None:
            by_position_copied = by_position

        random_lineup = build_random_line_up(by_position_copied)
        if random_lineup.cost > 50000 or not random_lineup.is_valid:
            continue


        result = optimize_roster(random_lineup, by_position_copied)
        if result.value >= best_roster_val - 0.5:
        # if result.cost >= min_roster_cost:
        # if result.value >= 56800.0:
            best_roster = result
            if result.value >= best_roster_val:
                best_roster_val = result.value

            all_names = [a.name for a in best_roster.players]
            all_names_sorted = sorted(all_names)
            roster_key = ",".join(all_names_sorted)
            if roster_key in seen_rosters:
                continue

            seen_rosters.append(roster_key)
            if evaluator != None:
                evaluator.Eval(result)

            # if roster_count > 50:
            #     break
            print(best_roster)
            roster_count += 1

class RosterEvaluator:
    def __init__(self, buy_in, result_path, payouts):
        self.bankroll = 0
        self.roster_count = 0
        self.buy_in = buy_in

        actual_value_file = open(result_path, "r")
        lines = actual_value_file.readlines()

        self.name_to_actual_value = {}

        for line in lines[1:]:
            parts = line.split(',')
            name = parts[7]
            if name == '':
                continue

            self.name_to_actual_value[name] = float(parts[-1].strip())

        # for name, actual_val in self.name_to_actual_value.items():
        #     print("{} - {}".format(name, actual_val))

        self.points_to_payout = []

        payout_idx = -1
        all_lines_copied = lines[1:]
        all_lines_copied.reverse()

        for line in all_lines_copied:
            parts = line.split(',')
            # print(parts)
            rank = int(parts[0])
            points = float(parts[4])

            target_rank = payouts[payout_idx][1]
            payout_val = payouts[payout_idx][2]

            if rank <= target_rank:
                self.points_to_payout.append((points, payout_val))
                payout_idx -= 1

        self.points_to_payout
        print(self.points_to_payout)


    def Eval(self, roster):
        self.bankroll -= self.buy_in
        actual_val = 0
        for pl in roster.players:
            name = pl.name.strip()
            if name == 'Aaaron Holiday':
                name = 'Aaron Holiday'


            if not name in self.name_to_actual_value:
                import pdb; pdb.set_trace()
            actual_val += self.name_to_actual_value[name]

            if actual_val == 0:
                print(name)
                assert False

        highest_payout = 0
        for (points, payout) in self.points_to_payout:
            if actual_val > points:
                highest_payout = float(payout)


        self.bankroll += highest_payout
        self.roster_count += 1
        print("{} | {} - {} = {}".format(self.roster_count, self.bankroll, actual_val, round(self.bankroll / self.roster_count, 2)))


def scrape_money_lines(contest_id):
    headers = {
        'authority': 'api.draftkings.com',
        'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36',
        'sec-ch-ua-platform': '"macOS"',
        'accept': '*/*',
        'origin': 'https://www.draftkings.com',
        'sec-fetch-site': 'same-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.draftkings.com/',
        'accept-language': 'en-US,en;q=0.9,he;q=0.8',
        'cookie': 'site=US-DK; LID=1; notice_behavior=none; VIDN=19272979; SINFN=PID=&AOID=&PUID=1557429&SSEG=&GLI=0&LID=1&site=US-DK; __zlcmid=16ekQ3hzJJO44E9; jws_sb=eyJhbGciOiJodHRwOi8vd3d3LnczLm9yZy8yMDAxLzA0L3htbGRzaWctbW9yZSNobWFjLXNoYTI1NiIsImtpZCI6ImdZWkxtVTVLS1FtSGpsUWpURE95NkE0Y1cvNEdlVy9Xb3B6NGJpOEtvMFU9IiwidHlwIjoiSldUIiwidmVyc2lvbiI6MX0.eyJzZSI6IlVTLVNCIiwicHNDbGllbnRLZXkiOiI0ZDg0NDI3NC1lZmZlLTQwYmEtYWY3ZC02ZDEyNTRmYTY3ZDEiLCJuYmYiOjE2MzUzNjY5OTMsImV4cCI6MTYzNTM2NzM1MywiaXNzIjoidXJuOmRrL2tyb25vcyIsImF1ZCI6InVybjpkayJ9.ZxF_CYIOWAh0DHSwIoxq2z1GnNqgOLfMw4POpW_ILD0; uk=1; _csrf=52af0842-89df-4e47-9551-12460beae2cd; ss-id=LSCZ0vLI6uLN4lizbODz; ss-pid=3gjxHW6pLlgyol1xx364; mlc=true; SIDN=23964716030; _abck=96613027ED2769B98B6B0C9E0475952F~0~YAAQqJcwFyHQ3t58AQAA0GQa5gaxVjgwK4QOCWlCsfOzfUY6aFU8RiALNH0V+1f/lSaasJOkDcCU7rtxPmDvmdGHhk/P6OLSVxHkp28lfO+uveNJpaTlegMQQuY2Hl02lwh6it1uRDeTuKhNDoBBVceF3CiZ/qiHhPBsnHTvv2caPA8ZfFP8qwN57Qfagtoic0vgPu1Wm9MIb2EqRcM2Jt4chGYMH/Yi8QigGfzBuBcWbuQaVOG/t/i0myLJTr+foyTEZx4uXRTdrV7AAnVnjYTj/yy78RTCv5rNBUDkWSZpRyV9kIJ//aJ4l+/6ApZ/iXprEhDy7PgvOZ0Cpn6r1HeU0RWwoE4OzCkPQMxo27jIcMYowR1BFf7voG7BTENpKtFtDtHuK9DPZqk2QdfJPE2nqCG4cXgQDpucnA==~-1~-1~-1; ak_bmsc=D2AC655E459098E600215A44F0667F61~000000000000000000000000000000~YAAQqJcwFyLQ3t58AQAA0GQa5g12iL2B+cDGcD9uWxyQwo2Fqxzzi4e9UEnQ4/qZ9F5EBtpuQlWhccC1Z10bKlf0FtnH39eriWTVACJ69H2VnC2bqNrFUbbzd4udhNlTe7bAFUsdufTyazUIss6HiAZjxmkXHoP36KN3V1/0O9to4tlYsR9sPdIiKMyCyO+NksmtVtG6fRBnbu1HnPHfnv+jVnX7K0NqGxVpPTPMccJvXjnNmQa2rEC0natAZk3pPT5lytk8HqbUn1ibbKnzAx/P0zjApDbdNuk/nrzFnnFut/x4IZmXO1OdTBzCO83dExU0LVfiGK8wdT4KNBFtc1GvK9l4wvLRs2f118zcDNv4UE0K0J0jftKzntTVuoHnUTzg5x5xAo7BKTzmais=; bm_sz=3495CE652A975A8E406145EDAA09C975~YAAQqJcwFyPQ3t58AQAA0GQa5g0nMHLVpas7pF/+3u8R+pH6ou+U4sffsppSHLNTwVkBn8sYXn5NzucCnAsXxqzmZ7QxFZYS1YsNpZLNrsj40a0o5SNCZtkZKXCPmtFzb3b6rVJVfiXJnWkXvP3fKw5IO0h5dVlcfjqsU4JiSdx9SPXtANmhMReF4zxALUdi6RGK66O3bhE47Ds4E8fDwrDPzixCtz3QvzWU4HaGbtW3Dxbsad1FSNM2f02BHlbf8tpxaYV86yD3/6bRDup/uyGg1TZCFWqc/zXP9p3YUVxwCZ4zcLnI~3622456~3425845; gch=eyJJZCI6NTMxODAxMzc4MiwiUmVzdHJpY3RlZCI6ZmFsc2UsIlNvdXJjZSI6NiwiU3RhdHVzIjoxLCJFeHBpcmVzIjoiMjAyMS0xMS0wM1QxNTowMToxMS4xMzM2MzYxWiIsIkdlb2xvY2F0ZUluU2Vjb25kcyI6MzYwMCwiTG9jYXRpb24iOiJVUy1OWSIsIkhhc2giOiJYazlhUkZkWnFNOW9WcUdubGdrYi92S2JFem5CTmJjN3gxZ1o0L3FOTE1vPSIsIlNpdGVFeHBlcmllbmNlIjoiVVMtREsiLCJCdWZmZXJUaW1lU2Vjb25kcyI6MzAsIklwQWRkcmVzcyI6IjEwOC40MS4xMDguMTU3IiwiQ29ubmVjdGlvblR5cGUiOm51bGx9; STIDN=eyJDIjo3ODQyMTY1MTUsIlMiOjIzOTY0NzE2MDMwLCJTUyI6MjQ5Njc2MDU3NjQsIlYiOjE5MjcyOTc5LCJMIjoxLCJFIjoiMjAyMS0xMS0wM1QxNDo0MDoyMS4wMTkyMjE1WiIsIlNFIjoiVVMtREsiLCJVQSI6IlFzUzJGbTFpQ1MyQnNNQ01vaHZ3bGVUeUFOQTJFcUpGa1JvUU1maExER009IiwiREsiOiJhODlkZDk3ZC1hYjcxLTRiMTYtOGY5NS04ZDlkMTQ4MmViYWYiLCJESSI6IjYwYzA2OGNmLTRkMDYtNGIwZS1iZThjLWNhYWM1ZGI1MGQzMCIsIkREIjo3NTY4NTc5OTk2fQ==; STH=9e13f25f1c08b02405d5e398166fd49a2471c58fed5846ae09af771d9e52fc3e; SSIDN=24967605764; SN=784216515; EXC=24967605764:73; jwe=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsInZlcnNpb24iOiIxIn0.eyJ1bmlxdWVfbmFtZSI6ImFtbDEiLCJ1ayI6Ijk1OWJkMzczLTU5MjctNDhmNy1hMTJjLWM1NTQ5Nzc1MWFmNCIsInJvbGUiOiJOb3JtYWwiLCJlbWFpbCI6ImFtaWNoYWltbGV2eUBnbWFpbC5jb20iLCJyYWZpZCI6IiIsInZpZCI6IjE5MjcyOTc5IiwibGlkIjoiMSIsImppZCI6IjExMTU5ODEzOTY5IiwiamtleSI6ImN1cnJlbnQiLCJmdGRiZSI6IkZhbHNlIiwiZ2VvIjoiVVMtTlkiLCJmdnMiOiIwIiwiY2RhdGUiOiIyMDIxLTEwLTI4IDIxOjIzOjUzWiIsIml2IjoiUUQzOS9GU3UzbTNQQi83QkpoR0ZrQT09IiwiZXVpZCI6Im5iOTJIaWpvWWJFYmNMUDBvZ3hOc3c9PSIsInV2cyI6WyIwLTEiLCIwLTciLCIwLTgiXSwiREtQLURlbnlMZWFndWUiOiIxMDAsOTgiLCJES1AtRGVueVBhaWRMZWFndWUiOiI3OSw4NCw4OCw4OSw5NyIsIkRLUC1EZW55UGFpZFNwb3J0IjoiMTksMjAsMjIsMjMsMjQsNSw2IiwiREtQLURlbnlTcG9ydCI6IjI1LDI2IiwiREtQLU1heE11bHRpRW50cnlQZXJjZW50YWdlIjoiMC4wMyIsIkRLUC1EZW55R2FtZVR5cGUiOiIxMTEsMTYxIiwiREtQLURlbnlQYWlkR2FtZVR5cGUiOiIxMzksMTQwLDE1MywxNTQsOTAsOTIsOTMiLCJES1AtRGVueUJlZ2lubmVyQ29udGVzdHMiOiJ0cnVlIiwiREtQLVNob3dTcG9ydHNib29rIjoidHJ1ZSIsIkRLUC1WaWV3T2RkcyI6InRydWUiLCJES1AtRGVtb0Nhc2lubyI6InRydWUiLCJES1AtVmlld0RmcyI6InRydWUiLCJES1AtU2hvd1Nwb3J0c2Jvb2tDcm9zc1NlbGwiOiJ0cnVlIiwic3hwIjoiVVMtREsiLCJhdXRoIjoiODFiYzI2MWItMmJmZi00YjYzLWJjYjktYWRkMDBmYWE1MTgwIiwibHQiOiJkcmFmdGtpbmdzIiwic2J0IjoiMjg0NjQ5MjYiLCJuYmYiOjE2MzU5NDkyNDMsImV4cCI6MTYzNTk0OTU0MywiaXNzIjoidXJuOmRrL2NlcmJlcnVzIiwiYXVkIjoidXJuOmRrIn0.EwcvrUUsSUlYpYYCCdu-JGc6rVY46qgvVYehNyWxnEc; iv=WiAmQNtGUbpb9Xxzb6MjfS+zLaIU8vQuDy4UbaccpWI=; hgg=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ2aWQiOiIxOTI3Mjk3OSIsImRrZS02MCI6IjI4NSIsImRrZS0xMjYiOiIzNzQiLCJka2UtMTQ0IjoiNDMxIiwiZGtlLTE0OSI6IjQ1NCIsImRrZS0xNTAiOiI1NjciLCJka2UtMTUxIjoiNDU3IiwiZGtlLTE1MiI6IjQ1OCIsImRrZS0xNTMiOiI0NTkiLCJka2UtMTU0IjoiNDYwIiwiZGtlLTE1NSI6IjQ2MSIsImRrZS0xNTYiOiI0NjIiLCJka2UtMTc5IjoiNTY5IiwiZGtlLTIwNCI6IjcxMCIsImRrZS0yMTkiOiIyMjQ2IiwiZGtlLTIyMSI6IjgxMyIsImRraC0yMjkiOiJJbE5oQzA2UyIsImRrZS0yMjkiOiIwIiwiZGtlLTIzMCI6Ijg1NyIsImRrZS0yODgiOiIxMTI4IiwiZGtlLTMwMCI6IjExODgiLCJka2UtMzE4IjoiMTI2MSIsImRrZS0zNDUiOiIxMzUzIiwiZGtlLTM0NiI6IjEzNTYiLCJka2UtMzk0IjoiMTU1MiIsImRrZS00MDgiOiIxNjEwIiwiZGtlLTQxNiI6IjE2NDkiLCJka2UtNDE4IjoiMTY1MSIsImRrZS00MTkiOiIxNjUyIiwiZGtlLTQyMCI6IjE2NTMiLCJka2UtNDIxIjoiMTY1NCIsImRrZS00MjIiOiIxNjU1IiwiZGtlLTQyOSI6IjE3MDUiLCJka2UtNTUwIjoiMjMxOCIsImRrZS01NjciOiIyMzg3IiwiZGtlLTU2OCI6IjIzOTAiLCJka2gtNTg4IjoieG9IUWhoWmciLCJka2UtNTg4IjoiMCIsImRrZS02MzYiOiIyNjkxIiwiZGtlLTcwMCI6IjI5OTIiLCJka2UtNzM5IjoiMzE0MCIsImRrZS03NTciOiIzMjEyIiwiZGtoLTc2OCI6IlVaR2Mwckh4IiwiZGtlLTc2OCI6IjAiLCJka2UtNzkwIjoiMzM0OCIsImRrZS03OTQiOiIzMzY0IiwiZGtlLTgwNCI6IjM0MTIiLCJka2UtODA2IjoiMzQyNiIsImRrZS04MDciOiIzNDM3IiwiZGtlLTgyNCI6IjM1MTEiLCJka2UtODI1IjoiMzUxNCIsImRrZS04MzQiOiIzNTU3IiwiZGtlLTgzNiI6IjM1NzAiLCJka2UtODY1IjoiMzY5NSIsImRrZS04NzMiOiIzNzQxIiwiZGtlLTg3NiI6IjM3NTIiLCJka2UtODc3IjoiMzc1NiIsImRrZS04ODAiOiIzNzY2IiwiZGtlLTg4MSI6IjM3NzAiLCJka2UtODgyIjoiMzc3MyIsImRraC04ODciOiJxOHpHY1FHbCIsImRrcy04ODciOiIwIiwiZGtoLTg5NSI6IjJ6MERZU0MyIiwiZGtlLTg5NSI6IjAiLCJka2UtOTAzIjoiMzg0OCIsImRrZS05MDQiOiIzODUyIiwiZGtlLTkwNyI6IjM4NjMiLCJka2UtOTE3IjoiMzkxMyIsImRrZS05MTgiOiIzOTE3IiwiZGtlLTkyNCI6IjM5NDIiLCJka2UtOTM4IjoiNDAwNCIsImRrZS05NDciOiI0MDQyIiwiZGtlLTk0OCI6IjQwNDUiLCJka2UtOTQ5IjoiNDA0OSIsImRrZS05NzUiOiI0MTY4IiwiZGtlLTk3NiI6IjQxNzEiLCJka2UtOTgwIjoiNDE4NyIsImRrZS05ODciOiI0MjE2IiwiZGtlLTk4OCI6IjQyMjEiLCJka2UtOTkxIjoiNDIzNCIsImRrZS05OTMiOiI0MjQwIiwiZGtlLTk5NiI6IjQyNTAiLCJka2UtOTk3IjoiNDI1MyIsImRrZS0xMDAxIjoiNDI3MyIsImRrZS0xMDAyIjoiNDI3NiIsImRrZS0xMDAzIjoiNDI3OSIsImRraC0xMDA1IjoiZHJZbmhVRTEiLCJka2UtMTAwNSI6IjAiLCJka2UtMTAwOCI6IjQzMDUiLCJka2UtMTAxOCI6IjQzNTAiLCJka2UtMTA1MSI6IjQ0NzkiLCJka2UtMTA1NyI6IjQ1MDUiLCJka2UtMTAyNSI6IjQzODYiLCJka2UtMTA3NSI6IjQ1NTciLCJka2UtMTA3NiI6IjQ1NjUiLCJuYmYiOjE2MzU5NDkyNDQsImV4cCI6MTYzNTk0OTU0NCwiaWF0IjoxNjM1OTQ5MjQ0LCJpc3MiOiJkayJ9.ep33k8SSqFOd0vE1G7Gr2U4XP3NJK3npiaO5b0UwJV8; STE="2021-11-03T14:54:21.9570395Z"; bm_sv=26802922AD2337CF4C40EFF9DF1ECBB7~ustf1djE3Py8n/OsuIqzEY2nL3wLLr9gz9Pq1J2r9DV4gUE9EYXSKEjMGfT/m7CW/pqmn48cxSpof4MrT6qa0HVdciI1BIghrjLOWX5FKHyXyT+rgnCa1FtyvwSPYGQcotJKxXf3CcJEdx/GIEb84C20UU4ftsv7xKvYjZmexq0=',
        'sec-gpc': '1',
    }

    params = (
        ('format', 'json'),
    )

    response = requests.get('https://api.draftkings.com/contests/v1/contests/{}'.format(contest_id), headers=headers, params=params)

    payouts = []
    for payout in response.json()['contestDetail']['payoutSummary']:
        min_position = payout["minPosition"]
        max_position = payout["maxPosition"]
        result = float(payout['tierPayoutDescriptions']['Cash'].strip("$").replace(",", ""))
        payouts.append((min_position, max_position, result))
    
    return payouts

if __name__ == "__main__":
    file = open("optimizer_player_pool.txt")
    lines = file.readlines()

    by_positino = {}
    for line in lines:
        pass
    pass