from datetime import datetime

from django import forms
from django.forms import ModelForm, Form
from django.utils.html import escape

from homeland_party.const import DEFAULT_LAT, DEFAULT_LON
from homeland_party.settings import geocoder
from personal_cabinet.model_geo import Geo


class GeoForm(ModelForm):
    class Meta:
        model = Geo
        fields = '__all__'

    def clean_geo_lat(self):
        try:
            geo_lat = float(self.cleaned_data['geo_lat'])
        except Exception:
            geo_lat = 0.0
        return geo_lat

    def clean_geo_lon(self):
        try:
            geo_lon = float(self.cleaned_data['geo_lon'])
        except Exception:
            geo_lon = 0.0
        return geo_lon


class ProfileForm(Form):
    user_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    latitude = forms.FloatField(widget=forms.HiddenInput())
    longitude = forms.FloatField(widget=forms.HiddenInput())
    birth_date = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control datetimepicker'}))

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['user_name'].required = False
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False
        self.fields['latitude'].required = False
        self.fields['longitude'].required = False
        self.fields['birth_date'].required = False

    def clean_user_name(self):
        return escape(self.cleaned_data['user_name'])

    def clean_first_name(self):
        return escape(self.cleaned_data['first_name'])

    def clean_last_name(self):
        return escape(self.cleaned_data['last_name'])

    def clean_birth_date(self):
        birth_date = self.cleaned_data['birth_date']
        if birth_date:
            try:
                birth_date = datetime.strptime(self.cleaned_data['birth_date'], "%d.%m.%Y").date()
            except Exception:
                raise forms.ValidationError('Формат даты не корректен')
        return birth_date

    def clean(self):
        latitude = self.cleaned_data.get('latitude')
        longitude = self.cleaned_data.get('longitude')
        # Если координаты остались дефолтными, то игнорируем
        is_default_coords = round(latitude, 5) == round(DEFAULT_LAT, 5) and round(longitude, 5) == round(DEFAULT_LON, 5)
        if is_default_coords:
            self.cleaned_data.pop('latitude')
            self.cleaned_data.pop('longitude')
        else:
            geo_data = geocoder.get_geo_data(latitude=latitude, longitude=longitude)
            if not geo_data:
                raise forms.ValidationError(geocoder.WRONG_GEO_MSG)
