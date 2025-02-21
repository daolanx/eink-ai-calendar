# Use official Python runtime as parent image
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy current directory contents into /app in container
COPY . /app

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 (assuming server runs on this port)
EXPOSE 8000

# Run application
CMD ["python", "app.py"]