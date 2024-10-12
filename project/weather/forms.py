from django import forms

class WeatherPreferencesForm(forms.Form):
    temp_min = forms.FloatField(label='Minimum Comfortable Temperature (°C)')
    temp_max = forms.FloatField(label='Maximum Comfortable Temperature (°C)')
    humidity_min = forms.IntegerField(label='Minimum Comfortable Humidity (%)')
    humidity_max = forms.IntegerField(label='Maximum Comfortable Humidity (%)')
    conditions = forms.CharField(label='Weather Conditions (comma-separated)', 
                                 help_text='E.g., Clear, Rain, Clouds')
