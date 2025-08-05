#!/usr/bin/env python3
"""Fully-Featured Grainchain Dashboard - Production Ready."""

import reflex as rx
import asyncio
from typing import Dict, List, Optional, Any
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Import Grainchain core
from grainchain import Sandbox, SandboxConfig, Providers
from grainchain.core.interfaces import SandboxStatus, ExecutionResult, FileInfo

class DashboardState(rx.State):
    """Production Grainchain Dashboard State."""
    
    # Navigation
    current_page: str = "dashboard"
    
    # Core Grainchain instance
    grainchain_instance: Optional[Sandbox] = None
    
    # Active sandbox
    active_sandbox_id: Optional[str] = None
    active_sandbox_session = None
    
    # Real-time data
    sandboxes: List[Dict[str, Any]] = []
    snapshots: List[Dict[str, Any]] = []
    providers: List[Dict[str, Any]] = []
    files: List[Dict[str, Any]] = []
    
    # Terminal state
    terminal_output: str = ""
    command_input: str = ""
    command_history: List[str] = []
    
    # Status indicators
    is_loading: bool = False
    error_message: str = ""
    success_message: str = ""
    
    # Statistics
    total_sandboxes: int = 0
    active_sandboxes: int = 0
    total_snapshots: int = 0
    commands_executed: int = 0
    
    async def initialize_grainchain(self):
        """Initialize Grainchain instance."""
        try:
            self.is_loading = True
            # Create a local sandbox instance for demonstration
            self.grainchain_instance = Sandbox(provider="local")
            await self.refresh_providers()
            await self.refresh_sandboxes()
            self.success_message = "Grainchain initialized successfully"
        except Exception as e:
            self.error_message = f"Failed to initialize Grainchain: {str(e)}"
        finally:
            self.is_loading = False
    
    async def refresh_providers(self):
        """Refresh provider list and status."""
        if not self.grainchain_instance:
            return
        
        try:
            # Get available providers
            provider_info = []
            for provider_name in ["local", "e2b", "daytona", "morph", "modal"]:
                try:
                    provider = await self.grainchain_instance.get_provider(provider_name)
                    status = "available" if provider else "unavailable"
                    provider_info.append({
                        "name": provider_name,
                        "status": status,
                        "description": self._get_provider_description(provider_name)
                    })
                except Exception:
                    provider_info.append({
                        "name": provider_name,
                        "status": "error",
                        "description": self._get_provider_description(provider_name)
                    })
            
            self.providers = provider_info
        except Exception as e:
            self.error_message = f"Failed to refresh providers: {str(e)}"
    
    def _get_provider_description(self, provider_name: str) -> str:
        """Get provider description."""
        descriptions = {
            "local": "Local development environment",
            "e2b": "Cloud sandboxes with templates",
            "daytona": "Development workspaces",
            "morph": "Custom VMs with fast snapshots",
            "modal": "Serverless compute platform"
        }
        return descriptions.get(provider_name, "Unknown provider")
    
    async def create_sandbox(self, provider_name: str):
        """Create a new sandbox."""
        if not self.grainchain_instance:
            await self.initialize_grainchain()
        
        try:
            self.is_loading = True
            config = SandboxConfig(
                timeout=300,
                working_directory="~",
                auto_cleanup=False
            )
            
            sandbox = await self.grainchain_instance.create_sandbox(
                provider=provider_name,
                config=config
            )
            
            self.active_sandbox_id = sandbox.sandbox_id
            self.active_sandbox_session = sandbox
            await self.refresh_sandboxes()
            self.success_message = f"Sandbox created: {sandbox.sandbox_id}"
            
        except Exception as e:
            self.error_message = f"Failed to create sandbox: {str(e)}"
        finally:
            self.is_loading = False
    
    async def refresh_sandboxes(self):
        """Refresh sandbox list."""
        if not self.grainchain_instance:
            return
        
        try:
            sandbox_list = []
            for provider_name in ["local", "e2b", "daytona", "morph", "modal"]:
                try:
                    provider = await self.grainchain_instance.get_provider(provider_name)
                    if provider:
                        sandbox_ids = await provider.list_sandboxes()
                        for sandbox_id in sandbox_ids:
                            status = await provider.get_sandbox_status(sandbox_id)
                            sandbox_list.append({
                                "id": sandbox_id,
                                "provider": provider_name,
                                "status": status.value,
                                "created": datetime.now().isoformat()
                            })
                except Exception:
                    continue
            
            self.sandboxes = sandbox_list
            self.total_sandboxes = len(sandbox_list)
            self.active_sandboxes = len([s for s in sandbox_list if s["status"] == "running"])
            
        except Exception as e:
            self.error_message = f"Failed to refresh sandboxes: {str(e)}"
    
    async def execute_command(self, command: str):
        """Execute command in active sandbox."""
        if not self.active_sandbox_session:
            self.error_message = "No active sandbox"
            return
        
        try:
            self.is_loading = True
            self.command_history.append(command)
            self.terminal_output += f"$ {command}\n"
            
            result = await self.active_sandbox_session.execute(command)
            
            self.terminal_output += result.output + "\n"
            self.commands_executed += 1
            self.command_input = ""
            
            if result.failed:
                self.error_message = f"Command failed with return code {result.return_code}"
            
        except Exception as e:
            self.error_message = f"Failed to execute command: {str(e)}"
            self.terminal_output += f"Error: {str(e)}\n"
        finally:
            self.is_loading = False
    
    async def create_snapshot(self, name: str = ""):
        """Create snapshot of active sandbox."""
        if not self.active_sandbox_session:
            self.error_message = "No active sandbox"
            return
        
        try:
            self.is_loading = True
            snapshot_id = await self.active_sandbox_session.create_snapshot()
            
            snapshot_info = {
                "id": snapshot_id,
                "name": name or f"Snapshot {len(self.snapshots) + 1}",
                "sandbox_id": self.active_sandbox_id,
                "created": datetime.now().isoformat(),
                "size": "Unknown"
            }
            
            self.snapshots.append(snapshot_info)
            self.total_snapshots = len(self.snapshots)
            self.success_message = f"Snapshot created: {snapshot_id}"
            
        except Exception as e:
            self.error_message = f"Failed to create snapshot: {str(e)}"
        finally:
            self.is_loading = False
    
    async def restore_snapshot(self, snapshot_id: str):
        """Restore sandbox from snapshot."""
        if not self.active_sandbox_session:
            self.error_message = "No active sandbox"
            return
        
        try:
            self.is_loading = True
            await self.active_sandbox_session.restore_snapshot(snapshot_id)
            self.success_message = f"Restored from snapshot: {snapshot_id}"
            await self.refresh_files()
            
        except Exception as e:
            self.error_message = f"Failed to restore snapshot: {str(e)}"
        finally:
            self.is_loading = False
    
    async def refresh_files(self, path: str = "/"):
        """Refresh file list."""
        if not self.active_sandbox_session:
            return
        
        try:
            file_list = await self.active_sandbox_session.list_files(path)
            self.files = [
                {
                    "name": f.name,
                    "path": f.path,
                    "size": f.size,
                    "is_directory": f.is_directory,
                    "modified": datetime.fromtimestamp(f.modified_time).isoformat(),
                    "permissions": f.permissions
                }
                for f in file_list
            ]
        except Exception as e:
            self.error_message = f"Failed to refresh files: {str(e)}"
    
    async def upload_file(self, path: str, content: str):
        """Upload file to sandbox."""
        if not self.active_sandbox_session:
            self.error_message = "No active sandbox"
            return
        
        try:
            self.is_loading = True
            await self.active_sandbox_session.upload_file(path, content)
            await self.refresh_files()
            self.success_message = f"File uploaded: {path}"
            
        except Exception as e:
            self.error_message = f"Failed to upload file: {str(e)}"
        finally:
            self.is_loading = False
    
    async def download_file(self, path: str):
        """Download file from sandbox."""
        if not self.active_sandbox_session:
            self.error_message = "No active sandbox"
            return
        
        try:
            content = await self.active_sandbox_session.download_file(path)
            # In a real implementation, this would trigger a download
            self.success_message = f"File downloaded: {path}"
            return content
            
        except Exception as e:
            self.error_message = f"Failed to download file: {str(e)}"
    
    def set_page(self, page: str):
        """Set current page."""
        self.current_page = page
        self.error_message = ""
        self.success_message = ""
    
    def set_command_input(self, value: str):
        """Set command input."""
        self.command_input = value
    
    def clear_messages(self):
        """Clear status messages."""
        self.error_message = ""
        self.success_message = ""

