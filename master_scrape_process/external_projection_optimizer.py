from library import normalize_name, load_start_times_and_slate_path, get_fd_slate_players

download_folder = "/Users/amichailevy/Downloads/"

projections_path = "DFSCRUNCH-DOWNLOAD-DATA-dk67328.csv"

lines = open(download_folder + projections_path, "r").readlines()



# print(lines)
(start_time_to_teams, path) = load_start_times_and_slate_path("start_times2.txt")


fd_players = get_fd_slate_players(download_folder + path)
__import__('pdb').set_trace()

print(start_time_to_teams)
print(path)

for line in lines[1:]:
  parts = line.split(',')
  name = parts[0].strip('"')
  name = normalize_name(name)
  projection = parts[1].strip('"')

  print("{} - {}".format(name, projection))