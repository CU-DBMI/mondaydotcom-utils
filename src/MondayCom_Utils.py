import logging
import json
from dateutil import parser
from MondayCom_Time import *
from MondayCom_FormattedValue import *
import pandas as pd

logger = logging.getLogger(__name__)


def get_items_by_board(conn, board_id, column_id="", column_value=""):
    """
    A common function to lookup all items on a specific board.
    Setting column_id and column_value, to e.g., "status" and "Done" will fetch only those items,
    otherwise the entire board will be fetched.

    Returns a dataframe.
    """

    if column_id:
        # if a column_id is set, then use one graphql query...
        test_board = conn.items.fetch_items_by_column_value(
            board_id, column_id, column_value
        )
        items = test_board["data"]["items_by_column_values"]
    else:
        # otherwise, use this one to fetch the entire board.
        test_board = conn.boards.fetch_items_by_board_id(board_id)
        items = test_board["data"]["boards"][0]["items"]

    # Grab a map of column IDs, their settings, and proper names.
    col_defs = get_col_defs(conn, board_id)

    # format the column values
    fv = FormattedValue(col_defs, use_mapped_name=True)

    # build up a list of name-value pairs
    rows = []
    for item in items:
        item_id = item["id"]
        item_name = item["name"]
        for col in item["column_values"]:
            row = fv.format(col["id"], col["value"], col["text"])
            row["monday_id"] = item_id
            row["Title"] = item_name
            rows.append(row)

    # create a dataframe
    df = pd.DataFrame(rows).set_index(["monday_id", "Title", "name"])

    # pivot the table around
    df = df.unstack(level=-1).droplevel(level=0, axis=1).reset_index()

    # change the monday_id to an integer
    df["monday_id"] = pd.to_numeric(df["monday_id"])

    return df.rename_axis("", axis="columns")


def validate_task_record(record):
    """
    Validate checks individual records and we'll use those rules to create journal records later.

    Rules:
      1. Either actual hours or sessions times are used, but not both.
         If both are found, this is an error.
      2. If actual hours is used, then the number of owners dictates the number
         of journal records. E.g., actual hours = 15, with 3 owners, yields
         three journal entries at 5 each (actual hours / owner count).
         If no owners are found, this is an error.
      3. If no time fields, either actual or sessions, this is a problem.

      If session times are used, then a journal entry is created for each
         session.
    """
    actual_hours = record["Actual Hours"]
    sessions_list = record["Time Sessions"]
    owners_list = record["Owner"]
    len_sessions_list = len(sessions_list)
    len_owners_list = len(owners_list)
    title = record["Title"]
    date_completed = record["Date Completed"]

    logger.debug(
        f"actual_hours:{actual_hours}, len(session_list):{len_sessions_list}, len(owners_list):{len_owners_list}"
    )

    # rule 1
    if not np.isnan(actual_hours) and len_sessions_list > 0:
        record["integration_state"] = "STOP"
        record["integration_state_rule"] = "actual_hours_and_sessions"
        logger.warning(f'{record["integration_state_rule"]}: {title}')

    # rule 2 - using actual hours requires at least one owner
    elif not np.isnan(actual_hours) and len_owners_list == 0:
        record["integration_state"] = "STOP"
        record["integration_state_rule"] = "actual_hours_and_no_owners"
        logger.warning(f'{record["integration_state_rule"]}: {title}')

    # rule 3
    elif np.isnan(actual_hours) and len_sessions_list == 0:
        record["integration_state"] = "STOP"
        record["integration_state_rule"] = "no_actual_hours_and_no_sessions"
        logger.warning(f'{record["integration_state_rule"]}: {title}')

    else:
        record["integration_state"] = "Ready"
        record["integration_state_rule"] = "Ready"

    return record


def breakout_record(record, users_df):
    """
    Validate takes an individual record and checks it against
    rules, and creates multiple task records where required.

    Rules:
      1. Either actual hours or sessions times are used, but not both.
         If both are found, this is an error.
      2. If actual hours is used, then the number of owners dictates the number
         of journal records. E.g., actual hours = 15, with 3 owners, yields
         three journal entries at 5 each (actual hours / owner count).
         If no owners are found, this is an error.
      3. If no time fields, either actual or sessions, this is a problem.

      If session times are used, then a journal entry is created for each
         session.
    """
    actual_hours = record["Actual Hours"]
    sessions_list = record["Time Sessions"]
    owners_list = record["Owner"]
    len_sessions_list = len(sessions_list)
    len_owners_list = len(owners_list)
    date_completed = record["Date Completed"]
    records = []

    logger.debug(
        f"validating: actual_hours:{actual_hours}, len(session_list):{len_sessions_list}, len(owners_list):{len_owners_list}"
    )

    if not record["Integration Message"].startswith("Ready"):
        # quietly pass this unready record
        pass

    elif not np.isnan(actual_hours):
        # split the hours up between the owners
        status_json = json.loads(record["Status"])
        for owner in owners_list:
            new_rec = record.copy()
            # add the owner
            new_rec["owner"] = users_df.loc[owner["id"]]["name"]
            # divide the task time
            new_rec["hours"] = actual_hours / len_owners_list
            # get the task time from date completed... or fallback on the status
            if record["Date Completed"]:
                new_rec["task_end_date"] = parser.parse(
                    f"{date_completed} 00:00:00+00:00"
                )
            else:
                new_rec["task_end_date"] = parser.parse(status_json["changed_at"])
            new_rec["integration_state_rule"] = "hours_split_between_owners"
            records.append(new_rec)

    elif len_sessions_list > 0:
        # multiply the number of tasks by sessions
        for session in sessions_list:
            new_rec = record.copy()
            new_rec["owner"] = users_df.loc[session["owner_id"]]["name"]
            new_rec["hours"] = session["hours"]
            # get the task time from date completed... or fallback on the status
            if record["Date Completed"]:
                new_rec["task_end_date"] = parser.parse(
                    f"{date_completed} 00:00:00+00:00"
                )
            else:
                new_rec["task_end_date"] = parser.parse(status_json["changed_at"])
            new_rec["integration_state_rule"] = "hours_from_session_records"
            records.append(new_rec)

    else:
        logger.error("An unknown condition stopped record processing.")

    return records
