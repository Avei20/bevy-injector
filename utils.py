from time import sleep

import numpy as np
import pandas as pd
import os
import requests
import logging as log

BASE_URL = 'https://gdg.community.dev/api'

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
        "event": os.getenv("EVENT_ID"),
        "attendees": [],
    }
    for index, row in df.iterrows():
        body["attendees"].append({
            "email": row["Email Address"],
            "first_name": row["First Name"],
            "last_name": row["Last Name"],
            "is_checked_in": False,
            "send_event_email": False,
        })
    return body

def transform_body(row):
    last_name = row["Last Name"]
    if row['Last Name'] == "":
        last_name = row['First Name']
    return {
        "event": os.getenv("EVENT_ID"),
        "attendees": [
            {
                "email": row["Email Address"],
                "first_name": row["First Name"],
                "last_name": last_name,
                "is_checked_in": False,
                "send_event_email": False,
            }
        ],
    }

def inject_attendees(df):
    df['Status'] = df['Status'].astype(str)

    for index, row in df.iterrows():
        print("Injecting attendee at {} from {} total datas".format(index + 1, len(df)))
        if df['Status'] == 'Injected':
            continue

        body = transform_body(row)
        res = inject_attendee(body)
        if res.status_code == 201:
            df.at[index, "Status"] = 'Injected'
        else:
            df.at[index, "Status"] = res.json()

def inject_attendee(body):
    url = f"{BASE_URL}/attendee/?event={os.getenv('EVENT_ID')}&chapter={os.getenv('CHAPTER_ID')}"
    # print(get_header())
    response = requests.post(url, headers=get_header(), json=body)
    print(response.status_code)
    print(response.json())
    return response

def update_data(df, response):
    df['Status'] = df['Status'].astype(str)
    df['TicketId'] = df['TicketId'].astype(str)
    for d in response:
        email = d["email"]
        # find row by email
        df.loc[df['Email Address'] == email, 'Status'] = 'Injected'
        df.loc[df['Email Address'] == email, 'TicketId'] = d['id']

    return df

def blast_emails(df):
    for index, row in df.iterrows():
        print("Processing Sending Email {} data from {} total data".format(index + 1, len(df)))
        if row['Status'] == "Injected":
            res = blast_email(row['TicketId'])
            print(res)
            df.at[index, 'Is Email Sent'] = True
            sleep(1)

def blast_qr():
    attendees = get_attendees()
    i = 1
    for a in attendees:
        print(f"Blasting for ticketId {a['id']} on {i} from {len(attendees)} datas.")
        if i < 258:
            print("Skipping blast email for ticketId {}".format(a['id']))
            i = i + 1
            continue

        resp = blast_email(a['id'])
        print(resp.status_code)
        print(resp.json())
        i = i + 1

def get_attendees():
    url = f'{BASE_URL}/attendee_search/?event={os.getenv("EVENT_ID")}&chapter={os.getenv("CHAPTER_ID")}&page_size=3000'

    response = requests.get(url, headers=get_header())
    print(response.status_code)
    print(response.json())
    return response.json()['results']

def blast_email(ticket_id):
    url = f"{BASE_URL}/attendee/{ticket_id}/send_event_email/?chapter={os.getenv('CHAPTER_ID')}"

    body = {
        "notification_email_countdown": 7
    }

    resp = requests.put(url, headers=get_header(), json=body)
    return resp