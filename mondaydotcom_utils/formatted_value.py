# pylint: disable="missing-module-docstring"

import json
import logging
from typing import Dict

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def get_items_by_board(conn, board_id, column_id="", column_value=""):
    """
    A common function to lookup all items on a specific board.
    Setting column_id and column_value, to e.g.,
    "status" and "Done" will fetch only those items,
    otherwise the entire board will be fetched.

    Returns a dataframe.
    """

    if column_id:
        # if a column_id is set, then use one graphql query...
        test_board = conn.items.fetch_items_by_column_value(board_id, column_id, column_value)
        items = test_board["data"]["items_by_column_values"]
    else:
        # otherwise, use this one to fetch the entire board.
        test_board = conn.boards.fetch_items_by_board_id(board_id)
        items = test_board["data"]["boards"][0]["items"]

    # Grab a map of column IDs, their settings, and proper names.
    col_defs = get_col_defs(conn, board_id)

    # format the column values
    formatted_board = FormattedBoard(col_defs)
    formatted_board.format(items)

    result_df = formatted_board.to_df()

    return result_df


def get_col_defs(monday_conn, board_id):
    """
    Get the column definitions. Useful for formatting values later.

    from https://github.com/ProdPerfect/monday/wiki/Code-Examples#whole-board-formatting-example
    """
    data = monday_conn.boards.fetch_boards_by_id(board_id)
    columns = data["data"]["boards"][0]["columns"]

    col_defs = {}
    for column in columns:
        col_defs[column["id"]] = column

    # returns a dict
    return col_defs


# pylint: disable="missing-class-docstring"
class FormattedBoard:

    # pylint: disable="missing-function-docstring"
    def __init__(self, col_defs):

        self.col_defs = col_defs
        self.rows = []

    def format(self, items):

        item_formatter = FormattedValue(self.col_defs)
        self.rows = []

        # build up a dict of name-value pairs
        for item in items:
            row_dict = {}
            row_dict["monday_id"] = item["id"]
            row_dict["monday_name"] = item["name"]
            for col in item["column_values"]:
                col_dict = item_formatter.format(col["id"], col["value"], col["text"])
                row_dict.update(col_dict)
            self.rows.append(row_dict)

    def to_df(self):

        # create a dataframe
        result_df = pd.DataFrame(self.rows)

        # # change the monday_id to an integer
        result_df["monday_id"] = pd.to_numeric(result_df["monday_id"])

        return result_df


