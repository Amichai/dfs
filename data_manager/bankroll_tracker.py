import csv
import statistics

download_folder = "past_entries/"
filepaths = [
  "fanduel entry history 20221208.csv",
  "fanduel entry history 20221207.csv",
  "fanduel entry history 20221206.csv",
  "fanduel entry history 20221201.csv",
  "fanduel entry history 20221126.csv",
  "fanduel entry history 20221125.csv",
  "fanduel entry history 20221124.csv", "fanduel entry history 20221121.csv",
  "fanduel entry history 20221120.csv", "fanduel entry history 20221119.csv","fanduel entry history 20221118.csv", "fanduel entry history 20221117.csv", "fanduel entry history 20221116.csv", "fanduel entry history 20221113.csv", "fanduel entry history 20221112.csv", "fanduel entry history 20221110.csv", "fanduel entry history 20221105.csv", "fanduel entry history 20221103.csv", "fanduel entry history 20221102.csv", "fanduel entry history 20221101.csv", "fanduel entry history 20221101 (1).csv", "fanduel entry history 20221101 (2).csv", "fanduel entry history 20221101 (3).csv", "fanduel entry history 20221101 (4).csv"]

target_sport = "nba"


def H2H_analysis():
  date_to_rows = {}
  seen_entry_ids = []
  for filepath in filepaths:
    file = open(download_folder + filepath)
    file_reader = csv.reader(file, delimiter=',', quotechar='"')
    for cells in file_reader:
      entry_id = cells[0]

      if entry_id in seen_entry_ids:
        continue

      seen_entry_ids.append(entry_id)

      sport = cells[1]
      if sport.strip() != target_sport:
        continue

      date = cells[2].strip()
      
      title = cells[3]

      if not "Head-to-head" in title:
        continue

      score = cells[5]
      opp_score = cells[6]
      position = cells[7]
      entries = cells[8]
      contest = cells[9]
      entry_fee = cells[10]
      winnings = cells[11]
      if len(cells) > 13 and cells[13].strip() == "voided":
        continue
      
      # if date != inspection_date:
      #   continue()
      if not date in date_to_rows:
        date_to_rows[date] = []
      date_to_rows[date].append(cells)

  name_to_distance_from_ave = {}
  for date, rows in date_to_rows.items():
    unique_scores = []
    for row in rows:
      opp_score = row[6]
      if not opp_score in unique_scores:
        unique_scores.append(opp_score)
      
    unique_scores_sorted = sorted(unique_scores)
    as_floats = [float(a) for a in unique_scores_sorted]
    average = statistics.mean(as_floats)
    for row in rows:
      name = row[9]
      if not name in name_to_distance_from_ave:
        name_to_distance_from_ave[name] = {}

      if not date in name_to_distance_from_ave[name]:
        name_to_distance_from_ave[name][date] = []

      score = float(row[6])
      diff = round(score - average, 2)
      if diff not in name_to_distance_from_ave[name][date]:
        name_to_distance_from_ave[name][date].append(diff)
      
    

    winnings = round(sum([float(a[11]) for a in rows]), 2)
    entries = round(sum([float(a[10]) for a in rows]), 2)

    print("{},{},{},{}".format(date, entries, winnings, round(winnings - entries, 2)))
  print(name_to_distance_from_ave)

  name_to_aggregate_score = []
  for name, dates in name_to_distance_from_ave.items():
    total_score = 0
    game_ct = 0
    for date, vals in dates.items():
      for val in vals:
        total_score += val
        game_ct += 1
      
    name_to_aggregate_score.append([name, total_score, game_ct, total_score / game_ct])


  name_to_aggregate_score_sorted = sorted(name_to_aggregate_score, key=lambda a: a[3])

  for name, total_score, game_ct, ave_score in name_to_aggregate_score_sorted:
    print("{}, {}, {}".format(name, round(ave_score, 2), game_ct))



def PandL(h2h_only=False):
  date_to_rows = {}
  seen_entry_ids = []
  for filepath in filepaths:
    file = open(download_folder + filepath)
    file_reader = csv.reader(file, delimiter=',', quotechar='"')
    for cells in file_reader:
      entry_id = cells[0]

      if entry_id in seen_entry_ids:
        continue

      seen_entry_ids.append(entry_id)

      sport = cells[1]
      if sport.strip() != target_sport:
        continue


      date = cells[2].strip()
      title = cells[3]
      
      
      if h2h_only and not "Head-to-head" in title:
        continue

      score = cells[5]
      opp_score = cells[6]
      position = cells[7]
      entries = cells[8]
      contest = cells[9]
      if len(cells) < 11:
        continue
      entry_fee = cells[10]
      winnings = cells[11]
      if len(cells) > 13 and cells[13].strip() == "voided":
        continue
      
      # if date != inspection_date:
      #   continue()
      if not date in date_to_rows:
        date_to_rows[date] = []
      date_to_rows[date].append(cells)


  for date, rows in date_to_rows.items():
    winnings = round(sum([float(a[11]) for a in rows]), 2)
    entries = round(sum([float(a[10]) for a in rows]), 2)

    print("{},{},{},{}".format(date, entries, winnings, round(winnings - entries, 2)))
    # print("{}| -{} + {} = {}".format(date, entries, winnings, round(winnings - entries, 2)))
  # __import__('pdb').set_trace()
    

H2H_analysis()
# PandL()