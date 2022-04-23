import json
import logging
import numpy as np

logger = logging.getLogger(__name__)


def get_col_defs(monday_conn, board_id):

    # from https://github.com/ProdPerfect/monday/wiki/Code-Examples#whole-board-formatting-example

    data = monday_conn.boards.fetch_boards_by_id(board_id)
    columns = data["data"]["boards"][0]["columns"]
    col_defs = {}

    for column in columns:
        col_defs[column["id"]] = column

    # returns a dict
    return col_defs


class FormattedValue:
    """
    Heavily influenced by https://github.com/ProdPerfect/monday/wiki/Code-Examples#whole-board-formatting-example

    Parses an individual "item" from Monday.com column_values creates a simple name-value pair for each column.

    IDEA Some of the values remain in json, and it might be good to have these blown out into more than just one key/value.
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
            else:
                return mapped_name
        else:
            return field_name

    def format_default(self, field_name, value, text):
        logger.debug(
            f"The default formatter is being used, field_name={field_name}, value={value}, text={text}"
        )
        return value

    def format_text_field(self, field_name, value, text):
        if value is not None:
            return json.loads(value)

    def format_date_field(self, field_name, value, text):
        if value is not None:
            return text

    def convert_numeric(self, value):
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return np.nan

    def format_numeric_field(self, field_name, value, text):
        return self.convert_numeric(text)

    def format_longtext_field(self, field_name, value, text):
        if value is not None:
            value = json.loads(value)["text"]
            return value.strip() if value else None

    def format_tag_field(self, field_name, value, text):
        return text

    def format_color_field(self, field_name, value, text):
        if value is not None:
            value_json = json.loads(value)
            # rough, but I'll need the changed_at date
            my_dict = {"text": text}
            if value_json.get("changed_at"):
                my_dict["changed_at"] = value_json["changed_at"]

            return json.dumps(my_dict)

    def format_boardrelation_field(self, field_name, value, text):
        if value is not None:
            try:
                json_val = json.loads(value)
                rows = []
                if json_val.get("linkedPulseIds"):
                    for x in json.loads(value)["linkedPulseIds"]:
                        rows.append(x["linkedPulseId"])
                return rows
            except:
                logger.error(f"Could not load json from {value}")
                return None
        else:
            return []

    def format_person_field(self, field_name, value, text):
        if value is not None:
            return json.loads(value)["personsAndTeams"]
        else:
            return []

    def format_dropdown_field(self, field_name, value, text):
        if value is not None:
            labels = json.loads(self.col_defs[field_name]["settings_str"])["labels"]
            label_map = dict([(row["id"], row["name"]) for row in labels])
            return ", ".join([label_map.get(id) for id in json.loads(value)["ids"]])

    def format(self, field_name, value, text):
        # get the column type from the column definitions
        t = self.col_defs[field_name]["type"]

        # use the map to lookup the function, using default if one isn't found.
        formatter = self.type_to_callable_map.get(t, self.format_default)

        # mirror columns doesn't bring back agg info, and formulas can be just about anything,
        # so try not to use them. Make that obvious in the column name.
        if t == "lookup":
            annotation = "mirror"
        elif t == "formula":
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
