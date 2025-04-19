import os
import boto3
from datetime import datetime, timedelta, timezone
from time import sleep

def get_lambda_logs(function_name, start_time=None, end_time=None):
    """Fetch logs from CloudWatch for the Lambda function."""
    if start_time is None:
        start_time = datetime.now(timezone.utc) - timedelta(hours=24)  # Look back 24 hours
    if end_time is None:
        end_time = datetime.now(timezone.utc)
    
    print(f"\nTime range: {start_time} to {end_time}")
    
    # Add a 10-second delay to ensure logs are available
    print("\nWaiting 10 seconds for logs to be available...")
    sleep(10)
    
    logs_client = boto3.client('logs')
    
    # Get log groups
    log_groups = logs_client.describe_log_groups(
        logGroupNamePrefix=f'/aws/lambda/{function_name}'
    )
    
    if not log_groups['logGroups']:
        return "No log groups found"
    
    log_group = log_groups['logGroups'][0]['logGroupName']
    print(f"\nFound log group: {log_group}")
    
    # Get log streams
    log_streams = logs_client.describe_log_streams(
        logGroupName=log_group,
        orderBy='LastEventTime',
        descending=True,
        limit=5
    )
    
    if not log_streams['logStreams']:
        return "No log streams found"
    
    print("\nFound log streams:")
    for stream in log_streams['logStreams']:
        print(f"- {stream['logStreamName']} (Last event: {datetime.fromtimestamp(stream['lastEventTimestamp']/1000, timezone.utc)})")
    
    # Get events from the most recent log stream
    log_stream = log_streams['logStreams'][0]['logStreamName']
    print(f"\nFetching events from stream: {log_stream}")
    
    events = logs_client.get_log_events(
        logGroupName=log_group,
        logStreamName=log_stream,
        startTime=int(start_time.timestamp() * 1000),
        endTime=int(end_time.timestamp() * 1000),
        limit=100
    )
    
    print(f"\nFound {len(events['events'])} events")
    print("\nLog Events:")
    print("=" * 80)
    for event in events['events']:
        print(event['message'])
    print("=" * 80)

if __name__ == "__main__":
    # Get Lambda function name from API Gateway
    client = boto3.client("apigatewayv2", region_name=os.environ.get("AWS_REGION", "us-east-1"))
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
            function_name = lambda_arn.split("/")[-1]
            break
    else:
        raise ValueError("Could not find Lambda integration for API")
    
    print(f"Found Lambda function: {function_name}")
    get_lambda_logs(function_name) 