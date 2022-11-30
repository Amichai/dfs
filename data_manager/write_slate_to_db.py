import boto3
from decimal import Decimal
import json
import datetime
from projection_providers.NBA_WNBA_Projections import NBA_WNBA_Projections
import utils

start_times = utils.load_start_times_and_slate_path('start_times.txt')[0]
print(start_times)

slate_id = utils.TODAYS_SLATE_ID_NBA
slate_name = "7pm ET Main"


slate_path = utils.most_recently_download_filepath('FanDuel-NBA-', slate_id, '-players-list', '.csv')

projections = NBA_WNBA_Projections(slate_path, "NBA")

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('MLE_Slates')
timestamp = str(datetime.datetime.now())
date = timestamp.split(' ')[0]

slates = {slate_id: slate_name}

to_write = {
    'date': date,
    'timestamp': timestamp,
    'slates': json.dumps(slates),
    'start_times': json.dumps(start_times),
    'player_data': json.dumps(list(projections.fd_players.values()))
}

to_write = json.loads(json.dumps(to_write), parse_float=Decimal)

try:
    result = table.put_item(
      Item=to_write
    )
    print("UPLOADED SLATE!")
except Exception as err:
    print("Error:", err)