"""
Simple script to run the dashboard API server
"""
import sys
import os

# Add parent directory to path so we can import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if __name__ == "__main__":
    import uvicorn
    from dashboard_api.server import app
    
    print("Starting Dashboard API on http://localhost:8000")
    print("Press Ctrl+C to stop")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

