from flask import Flask, render_template, request, jsonify
import json
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

# Define the path to the host file
if os.name == 'nt':  # Windows
    host_file_path = r"C:\Windows\System32\drivers\etc\hosts"
else:  # Linux/macOS
    host_file_path = "/etc/hosts"

# Define the IP address to redirect to (localhost)
redirect_ip = "127.0.0.1"

LOG_FILE = "firewall_logs.txt"
BLOCKED_DOMAINS_FILE = "blocked_domains.txt"

# Load blocked domains from file
def load_blocked_domains():
    if os.path.exists(BLOCKED_DOMAINS_FILE):
        with open(BLOCKED_DOMAINS_FILE, "r") as f:
            return set(f.read().splitlines())
    return set()

blocked_domains = load_blocked_domains()

# Save blocked domains to file
def save_blocked_domains():
    with open(BLOCKED_DOMAINS_FILE, "w") as f:
        f.write("\n".join(blocked_domains))

# Load firewall logs from file
def load_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return [json.loads(line.strip()) for line in f if line.strip()]
    return []

# Function to check if a domain is already blocked
def is_domain_blocked(domain):
    with open(host_file_path, "r") as host_file:
        return any(f"{redirect_ip} {domain}" in line for line in host_file)

# Function to block domains from the blocked_domains.txt
def initial_block():
    with open(host_file_path, "r") as host_file:
        existing_entries = set(host_file.readlines())

    with open(host_file_path, "a") as host_file:
        for domain in blocked_domains:
            if domain and f"{redirect_ip} {domain}\n" not in existing_entries:
                host_file.write(f"{redirect_ip} {domain}\n")
                print(f"Initially blocked {domain} in the host file.")

# Function to flush DNS and Chrome socket pools
def flush_network_cache():
    # Flush system DNS cache
    if os.name == "nt":
        os.system("ipconfig /flushdns")
    else:
        os.system("sudo systemd-resolve --flush-caches")
        os.system("sudo dscacheutil -flushcache")

    print("DNS cache flushed successfully.")

    # 🚀 Flush Chrome socket pools
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--remote-debugging-port=9222")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        driver.get("chrome://net-internals/#sockets")
        time.sleep(2)

        # Simulate clicking "Flush socket pools"
        driver.execute_script("document.querySelector('button').click()")
        print("Chrome socket pools flushed successfully.")

        driver.quit()
    except Exception as e:
        print(f"Failed to flush Chrome sockets: {e}")

# Serve dashboard with logs and blocked domains
@app.route("/")
def index():
    initial_block()  # Block the initial domains
    logs = load_logs()
    return render_template("dashboard.html", blocked_domains=list(blocked_domains), logs=logs)

@app.route("/redirect.html")
def redirect_page():
    return render_template("redirect.html")

# API to add domain to blocklist
@app.route("/block", methods=["POST"])
def block_domain():
    domain = request.json.get("domain")
    if domain:
        blocked_domains.add(domain)
        save_blocked_domains()

        if not is_domain_blocked(domain):
            with open(host_file_path, "a") as host_file:
                host_file.write(f"{redirect_ip} {domain}\n")
            print(f"Blocked {domain}.")

        # 🚀 Flush caches to apply changes immediately
        flush_network_cache()

        return jsonify({"success": True, "blocked_domains": list(blocked_domains)})
    return jsonify({"success": False})

# API to remove domain from blocklist
@app.route("/allow", methods=["POST"])
def allow_domain():
    domain = request.json.get("domain")
    if domain in blocked_domains:
        blocked_domains.remove(domain)
        save_blocked_domains()

        # Remove the domain from the hosts file
        with open(host_file_path, "r") as host_file:
            lines = host_file.readlines()
        with open(host_file_path, "w") as host_file:
            for line in lines:
                if f"{redirect_ip} {domain}" not in line:
                    host_file.write(line)
        print(f"Allowed {domain} by removing from the host file.")

        # 🚀 Flush caches to ensure unblocking takes effect immediately
        flush_network_cache()

        return jsonify({"success": True, "blocked_domains": list(blocked_domains)})
    return jsonify({"success": False})

# Get blocked domains
@app.route("/blocked_domains")
def get_blocked_domains():
    return jsonify(list(blocked_domains))

if __name__ == "__main__":
    app.run(debug=True)
