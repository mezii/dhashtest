# Running dHash App on Ubuntu Server

## 📦 **Method 1: Upload via Git (Recommended)**

### On your local Mac:
```bash
# Your code is already pushed to GitHub
# Repository: mezii/mtouch
```

### On your Ubuntu server:
```bash
# SSH into your server
ssh username@your-server-ip

# Clone the repository
cd /var/www
sudo git clone https://github.com/mezii/mtouch.git dhash
cd dhash

# Run the deployment script
chmod +x deploy.sh
sudo ./deploy.sh
```

The script will automatically:
- ✅ Install Python, nginx, dependencies
- ✅ Create virtual environment
- ✅ Install Python packages
- ✅ Configure systemd service
- ✅ Set up Nginx
- ✅ Start the app

---

## 📤 **Method 2: Upload via SCP (Direct Upload)**

### From your Mac:
```bash
# Upload entire directory to server
cd /Users/mins/Documents/MKApp
scp -r dhash username@your-server-ip:/home/username/

# SSH into server
ssh username@your-server-ip

# Move to proper location
sudo mv ~/dhash /var/www/
cd /var/www/dhash

# Run deployment script
chmod +x deploy.sh
sudo ./deploy.sh
```

---

## 🚀 **Method 3: Manual Setup (Step by Step)**

### SSH into your server:
```bash
ssh username@your-server-ip
```

### 1. Install system packages:
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nginx
sudo apt install -y libopencv-dev python3-opencv
```

### 2. Upload your files (or git clone):
```bash
cd /var/www
sudo mkdir dhash
sudo chown $USER:$USER dhash
# Upload files here or git clone
```

### 3. Create Python virtual environment:
```bash
cd /var/www/dhash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Test the app manually:
```bash
python app.py
# Should see: Running on http://127.0.0.1:5000
# Press Ctrl+C to stop
```

### 5. Create systemd service:
```bash
sudo nano /etc/systemd/system/dhash.service
```

Paste this:
```ini
[Unit]
Description=dHash Face Recognition App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/dhash
Environment="PATH=/var/www/dhash/venv/bin"
ExecStart=/var/www/dhash/venv/bin/gunicorn --workers 3 --bind unix:dhash.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```

Save and exit (Ctrl+X, Y, Enter)

### 6. Set permissions and start service:
```bash
sudo chown -R www-data:www-data /var/www/dhash
sudo chmod -R 755 /var/www/dhash

sudo systemctl daemon-reload
sudo systemctl start dhash
sudo systemctl enable dhash
sudo systemctl status dhash
```

### 7. Configure Nginx:
```bash
sudo nano /etc/nginx/sites-available/dhash
```

Paste this:
```nginx
server {
    listen 80;
    server_name _;

    client_max_body_size 16M;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/dhash/dhash.sock;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }

    location /static {
        alias /var/www/dhash/static;
        expires 30d;
    }
}
```

Save and exit

### 8. Enable site and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/dhash /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 9. Configure firewall:
```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

---

## ✅ **Check if it's running:**

```bash
# Check service status
sudo systemctl status dhash

# Check if port 80 is listening
sudo netstat -tlnp | grep :80

# Check Nginx status
sudo systemctl status nginx

# View logs
sudo journalctl -u dhash -f
```

---

## 🌐 **Access Your App:**

Open browser:
```
http://your-server-ip
```

You should see the dHash comparison interface!

---

## 🔄 **Useful Commands:**

```bash
# Restart app after code changes
sudo systemctl restart dhash

# View app logs
sudo journalctl -u dhash -n 50

# View Nginx logs
sudo tail -f /var/log/nginx/error.log

# Update code (if using git)
cd /var/www/dhash
sudo git pull
sudo systemctl restart dhash
```

---

## 🐛 **Troubleshooting:**

### App won't start:
```bash
# Check logs
sudo journalctl -u dhash -xe

# Test manually
cd /var/www/dhash
source venv/bin/activate
python app.py
```

### 502 Bad Gateway:
```bash
# Check if service is running
sudo systemctl status dhash

# Check socket file
ls -la /var/www/dhash/dhash.sock

# Restart both
sudo systemctl restart dhash
sudo systemctl restart nginx
```

### Permission errors:
```bash
sudo chown -R www-data:www-data /var/www/dhash
sudo chmod -R 755 /var/www/dhash
mkdir -p /var/www/dhash/static/temp
sudo chown -R www-data:www-data /var/www/dhash/static/temp
```
