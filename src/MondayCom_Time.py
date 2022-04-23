import json
import logging
from box import Box
from dateutil import parser

logger = logging.getLogger(__name__)


class MondayCom_Time:
    """I use this to crack open the time tracking json into a more refined structure."""

    def __init__(self):

        self.time_records = []
        self.total_duration_hours = 0

    def parse(self, items):
        """
        Take a Monday.com time entry and convert it into a time record.

        Monday.com's value is json, inside a string.
        """

        self.time_records = []

        if items:
            try:
                self.timejson = Box(json.loads(items))
            except:
                logger.warning(f"Cannot load into json: {type(items)} {items}")
                return

            # go through each additional_value and convert it into a cleaner dict
            if self.timejson.get("additional_value"):
                for item in self.timejson["additional_value"]:
                    self.time_records.append(self.parse_additional_value(item))

    def parse_additional_value(self, item):
        """Break down the individual session records, capturing the duration."""
        new_item = Box()

        new_item.owner_id = item.ended_user_id

        # Any manual entry means we consider the whole record as manual
        new_item.manually_entered = (
            item.manually_entered_end_date
            or item.manually_entered_end_time
            or item.manually_entered_start_date
            or item.manually_entered_start_time
        )

        new_item.started_at = item.started_at
        new_item.ended_at = item.ended_at
        new_item.created_at = item.created_at

        start_date = parser.parse(new_item.started_at)
        end_date = parser.parse(new_item.ended_at)

        # take the difference between the two dates as hours
        difference = end_date - start_date
        new_item.hours = difference.total_seconds() / 60 / 60

        self.total_duration_hours += new_item.hours

        return new_item.to_dict()
