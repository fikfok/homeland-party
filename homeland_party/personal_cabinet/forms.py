from django import forms
from django.forms import ModelForm, Form

from personal_cabinet.models import Geo


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
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    latitude = forms.FloatField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    longitude = forms.FloatField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    birth_date = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control datetimepicker'}))

    def clean(self):
        pass
        # password1 = self.cleaned_data.get('new_password1')
        # password2 = self.cleaned_data.get('new_password2')
        # if password1 != password2:
        #     raise forms.ValidationError('Пароли не совпадают')