# UI Components
def navbar():
    """Navigation bar."""
    return rx.hstack(
        rx.heading("🌾 Grainchain Dashboard", size="6", color="white"),
        rx.spacer(),
        rx.hstack(
            rx.button(
                "Dashboard", 
                on_click=DashboardState.set_page("dashboard"),
                variant="soft" if DashboardState.current_page == "dashboard" else "ghost",
                color="white"
            ),
            rx.button(
                "Providers", 
                on_click=DashboardState.set_page("providers"),
                variant="soft" if DashboardState.current_page == "providers" else "ghost",
                color="white"
            ),
            rx.button(
                "Terminal", 
                on_click=DashboardState.set_page("terminal"),
                variant="soft" if DashboardState.current_page == "terminal" else "ghost",
                color="white"
            ),
            rx.button(
                "Files", 
                on_click=DashboardState.set_page("files"),
                variant="soft" if DashboardState.current_page == "files" else "ghost",
                color="white"
            ),
            rx.button(
                "Snapshots", 
                on_click=DashboardState.set_page("snapshots"),
                variant="soft" if DashboardState.current_page == "snapshots" else "ghost",
                color="white"
            ),
            spacing="4",
        ),
        width="100%",
        padding="1rem",
        background="linear-gradient(90deg, #1a1a2e, #16213e)",
        align="center",
    )

