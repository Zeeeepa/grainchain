"""Working Dashboard - Part 2: Additional page components."""

import reflex as rx
from typing import Dict, List, Optional, Any

# Continue from working_main.py - these are the remaining page components

def providers_content() -> rx.Component:
    """Providers page content with interactive configuration."""
    return rx.vstack(
        rx.heading("🔌 Sandbox Providers", size="6"),
        rx.text("Configure and manage your sandbox providers", size="3", color="gray"),
        
        rx.grid(
            rx.foreach(
                WorkingDashboardState.providers,
                lambda provider_name, provider_data: rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.text("🏠" if provider_name == "local" else "☁️", size="5"),
                            rx.heading(provider_data["name"], size="4"),
                            status_badge(provider_data["status"]),
                            justify="between", width="100%"
                        ),
                        rx.text(provider_data["description"], size="2", color="gray"),
                        rx.text(f"API Key: {'✅ Configured' if provider_data['has_api_key'] else '❌ Missing'}", size="2"),
                        rx.button(
                            "Configure", 
                            size="2", 
                            variant="soft",
                            on_click=lambda p=provider_name: WorkingDashboardState.open_provider_modal(p)
                        ),
                        spacing="3", align="start"
                    ),
                    style={"padding": "1.5rem", "min_height": "180px"}
                )
            ),
            columns="2", spacing="4", width="100%"
        ),
        
        spacing="6",
        style={"padding": "2rem", "max_width": "1200px", "margin": "0 auto"}
    )

def terminal_content() -> rx.Component:
    """Interactive terminal page."""
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
                        WorkingDashboardState.command_output,
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
                    style={"width": "100%", "min_height": "400px", "overflow": "auto"}
                ),
                
                rx.divider(),
                
                rx.hstack(
                    rx.text("$", size="3", weight="bold", color="green"),
                    rx.input(
                        placeholder="Enter command...", 
                        value=WorkingDashboardState.current_command,
                        on_change=WorkingDashboardState.set_current_command,
                        on_key_down=lambda key: rx.cond(
                            key == "Enter",
                            WorkingDashboardState.execute_command,
                            rx.noop
                        ),
                        style={"flex": "1", "font_family": "monospace"}
                    ),
                    rx.button(
                        "Execute", 
                        color_scheme="blue",
                        on_click=WorkingDashboardState.execute_command
                    ),
                    spacing="3", width="100%"
                ),
                
                # Command history
                rx.details.root(
                    rx.details.trigger(
                        rx.hstack(
                            rx.icon("history", size=16),
                            rx.text("Command History", size="2"),
                            spacing="2"
                        )
                    ),
                    rx.details.content(
                        rx.vstack(
                            rx.foreach(
                                WorkingDashboardState.command_history[-10:],  # Last 10 commands
                                lambda cmd: rx.button(
                                    cmd,
                                    variant="ghost",
                                    size="1",
                                    on_click=lambda c=cmd: WorkingDashboardState.set_current_command(c),
                                    style={"font_family": "monospace", "width": "100%", "justify_content": "flex_start"}
                                )
                            ),
                            spacing="1", width="100%"
                        )
                    )
                ),
                
                spacing="4", width="100%"
            ),
            style={"padding": "1.5rem"}
        ),
        
        spacing="6",
        style={"padding": "2rem", "max_width": "1200px", "margin": "0 auto"}
    )

