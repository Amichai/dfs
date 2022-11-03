import csv

download_folder = "past_entries/"
filepaths = ["fanduel entry history 20221102.csv", "fanduel entry history 20221101.csv", "fanduel entry history 20221101 (1).csv", "fanduel entry history 20221101 (2).csv", "fanduel entry history 20221101 (3).csv", "fanduel entry history 20221101 (4).csv"]

target_sport = "nba"

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



for date, rows in date_to_rows.items():
  winnings = round(sum([float(a[11]) for a in rows]), 2)
  entries = round(sum([float(a[10]) for a in rows]), 2)

  print("{},{},{},{}".format(date, entries, winnings, round(winnings - entries, 2)))
  # print("{}| -{} + {} = {}".format(date, entries, winnings, round(winnings - entries, 2)))
# __import__('pdb').set_trace()
  