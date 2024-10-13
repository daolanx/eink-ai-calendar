# 使用官方 Python 运行时作为父镜像
FROM python:3.8-slim

# 设置工作目录
WORKDIR /app

# 将当前目录内容复制到容器的 /app 中
COPY . /app

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口 8000（假设您的服务器运行在此端口上）
EXPOSE 8000

# 运行应用
CMD ["python", "app.py"]