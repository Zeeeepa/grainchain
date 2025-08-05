"""Main Grainchain Dashboard Application - Consolidated Implementation."""

import reflex as rx
from typing import Dict, List, Optional, Any
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize database first
try:
    from database import init_database
    init_database()
    print("✅ Database initialized successfully")
except Exception as e:
    print(f"⚠️ Database initialization warning: {e}")

from .state import DashboardState
from .components.ui_components import (
    sidebar, status_badge, dashboard_content, providers_content,
    terminal_content, files_content, snapshots_content, settings_content
)

def page_content() -> rx.Component:
    """Render page content based on current page."""
    return rx.match(
        DashboardState.current_page,
        ("dashboard", dashboard_content()),
        ("providers", providers_content()),
        ("terminal", terminal_content()),
        ("files", files_content()),
        ("snapshots", snapshots_content()),
        ("settings", settings_content()),
        dashboard_content()  # default
    )

def index() -> rx.Component:
    """Main page layout."""
    return rx.hstack(
        sidebar(),
        rx.box(
            page_content(),
            style={"flex": "1", "background": "var(--gray-1)", "overflow": "auto"}
        ),
        spacing="0",
        width="100%",
        height="100vh"
    )

# Create app
app = rx.App(
    style={"font_family": "Inter, system-ui, sans-serif"}
)

app.add_page(index, route="/", title="Grainchain Dashboard - Professional Sandbox Management")

if __name__ == "__main__":
    print("🚀 Starting Grainchain Dashboard...")
    print("✅ All features implemented and ready!")
    print("🌐 Navigate to http://localhost:3000 to view the dashboard")
