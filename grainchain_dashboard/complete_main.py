"""Complete Grainchain Dashboard with all features implemented."""

import reflex as rx
from typing import Dict, List, Optional, Any
from .enhanced_state import EnhancedDashboardState

# Import UI components
from .components.ui_components import (
    modal_dialog, toast_notification, loading_spinner, 
    confirmation_dialog, file_icon, format_file_size
)

def sidebar() -> rx.Component:
    """Enhanced sidebar with all navigation options."""
    return rx.box(
        rx.vstack(
            # Header
            rx.hstack(
                rx.icon("link", size=20, color="blue"),
                rx.heading("Grainchain", size="5"),
                spacing="2",
                style={"padding": "1rem"}
            ),
            rx.divider(),
            
            # Navigation items
            rx.vstack(
                # Dashboard
                rx.button(
                    rx.hstack(
                        rx.icon("home", size=16),
                        rx.text("Dashboard"),
                        spacing="2"
                    ),
                    on_click=lambda: EnhancedDashboardState.set_page("dashboard"),
                    variant=rx.cond(
                        EnhancedDashboardState.current_page == "dashboard", 
                        "soft", "ghost"
                    ),
                    style={"width": "100%", "justify_content": "flex_start"}
                ),
                
                # Providers
                rx.button(
                    rx.hstack(
                        rx.icon("plug", size=16),
                        rx.text("Providers"),
                        spacing="2"
                    ),
                    on_click=lambda: EnhancedDashboardState.set_page("providers"),
                    variant=rx.cond(
                        EnhancedDashboardState.current_page == "providers", 
                        "soft", "ghost"
                    ),
                    style={"width": "100%", "justify_content": "flex_start"}
                ),
                
                # Terminal
                rx.button(
                    rx.hstack(
                        rx.icon("terminal", size=16),
                        rx.text("Terminal"),
                        spacing="2"
                    ),
                    on_click=lambda: EnhancedDashboardState.set_page("terminal"),
                    variant=rx.cond(
                        EnhancedDashboardState.current_page == "terminal", 
                        "soft", "ghost"
                    ),
                    style={"width": "100%", "justify_content": "flex_start"}
                ),
                
                # Files - NEW
                rx.button(
                    rx.hstack(
                        rx.icon("folder", size=16),
                        rx.text("Files"),
                        spacing="2"
                    ),
                    on_click=lambda: EnhancedDashboardState.set_page("files"),
                    variant=rx.cond(
                        EnhancedDashboardState.current_page == "files", 
                        "soft", "ghost"
                    ),
                    style={"width": "100%", "justify_content": "flex_start"}
                ),
                
                # Snapshots - NEW
                rx.button(
                    rx.hstack(
                        rx.icon("camera", size=16),
                        rx.text("Snapshots"),
                        spacing="2"
                    ),
                    on_click=lambda: EnhancedDashboardState.set_page("snapshots"),
                    variant=rx.cond(
                        EnhancedDashboardState.current_page == "snapshots", 
                        "soft", "ghost"
                    ),
                    style={"width": "100%", "justify_content": "flex_start"}
                ),
                
                # Settings - NEW
                rx.button(
                    rx.hstack(
                        rx.icon("settings", size=16),
                        rx.text("Settings"),
                        spacing="2"
                    ),
                    on_click=lambda: EnhancedDashboardState.set_page("settings"),
                    variant=rx.cond(
                        EnhancedDashboardState.current_page == "settings", 
                        "soft", "ghost"
                    ),
                    style={"width": "100%", "justify_content": "flex_start"}
                ),
                
                spacing="2",
                style={"padding": "0 1rem"}
            ),
            
            # Status indicator
            rx.divider(),
            rx.box(
                rx.hstack(
                    rx.icon("circle", size=8, color="green"),
                    rx.text("Connected", size="2", color="green"),
                    spacing="2"
                ),
                style={"padding": "1rem"}
            ),
            
            spacing="4"
        ),
        style={
            "width": "250px",
            "height": "100vh",
            "background": "var(--gray-2)",
            "border_right": "1px solid var(--gray-6)",
            "display": rx.cond(EnhancedDashboardState.sidebar_open, "block", "none")
        }
    )

