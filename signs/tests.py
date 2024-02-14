from django.test import TestCase
from django.http import HttpResponse
from signs.models import Location
from signs.views_utils import (
    construct_display_url,
    get_start_end_dates,
    get_single_location_hours,
    format_hours,
    format_date,
    parse_location_events,
    format_events,
    get_css_grid_row,
)
import json
import datetime


class LocationTestCase(TestCase):
    def setUp(self):
        Location.objects.create(name="Powell Library", location_id=1)

    def test_location_name(self):
        powell = Location.objects.get(location_id=1)
        self.assertEqual(powell.name, "Powell Library")


class ConstructDisplayURLTestCase(TestCase):
    def setUp(self):
        Location.objects.create(name="Powell Library", location_id=1)

    def test_construct_display_url(self):
        powell = Location.objects.get(location_id=1)
        response = self.client.get("get_hours_url/")
        request = response.wsgi_request
        url = construct_display_url(request, powell.location_id, "portrait_small")
        # dummy request will have host of "testserver" and scheme of "http"
        self.assertEqual(url, "http://testserver/display_hours/1/portrait_small")


class GetStartEndDatesTestCase(TestCase):
    def test_get_start_end_dates(self):
        hours = [
            {
                "date": "2024-01-29",
                "weekday": "Monday",
                "rendered_hours": "8am - 5pm",
            },
            {
                "date": "2024-01-30",
                "weekday": "Tuesday",
                "rendered_hours": "8am - 5pm",
            },
            {
                "date": "2024-01-31",
                "weekday": "Wednesday",
                "rendered_hours": "8am - 5pm",
            },
            {
                "date": "2024-02-01",
                "weekday": "Thursday",
                "rendered_hours": "8am - 5pm",
            },
            {
                "date": "2024-02-02",
                "weekday": "Friday",
                "rendered_hours": "8am - 3pm",
            },
            {
                "date": "2024-02-03",
                "weekday": "Saturday",
                "rendered_hours": "Closed",
            },
            {
                "date": "2024-02-04",
                "weekday": "Sunday",
                "rendered_hours": "Closed",
            },
        ]
        start, end = get_start_end_dates(hours)
        self.assertEqual(start, "Jan 29")
        self.assertEqual(end, "Feb 04")

    def test_get_start_end_dates_single_day(self):
        hours = [
            {
                "date": "2024-02-04",
                "weekday": "Sunday",
                "rendered_hours": "Closed",
            }
        ]
        start, end = get_start_end_dates(hours)
        self.assertEqual(start, "Feb 04")
        self.assertEqual(end, "Feb 04")


class FormatDateTestCase(TestCase):
    def test_format_date(self):
        date = "2024-05-25"
        formatted_date = format_date(date)
        self.assertEqual(formatted_date, "May 25")

    def test_format_date_single_digit(self):
        date = "2024-02-04"
        formatted_date = format_date(date)
        self.assertEqual(formatted_date, "Feb 04")


class FormatHoursTestCase(TestCase):
    def test_format_hours(self):
        with open("signs/fixtures/libcal_hours_response_two_weeks.json") as f:
            data = json.load(f)
        # Test response covers "2024-02-04" to "2024-02-17"
        # Formatted hours should cover "2024-02-05" to "2024-02-11"
        hours = format_hours(data)
        # 1 week of hours, 7 days
        self.assertEqual(len(hours), 7)
        # Monday, Feb 5th to Sunday, Feb 11th
        # Open 10am - 4pm on Monday, closed on Sunday
        self.assertEqual(hours[0]["date"], "2024-02-05")
        self.assertEqual(hours[0]["weekday"], "Monday")
        self.assertEqual(hours[0]["rendered_hours"], "10am - 4pm")

        self.assertEqual(hours[6]["date"], "2024-02-11")
        self.assertEqual(hours[6]["weekday"], "Sunday")
        self.assertEqual(hours[6]["rendered_hours"], "Closed")

    def test_format_hours_missing_days(self):
        with open("signs/fixtures/libcal_hours_response_missing_days.json") as f:
            data = json.load(f)
        # Test is missing Fri-Sat of 2nd week, so should return empty list
        hours = format_hours(data)
        self.assertEqual(hours, [])

    def test_format_hours_missing_week(self):
        with open("signs/fixtures/libcal_hours_response_one_week.json") as f:
            data = json.load(f)
        # Test is missing 2nd week, so should return empty list
        hours = format_hours(data)
        self.assertEqual(hours, [])

    def test_format_hours_multiple_locations(self):
        with open("signs/fixtures/libcal_hours_response_multiple_locations.json") as f:
            data = json.load(f)
        # Test has multiple locations, so should return empty list
        hours = format_hours(data)
        self.assertEqual(hours, [])

    def test_format_hours_wrong_order(self):
        with open("signs/fixtures/libcal_hours_response_wrong_order.json") as f:
            data = json.load(f)
        # Test has days out of order, but the correct structure
        hours = format_hours(data)
        # Should return a list of 7 days, in order
        self.assertEqual(len(hours), 7)

        self.assertEqual(hours[0]["date"], "2024-02-05")
        self.assertEqual(hours[0]["weekday"], "Monday")
        self.assertEqual(hours[0]["rendered_hours"], "10am - 4pm")

        self.assertEqual(hours[6]["date"], "2024-02-11")
        self.assertEqual(hours[6]["weekday"], "Sunday")
        self.assertEqual(hours[6]["rendered_hours"], "Closed")


