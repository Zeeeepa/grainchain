"""Demo of the complete Grainchain Dashboard implementation."""

import reflex as rx
from typing import Dict, List, Any

class DemoState(rx.State):
    """Demo state to showcase all features."""
    
    # Navigation
    current_page: str = "dashboard"
    
    # Statistics
    active_sandboxes_count: int = 1
    providers_count: int = 5
    commands_run_count: int = 42
    
    # Provider data
    providers: Dict[str, Dict[str, Any]] = {
        "local": {"name": "Local", "status": "success", "has_api_key": True},
        "e2b": {"name": "E2B", "status": "failed", "has_api_key": False},
        "daytona": {"name": "Daytona", "status": "unknown", "has_api_key": False},
        "morph": {"name": "Morph", "status": "unknown", "has_api_key": False},
        "modal": {"name": "Modal", "status": "unknown", "has_api_key": False},
    }
    
    # File data
    files: List[Dict[str, Any]] = [
        {"name": "main.py", "size": 1024, "type": "file", "modified": "2025-01-05"},
        {"name": "README.md", "size": 2048, "type": "file", "modified": "2025-01-05"},
        {"name": "src", "size": 0, "type": "directory", "modified": "2025-01-05"},
    ]
    
    # Snapshot data
    snapshots: List[Dict[str, Any]] = [
        {"id": "snap_001", "name": "Initial Setup", "status": "ready", "size": "50MB", "created": "2025-01-05"},
        {"id": "snap_002", "name": "After Dependencies", "status": "ready", "size": "120MB", "created": "2025-01-05"},
    ]
    
    # Terminal
    command_output: str = """$ ls -la
total 12
drwxr-xr-x 3 user user 4096 Jan  5 01:20 .
drwxr-xr-x 3 root root 4096 Jan  5 01:20 ..
-rw-r--r-- 1 user user 1024 Jan  5 01:20 main.py
-rw-r--r-- 1 user user 2048 Jan  5 01:20 README.md

$ python --version
Python 3.12.0

$ echo "Hello from Grainchain Dashboard!"
Hello from Grainchain Dashboard!

$ _"""
    
    # Settings
    theme: str = "dark"
    default_provider: str = "local"
    notifications_enabled: bool = True
    
    def set_page(self, page: str):
        """Navigate to a different page."""
        self.current_page = page

def status_badge(status: str) -> rx.Component:
    """Status badge component."""
    color_map = {
        "success": "green",
        "failed": "red", 
        "unknown": "gray",
        "ready": "green"
    }
    color = color_map.get(status, "gray")
    return rx.badge(status.title(), color_scheme=color, variant="soft")

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
                rx.button(
                    rx.hstack(rx.icon("home", size=16), rx.text("Dashboard"), spacing="2"),
                    on_click=lambda: DemoState.set_page("dashboard"),
                    variant=rx.cond(DemoState.current_page == "dashboard", "soft", "ghost"),
                    style={"width": "100%", "justify_content": "flex_start"}
                ),
                rx.button(
                    rx.hstack(rx.icon("plug", size=16), rx.text("Providers"), spacing="2"),
                    on_click=lambda: DemoState.set_page("providers"),
                    variant=rx.cond(DemoState.current_page == "providers", "soft", "ghost"),
                    style={"width": "100%", "justify_content": "flex_start"}
                ),
                rx.button(
                    rx.hstack(rx.icon("terminal", size=16), rx.text("Terminal"), spacing="2"),
                    on_click=lambda: DemoState.set_page("terminal"),
                    variant=rx.cond(DemoState.current_page == "terminal", "soft", "ghost"),
                    style={"width": "100%", "justify_content": "flex_start"}
                ),
                rx.button(
                    rx.hstack(rx.icon("folder", size=16), rx.text("Files"), spacing="2"),
                    on_click=lambda: DemoState.set_page("files"),
                    variant=rx.cond(DemoState.current_page == "files", "soft", "ghost"),
                    style={"width": "100%", "justify_content": "flex_start"}
                ),
                rx.button(
                    rx.hstack(rx.icon("camera", size=16), rx.text("Snapshots"), spacing="2"),
                    on_click=lambda: DemoState.set_page("snapshots"),
                    variant=rx.cond(DemoState.current_page == "snapshots", "soft", "ghost"),
                    style={"width": "100%", "justify_content": "flex_start"}
                ),
                rx.button(
                    rx.hstack(rx.icon("settings", size=16), rx.text("Settings"), spacing="2"),
                    on_click=lambda: DemoState.set_page("settings"),
                    variant=rx.cond(DemoState.current_page == "settings", "soft", "ghost"),
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
            "border_right": "1px solid var(--gray-6)"
        }
    )

