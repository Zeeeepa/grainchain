"""Simple working version of Grainchain Dashboard."""

import reflex as rx

class State(rx.State):
    """Simple state for demo."""
    current_page: str = "dashboard"
    
    def set_page(self, page: str):
        self.current_page = page

def sidebar() -> rx.Component:
    """Simple sidebar."""
    return rx.box(
        rx.vstack(
            rx.heading("🔗 Grainchain", size="5", style={"padding": "1rem"}),
            rx.divider(),
            rx.vstack(
                rx.button(
                    "📊 Dashboard",
                    on_click=lambda: State.set_page("dashboard"),
                    variant=rx.cond(State.current_page == "dashboard", "soft", "ghost"),
                    style={"width": "100%", "justify_content": "flex_start"}
                ),
                rx.button(
                    "🔌 Providers", 
                    on_click=lambda: State.set_page("providers"),
                    variant=rx.cond(State.current_page == "providers", "soft", "ghost"),
                    style={"width": "100%", "justify_content": "flex_start"}
                ),
                rx.button(
                    "💻 Terminal",
                    on_click=lambda: State.set_page("terminal"),
                    variant=rx.cond(State.current_page == "terminal", "soft", "ghost"),
                    style={"width": "100%", "justify_content": "flex_start"}
                ),
                spacing="2",
                style={"padding": "0 1rem"}
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
        
        # Stats cards
        rx.hstack(
            rx.card(
                rx.vstack(
                    rx.text("Active Sandboxes", size="2", color="gray"),
                    rx.text("1", size="6", weight="bold", color="green"),
                    spacing="1"
                ),
                style={"padding": "1.5rem", "min_width": "150px"}
            ),
            rx.card(
                rx.vstack(
                    rx.text("Providers", size="2", color="gray"),
                    rx.text("5", size="6", weight="bold", color="blue"),
                    spacing="1"
                ),
                style={"padding": "1.5rem", "min_width": "150px"}
            ),
            rx.card(
                rx.vstack(
                    rx.text("Commands Run", size="2", color="gray"),
                    rx.text("42", size="6", weight="bold", color="purple"),
                    spacing="1"
                ),
                style={"padding": "1.5rem", "min_width": "150px"}
            ),
            spacing="4"
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

def providers_content() -> rx.Component:
    """Providers page content."""
    return rx.vstack(
        rx.heading("🔌 Sandbox Providers", size="6"),
        rx.text("Configure and manage your sandbox providers", size="3", color="gray"),
        
        rx.grid(
            # Local Provider
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.text("🏠", size="5"),
                        rx.heading("Local", size="4"),
                        rx.badge("Available", color_scheme="green"),
                        justify="between", width="100%"
                    ),
                    rx.text("Local development environment", size="2", color="gray"),
                    rx.text("✅ Dependencies installed", size="2", color="green"),
                    rx.text("✅ Configuration valid", size="2", color="green"),
                    spacing="3", align="start"
                ),
                style={"padding": "1.5rem", "min_height": "150px"}
            ),
            
            # E2B Provider
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.text("☁️", size="5"),
                        rx.heading("E2B", size="4"),
                        rx.badge("Unavailable", color_scheme="red"),
                        justify="between", width="100%"
                    ),
                    rx.text("Cloud sandboxes with templates", size="2", color="gray"),
                    rx.text("❌ Missing E2B_API_KEY", size="2", color="red"),
                    rx.text("Install: pip install grainchain[e2b]", size="2", color="blue"),
                    spacing="3", align="start"
                ),
                style={"padding": "1.5rem", "min_height": "150px"}
            ),
            
            # Daytona Provider
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.text("🚀", size="5"),
                        rx.heading("Daytona", size="4"),
                        rx.badge("Unavailable", color_scheme="red"),
                        justify="between", width="100%"
                    ),
                    rx.text("Development workspaces", size="2", color="gray"),
                    rx.text("❌ Missing DAYTONA_API_KEY", size="2", color="red"),
                    rx.text("Install: pip install grainchain[daytona]", size="2", color="blue"),
                    spacing="3", align="start"
                ),
                style={"padding": "1.5rem", "min_height": "150px"}
            ),
            
            columns="2",
            spacing="4",
            width="100%"
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
                
                # Terminal output area
                rx.box(
                    rx.text(
                        """$ ls -la
total 12
drwxr-xr-x 3 user user 4096 Jan  5 01:20 .
drwxr-xr-x 3 root root 4096 Jan  5 01:20 ..
-rw-r--r-- 1 user user 1024 Jan  5 01:20 main.py
-rw-r--r-- 1 user user 2048 Jan  5 01:20 README.md

$ python --version
Python 3.12.0

$ whoami
user

$ pwd
/home/user

$ echo "Hello from Grainchain Dashboard!"
Hello from Grainchain Dashboard!

$ _""",
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
                
                # Command input
                rx.hstack(
                    rx.text("$", size="3", weight="bold", color="green"),
                    rx.input(
                        placeholder="Enter command...",
                        style={"flex": "1", "font_family": "monospace"}
                    ),
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

def page_content() -> rx.Component:
    """Render page content based on current page."""
    return rx.match(
        State.current_page,
        ("dashboard", dashboard_content()),
        ("providers", providers_content()),
        ("terminal", terminal_content()),
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
    style={
        "font_family": "Inter, system-ui, sans-serif"
    }
)

app.add_page(index, route="/", title="Grainchain Dashboard")
