import csv
import utils
from projection_providers.NBA_WNBA_Projections import NBA_WNBA_Projections, NBA_Projections_dk
import datetime

download_folder = "/Users/amichailevy/Downloads/"

dfs_crunch_filepath = "DFSCRUNCH-DOWNLOAD-DATA-fd82793.csv"
dfs_crunch_filepath_prefix = dfs_crunch_filepath.split('.')[0]

file = open(download_folder + dfs_crunch_filepath)
file_reader = csv.reader(file, delimiter=',', quotechar='"')

slate_path = "FanDuel-NBA-2022 ET-11 ET-04 ET-82793-players-list.csv"
projections = NBA_WNBA_Projections(download_folder + slate_path, "NBA")
name_to_player = projections.name_to_player()


name_to_val = {}
all_rows = projections.get_player_rows()
for row in all_rows:
  name = row[0]
  team = row[1]
  pos = row[2]
  cost = row[3]
  status = row[4]
  dfs_crunch = row[5]
  pp_proj = row[6]
  caesars_proj = row[7]
  rotowire_proj = row[8]
  numberfire_proj = row[9]
  fantasy_data_proj = row[10]
  caesars_is_active = row[11]
  if caesars_proj != '' and int(caesars_is_active) >= 3:
    name_to_val[name] = caesars_proj

new_lines = []
idx = 0
for cells in file_reader:
  if idx == 0:
    new_lines.append(cells)
    idx += 1
    continue
  
  name = cells[0]
  name = utils.normalize_name(name)
  if name in name_to_val:

    cells[1] = name_to_val[name]
  new_lines.append(cells)

  idx += 1

timestamp = str(datetime.datetime.now())
date = timestamp.replace('.', '_')
date = date.replace(":", "_")
output_file = open("/Users/amichailevy/Downloads/{}_MLE_{}.csv".format(dfs_crunch_filepath_prefix, date), "x")

for line in new_lines:
  line_str = [str(a) for a in line]
  output_file.write(",".join(line_str) + "\n")
# csv.writer(new_lines)

  