def status_messages():
    """Status message display."""
    return rx.vstack(
        rx.cond(
            DashboardState.error_message != "",
            rx.callout(
                DashboardState.error_message,
                icon="alert-triangle",
                color_scheme="red",
                size="2"
            )
        ),
        rx.cond(
            DashboardState.success_message != "",
            rx.callout(
                DashboardState.success_message,
                icon="check",
                color_scheme="green",
                size="2"
            )
        ),
        width="100%",
        spacing="2"
    )

def dashboard_page():
    """Dashboard overview page."""
    return rx.vstack(
        rx.heading("📊 Dashboard Overview", size="7", color="white", margin_bottom="2rem"),
        
        # Statistics cards
        rx.hstack(
            rx.card(
                rx.vstack(
                    rx.heading(DashboardState.active_sandboxes, size="6", color="green"),
                    rx.text("Active Sandboxes", size="3", color="gray"),
                    align="center",
                    spacing="1"
                ),
                padding="1.5rem",
                min_width="150px"
            ),
            rx.card(
                rx.vstack(
                    rx.heading(DashboardState.total_sandboxes, size="6", color="blue"),
                    rx.text("Total Sandboxes", size="3", color="gray"),
                    align="center",
                    spacing="1"
                ),
                padding="1.5rem",
                min_width="150px"
            ),
            rx.card(
                rx.vstack(
                    rx.heading(DashboardState.total_snapshots, size="6", color="purple"),
                    rx.text("Snapshots", size="3", color="gray"),
                    align="center",
                    spacing="1"
                ),
                padding="1.5rem",
                min_width="150px"
            ),
            rx.card(
                rx.vstack(
                    rx.heading(DashboardState.commands_executed, size="6", color="orange"),
                    rx.text("Commands Run", size="3", color="gray"),
                    align="center",
                    spacing="1"
                ),
                padding="1.5rem",
                min_width="150px"
            ),
            spacing="4",
            wrap="wrap"
        ),
        
        # Quick actions
        rx.card(
            rx.vstack(
                rx.heading("🚀 Quick Actions", size="5", margin_bottom="1rem"),
                rx.hstack(
                    rx.button(
                        "Initialize Grainchain",
                        on_click=DashboardState.initialize_grainchain,
                        loading=DashboardState.is_loading,
                        size="3"
                    ),
                    rx.button(
                        "Refresh Data",
                        on_click=DashboardState.refresh_sandboxes,
                        variant="soft",
                        size="3"
                    ),
                    spacing="3"
                ),
                align="start",
                spacing="3"
            ),
            padding="2rem",
            margin_top="2rem"
        ),
        
        # Recent activity
        rx.card(
            rx.vstack(
                rx.heading("📈 Recent Activity", size="5", margin_bottom="1rem"),
                rx.cond(
                    DashboardState.sandboxes.length() > 0,
                    rx.vstack(
                        rx.foreach(
                            DashboardState.sandboxes,
                            lambda sandbox: rx.hstack(
                                rx.badge(sandbox["status"], color_scheme="green" if sandbox["status"] == "running" else "gray"),
                                rx.text(f"{sandbox['provider']}: {sandbox['id']}", size="2"),
                                rx.spacer(),
                                rx.text(sandbox["created"], size="1", color="gray"),
                                width="100%",
                                align="center"
                            )
                        ),
                        spacing="2"
                    ),
                    rx.text("No sandboxes found. Create one to get started!", color="gray")
                ),
                align="start",
                spacing="3"
            ),
            padding="2rem",
            margin_top="2rem"
        ),
        
        width="100%",
        spacing="4",
        padding="2rem"
    )

