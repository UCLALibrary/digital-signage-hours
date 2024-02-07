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
    return hours


def get_start_end_dates(hours: list[dict]) -> tuple[str, str]:
    """Given a formatted list of hours, return start and end dates in short
    month-day format, e.g. ("Feb 05","Feb 11")."""
    # hours list is constructed in order, so we can just take the first and last items
    start = hours[0]["date"]
    start = datetime.strptime(start, "%Y-%m-%d")
    start = start.strftime("%b %d")
    end = hours[-1]["date"]
    end = datetime.strptime(end, "%Y-%m-%d")
    end = end.strftime("%b %d")
    return start, end


def construct_display_url(
    request: HttpRequest, location_id: int, orientation: str
) -> str:
    """Construct URL for display of hours given location ID and orientation."""

    scheme = request.scheme
    host = request.get_host()
    return f"{scheme}://{host}/display_hours/{location_id}/{orientation}"
