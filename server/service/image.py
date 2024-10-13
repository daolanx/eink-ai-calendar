import re
import requests
import dashscope
import logging
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from dashscope import ImageSynthesis
from config import image_api_dashscope_api_key, image_api_dashscope_model, image_api_dashscope_prompt, font_path
from http import HTTPStatus
import random

dashscope.api_key = image_api_dashscope_api_key

def get_ai_image(date, weather, motto):
    image = generate_ai_image(date, weather, motto)
    
    if image is None:
        # 如果AI生成失败，创建一个有趣的默认图像
        image = create_interesting_default_image(448, 370)
    
    return image

def generate_ai_image(date, weather, motto):
    prompt = image_api_dashscope_prompt.format(
        weather=weather['weather'] if weather else '',
        festival=date['festival'] if date else '',
        motto=motto['content'] if motto else ''
    )
    print('[prompt]', prompt)
    try:
        rsp = ImageSynthesis.call(model=image_api_dashscope_model,
                                  prompt=prompt,
                                  size='768*512')
        if rsp.status_code == HTTPStatus.OK:
            logging.info(f"Image generation response: {rsp.output}")
            if rsp.output.get('results') and len(rsp.output['results']) > 0:
                image_url = rsp.output['results'][0].get('url')
                if image_url:
                    img_response = requests.get(image_url, timeout=60)
                    img_response.raise_for_status()
                    ai_img_pil = Image.open(BytesIO(img_response.content))
                    
                    # Calculate the aspect ratio of the original image
                    aspect_ratio = ai_img_pil.width / ai_img_pil.height
                    target_ratio = 448 / 370

                    if aspect_ratio > target_ratio:
                        # Image is wider, crop the width
                        new_width = int(ai_img_pil.height * target_ratio)
                        left = (ai_img_pil.width - new_width) // 2
                        ai_img_cropped = ai_img_pil.crop((left, 0, left + new_width, ai_img_pil.height))
                    else:
                        # Image is taller, crop the height
                        new_height = int(ai_img_pil.width / target_ratio)
                        top = (ai_img_pil.height - new_height) // 2
                        ai_img_cropped = ai_img_pil.crop((0, top, ai_img_pil.width, top + new_height))

                    # Resize the cropped image to the target size
                    ai_img_resized = ai_img_cropped.resize((448, 370), Image.LANCZOS)
                    return ai_img_resized
                else:
                    logging.error("No image URL in the response")
            else:
                logging.error("No results in the response")
        else:
            logging.error(f'Failed to generate image, status_code: {rsp.status_code}, code: {rsp.code}, message: {rsp.message}')
    except Exception as e:
        logging.error(f'Error in generate_ai_image: {str(e)}')
    return None

def get_dominant_color(pil_img):
    if pil_img is None:
        return (200, 200, 200)  # 默认灰色
    img = pil_img.copy()
    img = img.convert("RGBA")
    img = img.resize((5, 5), resample=0)
    dominant_color = img.getpixel((2, 2))[:3]  # 获取RGB值，忽略Alpha通道
    # 检查颜色是否接近白色，如果是则返回黑色
    threshold = 180  # 定义"接近白色"的阈值
    if all(c > threshold for c in dominant_color):
        # 如果颜色太接近白色，返回黑色
        return (0, 0, 0)  # 黑色
    
    return dominant_color

def get_date_img(dominant_color, date_info):
    date_img = Image.new('RGB', (150, 230), color = (255, 255, 255))
    draw = ImageDraw.Draw(date_img)

    fnt_s = ImageFont.truetype(font_path, 17)
    fnt_b = ImageFont.truetype(font_path, 80)

    text_bbox = draw.textbbox((0, 0), date_info['day'], font=fnt_b)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    draw.text(((150 - text_width) / 2, 0), date_info['day'], font=fnt_b, fill=dominant_color)

    # Center date_info['date']
    date_text = date_info['date']
    date_bbox = draw.textbbox((0, 0), date_text, font=fnt_s)
    date_width = date_bbox[2] - date_bbox[0]
    draw.text(((150 - date_width) / 2, text_height + 30), date_text, font=fnt_s, fill=(0, 0, 0))

    # Center date_info['festival']
    festival_text = date_info['festival'] if isinstance(date_info['festival'], str) else ' '.join(date_info['festival'])
    festival_bbox = draw.textbbox((0, 0), festival_text, font=fnt_s)
    festival_width = festival_bbox[2] - festival_bbox[0]
    draw.text(((150 - festival_width) / 2, text_height + 60), festival_text, font=fnt_s, fill=(0, 0, 0))

    return date_img