def providers_page():
    """Providers management page."""
    return rx.vstack(
        rx.heading("🔌 Sandbox Providers", size="7", color="white", margin_bottom="2rem"),
        rx.text("Configure and manage your sandbox providers", size="4", color="gray", margin_bottom="2rem"),
        
        # Provider grid
        rx.grid(
            rx.foreach(
                DashboardState.providers,
                lambda provider: rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.heading(provider["name"], size="4"),
                            rx.spacer(),
                            rx.badge(
                                provider["status"],
                                color_scheme="green" if provider["status"] == "available" else "red"
                            ),
                            width="100%",
                            align="center"
                        ),
                        rx.text(provider["description"], size="2", color="gray"),
                        rx.button(
                            "Create Sandbox",
                            on_click=lambda p=provider: DashboardState.create_sandbox(p["name"]),
                            disabled=provider["status"] != "available",
                            size="2",
                            width="100%"
                        ),
                        align="start",
                        spacing="3"
                    ),
                    padding="1.5rem"
                )
            ),
            columns="2",
            spacing="4",
            width="100%"
        ),
        
        width="100%",
        spacing="4",
        padding="2rem"
    )

def terminal_page():
    """Interactive terminal page."""
    return rx.vstack(
        rx.heading("💻 Interactive Terminal", size="7", color="white", margin_bottom="2rem"),
        
        rx.cond(
            DashboardState.active_sandbox_id,
            rx.text(f"Active Sandbox: {DashboardState.active_sandbox_id}", size="3", color="green"),
            rx.text("No active sandbox. Create one from the Providers page.", size="3", color="red")
        ),
        
        # Terminal output
        rx.card(
            rx.scroll_area(
                rx.text(
                    DashboardState.terminal_output,
                    font_family="monospace",
                    font_size="14px",
                    white_space="pre-wrap",
                    color="green"
                ),
                height="400px",
                width="100%"
            ),
            padding="1rem",
            background="black",
            margin_bottom="1rem"
        ),
        
        # Command input
        rx.hstack(
            rx.text("$", font_family="monospace", color="green"),
            rx.input(
                placeholder="Enter command...",
                value=DashboardState.command_input,
                on_change=DashboardState.set_command_input,
                font_family="monospace",
                flex="1"
            ),
            rx.button(
                "Execute",
                on_click=lambda: DashboardState.execute_command(DashboardState.command_input),
                loading=DashboardState.is_loading,
                disabled=DashboardState.active_sandbox_id == None
            ),
            width="100%",
            spacing="2"
        ),
        
        width="100%",
        spacing="4",
        padding="2rem"
    )

