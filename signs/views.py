import logging
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from signs.models import Location
from signs.views_utils import (
    get_hours,
    format_hours,
    get_start_end_dates,
    construct_display_url,
)
from signs.forms import LocationForm, DisplayTypeForm

logger = logging.getLogger(__name__)


@login_required
def get_hours_URL(request: HttpRequest) -> HttpResponse:
    """Construct URL for display of hours."""
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
                "signs/get_URL.html",
                {
                    "location_form": location_form,
                    "display_type_form": display_type_form,
                    "url": url,
                },
            )
    return render(
        request,
        "signs/get_URL.html",
        {"location_form": location_form, "display_type_form": display_type_form},
    )


def display_hours(
    request: HttpRequest, location_id: int, orientation: str
) -> HttpResponse:
    """Display hours for a location. This view is used by the digital signage system."""

    widget_url = "https://calendar.library.ucla.edu/widget/hours/grid?"

    location_name = Location.objects.get(location_id=location_id).name
    hours = get_hours(widget_url, location_id)
    formatted_hours = format_hours(hours)
    start, end = get_start_end_dates(formatted_hours)
    stylesheet = f"css/{orientation}.css"

    context = {
        "start": start,
        "end": end,
        "hours": formatted_hours,
        "stylesheet": stylesheet,
        "location_name": location_name,
    }
    return render(request, "signs/display.html", context)


@login_required
def show_log(request, line_count: int = 200) -> HttpResponse:
    """Display log."""
    log_file = "logs/application.log"
    try:
        with open(log_file, "r") as f:
            # Get just the last line_count lines in the log.
            lines = f.readlines()[-line_count:]
            # Template prints these as a single block, so join lines into one chunk.
            log_data = "".join(lines)
    except FileNotFoundError:
        log_data = f"Log file {log_file} not found"

    return render(request, "signs/log.html", {"log_data": log_data})


@login_required
def release_notes(request: HttpRequest) -> HttpResponse:
    """Display release notes."""
    return render(request, "signs/release_notes.html")
