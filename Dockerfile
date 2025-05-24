# Dockerfile

# 0. Base image
FROM python:3.10-slim

# 1. Disable nest_asyncio patching globally
ENV DISABLE_NEST_ASYNCIO=true

# 2. Install OS deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential git \
 && rm -rf /var/lib/apt/lists/*

# 3. Set working dir
WORKDIR /app

# 4. Copy & install Python deps
COPY requirements.txt .
# optionally upgrade pip & install
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 5. Copy your code
COPY . /app

# 6. Expose port & launch with asyncio loop
EXPOSE 8080
CMD ["sh","-c","uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --loop asyncio"]
