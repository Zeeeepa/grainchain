#!/usr/bin/env python3
"""Simple startup script for Grainchain Dashboard."""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Set environment variables if not already set
if not os.getenv("PYTHONPATH"):
    os.environ["PYTHONPATH"] = str(current_dir)

try:
    from main import app
    
    print("🚀 Starting Grainchain Dashboard...")
    print(f"📍 Dashboard will be available at: http://localhost:3000")
    print("🔧 Configure providers in the Settings page")
    print("📖 Check README.md for setup instructions")
    print()
    
    app.run()
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure you've installed the requirements:")
    print("   pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error starting dashboard: {e}")
    sys.exit(1)

if __name__ == "__main__":
    pass

