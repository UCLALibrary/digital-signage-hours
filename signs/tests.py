from django.test import TestCase
from signs.models import Location
from signs.views_utils import construct_display_url, get_hours, get_start_end_dates

# Create your tests here.


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
        url = construct_display_url(powell.location_id, "portrait_small")
        self.assertEqual(url, "/display/1/portrait_small")


class GetStartEndDatesTestCase(TestCase):
    def test_get_start_end_dates(self):
        hours = [
            {"date": "2024-01-29", "weekday": "Monday", "rendered_hours": "8am - 5pm"},
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
            {"date": "2024-02-02", "weekday": "Friday", "rendered_hours": "8am - 3pm"},
            {
                "date": "2024-02-03",
                "weekday": "Saturday",
                "rendered_hours": "Closed",
            },
            {"date": "2024-02-04", "weekday": "Sunday", "rendered_hours": "Closed"},
        ]
        start, end = get_start_end_dates(hours)
        self.assertEqual(start, "Jan 29")
        self.assertEqual(end, "Feb 04")
