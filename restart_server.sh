#!/bin/bash
# Quick restart script for server

echo "🔄 Restarting dHash app..."

# Kill existing process
pkill -f "python app.py" || true
sleep 1

# Start the app
cd /var/www/dhash
source venv/bin/activate
nohup python app.py > /var/log/dhash.log 2>&1 &

echo "✅ App restarted!"
echo "📝 View logs: tail -f /var/log/dhash.log"
echo "🌐 Access at: http://$(hostname -I | awk '{print $1}'):5000"
