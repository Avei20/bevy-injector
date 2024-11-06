import csv
import os
import pandas as pd

from dotenv import load_dotenv
from utils import body_transformer, inject_attendees

if __name__ == '__main__':
    load_dotenv()

    df = pd.read_csv(f"./data/{os.getenv('FILENAME')}")

    # Transfrom into Accepted Body by Bevy
    body = body_transformer(df)
    print(body)

    # Injecting to Attendees .
    attendees = inject_attendees(body)

    # Checkin .


    # Blast Email.
