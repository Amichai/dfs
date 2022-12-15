import utils

class Reoptimizer():
  def __init__(self, projections, optimizer, locked_teams) -> None:
    self.projections = projections
    self.optimizer = optimizer
    self.locked_teams = locked_teams

  def run(self, existing_rosters, player_id_to_name, allow_duplicate_rosters, is_dk=False):
    projections = self.projections
    projections.print_slate()
    by_position = projections.players_by_position(exclude_zero_value=False)
    name_to_players = get_name_to_player_objects(by_position)
    by_position = filter_out_locked_teams(by_position, self.locked_teams)
    seen_roster_strings = []
    seen_roster_string_to_optimized_roster = {}


    roster_idx = 0
    all_results = []
    for existing_roster in existing_rosters:
      print("ROSTER: {}".format(roster_idx))
      roster_idx += 1
      players = existing_roster[3:12]
      if players[0] == '':
        continue

      roster_string = ",".join(players)

      if roster_string in seen_roster_strings:
        result = seen_roster_string_to_optimized_roster[roster_string]
        all_results.append(result)
        continue

      seen_roster_strings.append(roster_string)
      players3 = []
      for p in players:
        if ':' in p:
          p = p.split(':')[0]
        if not p in player_id_to_name:
          __import__('pdb').set_trace()

        players3.append(player_id_to_name[p])

      players4 = [name_to_players[p][0] for p in players3]
      players5 = []
      initial_roster = []
      lock_ct = 0
      for p in players4:
        if p.team in self.locked_teams:
          players5.append(p)
          lock_ct += 1
        else:
          players5.append(None)
        initial_roster.append(p.name)

      is_se_roster_or_h2h = "Single Entry" in existing_roster[2] or "Entries Max" in existing_roster[2] or "H2H vs" in existing_roster[2]


      if lock_ct != 9:
        # todo: this will be optimize_top_n
        # iterate over the n results and take the first one not seen already (within range)
        # result = optimizer.optimize(by_position, players5, int(1750), is_roster_valid)
        candidate_rosters = self.optimizer.optimize_top_n(by_position, 20, int(1150), players5, is_roster_valid)
        result = candidate_rosters[0]
        
        top_val = result.value
        candidate_rosters_filtered = [a for a in candidate_rosters if a.value >= top_val - 10]
        if not is_se_roster_or_h2h:
          counter = 0
          for roster in candidate_rosters_filtered:
            names1 = [p.name for p in roster.players]
            roster1_key = ",".join(sorted(names1))
            if not roster1_key in seen_roster_strings:
              result = roster
              print("TAKING CANDIDATE ROSTER: {}".format(counter))
              break

            counter += 1
            # else:
            #   __import__('pdb').set_trace()
            
      else:
        result = utils.Roster(players4)
      
      try:
        names1 = [p.name for p in result.players]
        roster1_key = ",".join(sorted(names1))

        if is_se_roster_or_h2h:
          print("IS SE ROSTER or H2H!")

        has_dead_player = any([a.value < 12.0 and a.team not in locked_teams for a in result.players])
        if roster1_key in seen_roster_strings \
            and not allow_duplicate_rosters \
            and not is_se_roster_or_h2h \
            and not has_dead_player:
          # don't change the result!
          print("initial roster unchanged! {}")
          all_results.append(utils.Roster(players4))
        else:
          seen_roster_strings.append(roster1_key)
          seen_roster_string_to_optimized_roster[roster_string] = result


          roster2_key = ",".join(sorted(initial_roster))
          if roster1_key != roster2_key:
            print("LOCKED PLAYERS: {}".format(players5))


            print("INITIAL ROSTER:\n{}".format(initial_roster))
            __import__('pdb').set_trace()

            print(result)

          all_results.append(result)
      except:
        __import__('pdb').set_trace()

    total_roster_val = sum([a.value for a in all_results])
    utils.print_player_exposures(all_results, locked_teams)
    variation = utils.print_roster_variation(all_results)
    print(variation)
    
    # variation = utils.print_roster_variation(existing_rosters)
    # print(variation)
    print("TOTAL ROSTER VAL: {}".format(total_roster_val))
    
    __import__('pdb').set_trace()
    return all_results