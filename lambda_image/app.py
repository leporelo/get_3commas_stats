import json
import boto3
from datetime import datetime, date, timedelta
import dateutil.parser
import dateutil.tz
import hmac
import hashlib
import requests
from requests.structures import CaseInsensitiveDict

key='INSERT_KEY'
secret='INSERT_SECRET'
url='/public/api/ver1/deals?scope=finished&limit=100'
relative_url = f"{url}"
prefix = "https://api.3commas.io"

dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
table_name = 'TABLE_NAME'
table = dynamodb.Table(table_name)

def generate_signature(path: str) -> str:
    encoded_key = str.encode(secret)
    message = str.encode(path)
    signature = hmac.new(encoded_key, message, hashlib.sha256).hexdigest()
    return signature

def get_data(signature: str):
    headers = CaseInsensitiveDict()
    headers["APIKEY"] = key
    headers["Signature"] = signature
    resp = requests.get(prefix+url, headers=headers)
    return resp.json()

def insert_record(data):
    dates = {}
    count = 0
    to_zone = dateutil.tz.gettz('Europe/Zurich')
    # today = datetime.now().strftime('%Y-%m-%d')
    today = date.today()
    str_today = str(today)
    yesterday = date.today()
    yesterday = yesterday - timedelta(days = 1)

    for deal in data:
        # print(deal)
        timestamp = dateutil.parser.parse(deal['closed_at'])
        convert = timestamp.astimezone(to_zone)
        convert = convert.strftime('%Y-%m-%d')

        dates[convert] = {}

    if str_today not in dates:
        dates[str_today] = {}

    for deal in data:
        # print(deal)
        timestamp = dateutil.parser.parse(deal['closed_at'])
        convert = timestamp.astimezone(to_zone)
        convert = convert.strftime('%Y-%m-%d')
        dates[convert][str(deal['id'])] = round(float(deal['usd_final_profit']),2)
    total_value = 0
    

    for date1,row in dates.items():
        day_value = 0
        if date1 == str_today:
            for k,v in row.items():
                day_value += v
                total_value += v
            update_table(date1, str(round(day_value,2)))
        elif date1 == str(yesterday):
            for k,v in row.items():
                day_value += v
                total_value += v
            update_table(date1, str(round(day_value,2)))

def update_table(date, value):
        table.put_item(
            Item={
                'date': date,
                'profit': value
            }
        )

def handler(event, context):
    signature = generate_signature(relative_url)
    data = get_data(signature)
    insert_record(data)
