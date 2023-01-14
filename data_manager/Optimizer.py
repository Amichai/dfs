import random
import time

import utils

def random_element(arr):
  idx = random.randint(0, len(arr) - 1)
  val = arr[idx]
  return val

class Optimizer:
  def __init__(self, max_cost, positions_to_fill):
      self.max_cost = max_cost
      self.positions_to_fill = positions_to_fill

      self.pos_to_ct = {}
      self.positions_to_fill_condensed = []
      for position in self.positions_to_fill:
        if not position in self.pos_to_ct:
          self.pos_to_ct[position] = 1
          self.positions_to_fill_condensed.append(position)
        else:
          self.pos_to_ct[position] += 1
        pass


  def select_better_player(self, players, max_cost, excluding, initial_value):
      better_players = []
      for p in players:
          if p.name in excluding:
              continue
          if p.cost <= max_cost and p.value > initial_value:
              better_players.append(p)

      if len(better_players) == 0:
          return None

      return random_element(better_players)


  def optimize_roster(self, roster, by_position):
      initial_cost = roster.cost

      no_improvement_count = 0
      if initial_cost <= self.max_cost:
          # pick a random player
          # swap that player for the best player we can afford that brings more value
          while True:
              swap_idx = random.randint(0, len(roster.players) - 1)
              
              if swap_idx in roster.locked_indices:
                  continue
                
              to_swap = roster.players[swap_idx]
              position = self.positions_to_fill[swap_idx]
              excluding = [p.name for p in roster.players]

              replacement = self.select_better_player(by_position[position], roster.remaining_funds(self.max_cost) + to_swap.cost, excluding, to_swap.value)
              if replacement == None or to_swap.name == replacement.name:
                no_improvement_count += 1
              else:
                no_improvement_count = 0
                roster.replace(replacement, swap_idx)
                if len(roster.players) != len(set([a.name for a in roster.players])):
                  __import__('pdb').set_trace()

              if no_improvement_count > 20:
                  return roster

      print(roster)
      assert False

  def random_lineup(self, by_position):
    return self.build_random_line_up(by_position)

    
    # to_return = []
    # taken_names = []
    # for pos in self.positions_to_fill:
    #   element = random_element(by_position[pos], taken_names)
    #   taken_names.append(element.name)
    #   to_return.append(element)

    # if len(to_return) != len(set(p.name for p in to_return)):
    #   __import__('pdb').set_trace()

    # to_return.reverse()
    # return utils.Roster(to_return)

  def random_elements(self, arr, count, exclude=[]):
      if count > len(arr):
          assert False
      if count == len(arr):
        if arr[0].name in exclude:
          return None
        return arr

      to_return = []
      loop_counter = 0
      while True:
        loop_counter += 1
        if loop_counter >= 100:
          return None
        idx = random.randint(0, len(arr) - 1)
        val = arr[idx]
        if val.name in exclude:
          continue

        if not val in to_return:
            to_return.append(val)

        if len(to_return) == count:
            break

      return to_return
    
  def build_random_line_up(self, by_position):
    to_return = []
    for pos in self.positions_to_fill_condensed:
      ct = self.pos_to_ct[pos]
      result = self.random_elements(by_position[pos], ct, [a.name for a in to_return])

      if result == None:
        return None

      to_return += result

      if len(to_return) != len(set([a.name for a in to_return])):
        __import__('pdb').set_trace()

    return utils.Roster(to_return)


  def optimize(self, by_position, iter_count = 600000, lineup_validator = None, seed_roster = None):
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

          random_lineup = self.build_random_line_up(by_position_copied)
          if random_lineup == None:
            continue

          is_full_locked = False
          if seed_roster != None:
              is_full_locked = True
              for i in range(len(self.positions_to_fill)):
                  pl = seed_roster[i]
                  if pl != '' and pl != None:
                      random_lineup.locked_indices.append(i)
                      random_lineup.replace(pl, i)
                  else:
                      is_full_locked = False

              if is_full_locked:
                  print("ROSTER FULLY LOCKED")
                  return [random_lineup]
              
          if random_lineup == None or random_lineup.cost > self.max_cost:
            continue

          if len(random_lineup.players) != len(set([a.name for a in random_lineup.players])):
            __import__('pdb').set_trace()

          result = self.optimize_roster(random_lineup, by_position_copied)

          if lineup_validator != None and lineup_validator(result) != True:
            continue

          if result.value > best_roster_val:
              best_roster = result
              best_roster_val = result.value

              # all_names = [a.name for a in best_roster.players]
              # all_names_sorted = sorted(all_names)
              # roster_key = ",".join(all_names_sorted)
              # if roster_count > 50:
              #     break

              #TODO: PUT THIS BACK IN AND TROUBLESHOOT
              # best_roster = optimize_roster_by_start_time(by_position_copied, best_roster)
              # later games get laters slots
              # earlier games get earlier slots
              teams = []
              for pl in best_roster.players[1:]:
                if pl.team not in teams:
                  teams.append(pl.team)
              print("B: {} - team ct: {}\n".format(best_roster, len(teams)))


      return best_roster
  
  def optimize_top_n(self, by_position, n, iter_count = 600000, lineup_validator = None, seed_roster = None):
    all_rosters = []
    roster_keys = []
    random.seed(time.time())
    
    for i in range(iter_count):
        if i % 50000 == 0:
            print(i)

        random_lineup = self.build_random_line_up(by_position)
        if random_lineup == None:
          continue

        is_full_locked = False
        if seed_roster != None:
            is_full_locked = True
            for i in range(len(seed_roster)):
                pl = seed_roster[i]
                if pl != '' and pl != None:
                    random_lineup.replace(pl, i)
                    random_lineup.locked_indices.append(i)
                else:
                    is_full_locked = False

            if is_full_locked:
                print("ROSTER FULLY LOCKED")
                return [random_lineup]
            
        if random_lineup == None or random_lineup.cost > self.max_cost:
          continue

        if len(random_lineup.players) != len(set([a.name for a in random_lineup.players])):
          __import__('pdb').set_trace()

        result = self.optimize_roster(random_lineup, by_position)
    
        if lineup_validator != None and lineup_validator(result) != True:
          continue

        all_names = [a.name for a in result.players]
        all_names_sorted = sorted(all_names)
        roster_key = ",".join(all_names_sorted)

        if roster_key in roster_keys:
          continue

        roster_keys.append(roster_key)
        all_rosters.append(result)

    all_rosters_sorted = sorted(all_rosters, key=lambda a: a.value, reverse=True)
    return all_rosters_sorted[:n]


