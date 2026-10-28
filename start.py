#!/usr/bin/env python3
"""
Face Recognition Attendance System - Startup Script
Simple script to start the application with proper error handling
"""

import sys
import os

def main():
    print("Starting Face Recognition Attendance System...")
    print("=" * 50)
    
    # Check if required packages are installed
    try:
        import flask
        import cv2
        import numpy
        import PIL
        print("[OK] All required packages are installed")
    except ImportError as e:
        print(f"[ERROR] Missing package: {e}")
        print("Please run: pip install -r requirements.txt")
        return 1
    
    # Check if app.py exists
    if not os.path.exists('app.py'):
        print("[ERROR] app.py not found in current directory")
        return 1
    
    # Check if templates and static directories exist
    if not os.path.exists('templates'):
        print("[ERROR] templates directory not found")
        return 1
    
    if not os.path.exists('static'):
        print("[ERROR] static directory not found")
        return 1
    
    print("[OK] All required files and directories found")
    print("=" * 50)
    
    # Start the application
    try:
        print("Starting Flask server...")
        print("Open your browser and go to: http://127.0.0.1:5000")
        print("Press Ctrl+C to stop the server")
        print("=" * 50)
        
        # Import and run the app
        from app import app
        app.run(debug=True, host='127.0.0.1', port=5000)
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        return 0
    except Exception as e:
        print(f"[ERROR] Failed to start server: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())

