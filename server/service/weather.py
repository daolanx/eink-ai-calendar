import requests
from config import weather_api_url, weather_api_key

from typing import Optional, TypedDict
from dataclasses import dataclass

@dataclass
class WeatherInfo(TypedDict):
    weather: str  # 白天天气状况
    tempRange: str  # 温度范围

# get today weather
def get_weather() -> Optional[WeatherInfo]:
    weather_url = weather_api_url
    weather = requests.get(weather_url).json()
    
    if weather['code'] == '200' and weather['daily']:
        today = weather['daily'][0]
        return {
            'weather': today['textDay'],
            'tempRange':  f"{today['tempMin']} ~ {today['tempMax']}°C"
        }
    else:
        return None