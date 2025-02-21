import requests
from typing import TypedDict, Optional
from config import motto_api_url

class MottoInfo(TypedDict):
    content: str
    origin: Optional[str]

def get_motto() -> MottoInfo:
    default_motto = MottoInfo(content="Silence is golden.", origin=None)
    
    try:
        response = requests.get(motto_api_url, timeout=5)
        response.raise_for_status()
        one = response.json()
        one_data = one['data']
        content: str = one_data.get('content', '')
        origin: Optional[str] = one_data.get('origin')
        
        if content:
            return MottoInfo(content=content, origin=origin)
        else:
            return default_motto
    except Exception as e:
        print(f"Error fetching motto: {e}")
        return default_motto
