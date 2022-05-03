# pylint: disable="missing-module-docstring"
import json
import os
from pathlib import Path

from mondaydotcom_utils.formatted_value import FormattedBoard


# pylint: disable="missing-function-docstring"
def test_board_formatter():

    current_path = Path(os.path.dirname(os.path.realpath(__file__)))

    # open the board resource file
    with open(
        os.path.join(current_path, "resources", "test_board.json"), "r", encoding="UTF-8"
    ) as file_handle:
        board_json = json.load(file_handle)

    # there's just one board
    our_board = board_json["data"]["boards"][0]
    items = our_board["items"]

    # open the board resource file
    with open(
        os.path.join(current_path, "resources", "test_board_col_defs.json"), "r", encoding="UTF-8"
    ) as file_handle:
        col_defs = json.load(file_handle)

    board_formatter = FormattedBoard(col_defs)
    board_formatter.format(items)

    assert board_formatter.to_df().columns.to_list() == [
        "monday_id",
        "monday_name",
        "Subitems",
        "Person",
        "Status__text",
        "Status__changed_at",
        "Date",
        "Timeline__to",
        "Timeline__from",
        "Timeline__changed_at",
        "Timeline Days",
        "Another Status__text",
        "Another Status__changed_at",
        "Percent Complete",
        "Notes",
        "Time Tracking__running",
        "Time Tracking__duration",
        "Time Tracking__startDate",
        "Time Tracking__changed_at",
        "Time Tracking__additional_value",
        "Hour",
        "Hour__default_formatter",
        "Some Date",
        "Formula__formula",
        "Dependency",
        "Test Board",
        "A Mirror Column__mirror",
        "Tags",
        "Long Notes",
        "Check__checked",
        "Check__changed_at",
        "Timeline__visualization_type",
        "Timeline",
        "Time Tracking",
        "Status",
        "Another Status",
    ]
