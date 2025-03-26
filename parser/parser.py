import re
from typing import Any

import gspread
import requests
from black.trans import defaultdict
from google.oauth2.service_account import Credentials

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

values = worksheet.get_all_values()


def apply_merges(sheet_values: list[list], sheet_metadata: dict[str, Any]) -> None:
    if not "merges" in sheet_metadata.keys():
        return

    for merge in sheet_metadata["merges"]:
        rows = len(sheet_values)
        if rows < merge["endRowIndex"]:
            for i in range(0, merge["endRowIndex"] - rows):
                sheet_values.append([""])
        for row in range(merge["startRowIndex"], merge["endRowIndex"]):
            cols = len(sheet_values[row])
            if cols < merge["endColumnIndex"]:
                sheet_values[row].extend([""] * (merge["endColumnIndex"] - cols))
            for col in range(merge["startColumnIndex"], merge["endColumnIndex"]):
                sheet_values[row][col] = sheet_values[merge["startRowIndex"]][
                    merge["startColumnIndex"]
                ]


def get_schedule_by_group_index_and_day(arg_values, week_type: str, group_index) -> str:
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

        subject: str = value[group_index_col]

        if not subject or subject.isspace():
            subject = "empty_subject"

        time_interval = value[1]
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
            if len(subjects) > 1:
                if week_type == "верхній" and subjects[1] == "empty_subject":
                    subject_to_add = subjects[0]
                elif week_type == "нижній" and subjects[0] == "empty_subject":
                    subject_to_add = subjects[1]
                elif week_type == "верхній":
                    subject_to_add = subjects[0]
                elif week_type == "нижній":
                    subject_to_add = subjects[1]
            else:
                if subjects[0] == "empty_subject":
                    continue

                subject_to_add = subjects[0]

            time = time.replace("\n", "")
            if subject_to_add == "empty_subject":
                subject_to_add = "чіл в пузатці"
            subject_to_add = re.sub(" +", " ", subject_to_add)
            result_lines.append(time + " " + subject_to_add + "\n\n")

    return "".join(result_lines)


def main():
    apply_merges(values, obj["sheets"][0])
    print(get_schedule_by_group_index_and_day(values, "нижній", "К-16"))


main()
