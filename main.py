import csv
import os
import pandas as pd

from dotenv import load_dotenv
from utils import body_transformer, inject_attendees, update_data, blast_emails, blast_qr

if __name__ == '__main__':
    load_dotenv()

    df = pd.read_csv(f"./data/{os.getenv('FILENAME')}")
    df.to_csv(f'./data/backup/bak-{os.getenv("FILENAME")}', index=False)

    # Transfrom into Accepted Body by Bevy
    # body = body_transformer(df)
    # print(body)

    # Injecting to Attendees
    if os.getenv("IS_INJECT") == "TRUE":
        try:
            inject_attendees(df)
        except Exception as e:
            print (e)
    # Update Df
    # df = update_data(df, attendees)
    df.to_csv(f"./data/backup/01-{os.getenv('FILENAME')}", index=False)

    # Checkin
    if os.getenv("ONLY_BLAST") == "TRUE":
        blast_qr()

    # Blast Email
    if os.getenv("IS_BLAST") != "TRUE":
        df['Is Email Sent'] = False

    if os.getenv("IS_BLAST") == 'TRUE':
        try:
            blast_emails(df)
        except Exception as e:
            print(e)

        df.to_csv(f"./data/backup/02-blast-{os.getenv('FILENAME')}", index=False)

    df.to_csv(f"./data/{os.getenv('FILENAME')}", index=False)
