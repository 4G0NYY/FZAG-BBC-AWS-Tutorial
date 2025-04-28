import requests
import time

# Hier müsst ihr eine Discord Webhook erstellen und den Link dazu eintragen
WEBHOOK_URL = "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"

def send_message(content):
    payload = {"content": content}
    response = requests.post(WEBHOOK_URL, json=payload)
    
    if response.status_code == 204:
        print(f"Sent message: {content}")
    else:
        print(f"Failed to send message: {response.status_code} - {response.text}")

send_message("Wow, das Skript funktioniert und somit funktioniert wahrscheinlich auch der Container")

while True:
    time.sleep(3600)  # Eine Stunde warten
    send_message("Hello")