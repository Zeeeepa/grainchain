#!/usr/bin/env python3
"""
Simple Grainchain Dashboard

A working dashboard for Grainchain sandboxes.
"""

import os
import sys
from typing import Dict, List, Optional, Any

import reflex as rx

# Add parent directory to path for grainchain imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Import Grainchain core
from grainchain import Sandbox, get_available_providers, Providers

class DashboardState(rx.State):
    """Simple Grainchain Dashboard State."""
    
    # Navigation state
    current_page: str = "dashboard"
    
    # Provider management
    available_providers: List[str] = []
    
    # UI state
    is_loading: bool = False
    error_message: str = ""
    success_message: str = ""
    
    # Statistics
    sandbox_count: int = 0
    total_commands_executed: int = 0

    def initialize_grainchain(self):
        """Initialize Grainchain and get available providers."""
        try:
            self.is_loading = True
            self.error_message = ""
            
            # Get available providers
            providers = get_available_providers()
            self.available_providers = list(providers)
            
            self.success_message = f"Found {len(providers)} available providers: {', '.join(providers)}"
            
        except Exception as e:
            self.error_message = f"Failed to initialize: {str(e)}"
        finally:
            self.is_loading = False

    def set_page(self, page: str):
        """Set the current page."""
        self.current_page = page

    def clear_messages(self):
        """Clear success and error messages."""
        self.success_message = ""
        self.error_message = ""

def navbar():
    """Navigation bar component."""
    return rx.hstack(
        rx.heading("🌾 Grainchain Dashboard", size="6"),
        rx.spacer(),
        rx.hstack(
            rx.button(
                "Dashboard",
                on_click=DashboardState.set_page("dashboard"),
                variant="ghost" if DashboardState.current_page != "dashboard" else "solid",
            ),
            rx.button(
                "Providers",
                on_click=DashboardState.set_page("providers"),
                variant="ghost" if DashboardState.current_page != "providers" else "solid",
            ),
            rx.button(
                "Terminal",
                on_click=DashboardState.set_page("terminal"),
                variant="ghost" if DashboardState.current_page != "terminal" else "solid",
            ),
            spacing="2",
        ),
        width="100%",
        padding="1rem",
        border_bottom="1px solid var(--gray-6)",
    )

def dashboard_page():
    """Main dashboard page."""
    return rx.vstack(
        rx.heading("Dashboard Overview", size="5"),
        
        # Statistics cards
        rx.hstack(
            rx.card(
                rx.vstack(
                    rx.text("Available Providers", size="2", color="gray"),
                    rx.text(str(len(DashboardState.available_providers)), size="6", weight="bold"),
                    align="center",
                ),
                width="200px",
            ),
            rx.card(
                rx.vstack(
                    rx.text("Active Sandboxes", size="2", color="gray"),
                    rx.text(str(DashboardState.sandbox_count), size="6", weight="bold"),
                    align="center",
                ),
                width="200px",
            ),
            rx.card(
                rx.vstack(
                    rx.text("Commands Executed", size="2", color="gray"),
                    rx.text(str(DashboardState.total_commands_executed), size="6", weight="bold"),
                    align="center",
                ),
                width="200px",
            ),
            spacing="4",
        ),
        
        # Actions
        rx.vstack(
            rx.button(
                "Initialize Grainchain",
                on_click=DashboardState.initialize_grainchain,
                loading=DashboardState.is_loading,
                size="3",
            ),
            rx.button(
                "Clear Messages",
                on_click=DashboardState.clear_messages,
                variant="outline",
                size="2",
            ),
            spacing="2",
        ),
        
        # Messages
        rx.cond(
            DashboardState.success_message != "",
            rx.callout(
                DashboardState.success_message,
                icon="check",
                color="green",
            ),
        ),
        rx.cond(
            DashboardState.error_message != "",
            rx.callout(
                DashboardState.error_message,
                icon="triangle_alert",
                color="red",
            ),
        ),
        
        spacing="6",
        padding="2rem",
        width="100%",
    )

def providers_page():
    """Providers management page."""
    return rx.vstack(
        rx.heading("Available Providers", size="5"),
        
        rx.cond(
            len(DashboardState.available_providers) > 0,
            rx.vstack(
                rx.foreach(
                    DashboardState.available_providers,
                    lambda provider: rx.card(
                        rx.hstack(
                            rx.text(f"🔧 {provider}", size="4", weight="bold"),
                            rx.spacer(),
                            rx.badge("Available", color="green"),
                            width="100%",
                        ),
                        width="100%",
                    ),
                ),
                width="100%",
            ),
            rx.text("No providers available. Click 'Initialize Grainchain' to load providers.", color="gray"),
        ),
        
        spacing="4",
        padding="2rem",
        width="100%",
    )

def terminal_page():
    """Terminal page."""
    return rx.vstack(
        rx.heading("Interactive Terminal", size="5"),
        
        rx.card(
            rx.vstack(
                rx.text("Terminal functionality will be available after selecting a sandbox.", color="gray"),
                rx.code_block(
                    "# Example commands:\n$ echo 'Hello, Grainchain!'\n$ python -c 'print(2+2)'\n$ ls -la",
                    language="bash",
                ),
                spacing="4",
            ),
            width="100%",
            min_height="400px",
        ),
        
        spacing="4",
        padding="2rem",
        width="100%",
    )

def main_content():
    """Main content area based on current page."""
    return rx.cond(
        DashboardState.current_page == "dashboard",
        dashboard_page(),
        rx.cond(
            DashboardState.current_page == "providers",
            providers_page(),
            terminal_page(),
        ),
    )

def index():
    """Main application layout."""
    return rx.vstack(
        navbar(),
        main_content(),
        width="100%",
        min_height="100vh",
        bg="var(--gray-1)",
    )

# Create the app
app = rx.App(
    theme=rx.theme(
        appearance="dark",
        has_background=True,
        radius="medium",
        scaling="100%",
    )
)

app.add_page(index, route="/")

if __name__ == "__main__":
    import reflex as rx
    rx.run(app, host="0.0.0.0", port=3000)
