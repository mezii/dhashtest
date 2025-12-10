#!/usr/bin/env python3
"""
Desktop launcher for dHash Face Recognition App
Opens the Flask app in a native window using webview
"""

import webview
import threading
import time
from app import app
import os

def start_flask():
    """Start Flask server in background thread"""
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

def main():
    """Launch the desktop app"""
    # Create required directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/temp', exist_ok=True)
    
    # Start Flask in background
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    
    # Wait for Flask to start
    time.sleep(2)
    
    # Create desktop window
    webview.create_window(
        'dHash Face Recognition',
        'http://127.0.0.1:5000',
        width=1200,
        height=800,
        resizable=True,
        fullscreen=False
    )
    
    # Start the window
    webview.start()

if __name__ == '__main__':
    main()