def dashboard_content() -> rx.Component:
    """Dashboard page content."""
    return rx.vstack(
        rx.heading("🚀 Grainchain Dashboard", size="7"),
        rx.text("Modern sandbox management interface", size="4", color="gray"),
        
        # Statistics cards
        rx.hstack(
            rx.card(
                rx.vstack(
                    rx.text("Active Sandboxes", size="2", color="gray"),
                    rx.text(DemoState.active_sandboxes_count, size="6", weight="bold", color="green"),
                    spacing="1"
                ),
                style={"padding": "1.5rem", "min_width": "150px"}
            ),
            rx.card(
                rx.vstack(
                    rx.text("Providers", size="2", color="gray"),
                    rx.text(DemoState.providers_count, size="6", weight="bold", color="blue"),
                    spacing="1"
                ),
                style={"padding": "1.5rem", "min_width": "150px"}
            ),
            rx.card(
                rx.vstack(
                    rx.text("Commands Run", size="2", color="gray"),
                    rx.text(DemoState.commands_run_count, size="6", weight="bold", color="purple"),
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
                        rx.vstack(rx.icon("plus", size=20), rx.text("Create Snapshot"), spacing="2", align="center"),
                        variant="outline", style={"height": "80px", "width": "100%"}
                    ),
                    rx.button(
                        rx.vstack(rx.icon("upload", size=20), rx.text("Upload File"), spacing="2", align="center"),
                        variant="outline", style={"height": "80px", "width": "100%"}
                    ),
                    rx.button(
                        rx.vstack(rx.icon("settings", size=20), rx.text("Configure Provider"), spacing="2", align="center"),
                        on_click=lambda: DemoState.set_page("providers"),
                        variant="outline", style={"height": "80px", "width": "100%"}
                    ),
                    rx.button(
                        rx.vstack(rx.icon("terminal", size=20), rx.text("Open Terminal"), spacing="2", align="center"),
                        on_click=lambda: DemoState.set_page("terminal"),
                        variant="outline", style={"height": "80px", "width": "100%"}
                    ),
                    columns="2", spacing="4"
                ),
                spacing="4", width="100%"
            ),
            style={"padding": "2rem"}
        ),
        
        spacing="6",
        style={"padding": "2rem", "max_width": "1200px", "margin": "0 auto"}
    )

def providers_content() -> rx.Component:
    """Providers page content."""
    return rx.vstack(
        rx.heading("🔌 Sandbox Providers", size="6"),
        rx.text("Configure and manage your sandbox providers", size="3", color="gray"),
        
        rx.grid(
            rx.foreach(
                DemoState.providers,
                lambda provider_name, provider_data: rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.text("🏠" if provider_name == "local" else "☁️", size="5"),
                            rx.heading(provider_data["name"], size="4"),
                            status_badge(provider_data["status"]),
                            justify="between", width="100%"
                        ),
                        rx.text(f"API Key: {'✅ Configured' if provider_data['has_api_key'] else '❌ Missing'}", size="2"),
                        rx.button("Configure", size="2", variant="soft"),
                        spacing="3", align="start"
                    ),
                    style={"padding": "1.5rem", "min_height": "150px"}
                )
            ),
            columns="2", spacing="4", width="100%"
        ),
        
        spacing="6",
        style={"padding": "2rem", "max_width": "1200px", "margin": "0 auto"}
    )

def terminal_content() -> rx.Component:
    """Terminal page content."""
    return rx.vstack(
        rx.heading("💻 Interactive Terminal", size="6"),
        rx.text("Execute commands in your sandbox environment", size="3", color="gray"),
        
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.text("Connected to:", size="2", color="gray"),
                    rx.badge("local-sandbox-123", color_scheme="green"),
                    justify="start"
                ),
                rx.divider(),
                
                rx.box(
                    rx.text(
                        DemoState.command_output,
                        style={
                            "font_family": "monospace",
                            "white_space": "pre",
                            "background": "var(--gray-1)",
                            "padding": "1rem",
                            "border_radius": "6px",
                            "font_size": "14px",
                            "line_height": "1.5"
                        }
                    ),
                    style={"width": "100%", "min_height": "300px", "overflow": "auto"}
                ),
                
                rx.divider(),
                
                rx.hstack(
                    rx.text("$", size="3", weight="bold", color="green"),
                    rx.input(placeholder="Enter command...", style={"flex": "1", "font_family": "monospace"}),
                    rx.button("Execute", color_scheme="blue"),
                    spacing="3", width="100%"
                ),
                
                spacing="4", width="100%"
            ),
            style={"padding": "1.5rem"}
        ),
        
        spacing="6",
        style={"padding": "2rem", "max_width": "1200px", "margin": "0 auto"}
    )

