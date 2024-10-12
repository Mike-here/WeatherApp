import requests
from django.shortcuts import render
from .forms import WeatherPreferencesForm
from datetime import datetime
import sys
from django.conf import settings

ACTIVITIES = [
    {"name": "Hiking", "temp_min": 10, "temp_max": 21},   # ~10 to 21°C
    {"name": "Swimming", "temp_min": 21, "temp_max": 32},  # ~21 to 32°C
    {"name": "Biking", "temp_min": 16, "temp_max": 29},    # ~16 to 29°C
    {"name": "Picnicking", "temp_min": 18, "temp_max": 27}, # ~18 to 27°C
    {"name": "Running", "temp_min": 10, "temp_max": 24},    # ~10 to 24°C
    {"name": "Camping", "temp_min": 7, "temp_max": 27},     # ~7 to 27°C
    {"name": "Fishing", "temp_min": 13, "temp_max": 32},     # ~13 to 32°C
    {"name": "Kayaking", "temp_min": 16, "temp_max": 29},    # ~16 to 29°C
    {"name": "Surfing", "temp_min": 21, "temp_max": 29},     # ~21 to 29°C
    {"name": "Rock Climbing", "temp_min": 10, "temp_max": 24}, # ~10 to 24°C
]


#get location
def get_location():
    response = requests.get("http://ip-api.com/json/")
    data = response.json()
    return {
        'city': data['city'],
        'lat': data['lat'],
        'lon': data['lon']
    }
#fetch weather data
def fetch_weather(lat, lon):
    api_key=settings.WEATHER_API_TOKEN
    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={api_key}"
    response = requests.get(url)
    return response.json()
#fetch news headlines
def fetch_headlines():
    NEWS_API_KEY=settings.NEWS_API_TOKEN
    url = f"https://newsapi.org/v2/top-headlines?language=en&apiKey={NEWS_API_KEY}"
    """ response = requests.get(url)
    return response.json() """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        articles = data.get('articles', [])  # Extract the articles from the response
        return articles
    except requests.exceptions.RequestException as e:
        print(f"Error fetching headlines: {e}")
        return []

# Analyze weather data against user preferences
def analyze_weather(data, preferences):
    optimal_times = []
    
    for entry in data['list']:
        if 'main' in entry and 'temp' in entry['main'] and 'humidity' in entry['main'] and 'weather' in entry and 'dt' in entry:
            temp = entry['main']['temp']
            humidity = entry['main']['humidity']
            condition = entry['weather'][0]['main']
            timestamp = entry['dt']

            # Check if preferences match (case-insensitive for conditions)
            temp_check = preferences['temp_min'] <= temp <= preferences['temp_max']
            humidity_check = preferences['humidity_min'] <= humidity <= preferences['humidity_max']
            condition_check = condition.lower() in [cond.lower() for cond in preferences['conditions']]

            if temp_check and humidity_check and condition_check:
                time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')

                # ACTIVITIES exists and has the correct structure
                suitable_activities = []
                for activity in ACTIVITIES:
                    if activity['temp_min'] <= temp <= activity['temp_max']:
                        suitable_activities.append(activity['name'])
                
                #temp = int((temp * (9/5)) + 32) #convert output temperature to Farenheit
                optimal_times.append({
                    'datetime': time,
                    'temp': temp,
                    'humidity': humidity,
                    'condition': condition,
                    'suitable_activities': suitable_activities
                })
    
    return optimal_times


def index(request):
  if request.method == 'POST':
    form = WeatherPreferencesForm(request.POST)
    if form.is_valid():
      # Get user preferences
      preferences = {
          'temp_min': form.cleaned_data['temp_min'],
          'temp_max': form.cleaned_data['temp_max'],
          'humidity_min': form.cleaned_data['humidity_min'],
          'humidity_max': form.cleaned_data['humidity_max'],
          'conditions': [condition.strip() for condition in form.cleaned_data['conditions'].split(',')],
      }

      # Get location, headlines and weather data
      location = get_location()
      weather_data = fetch_weather(location['lat'], location['lon'])
      top_headlines = fetch_headlines()
      

      # Analyze weather
      optimal_times = analyze_weather(weather_data, preferences)

      return render(request, 'weather/results.html', {
          'location': location['city'],
          'optimal_times': optimal_times,
          'top_headlines': top_headlines,
      })
  else:
    form = WeatherPreferencesForm()

  return render(request, 'weather/index.html', {'form': form})

