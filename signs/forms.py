from django import forms
from signs.models import Location


ORIENTATION_CHOICES = [
    ("landscape", "Landscape (3840x2160)"),
    ("portrait_small", "Portrait (1080x1920)"),
    ("portrait_large", "Portrait (2160x3840)"),
]


# DisplayTypeForm and LocationForm used in get_URL view
class DisplayTypeForm(forms.Form):
    orientation = forms.ChoiceField(choices=ORIENTATION_CHOICES)


class LocationForm(forms.ModelForm):
    location = forms.ModelChoiceField(queryset=Location.objects.all())

    class Meta:
        model = Location
        fields = []
