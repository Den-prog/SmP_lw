from django import forms

class CoordinateForm(forms.Form):
    lat = forms.FloatField(label='Широта (Latitude)', initial=50.0152)
    lng = forms.FloatField(label='Довгота (Longitude)', initial=36.2247)