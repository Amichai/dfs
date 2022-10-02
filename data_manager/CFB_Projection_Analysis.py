from data_manager import DataManager

def print_stat_to_fp_correlations(pp_results):
  for result in pp_results:
    projections = result["projections"]
    if not 'Fantasy Score' in projections:
      continue


    #ignore QBs
    if 'Passing Yards' in projections or 'Passing Completions' in projections:
      continue

    
    if not 'Rushing Yards' in projections:
      continue

    if 'Receiving Yards' in projections:
      continue

    name = result['name']
    fantasy_score = projections['Fantasy Score']
    # rushing_yards = projections['Rushing Yards']
    receiving_yards = projections['Rushing Yards']
  
  print("{}, {}, {}".format(name, receiving_yards, fantasy_score))

dm = DataManager("CFB")
result = dm.todays_rows('CFB')

caesar_results = [a for a in result if a['scraper'] == 'Caesars']
pp_results = [a for a in result if a['scraper'] == 'PP']
underdog_results = [a for a in result if a['scraper'] == 'Underdog']



for result in caesar_results:
  print(result['name'])
  projections = result['projections']

  name = result['name']

  if not 'Rushing Yards' in projections:
    continue

  if projections['Rushing Yards:isActive'] == False:
    continue

  if 'Passing Touchdowns' in projections:
    continue # skip QB

  # print(name)
  # print(projections)
  # project from rushing + receiving
  pass

# RB projections – 
# rushing yards -> fantasy score  (no receiving yards)
# 0.148x + 3.2561


# Rush+Rec Yards -> Fantasy Score
# 0.1815x - 1.5062

# Receiving Yards -> Fantasy Score (no rushing yards!)
# 0.2105x - 0.0954