class FormattedValue:
    """
    Influenced by
    https://github.com/ProdPerfect/monday/wiki/Code-Examples#whole-board-formatting-example

    Parses an individual "item" from Monday.com column_values
    and creates simple name-value pair(s) for each column.

    Column titles in the UI can be duplicates. Duplicate column names can have unexpected results,
    and are not supported.

    Each formatter returns a list with zero, one, or more name-value pairs in a dict.
    """

    def __init__(self, col_defs: Dict):

        self.col_defs = col_defs

        self.type_to_callable_map = {
            "color": self.format_color_field,
            "dropdown": self.format_dropdown_field,
            "long-text": self.format_longtext_field,
            "date": self.format_date_field,
            "numeric": self.format_numeric_field,
            "text": self.format_text_field,
            "tag": self.format_tag_field,
            "multiple-person": self.format_person_field,
            "board-relation": self.format_boardrelation_field,
            "dependency": self.format_dependency_field,
            "formula": self.format_formula_field,
            "lookup": self.format_lookup_field,
            "timerange": self.format_timerange_field,
            "duration": self.format_duration_field,
            "subtasks": self.format_subtasks_field,
            "boolean": self.format_boolean_field,
        }

    @staticmethod
    def format_default(field_name, value, text) -> Dict:
        """
        When no other formatter matches, use this as the default.
        """
        logger.debug(
            "The default formatter is being used, field_name=%s, value=%s, text=%s",
            field_name,
            value,
            text,
        )
        return {field_name: value, f"{field_name}__default_formatter": True}

    @staticmethod
    # pylint: disable="unused-argument, missing-function-docstring"
    def format_lookup_field(field_name, value, text) -> Dict:
        """
        Lookup fields aren't exported, so almost a straight default here.
        """
        return {f"{field_name}__mirror": None}

    @staticmethod
    # pylint: disable="unused-argument, missing-function-docstring"
    def format_formula_field(field_name, value, text) -> Dict:
        """
        Formula fields aren't exported, so almost a straight default here.
        """
        return {f"{field_name}__formula": None}

    @staticmethod
    # pylint: disable="unused-argument, missing-function-docstring"
    def format_text_field(field_name, value, text):
        retval = None
        if value is not None:
            retval = json.loads(value)

        return {field_name: retval}

    @staticmethod
    # pylint: disable="unused-argument, missing-function-docstring"
    def format_date_field(field_name, value, text):
        retval = None
        if value is not None:
            retval = text

        return {field_name: retval}

    @staticmethod
    def convert_numeric(value):
        """
        Numeric values in Monday.com are both ints and floats in a string.

        This funciton breaks them out, or if the string is empty, spaces,
        or zero-length return NaN.
        """
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return np.nan

    # pylint: disable="unused-argument, missing-function-docstring"
    def format_numeric_field(self, field_name, value, text):
        return {field_name: self.convert_numeric(text)}

    @staticmethod
    # pylint: disable="unused-argument, missing-function-docstring"
    def format_longtext_field(field_name, value, text):
        retval = None
        if value is not None:
            value = json.loads(value)["text"]
            retval = value.strip() if value else None

        return {field_name: retval}

    @staticmethod
    # pylint: disable="unused-argument, missing-function-docstring"
    def format_timerange_field(field_name, value, text):
        my_dict = {}
        retval = None
        if value is not None:
            value_json = json.loads(value)
            for k, v in value_json.items():  # pylint: disable="invalid-name"
                my_dict.update({f"{field_name}__{k}": v})
            return my_dict

        return {field_name: retval}

    @staticmethod
    # pylint: disable="unused-argument, missing-function-docstring"
    def format_tag_field(field_name, value, text):
        retval = None
        if value is not None:
            retval = json.loads(value)["tag_ids"]
        return {field_name: retval}

    @staticmethod
    # pylint: disable="unused-argument, missing-function-docstring"
    def format_color_field(field_name, value, text):
        my_dict = {}

        if value is not None:
            if text:
                my_dict.update({f"{field_name}__text": text})

            value_json = json.loads(value)

            if value_json.get("changed_at"):
                my_dict.update({f"{field_name}__changed_at": value_json["changed_at"]})

            return my_dict

        return {field_name: None}

    @staticmethod
    # pylint: disable="unused-argument, missing-function-docstring"
    def format_boolean_field(field_name, value, text):
        my_dict = {}

        if value is not None:

            value_json = json.loads(value)
            my_dict.update({f"{field_name}__checked": True})

            if value_json.get("changed_at"):
                my_dict.update({f"{field_name}__changed_at": value_json["changed_at"]})

        else:
            my_dict.update({f"{field_name}__checked": False})

        return my_dict

    @staticmethod
    # pylint: disable="unused-argument, missing-function-docstring"
    def format_boardrelation_field(field_name, value, text):
        if value is not None:
            try:
                json_val = json.loads(value)
                rows = []
                if json_val.get("linkedPulseIds"):
                    for pulse_id in json.loads(value)["linkedPulseIds"]:
                        rows.append(pulse_id["linkedPulseId"])
                return {field_name: rows}

            except BaseException as ex:  # pylint: disable="broad-except"
                logger.exception(ex)

        return {field_name: None}

    @staticmethod
    # pylint: disable="unused-argument, missing-function-docstring"
    def format_subtasks_field(field_name, value, text):
        if value is not None:
            try:
                json_val = json.loads(value)
                rows = []
                if json_val.get("linkedPulseIds"):
                    for pulse_id in json.loads(value)["linkedPulseIds"]:
                        rows.append(pulse_id["linkedPulseId"])
                if len(rows) > 0:
                    return {field_name: rows}

            except BaseException as ex:  # pylint: disable="broad-except"
                logger.exception(ex)

        return {field_name: None}

    @staticmethod
    # pylint: disable="unused-argument, missing-function-docstring"
    def format_dependency_field(field_name, value, text):
        if value is not None:
            try:
                json_val = json.loads(value)
                rows = []
                if json_val.get("linkedPulseIds"):
                    for pulse_id in json.loads(value)["linkedPulseIds"]:
                        rows.append(pulse_id["linkedPulseId"])
                return {field_name: rows}

            except BaseException as ex:  # pylint: disable="broad-except"
                logger.exception(ex)

        return {field_name: None}

    @staticmethod
    # pylint: disable="unused-argument, missing-function-docstring"
    def format_duration_field(field_name, value, text):
        my_dict = {}
        if value is not None:
            try:
                json_val = json.loads(value)

                for k, v in json_val.items():  # pylint: disable="invalid-name"
                    my_dict.update({f"{field_name}__{k}": v})
                return my_dict

            except BaseException as ex:  # pylint: disable="broad-except"
                logger.exception(ex)

        return {field_name: None}

    @staticmethod
    # pylint: disable="unused-argument, missing-function-docstring"
    def format_person_field(field_name, value, text):
        if value is not None:
            return {field_name: json.loads(value)["personsAndTeams"]}

        return {field_name: None}

    # pylint: disable="unused-argument, missing-function-docstring"
    def format_dropdown_field(self, field_name, value, text):
        if value is not None:
            labels = json.loads(self.col_defs[field_name]["settings_str"])["labels"]
            # pylint: disable = "consider-using-dict-comprehension"
            label_map = dict([(row["id"], row["name"]) for row in labels])
            return {field_name: ", ".join([label_map.get(id) for id in json.loads(value)["ids"]])}

        return {field_name: None}

    def format(self, field_name, value, text):
        """
        Get the column type from the column definitions

        This is the "entry" method; it uses the formatter below
        to "route" based on the `type_to_callable_map`.
        """
        field_type = self.col_defs[field_name]["type"]
        column_name = self.col_defs[field_name]["title"]

        # use the map to lookup the function, using default if one isn't found.
        formatter = self.type_to_callable_map.get(field_type, self.format_default)

        formatted_items = formatter(column_name, value, text)

        # call the mapped function with the proper column name
        return formatted_items
