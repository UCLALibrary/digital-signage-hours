import logging
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.conf import settings
from signs.models import Location
from signs.views_utils import (
    format_hours,
    get_hours,
    get_single_location_hours,
    get_start_end_dates,
    construct_display_url,
    get_location_events,
    parse_events,
    format_events,
)
from signs.forms import LocationForm

logger = logging.getLogger(__name__)


@login_required
def get_hours_url(request: HttpRequest) -> HttpResponse:
    """Construct URL for display of hours."""
    location_form = LocationForm()
    url = None

    if request.method == "POST":
        location_form = LocationForm(request.POST)
        if location_form.is_valid():
            location_id = location_form.cleaned_data["location"].location_id
            orientation = location_form.cleaned_data["orientation"]
            # run_env is used to determine the correct scheme for the URL (http or https)
            run_env = settings.RUN_ENV
            url = construct_display_url(request, location_id, orientation, run_env)

    context = {"location_form": location_form, "url": url}
    return render(
        request,
        "signs/get_hours_url.html",
        context,
    )


# This view is public, and needs to be allowed in a Rise Vision iframe.
@xframe_options_exempt
def display_hours(
    request: HttpRequest, location_id: int, orientation: str
) -> HttpResponse:
    """Display hours for a location. This view is used by the digital signage system."""

    hours_widget_url = settings.LIBCAL_HOURS_WIDGET

    location_name = Location.objects.get(location_id=location_id).name
    stylesheet = f"css/{orientation}.css"

    hours = get_hours(hours_widget_url, location_id)
    single_location_hours = get_single_location_hours(hours, location_id)
    formatted_hours = format_hours(single_location_hours)
    if not formatted_hours:
        # formatted_hours will be an empty list if there was an error
        context = {
            "location_name": location_name,
            "stylesheet": stylesheet,
            "error": "There was an error retrieving hours for this location.",
        }
        return render(request, "signs/display.html", context)

    start, end = get_start_end_dates(formatted_hours)

    context = {
        "start": start,
        "end": end,
        "hours": formatted_hours,
        "stylesheet": stylesheet,
        "location_name": location_name,
    }
    return render(request, "signs/display.html", context)


# This view is public, and needs to be allowed in a Rise Vision iframe.
@xframe_options_exempt
def display_clicc_events(request: HttpRequest) -> HttpResponse:
    """Display events for CLICC classroom locations.
    This view is used by the digital signage system."""

    events_widget_url = settings.LIBCAL_EVENTS_WIDGET
    # location IDs for CLICC classrooms, with corresponding names used as CSS classes
    locations = [
        {"location_id": 3363, "css_class": "classA"},
        {"location_id": 4357, "css_class": "classB"},
        {"location_id": 4358, "css_class": "classC"},
        {"location_id": 4799, "css_class": "inq3"},
    ]
    location_events = {}

    for location in locations:
        location_id = location["location_id"]
        events = get_location_events(events_widget_url, location_id)
        parsed_events = parse_events(events)
        formatted_events = format_events(parsed_events)
        location_events[location_id] = formatted_events
        for event in formatted_events:
            event["css_class"] = location["css_class"]
    context = {"location_events": location_events}
    return render(request, "signs/display_events.html", context)


@login_required
def show_log(request: HttpRequest, line_count: int = 200) -> HttpResponse:
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
