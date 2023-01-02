from datetime import datetime
import sched, time
import utils
from ScrapeProcessManager import run
from projection_providers.NBA_WNBA_Projections import NBA_WNBA_Projections, NBA_Projections_dk

# markers_min = [7,15,23,27,37,45,53,57,67]
markers_min = []

for i in range(61):
  markers_min.append(i + 0.25)

markers_sec = [a * 60 for a in markers_min]

s = sched.scheduler(time.time, time.sleep)

def scrape():
  print(datetime.now())
  to_next_alert = calculate_duration_to_next_alert()
  print("to next alert: {}".format(to_next_alert))
  s.enter(to_next_alert, 1, scrape)

def calculate_duration_to_next_alert():
  now = datetime.now()
  current_second = now.minute * 60 + now.second

  current_alert_index = None

  for i in range(len(markers_sec)):
    if current_second < markers_sec[i]:
      current_alert_index = i
      break

    
  next_marker = markers_sec[current_alert_index] 
  return next_marker - current_second

# run on - 7 15 23 27, 37 45, 53 57

to_next_alert = calculate_duration_to_next_alert()
print("to next alert: {}".format(to_next_alert))
s.enter(to_next_alert, 1, scrape)

print("end")

s.run()
# now = datetime.datetime.now()
# current_hour = (now.hour - 12) + (now.minute / 60)
# current_hour = round(current_hour, 2)
# print("CURRENT TIME: {}".format(current_hour))
# sport = "NBA"
# run(sport)


# fd_slate_path = utils.most_recently_download_filepath('FanDuel-NBA-', utils.TODAYS_SLATE_ID_NBA, '-players-list', '.csv')
# by_position = NBA_WNBA_Projections(fd_slate_path, "NBA").write_player_projections_to_db()