class DK_NBA_Optimizer:
  def __init__(self):
    self.optimizer = Optimizer(50000, ["PG", "SG", "SF", "PF", "C", "G", "F", "UTIL"])

  def prune_player_pool(self, by_position):
    by_position_copied = {}
    for position, players in by_position.items():
      by_position_copied[position] = []

      all_value_per_dollars = [pl.value_per_dollar for pl in players]

      # best_value = max(all_value_per_dollars)
      # cuttoff = best_value / 3


      best_value = max(all_value_per_dollars)
      worst_value = min(all_value_per_dollars)
      value_range = best_value - worst_value
      cuttoff = best_value - value_range / 1.6

      for player in players:
        if player.value_per_dollar < cuttoff:
          # print("Filtered out: {}".format(player))
          continue
        by_position_copied[position].append(player)

      # print("{} Player ct before: {} after: {}".format(position, len(players), len(by_position_copied[position])))
    
    return by_position_copied

  def optimize(self, by_position, locked_players, iter=int(100000)):
    by_position = self.prune_player_pool(by_position)
    return self.optimizer.optimize(by_position, iter, None, locked_players)
  
  def optimize_top_n(self, by_position, n, locked_players, iter = int(60000)):
    by_position = self.prune_player_pool(by_position)
    # __import__('pdb').set_trace()
    result = self.optimizer.optimize_top_n(by_position, n, iter, None, seed_roster=locked_players)
    return result

