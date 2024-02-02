from django.test import TestCase
from signs.models import Location
from signs.views_utils import construct_display_url

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
