import json
import boto3
from datetime import datetime, date, timedelta

client = boto3.client('iot-data', region_name='eu-central-1')

dynamodb_client = boto3.resource('dynamodb', region_name='eu-central-1')
table_name = 'TABLE_NAME'
table = dynamodb_client.Table(table_name)

def overall_stats():
    total_value = 0
    resp = table.scan(AttributesToGet=['profit'])
    for k in resp['Items']:
        total_value += float(k['profit'])
    return round(total_value,2)


def lambda_handler(event, context):
    
    today = date.today()
    today = str(today)
    
    profit = table.get_item(Key={
        'date': today})
        
    overall_profit = overall_stats()
    
    response = client.publish(
        topic='TOPIC/TO ACCEPT',
        qos=1,
        payload=json.dumps({ "today" : profit['Item']['profit'], "overall": overall_profit })
    )