class DK_CBB_Optimizer:
  def __init__(self):
    self.optimizer = Optimizer(50000, ["G", "G", "G", "F", "F", "F", "UTIL", "UTIL"])

  def prune_player_pool(self, by_position):
    by_position_copied = {}
    for position, players in by_position.items():
      by_position_copied[position] = []

      all_value_per_dollars = [pl.value_per_dollar for pl in players]

      best_value = max(all_value_per_dollars)
      cuttoff = best_value / 3
      for player in players:
        if player.value_per_dollar < cuttoff:
          # print("Filtered out: {}".format(player))
          continue
        by_position_copied[position].append(player)

      print("{} Player ct before: {} after: {}".format(position, len(players), len(by_position_copied[position])))
    
    return by_position_copied

  def optimize(self, by_position, locked_players, iter=int(100000)):
    by_position = self.prune_player_pool(by_position)
    return self.optimizer.optimize(by_position, iter, None, locked_players)
  
  def optimize_top_n(self, by_position, n, iter = int(60000)):
    by_position = self.prune_player_pool(by_position)
    result = self.optimizer.optimize_top_n(by_position, n, iter)
    return result

  def optimize_top_n_diverse(self, by_position, n, value_tolerance, iter):
    initial_set = self.optimize_top_n(by_position, 5000, iter)
    initial_set_sorted = sorted(initial_set, key=lambda a:a.value, reverse=True)
    value_couttoff = initial_set_sorted[0].value - value_tolerance
    filtered_rosters = [r for r in initial_set_sorted if r.value > value_couttoff]
    print("INITIAL CT: {} FILTERED: {} CUTOOFF: {}".format(len(initial_set), len(filtered_rosters), value_couttoff))
    player_exposures = utils.get_player_exposures(filtered_rosters)
    player_to_new_value = {}

    for player, ct in player_exposures.items():
      player_to_new_value[player] = 1 / ct

    roster_and_new_value = []
    idx = 0
    for roster in filtered_rosters:

      new_roster_value = sum([player_to_new_value[pl.name] for pl in roster.players])
      roster_and_new_value.append((roster, new_roster_value, idx))
      idx += 1
        
    roster_and_new_value_sorted = sorted(roster_and_new_value, key=lambda a: a[1], reverse=True)
    
    all_the_new_rosters = [r[0] for r in roster_and_new_value_sorted]
    to_return = all_the_new_rosters[:n]
    print("BEST ROSTER: {}".format(initial_set_sorted[0]))
    return (to_return, initial_set_sorted[0])

class FD_NBA_Optimizer:
  def __init__(self):
    self.optimizer = Optimizer(60000, ["PG", "PG", "SG", "SG", "SF", "SF", "PF", "PF", "C"])

  def prune_player_pool(self, by_position):
    by_position_copied = {}
    for position, players in by_position.items():
      by_position_copied[position] = []

      all_value_per_dollars = [pl.value_per_dollar for pl in players]
      cuttoff = 0
      if len(all_value_per_dollars) > 18:
        best_value = max(all_value_per_dollars)
        cuttoff = best_value / 3


      # best_value = max(all_value_per_dollars)
      # worst_value = min(all_value_per_dollars)
      # value_range = best_value - worst_value
      # cuttoff = best_value - value_range / 1.5

      for player in players:
        if player.value_per_dollar < cuttoff:
          # print("Filtered out: {}".format(player))
          continue
        by_position_copied[position].append(player)

      # print("{} Player ct before: {} after: {}".format(position, len(players), len(by_position_copied[position])))
    
    return by_position_copied

  def optimize(self, by_position, locked_players, iter=int(100000), lineup_validator=None):
    by_position = self.prune_player_pool(by_position)
    return self.optimizer.optimize(by_position, iter, lineup_validator, locked_players)
  
  def optimize_top_n(self, by_position, n, iter = int(60000), locked_players=None, lineup_validator=None):
    by_position = self.prune_player_pool(by_position)
    result = self.optimizer.optimize_top_n(by_position, n, iter, lineup_validator, locked_players)
    return result

