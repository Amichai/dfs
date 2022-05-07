from NBA_projections import NBAProjections
from MLB_projections import MLBProjections

# produce a table of projections
# generate an ensemble of rosters
# produce a file to upload


if __name__ == "__main__":
  download_folder = "/Users/amichailevy/Downloads/"
  slate_path = "FanDuel-NBA-2022 ET-05 ET-07 ET-75769-players-list.csv"

  projections = NBAProjections(download_folder + slate_path)
  projections.print_slate()

  # slate_path = "FanDuel-MLB-2022 ET-05 ET-07 ET-75778-players-list.csv"

  # projections = MLBProjections(download_folder + slate_path)
  # projections.print_slate()