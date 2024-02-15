import requests
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)


def get_hours(widget_url: str, location_id: str) -> dict:
    """Retrieve hours for a location from the LibCal widget.
    Results for parent locations will include hours for all child locations."""
    # We request 2 weeks of hours from the widget to cover Monday-Sunday
    # instead of Sunday-Saturday
    response = requests.get(
        widget_url, params={"lid": location_id, "weeks": 2, "format": "json"}
    )
    data = response.json()
    return data


def get_single_location_hours(data: dict, location_id: str) -> dict:
    """Given a LibCal hours response, return hours for a single location."""

    # We might have extra locations in the response, so check for the one we want
    location_key = f"loc_{location_id}"

    if location_key not in data:
        logger.error(
            f"Location {location_id} not found in LibCal hours response: {data}"
        )
        return {}
    else:
        data = {location_key: data[location_key]}

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

    # Check if the data is empty,
    # since get_hours will return an empty dict if there's an error
    if not data:
        logger.error("No LibCal hours data available for formatting.")
        return []

    weeks = list(data.values())[0]["weeks"]

    # Check that the data contains the expected number of values:
    # 1 location, 2 weeks, 7 days each
    if len(data) != 1:
        logger.error(f"Unexpected number of locations in LibCal hours response: {data}")
        return []
    if len(weeks) != 2:
        logger.error(f"Unexpected number of weeks in LibCal hours response: {data}")
        return []

    first_week = weeks[0]
    second_week = weeks[1]
    if (len(first_week) != 7) or (len(second_week) != 7):
        logger.error(f"Unexpected number of days in LibCal hours response: {data}")
        return []

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


def get_location_events(widget_url: str, location_id: int) -> HttpResponse:
    """Get events for a location from the LibCal widget."""

    widget_url += f"{location_id}"
    response = requests.get(widget_url)
    return response


def parse_events(response: HttpResponse) -> list[dict]:
    """Parse the HTML response from the LibCal widget using BeautifulSoup.
    Return a list of events, each as a dictionary with title and times."""
    if b"No events are scheduled." in response.content:
        return []
    else:
        soup = BeautifulSoup(response.content, "html.parser")
        events = []
        for li in soup.find_all("li"):
            # events are in the form <li><a>Event Title</a><span>Event Times</span></li>
            a_content = li.find("a").text if li.find("a") else ""
            span_content = li.find("span").text if li.find("span") else ""
            events.append({"title": a_content, "times": span_content})
    return events


def format_events(events: list[dict]) -> list[dict]:
    """Format events for display on the digital sign."""
    parsed_events = []
    for event in events:
        # events are in the form of "8:00am - 12:00pm Friday, February 2, 2024"
        # we only want the times
        start, end = event["times"].split(" - ")
        end = end.split(" ")[0]

        # we now have times in the form of "8:00am"
        # convert to datetime.time
        strptime_format = "%I:%M%p"
        start_time = datetime.strptime(start, strptime_format).time()
        end_time = datetime.strptime(end, strptime_format).time()

        # only display events starting and ending between 8am and 8pm
        if (start_time >= datetime.strptime("8:00am", strptime_format).time()) and (
            end_time <= datetime.strptime("8:00pm", strptime_format).time()
        ):
            start_css_row = get_css_grid_row(start_time)
            end_css_row = get_css_grid_row(end_time)
            parsed_events.append(
                {
                    "title": event["title"],
                    "start_time": start_time,
                    "end_time": end_time,
                    "start_css_row": start_css_row,
                    "end_css_row": end_css_row,
                }
            )
    return parsed_events


def get_css_grid_row(time: datetime) -> str:
    """Given a time, return the grid row that corresponds to the time."""
    # time is a datetime object with only the time set
    # return the grid row that corresponds to the time
    # 8am is row 2, 8:30am is row 3, 9am is row 4, etc.
    hour = time.hour
    minute = time.minute

    # events starting on the half hour or later should be on the next row
    # so add 0.5 to the hour (since we multiply by 2 in getting the row number)
    if minute >= 30:
        hour += 0.5

    return str(int((hour - 8) * 2 + 2))
