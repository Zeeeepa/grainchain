"""Main dashboard page with overview and quick actions."""

import reflex as rx
from ..components.provider_selector import provider_grid, provider_status_panel
from ..components.status_bar import quick_stats, system_metrics, connection_status
from ..components.snapshot_manager import snapshot_quick_actions
from ..components.file_browser import file_quick_actions, directory_tree

def sandbox_overview() -> rx.Component:
    """Overview of active sandboxes."""
    from ..state import DashboardState
    
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading("Active Sandboxes", size="4"),
                rx.button(
                    rx.icon("plus", size=16),
                    "Create Sandbox",
                    on_click=DashboardState.create_sandbox,
                    loading=DashboardState.loading,
                    size="2"
                ),
                justify="between",
                width="100%"
            ),
            rx.divider(),
            rx.cond(
                DashboardState.active_sandboxes,
                rx.vstack(
                    rx.foreach(
                        DashboardState.active_sandboxes,
                        lambda sandbox: rx.card(
                            rx.hstack(
                                rx.vstack(
                                    rx.hstack(
                                        rx.text(
                                            f"Sandbox {sandbox['sandbox_id'][:8]}...",
                                            weight="bold",
                                            size="3",
                                            style={"font_family": "monospace"}
                                        ),
                                        rx.badge(
                                            sandbox["provider"].title(),
                                            variant="soft"
                                        ),
                                        spacing="2"
                                    ),
                                    rx.text(
                                        f"Created: {sandbox['created_at']}",
                                        size="2",
                                        color="gray"
                                    ),
                                    rx.text(
                                        f"Last activity: {sandbox['last_activity']}",
                                        size="2",
                                        color="gray"
                                    ),
                                    align="start",
                                    spacing="1"
                                ),
                                rx.vstack(
                                    rx.badge(
                                        sandbox["status"].title(),
                                        color_scheme="green" if sandbox["status"] == "running" else "gray"
                                    ),
                                    rx.hstack(
                                        rx.button(
                                            "Select",
                                            on_click=lambda sid=sandbox['sandbox_id']: DashboardState.select_sandbox(sid),
                                            variant="soft",
                                            size="2"
                                        ),
                                        rx.button(
                                            rx.icon("x", size=14),
                                            on_click=lambda sid=sandbox['sandbox_id']: DashboardState.close_sandbox(sid),
                                            variant="soft",
                                            color_scheme="red",
                                            size="2"
                                        ),
                                        spacing="2"
                                    ),
                                    spacing="2",
                                    align="end"
                                ),
                                justify="between",
                                width="100%",
                                align="center"
                            ),
                            variant="surface"
                        )
                    ),
                    spacing="3",
                    width="100%"
                ),
                rx.text(
                    "No active sandboxes. Create one to get started!",
                    size="2",
                    color="gray",
                    style={"text_align": "center", "padding": "2rem"}
                )
            ),
            spacing="4",
            width="100%"
        ),
        variant="surface"
    )

def recent_activity() -> rx.Component:
    """Recent activity feed."""
    from ..state import DashboardState
    
    # Mock recent activities - in real implementation, this would come from a service
    activities = [
        {"type": "sandbox_created", "message": "Sandbox created with E2B provider", "time": "2 minutes ago"},
        {"type": "command_executed", "message": "Executed: pip install requests", "time": "5 minutes ago"},
        {"type": "snapshot_created", "message": "Snapshot created: Initial setup", "time": "10 minutes ago"},
        {"type": "file_uploaded", "message": "Uploaded: main.py", "time": "15 minutes ago"},
    ]
    
    activity_icons = {
        "sandbox_created": ("server", "blue"),
        "command_executed": ("terminal", "green"),
        "snapshot_created": ("camera", "purple"),
        "file_uploaded": ("upload", "orange")
    }
    
    return rx.card(
        rx.vstack(
            rx.heading("Recent Activity", size="4"),
            rx.divider(),
            rx.vstack(
                *[
                    rx.hstack(
                        rx.icon(
                            activity_icons.get(activity["type"], ("activity", "gray"))[0],
                            size=16,
                            color=activity_icons.get(activity["type"], ("activity", "gray"))[1]
                        ),
                        rx.vstack(
                            rx.text(activity["message"], size="2"),
                            rx.text(activity["time"], size="1", color="gray"),
                            spacing="0",
                            align="start"
                        ),
                        spacing="3",
                        align="center",
                        width="100%"
                    )
                    for activity in activities
                ],
                spacing="3",
                width="100%"
            ),
            spacing="4",
            width="100%"
        ),
        variant="surface"
    )

