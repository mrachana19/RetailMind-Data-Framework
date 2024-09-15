import pandas as pd
import boto3
import time
from botocore.exceptions import ClientError

# Configuration
dynamodb = boto3.resource('dynamodb')
table_name = 'EcommDynamoDB'  # Replace with your DynamoDB table name

def load_data(file_name, table_name):
    table = dynamodb.Table(table_name)
    data = pd.read_csv(file_name)

    for index, row in data.iterrows():
        try:
            table.put_item(
                Item={
                    'user_id': row['user_id'],
                    'timestamp': row['timestamp'],
                    'action': row['action'],
                    'product_id': row['product_id'],
                }
            )
            print(f"Added item: {row['user_id']} at {row['timestamp']}")
        except ClientError as e:
            print(f"Could not add item: {e.response['Error']['Message']}")
        time.sleep(0.1)  # To avoid provisioned throughput exceeded error

if __name__ == '__main__':
    file_name = 'clickstream_data'  # Replace with your CSV file name
    load_data(file_name, table_name)
