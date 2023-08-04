
class Player:
    def __init__(self, name, position, cost, team, value, opp=None, projection_source=''):
        self.name = name
        self.position = position
        self.cost = float(cost)
        self.team = team
        self.value = float(value)
        self.opp = opp
        self.value_per_dollar = self.value * 100 / (self.cost + 1)
        self.projection_source = projection_source

    def __repr__(self):
        return "{} - {} - {}".format(self.name, self.value, self.team)

    def clone(self):
        return Player(self.name, self.position, self.cost, self.team, self.value, self.opp, self.projection_source)


class Roster:
  def __init__(self, players):
      self.players = players
      self.cost = sum([float(p.cost) for p in self.players])
      self.value = sum([float(p.value) for p in self.players])
      self.locked_indices = []

  def __repr__(self):
      return ",".join([p.name for p in self.players]) + " {} - {}".format(self.cost, self.value)

  def remaining_funds(self, max_cost):
      return max_cost - self.cost

  def replace(self, player, idx):
      self.players[idx] = player
      self.cost = sum([float(p.cost) for p in self.players])
      self.value = sum([float(p.value) for p in self.players])

  def at_position(self, position):
      return [p for p in self.players if p.position == position]

  def clone(self):
    return Roster(list(self.players))

  def get_ids(self, id_mapping):
      ids = []
      for p in self.players:
          id = id_mapping[p.name]
          ids.append(id)

      ids.reverse()
      return ",".join(ids)

  def are_names_unique(self):
    return len(self.players) == len(set([a.name for a in self.players]))

  def roster_key(self):
    names = [a.name for a in self.players]
    return ",".join(sorted(names))


def normalize_name(name):
    name = unidecode.unidecode(name)
    name = name.replace("  ", " ")
    name = name.replace("’", "'")
    parts = name.split(" ")
    if len(parts) > 2:
        name = "{} {}".format(parts[0], parts[1]).strip()

    name = name.replace(".", "")
    if name in name_mapper:
        name = name_mapper[name]

    return name.strip()


def random_element(arr):
    idx = random.randint(0, len(arr) - 1)
    val = arr[idx]
    return val


def get_player_exposures(rosters_sorted):
    player_to_ct = {}
    for roster in rosters_sorted:
        for player in roster.players:
            if not player.name in player_to_ct:
                player_to_ct[player.name] = 1
            else:
                player_to_ct[player.name] += 1
    
    return player_to_ct