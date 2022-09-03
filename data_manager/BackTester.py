from MLB_projections import MLBProjections



if __name__ == "__main__":
  download_folder = "/Users/amichailevy/Downloads/csvs/"
  slate_path = "FanDuel-MLB-2022 ET-05 ET-25 ET-76619-players-list.csv"
  template_path = "FanDuel-MLB-2022-05-25-76619-entries-upload-template.csv"
  teams_to_remove = []

  projections = MLBProjections(download_folder + slate_path)
  projections.print_slate()