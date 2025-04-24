import boto3
import json
import time
import random
import botocore.exceptions

# Config
REGION = "us-east-1"
TABLE_NAME = "DatabaseStack-SongsTable64F8B317-1AKO0N84TMQ16"
MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

# Clients
dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(TABLE_NAME)
bedrock = boto3.client("bedrock-runtime", region_name=REGION)

def get_songs(limit=10):
    response = table.scan(Limit=limit)
    return response.get("Items", [])

def call_claude_messages(prompt, max_tokens=2000, temperature=0.7):
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps(body)
    )
    output = json.loads(response["body"].read())
    return output["content"][0]["text"].strip()

def infer_lineage(song_obj):
    prompt = (
        "You are an anthropologist and ethnomusicologist with expertise in sacred and spiritual music traditions.\n"
        "Given the following JSON object representing a song's metadata, make your best guess as to the spiritual "
        "lineage or cultural tradition this song might belong to.\n"
        "If there is not enough information to guess with any confidence, simply respond: 'Lineage unknown.'\n\n"
        f"```json\n{json.dumps(song_obj, indent=2)}\n```"
    )
    return call_claude_messages(prompt, max_tokens=2000, temperature=0.3)

def generate_poetic_metadata(song_obj, lineage_description):
    prompt = (
        f"Here is a JSON object containing song metadata:\n```json\n{json.dumps(song_obj, indent=2)}\n```\n"
        f"The song is believed to originate from the following spiritual tradition or lineage:\n"
        f"{lineage_description}\n\n"
        f"As a poetic storyteller, write a 3–5 sentence description imagining who may have sung this song, where they were, why they sang it, and what it might mean spiritually. "
        f"Use the song metadata and the lineage analysis to inspire the story, but you are free to be imaginative as long as it feels grounded and respectful. "
        f"Begin with: 'Song metadata analysis:'"
    )
    return call_claude_messages(prompt, max_tokens=2000, temperature=0.9)

def print_block(title, content):
    print(f"\n📜 {title}")
    print("―" * 80)
    print(content)
    print("―" * 80 + "\n")

def main():
    songs = get_songs(limit=10)
    if not songs:
        print("No songs found.")
        return

    for i, song in enumerate(songs, 1):
        title = song.get("title", "Unknown Title")
        artist = song.get("artist", "Unknown Artist")
        print("\n" + "=" * 100)
        print(f"🎶 [{i}] {title} — {artist}")
        print("=" * 100)

        lineage = None
        commentary = None

        # Retry lineage generation
        for attempt in range(3):
            try:
                lineage = infer_lineage(song)
                print_block("Inferred Lineage", lineage)
                break
            except botocore.exceptions.ClientError as e:
                if e.response["Error"]["Code"] == "ThrottlingException":
                    sleep_time = 2 ** attempt + random.random()
                    print(f"⚠️ Rate limited during lineage. Retrying in {sleep_time:.2f}s...\n")
                    time.sleep(sleep_time)
                else:
                    raise

        # Retry poetic commentary generation
        for attempt in range(3):
            try:
                commentary = generate_poetic_metadata(song, lineage)
                print_block("AI-Poetic Commentary", commentary)
                break
            except botocore.exceptions.ClientError as e:
                if e.response["Error"]["Code"] == "ThrottlingException":
                    sleep_time = 2 ** attempt + random.random()
                    print(f"⚠️ Rate limited during commentary. Retrying in {sleep_time:.2f}s...\n")
                    time.sleep(sleep_time)
                else:
                    raise

        if commentary is None:
            print_block("AI-Poetic Commentary", "❌ Skipped due to repeated throttling or failure.")

        time.sleep(1.5)


if __name__ == "__main__":
    main()
