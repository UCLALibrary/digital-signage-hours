from django.shortcuts import render
from signs.views_utils import get_weekdays
from django.http import HttpRequest, HttpResponse


def display(request: HttpRequest) -> HttpResponse:
    api_url = "https://calendar.library.ucla.edu/widget/hours/grid?"
    location_ids = {
        "powLab": 2609,
        "powLend": 2608,
        "yrlLend": 2614,
        "powClass": 2607,
    }
    num_weeks = 1

    location_id = location_ids["powClass"]
    weekdays = get_weekdays(api_url, location_id, num_weeks)

    start = weekdays[0]["date"].strftime("%b %d")
    end = weekdays[-1]["date"].strftime("%b %d")

    context = {
        "start": start,
        "end": end,
        "weekdays": weekdays,
    }

    return render(request, "display.html", context)
