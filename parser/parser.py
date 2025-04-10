import re
from collections import defaultdict
from typing import Any, TypeAlias

import gspread
import requests
from google.oauth2.service_account import Credentials
from google.protobuf.any import type_name
from gspread import Client
import logging
from gspread.utils import extract_id_from_url

import config

# dict[day, dict[time_interval, list["subject1", "subject2", ...]]]
ScheduleDict: TypeAlias = dict[str, dict[str, list[tuple[str, tuple[int, int]]]]]


def get_spreadsheet_merges_info(
    client: Client, sheet_id: str, sheet_name: str
) -> list[dict[str, int]]:
    try:
        client.http_client.login()
    except Exception as e:
        logging.error("Failed to login: %s", e)
        return []

    access_token = client.http_client.auth.token
    url = (
        "https://sheets.googleapis.com/v4/spreadsheets/"
        + sheet_id
        + "?ranges="
        + sheet_name
        + "&fields=sheets.merges"
    )

    try:
        res = requests.get(
            url, headers={"Authorization": "Bearer " + access_token}, timeout=20
        )
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error("Failed to fetch spreadsheet merges info: %s", e)
        return []

    obj = res.json()

    sheets = obj.get("sheets")
    if not sheets:
        return []

    merges = sheets[0].get("merges")
    if not merges:
        return []

    return obj["sheets"][0]["merges"]


def get_spreadsheet_format_info(client: Client, sheet_id: str, sheet_name: str):
    client.http_client.login()

    url = (
        "https://sheets.googleapis.com/v4/spreadsheets/"
        + sheet_id
        + "?ranges="
        + sheet_name
        + "&fields=sheets.data.rowData.values.effectiveValue,sheets.data.rowData.values.textFormatRuns"
    )

    res = requests.get(
        url,
        headers={"Authorization": "Bearer " + client.http_client.auth.token},
        timeout=10,
    )

    data = res.json()

    rows = data["sheets"][0]["data"][0]["rowData"]

    return rows


def get_spreadsheet_cell_values(
    client: Client, spreadsheet_url: str, sheet_name: str
) -> list[list[str]]:
    sheet = client.open_by_url(spreadsheet_url)
    worksheet = sheet.worksheet(sheet_name)
    sheet_values = worksheet.get_all_values()

    merges_info = get_spreadsheet_merges_info(
        client, extract_id_from_url(spreadsheet_url), sheet_name
    )

    apply_merges(sheet_values, merges_info)

    return sheet_values


def apply_merges(
    sheet_values: list[list], sheet_metadata: list[dict[str, int]]
) -> None:
    for merge in sheet_metadata:
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


def format_time_interval(time: str) -> str:
    time = time.replace("\n", "")
    time_intervals = time.split(" ")
    first_timestamp = time_intervals[0].split("-")
    second_timestamp = time_intervals[1].split("-")

    time_interval = first_timestamp[0] + "-" + second_timestamp[1]

    return time_interval


def format_subject_string(
    string_to_format: str, time_interval: str, link_info: dict
) -> str:
    time_interval = format_time_interval(time_interval)
    if string_to_format == "empty_subject":
        return f"<b>{time_interval}</b>\n💤💤💤\n\n"

    teacher_names = re.findall(r"((?:ас[.]|доц[.]|пр[.])\s*?\w+)", string_to_format)

    string_to_format = re.sub(r"\s+", " ", string_to_format)
    string_to_format = re.sub(
        r"\d\s?п/г", "", string_to_format
    )  # maybe it should be removed
    subject_name = re.findall(r"(^.+?)(?:\()", string_to_format)
    if subject_name:
        string_to_format = string_to_format.replace(subject_name[0].strip(), "")
    string_to_format = re.sub(r"\(.+год", "", string_to_format)

    classroom_numbers = re.findall(r"\d+", string_to_format)

    result_lines: list[str] = [f"<b>{time_interval}</b>\n"]

    if subject_name:
        result_lines.append(subject_name[0].strip() + "\n")

    longest_teacher_name_len = 0

    for teacher_name in teacher_names:
        longest_teacher_name_len = max(len(teacher_name), longest_teacher_name_len)

    if len(teacher_names) == len(classroom_numbers):
        for teacher_name, classroom_number in zip(teacher_names, classroom_numbers):
            link = ""
            space_count = longest_teacher_name_len - len(teacher_name)

            if link_info and "link_is_on_subject" in link_info:
                if link_info["link_is_on_subject"]:
                    link = link_info["subject_link"]
                else:
                    link = link_info["teacher_names"].get(teacher_name, "")
            result_lines.append(
                f"•[{teacher_name}]({link}) {" " * space_count}{classroom_number} каб.\n"
            )
    elif len(teacher_names) > 0:
        result_lines.append(f"•{teacher_names[0]}\n")

    result_lines.append("\n")

    return "".join(result_lines)


