import utils
import time
import statistics
import random

class Optimizer:
  def __init__(self, cost, positions, by_position):
    # for each position, (subset of positions)
    # for each salary remaining
    # give me the n best rosters
    self.positions = positions
    self.max_cost = cost
    self.positions_unique = list(set(positions))
    (self.by_position_cost_first, self.by_position_value_first) = self.sort_players(by_position)

    self.BATCH_SIZE = 2000
    self.all_rosters = None

  def generate_random_lineup(self):
    roster_players = []
    value = 0
    cost = 0
    names = []
    for position in self.positions:
      players = self.by_position_cost_first[position]
      random_index = random.randint(int(len(players) / 2), len(players) - 1)
      pl = players[random_index].clone()
      roster_players.append(pl)
      cost += pl.cost
      value += pl.value
      if pl.name in names:
        return None
      names.append(pl.name)
      if cost > self.max_cost:
        return None

    to_return = utils.Roster(roster_players)

    return to_return

  def sort_players(self, by_position):
    by_position_cost_first = {}
    by_position_value_first = {}
    for pos, players in by_position.items():
      by_position_cost_first[pos] = sorted(players, key=lambda a: a.cost, reverse=True)
      by_position_value_first[pos] = sorted(players, key=lambda a: a.value, reverse=True)

    return (by_position_cost_first, by_position_value_first)

  def improve_position(self, position, names, remaining_cost, target_value):
    candidates = self.by_position_value_first[position]
    for candidate in candidates:
      if candidate.cost <= remaining_cost and candidate.value > target_value and not candidate.name in names:
        return candidate.clone()

    return None

  def improve_roster(self, roster):
    # for every player, is there a better swap?
    # for every pair of players is there a better swap, etc?
    # given a position, name set, remaining cost, what is my best option?
    
    pos_ct = len(self.positions)
    while True:
      start_idx = random.randint(0, 8)
      saw_improvement = False
      for i in range(pos_ct):
        index_to_swap = (start_idx + i) % pos_ct
        names = [pl.name for pl in roster.players]
        target_player = roster.players[index_to_swap]
        remaining_cost = self.max_cost - roster.cost + target_player.cost
        target_value = target_player.value
        position = self.positions[index_to_swap]
        replacement = self.improve_position(position, names, remaining_cost, target_value)
        if replacement == None:
          continue

        roster.replace(replacement, index_to_swap)

        saw_improvement = True
        break

      if not saw_improvement:
        return roster

  def generate_random_batch(self):
    random_lineups = []
    for i in range(self.BATCH_SIZE):
      random = self.generate_random_lineup()
      if random == None:
        continue
        
      random = self.improve_roster(random)
      random_lineups.append(random)

    return random_lineups

  def perturb_existing_rosters(self):
    to_return = []
    for i in range(self.BATCH_SIZE):
      before_clone = utils.random_element(self.all_rosters)
      random_roster = before_clone.clone()
      names = [a.name for a in before_clone.players]

      # TODO PLAY WITH THIS NUMBER
      for i in range(4):
        replace_idx = random.randint(0, 8)
        position = self.positions[replace_idx]
        candidate_pool = self.by_position_cost_first[position]
        take_idx = random.randint(int(len(candidate_pool) / 2), len(candidate_pool) - 1)
        replace_with = candidate_pool[take_idx].clone()
        if replace_with.name in names:
          continue

        names.append(replace_with.name)

        random_roster.replace(replace_with, replace_idx)

      cost = sum([a.cost for a in random_roster.players])
      if cost > self.max_cost:
        continue

      random_roster = self.improve_roster(random_roster)

      to_return.append(random_roster)

    return to_return

  def assimilate_batch(self, batch):
    if not self.all_rosters:
      self.all_rosters = sorted(batch, key=lambda a: a.value, reverse=True)
      return

    min_val = self.all_rosters[-1].value
    roster_keys = [a.roster_key() for a in self.all_rosters]
    
    batch_filtered = [b for b in batch if b.value >= min_val and (b.roster_key() not in roster_keys)]

    self.all_rosters += batch_filtered
    self.all_rosters = sorted(self.all_rosters, key=lambda a: a.value, reverse=True)    

  def optimize_top_n(self, n, iter, lineup_validator, locked_players):
    start_time = time.time()
    while True:
      if self.all_rosters == None or len(self.all_rosters) < self.BATCH_SIZE:
        batch = self.generate_random_batch()
      else:
        batch = self.perturb_existing_rosters()

      self.assimilate_batch(batch)

      if time.time() - start_time > iter / 1000:
        break
  
    return self.all_rosters[:n]

class FD_NBA_Optimizer:
  def __init__(self, by_position):
    by_position = self.prune_player_pool(by_position)
    self.optimizer = Optimizer(60000, ["PG", "PG", "SG", "SG", "SF", "SF", "PF", "PF", "C"], by_position)

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
    return self.optimizer.optimize(by_position, iter, lineup_validator, locked_players)
  
  def optimize_top_n(self, by_position, n, iter = int(60000), locked_players=None, lineup_validator=None):
    result = self.optimizer.optimize_top_n(n, iter, lineup_validator, locked_players)
    return result