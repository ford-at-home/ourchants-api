import json
import boto3
from botocore.exceptions import ClientError
import os
from uuid import uuid4

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])

def lambda_handler(event, context):
    try:
        http_method = event['httpMethod']
        path = event['path']
        
        if path == '/songs':
            if http_method == 'GET':
                return list_songs()
            elif http_method == 'POST':
                return create_song(json.loads(event['body']))
        elif path.startswith('/songs/'):
            song_id = path.split('/')[-1]
            if http_method == 'GET':
                return get_song(song_id)
            elif http_method == 'PUT':
                return update_song(song_id, json.loads(event['body']))
            elif http_method == 'DELETE':
                return delete_song(song_id)
        
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'Method Not Allowed'})
        }
    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def list_songs():
    response = table.scan()
    return {
        'statusCode': 200,
        'body': json.dumps(response.get('Items', []))
    }

def create_song(song_data):
    song_data['song_id'] = str(uuid4())
    table.put_item(Item=song_data)
    return {
        'statusCode': 201,
        'body': json.dumps(song_data)
    }

def get_song(song_id):
    response = table.get_item(Key={'song_id': song_id})
    item = response.get('Item')
    if item is None:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Song not found'})
        }
    return {
        'statusCode': 200,
        'body': json.dumps(item)
    }

def update_song(song_id, update_data):
    # Build update expression
    update_expr = 'SET '
    expr_names = {}
    expr_values = {}
    
    for key, value in update_data.items():
        if key != 'song_id':  # Don't update the primary key
            update_expr += f'#{key} = :{key}, '
            expr_names[f'#{key}'] = key
            expr_values[f':{key}'] = value
    
    update_expr = update_expr.rstrip(', ')
    
    response = table.update_item(
        Key={'song_id': song_id},
        UpdateExpression=update_expr,
        ExpressionAttributeNames=expr_names,
        ExpressionAttributeValues=expr_values,
        ReturnValues='ALL_NEW'
    )
    return {
        'statusCode': 200,
        'body': json.dumps(response['Attributes'])
    }

def delete_song(song_id):
    table.delete_item(Key={'song_id': song_id})
    return {
        'statusCode': 204,
        'body': ''
    } 