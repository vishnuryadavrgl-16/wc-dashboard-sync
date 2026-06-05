import pandas as pd
import gspread
import time
from auth import get_credentials

# =========================
# SHEET CONFIG
# =========================
SOURCE_SHEET_ID = "1kyRGC_FMo1DQkU5NUz0Y3lAklYAa5Tvq9VklGvyl7co"
SOURCE_TAB_NAME = "From Diamond Buying Sheet"

DEST_SHEET_ID = "1x6CzQjtflcb6G6rnEIX7ojXZvkC2_ZxRkMtpPJ8jERk"
DEST_TAB_NAME = "Engagement Analysis"

print("AUTHENTICATING...")

gc = gspread.authorize(get_credentials())

# =========================
# DOWNLOAD SOURCE (FIXED)
# =========================
print("Downloading from SOURCE sheet...")

source_sheet = gc.open_by_key(SOURCE_SHEET_ID)
source_ws = source_sheet.worksheet(SOURCE_TAB_NAME)

data = source_ws.get_all_values()

if not data:
    raise Exception("Source sheet is empty")

df = pd.DataFrame(data[1:], columns=data[0])

print(f"Rows downloaded: {len(df)}")
print(f"Columns: {len(df.columns)}")

# =========================
# CLEAN (SAFE)
# =========================
df = df.fillna("")

upload_data = [df.columns.tolist()] + df.values.tolist()

# =========================
# DESTINATION
# =========================
print("Connecting to destination...")

dest_sheet = gc.open_by_key(DEST_SHEET_ID)
ws = dest_sheet.worksheet(DEST_TAB_NAME)

# =========================
# FULL REFRESH (SAFE)
# =========================
print("Clearing destination sheet...")

ws.clear()
time.sleep(2)

ws.resize(rows=len(upload_data) + 100, cols=len(df.columns))

print("Uploading...")

chunk_size = 200

for i in range(0, len(upload_data), chunk_size):
    chunk = upload_data[i:i + chunk_size]

    ws.update(
        range_name=f"A{i+1}",
        values=chunk,
        value_input_option="USER_ENTERED"
    )

    print(f"Uploaded rows {i+1} - {i+len(chunk)}")
    time.sleep(1)

print("FULL SYNC COMPLETE (SOURCE → DESTINATION)")