# pylint: disable="missing-module-docstring"

import json
import logging

import numpy as np

logger = logging.getLogger(__name__)


def get_col_defs(monday_conn, board_id):
    """
    Get the column definitions. Useful for formatting values later.

    from https://github.com/ProdPerfect/monday/wiki/Code-Examples#whole-board-formatting-example

    # TODO bring this into a class
    """
    data = monday_conn.boards.fetch_boards_by_id(board_id)
    columns = data["data"]["boards"][0]["columns"]
    col_defs = {}

    for column in columns:
        col_defs[column["id"]] = column

    # returns a dict
    return col_defs


class FormattedValue:
    """
    Heavily influenced by
    https://github.com/ProdPerfect/monday/wiki/Code-Examples#whole-board-formatting-example

    Parses an individual "item" from Monday.com column_values
    and creates a simple name-value pair for each column.

    IDEA Some of the values remain in json, and it might be good
    to have these blown out into more than just one key/value.
    """

    def __init__(self, col_defs, use_mapped_name=True):

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
        }
        self.use_mapped_name = use_mapped_name

    def get_my_name(self, field_name, annotation=""):
        """
        If self.use_mapped_name is True, then use the propper mapped name.
        Else, output the nearly useful field names from Monday.com

        TODO refine this so self.col_defs isn't strictly required
        """

        if self.use_mapped_name:
            # If use_mapped_name is true, then use the proper mapped name.
            mapped_name = self.col_defs[field_name]["title"]

            if annotation:
                return f"{mapped_name} ({annotation})"

            return mapped_name

        # else return the field name
        return field_name

    @staticmethod
    def format_default(field_name, value, text):
        """
        When no other formatter matches, use this as the default.
        """
        logger.debug(
            "The default formatter is being used, field_name=%s, value=%s, text=%s",
            field_name,
            value,
            text,
        )
        return value

    @staticmethod
    # pylint: disable="unused-argument, missing-function-docstring"
    def format_text_field(field_name, value, text):
        if value is not None:
            return json.loads(value)

        return None

    @staticmethod
    # pylint: disable="unused-argument, missing-function-docstring"
    def format_date_field(field_name, value, text):
        if value is not None:
            return text

        return None

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
        return self.convert_numeric(text)

    @staticmethod
    # pylint: disable="unused-argument, missing-function-docstring"
    def format_longtext_field(field_name, value, text):
        if value is not None:
            value = json.loads(value)["text"]
            return value.strip() if value else None

        return None

    @staticmethod
    # pylint: disable="unused-argument, missing-function-docstring"
    def format_tag_field(field_name, value, text):
        return text

    @staticmethod
    # pylint: disable="unused-argument, missing-function-docstring"
    def format_color_field(field_name, value, text):
        if value is not None:
            value_json = json.loads(value)
            # rough, but I'll need the changed_at date
            my_dict = {"text": text}
            if value_json.get("changed_at"):
                my_dict["changed_at"] = value_json["changed_at"]

            return json.dumps(my_dict)

        return None

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
                return rows

            except BaseException as ex:  # pylint: disable="broad-except"
                logger.exception(ex)

        return []

    @staticmethod
    # pylint: disable="unused-argument, missing-function-docstring"
    def format_person_field(field_name, value, text):
        if value is not None:
            return json.loads(value)["personsAndTeams"]

        return []

    # pylint: disable="unused-argument, missing-function-docstring"
    def format_dropdown_field(self, field_name, value, text):
        if value is not None:
            labels = json.loads(self.col_defs[field_name]["settings_str"])["labels"]
            # pylint: disable = "consider-using-dict-comprehension"
            label_map = dict([(row["id"], row["name"]) for row in labels])
            return ", ".join([label_map.get(id) for id in json.loads(value)["ids"]])

        return None

    def format(self, field_name, value, text):
        """
        Get the column type from the column definitions

        This is the "entry" method; it uses the formatter below
        to "route" based on the `type_to_callable_map`.
        """
        field_type = self.col_defs[field_name]["type"]

        # use the map to lookup the function, using default if one isn't found.
        formatter = self.type_to_callable_map.get(field_type, self.format_default)

        # mirror columns doesn't bring back agg info, and formulas can be just about anything,
        # so try not to use them. Make that obvious in the column name.
        if field_type == "lookup":
            annotation = "mirror"
        elif field_type == "formula":
            annotation = "formula"
        else:
            annotation = ""

        # call the mapped function
        value_return = formatter(field_name, value, text)

        result = {
            "name": self.get_my_name(field_name, annotation),
            "value": value_return,
        }

        return result
