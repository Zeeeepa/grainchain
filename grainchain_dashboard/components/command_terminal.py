"""Command execution terminal component."""

import reflex as rx
from typing import List

def command_input_form() -> rx.Component:
    """Create the command input form."""
    from ..state import DashboardState
    
    return rx.form(
        rx.hstack(
            rx.text("$", size="3", weight="bold", color="green"),
            rx.input(
                placeholder="Enter command...",
                value=DashboardState.command_input,
                on_change=DashboardState.set_command_input,
                disabled=DashboardState.command_running | ~DashboardState.selected_sandbox_id,
                style={"flex": "1", "font_family": "monospace"}
            ),
            rx.button(
                rx.cond(
                    DashboardState.command_running,
                    rx.spinner(size="4"),
                    rx.icon("play", size=16)
                ),
                "Execute",
                type="submit",
                loading=DashboardState.command_running,
                disabled=~DashboardState.selected_sandbox_id
            ),
            spacing="2",
            width="100%",
            align="center"
        ),
        on_submit=DashboardState.execute_command,
        width="100%"
    )

def command_output_display() -> rx.Component:
    """Display command output with syntax highlighting."""
    from ..state import DashboardState
    
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text("Output", weight="bold", size="3"),
                rx.button(
                    rx.icon("trash-2", size=16),
                    "Clear",
                    on_click=DashboardState.clear_command_output,
                    variant="ghost",
                    size="2"
                ),
                justify="between",
                width="100%"
            ),
            rx.divider(),
            rx.cond(
                DashboardState.command_output,
                rx.code_block(
                    DashboardState.command_output,
                    language="bash",
                    style={
                        "max_height": "400px",
                        "overflow_y": "auto",
                        "width": "100%",
                        "white_space": "pre-wrap",
                        "font_size": "0.875rem"
                    }
                ),
                rx.text(
                    "No output yet. Execute a command to see results.",
                    size="2",
                    color="gray",
                    style={"text_align": "center", "padding": "2rem"}
                )
            ),
            spacing="3",
            width="100%"
        ),
        variant="surface",
        style={"min_height": "300px"}
    )

def command_history_panel() -> rx.Component:
    """Display command history."""
    from ..state import DashboardState
    
    return rx.card(
        rx.vstack(
            rx.text("Command History", weight="bold", size="3"),
            rx.divider(),
            rx.cond(
                DashboardState.command_history,
                rx.vstack(
                    rx.foreach(
                        DashboardState.command_history,
                        lambda cmd: rx.hstack(
                            rx.text(
                                cmd,
                                size="2",
                                style={"font_family": "monospace"}
                            ),
                            rx.button(
                                rx.icon("repeat", size=12),
                                on_click=lambda c=cmd: DashboardState.set_command_input(c.replace("$ ", "")),
                                variant="ghost",
                                size="1"
                            ),
                            justify="between",
                            width="100%",
                            align="center"
                        )
                    ),
                    spacing="1",
                    width="100%",
                    style={"max_height": "200px", "overflow_y": "auto"}
                ),
                rx.text(
                    "No commands executed yet",
                    size="2",
                    color="gray",
                    style={"text_align": "center", "padding": "1rem"}
                )
            ),
            spacing="3",
            width="100%"
        ),
        variant="surface"
    )

def quick_commands() -> rx.Component:
    """Quick command buttons for common operations."""
    from ..state import DashboardState
    
    common_commands = [
        ("ls -la", "List files"),
        ("pwd", "Current directory"),
        ("whoami", "Current user"),
        ("python --version", "Python version"),
        ("pip list", "Installed packages"),
        ("df -h", "Disk usage"),
        ("ps aux", "Running processes"),
        ("env", "Environment variables")
    ]
    
    return rx.card(
        rx.vstack(
            rx.text("Quick Commands", weight="bold", size="3"),
            rx.divider(),
            rx.grid(
                *[
                    rx.button(
                        description,
                        on_click=lambda cmd=command: DashboardState.set_command_input(cmd),
                        variant="soft",
                        size="2",
                        style={"justify_content": "flex-start"}
                    )
                    for command, description in common_commands
                ],
                columns="2",
                spacing="2",
                width="100%"
            ),
            spacing="3",
            width="100%"
        ),
        variant="surface"
    )

def terminal_status_bar() -> rx.Component:
    """Status bar showing current sandbox and execution state."""
    from ..state import DashboardState
    
    return rx.card(
        rx.hstack(
            rx.hstack(
                rx.icon("terminal", size=16),
                rx.text("Terminal", weight="bold", size="2"),
                spacing="2"
            ),
            rx.cond(
                DashboardState.selected_sandbox_id,
                rx.hstack(
                    rx.text("Sandbox:", size="2", color="gray"),
                    rx.text(
                        DashboardState.selected_sandbox_id[:8] + "...",
                        size="2",
                        weight="bold",
                        style={"font_family": "monospace"}
                    ),
                    rx.badge(
                        DashboardState.selected_provider.title(),
                        variant="soft",
                        size="1"
                    ),
                    spacing="2"
                ),
                rx.text("No sandbox selected", size="2", color="red")
            ),
            rx.cond(
                DashboardState.command_running,
                rx.hstack(
                    rx.spinner(size="4"),
                    rx.text("Executing...", size="2", color="blue"),
                    spacing="2"
                )
            ),
            justify="between",
            width="100%",
            align="center"
        ),
        variant="surface",
        style={"padding": "0.75rem"}
    )

def command_terminal() -> rx.Component:
    """Main terminal component."""
    from ..state import DashboardState
    
    return rx.vstack(
        terminal_status_bar(),
        rx.cond(
            DashboardState.selected_sandbox_id,
            rx.vstack(
                command_input_form(),
                rx.grid(
                    rx.box(
                        command_output_display(),
                        grid_column="span 2"
                    ),
                    command_history_panel(),
                    columns="3",
                    spacing="4",
                    width="100%"
                ),
                quick_commands(),
                spacing="4",
                width="100%"
            ),
            rx.card(
                rx.vstack(
                    rx.icon("terminal", size=48, color="gray"),
                    rx.heading("No Sandbox Selected", size="4"),
                    rx.text(
                        "Select a sandbox to start executing commands",
                        size="2",
                        color="gray"
                    ),
                    rx.button(
                        "Create Sandbox",
                        on_click=DashboardState.create_sandbox,
                        loading=DashboardState.loading
                    ),
                    spacing="3",
                    align="center"
                ),
                variant="surface",
                style={"text_align": "center", "padding": "3rem"}
            )
        ),
        spacing="4",
        width="100%"
    )

def terminal_shortcuts_help() -> rx.Component:
    """Help panel showing terminal shortcuts."""
    
    shortcuts = [
        ("Enter", "Execute command"),
        ("↑/↓", "Navigate history"),
        ("Ctrl+C", "Clear input"),
        ("Ctrl+L", "Clear output"),
        ("Tab", "Auto-complete (future)")
    ]
    
    return rx.card(
        rx.vstack(
            rx.text("Keyboard Shortcuts", weight="bold", size="2"),
            rx.divider(),
            rx.vstack(
                *[
                    rx.hstack(
                        rx.kbd(key),
                        rx.text(description, size="2"),
                        justify="between",
                        width="100%"
                    )
                    for key, description in shortcuts
                ],
                spacing="2",
                width="100%"
            ),
            spacing="3",
            width="100%"
        ),
        variant="surface"
    )

