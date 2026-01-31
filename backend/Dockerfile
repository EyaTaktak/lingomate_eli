# 1️ Base image
FROM python:3.11-slim

# 2️ Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3️ Set working directory
WORKDIR /app

# 4️ Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# 5️ Copy requirements
COPY requirements.txt .

# 6️ Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 7️ Copy the app code
COPY . .

# 8️ Expose port for FastAPI
EXPOSE 8000

# 9️ Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
