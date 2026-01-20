# Multi-stage Dockerfile for Rose-Bot
# Runs both Node.js (WhatsApp bridge) and Python (Bot logic)

FROM node:18-slim

# Install Python 3 and minimal dependencies for Puppeteer
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    chromium \
    fonts-liberation \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdrm2 \
    libgbm1 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    supervisor \
    dumb-init \
    curl \
    git \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set Puppeteer to use system Chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
# Disable Chromium sandbox since we're running as root in container
ENV CHROME_PATH=/usr/bin/chromium
ENV CHROMIUM_FLAGS="--no-sandbox --disable-dev-shm-usage"

# Create app directory
WORKDIR /app

# Copy package files and install Node.js dependencies
COPY package.json package-lock.json* ./
RUN npm install --omit=dev || npm install

# Copy Python requirements and install (production - no torch)
COPY requirements-prod.txt ./
RUN pip3 install --no-cache-dir --break-system-packages -r requirements-prod.txt

# Copy the rest of the application
COPY . .

# Copy supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create data directories for persistence
RUN mkdir -p /app/data/.wwebjs_auth /app/data/.wwebjs_cache

# Expose ports
EXPOSE 3000 5000

# Use supervisor to run both Node.js and Python
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
