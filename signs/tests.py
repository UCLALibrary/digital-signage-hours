from django.test import TestCase
from signs.models import Location
from signs.views_utils import (
    construct_display_url,
    get_start_end_dates,
    get_single_location_hours,
    format_hours,
    format_date,
)
import json


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
