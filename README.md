# Firewall Web App

This is a Flask-based firewall application that blocks and redirects access to specified domains by modifying the system's `hosts` file.

## Features
- Block specific domains by adding them to `hosts`
- Redirect blocked domains to `redirect.html`
- Allow blocked domains by removing them from `hosts`
- Logs all blocked attempts
- Provides a simple web dashboard

## Prerequisites
- Python 3.x
- Flask
- Selenium (for automated tasks)

## Setup Instructions
### 1. Clone the Repository
```sh
git clone https://github.com/your-repo/firewall.git
cd firewall
```

### 2. Create and Activate Virtual Environment
```sh
python -m venv venv
```
#### Windows:
```sh
venv\Scripts\activate
```
#### Linux/Mac:
```sh
source venv/bin/activate
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Run the Application (As Administrator)
**Important:** Since this app modifies the `hosts` file, it **must be run as Administrator**.

#### Windows:
1. Open **Command Prompt (CMD) as Administrator**
2. Navigate to the project directory:
   ```sh
   cd C:\Users\YourUsername\path\to\firewall
   ```
3. Activate the virtual environment:
   ```sh
   venv\Scripts\activate
   ```
4. Run the script:
   ```sh
   python firewall.py
   ```

#### Linux/Mac:
Run the script with `sudo`:
```sh
sudo python firewall.py
```

### 5. Access the Dashboard
Once the script is running, open:
```
http://127.0.0.1:5000/
```

## Manual Socket Flush (If Needed)
When blocking a website, changes may not apply instantly due to Chrome's DNS caching. If websites are still accessible, try manually flushing socket pools:

### **Chrome Socket Flush Method:**
1. Open Chrome and go to:
   ```
   chrome://net-internals/#sockets
   ```
2. Click **Flush socket pools**.

Alternatively, you can flush the system’s DNS cache:

#### Windows:
```sh
ipconfig /flushdns
```
#### Linux/Mac:
```sh
sudo systemd-resolve --flush-caches
```

## License
This project is open-source and free to use
.

