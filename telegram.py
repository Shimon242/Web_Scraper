import requests

TOKEN = "7817487510:AAHxFno48Um2htiDmWvFjijJWWYdx10DfE0"
CHAT_ID = "-1002573467611"  # your group chat ID
MESSAGE = "Hello, this is an automated message from my Python script!"

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

payload = {
    "chat_id": CHAT_ID,
    "text": MESSAGE
}

resp = requests.post(url, data=payload)

if resp.status_code == 200:
    print("✅ Message sent successfully!")
else:
    print("❌ Failed to send message:", resp.text)
