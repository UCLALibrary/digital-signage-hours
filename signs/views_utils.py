import requests
import logging
from datetime import datetime
from django.http import HttpRequest

logger = logging.getLogger(__name__)


def get_hours(widget_url: str, location_id: str) -> list[dict]:
    """Retrieve hours for a location from the LibCal widget."""
    # We request 2 weeks of hours from the widget to cover Monday-Sunday
    # instead of Sunday-Saturday
    response = requests.get(
        widget_url, params={"lid": location_id, "weeks": 2, "format": "json"}
    )
    data = response.json()
    return data


def format_hours(data: dict) -> list[dict]:
    """Reformat and remove unnecessary data from LibCal hours response."""
    # Hours data is nested three dictionaries deep in LibCal's response
    # Example (truncated) data from LibCal:
    # {"loc_2609": {
    #     ...
    #     "weeks": [
    #         {
    #             "Sunday": {
    #                 "date": "2024-02-04",
    #                 "times": {
    #                     "status": "open",
    #                     "hours": [{"from": "10am", "to": "3pm"}],
    #                     "currently_open": False,
    #                 },
    #                 "rendered": "10am - 3pm",
    #             }, ...

    # First, check that the data contains the expected number of values:
    #  1 location, 2 weeks, 7 days each
    if len(data) != 1:
        logger.error(f"Unexpected number of locations in LibCal hours response: {data}")
        return []
    if len(list(data.values())[0]["weeks"]) != 2:
        logger.error(f"Unexpected number of weeks in LibCal hours response: {data}")
        return []
    if (len(list(data.values())[0]["weeks"][0]) != 7) or (
        len(list(data.values())[0]["weeks"][1]) != 7
    ):
        logger.error(f"Unexpected number of days in LibCal hours response: {data}")
        return []

    weeks = list(data.values())[0]["weeks"]
    first_week = weeks[0]
    second_week = weeks[1]

    # We want to display Monday-Sunday, so we use the first week's Monday-Saturday
    # and the second week's Sunday
    days = first_week
    days["Sunday"] = second_week["Sunday"]

    # Days dicts contain data we don't need, so reformat into a new list of dicts
    hours = []
    for day in days:
        item = {}
        item["date"] = days[day]["date"]
        item["weekday"] = day
        item["rendered_hours"] = days[day]["rendered"]
        hours.append(item)

    # Sort the final hours list by date
    hours = sorted(hours, key=lambda x: x["date"])
    return hours


def get_start_end_dates(hours: list[dict]) -> tuple[str, str]:
    """Given a formatted list of hours, return start and end dates in short
    month-day format, e.g. ("Feb 05","Feb 11")."""
    # Hours list is already sorted by date, so we can just take the first and last items
    # hours list is constructed in order, so we can just take the first and last items
    start = hours[0]["date"]
    formatted_start = format_date(start)
    end = hours[-1]["date"]
    formatted_end = format_date(end)
    return formatted_start, formatted_end


def format_date(date: str) -> str:
    """Format date for display on digital sign. Converts 2024-02-04 to Feb 04."""

    date = datetime.strptime(date, "%Y-%m-%d")
    return date.strftime("%b %d")


def construct_display_url(
    request: HttpRequest, location_id: int, orientation: str
) -> str:
    """Construct URL for display of hours given location ID and orientation."""

    scheme = request.scheme
    host = request.get_host()
    return f"{scheme}://{host}/display_hours/{location_id}/{orientation}"
