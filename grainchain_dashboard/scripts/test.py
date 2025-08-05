#!/usr/bin/env python3
"""Test runner script for Grainchain Dashboard."""

import os
import sys
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """Run the test suite."""
    print("🧪 Running Grainchain Dashboard test suite...")
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Set test environment
    os.environ["ENVIRONMENT"] = "testing"
    
    try:
        # Run pytest with coverage
        subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/",
            "--cov=src/",
            "--cov-report=html",
            "--cov-report=term-missing",
            "-v"
        ], check=True)
        
        print("✅ All tests passed!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed with exit code: {e.returncode}")
        sys.exit(1)

if __name__ == "__main__":
    main()
