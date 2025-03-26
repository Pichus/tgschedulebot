import re
import gspread
import requests
from black.trans import defaultdict
from google.oauth2.service_account import Credentials
from gspread import Worksheet

spreadsheet_id = "1kfdlUUWgZ9PKdL4oqJi-Og_Bz--ll-hF2yYgpfrxF4U"
sheet_name = "бакалаври"

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

credentials = Credentials.from_service_account_file("./credentials.json", scopes=scopes)

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


def get_schedule_by_group_index_and_day(
    arg_values, week_type: str, group_index: str = ""
) -> str:
    days = ["понеділок", "вівторок", "середа", "четвер", "п'ятниця"]
    result_dict: dict[str, dict[str, list]] = {}

    result_lines = []

    for day in days:
        result_dict[day] = defaultdict(list)

    group_index_col = arg_values[1].index(group_index)

    for value in arg_values:
        value_day = "".join(value[0].split()).lower()

        if value_day not in days:
            continue

        time_interval = value[1]
        subject = value[group_index_col]
        time_interval_dict_key = time_interval

        if (not result_dict[value_day].get(time_interval_dict_key)) or (
            subject not in result_dict[value_day][time_interval_dict_key]
        ):
            result_dict[value_day][time_interval_dict_key].append(subject)

    day: str
    schedule_dict: dict[str, list]
    for day, schedule_dict in result_dict.items():
        result_lines.append(day.capitalize() + "\n\n")

        time: str
        subjects: list
        for time, subjects in schedule_dict.items():
            if (len(subjects) == 1) or (week_type == "верхній"):
                subject_to_add = subjects[0]
            else:
                subject_to_add = subjects[1]

            time = time.replace("\n", "")
            subject_to_add = re.sub(" +", " ", subject_to_add)
            result_lines.append(time + " " + subject_to_add + "\n\n")

    return "".join(result_lines)


# print(whole_schedule(values, "верхній", "К-16"))
print(get_schedule_by_group_index_and_day(values, "верхній", "К-16"))
