FROM python:3.10-slim


# Install Node.js and other dependencies
RUN apt-get update && \
    apt-get install -y curl gnupg ca-certificates \
    fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \
    libatk1.0-0 libcups2 libdbus-1-3 libgdk-pixbuf2.0-0 libnspr4 \
    libnss3 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 \
    xdg-utils libu2f-udev libvulkan1 libgbm1 wget && \
    apt-get install -y nodejs npm chromium && \

    rm -rf /var/lib/apt/lists/*



# Set working directory
WORKDIR /app

# Copy Bottle app
COPY Bottle /app/bottle-note-app

# Copy Bot app
COPY Bottle/Bot /app/bot

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/bottle-note-app/requirements.txt

# Install Node.js dependencies for the bot
RUN cd /app/bot/bot && npm install

# Copy init script
COPY init.sh /app/init.sh
RUN chmod +x /app/init.sh

RUN apt-get install -y chromium

# Set /etc/hosts so 127.0.0.1 resolves to localhost (for gethostbyaddr)
# RUN echo "127.0.0.1 localhost" > /etc/hosts

EXPOSE 8081 3000

ENTRYPOINT ["/app/init.sh"]
