import requests
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from signs.models import Location

logger = logging.getLogger(__name__)


def get_hours(widget_url: str, location_id: str) -> list[dict]:
    # We request 2 weeks of hours from the widget to cover Monday-Sunday
    # instead of Sunday-Saturday
    response = requests.get(
        widget_url, params={"lid": location_id, "weeks": 2, "format": "json"}
    )
    data = response.json()
    return data


def format_hours(data: dict) -> list[dict]:
    # Data comes back from get_hours() as a dictionary with one key (related to location ID),
    # and a value that is a dictionary
    # This dictionary has a key "weeks" with a value that is a list of dictionaries,
    # one for each week
    # Each week dictionary has keys for each day of the week,
    # with values that are dictionaries with data about the day
    weeks = list(data.values())[0]["weeks"]
    first_week = weeks[0]
    second_week = weeks[1]

    days = {}
    days["Monday"] = first_week["Monday"]
    days["Tuesday"] = first_week["Tuesday"]
    days["Wednesday"] = first_week["Wednesday"]
    days["Thursday"] = first_week["Thursday"]
    days["Friday"] = first_week["Friday"]
    days["Saturday"] = first_week["Saturday"]
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
    # hours list is constructed in order, so we can just take the first and last items
    start = hours[0]["date"]
    start = datetime.strptime(start, "%Y-%m-%d")
    start = start.strftime("%b %d")
    end = hours[-1]["date"]
    end = datetime.strptime(end, "%Y-%m-%d")
    end = end.strftime("%b %d")
    return start, end


def construct_display_url(location_id: int, orientation: str) -> str:
    return f"/display_hours/{location_id}/{orientation}"
