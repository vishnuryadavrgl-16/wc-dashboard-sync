import pandas as pd
import numpy as np
import gspread
import time

from auth import get_credentials

DEST_SHEET_ID = "1IvMRThSkeEG7-g9P9d3HHqrc7nBvywEidRCZZgrCPoM"
DEST_TAB_NAME = "Importing DB"

print("Reading CSV...")

df = pd.read_csv(
    "order_summary.csv",
    header=None,
    low_memory=False
)

print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")

print("Cleaning data...")

df = df.replace([np.inf, -np.inf], "")
df = df.fillna("")
df = df.astype(str)

data = df.values.tolist()

print(f"Prepared {len(data)} rows")

print("Connecting to Google Sheets...")

gc = gspread.authorize(get_credentials())

sheet = gc.open_by_key(DEST_SHEET_ID)
ws = sheet.worksheet(DEST_TAB_NAME)

print("Resizing sheet...")

required_rows = len(data)
required_cols = len(data[0])

ws.resize(rows=required_rows, cols=required_cols)

print("Clearing sheet...")

ws.clear()

print("Uploading...")

chunk_size = 50

for i in range(0, len(data), chunk_size):

    chunk = data[i:i + chunk_size]

    start_row = i + 1
    end_row = start_row + len(chunk) - 1

    ws.update(
        range_name=f"A{start_row}",
        values=chunk,
        value_input_option="RAW"
    )

    print(f"Uploaded rows {start_row}-{end_row}")

    time.sleep(2)

print("UPLOAD COMPLETE")