# Use the official Node.js 18 image
FROM node:18

RUN apt update
# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy package files to the container
COPY package*.json ./

# Install Node.js dependencies
RUN npm install

COPY . .
RUN rm -f Dockerfile init.sh

# Copy init.sh to the root directory
COPY init.sh /init.sh
RUN chmod +x /init.sh

# Expose the application and MySQL ports
EXPOSE 3000

# Ensure proper permissions (example, adjust as needed)
RUN chown -R node:node /usr/src/app

# Start both MySQL and Node.js app using the init.sh script

ENTRYPOINT ["/init.sh"]