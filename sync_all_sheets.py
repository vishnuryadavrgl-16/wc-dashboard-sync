import pandas as pd
import time
import gspread
from auth import get_credentials

# =========================
# AUTH
# =========================
gc = gspread.authorize(get_credentials())

# =========================
# SHEET IDS
# =========================
SOURCE_SHEET_ID = "17lSgib7ggxLB88YBe_fxsc1niDk5QcmOMn6_V1dJ98A"
DEST_SHEET_ID = "1tGu5zmA5sce9iifZekYE1EnnGZREecygFZGIYeOgvDc"

IMPORT_DB_SHEET_ID = "1IvMRThSkeEG7-g9P9d3HHqrc7nBvywEidRCZZgrCPoM"
IMPORT_DB_TAB_NAME = "Importing DB"

# =========================
# NORMALIZATION
# =========================
def normalize(name: str) -> str:
    return (
        name.strip()
        .replace("_", " ")
        .replace("\u200b", "")
        .lower()
    )

# =========================
# SOURCE WORKSHEET
# =========================
def get_source_ws(sheet, tab_name):
    target = normalize(tab_name)

    for ws in sheet.worksheets():
        if normalize(ws.title) == target:
            return ws

    raise Exception(f"Source tab not found: {tab_name}")

# =========================
# DEST WORKSHEET
# =========================
def get_dest_ws(sheet, tab_name):
    target = normalize(tab_name)

    for ws in sheet.worksheets():
        if normalize(ws.title) == target:
            return ws

    raise Exception(f"Destination tab not found: {tab_name}")

# =========================
# DOWNLOAD
# =========================
def download_tab(sheet_id, tab_name):
    sh = gc.open_by_key(sheet_id)
    ws = get_source_ws(sh, tab_name)

    data = ws.get_all_values()

    if not data:
        return pd.DataFrame()

    return pd.DataFrame(data[1:], columns=data[0])

# =========================
# CLEAN
# =========================
def clean(df):
    df = df.fillna("")
    return df

# =========================
# UPLOAD
# =========================
def upload_tab(ws, df):

    df = clean(df)

    values = [df.columns.tolist()] + df.values.tolist()

    ws.clear()
    time.sleep(1)

    chunk_size = 1000
    i = 0

    while i < len(values):

        chunk = values[i:i + chunk_size]

        ws.update(
            range_name=f"A{i+1}",
            values=chunk,
            value_input_option="USER_ENTERED"
        )

        print(f"Uploaded rows {i+1} - {i + len(chunk)}")

        i += chunk_size
        time.sleep(0.2)

# =========================
# MAIN ENGINE
# =========================
def run():

    print("\n==============================")
    print("MASTER SYNC ENGINE START")
    print("==============================")

    source = gc.open_by_key(SOURCE_SHEET_ID)
    dest = gc.open_by_key(DEST_SHEET_ID)

    tabs = [
        "Order Summary",
        "Order Summary New",
        "Order Summary New _ Gross",
        "Order Summary New _ Actual Gross"   # ✅ NEW ADDED TAB
    ]

    for tab in tabs:

        print(f"\nProcessing: {tab}")

        df = download_tab(SOURCE_SHEET_ID, tab)

        print("Rows:", len(df))

        dest_ws = get_dest_ws(dest, tab)
        upload_tab(dest_ws, df)

        # =========================
        # EXTRA SYNC: Order Summary → Importing DB
        # =========================
        if tab == "Order Summary":

            print("Syncing Order Summary → Importing DB")

            import_db_sheet = gc.open_by_key(IMPORT_DB_SHEET_ID)
            import_ws = import_db_sheet.worksheet(IMPORT_DB_TAB_NAME)

            upload_tab(import_ws, df)

    print("\n==============================")
    print("SYNC COMPLETE")
    print("==============================")

if __name__ == "__main__":
    run()