def get_group_indexes(
    arg_values: list[list[str]], group_indexes_row: int, group_indexes_start_col: int
) -> list[str]:
    group_indexes: list = []

    for col in range(group_indexes_start_col, len(arg_values[group_indexes_row])):
        group_index = arg_values[group_indexes_row][col]
        if not group_index or group_index.isspace():
            continue

        group_indexes.append(group_index)

    return group_indexes


def get_all_schedules(
    arg_values: list[list[str]],
    group_indexes_row: int,
    days_col: int,
    time_interval_col: int,
    group_indexes_start_col: int,
) -> dict[str, ScheduleDict]:
    days = ["понеділок", "вівторок", "середа", "четвер", "п'ятниця"]
    group_indexes = get_group_indexes(
        arg_values, group_indexes_row, group_indexes_start_col
    )

    result_dict: dict[str, ScheduleDict] = {}

    for group_index in group_indexes:
        result_dict[group_index] = {}

        for day in days:
            result_dict[group_index][day] = defaultdict(list)

    row_cord = 0
    for row in arg_values:
        value_day = "".join(row[days_col].split()).lower()

        if value_day not in days:
            row_cord += 1
            continue

        col_cord = 0
        for col in range(group_indexes_start_col, len(row)):
            group_index = arg_values[group_indexes_row][col]
            if group_index not in group_indexes:
                col_cord += 1
                continue

            subject = row[col]

            if not subject or subject.isspace():
                subject = "empty_subject"

            time_interval = row[time_interval_col]

            if (time_interval not in result_dict[group_index][value_day]) or (
                [subject, [row_cord, col]]
                not in result_dict[group_index][value_day][time_interval][0]
            ):
                result_dict[group_index][value_day][time_interval].append(
                    [subject, [row_cord, col]]
                )

            col_cord += 1

        row_cord += 1

    return result_dict


def fetch_schedules_dictionary(
    credentials_json,
    spreadsheet_url: str,
    sheet_name: str,
    group_indexes_row,
    days_col,
    time_interval_col,
    group_indexes_start_col,
) -> dict[str, ScheduleDict]:
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    client = gspread.service_account_from_dict(credentials_json, scopes=scopes)

    values = get_spreadsheet_cell_values(
        client,
        spreadsheet_url,
        sheet_name,
    )

    apply_merges(
        values,
        get_spreadsheet_merges_info(
            client, extract_id_from_url(spreadsheet_url), sheet_name
        ),
    )

    schedules_dictionary = get_all_schedules(
        values, group_indexes_row, days_col, time_interval_col, group_indexes_start_col
    )

    return schedules_dictionary


def match_link_with_text(
    strings_to_compare_with: list[str], cell_text: str, link_start_index: int
) -> str:
    for teacher in strings_to_compare_with:
        if teacher.startswith(
            cell_text[link_start_index : link_start_index + len(teacher)].strip()
        ):
            return teacher

    return ""


def retrieve_subject(cell_text: str) -> str:
    result = re.sub(r"\s+", " ", cell_text)
    result = re.sub(r"\d\s?п/г", "", result)
    result = re.findall(r"(^.+?)(?:\()", result)

    if not result:
        return ""

    return result[0]


