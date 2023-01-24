import Optimizer
import EnsembleOptimizer
import statistics
import utils
import random
import time

positions = ["PG", "SG", "SF", "PF", "C"]
price_min = 3500
price_max = 12000

players = []

random.seed(0)

for i in range(1500):
  name = "name{}".format(i)
  team = "team{}".format(i % 10)
  pos1 = utils.random_element(positions)

  cost = random.randrange(price_min, price_max)
  value = round(cost / 200 + random.uniform(-10, 10), 2)

  player = utils.Player(name, pos1, cost, team, value)
  players.append(player)
  
  pos2 = utils.random_element(positions)
  if pos1 != pos2:
    player = utils.Player(name, pos2, cost, team, value)
    players.append(player)


# for player in players:
#   print("{},{},{},{}".format(player.name, player.position, player.cost, player.value))

by_position = {}
for player in players:
  position = player.position
  if not position in by_position:
    by_position[position] = []
  
  by_position[position].append(player)


optimizer1 = Optimizer.FD_NBA_Optimizer()
optimizer2 = EnsembleOptimizer.FD_NBA_Optimizer(by_position)

def test(optimizer, iter):
  start_time = time.time()

  rosters = optimizer.optimize_top_n(by_position, 1000, iter)
  rosters = rosters[:50]

  end_time = time.time()

  duration = end_time - start_time
  max_val = max([a.value for a in rosters])
  ave_val = statistics.mean([a.value for a in rosters])

  exposures = utils.get_player_exposures(rosters)
  player_to_ct_sorted = sorted(exposures.items(), key=lambda a: a[1], reverse=True)

  print("{} - {}".format(max_val, ave_val))
  print("DURATION: {}".format(round(duration, 2)))

print("NEW OPTIMIZER")
test(optimizer2, 15000)

print("OLD OPTIMIZER")
test(optimizer1, 28000)