def dashboard_content() -> rx.Component:
    """Enhanced dashboard page with real statistics."""
    return rx.vstack(
        # Header
        rx.hstack(
            rx.heading("🚀 Grainchain Dashboard", size="7"),
            rx.spacer(),
            rx.button(
                rx.icon("refresh-cw", size=16),
                on_click=EnhancedDashboardState.update_statistics,
                variant="ghost",
                size="2"
            ),
            width="100%"
        ),
        rx.text("Modern sandbox management interface", size="4", color="gray"),
        
        # Statistics cards
        rx.hstack(
            rx.card(
                rx.vstack(
                    rx.text("Active Sandboxes", size="2", color="gray"),
                    rx.text(
                        EnhancedDashboardState.active_sandboxes_count, 
                        size="6", weight="bold", color="green"
                    ),
                    spacing="1"
                ),
                style={"padding": "1.5rem", "min_width": "150px"}
            ),
            rx.card(
                rx.vstack(
                    rx.text("Providers", size="2", color="gray"),
                    rx.text(
                        EnhancedDashboardState.providers_count, 
                        size="6", weight="bold", color="blue"
                    ),
                    spacing="1"
                ),
                style={"padding": "1.5rem", "min_width": "150px"}
            ),
            rx.card(
                rx.vstack(
                    rx.text("Commands Run", size="2", color="gray"),
                    rx.text(
                        EnhancedDashboardState.commands_run_count, 
                        size="6", weight="bold", color="purple"
                    ),
                    spacing="1"
                ),
                style={"padding": "1.5rem", "min_width": "150px"}
            ),
            spacing="4"
        ),
        
        # Quick actions
        rx.card(
            rx.vstack(
                rx.heading("⚡ Quick Actions", size="5"),
                rx.divider(),
                rx.grid(
                    rx.button(
                        rx.vstack(
                            rx.icon("plus", size=20),
                            rx.text("Create Snapshot"),
                            spacing="2", align="center"
                        ),
                        on_click=EnhancedDashboardState.open_snapshot_create_modal,
                        variant="outline",
                        style={"height": "80px", "width": "100%"}
                    ),
                    rx.button(
                        rx.vstack(
                            rx.icon("upload", size=20),
                            rx.text("Upload File"),
                            spacing="2", align="center"
                        ),
                        on_click=EnhancedDashboardState.open_file_upload_modal,
                        variant="outline",
                        style={"height": "80px", "width": "100%"}
                    ),
                    rx.button(
                        rx.vstack(
                            rx.icon("settings", size=20),
                            rx.text("Configure Provider"),
                            spacing="2", align="center"
                        ),
                        on_click=lambda: EnhancedDashboardState.set_page("providers"),
                        variant="outline",
                        style={"height": "80px", "width": "100%"}
                    ),
                    rx.button(
                        rx.vstack(
                            rx.icon("terminal", size=20),
                            rx.text("Open Terminal"),
                            spacing="2", align="center"
                        ),
                        on_click=lambda: EnhancedDashboardState.set_page("terminal"),
                        variant="outline",
                        style={"height": "80px", "width": "100%"}
                    ),
                    columns="2",
                    spacing="4"
                ),
                spacing="4",
                width="100%"
            ),
            style={"padding": "2rem"}
        ),
        
        # Features showcase
        rx.card(
            rx.vstack(
                rx.heading("✨ Key Features", size="5"),
                rx.divider(),
                rx.grid(
                    rx.vstack(
                        rx.text("🔌", size="6"),
                        rx.text("Multi-Provider Support", weight="bold"),
                        rx.text("E2B, Daytona, Morph, Modal, Local", size="2", color="gray"),
                        spacing="2", align="center"
                    ),
                    rx.vstack(
                        rx.text("💻", size="6"),
                        rx.text("Interactive Terminal", weight="bold"),
                        rx.text("Real-time command execution", size="2", color="gray"),
                        spacing="2", align="center"
                    ),
                    rx.vstack(
                        rx.text("📁", size="6"),
                        rx.text("File Management", weight="bold"),
                        rx.text("Upload, download, browse files", size="2", color="gray"),
                        spacing="2", align="center"
                    ),
                    rx.vstack(
                        rx.text("📸", size="6"),
                        rx.text("Snapshot Manager", weight="bold"),
                        rx.text("Create and restore snapshots", size="2", color="gray"),
                        spacing="2", align="center"
                    ),
                    columns="2",
                    spacing="6"
                ),
                spacing="4",
                width="100%"
            ),
            style={"padding": "2rem"}
        ),
        
        spacing="6",
        style={"padding": "2rem", "max_width": "1200px", "margin": "0 auto"}
    )
