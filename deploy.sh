#!/bin/bash
# Quick deployment script for Ubuntu server

echo "🚀 dHash App Deployment Script"
echo "================================"

# Check if running on Ubuntu
if [ ! -f /etc/lsb-release ]; then
    echo "⚠️  This script is designed for Ubuntu. Proceed with caution."
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install dependencies
echo "📦 Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv nginx supervisor
sudo apt install -y libopencv-dev python3-opencv

# Create app directory
echo "📁 Setting up application directory..."
sudo mkdir -p /var/www/dhash
sudo chown $USER:$USER /var/www/dhash

# Create Python virtual environment
echo "🐍 Creating Python virtual environment..."
cd /var/www/dhash
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating required directories..."
mkdir -p static/temp
chmod 755 static/temp

# Set up Gunicorn systemd service
echo "⚙️  Creating systemd service..."
sudo tee /etc/systemd/system/dhash.service > /dev/null <<EOF
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
EOF

# Set permissions
echo "🔒 Setting permissions..."
sudo chown -R www-data:www-data /var/www/dhash
sudo chmod -R 755 /var/www/dhash

# Start service
echo "🚀 Starting dHash service..."
sudo systemctl daemon-reload
sudo systemctl start dhash
sudo systemctl enable dhash

# Configure Nginx
echo "⚙️  Configuring Nginx..."
sudo tee /etc/nginx/sites-available/dhash > /dev/null <<EOF
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
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/dhash /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

# Configure firewall
echo "🔥 Configuring firewall..."
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
echo "y" | sudo ufw enable

# Check status
echo ""
echo "✅ Deployment complete!"
echo ""
echo "Service status:"
sudo systemctl status dhash --no-pager
echo ""
echo "Access your app at: http://$(hostname -I | awk '{print $1}')"
echo ""
echo "Useful commands:"
echo "  - Check status: sudo systemctl status dhash"
echo "  - View logs: sudo journalctl -u dhash -f"
echo "  - Restart: sudo systemctl restart dhash"
