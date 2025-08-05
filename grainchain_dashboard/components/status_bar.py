"""Status bar and notification components."""

import reflex as rx

def notification_toast() -> rx.Component:
    """Toast notification for success/error messages."""
    from ..state import DashboardState
    
    return rx.cond(
        DashboardState.success_message | DashboardState.error_message,
        rx.box(
            rx.card(
                rx.hstack(
                    rx.cond(
                        DashboardState.success_message,
                        rx.icon("check-circle", size=20, color="green"),
                        rx.icon("alert-circle", size=20, color="red")
                    ),
                    rx.vstack(
                        rx.text(
                            rx.cond(
                                DashboardState.success_message,
                                DashboardState.success_message,
                                DashboardState.error_message
                            ),
                            size="2",
                            weight="medium"
                        ),
                        spacing="0",
                        align="start"
                    ),
                    rx.button(
                        rx.icon("x", size=16),
                        on_click=DashboardState.clear_messages,
                        variant="ghost",
                        size="1"
                    ),
                    spacing="3",
                    align="center",
                    width="100%"
                ),
                variant="surface",
                style={
                    "border_left": f"4px solid {'var(--green-9)' if DashboardState.success_message else 'var(--red-9)'}",
                    "max_width": "400px"
                }
            ),
            style={
                "position": "fixed",
                "top": "1rem",
                "right": "1rem",
                "z_index": "1000",
                "animation": "slideInRight 0.3s ease-out"
            }
        )
    )

def loading_overlay() -> rx.Component:
    """Loading overlay for long operations."""
    from ..state import DashboardState
    
    return rx.cond(
        DashboardState.loading,
        rx.box(
            rx.card(
                rx.vstack(
                    rx.spinner(size="6"),
                    rx.text("Processing...", size="3", weight="medium"),
                    spacing="3",
                    align="center"
                ),
                variant="surface",
                style={
                    "padding": "2rem",
                    "border": "1px solid var(--gray-6)",
                    "box_shadow": "var(--shadow-5)"
                }
            ),
            style={
                "position": "fixed",
                "top": "0",
                "left": "0",
                "right": "0",
                "bottom": "0",
                "background": "rgba(0, 0, 0, 0.5)",
                "display": "flex",
                "align_items": "center",
                "justify_content": "center",
                "z_index": "9999"
            }
        )
    )

def status_bar() -> rx.Component:
    """Bottom status bar showing system information."""
    from ..state import DashboardState
    
    return rx.box(
        rx.hstack(
            # Left side - System status
            rx.hstack(
                rx.text("Grainchain Dashboard", size="1", weight="bold"),
                rx.text("•", size="1", color="gray"),
                rx.text(
                    f"{len(DashboardState.active_sandboxes)} active sandboxes",
                    size="1",
                    color="gray"
                ),
                rx.text("•", size="1", color="gray"),
                rx.text(
                    f"{len([p for p in DashboardState.provider_health_status.values() if p == 'healthy'])} providers online",
                    size="1",
                    color="gray"
                ),
                spacing="2",
                align="center"
            ),
            
            # Right side - Current status
            rx.hstack(
                rx.cond(
                    DashboardState.command_running,
                    rx.hstack(
                        rx.spinner(size="3"),
                        rx.text("Executing command...", size="1", color="blue"),
                        spacing="2"
                    )
                ),
                rx.cond(
                    DashboardState.selected_sandbox_id,
                    rx.hstack(
                        rx.circle(size="1", color_scheme="green"),
                        rx.text(
                            f"Sandbox: {DashboardState.selected_sandbox_id[:8]}...",
                            size="1",
                            style={"font_family": "monospace"}
                        ),
                        spacing="2"
                    ),
                    rx.hstack(
                        rx.circle(size="1", color_scheme="gray"),
                        rx.text("No sandbox selected", size="1", color="gray"),
                        spacing="2"
                    )
                ),
                spacing="4",
                align="center"
            ),
            
            justify="between",
            width="100%",
            align="center"
        ),
        style={
            "position": "fixed",
            "bottom": "0",
            "left": "0",
            "right": "0",
            "height": "32px",
            "background": "var(--gray-2)",
            "border_top": "1px solid var(--gray-6)",
            "padding": "0 1rem",
            "z_index": "100"
        }
    )

