import boto3
import json
from datetime import datetime
import dateutil.parser
import dateutil.tz

dynamodb_client = boto3.client('dynamodb', region_name='eu-central-1')
table_name = 'TABLE_NAME'

def lambda_handler(event, context):
    existing_tables = dynamodb_client.list_tables()['TableNames']
    if table_name not in existing_tables:
        create_table()
        populate(table_name)
    else:
        populate(table_name)
        
def populate(table_name):
    count = 0
    dynamodb = boto3.resource('dynamodb', region_name='eu-central-1')
    table = dynamodb.Table(table_name)
    
    with open('deals', 'r') as openfile:
            data = json.load(openfile)
            
    dates = {}
    to_zone = dateutil.tz.gettz('Europe/Zurich')
    today = datetime.now().strftime('%Y-%m-%d')   
        
    for deal in data:
        timestamp = dateutil.parser.parse(deal['closed_at'])
        convert = timestamp.astimezone(to_zone)
        convert = convert.strftime('%Y-%m-%d')
    
        if today not in dates:
            dates[today] = {}
            dates[today][str(deal['id'])] = round(float(deal['final_profit']),2)
        elif convert not in dates:
            dates[convert] = {}
            dates[convert][str(deal['id'])] = round(float(deal['usd_final_profit']),2)
        else:
            dates[convert][str(deal['id'])] = round(float(deal['final_profit']),2)
        count += 1
        
    total_value = 0
    
    for date,row in dates.items():
        day_value = 0
        for k,v in row.items():
            day_value += v
            total_value += v
            table.put_item(
                Item={
                    'date': date,
                    'profit': str(round(day_value,2))
                }
                )
        print(date, round(day_value,2))
    print(round(total_value,2))

def create_table():
    table = dynamodb_client.create_table(
        TableName=table_name,
        KeySchema=[
            {
                'AttributeName': 'date',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'date',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )
