# Deploying dHash App to Ubuntu Server

## Prerequisites
- Ubuntu server (18.04, 20.04, 22.04, or newer)
- SSH access to the server
- sudo privileges

## Deployment Steps

### 1. Prepare Your Server

SSH into your Ubuntu server:
```bash
ssh username@your-server-ip
```

Update system packages:
```bash
sudo apt update
sudo apt upgrade -y
```

Install Python 3, pip, and required system packages:
```bash
sudo apt install -y python3 python3-pip python3-venv nginx supervisor
sudo apt install -y libopencv-dev python3-opencv  # For opencv-python
```

### 2. Upload Your Application

**Option A: Using Git (Recommended)**
```bash
# On your server
cd /var/www
sudo mkdir -p dhash
sudo chown $USER:$USER dhash
cd dhash
git clone your-repository-url .
```

**Option B: Using SCP (from your Mac)**
```bash
# From your local machine
cd /Users/mins/Documents/MKApp
scp -r dhash username@your-server-ip:/home/username/
# Then on server, move it
ssh username@your-server-ip
sudo mv ~/dhash /var/www/
sudo chown -R $USER:$USER /var/www/dhash
```

**Option C: Using rsync (from your Mac)**
```bash
# From your local machine
cd /Users/mins/Documents/MKApp
rsync -avz --exclude='.venv' --exclude='__pycache__' --exclude='*.pyc' \
  dhash/ username@your-server-ip:/home/username/dhash/
```

### 3. Set Up Python Environment on Server

```bash
cd /var/www/dhash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create Production Configuration

Create a production-ready app config:
```bash
nano wsgi.py
```

Add this content:
```python
from app import app

if __name__ == "__main__":
    app.run()
```

### 5. Set Up Gunicorn (Production WSGI Server)

Install Gunicorn:
```bash
pip install gunicorn
```

Test that it works:
```bash
gunicorn --bind 0.0.0.0:8000 wsgi:app
```

Press Ctrl+C to stop after testing.

### 6. Create Systemd Service (Auto-start on boot)

Create service file:
```bash
sudo nano /etc/systemd/system/dhash.service
```

Add this content:
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

Set permissions:
```bash
sudo chown -R www-data:www-data /var/www/dhash
sudo chmod -R 755 /var/www/dhash
```

Start and enable the service:
```bash
sudo systemctl start dhash
sudo systemctl enable dhash
sudo systemctl status dhash
```

### 7. Configure Nginx as Reverse Proxy

Create Nginx configuration:
```bash
sudo nano /etc/nginx/sites-available/dhash
```

Add this content:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Or use server IP

    client_max_body_size 16M;  # Allow larger image uploads

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

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/dhash /etc/nginx/sites-enabled
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

### 8. Configure Firewall

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

### 9. Access Your App

Open browser and navigate to:
```
http://your-server-ip
# or
http://your-domain.com
```

## Optional: Enable HTTPS with Let's Encrypt

Install Certbot:
```bash
sudo apt install -y certbot python3-certbot-nginx
```

Get SSL certificate:
```bash
sudo certbot --nginx -d your-domain.com
```

Follow the prompts. Auto-renewal is configured automatically.

## Useful Commands

### Check app status:
```bash
sudo systemctl status dhash
```

### View logs:
```bash
sudo journalctl -u dhash -f  # Follow logs
sudo tail -f /var/log/nginx/error.log  # Nginx errors
```

### Restart services:
```bash
sudo systemctl restart dhash
sudo systemctl restart nginx
```

### Update application:
```bash
cd /var/www/dhash
source venv/bin/activate
git pull  # If using git
pip install -r requirements.txt
sudo systemctl restart dhash
```

## Troubleshooting

### If app won't start:
1. Check logs: `sudo journalctl -u dhash -n 50`
2. Check permissions: `ls -la /var/www/dhash`
3. Test manually: `cd /var/www/dhash && source venv/bin/activate && python app.py`

### If images won't upload:
1. Check Nginx client_max_body_size setting
2. Check folder permissions for static/temp directory
3. Ensure temp directory exists: `mkdir -p /var/www/dhash/static/temp`

### If getting 502 Bad Gateway:
1. Check if dhash service is running: `sudo systemctl status dhash`
2. Check socket file exists: `ls -la /var/www/dhash/dhash.sock`
3. Restart both services: `sudo systemctl restart dhash nginx`