def connection_status() -> rx.Component:
    """Connection status indicator."""
    from ..state import DashboardState
    
    # Count healthy providers
    healthy_count = len([
        status for status in DashboardState.provider_health_status.values() 
        if status == "healthy"
    ])
    total_count = len(DashboardState.provider_health_status)
    
    return rx.card(
        rx.hstack(
            rx.cond(
                healthy_count > 0,
                rx.icon("wifi", size=16, color="green"),
                rx.icon("wifi-off", size=16, color="red")
            ),
            rx.vstack(
                rx.text(
                    "Connection Status",
                    size="1",
                    weight="bold",
                    color="gray"
                ),
                rx.text(
                    f"{healthy_count}/{total_count} providers online",
                    size="2"
                ),
                spacing="0",
                align="start"
            ),
            spacing="3",
            align="center"
        ),
        variant="surface",
        style={"padding": "0.75rem"}
    )

def system_metrics() -> rx.Component:
    """System metrics display."""
    from ..state import DashboardState
    
    return rx.card(
        rx.vstack(
            rx.text("System Metrics", size="2", weight="bold"),
            rx.divider(),
            rx.grid(
                rx.vstack(
                    rx.text("Active Sandboxes", size="1", color="gray"),
                    rx.text(
                        str(len(DashboardState.active_sandboxes)),
                        size="4",
                        weight="bold"
                    ),
                    spacing="1",
                    align="center"
                ),
                rx.vstack(
                    rx.text("Snapshots", size="1", color="gray"),
                    rx.text(
                        str(len(DashboardState.snapshots)),
                        size="4",
                        weight="bold"
                    ),
                    spacing="1",
                    align="center"
                ),
                rx.vstack(
                    rx.text("Commands Run", size="1", color="gray"),
                    rx.text(
                        str(len(DashboardState.command_history)),
                        size="4",
                        weight="bold"
                    ),
                    spacing="1",
                    align="center"
                ),
                columns="3",
                spacing="4",
                width="100%"
            ),
            spacing="3",
            width="100%"
        ),
        variant="surface"
    )

def quick_stats() -> rx.Component:
    """Quick statistics panel."""
    from ..state import DashboardState
    
    return rx.hstack(
        rx.card(
            rx.hstack(
                rx.icon("server", size=20, color="blue"),
                rx.vstack(
                    rx.text(
                        str(len(DashboardState.active_sandboxes)),
                        size="4",
                        weight="bold"
                    ),
                    rx.text("Active Sandboxes", size="1", color="gray"),
                    spacing="0",
                    align="start"
                ),
                spacing="3",
                align="center"
            ),
            variant="surface",
            style={"padding": "1rem", "min_width": "150px"}
        ),
        rx.card(
            rx.hstack(
                rx.icon("camera", size=20, color="green"),
                rx.vstack(
                    rx.text(
                        str(len(DashboardState.snapshots)),
                        size="4",
                        weight="bold"
                    ),
                    rx.text("Snapshots", size="1", color="gray"),
                    spacing="0",
                    align="start"
                ),
                spacing="3",
                align="center"
            ),
            variant="surface",
            style={"padding": "1rem", "min_width": "150px"}
        ),
        rx.card(
            rx.hstack(
                rx.icon("terminal", size=20, color="purple"),
                rx.vstack(
                    rx.text(
                        str(len(DashboardState.command_history)),
                        size="4",
                        weight="bold"
                    ),
                    rx.text("Commands", size="1", color="gray"),
                    spacing="0",
                    align="start"
                ),
                spacing="3",
                align="center"
            ),
            variant="surface",
            style={"padding": "1rem", "min_width": "150px"}
        ),
        spacing="4"
    )

