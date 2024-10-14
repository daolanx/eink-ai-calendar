import os

def get_config(key, default):
    return os.environ.get(key, default)

# Paths
log_path = get_config('LOG_PATH', 'log/log.log')  # 日志文件路径
font_path = get_config('FONT_PATH', 'static/wqy-microhei.ttc')

# Server Port
server_port = int(get_config('PORT', '8000'))

# Date API Config
# 万年历 API 文档：https://docs.xygeng.cn/docs/day.html
date_api_url = get_config('DATE_API_URL', 'https://api.xygeng.cn/openapi/day')

# Weather API Config
# 和风天气 API 文档 https://dev.qweather.com/docs/api/weather/weather-daily-forecast/
weather_api_location = get_config('WEATHER_API_LOCATION', '<YOUR_WEATHER_API_LOCATION>')  # 和风天气城市编码
weather_api_key = get_config('WEATHER_API_KEY', '<YOUR_WEATHER_API_KEY>')  # 和风天气API密钥
weather_api_base_url = get_config('WEATHER_BASE_URL', 'https://devapi.qweather.com/v7/weather/3d')
weather_api_url = f'{weather_api_base_url}?location={weather_api_location}&key={weather_api_key}'

# Motto  API Config
# ONE 一言 API 文档：https://docs.xygeng.cn/docs/one.html
motto_api_url = get_config('MOTTO_API_URL', 'https://api.xygeng.cn/openapi/one') # 一言API

# Image API Config
# 阿里云 模型服务灵积 SDK 文档：https://help.aliyun.com/zh/dashscope/developer-reference/acquisition-and-configuration-of-api-key
image_api_dashscope_api_key = get_config('IMAGE_API_DASHSCOPE_API_KEY', '<YOUR_IMAGE_API_DASHSCOPE_API_KEY>')
image_api_dashscope_model = get_config('IMAGE_API_DASHSCOPE_MODEL', '<YOUR_IMAGE_API_DASHSCOPE_MODEL>')
image_api_dashscope_prompt = get_config('IMAGE_API_DASHSCOPE_PROMPT', "假设你是个唐代画家，当天天气:{weather}，当天节日:{festival}，当天格言:{motto}，请结合上述信息创作一幅中国画，水墨风格")

EINK_WIDTH = 448
EINK_HEIGHT = 600
MAIN_IMG_HEIGHT = 370
DATE_IMG_WIDTH = 150
DATE_IMG_HEIGHT = 230