class GetSingleLocationHoursTestCase(TestCase):
    def test_get_single_location_hours(self):
        with open("signs/fixtures/libcal_hours_response_two_weeks.json") as f:
            data = json.load(f)
        # standard single-location response for location
        # "Arts Library Reference Desk", ID 20525
        single_location_hours = get_single_location_hours(data, "20525")

        # we should have single location in the response
        self.assertEqual(len(single_location_hours), 1)
        self.assertEqual(
            single_location_hours["loc_20525"]["name"], "Arts Library Reference Desk"
        )
        # we expect two weeks of hours (2 dictionaries in the "weeks" list)
        self.assertEqual(len(single_location_hours["loc_20525"]["weeks"]), 2)

    def test_get_multiple_location_hours(self):
        with open("signs/fixtures/libcal_hours_response_multiple_locations.json") as f:
            data = json.load(f)
        # data contains two locations, 20525 and 4690
        # try to get hours for location 20525
        single_location_hours = get_single_location_hours(data, "20525")
        # should have single location in the response
        # we should have single location in the response
        self.assertEqual(len(single_location_hours), 1)
        self.assertEqual(
            single_location_hours["loc_20525"]["name"], "Arts Library Reference Desk"
        )
        # we expect two weeks of hours (2 dictionaries in the "weeks" list)
        self.assertEqual(len(single_location_hours["loc_20525"]["weeks"]), 2)

    def test_get_missing_location_hours(self):
        with open("signs/fixtures/libcal_hours_response_two_weeks.json") as f:
            data = json.load(f)
        # this ID is not in the response, so should return an empty dict
        single_location_hours = get_single_location_hours(data, "11111111")
        self.assertEqual(single_location_hours, {})


class ParseLocationEventsTestCase(TestCase):
    def test_parse_location_events(self):
        with open("signs/fixtures/libcal_events_response_3363.txt") as f:
            html_response = f.read()
        data = HttpResponse(html_response)
        location_id = 3363
        parsed_events = parse_location_events(location_id, data)
        self.assertEqual(len(parsed_events), 4)
        # check that the parsed events are for the correct location
        for event in parsed_events:
            self.assertEqual(event["location_id"], location_id)

    def test_parse_location_events_no_event(self):
        with open("signs/fixtures/libcal_events_response_10430.txt") as f:
            html_response = f.read()
        data = HttpResponse(html_response)
        location_id = 10430
        parsed_events = parse_location_events(location_id, data)
        # no events for this location, so should return an empty list
        self.assertEqual(parsed_events, [])


class FormatEventsTestCase(TestCase):
    def test_format_events(self):
        with open("signs/fixtures/libcal_events_response_3363.txt") as f:
            html_response = f.read()
        data = HttpResponse(html_response)
        location_id = 3363
        parsed_events = parse_location_events(location_id, data)
        formatted_events = format_events(parsed_events)
        # should have 3 events after formatting
        self.assertEqual(len(formatted_events), 3)
        # check expected values for first event
        self.assertEqual(formatted_events[0]["title"], "Philosophy 31")
        self.assertEqual(formatted_events[0]["start_time"], datetime.time(9, 30))
        self.assertEqual(formatted_events[0]["end_time"], datetime.time(11, 30))

    def test_format_events_no_event(self):
        with open("signs/fixtures/libcal_events_response_10430.txt") as f:
            html_response = f.read()
        data = HttpResponse(html_response)
        location_id = 10430
        parsed_events = parse_location_events(location_id, data)
        formatted_events = format_events(parsed_events)
        # no events for this location, so should return an empty list
        self.assertEqual(formatted_events, [])


class GetCSSGridRowTestCase(TestCase):
    def test_get_css_grid_row(self):
        nine_am = datetime.time(9, 0)
        row = get_css_grid_row(nine_am)
        self.assertEqual(row, "4")

    def test_get_css_grid_row_half_hour(self):
        nine_thirty_am = datetime.time(9, 30)
        row = get_css_grid_row(nine_thirty_am)
        self.assertEqual(row, "5")

    def test_get_css_grid_rounded_down(self):
        nine_fifteen_am = datetime.time(9, 15)
        row = get_css_grid_row(nine_fifteen_am)
        # should round down to 9:00am, row 4
        self.assertEqual(row, "4")
