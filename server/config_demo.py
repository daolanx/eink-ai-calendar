import os

def get_config(key, default):
    return os.environ.get(key, default)

# Paths
log_path = get_config('LOG_PATH', 'log/log.log')  # Log file path
font_path = get_config('FONT_PATH', 'static/wqy-microhei.ttc')

# Server Port
server_port = int(get_config('PORT', '8000'))

# Date API Config
# Calendar API Documentation: https://docs.xygeng.cn/docs/day.html
date_api_url = get_config('DATE_API_URL', 'https://api.xygeng.cn/openapi/day')

# Weather API Config
# QWeather API Documentation https://dev.qweather.com/docs/api/weather/weather-daily-forecast/
weather_api_location = get_config('WEATHER_API_LOCATION', '<YOUR_WEATHER_API_LOCATION>')  # QWeather city code
weather_api_key = get_config('WEATHER_API_KEY', '<YOUR_WEATHER_API_KEY>')  # QWeather API key
weather_api_base_url = get_config('WEATHER_BASE_URL', 'https://devapi.qweather.com/v7/weather/3d')
weather_api_url = f'{weather_api_base_url}?location={weather_api_location}&key={weather_api_key}'

# Motto API Config
# ONE Hitokoto API Documentation: https://docs.xygeng.cn/docs/one.html
motto_api_url = get_config('MOTTO_API_URL', 'https://api.xygeng.cn/openapi/one') # Hitokoto API

# Image API Config
# Alibaba Cloud Model Service Lingji SDK Documentation: https://help.aliyun.com/zh/dashscope/developer-reference/acquisition-and-configuration-of-api-key
image_api_dashscope_api_key = get_config('IMAGE_API_DASHSCOPE_API_KEY', '<YOUR_IMAGE_API_DASHSCOPE_API_KEY>')
image_api_dashscope_model = get_config('IMAGE_API_DASHSCOPE_MODEL', '<YOUR_IMAGE_API_DASHSCOPE_MODEL>')
image_api_dashscope_prompt = get_config('IMAGE_API_DASHSCOPE_PROMPT', "Imagine you are a Tang Dynasty painter, today's weather:{weather}, today's festival:{festival}, today's motto:{motto}, please create a Chinese painting in ink wash style based on this information")

EINK_WIDTH = 448
EINK_HEIGHT = 600
MAIN_IMG_HEIGHT = 370
DATE_IMG_WIDTH = 150
DATE_IMG_HEIGHT = 230