def get_teachers(cell_string: str) -> list[str]:
    teacher_names = re.findall(r"((?:ас[.]|доц[.]|пр[.])\s*?\w+)", cell_string)

    return teacher_names


def get_links_matrix(
    credentials_json, spreadsheet_url: str, range_: str
) -> list[list[str]]:
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    client = gspread.service_account_from_dict(credentials_json, scopes=scopes)
    rows = get_spreadsheet_format_info(
        client, extract_id_from_url(spreadsheet_url), range_
    )

    values = [[] for _ in range(len(rows))]

    row_cord = 0
    for row in rows:
        if not row.get("values"):
            row_cord += 1
            continue

        values[row_cord] = [{} for _ in range(len(row["values"]))]

        col_cord = 0
        for col in row["values"]:
            if not col.get("textFormatRuns"):
                col_cord += 1
                continue

            for text_format_run in col["textFormatRuns"]:
                if not text_format_run["format"].get("link"):
                    continue

                link_is_on_subject = True
                cell_text = col["effectiveValue"]["stringValue"]
                teachers = get_teachers(cell_text)
                subject = retrieve_subject(cell_text)

                start_index = 0
                strings_to_compare_with = []

                if text_format_run.get("startIndex", []):
                    strings_to_compare_with = teachers
                    start_index = int(text_format_run["startIndex"])
                    link_is_on_subject = False

                values[row_cord][col_cord]["link_is_on_subject"] = link_is_on_subject
                values[row_cord][col_cord]["subject"] = subject if subject else ""

                if not values[row_cord][col_cord].get("teacher_names", []):
                    values[row_cord][col_cord]["teacher_names"] = {}

                link = text_format_run["format"]["link"]["uri"]
                if link_is_on_subject:
                    values[row_cord][col_cord]["subject_link"] = link
                else:
                    teacher_name = match_link_with_text(
                        strings_to_compare_with, cell_text, start_index
                    )
                    values[row_cord][col_cord]["teacher_names"][teacher_name] = link

            col_cord += 1

        row_cord += 1

    return values


def process_schedule_dictionary(
    schedule_dict: ScheduleDict, links_matrix: list[list[dict]]
) -> tuple[str, str]:
    # print(links_matrix)
    results: tuple[list[str], list[str]] = ([], [])

    results[0].append("Розклад <b>ВЕРХНІЙ</b>\n\n")
    results[1].append("Розклад <b>НИЖНІЙ</b>\n\n")

    day: str
    schedule_dict: dict[str, list]
    for day, schedule_dict in schedule_dict.items():

        beginning = f"<b>{day.capitalize()}</b>\n" + ("-" * 18 + "\n")
        for result in results:
            result.append(beginning)

        time: str
        subjects: list
        for time, subjects in schedule_dict.items():
            if len(subjects) == 1 and subjects[0] == "empty_subject":
                continue

            if len(subjects) > 1:
                for count, result in enumerate(results):
                    subject = subjects[count][0]
                    x = subjects[count][1][0]
                    y = subjects[count][1][1]
                    try:
                        result.append(
                            format_subject_string(subject, time, links_matrix[x][y])
                        )
                    except IndexError as e:
                        print("HELP-----------------------------------------------")
                        print(f"x = {x} y = {y}")
                        print(f"len 1 = {len(links_matrix)}")
                        print(f"len 2 = {len(links_matrix[x])}")
                        print("HELP-----------------------------------------------")
            else:
                for result in results:
                    subject = subjects[0][0]
                    x = subjects[0][1][0]
                    y = subjects[0][1][1]
                    try:
                        result.append(
                            format_subject_string(subject, time, links_matrix[x][y])
                        )
                    except IndexError as e:
                        print("HELP-----------------------------------------------")
                        print(f"x = {x} y = {y}")
                        print(f"len 1 = {len(links_matrix)}")
                        print(f"len 2 = {len(links_matrix[x])}")
                        print("HELP-----------------------------------------------")

    return "".join(results[0]), "".join(results[1])
