import logging
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from signs.models import Location
from signs.views_utils import get_hours, get_start_end_dates, construct_display_url
from signs.forms import LocationForm, DisplayTypeForm

logger = logging.getLogger(__name__)


def display(request: HttpRequest, location_id: int, orientation: str) -> HttpResponse:
    widget_url = "https://calendar.library.ucla.edu/widget/hours/grid?"

    location_name = Location.objects.get(location_id=location_id).name
    hours = get_hours(widget_url, location_id)
    start, end = get_start_end_dates(hours)
    stylesheet = f"{orientation}.css"

    context = {
        "start": start,
        "end": end,
        "hours": hours,
        "stylesheet": stylesheet,
        "location_name": location_name,
    }
    return render(request, "display.html", context)


def get_URL(request: HttpRequest) -> HttpResponse:
    location_form = LocationForm()
    display_type_form = DisplayTypeForm()

    if request.method == "POST":
        location_form = LocationForm(request.POST)
        display_type_form = DisplayTypeForm(request.POST)

        if location_form.is_valid() and display_type_form.is_valid():
            location_id = location_form.cleaned_data["location"].location_id
            orientation = display_type_form.cleaned_data["orientation"]
            url = construct_display_url(location_id, orientation)
            return render(
                request,
                "get_URL.html",
                {
                    "location_form": location_form,
                    "display_type_form": display_type_form,
                    "url": url,
                },
            )
    return render(
        request,
        "get_URL.html",
        {"location_form": location_form, "display_type_form": display_type_form},
    )
