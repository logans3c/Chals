FROM python:3.9-slim

# Create non-root user
RUN useradd -m appuser

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir flask PyJWT

# Copy application files
COPY . /app/

# Set ownership
RUN chown -R appuser:appuser /app

# Make the init script executable
RUN chmod +x /app/init.sh

# Create necessary directories
RUN chown -R appuser:appuser /app/*

# Expose the app port
EXPOSE 5000

# Switch to non-root user
USER appuser

# Run the initialization script
CMD ["/app/init.sh"]
