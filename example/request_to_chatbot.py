import argparse

import httpx

parser = argparse.ArgumentParser(description="Send message to chatbot")
parser.add_argument("--session_id", required=True, help="Session ID for the request")
parser.add_argument("--content", required=True, help="Message content to send")

args = parser.parse_args()

url = "http://127.0.0.1:8000/message"

headers = {
    "X-OAuth-Token": "1", 
    "X-Session-Id": args.session_id,
    "Content-Type": "application/json"
}

data = {
    "content": args.content
}

with httpx.stream("POST", url, headers=headers, json=data, timeout=None) as response:
    if response.status_code != 200:
        print(f"\nError: {response.status_code} - {response.text}")
    else:
        for chunk in response.iter_text():
            print(chunk, end="", flush=True)