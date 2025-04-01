import re
from collections import defaultdict
from typing import Any

import gspread
import requests
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
                sheet_values[row][col] = sheet_values[merge["startRowIndex"]][merge["startColumnIndex"]]


def format_subject_string(string_to_format: str):
    string_to_format = re.sub(r"\s+", " ", string_to_format)
    string_to_format = re.sub(r"\d\s?п/г", "", string_to_format) # maybe it should be removed
    subject_name = re.findall(r"(^.+?)(?:\()", string_to_format)
    if subject_name:
        string_to_format = string_to_format.replace(subject_name[0].strip(), "")
    string_to_format = re.sub(r"\(.+год", "", string_to_format)

    classroom_numbers = re.findall(r"\d+", string_to_format)
    teacher_names = re.findall(r"(?:ас[.]|доц[.]|пр[.])\s*?(\w+)", string_to_format)

    result_lines: list[str] = []

    if subject_name:
        result_lines.append(subject_name[0].strip() + '\n')

    longest_teacher_name_len = 0

    for teacher_name in teacher_names:
        longest_teacher_name_len = max(len(teacher_name), longest_teacher_name_len)

    if len(teacher_names) == len(classroom_numbers):
        for teacher_name, classroom_number in zip(teacher_names, classroom_numbers):
            space_count = longest_teacher_name_len - len(teacher_name)
            result_lines.append(f"•{teacher_name} {" " * space_count}{classroom_number} каб.\n")
    else:
        result_lines.append(f"• {teacher_names[0]}\n")

    return "".join(result_lines)


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
                subject not in result_dict[value_day][time_interval_dict_key]):
            result_dict[value_day][time_interval_dict_key].append(subject)

    day: str
    schedule_dict: dict[str, list]
    for day, schedule_dict in result_dict.items():
        result_lines.append(day.capitalize() + "\n\n")

        time: str
        subjects: list
        for time, subjects in schedule_dict.items():
            subject_to_add = subjects[0]

            if len(subjects) > 1:
                index = 0 if week_type == "верхній" else 1
                subject_to_add = subjects[index]
            elif subject_to_add == "empty_subject":
                continue

            if subject_to_add == "empty_subject":
                subject_to_add = "чіл в пузатці"
            else:
                subject_to_add = format_subject_string(subject_to_add)

            time = time.replace("\n", "")
            result_lines.append(time + " " + subject_to_add + "\n\n")

    return "".join(result_lines)


def main():
    apply_merges(values, obj["sheets"][0])
    print(get_schedule_by_group_index_and_day(values, "верхній", "К-10"))

#     string = """Українська та зарубіжна культура
# (лек) 30 год
# (кон) 2 год
# пр. Сторожук С.В.
#
#
# 	"""
#     print(format_subject_string(string))


main()