def files_content() -> rx.Component:
    """Files page content."""
    return rx.vstack(
        rx.heading("📁 File Manager", size="6"),
        rx.text("Browse, upload, and manage sandbox files", size="3", color="gray"),
        
        rx.hstack(
            rx.button(rx.hstack(rx.icon("upload", size=16), rx.text("Upload"), spacing="2"), color_scheme="blue"),
            rx.button(rx.hstack(rx.icon("folder-plus", size=16), rx.text("New Folder"), spacing="2"), variant="soft"),
            rx.input(placeholder="Search files...", style={"flex": "1"}),
            spacing="3", width="100%"
        ),
        
        rx.card(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Name"),
                        rx.table.column_header_cell("Size"),
                        rx.table.column_header_cell("Modified"),
                        rx.table.column_header_cell("Actions")
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        DemoState.files,
                        lambda file: rx.table.row(
                            rx.table.cell(
                                rx.hstack(
                                    rx.icon("folder" if file["type"] == "directory" else "file", size=16),
                                    rx.text(file["name"]),
                                    spacing="2"
                                )
                            ),
                            rx.table.cell(f"{file['size']} bytes" if file["type"] == "file" else "-"),
                            rx.table.cell(file["modified"]),
                            rx.table.cell(
                                rx.hstack(
                                    rx.button(rx.icon("download", size=14), size="1", variant="ghost"),
                                    rx.button(rx.icon("trash", size=14), size="1", variant="ghost", color_scheme="red"),
                                    spacing="1"
                                )
                            )
                        )
                    )
                ),
                variant="surface", size="2"
            ),
            style={"padding": "1rem"}
        ),
        
        spacing="6",
        style={"padding": "2rem", "max_width": "1200px", "margin": "0 auto"}
    )

def snapshots_content() -> rx.Component:
    """Snapshots page content."""
    return rx.vstack(
        rx.heading("📸 Snapshot Manager", size="6"),
        rx.text("Create, restore, and manage sandbox snapshots", size="3", color="gray"),
        
        rx.hstack(
            rx.button(rx.hstack(rx.icon("plus", size=16), rx.text("Create Snapshot"), spacing="2"), color_scheme="blue"),
            rx.button(rx.hstack(rx.icon("download", size=16), rx.text("Import"), spacing="2"), variant="soft"),
            spacing="3"
        ),
        
        rx.grid(
            rx.foreach(
                DemoState.snapshots,
                lambda snapshot: rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.text("📸", size="5"),
                            rx.heading(snapshot["name"], size="4"),
                            status_badge(snapshot["status"]),
                            justify="between", width="100%"
                        ),
                        rx.text(f"Size: {snapshot['size']}", size="2", color="gray"),
                        rx.text(f"Created: {snapshot['created']}", size="2", color="gray"),
                        rx.hstack(
                            rx.button("Restore", size="2", color_scheme="blue"),
                            rx.button("Export", size="2", variant="soft"),
                            rx.button("Delete", size="2", variant="soft", color_scheme="red"),
                            spacing="2"
                        ),
                        spacing="3", align="start"
                    ),
                    style={"padding": "1.5rem"}
                )
            ),
            columns="2", spacing="4", width="100%"
        ),
        
        spacing="6",
        style={"padding": "2rem", "max_width": "1200px", "margin": "0 auto"}
    )

def settings_content() -> rx.Component:
    """Settings page content."""
    return rx.vstack(
        rx.heading("⚙️ Settings", size="6"),
        rx.text("Configure dashboard preferences and global settings", size="3", color="gray"),
        
        rx.grid(
            rx.card(
                rx.vstack(
                    rx.heading("General", size="4"),
                    rx.divider(),
                    rx.vstack(
                        rx.hstack(
                            rx.text("Theme:", size="2", weight="medium"),
                            rx.select(["Light", "Dark"], value=DemoState.theme.title()),
                            spacing="3", width="100%", justify="between"
                        ),
                        rx.hstack(
                            rx.text("Default Provider:", size="2", weight="medium"),
                            rx.select(["Local", "E2B", "Daytona"], value=DemoState.default_provider.title()),
                            spacing="3", width="100%", justify="between"
                        ),
                        rx.hstack(
                            rx.text("Notifications:", size="2", weight="medium"),
                            rx.switch(checked=DemoState.notifications_enabled),
                            spacing="3", width="100%", justify="between"
                        ),
                        spacing="4", width="100%"
                    ),
                    spacing="3", width="100%"
                ),
                style={"padding": "1.5rem"}
            ),
            
            rx.card(
                rx.vstack(
                    rx.heading("Advanced", size="4"),
                    rx.divider(),
                    rx.vstack(
                        rx.button("Export Configuration", variant="soft", width="100%"),
                        rx.button("Import Configuration", variant="soft", width="100%"),
                        rx.button("Reset to Defaults", variant="soft", color_scheme="red", width="100%"),
                        spacing="3", width="100%"
                    ),
                    spacing="3", width="100%"
                ),
                style={"padding": "1.5rem"}
            ),
            
            columns="2", spacing="4", width="100%"
        ),
        
        spacing="6",
        style={"padding": "2rem", "max_width": "1200px", "margin": "0 auto"}
    )

def page_content() -> rx.Component:
    """Render page content based on current page."""
    return rx.match(
        DemoState.current_page,
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

app.add_page(index, route="/", title="Grainchain Dashboard - Complete Implementation")
