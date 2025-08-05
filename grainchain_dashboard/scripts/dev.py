#!/usr/bin/env python3
"""Development server script for Grainchain Dashboard."""

import os
import sys
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """Start the development server."""
    print("🚀 Starting Grainchain Dashboard in development mode...")
    
    # Change to src directory
    src_dir = Path(__file__).parent.parent / "src"
    os.chdir(src_dir)
    
    # Set environment
    os.environ["ENVIRONMENT"] = "development"
    
    try:
        # Start reflex in development mode
        subprocess.run([
            sys.executable, "-m", "reflex", "run", 
            "--dev", 
            "--frontend-port", "3000",
            "--backend-port", "8000"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Development server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting development server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
