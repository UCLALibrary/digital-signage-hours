import requests
import logging
from datetime import datetime
from bs4 import BeautifulSoup
from signs.models import Location

logger = logging.getLogger(__name__)


def get_hours(widget_url: str, location_id: str) -> list[dict]:
    # We request 2 weeks of hours from the widget to cover Monday-Sunday instead of Sunday-Saturday
    response = requests.get(
        widget_url, params={"lid": location_id, "weeks": 2, "format": "json"}
    )
    data = response.json()

    # Data comes back as a dictionary with one key (related to location ID) and a value that is a dictionary
    # This dictionary has a key "weeks" with a value that is a list of dictionaries, one for each week
    # Each week dictionary has keys for each day of the week, with values that are dictionaries with data about the day
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


def get_location_events(location_id: int) -> list[dict]:
    widget_url = (
        "https://calendar.library.ucla.edu/api_events.php?m=today&simple=ul_date&cid="
    )
    events = []
    widget_url += f"{location_id}"
    response = requests.get(widget_url)
    if "No events are scheduled." in response.text:
        return events
    else:
        soup = BeautifulSoup(response.text, "html.parser")
        events = []
        for li in soup.find_all("li"):
            # events are in the form of <li><a>Event Title</a><span>Event Times</span></li>
            a_content = li.find("a").text if li.find("a") else ""
            span_content = li.find("span").text if li.find("span") else ""
            events.append(
                {
                    "title": a_content,
                    "times": span_content,
                    "location_id": location_id,
                }
            )

    return events


def parse_location_events(events: list[dict]) -> list[dict]:
    parsed_events = []
    for event in events:
        # events are in the form of "8:00am - 12:00pm Friday, February 2, 2024"
        start, end = event["times"].split(" - ")
        end = end.split(" ")[0]

        start_time = datetime.strptime(start, "%I:%M%p").time()
        end_time = datetime.strptime(end, "%I:%M%p").time()
        # only display events starting and ending between 8am and 8pm
        if (start_time >= datetime.strptime("8:00am", "%I:%M%p").time()) and (
            end_time <= datetime.strptime("8:00pm", "%I:%M%p").time()
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
    # time is a datetime object with only the time set
    # return the grid row that corresponds to the time
    # 8am is row 1, 8:30am is row 2, etc
    hour = time.hour
    minute = time.minute
    if minute == 30:
        hour += 0.5
    return str((hour - 8) * 2 + 1)
