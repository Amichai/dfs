from library import *
import websocket

ws = websocket.WebSocket()

url = "wss://6xz3koia4i.execute-api.us-east-2.amazonaws.com/prod"
ws.connect(url)

slates = [
  ('nba', 'dk67509'),
  ('mlb', 'dk67556')
]

sport, slate = slates[0]

roster_count = str(1)
# iterations = 1


nba_payload = '{"action":"builder1024","banned":[],"exposure_bounds":[],"is_late_swap_retry":false,"is_staff":false,"iterations":1,"lines_allowed":null,"lineup_settings":[],"is_late_swap":false,"locked":"","min_pfp":1,"maximize_teams_stacks":false,"max_exposure":100,"max_opponent_players":0,"max_position_exposure":null,"max_same_teams_stacks":100,"max_total_ownerships":null,"my_min_salary":30000,"my_max_salary":50000,"min_pfp_per_min_in_last_games_skip_count":0,"use_max_difference_exposure":null,"max_difference_exposure":null,"optimize_by":"pfp","optimize_for_speed":false,"optimize_for_speed_value":10,"player_groups":[],"position_stacks":[],"profile":"Default","site":"draftkings","slate":"' + slate + '","smart_random":null,"spec_positions_by_real_positions":null,"sport":"' + sport + '","team_stack_groups":[],"teams_min_max":[],"time_beginning":"20220421","use_random":0,"user_id":936,"username":"aml","uniques":' + roster_count + ',"model_settings":{},"is_v2":false,"token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo5MzYsInNsYXRlIjoiZGs2NzUwOSJ9.76dOJjqVoxf8U0De-uyKwDjbfL4xlDFgqhKb6W4C7T8"}'


mlb_payload = '{"action":"builder2048","banned":"","exposure_bounds":[],"is_late_swap_retry":false,"is_staff":false,"iterations":3,"lines_allowed":null,"lineup_settings":[],"is_late_swap":false,"locked":[],"min_pfp":1,"maximize_teams_stacks":false,"max_exposure":100,"max_opponent_players":4,"max_position_exposure":null,"max_same_teams_stacks":100,"max_total_ownerships":null,"my_min_salary":30000,"my_max_salary":50000,"min_pfp_per_min_in_last_games_skip_count":{"Pitchers":0,"Batters":0},"use_max_difference_exposure":null,"max_difference_exposure":null,"optimize_by":"pfp", ////"optimize_for_speed":true,"optimize_for_speed_value":10,"player_groups":[],"position_stacks":[],"profile":"Default","site":"draftkings","slate":' + slate + ',"smart_random":null,"spec_positions_by_real_positions":null,"sport":"' + sport + '","team_stack_groups":[],"teams_min_max":[],"time_beginning":"20220421","use_random":0,"user_id":936,"username":"aml","uniques":1,"model_settings":{},"is_v2":false,"token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo5MzYsInNsYXRlIjoiZGs2NzU1NiJ9.HgqmmId6R_1tydgmFu8TZot4ByFW-lLh2_oeuov572A"}'


mlb_payload = '{"action":"builder2048","banned":["Carlos Carrasco","Dylan Cease","Jordan Montgomery"],"exposure_bounds":[],"is_late_swap_retry":false,"is_staff":false,"iterations":3,"lines_allowed":null,"lineup_settings":[],"is_late_swap":false,"locked":"","min_pfp":1,"maximize_teams_stacks":false,"max_exposure":100,"max_opponent_players":4,"max_position_exposure":null,"max_same_teams_stacks":100,"max_total_ownerships":null,"my_min_salary":30000,"my_max_salary":50000,"min_pfp_per_min_in_last_games_skip_count":{"Pitchers":0,"Batters":0},"use_max_difference_exposure":null,"max_difference_exposure":null,"optimize_by":"pfp","optimize_for_speed":true,"optimize_for_speed_value":10,"player_groups":[],"position_stacks":[],"profile":"Default","site":"draftkings","slate":"' + slate + '","smart_random":null,"spec_positions_by_real_positions":null,"sport":"' + sport + '","team_stack_groups":[],"teams_min_max":[],"time_beginning":"20220421","use_random":0,"user_id":936,"username":"aml","uniques":1,"model_settings":{},"is_v2":false,"token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo5MzYsInNsYXRlIjoiZGs2NzU1NiJ9.HgqmmId6R_1tydgmFu8TZot4ByFW-lLh2_oeuov572A"}'

ws.send(mlb_payload)

response = ws.recv()
print(response)

ws.close()
generate_lineups_file_from_dfs_cruncher_response(response, 'ws', sport)


