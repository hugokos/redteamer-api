# Dockerfile

FROM python:3.10-slim

# 0. Disable nest_asyncio patching globally
ENV DISABLE_NEST_ASYNCIO=true

# 1. Install OS deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Copy & install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy your code
COPY . /app

# 4. Expose port and force asyncio loop
EXPOSE 8080
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8080","--loop","asyncio"]
