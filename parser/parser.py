import gspread
import requests
from google.oauth2.service_account import Credentials
from gspread import Worksheet

spreadsheet_id = (
    "1kfdlUUWgZ9PKdL4oqJi-Og_Bz--ll-hF2yYgpfrxF4U"  # Please set the Spreadsheet ID.
)
sheet_name = "бакалаври"  # Please set the sheet name.

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = Credentials.from_service_account_file(
    './service_account.json',
    scopes=scopes
)

client = gspread.authorize(credentials)

client.open_by_key(spreadsheet_id)

access_token = client.http_client.auth.token
url = (
        "https://sheets.googleapis.com/v4/spreadsheets/"
        + spreadsheet_id
        + "?fields=sheets&ranges="
        + sheet_name
)
res = requests.get(url, headers={"Authorization": "Bearer " + access_token})
obj = res.json()

sheet = client.open_by_key(spreadsheet_id)
worksheet = sheet.worksheet(sheet_name)

# 1. All values are retrieved.
values = worksheet.get_all_values()

# 2. Put the values to the merged cells.
if "merges" in obj["sheets"][0].keys():
    for e in obj["sheets"][0]["merges"]:
        rows = len(values)
        if rows < e["endRowIndex"]:
            for i in range(0, e["endRowIndex"] - rows):
                values.append([""])
        for r in range(e["startRowIndex"], e["endRowIndex"]):
            cols = len(values[r])
            if cols < e["endColumnIndex"]:
                values[r].extend([""] * (e["endColumnIndex"] - cols))
            for c in range(e["startColumnIndex"], e["endColumnIndex"]):
                values[r][c] = values[e["startRowIndex"]][e["startColumnIndex"]]


def get_group_indexes(worksheet: Worksheet):
    raw_data = worksheet.row_values(2)
    return list(filter(lambda item: item, raw_data))


def get_schedule_by_group_index(worksheet: Worksheet, group_index: str):
    col = worksheet.find(group_index).col
    raw_data = worksheet.col_values(col)

    return list(filter(lambda item: item, raw_data))


def get_schedule_by_group_index_and_day(arg_values, day: str = "", group_index: str = ""):
    print(f"Розклад групи {group_index} на {day}")
    group_index_col = arg_values[1].index(group_index)
    time_intervals: dict = {}

    for value in arg_values:
        value_day = "".join(value[0].split()).lower()
        if value_day == day:
            time_interval = value[1]
            time_interval_dict_key = time_interval + value[group_index_col]

            if not time_intervals.get(time_interval_dict_key):
                print(time_interval)
                print(value[group_index_col])
                time_intervals[time_interval_dict_key] = 1


get_schedule_by_group_index_and_day(values, "середа", "К-17")
