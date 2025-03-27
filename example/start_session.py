import httpx

url = "http://127.0.0.1:8000/session"

headers = {
    "X-OAuth-Token": "1", 
}

with httpx.stream("POST", url, headers=headers,  timeout=None) as response:
    if response.status_code != 200:
        print(f"\nError: {response.status_code} - {response.text}")
    else:
        for chunk in response.iter_text():
            print(chunk, end="", flush=True)