def files_content() -> rx.Component:
    """File management page."""
    return rx.vstack(
        rx.heading("📁 File Manager", size="6"),
        rx.text("Browse, upload, and manage sandbox files", size="3", color="gray"),
        
        rx.hstack(
            rx.button(
                rx.hstack(rx.icon("upload", size=16), rx.text("Upload"), spacing="2"), 
                color_scheme="blue",
                on_click=WorkingDashboardState.open_file_upload_modal
            ),
            rx.button(
                rx.hstack(rx.icon("folder-plus", size=16), rx.text("New Folder"), spacing="2"), 
                variant="soft"
            ),
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
                        WorkingDashboardState.files,
                        lambda file: rx.table.row(
                            rx.table.cell(
                                rx.hstack(
                                    rx.icon("folder" if file["type"] == "directory" else "file", size=16),
                                    rx.text(file["name"]),
                                    spacing="2"
                                )
                            ),
                            rx.table.cell(
                                rx.cond(
                                    file["type"] == "file",
                                    f"{file['size']} bytes",
                                    "-"
                                )
                            ),
                            rx.table.cell(file["modified"]),
                            rx.table.cell(
                                rx.hstack(
                                    rx.button(
                                        rx.icon("download", size=14), 
                                        size="1", 
                                        variant="ghost",
                                        title="Download"
                                    ),
                                    rx.button(
                                        rx.icon("edit", size=14), 
                                        size="1", 
                                        variant="ghost",
                                        title="Edit"
                                    ),
                                    rx.button(
                                        rx.icon("trash", size=14), 
                                        size="1", 
                                        variant="ghost", 
                                        color_scheme="red",
                                        title="Delete",
                                        on_click=lambda p=file["path"]: WorkingDashboardState.delete_file(p)
                                    ),
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
    """Snapshot management page."""
    return rx.vstack(
        rx.heading("📸 Snapshot Manager", size="6"),
        rx.text("Create, restore, and manage sandbox snapshots", size="3", color="gray"),
        
        rx.hstack(
            rx.button(
                rx.hstack(rx.icon("plus", size=16), rx.text("Create Snapshot"), spacing="2"), 
                color_scheme="blue",
                on_click=WorkingDashboardState.open_snapshot_modal
            ),
            rx.button(
                rx.hstack(rx.icon("download", size=16), rx.text("Import"), spacing="2"), 
                variant="soft"
            ),
            spacing="3"
        ),
        
        rx.grid(
            rx.foreach(
                WorkingDashboardState.snapshots,
                lambda snapshot: rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.text("📸", size="5"),
                            rx.heading(snapshot["name"], size="4"),
                            status_badge(snapshot["status"]),
                            justify="between", width="100%"
                        ),
                        rx.text(f"Size: {snapshot['size']}", size="2", color="gray"),
                        rx.text(f"Files: {snapshot['files_count']}", size="2", color="gray"),
                        rx.text(f"Created: {snapshot['created']}", size="2", color="gray"),
                        rx.hstack(
                            rx.button("Restore", size="2", color_scheme="blue"),
                            rx.button("Export", size="2", variant="soft"),
                            rx.button(
                                "Delete", 
                                size="2", 
                                variant="soft", 
                                color_scheme="red",
                                on_click=lambda s_id=snapshot["id"]: WorkingDashboardState.delete_snapshot(s_id)
                            ),
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
    """Settings and configuration page."""
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
                            rx.select(
                                ["Light", "Dark"], 
                                value=WorkingDashboardState.theme.title(),
                                on_change=lambda v: WorkingDashboardState.set_theme(v.lower())
                            ),
                            spacing="3", width="100%", justify="between"
                        ),
                        rx.hstack(
                            rx.text("Default Provider:", size="2", weight="medium"),
                            rx.select(
                                ["Local", "E2B", "Daytona", "Morph", "Modal"], 
                                value=WorkingDashboardState.default_provider.title(),
                                on_change=lambda v: WorkingDashboardState.set_default_provider(v.lower())
                            ),
                            spacing="3", width="100%", justify="between"
                        ),
                        rx.hstack(
                            rx.text("Notifications:", size="2", weight="medium"),
                            rx.switch(
                                checked=WorkingDashboardState.notifications_enabled,
                                on_change=WorkingDashboardState.set_notifications_enabled
                            ),
                            spacing="3", width="100%", justify="between"
                        ),
                        rx.hstack(
                            rx.text("Auto-save:", size="2", weight="medium"),
                            rx.switch(
                                checked=WorkingDashboardState.auto_save_enabled,
                                on_change=WorkingDashboardState.set_auto_save_enabled
                            ),
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
                        rx.hstack(
                            rx.text("Command History Limit:", size="2", weight="medium"),
                            rx.number_input(
                                value=WorkingDashboardState.command_history_limit,
                                on_change=WorkingDashboardState.set_command_history_limit,
                                min=10, max=1000, step=10
                            ),
                            spacing="3", width="100%", justify="between"
                        ),
                        rx.divider(),
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
