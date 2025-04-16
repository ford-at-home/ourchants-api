#!/usr/bin/env python3

import json
import boto3
from botocore.exceptions import ClientError
import os
from typing import List, Dict
import uuid
from datetime import datetime

def load_songs(file_path: str) -> List[Dict]:
    """Load songs from a JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)

def transform_song(song: Dict) -> Dict:
    """Transform song data to match DynamoDB schema."""
    # Generate a unique song_id if not present
    if 'song_id' not in song:
        song['song_id'] = str(uuid.uuid4())
    
    # Add created_at timestamp if not present
    if 'created_at' not in song:
        song['created_at'] = datetime.utcnow().isoformat() + 'Z'
    
    # Map existing fields to our schema
    transformed = {
        'song_id': song['song_id'],
        'title': song.get('title', ''),
        'artist': song.get('artist', ''),
        'album': song.get('album', ''),
        'genre': song.get('genre', ''),
        'composer': song.get('composer', ''),
        'filename': song.get('filename', ''),
        'filepath': song.get('filepath', ''),
        'description': song.get('description', ''),
        'created_at': song['created_at']
    }
    
    return transformed

def upload_songs(songs: List[Dict], table_name: str = 'Songs') -> None:
    """Upload songs to DynamoDB table."""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    for song in songs:
        try:
            transformed_song = transform_song(song)
            table.put_item(Item=transformed_song)
            print(f"Uploaded song: {transformed_song['song_id']} - {transformed_song['title']}")
            
        except ClientError as e:
            print(f"Error uploading song {song.get('song_id', 'unknown')}: {e}")

def main():
    # Get the path to songs.json from the first command line argument
    import sys
    if len(sys.argv) != 2:
        print("Usage: python upload_songs.py <path_to_songs.json>")
        sys.exit(1)
        
    songs_file = sys.argv[1]
    
    try:
        songs = load_songs(songs_file)
        print(f"Loaded {len(songs)} songs from {songs_file}")
        upload_songs(songs)
        print("Upload complete!")
        
    except FileNotFoundError:
        print(f"Error: Could not find file {songs_file}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: {songs_file} is not valid JSON")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 