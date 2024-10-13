import logging
import service.image as imageService
import service.date as dateService
import service.weather as weatherService
import service.motto as mottoService

from PIL import Image, ImageDraw
from io import BytesIO


def hello(self):
    message = 'This is esp32 eink server.'
    self.send_response(200)
    self.send_header('Content-type', 'text/html')
    self.send_header('Content-Length', len(message))
    self.end_headers()
    self.wfile.write(message.encode('utf-8'))

def show(self):
  try:
    resDate = dateService.get_today_date()
    weather = weatherService.get_weather()
    motto = mottoService.get_motto()
    logging.info(f'[weather] {weather}')
    logging.info(f'[date] {resDate}')
    logging.info(f'[motto] {motto}')

    canvas = Image.new('RGB', (448, 600), color = (255, 255, 255))

    ai_img = imageService.get_ai_image(resDate, weather, motto)
    if ai_img is None:
        logging.error("AI image generation failed, using fallback image")
        ai_img = Image.new('RGB', (448, 370), color=(200, 200, 200))
        draw = ImageDraw.Draw(ai_img)
        draw.text((10, 10), "AI Image Generation Failed", fill=(0, 0, 0))

    canvas.paste(ai_img, (0, 0))

    dominant_color = imageService.get_dominant_color(ai_img)
    date_img = imageService.get_date_img(dominant_color, resDate)

    motto_img = imageService.get_motto_img(motto)
    canvas.paste(date_img,(448 - 150, 370))

    motto_img = imageService.get_motto_img(motto)
    canvas.paste(motto_img, (0, 370))

    weather_img = imageService.get_weather_img(weather)
    canvas.paste(weather_img, (448 - 150, 370 + 150))

    canvas = imageService.dithering(canvas).convert("RGB")

    # Convert the image to bytes
    canvas_bytes = BytesIO()
    canvas.save(canvas_bytes, format='PNG')

    canvas_bytes = canvas_bytes.getvalue()
    
    self.send_response(200)
    self.send_header('Content-type', 'image/png')
    self.send_header('Content-Length', len(canvas_bytes))
    self.end_headers()
    self.wfile.write(canvas_bytes)
  except Exception as e:
    logging.error(f"Error in show function: {str(e)}")
    self.send_error(500, f"Internal Server Error: {str(e)}")

def bytes(self):
  try:
    resDate = dateService.get_today_date()
    weather = weatherService.get_weather()
    motto = mottoService.get_motto()
    logging.info(f'[weather] {weather}')
    logging.info(f'[date] {resDate}')
    logging.info(f'[motto] {motto}')

    canvas = Image.new('RGB', (448, 600), color = (255, 255, 255))

    ai_img = imageService.get_ai_image(resDate, weather, motto)
    if ai_img is None:
        logging.error("AI image generation failed, using fallback image")
        ai_img = Image.new('RGB', (448, 370), color=(200, 200, 200))
        draw = ImageDraw.Draw(ai_img)
        draw.text((10, 10), "AI Image Generation Failed", fill=(0, 0, 0))

    canvas.paste(ai_img, (0, 0))

    dominant_color = imageService.get_dominant_color(ai_img)
    date_img = imageService.get_date_img(dominant_color, resDate)

    motto_img = imageService.get_motto_img(motto)
    canvas.paste(date_img, (448 - 150, 370))

    canvas.paste(motto_img, (0, 370))

    weather_img = imageService.get_weather_img(weather)
    canvas.paste(weather_img, (448 - 150, 370 + 150))

    canvas = imageService.dithering(canvas).convert("RGB")

    # Apply buffImg processing
    canvas_bytes = imageService.buffImg(canvas)

    self.send_response(200)
    self.send_header('Content-type', 'application/octet-stream')
    self.send_header('Content-Length', len(canvas_bytes))
    self.end_headers()
    self.wfile.write(canvas_bytes)
    
  except Exception as e:
    logging.error(f"Error in bytes function: {str(e)}")
    raise  # Re-raise the exception to be handled by the caller