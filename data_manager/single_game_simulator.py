import utils
import json
import csv
# load up the projections
# come up with roster generation strategies
# (add actual point annotaitions as needed)
# max value + what percentage are over the money line?

projections_path = "DFSCRUNCH-DOWNLOAD-DATA-fd84100.csv"

data_file = open('data_files/dfs_crunch.json', "r")

as_json = json.loads(data_file.read())

name_to_info = {}

for row in as_json:
  name = row['name']
  if not 'UTIL' in name:
    continue

  print(row)
  salary = float(row['salary'])
  projected = float(row['pfp'])
  actual_points = float(row['points'])

  name_to_info[name] = [salary, projected, actual_points]

__import__('pdb').set_trace()



file = open(utils.DOWNLOAD_FOLDER + projections_path)
file_reader = csv.reader(file, delimiter=',', quotechar='"')

new_lines = []
idx = 0
for cells in file_reader:
  if idx == 0:
    idx += 1
    continue
  
  name = cells[0]
  if not "UTIL" in name:
    continue
  name = utils.normalize_name(name)
  new_lines.append(cells)

  idx += 1

__import__('pdb').set_trace()