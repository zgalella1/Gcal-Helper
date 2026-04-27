import os
from flask import Flask, request
import requests
from dateparser import parse
from datetime import timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)

TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# Google Calendar setup
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'credentials.json'
calendar_id = 'primary'

creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('calendar', 'v3', credentials=creds)

def send_telegram(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    chat_id = data["message"]["chat"]["id"]
    text = data["message"]["text"]

    dt = parse(text)

    if not dt:
        send_telegram(chat_id, "Couldn't understand date/time 😕")
        return "ok"

    end = dt + timedelta(hours=1)

    event = {
        'summary': text,
        'start': {'dateTime': dt.isoformat(), 'timeZone': 'America/New_York'},
        'end': {'dateTime': end.isoformat(), 'timeZone': 'America/New_York'},
    }

    service.events().insert(calendarId=calendar_id, body=event).execute()

    send_telegram(chat_id, f"Added: {text} ✅")

    return "ok"
