#!/usr/bin/env python3
"""
Utility script to fetch Lambda function logs for debugging.

Usage:
    python3 get_lambda_logs.py [function_name] [--hours HOURS]

If function_name is not provided, it will attempt to find the Songs API Lambda function.
"""

import os
import sys
import boto3
import argparse
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

def get_api_lambda_name():
    """Get the Lambda function name from API Gateway integration."""
    client = boto3.client("apigatewayv2", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    
    # Find the Songs API
    apis = client.get_apis()
    for api in apis["Items"]:
        if "songs" in api["Name"].lower():
            api_id = api["ApiId"]
            break
    else:
        raise ValueError("Could not find Songs API in API Gateway v2")

    # Get Lambda function name from API Gateway integration
    integrations = client.get_integrations(ApiId=api_id)
    for integration in integrations["Items"]:
        if integration["IntegrationType"] == "AWS_PROXY":
            lambda_arn = integration["IntegrationUri"].split(":")[-1]
            return lambda_arn.split("/")[-1]
    
    raise ValueError("Could not find Lambda integration for API")

def get_lambda_logs(function_name, hours=1):
    """Fetch logs for a Lambda function."""
    client = boto3.client('logs')
    
    # Calculate start time
    start_time = int((datetime.now() - timedelta(hours=hours)).timestamp() * 1000)
    
    # Get log streams
    log_group = f"/aws/lambda/{function_name}"
    try:
        streams = client.describe_log_streams(
            logGroupName=log_group,
            orderBy='LastEventTime',
            descending=True,
            limit=5
        )
    except ClientError as e:
        print(f"Error getting log streams: {e}")
        return

    # Get logs from each stream
    for stream in streams['logStreams']:
        print(f"\n=== Log Stream: {stream['logStreamName']} ===")
        try:
            response = client.get_log_events(
                logGroupName=log_group,
                logStreamName=stream['logStreamName'],
                startTime=start_time,
                limit=100
            )
            
            for event in response['events']:
                timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
                print(f"{timestamp}: {event['message']}")
                
        except ClientError as e:
            print(f"Error getting logs: {e}")

def main():
    parser = argparse.ArgumentParser(description='Fetch Lambda function logs')
    parser.add_argument('function_name', nargs='?', help='Lambda function name')
    parser.add_argument('--hours', type=int, default=1, help='Number of hours of logs to fetch')
    
    args = parser.parse_args()
    
    try:
        function_name = args.function_name or get_api_lambda_name()
        print(f"Fetching logs for Lambda function: {function_name}")
        get_lambda_logs(function_name, args.hours)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 