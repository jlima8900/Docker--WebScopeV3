# Use a lightweight Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install essential debugging tools (with nano retained)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl-dev openssl chromium-driver \
    net-tools iproute2 curl wget jq git \
    procps htop nano \
    && rm -rf /var/lib/apt/lists/*

# Install Selenium and Chromedriver dependencies
RUN pip install --no-cache-dir selenium webdriver-manager undetected-chromedriver

# Generate a self-signed SSL certificate
RUN mkdir -p /app/ssl && \
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /app/ssl/server.key -out /app/ssl/server.crt \
    -subj "/C=US/ST=Denial/L=Springfield/O=Dis/CN=localhost"

# Copy application dependencies
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure undetected-chromedriver is installed
RUN pip install --no-cache-dir undetected-chromedriver

# Copy application files
COPY . /app/

# Expose the correct port
EXPOSE 9017

# Run VaultScope securely with Gunicorn
CMD ["gunicorn", "--certfile=/app/ssl/server.crt", "--keyfile=/app/ssl/server.key", "--bind", "0.0.0.0:9017", "app:app"]