def files_page():
    """File management page."""
    return rx.vstack(
        rx.heading("📁 File Manager", size="7", color="white", margin_bottom="2rem"),
        
        rx.hstack(
            rx.button(
                "Refresh Files",
                on_click=DashboardState.refresh_files,
                loading=DashboardState.is_loading
            ),
            rx.button(
                "Upload File",
                variant="soft"
            ),
            spacing="3"
        ),
        
        # File list
        rx.card(
            rx.vstack(
                rx.cond(
                    DashboardState.files.length() > 0,
                    rx.vstack(
                        rx.foreach(
                            DashboardState.files,
                            lambda file: rx.hstack(
                                rx.icon("folder" if file["is_directory"] else "file"),
                                rx.text(file["name"], font_weight="bold"),
                                rx.spacer(),
                                rx.text(f"{file['size']} bytes" if not file["is_directory"] else "", size="2", color="gray"),
                                rx.text(file["modified"], size="1", color="gray"),
                                width="100%",
                                align="center"
                            )
                        ),
                        spacing="2"
                    ),
                    rx.text("No files found or no active sandbox.", color="gray")
                ),
                align="start",
                spacing="3"
            ),
            padding="2rem"
        ),
        
        width="100%",
        spacing="4",
        padding="2rem"
    )

def snapshots_page():
    """Snapshot management page."""
    return rx.vstack(
        rx.heading("📸 Snapshot Manager", size="7", color="white", margin_bottom="2rem"),
        
        rx.hstack(
            rx.button(
                "Create Snapshot",
                on_click=DashboardState.create_snapshot,
                loading=DashboardState.is_loading,
                disabled=DashboardState.active_sandbox_id == None
            ),
            spacing="3"
        ),
        
        # Snapshots list
        rx.card(
            rx.vstack(
                rx.cond(
                    DashboardState.snapshots.length() > 0,
                    rx.vstack(
                        rx.foreach(
                            DashboardState.snapshots,
                            lambda snapshot: rx.hstack(
                                rx.vstack(
                                    rx.text(snapshot["name"], font_weight="bold"),
                                    rx.text(f"ID: {snapshot['id']}", size="1", color="gray"),
                                    align="start",
                                    spacing="1"
                                ),
                                rx.spacer(),
                                rx.text(snapshot["created"], size="2", color="gray"),
                                rx.button(
                                    "Restore",
                                    on_click=lambda s=snapshot: DashboardState.restore_snapshot(s["id"]),
                                    size="1",
                                    variant="soft"
                                ),
                                width="100%",
                                align="center"
                            )
                        ),
                        spacing="3"
                    ),
                    rx.text("No snapshots found. Create one to get started!", color="gray")
                ),
                align="start",
                spacing="3"
            ),
            padding="2rem"
        ),
        
        width="100%",
        spacing="4",
        padding="2rem"
    )

def main_content():
    """Main content area based on current page."""
    return rx.cond(
        DashboardState.current_page == "dashboard",
        dashboard_page(),
        rx.cond(
            DashboardState.current_page == "providers",
            providers_page(),
            rx.cond(
                DashboardState.current_page == "terminal",
                terminal_page(),
                rx.cond(
                    DashboardState.current_page == "files",
                    files_page(),
                    rx.cond(
                        DashboardState.current_page == "snapshots",
                        snapshots_page(),
                        dashboard_page()  # Default fallback
                    )
                )
            )
        )
    )

def index():
    """Main application layout."""
    return rx.vstack(
        navbar(),
        status_messages(),
        main_content(),
        width="100%",
        min_height="100vh",
        background="linear-gradient(135deg, #0f0f23, #1a1a2e, #16213e)",
        spacing="0"
    )

# Create the app
app = rx.App(
    theme=rx.theme(
        appearance="dark",
        has_background=True,
        radius="large",
        scaling="100%"
    )
)

app.add_page(index, route="/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