class FD_WNBA_Optimizer:
  def __init__(self):
    self.optimizer = Optimizer(40000, ["G", "G", "G", "F", "F", "F", "F"])

  def prune_player_pool(self, by_position):
    by_position_copied = {}
    for position, players in by_position.items():
      by_position_copied[position] = []

      all_value_per_dollars = [pl.value_per_dollar for pl in players]

      best_value = max(all_value_per_dollars)
      cuttoff = best_value / 3
      for player in players:
        if player.value_per_dollar < cuttoff:
          print("Filtered out: {}".format(player))
          continue
        by_position_copied[position].append(player)

      print("{} Player ct before: {} after: {}".format(position, len(players), len(by_position_copied[position])))
    
    return by_position_copied

  def optimize(self, by_position):
    by_position = self.prune_player_pool(by_position)
    return self.optimizer.optimize(by_position, iter_count = int(800000 / 0.6))

  def optimize_top_n(self, by_position, n):
    by_position = self.prune_player_pool(by_position)
    result = self.optimizer.optimize_top_n(by_position, n, iter_count = int(200000))
    return result


class MLB_Optimizer:
  def __init__(self):
    self.optimizer = Optimizer(35000, ["P", "C/1B", "2B", "3B", "SS", "OF", "OF", "OF", "UTIL"])

  def optimize(self, by_position, iter_count, seed_roster=None):

    def lineup_validator(lineup):
      team_ct = {}
      team_ct_including_p = {}
      for player in lineup.players:
        pl_team = player.team
        if not pl_team in team_ct:
          team_ct_including_p[pl_team] = 1
        else:
          team_ct_including_p[pl_team] += 1
        if player.position == "P":
          continue
        if not pl_team in team_ct:
          team_ct[pl_team] = 1
        else:
          team_ct[pl_team] += 1

      makes_per_team_limit = max(team_ct.values()) <= 4
      min_teams_constraint = len(team_ct_including_p.values()) > 2
      return makes_per_team_limit and min_teams_constraint


    return self.optimizer.optimize(by_position, iter_count, lineup_validator=lineup_validator, seed_roster=seed_roster)

class NFL_Optimizer:
  def __init__(self, salary_cap=60000):
    self.optimizer = Optimizer(salary_cap, ["QB", "RB", "RB", "WR", "WR", "WR", "TE", "FLEX", "D"])


    def lineup_validator(roster):
      # the selected defense can't be playing against any of the other player teams
      defense_opp = roster.players[-1].opp
      is_valid = True
      for pl in roster.players:
        if pl.team == defense_opp:
          is_valid = False
          break
      
      return is_valid

    self.lineup_validator = lineup_validator
    

  def optimize(self, by_position, locked_players, iter):
    return self.optimizer.optimize(by_position, iter, self.lineup_validator, locked_players)

  def optimize_top_n(self, by_position, n, iter):
    result = self.optimizer.optimize_top_n(by_position, n, iter, self.lineup_validator)
    return result

class CFB_Optimizer:
  def __init__(self):
    self.optimizer = Optimizer(60000, ["QB", "RB", "RB", "WR", "WR", "WR", "FLEX"])

  def optimize(self, by_position, locked_players):
    return self.optimizer.optimize(by_position, int(90000), None, locked_players)

  def optimize_top_n(self, by_position, n):
    result = self.optimizer.optimize_top_n(by_position, n, int(90000 / 1))
    return result

class NASCAR_Optimizer:
  def __init__(self):
    self.optimizer = Optimizer(50000, ["D", "D", "D", "D", "D"])

  def optimize(self, by_position, locked_players):
    return self.optimizer.optimize(by_position, int(800000 / 3.6), None, locked_players)

  def optimize_top_n(self, by_position, n):
    result = self.optimizer.optimize_top_n(by_position, n, iter_count = int(200000 / 3))
    return result

class NHL_Optimizer:
  def __init__(self):
    self.optimizer = Optimizer(55000, ['C', 'C', 'W', 'W', 'D', 'D', 'UTIL', 'UTIL', 'G'])

  def optimize(self, by_position, locked_players):
    return self.optimizer.optimize(by_position, int(800000 / 1.6), None, locked_players)

  def optimize_top_n(self, by_position, n):
    result = self.optimizer.optimize_top_n(by_position, n, iter_count = int(200000 / 0.6))
    return result