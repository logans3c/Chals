from flask import Flask, request, jsonify, Response, render_template
import requests
import logging
import re
import json
import traceback
import time

app = Flask(__name__)

# Configuration for allowed destination apps
ALLOWED_APPS = {
    'main_app': 'http://localhost:3000',  # Main app on port 3000
}

# Load attack patterns from the JSON file
def load_patterns():
    with open('patterns.json', 'r') as f:
        return json.load(f)

patterns = load_patterns()

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Dictionary to store request timestamps by IP address
request_times = {}

# Rate limit constants
REQUEST_LIMIT = 5  # Max 5 requests per second
BLOCK_TIME = 5  # Block user for 5 seconds if limit is exceeded

# Function to apply rate limiting
def is_rate_limited(ip):
    current_time = time.time()

    # If this IP is in the request_times dictionary
    if ip in request_times:
        # Check if the user is currently blocked
        if request_times[ip].get("blocked_until") and current_time < request_times[ip]["blocked_until"]:
            return True

        # Remove old timestamps (requests older than 1 second)
        request_times[ip]["timestamps"] = [t for t in request_times[ip]["timestamps"] if t > current_time - 1]

        # If more than REQUEST_LIMIT requests in the past second, block the user for BLOCK_TIME seconds
        if len(request_times[ip]["timestamps"]) >= REQUEST_LIMIT:
            request_times[ip]["blocked_until"] = current_time + BLOCK_TIME  # Block for BLOCK_TIME seconds
            return True

        # Otherwise, record the request timestamp
        request_times[ip]["timestamps"].append(current_time)
    else:
        # If IP not in the dictionary, initialize with the current timestamp
        request_times[ip] = {
            "timestamps": [current_time],
            "blocked_until": None  # No block initially
        }

    return False


# Function to check for malicious characters or patterns
def is_request_allowed(req):
    logging.info(f"Checking request for URL: {req.url}")

    # Check if the request exceeds 8KB in size
    total_length = len(req.url) + int(req.content_length or 0)
    if total_length > 8192:  # 8KB = 8192 bytes
        logging.warning(f"Request size exceeds 8KB (total size: {total_length} bytes). Skipping firewall checks.")
        return True, "", 200

    # Check URL query string
    url_str = req.url

    # Check data for POST/PUT requests
    if req.method in ['POST', 'PUT']:
        if req.content_type == 'application/x-www-form-urlencoded':
            # Check each form parameter for malicious patterns
            data_str = "&".join([f"{key}={value}" for key, value in request.form.items()])
        else:
            # Use raw data for other content types
            data_str = req.get_data(as_text=True).lower()
    else:
        data_str = ""

    # Check for malicious patterns in both data and URL
    for attack_type, regex_patterns in patterns.items():
        for pattern in regex_patterns:
            if re.search(pattern, data_str) or re.search(pattern, url_str):
                logging.warning(f"Blocked {attack_type.replace('_', ' ').title()} attempt detected.")
                reason = f"{attack_type.replace('_', ' ').title()} Detected"
                return False, render_template('firewall.html', reason=reason), 403

    return True, "", 200

# Middleware to remove Server header and handle duplicates
@app.after_request
def remove_server_and_handle_duplicates(response: Response) -> Response:
    if 'Server' in response.headers:
        del response.headers['Server']

    # Handle duplicate headers
    unique_headers = {}
    for key, value in response.headers.items():
        key = key.lower()
        if key in unique_headers:
            unique_headers[key] += ', ' + value
        else:
            unique_headers[key] = value

    response.headers = unique_headers
    return response


@app.route('/<app_name>/docs', methods=['GET'])
def docs(app_name):
    return render_template('docs.html', app_name=app_name), 200


@app.route('/', defaults={'endpoint': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(endpoint):
    ip = request.remote_addr  # Get the user's IP address
    logging.info(f"Request received from {ip}: {request.method} {request.url}")

    # Apply WAF checks (rate limiting, malicious patterns)
    allowed, response_or_html, status_code = is_request_allowed(request)
    if not allowed:
        return response_or_html, status_code  # Block and return appropriate response if checks fail

    # Check the total request length
    total_length = len(request.url) + int(request.content_length or 0)
    
    # Apply rate limit only if the total length is less than 8192 bytes
    if total_length <= 8000:
        if is_rate_limited(ip):
            logging.warning(f"Rate limit exceeded for IP {ip}. Blocking for {BLOCK_TIME} seconds.")
            reason = "Too many requests, try again after 5 sec"
            return render_template('firewall.html', reason=reason), 429

    # Forward traffic to the main app on localhost:3000
    query_string = request.query_string.decode('utf-8') if request.query_string else ''
    target_url = f"http://localhost:3000/{endpoint}"

    query_string = request.query_string.decode('utf-8') if request.query_string else ''
    if query_string:
        target_url += f"?{query_string}"

    logging.info(f"Forwarding request to: {target_url}")

    headers={key: value for (key, value) in request.headers if key.lower() != 'host'}
    headers['Connection'] = 'keep-alive'  # Force keep-alive connection


    try:
        if request.method in ['POST', 'PUT']:
            if request.content_type == 'application/json':
                data = request.get_json()
            elif request.content_type == 'application/x-www-form-urlencoded':
                data = request.form
            else:
                data = request.get_data()
        else:
            data = None
        #print the request
        logging.info(f"Method: {request.method}")
        logging.info(f"Request headers: {request.headers}")
        logging.info(f"Request content: {request.get_data()}")
        logging.info(f"Form Data: {request.form}")
        logging.info(f"Args: {request.args}")


        # Forward the request
        response = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=data if request.method in ['POST', 'PUT'] else None,
            cookies=request.cookies,
            allow_redirects=False,
        )



        logging.info(f"Response from main app: {response.status_code}")
        logging.info(f"Response headers: {response.headers}")
        logging.info(f"Response content: {response.content}")
        return Response(response.iter_content(chunk_size=8192), status=response.status_code, headers=dict(response.headers),direct_passthrough=True)
    except requests.RequestException as e:
        logging.error(f"Error forwarding request: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({"error": f"Request error: {str(e)}"}), 500

if __name__ == "__main__":
    logging.info("Starting Flask WAF on port 8000")
    app.run(host='0.0.0.0', port=8000)
