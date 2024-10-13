import requests
from typing import TypedDict, List
from datetime import datetime
from config import date_api_url


class DateInfo(TypedDict):
    date: str
    year: str
    month: str
    day: str
    weekday: str
    lunar_date: str
    festival: List[str]

def get_today_date() -> DateInfo:
    now = datetime.now()
    default_date = DateInfo(
        date=now.strftime("%Y/%m/%d"),
        year=now.strftime("%Y"),
        month=now.strftime("%m"),
        day=now.strftime("%d"),
        weekday=now.strftime("%A"),
        lunar_date="",
        festival=""
    )
    
    try:
        response = requests.get(date_api_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data['code'] == 200 and 'data' in data:
            date_info = data['data']
            return DateInfo(
                date=f"{date_info['solar']['year']}/{date_info['solar']['month']}/{date_info['solar']['date']}",
                weekday=date_info['solar']['day'],
                year=str(date_info['solar']['year']),
                month=str(date_info['solar']['month']),
                day=str(date_info['solar']['date']),
                lunar_date=f"{date_info['lunar']['month']}{date_info['lunar']['date']}",
                festival = date_info['festival'][0] if date_info['festival'] else ''
            )
        else:
            return default_date
    except Exception as e:
        print(f"Error fetching date information: {e}")
        return default_date
