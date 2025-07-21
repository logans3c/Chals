FROM python:3.9

# Install Node.js for the bot
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    libnss3 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxkbcommon0 \
    libasound2 \
    curl

# Set working directory
WORKDIR /app

# Copy the main application files
COPY . .

# Install Python dependencies
RUN pip install flask requests

# Set up the bot application
WORKDIR /app/ctfbot
RUN npm install
WORKDIR /app

# Make init.sh executable
RUN chmod +x init.sh

# Expose both application ports
EXPOSE 5000 3000

# Set environment variables 
ENV DOMAIN=127.0.0.1:5000
ENV ADMIN_PASSWORD=admin_secure_password123

# Run the initialization script
CMD ["/app/init.sh"]
