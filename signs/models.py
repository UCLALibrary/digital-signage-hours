from django.db import models


class Location(models.Model):
    name = models.CharField(
        max_length=100, help_text="This name will be displayed on the digital sign."
    )
    location_id = models.IntegerField(
        help_text="Location ID must match LibCal ID exactly."
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
