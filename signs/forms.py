from django import forms
from signs.models import Location


ORIENTATION_CHOICES = [
    ("landscape_small", "Landscape (1920x1080)"),
    ("landscape_large", "Landscape (3840x2160)"),
    ("portrait_small", "Portrait (1080x1920)"),
    ("portrait_large", "Portrait (2160x3840)"),
]


# LocationForm used in get_hours_url view
class LocationForm(forms.ModelForm):
    location = forms.ModelChoiceField(queryset=Location.objects.all())
    orientation = forms.ChoiceField(choices=ORIENTATION_CHOICES)

    class Meta:
        model = Location
        fields = []
