"""Simplified demo version of Grainchain Dashboard for testing."""

import reflex as rx
from typing import Dict, List, Any

class DemoState(rx.State):
    """Demo state for the dashboard."""
    
    # UI State
    current_page: str = "dashboard"
    sidebar_open: bool = True
    
    # Mock data
    providers: Dict[str, Dict[str, Any]] = {
        "local": {
            "available": True,
            "dependencies_installed": True,
            "config_valid": True,
            "missing_config": [],
            "status": "healthy"
        },
        "e2b": {
            "available": False,
            "dependencies_installed": False,
            "config_valid": False,
            "missing_config": ["E2B_API_KEY"],
            "status": "unhealthy"
        },
        "daytona": {
            "available": False,
            "dependencies_installed": False,
            "config_valid": False,
            "missing_config": ["DAYTONA_API_KEY"],
            "status": "unhealthy"
        }
    }
    
    active_sandboxes: List[Dict[str, Any]] = [
        {
            "sandbox_id": "local-1234567890",
            "provider": "local",
            "status": "running",
            "created_at": "2025-01-05 01:20:00",
            "last_activity": "2025-01-05 01:25:00"
        }
    ]
    
    selected_provider: str = "local"
    selected_sandbox_id: str = "local-1234567890"
    command_input: str = ""
    command_output: str = "Welcome to Grainchain Dashboard!\nType a command to get started."
    
    def set_page(self, page: str):
        """Set the current page."""
        self.current_page = page
    
    def toggle_sidebar(self):
        """Toggle sidebar visibility."""
        self.sidebar_open = not self.sidebar_open
    
    def select_provider(self, provider: str):
        """Select a provider."""
        self.selected_provider = provider
    
    def execute_command(self):
        """Mock command execution."""
        if self.command_input.strip():
            self.command_output += f"\n$ {self.command_input}\n"
            
            # Mock responses
            if self.command_input.strip() == "ls":
                self.command_output += "main.py  README.md  requirements.txt\n"
            elif self.command_input.strip() == "pwd":
                self.command_output += "/home/user\n"
            elif self.command_input.strip() == "whoami":
                self.command_output += "user\n"
            else:
                self.command_output += f"Mock output for: {self.command_input}\n"
            
            self.command_input = ""

def provider_card(name: str, info: Dict[str, Any]) -> rx.Component:
    """Create a provider card."""
    status_color = "green" if info.get("available", False) else "red"
    
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading(name.title(), size="4"),
                rx.badge(
                    "Available" if info.get("available", False) else "Unavailable",
                    color_scheme=status_color,
                    variant="soft"
                ),
                justify="between",
                width="100%"
            ),
            rx.text(
                f"Dependencies: {'✓' if info.get('dependencies_installed', False) else '✗'}",
                size="2",
                color="gray"
            ),
            spacing="2",
            align="start"
        ),
        variant="surface",
        style={"min_height": "100px", "cursor": "pointer"},
        on_click=lambda: DemoState.select_provider(name)
    )

def sidebar() -> rx.Component:
    """Create the sidebar."""
    return rx.box(
        rx.vstack(
            # Header
            rx.hstack(
                rx.icon("layers", size=24, color="blue"),
                rx.heading("Grainchain", size="4"),
                spacing="2",
                align="center",
                style={"padding": "1rem"}
            ),
            
            rx.divider(),
            
            # Navigation
            rx.vstack(
                rx.button(
                    rx.hstack(
                        rx.icon("home", size=18),
                        rx.text("Dashboard", size="2"),
                        spacing="3"
                    ),
                    on_click=lambda: DemoState.set_page("dashboard"),
                    variant="soft" if DemoState.current_page == "dashboard" else "ghost",
                    style={"width": "100%", "justify_content": "flex_start"}
                ),
                rx.button(
                    rx.hstack(
                        rx.icon("server", size=18),
                        rx.text("Providers", size="2"),
                        spacing="3"
                    ),
                    on_click=lambda: DemoState.set_page("providers"),
                    variant="soft" if DemoState.current_page == "providers" else "ghost",
                    style={"width": "100%", "justify_content": "flex_start"}
                ),
                rx.button(
                    rx.hstack(
                        rx.icon("terminal", size=18),
                        rx.text("Terminal", size="2"),
                        spacing="3"
                    ),
                    on_click=lambda: DemoState.set_page("terminal"),
                    variant="soft" if DemoState.current_page == "terminal" else "ghost",
                    style={"width": "100%", "justify_content": "flex_start"}
                ),
                rx.button(
                    rx.hstack(
                        rx.icon("folder", size=18),
                        rx.text("Files", size="2"),
                        spacing="3"
                    ),
                    on_click=lambda: DemoState.set_page("files"),
                    variant="soft" if DemoState.current_page == "files" else "ghost",
                    style={"width": "100%", "justify_content": "flex_start"}
                ),
                spacing="1",
                width="100%",
                style={"padding": "0 1rem"}
            ),
            
            spacing="0",
            height="100vh",
            width="100%"
        ),
        style={
            "width": "280px",
            "min_width": "280px",
            "background": "var(--gray-2)",
            "border_right": "1px solid var(--gray-6)"
        }
    )