def quick_actions_panel() -> rx.Component:
    """Quick actions for common tasks."""
    from ..state import DashboardState
    
    return rx.card(
        rx.vstack(
            rx.heading("Quick Actions", size="4"),
            rx.divider(),
            rx.grid(
                rx.button(
                    rx.vstack(
                        rx.icon("plus", size=24),
                        rx.text("Create Sandbox", size="2", weight="medium"),
                        spacing="2",
                        align="center"
                    ),
                    on_click=DashboardState.create_sandbox,
                    loading=DashboardState.loading,
                    variant="soft",
                    style={"height": "80px", "width": "100%"}
                ),
                rx.button(
                    rx.vstack(
                        rx.icon("terminal", size=24),
                        rx.text("Open Terminal", size="2", weight="medium"),
                        spacing="2",
                        align="center"
                    ),
                    on_click=lambda: DashboardState.set_page("terminal"),
                    variant="soft",
                    style={"height": "80px", "width": "100%"}
                ),
                rx.button(
                    rx.vstack(
                        rx.icon("folder", size=24),
                        rx.text("Browse Files", size="2", weight="medium"),
                        spacing="2",
                        align="center"
                    ),
                    on_click=lambda: DashboardState.set_page("files"),
                    variant="soft",
                    style={"height": "80px", "width": "100%"}
                ),
                rx.button(
                    rx.vstack(
                        rx.icon("camera", size=24),
                        rx.text("Manage Snapshots", size="2", weight="medium"),
                        spacing="2",
                        align="center"
                    ),
                    on_click=lambda: DashboardState.set_page("snapshots"),
                    variant="soft",
                    style={"height": "80px", "width": "100%"}
                ),
                columns="2",
                spacing="3",
                width="100%"
            ),
            spacing="4",
            width="100%"
        ),
        variant="surface"
    )

def welcome_banner() -> rx.Component:
    """Welcome banner for new users."""
    from ..state import DashboardState
    
    return rx.cond(
        ~DashboardState.active_sandboxes,
        rx.card(
            rx.hstack(
                rx.vstack(
                    rx.heading("Welcome to Grainchain Dashboard! 🚀", size="5"),
                    rx.text(
                        "Get started by selecting a provider and creating your first sandbox.",
                        size="3",
                        color="gray"
                    ),
                    rx.hstack(
                        rx.button(
                            "Select Provider",
                            on_click=lambda: DashboardState.set_page("providers"),
                            size="3"
                        ),
                        rx.button(
                            "View Documentation",
                            variant="outline",
                            size="3"
                        ),
                        spacing="3"
                    ),
                    spacing="3",
                    align="start"
                ),
                rx.icon("rocket", size=64, color="blue"),
                justify="between",
                width="100%",
                align="center"
            ),
            variant="surface",
            style={
                "background": "linear-gradient(135deg, var(--blue-2), var(--purple-2))",
                "border": "1px solid var(--blue-6)"
            }
        )
    )

def dashboard_page() -> rx.Component:
    """Main dashboard page."""
    from ..state import DashboardState
    
    return rx.vstack(
        # Welcome banner (shown only when no sandboxes)
        welcome_banner(),
        
        # Quick stats
        quick_stats(),
        
        # Main content grid
        rx.grid(
            # Left column
            rx.vstack(
                sandbox_overview(),
                quick_actions_panel(),
                spacing="6",
                width="100%"
            ),
            
            # Right column
            rx.vstack(
                provider_status_panel(),
                recent_activity(),
                system_metrics(),
                spacing="6",
                width="100%"
            ),
            
            columns="2",
            spacing="6",
            width="100%"
        ),
        
        spacing="6",
        width="100%",
        style={"padding": "2rem"}
    )

