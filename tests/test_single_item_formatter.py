# pylint: disable="missing-module-docstring"
import json
import os
from pathlib import Path

from mondaydotcom_utils.formatted_value import FormattedValue


# pylint: disable="missing-function-docstring"
def test_board_item1_formatter():

    current_path = Path(os.path.dirname(os.path.realpath(__file__)))

    # open the board resource file
    with open(
        os.path.join(current_path, "resources", "test_board.json"), "r", encoding="UTF-8"
    ) as file_handle:
        board_json = json.load(file_handle)

    # there's just one board
    our_board = board_json["data"]["boards"][0]

    # get the column names and convert to a helpful dict
    col_defs = {}
    for column in our_board["columns"]:
        col_defs[column["id"]] = column
    # print(col_defs)

    item = our_board["items"][0]
    # print(item)

    item_formatter = FormattedValue(col_defs)

    item_row = {}
    for col in item["column_values"]:
        item_columns = item_formatter.format(col["id"], col["value"], col["text"])
        item_row.update(item_columns)
        # print(col["type"], item_columns)

    # pylint: disable="line-too-long"
    assert item_row == {
        "Subitems": [2621588113],
        "Person": [{"id": 25810257, "kind": "person"}],
        "Status__text": "Working on it",
        "Status__changed_at": "2019-03-01T17:24:57.321Z",
        "Date": "2022-04-30",
        "Timeline__to": "2022-05-05",
        "Timeline__from": "2022-05-02",
        "Timeline__changed_at": "2022-05-02T19:48:21.426Z",
        "Timeline Days": 4,
        "Another Status__text": "Stuck",
        "Another Status__changed_at": "2022-05-02T19:48:31.434Z",
        "Percent Complete": 25,
        "Notes": "A note here",
        "Notes2": "Column names can be duplicated.",
        "Time Tracking__running": False,
        "Time Tracking__duration": 3,
        "Time Tracking__startDate": 1651521018,
        "Time Tracking__changed_at": "2022-05-02T19:50:20.595Z",
        "Time Tracking__additional_value": [
            {
                "id": 222066299,
                "account_id": 10368903,
                "project_id": 2619086128,
                "column_id": "time_tracking",
                "started_user_id": 25810257,
                "ended_user_id": 25810257,
                "started_at": "2022-05-02T16:45:09Z",
                "ended_at": "2022-05-02T16:45:10Z",
                "manually_entered_start_time": False,
                "manually_entered_end_time": False,
                "manually_entered_start_date": False,
                "manually_entered_end_date": False,
                "created_at": "2022-05-02T16:45:10Z",
                "updated_at": "2022-05-02T16:45:11Z",
                "status": "active",
            },
            {
                "id": 222169620,
                "account_id": 10368903,
                "project_id": 2619086128,
                "column_id": "time_tracking",
                "started_user_id": 25810257,
                "ended_user_id": 25810257,
                "started_at": "2022-05-02T19:50:18Z",
                "ended_at": "2022-05-02T19:50:20Z",
                "manually_entered_start_time": False,
                "manually_entered_end_time": False,
                "manually_entered_start_date": False,
                "manually_entered_end_date": False,
                "created_at": "2022-05-02T19:50:18Z",
                "updated_at": "2022-05-02T19:50:20Z",
                "status": "active",
            },
        ],
        "Hour": '{"hour":12,"minute":0,"changed_at":"2022-05-02T16:45:25.941Z"}',
        "Hour__default_formatter": True,
        "Some Date": "2022-05-20",
        "Formula__formula": None,
        "Dependency": [2619086253, 2619086190],
        "Test Board": [2619086318, 2619086190],
        "A Mirror Column__mirror": None,
        "Tags": [14429933, 14429935],
        "Long Notes": 'The standard Lorem Ipsum passage, used since the 1500s\n"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."\n\nSection 1.10.32 of "de Finibus Bonorum et Malorum", written by Cicero in 45 BC\n"Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem. Ut enim ad minima veniam, quis nostrum exercitationem ullam corporis suscipit laboriosam, nisi ut aliquid ex ea commodi consequatur? Quis autem vel eum iure reprehenderit qui in ea voluptate velit esse quam nihil molestiae consequatur, vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?"',
        "Check__checked": True,
        "Check__changed_at": "2022-05-03T00:47:16.789Z",
    }
