#!/usr/bin/env python3

import os
import sys
import shutil
import uuid
import boto3
import logging
from pathlib import Path
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from tqdm import tqdm
from botocore.exceptions import ClientError
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configuration
AWS_REGION = 'us-east-1'
DYNAMODB_TABLE = 'DatabaseStack-SongsTable64F8B317-1AKO0N84TMQ16'
S3_BUCKET = 'ourchants-songs'
SOURCE_DIR = '/Users/williamprior/Music/Music/Media.localized'

def find_audio_files(directory):
    """Find all MP3 and M4A files in the given directory and its subdirectories."""
    audio_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.mp3', '.m4a')):
                audio_files.append(os.path.join(root, file))
    return audio_files

def extract_metadata(file_path):
    """Extract metadata from MP3 or M4A file."""
    try:
        logger.info(f"Extracting metadata from: {os.path.basename(file_path)}")
        metadata = {
            'title': '',
            'artist': '',
            'album': '',
            'genre': '',
            'composer': '',
            'duration': '',
            'filename': os.path.basename(file_path),
            'filepath': file_path,
            'track_number': '',
            'disc_number': '',
            'year': '',
            'bpm': '',
            'lyrics': '',
            'comment': '',
            'copyright': '',
            'publisher': '',
            'encoded_by': '',
            'date_added': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }

        if file_path.lower().endswith('.mp3'):
            audio = MP3(file_path, ID3=EasyID3)
            # Extract all available ID3 tags
            for key in audio.keys():
                if key in ['title', 'artist', 'album', 'genre', 'composer', 'tracknumber', 
                          'discnumber', 'date', 'bpm', 'lyrics', 'comment', 'copyright', 
                          'publisher', 'encodedby']:
                    value = audio.get(key, [''])[0]
                    if key == 'tracknumber':
                        metadata['track_number'] = value
                    elif key == 'discnumber':
                        metadata['disc_number'] = value
                    elif key == 'date':
                        metadata['year'] = value
                    else:
                        metadata[key] = value
            metadata['duration'] = str(int(audio.info.length))
        else:  # M4A
            audio = MP4(file_path)
            # Map MP4 tags to our metadata fields
            tag_map = {
                '\xa9nam': 'title',
                '\xa9ART': 'artist',
                '\xa9alb': 'album',
                '\xa9gen': 'genre',
                '\xa9wrt': 'composer',
                'trkn': 'track_number',
                'disk': 'disc_number',
                '\xa9day': 'year',
                'tmpo': 'bpm',
                '\xa9lyr': 'lyrics',
                '\xa9cmt': 'comment',
                'cprt': 'copyright',
                '\xa9pub': 'publisher',
                '\xa9too': 'encoded_by'
            }
            for mp4_tag, our_tag in tag_map.items():
                if mp4_tag in audio:
                    value = audio[mp4_tag][0]
                    if isinstance(value, (list, tuple)):
                        value = value[0]
                    metadata[our_tag] = str(value)
            metadata['duration'] = str(int(audio.info.length))

        # Clean up metadata
        for key, value in metadata.items():
            if value is None:
                metadata[key] = ''
        
        # Log extracted metadata
        logger.info("Metadata extracted:")
        for key, value in metadata.items():
            if value:  # Only log non-empty values
                logger.info(f"  {key}: {value}")
        
        return metadata
    except Exception as e:
        logger.error(f"Error extracting metadata from {file_path}: {str(e)}")
        return None

def upload_to_s3(s3_client, file_path, bucket_name):
    """Upload file to S3 bucket."""
    try:
        key = os.path.basename(file_path)
        logger.info(f"Uploading to S3: {key}")
        s3_client.upload_file(file_path, bucket_name, key)
        logger.info(f"Successfully uploaded to S3: {key}")
        return key
    except ClientError as e:
        logger.error(f"Error uploading {file_path} to S3: {str(e)}")
        return None

def add_to_dynamodb(dynamodb_client, song_data):
    """Add song metadata to DynamoDB table."""
    try:
        logger.info(f"Adding to DynamoDB: {song_data['filename']}")
        
        # Convert all metadata to DynamoDB format
        item = {
            'song_id': {'S': str(uuid.uuid4())},
            's3_uri': {'S': f"s3://{S3_BUCKET}/{song_data['s3_key']}"},
            'date_added': {'S': song_data['date_added']}
        }
        
        # Add all other fields if they have values
        for key, value in song_data.items():
            if key not in ['s3_key', 'date_added'] and value:
                item[key] = {'S': str(value)}
        
        dynamodb_client.put_item(
            TableName=DYNAMODB_TABLE,
            Item=item
        )
        logger.info(f"Successfully added to DynamoDB: {song_data['filename']}")
        return True
        except ClientError as e:
        logger.error(f"Error adding song to DynamoDB: {str(e)}")
        return False

def main():
    # Initialize AWS clients
    s3_client = boto3.client('s3', region_name=AWS_REGION)
    dynamodb_client = boto3.client('dynamodb', region_name=AWS_REGION)

    # Find all audio files
    logger.info(f"Searching for audio files in {SOURCE_DIR}...")
    audio_files = find_audio_files(SOURCE_DIR)
    
    if not audio_files:
        logger.warning("No audio files found.")
        return

    logger.info(f"Found {len(audio_files)} audio files.")
    
    # Process files
    successful_uploads = 0
    failed_uploads = []
    
    for file_path in tqdm(audio_files, desc="Processing files"):
        try:
            # Extract metadata
            metadata = extract_metadata(file_path)
            if not metadata:
                failed_uploads.append((file_path, "Metadata extraction failed"))
                continue

            # Upload to S3
            s3_key = upload_to_s3(s3_client, file_path, S3_BUCKET)
            if not s3_key:
                failed_uploads.append((file_path, "S3 upload failed"))
                continue

            # Add metadata to DynamoDB
            metadata['s3_key'] = s3_key
            if add_to_dynamodb(dynamodb_client, metadata):
                successful_uploads += 1
            else:
                failed_uploads.append((file_path, "DynamoDB update failed"))
    except Exception as e:
            logger.error(f"Unexpected error processing {file_path}: {str(e)}")
            failed_uploads.append((file_path, f"Unexpected error: {str(e)}"))

    # Print summary
    logger.info("\n=== Upload Summary ===")
    logger.info(f"Total files found: {len(audio_files)}")
    logger.info(f"Successfully processed: {successful_uploads}")
    logger.info(f"Failed: {len(failed_uploads)}")
    
    if failed_uploads:
        logger.info("\nFailed uploads:")
        for file_path, reason in failed_uploads:
            logger.info(f"- {os.path.basename(file_path)}: {reason}")

if __name__ == "__main__":
    main() 