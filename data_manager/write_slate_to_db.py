import boto3
from decimal import Decimal
import json
import datetime
from projection_providers.NBA_WNBA_Projections import NBA_WNBA_Projections
import utils

start_times = utils.load_start_times_and_slate_path('start_times.txt')[0]

hour_to_time = {
    1: '1:00pm ET',
    1.5: '1:30pm ET',
    2: '2:00pm ET',
    2.5: '2:30pm ET',
    3: '3:00pm ET',
    3.5: '3:30pm ET',
    4: '4:00pm ET',
    4.5: '4:30pm ET',
    4.02: '4:05pm ET',
    4.48: '4:25pm ET',
    5: '5:00pm ET',
    5.5: '5:30pm ET',
    6: '6:00pm ET',
    6.5: '6:30pm ET',
    7: '7:00pm ET',
    7.5: '7:30pm ET',
    7.15: '7:15pm ET',
    7.85: '7:45pm ET',
    8: '8:00pm ET',
    8.5: '8:30pm ET',
    8.15: '8:15pm ET',
    8.85: '8:45pm ET',
    8.2: '8:20pm ET',
    9: '9:00pm ET',
    9.5: '9:30pm ET',
    9.15: '9:15pm ET',
    9.85: '9:45pm ET',
    10: '10:00pm ET',
    10.5: '10:30pm ET',
    10.15: '10:15pm ET',
    10.85: '10:45pm ET',
    11: '11:00pm ET',
    11.5: '11:30pm ET',
    11.1: '11:15pm ET'
}

earliest_start_time = min(list(start_times.keys()))
time_string = hour_to_time[earliest_start_time]

slate_id = utils.TODAYS_SLATE_ID_NBA
slate_name = "{} Main".format(time_string)

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
print(to_write)

try:
    result = table.put_item(
      Item=to_write
    )
    print("UPLOADED SLATE!")
except Exception as err:
    print("Error:", err)