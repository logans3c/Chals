from flask import Flask, request, jsonify
import re
import ipaddress
import socket
import time
from flask import render_template

import hashlib
import requests
app = Flask(__name__)

def read_flag():
    try:
        with open('/app/flag.txt', 'r') as f:
            return f.read().strip()
    except:
        return "flag{stigmata_stigmata_stigmata}"

flag = read_flag()

@app.route('/')
def index():
    return render_template('index.html')

def sha256_hash(text):
    text_bytes = text.encode('utf-8')
    sha256 = hashlib.sha256()
    sha256.update(text_bytes)
    hash_hex = sha256.hexdigest()
    return hash_hex

isSafe = False
def check_ssrf(url,checked):
    global isSafe
    if "@" in url or "#" in url:
        isSafe = False
        return "Fail"
    if checked > 3:
        print("URLs that are redirected more than 3 times are prohibited.")
        isSafe = False
        return "Fail"
    protocol = re.match(r'^[^:]+', url)
    if protocol is None:
        isSafe = False
        print("Protocol was not detected.")
        return "Fail"
    print("Protocol :",protocol.group())
    if protocol.group() == "http" or protocol.group() == "https":
        host = re.search(r'(?<=//)[^/]+', url)
        print(host.group())
        if host is None:
            isSafe = False
            print("Host was not detected.")
            return "Fail"
        host = host.group()
        print("Host :",host)
        try:
            ip_address = socket.gethostbyname(host)
            print("Host IP Address:", ip_address)
        except:
            print("Host is not valid.")
            isSafe = False
            return "Fail"
        for _ in range(2): # Loop to prevent DNS Rebinding attacks
            print("Verifying IP..", _)
            ip_address = socket.gethostbyname(host) # Get IP from the host
            if ipaddress.ip_address(ip_address).is_private: # If any one of the IPs is an internal IP
                print("Internal network IP was detected.")
                isSafe = False
                return "Fail"
            time.sleep(1) # 1 second wait
        print("Checking redirection: ",url)
        try:
            response = requests.get(url,allow_redirects=False) # Send request. It's safe because we've verified the URL.
            if 300 <= response.status_code and response.status_code <= 309:
                redirect_url = response.headers['location']  # Get the URL being redirected to
                print("Redirection was detected.",redirect_url)
                if len(redirect_url) >= 120:
                    isSafe = False
                    return "fail"
                check_ssrf(redirect_url,checked + 1) # Count the number of redirections and check if it's safe at the same time
        except:
            print("URL request failed.")
            isSafe = False
            return "Fail"
        if isSafe == True:
            print("URL registration successful.")
            return "SUCCESS"
        else:
            return "Fail"

    else:
        print("Check if URL starts with HTTP / HTTPS.")
        isSafe = False
        return "Fail"

@app.route('/check-url', methods=['POST'])
def check_url():
    global isSafe
    data = request.get_json()
    if 'url' not in data:
        return jsonify({'error': 'No URL provided'}), 400

    url = data['url']
    host = re.search(r'(?<=//)[^/]+', url)
    print(host.group())
    if host is None:
        print("Host was not detected.")
        return "Fail"
    host = host.group()
    if host != "www.google.com":
        isSafe = False
        return "Host must be www.google.com."
    isSafe = True
    result = check_ssrf(url,1)
    if result != "SUCCESS" or isSafe != True:
        return "This URL can cause SSRF."
    try:
        response = requests.get(url)
        status_code = response.status_code
        return jsonify({'url': url, 'status_code': status_code})
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Request Failed.'}), 500
    
@app.route('/admin',methods=['GET'])
def admin():
    global flag
    user_ip = request.remote_addr
    if user_ip != "127.0.0.1":
        return "only localhost."
    if request.args.get('nickname'):
        nickname = request.args.get('nickname')
        flag = sha256_hash(nickname)
        return "success."

@app.route("/flag",methods=['POST'])
def clear():
    global flag
    if flag == sha256_hash(request.args.get('nickname')):
        return read_flag()
    else:
        return "you can't bypass SSRF-FILTER. Try again."

if __name__ == '__main__':
    print("Hash : ",sha256_hash("Show your creative attack ideas!"))
    app.run(debug=False,host='0.0.0.0',port=80)