import pandas as pd
import os
import requests

BASE_URL = 'https://gdg.community.dev/api/'

def get_header():
    return {
        "Content-Type": "application/json",
        "Accept": "application/json; version=bevy.1.0",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en",
        "Cookie": 'correlation_key="google/c43a364e-fb10-4c80-813c-0c9f49c168a5"; csrftoken=4ZbCiSC4WlCy4EGFFAH0Q5lFVTTCaoVRjLNxucPLebInpac3nsH7rsr1CY9k6Yjh; sessionid=5s0pgpafg245ejw8bqf6fohayngwgjiw',
        "Priority": "u=1, i",
        "Referer": "https://gdg.community.dev/accounts/dashboard/",
        "Sec-Ch-Ua": '"Brave";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        "Sec-Ch-Ua-Platform": '"macOS',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Gpc": '1',
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "X-Csrftoken": "Dj0C7XEgxpem5Kfd8i2E6jT8cy7PXcIZS5CxjhRXPfkbqgLBQa2LHGZuTDnxTM6p",
        'X-Reuquested-With': "XMLHttpRequest"
    }

def body_transformer(df):
    # The goals is return a dict with this structure:
        # {
        #    "attendees": [
        #       {
        #           "email": "string",
        #           "first_name": "string",
        #           "last_name": "string",
        #           "is_chceked_in": "boolean",
        #           "sent_event_email": "boolean"
        #      }
        #   ],
        #  "event_id": "string"
        # }
    body = {
        "event_id": os.getenv("EVENT_ID"),
        "attendees": [],
    }
    for index, row in df.iterrows():
        body["attendees"].append({
            "email": row["Email Address"],
            "first_name": row["First Name"],
            "last_name": row["Last Name"],
            "is_checked_in": row['Is Check In'],
            "send_event_email": row["Is Email Sent"],
        })
    return body

def inject_attendees(body):
    url = f"{BASE_URL}/attendee/?event={os.getenv('EVENT_ID')}&chapter={os.getenv('CHAPTER_ID')}"
    print(url)
    # print(get_header())
    response = requests.post(url, headers=get_header(), json=body)
    print(response.status_code)
    print(response.json())
    return None
