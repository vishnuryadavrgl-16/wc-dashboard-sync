import pandas as pd
import time
import gspread
from auth import get_credentials

# =========================
# AUTH
# =========================
gc = gspread.authorize(get_credentials())

# =========================
# CONFIG
# =========================
SOURCE_SHEET_ID = "17lSgib7ggxLB88YBe_fxsc1niDk5QcmOMn6_V1dJ98A"
DEST_SHEET_ID = "1x6CzQjtflcb6G6rnEIX7ojXZvkC2_ZxRkMtpPJ8jERk"

SOURCE_TAB_NAME = "Order"
DEST_TAB_NAME = "Order"

CUTOVER_DATE = pd.Timestamp("2026-01-01")
CUTOVER_ORDER_ID = "WC2032926"

# =========================
# DOWNLOAD
# =========================
def download_tab():
    sh = gc.open_by_key(SOURCE_SHEET_ID)
    ws = sh.worksheet(SOURCE_TAB_NAME)

    data = ws.get_all_values()

    if not data:
        return pd.DataFrame()

    return pd.DataFrame(data[1:], columns=data[0])

# =========================
# CLEAN DATE PARSING
# =========================
def prepare(df):

    # --- parse date safely ---
    if "Purchase" in df.columns:
        df["Purchase"] = pd.to_datetime(
            df["Purchase"],
            errors="coerce",
            dayfirst=False
        )

    # =========================
    # PRIMARY FILTER: DATE CUTOVER
    # =========================
    if "Purchase" in df.columns:
        df = df[df["Purchase"] >= CUTOVER_DATE].copy()

    # =========================
    # SECONDARY FILTER: ORDER ID CUTOVER (SAFETY)
    # =========================
    if "order_id" in df.columns:

        df["order_id"] = df["order_id"].astype(str)

        df = df[
            (df["order_id"] >= CUTOVER_ORDER_ID)
            | (df["Purchase"] >= CUTOVER_DATE)
        ].copy()

    return df

# =========================
# CLEAN FORMATTING
# =========================
def clean(df):
    df = df.fillna("")

    # convert dates back to stable string format (avoid ' issue)
    if "Purchase" in df.columns:
        df["Purchase"] = df["Purchase"].dt.strftime("%Y-%m-%d")

    return df

# =========================
# UPLOAD
# =========================
def upload(ws, df):

    values = [df.columns.tolist()] + df.values.tolist()

    ws.clear()
    time.sleep(1)

    chunk_size = 1000

    for i in range(0, len(values), chunk_size):

        chunk = values[i:i + chunk_size]

        ws.update(
            range_name=f"A{i+1}",
            values=chunk,
            value_input_option="USER_ENTERED"
        )

        print(f"Uploaded rows {i+1} - {i + len(chunk)}")

        time.sleep(0.2)

# =========================
# MAIN
# =========================
def run():

    print("\n====================")
    print("ORDER SYNC (CUTOFF MODE)")
    print("====================")

    df = download_tab()
    print("Downloaded rows:", len(df))

    df = prepare(df)
    print("After cutover filter:", len(df))

    df = clean(df)

    dest = gc.open_by_key(DEST_SHEET_ID)
    ws = dest.worksheet(DEST_TAB_NAME)

    upload(ws, df)

    print("\nSYNC COMPLETE (FROM 2026 CUTOVER)")


if __name__ == "__main__":
    run()