def get_motto_img(motto_info):
    max_width = 448 - 150
    max_height = 600 - 370
    canvas = Image.new('RGB', (max_width, max_height), color=(255, 255, 255))  # 使用白色背景
    fnt = ImageFont.truetype(font_path, 16)
    draw = ImageDraw.Draw(canvas)

    content = motto_info['content']
    origin = f"—— {motto_info['origin']}" if motto_info['origin'] else ""

    # 计算实际的行高
    font_bbox = fnt.getbbox('Ay')  # 使用包含上下延伸的字符来获取更准确的高度
    line_height = font_bbox[3] - font_bbox[1]
    line_spacing = int(line_height * 0.4)  # 添加 40% 的行间距
    total_line_height = line_height + line_spacing

    # 首先按 \n 分割
    content_lines = content.split('\n')
    
    # 然后对每一行进行标点符号分割
    punctuation = r'[，。！？；：、,]'
    final_content_lines = []
    for line in content_lines:
        content_segments = re.split(f'({punctuation})', line)
        content_segments = [seg for seg in content_segments if seg]  # 移除空字符串

        current_line = ""
        for segment in content_segments:
            if draw.textbbox((0, 0), current_line + segment, font=fnt)[2] <= max_width:
                current_line += segment
            else:
                if current_line:
                    final_content_lines.append(current_line)
                current_line = segment
        if current_line:
            final_content_lines.append(current_line)

    # 计算文本总高度（包括内容和来源，以及额外的空间）
    extra_space = total_line_height  # 在内容和来源之间添加一个额外的行高
    total_text_height = (len(final_content_lines) + (1 if origin else 0)) * total_line_height + extra_space - line_spacing

    # 计算起始 y 坐标以使文本垂直居中
    start_y = (max_height - total_text_height) // 2

    # 计算所有行的最大宽度
    max_line_width = max(draw.textbbox((0, 0), line, font=fnt)[2] for line in final_content_lines)
    if origin:
        max_line_width = max(max_line_width, draw.textbbox((0, 0), origin, font=fnt)[2])

    # 计算整体左边距，使文本块水平居中
    left_margin = (max_width - max_line_width) // 2

    # 绘制内容文本
    for i, line in enumerate(final_content_lines):
        bbox = draw.textbbox((0, 0), line, font=fnt)
        line_width = bbox[2] - bbox[0]
        x = left_margin + (max_line_width - line_width) // 2  # 使每行文本在文本块内水平居中
        y = start_y + i * total_line_height
        draw.text((x, y), line, font=fnt, fill=(0, 0, 0))

    # 绘制来源（如果有）
    if origin:
        bbox = draw.textbbox((0, 0), origin, font=fnt)
        line_width = bbox[2] - bbox[0]
        x = left_margin + max_line_width - line_width  # 靠右对齐，但在文本块内
        y = start_y + len(final_content_lines) * total_line_height + extra_space  # 添加额外的空间
        draw.text((x, y), origin, font=fnt, fill=(0, 0, 0))

    return canvas

def get_weather_img(res_weather):
    weather_img = Image.new('RGB', (150, 150), color=(255, 255, 255))
    draw = ImageDraw.Draw(weather_img)
    fnt_s = ImageFont.truetype(font_path, 17)
    weather_text = f"{res_weather['weather']}, {res_weather['tempRange']}"
    draw.text((10, 10), weather_text, font=fnt_s, fill=(0, 0, 0))
    return weather_img

def dithering(image):
    pal_image = Image.new("P", (1,1))
    # pal_image.putpalette((16,14,27,  169,164,155,  19,30,19,  21,15,50,  122,41,37,  156,127,56,  128,67,54) + (0,0,0)*249)
    pal_image.putpalette((0,0,0,  255,255,255,  0,255,0,  0,0,255,  255,0,0,  255,255,0,  255,128,0) + (0,0,0)*249)

    image_7color = image.convert("RGB").quantize(palette=pal_image)
    # image_7color = image_7color.convert("RGB")

    return image_7color

def create_interesting_default_image(width, height):
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)

    # 添加一些随机的几何图形
    for _ in range(20):
        shape = random.choice(['circle', 'rectangle', 'line'])
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        
        if shape == 'circle':
            x = random.randint(0, width)
            y = random.randint(0, height)
            radius = random.randint(10, 50)
            draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color)
        elif shape == 'rectangle':
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(x1, width)
            y2 = random.randint(y1, height)
            draw.rectangle([x1, y1, x2, y2], fill=color)
        else:  # line
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            x2 = random.randint(0, width)
            y2 = random.randint(0, height)
            draw.line([x1, y1, x2, y2], fill=color, width=random.randint(1, 5))

    return image

def buffImg(image):
    if image.size == (448, 600):
        image = image.transpose(Image.ROTATE_90)
    image_temp = dithering(image)
    buf_7color = bytearray(image_temp.tobytes('raw'))
    # PIL does not support 4 bit color, so pack the 4 bits of color
    # into a single byte to transfer to the panel
    buf = [0x00] * int(image_temp.width * image_temp.height / 2)
    idx = 0
    for i in range(0, len(buf_7color), 2):
        buf[idx] = (buf_7color[i] << 4) + buf_7color[i+1]
        idx += 1
    return bytes(buf)

def get_dominant_color(pil_img):
    img = pil_img.copy()
    img = img.convert("RGBA")
    img = img.resize((5, 5), resample=0)
    dominant_color = img.getpixel((2, 2))
    return dominant_color
# 600 * 0.618 = 370 黄金比例
def image_reshape(img, target_width=448, target_height=370):
    # Calculate the aspect ratio of the original image
    aspect_ratio = img.width / img.height
    
    # Calculate new dimensions to fill the target size while maintaining aspect ratio
    if aspect_ratio > target_width / target_height:  # Image is wider
        new_height = target_height
        new_width = int(target_height * aspect_ratio)
    else:  # Image is taller or equal
        new_width = target_width
        new_height = int(target_width / aspect_ratio)
    
    # Resize the image to fill the target dimensions
    img_resized = img.resize((new_width, new_height), Image.LANCZOS)
    
    # Create a new image with the target size
    result = Image.new('RGB', (target_width, target_height))
    
    # Calculate paste coordinates to center the image
    paste_x = (target_width - new_width) // 2
    paste_y = (target_height - new_height) // 2
    
    # Paste the resized image onto the center of the new image
    result.paste(img_resized, (paste_x, paste_y))
    
    return result