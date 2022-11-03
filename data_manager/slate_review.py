import csv

history_folder = "past_entries/"
history_filepath = "fanduel entry history 20221101.csv"

download_folder = "/Users/amichailevy/Downloads/"
upload_template_path = "upload_template_2022-10-31 18_50_34_901479.csv"


target_sport = "nba"

entry_id_to_score_and_label = {}

file = open(history_folder + history_filepath)
file_reader = csv.reader(file, delimiter=',', quotechar='"')
for cells in file_reader:
  entry_id = cells[0].strip('S')
  score = cells[5]
  entry_id_to_score_and_label[entry_id] = [score]

file2 = open(download_folder + upload_template_path)
file_reader2 = csv.reader(file2, delimiter=',', quotechar='"')
for cells in file_reader2:
  entry_id = cells[0]
  if not entry_id in entry_id_to_score_and_label:
    continue
  label = cells[12]
  entry_id_to_score_and_label[entry_id].append(label)
  

seen_labels = []
table = []
for entry_id, vals in entry_id_to_score_and_label.items():
  if len(vals) != 2:
    continue

  label = vals[1]
  if label in seen_labels:
    continue
  seen_labels.append(label)
  
  table.append([vals[0], vals[1]])

table_sorted = sorted(table, key=lambda a: float(a[1].split('_')[0]))
for row in table_sorted:
  if "HEDGE" in row[1]:
    continue
  print("{}, {}".format(row[1], row[0]))

for row in table_sorted:
  if not "HEDGE" in row[1]:
    continue
  print("{}, {}".format(row[1], row[0]))