"""Main entry point for Grainchain Dashboard."""

# Import everything from app.py
from app import *

# This makes the app discoverable by Reflex
if __name__ == "__main__":
    app.compile()
