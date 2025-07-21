FROM node:22
# Install system utilities and pm2
RUN apt-get update && \
    apt-get install -y ffmpeg curl vim nano && \
    npm install -g pm2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install app dependencies
RUN npm install

# Copy app source code
COPY . .

# Create directories for uploads and processed videos
RUN mkdir -p /app/uploads /app/processed

# Copy the init script and make it executable
COPY init.sh /root/init.sh
RUN chmod +x /root/init.sh

# Expose the port the app runs on
EXPOSE 3000

# Run as root (default in node:16)
USER root

ENTRYPOINT ["/root/init.sh"]
