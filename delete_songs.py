import boto3
import os
from typing import List

def delete_songs_with_matching_uri(table_name: str, search_string: str) -> int:
    """
    Delete all songs from DynamoDB that have an s3_uri containing the search string.
    
    Args:
        table_name (str): Name of the DynamoDB table
        search_string (str): String to match in s3_uri
        
    Returns:
        int: Number of items deleted
    """
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    # Scan the table to find all items
    response = table.scan()
    items = response.get('Items', [])
    
    # Continue scanning if there are more items
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response.get('Items', []))
    
    # Filter items with matching s3_uri
    items_to_delete = [
        item for item in items 
        if 's3_uri' in item and search_string in item['s3_uri']
    ]
    
    # Delete matching items
    deleted_count = 0
    with table.batch_writer() as batch:
        for item in items_to_delete:
            batch.delete_item(
                Key={
                    'song_id': item['song_id']
                }
            )
            deleted_count += 1
    
    return deleted_count

if __name__ == "__main__":
    # Get table name from environment variable or use the specific table name
    table_name = os.getenv('DYNAMODB_TABLE_NAME', 'DatabaseStack-SongsTable64F8B317-1AKO0N84TMQ16')
    search_string = 'ourchantsbucket'
    
    print(f"Searching for songs with s3_uri containing '{search_string}'...")
    deleted_count = delete_songs_with_matching_uri(table_name, search_string)
    print(f"Deleted {deleted_count} songs with matching s3_uri.") 