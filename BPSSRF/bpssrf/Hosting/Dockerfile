FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x init.sh

EXPOSE 80

# Use init.sh as the entry point
CMD ["/app/init.sh"]