"""Weather service using OpenWeatherMap API."""

import os
import requests
from django.conf import settings


# OpenWeatherMap API endpoint
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_api_key() -> str:
    """Get the OpenWeatherMap API key from settings or environment."""
    return getattr(settings, 'OPENWEATHER_API_KEY', None) or os.environ.get('OPENWEATHER_API_KEY', '')


def get_location() -> str:
    """Get the configured weather location."""
    return getattr(settings, 'WEATHER_LOCATION', None) or os.environ.get('WEATHER_LOCATION', 'Toronto,CA')


def get_weather(location: str = None) -> dict:
    """Fetch current weather data from OpenWeatherMap.

    Args:
        location: City name (e.g., "Toronto,CA") or coordinates.
                  Uses configured default if not specified.

    Returns:
        Weather data dict with temp, conditions, humidity, wind, etc.

    Raises:
        ValueError: If API key is not configured
        requests.RequestException: If API call fails
    """
    api_key = get_api_key()
    if not api_key:
        raise ValueError("OPENWEATHER_API_KEY not configured")

    location = location or get_location()

    params = {
        'q': location,
        'appid': api_key,
        'units': 'metric',  # Celsius
    }

    response = requests.get(BASE_URL, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    # Parse response into simplified format
    weather = {
        'location': data.get('name', location),
        'country': data.get('sys', {}).get('country', ''),
        'temp_c': round(data['main']['temp']),
        'feels_like_c': round(data['main']['feels_like']),
        'humidity': data['main']['humidity'],
        'description': data['weather'][0]['description'] if data.get('weather') else 'unknown',
        'wind_speed_kmh': round(data['wind']['speed'] * 3.6),  # m/s to km/h
        'wind_direction': _wind_direction(data['wind'].get('deg', 0)),
    }

    # Add optional fields if present
    if 'visibility' in data:
        weather['visibility_km'] = round(data['visibility'] / 1000, 1)

    if data.get('clouds'):
        weather['cloud_cover'] = data['clouds'].get('all', 0)

    return weather


def _wind_direction(degrees: int) -> str:
    """Convert wind degrees to compass direction."""
    directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    index = round(degrees / 45) % 8
    return directions[index]


def format_weather(weather: dict) -> str:
    """Format weather data into a readable string.

    Args:
        weather: Weather dict from get_weather()

    Returns:
        Formatted weather string
    """
    lines = [
        f"{weather['location']}, {weather['country']}: {weather['description'].title()}",
        f"Temp: {weather['temp_c']}°C (feels like {weather['feels_like_c']}°C)",
        f"Humidity: {weather['humidity']}%",
        f"Wind: {weather['wind_speed_kmh']} km/h {weather['wind_direction']}",
    ]

    if 'visibility_km' in weather:
        lines.append(f"Visibility: {weather['visibility_km']} km")

    if 'cloud_cover' in weather:
        lines.append(f"Cloud cover: {weather['cloud_cover']}%")

    return "\n".join(lines)


def is_good_for_painting(weather: dict) -> tuple[bool, str]:
    """Check if weather conditions are suitable for spray painting outside.

    Ideal conditions:
    - Temperature: 10-30°C
    - Humidity: 40-70%
    - Low wind: < 15 km/h
    - No rain

    Args:
        weather: Weather dict from get_weather()

    Returns:
        Tuple of (is_good, reason)
    """
    issues = []

    temp = weather['temp_c']
    if temp < 10:
        issues.append(f"too cold ({temp}°C, need 10°C+)")
    elif temp > 30:
        issues.append(f"too hot ({temp}°C, need under 30°C)")

    humidity = weather['humidity']
    if humidity < 40:
        issues.append(f"too dry ({humidity}%, need 40%+)")
    elif humidity > 70:
        issues.append(f"too humid ({humidity}%, need under 70%)")

    wind = weather['wind_speed_kmh']
    if wind > 15:
        issues.append(f"too windy ({wind} km/h, need under 15)")

    desc = weather['description'].lower()
    if any(word in desc for word in ['rain', 'drizzle', 'shower', 'storm', 'snow']):
        issues.append(f"precipitation ({weather['description']})")

    if issues:
        return False, "Not ideal: " + ", ".join(issues)

    return True, f"Good conditions! {temp}°C, {humidity}% humidity, {wind} km/h wind"
