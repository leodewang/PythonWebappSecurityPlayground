# 1) Pick a base image with OS + Python
FROM python:3.11-slim

# 2) Configure Python behavior for containers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3) Set the working directory inside the container
WORKDIR /app

# 4) Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5) Copy the application code into the image
COPY . .

# 6) Default port the app will listen on
ENV PORT=5000

# 7) Command to start the app when the container runs
CMD ["python", "app.py"]
