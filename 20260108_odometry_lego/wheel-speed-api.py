#!/usr/bin/env python3
"""
CAN Bus Wheel Speed API Server
Provides REST API endpoints to access wheel speed data from CAN bus
"""

from flask import Flask, jsonify
import json
import os
from datetime import datetime
import threading
import time

app = Flask(__name__)

# Global variables for wheel speed data
wheel_speed_data = {
    "left_rear": 0.0,
    "right_rear": 0.0,
    "timestamp": None,
    "rtd_active": False,
    "cumulative_distance": 0.0
}
data_lock = threading.Lock()

def load_cumulative_distance():
    """Load cumulative distance from log file"""
    try:
        log_file = "/home/pi/Desktop/RPI_Desktop/LOGS/trip_distance_cumulative.csv"
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    if "Cumulative Distance (km)" in line and "Cumulative Distance (m)" not in line:
                        parts = line.strip().split(',')
                        if len(parts) >= 2:
                            try:
                                distance = float(parts[1].strip())
                                return distance
                            except ValueError:
                                pass
    except Exception as e:
        print(f"Error loading cumulative distance: {e}")
    return 0.0

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "service": "CAN Bus Wheel Speed API",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/wheel-speed', methods=['GET'])
def get_wheel_speed():
    """Get current wheel speed data"""
    with data_lock:
        return jsonify({
            "left_rear_speed_kmh": wheel_speed_data["left_rear"],
            "right_rear_speed_kmh": wheel_speed_data["right_rear"],
            "average_speed_kmh": (wheel_speed_data["left_rear"] + wheel_speed_data["right_rear"]) / 2,
            "timestamp": wheel_speed_data["timestamp"],
            "rtd_active": wheel_speed_data["rtd_active"]
        })

@app.route('/api/odometry', methods=['GET'])
def get_odometry():
    """Get odometry/cumulative distance data"""
    cumulative = load_cumulative_distance()
    
    return jsonify({
        "cumulative_distance_km": cumulative,
        "cumulative_distance_m": cumulative * 1000,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get overall system status"""
    with data_lock:
        cumulative = load_cumulative_distance()
        
        return jsonify({
            "system_status": "running",
            "rtd_active": wheel_speed_data["rtd_active"],
            "left_rear_speed_kmh": wheel_speed_data["left_rear"],
            "right_rear_speed_kmh": wheel_speed_data["right_rear"],
            "cumulative_distance_km": cumulative,
            "logs_directory": "/home/pi/Desktop/RPI_Desktop/LOGS",
            "timestamp": datetime.now().isoformat()
        })

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get system configuration"""
    return jsonify({
        "can_bus": {
            "can0": "enabled",
            "can1": "enabled",
            "bitrate": 1000000
        },
        "wheel_speed_ids": {
            "left_rear": "0x193",
            "right_rear": "0x194"
        },
        "vcu_status_id": "0x281",
        "logs_location": "/home/pi/Desktop/RPI_Desktop/LOGS"
    })

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": [
            "/api/health",
            "/api/wheel-speed",
            "/api/odometry",
            "/api/status",
            "/api/config"
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return jsonify({
        "error": "Internal server error",
        "message": str(error)
    }), 500

if __name__ == '__main__':
    print("Starting CAN Bus Wheel Speed API Server...")
    print("Available endpoints:")
    print("  GET /api/health        - Health check")
    print("  GET /api/wheel-speed   - Current wheel speed")
    print("  GET /api/odometry      - Cumulative distance")
    print("  GET /api/status        - System status")
    print("  GET /api/config        - Configuration")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False,
        threaded=True
    )
