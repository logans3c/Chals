FROM node:22
WORKDIR /app

# Install Python and dependencies for Flask app
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    chromium \
    chromium-driver \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    wget \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for Puppeteer
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# Create directory structure
RUN mkdir -p /app/Bot/bot/extensions
RUN mkdir -p /app/Bot/bot/views

# Copy package.json for bot and install dependencies
COPY Bot/bot/package*.json /app/Bot/bot/
RUN cd /app/Bot/bot && npm install

# Copy Flask app requirements and install
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir  -r /app/requirements.txt --break-system-packages

# Copy the entire application
COPY . /app/

# Make sure the init script is executable
RUN chmod +x /app/init.sh

# Set environment variables
ENV APPNAME="Admin Bot"
ENV APPURL="http://localhost:5000"
ENV ADMIN_PASSWORD="adminwwwwwwwwwwwwwwws"
# Expose required ports
EXPOSE 5000
EXPOSE 3000

# Use the init script as the entrypoint
ENTRYPOINT ["/app/init.sh"]

