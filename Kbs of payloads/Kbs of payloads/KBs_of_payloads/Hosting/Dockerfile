FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary packages for Python and Node.js
RUN apt update && apt install -y python3-pip nginx python3-dev build-essential pkg-config sudo nodejs npm


# Set timezone to UTC
RUN ln -fs /usr/share/zoneinfo/UTC /etc/localtime
RUN dpkg-reconfigure -f noninteractive tzdata

# Install Python dependencies
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt --break-system-packages

# Install nodemon globally
RUN npm install -g nodemon

# Create a low privileged user to run the applications
RUN useradd -m -s /bin/bash app

# Set the application preview for Node.js
COPY ./preview /home/app/preview
RUN chown -R app:app /home/app/preview

# Set the application challenge for Python
COPY --chown=app:app ./waf /home/app/waf

# Switch to app user and install npm dependencies
USER app
WORKDIR /home/app/preview
RUN npm install

# Switch back to root for remaining operations
USER root

# Nginx configuration
COPY conf/nginx.conf /etc/nginx/nginx.conf


# Copy and set permissions for initialization script
COPY init.sh /init.sh
RUN chmod 700 /init.sh

# Set the default command to run the initialization script
RUN apt install sqlite3
CMD ["/init.sh"]