def dashboard_page() -> rx.Component:
    """Dashboard page content."""
    return rx.vstack(
        rx.heading("Dashboard Overview", size="6"),
        
        # Quick stats
        rx.hstack(
            rx.card(
                rx.vstack(
                    rx.text("Active Sandboxes", size="2", color="gray"),
                    rx.text("1", size="6", weight="bold"),
                    spacing="1"
                ),
                variant="surface",
                style={"padding": "1rem", "min_width": "150px"}
            ),
            rx.card(
                rx.vstack(
                    rx.text("Providers Online", size="2", color="gray"),
                    rx.text("1", size="6", weight="bold"),
                    spacing="1"
                ),
                variant="surface",
                style={"padding": "1rem", "min_width": "150px"}
            ),
            rx.card(
                rx.vstack(
                    rx.text("Commands Run", size="2", color="gray"),
                    rx.text("0", size="6", weight="bold"),
                    spacing="1"
                ),
                variant="surface",
                style={"padding": "1rem", "min_width": "150px"}
            ),
            spacing="4"
        ),
        
        # Active sandboxes
        rx.card(
            rx.vstack(
                rx.heading("Active Sandboxes", size="4"),
                rx.divider(),
                rx.hstack(
                    rx.vstack(
                        rx.text("Sandbox local-12...", weight="bold"),
                        rx.text("Provider: local", size="2", color="gray"),
                        align="start"
                    ),
                    rx.badge("Running", color_scheme="green"),
                    justify="between",
                    width="100%"
                ),
                spacing="3",
                width="100%"
            ),
            variant="surface"
        ),
        
        spacing="6",
        width="100%",
        style={"padding": "2rem"}
    )

def providers_page() -> rx.Component:
    """Providers page content."""
    return rx.vstack(
        rx.heading("Sandbox Providers", size="6"),
        rx.text("Select and configure your sandbox providers", size="3", color="gray"),
        
        rx.grid(
            provider_card("local", {"available": True, "dependencies_installed": True}),
            provider_card("e2b", {"available": False, "dependencies_installed": False}),
            provider_card("daytona", {"available": False, "dependencies_installed": False}),
            columns="3",
            spacing="4",
            width="100%"
        ),
        
        spacing="6",
        width="100%",
        style={"padding": "2rem"}
    )

def terminal_page() -> rx.Component:
    """Terminal page content."""
    return rx.vstack(
        rx.heading("Interactive Terminal", size="6"),
        rx.text(f"Connected to: {DemoState.selected_sandbox_id}", size="2", color="gray"),
        
        # Command output
        rx.card(
            rx.vstack(
                rx.text("Output", weight="bold"),
                rx.divider(),
                rx.text_area(
                    value=DemoState.command_output,
                    read_only=True,
                    rows=15,
                    style={"font_family": "monospace", "width": "100%"}
                ),
                spacing="2",
                width="100%"
            ),
            variant="surface"
        ),
        
        # Command input
        rx.form(
            rx.hstack(
                rx.text("$", size="3", weight="bold", color="green"),
                rx.input(
                    placeholder="Enter command...",
                    value=DemoState.command_input,
                    on_change=DemoState.set_command_input,
                    style={"flex": "1", "font_family": "monospace"}
                ),
                rx.button("Execute", type="submit"),
                spacing="2",
                width="100%"
            ),
            on_submit=DemoState.execute_command,
            width="100%"
        ),
        
        spacing="6",
        width="100%",
        style={"padding": "2rem"}
    )

def files_page() -> rx.Component:
    """Files page content."""
    return rx.vstack(
        rx.heading("File Browser", size="6"),
        rx.text("Browse and manage sandbox files", size="3", color="gray"),
        
        rx.card(
            rx.vstack(
                rx.text("File browser functionality coming soon!", size="3"),
                rx.text("This would show:", size="2", color="gray"),
                rx.unordered_list(
                    rx.list_item("Directory navigation"),
                    rx.list_item("File upload/download"),
                    rx.list_item("File editing capabilities"),
                    rx.list_item("Permission management")
                ),
                spacing="3"
            ),
            variant="surface",
            style={"padding": "2rem", "text_align": "center"}
        ),
        
        spacing="6",
        width="100%",
        style={"padding": "2rem"}
    )

def page_content() -> rx.Component:
    """Render the appropriate page content."""
    return rx.match(
        DemoState.current_page,
        ("dashboard", dashboard_page()),
        ("providers", providers_page()),
        ("terminal", terminal_page()),
        ("files", files_page()),
        dashboard_page()  # Default
    )

def index() -> rx.Component:
    """Main index page."""
    return rx.hstack(
        # Sidebar
        sidebar(),
        
        # Main content
        rx.box(
            rx.vstack(
                # Header
                rx.box(
                    rx.hstack(
                        rx.heading(
                            rx.match(
                                DemoState.current_page,
                                ("dashboard", "Dashboard"),
                                ("providers", "Providers"),
                                ("terminal", "Terminal"),
                                ("files", "Files"),
                                "Dashboard"
                            ),
                            size="6"
                        ),
                        rx.spacer(),
                        rx.text("Grainchain Dashboard Demo", size="2", color="gray"),
                        justify="between",
                        width="100%"
                    ),
                    style={
                        "padding": "1.5rem 2rem",
                        "border_bottom": "1px solid var(--gray-6)",
                        "background": "var(--gray-1)"
                    }
                ),
                
                # Page content
                rx.box(
                    page_content(),
                    style={"flex": "1", "overflow_y": "auto"}
                ),
                
                spacing="0",
                width="100%",
                height="100vh"
            ),
            style={"flex": "1", "background": "var(--gray-1)"}
        ),
        
        spacing="0",
        width="100%",
        height="100vh"
    )

# Create the app
app = rx.App(
    style={
        "font_family": "Inter, system-ui, sans-serif",
        "background_color": "var(--gray-1)",
    }
)

# Add the main page
app.add_page(index, route="/", title="Grainchain Dashboard Demo")

if __name__ == "__main__":
    app.compile()
