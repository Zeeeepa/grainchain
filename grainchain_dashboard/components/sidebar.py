"""Sidebar navigation component."""

import reflex as rx

def nav_item(icon: str, label: str, page: str, is_active: bool = False) -> rx.Component:
    """Create a navigation item."""
    from ..state import DashboardState
    
    return rx.button(
        rx.hstack(
            rx.icon(icon, size=18),
            rx.text(label, size="2", weight="medium"),
            spacing="3",
            align="center"
        ),
        on_click=lambda: DashboardState.set_page(page),
        variant="ghost" if not is_active else "soft",
        color_scheme="gray" if not is_active else "blue",
        style={
            "width": "100%",
            "justify_content": "flex_start",
            "padding": "0.75rem 1rem"
        }
    )

def sandbox_status_indicator() -> rx.Component:
    """Show current sandbox status."""
    from ..state import DashboardState
    
    return rx.card(
        rx.vstack(
            rx.text("Active Sandbox", size="1", weight="bold", color="gray"),
            rx.cond(
                DashboardState.selected_sandbox_id,
                rx.vstack(
                    rx.hstack(
                        rx.circle(size="2", color_scheme="green"),
                        rx.text(
                            DashboardState.selected_sandbox_id[:8] + "...",
                            size="2",
                            weight="medium",
                            style={"font_family": "monospace"}
                        ),
                        spacing="2",
                        align="center"
                    ),
                    rx.badge(
                        DashboardState.selected_provider.title(),
                        variant="soft",
                        size="1"
                    ),
                    spacing="2",
                    align="start"
                ),
                rx.text(
                    "No sandbox active",
                    size="2",
                    color="gray"
                )
            ),
            spacing="2",
            align="start",
            width="100%"
        ),
        variant="surface",
        style={"padding": "0.75rem"}
    )

def provider_status_mini() -> rx.Component:
    """Mini provider status display."""
    from ..state import DashboardState
    
    return rx.card(
        rx.vstack(
            rx.text("Providers", size="1", weight="bold", color="gray"),
            rx.hstack(
                rx.foreach(
                    DashboardState.provider_health_status,
                    lambda status_item: rx.tooltip(
                        rx.circle(
                            size="2",
                            color_scheme="green" if status_item[1] == "healthy" else "red"
                        ),
                        content=f"{status_item[0].title()}: {status_item[1].title()}"
                    )
                ),
                spacing="1",
                wrap="wrap"
            ),
            spacing="2",
            align="start",
            width="100%"
        ),
        variant="surface",
        style={"padding": "0.75rem"}
    )

def sidebar() -> rx.Component:
    """Main sidebar component."""
    from ..state import DashboardState
    
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
                nav_item("home", "Dashboard", "dashboard", DashboardState.current_page == "dashboard"),
                nav_item("server", "Providers", "providers", DashboardState.current_page == "providers"),
                nav_item("terminal", "Terminal", "terminal", DashboardState.current_page == "terminal"),
                nav_item("folder", "Files", "files", DashboardState.current_page == "files"),
                nav_item("camera", "Snapshots", "snapshots", DashboardState.current_page == "snapshots"),
                nav_item("activity", "Monitoring", "monitoring", DashboardState.current_page == "monitoring"),
                nav_item("settings", "Settings", "settings", DashboardState.current_page == "settings"),
                spacing="1",
                width="100%",
                style={"padding": "0 1rem"}
            ),
            
            rx.divider(),
            
            # Status indicators
            rx.vstack(
                sandbox_status_indicator(),
                provider_status_mini(),
                spacing="3",
                style={"padding": "0 1rem"}
            ),
            
            # Footer
            rx.spacer(),
            rx.vstack(
                rx.divider(),
                rx.hstack(
                    rx.button(
                        rx.icon("help-circle", size=16),
                        variant="ghost",
                        size="2"
                    ),
                    rx.button(
                        rx.icon("settings", size=16),
                        on_click=DashboardState.open_settings,
                        variant="ghost",
                        size="2"
                    ),
                    rx.button(
                        rx.icon(
                            "chevron-left" if DashboardState.sidebar_open else "chevron-right",
                            size=16
                        ),
                        on_click=DashboardState.toggle_sidebar,
                        variant="ghost",
                        size="2"
                    ),
                    spacing="1",
                    justify="center",
                    width="100%"
                ),
                style={"padding": "1rem"}
            ),
            
            spacing="0",
            height="100vh",
            width="100%"
        ),
        style={
            "width": "280px" if DashboardState.sidebar_open else "60px",
            "min_width": "280px" if DashboardState.sidebar_open else "60px",
            "background": "var(--gray-2)",
            "border_right": "1px solid var(--gray-6)",
            "transition": "width 0.2s ease",
            "overflow": "hidden"
        }
    )

def mobile_sidebar() -> rx.Component:
    """Mobile version of sidebar (drawer)."""
    from ..state import DashboardState
    
    return rx.drawer.root(
        rx.drawer.trigger(
            rx.button(
                rx.icon("menu", size=20),
                variant="ghost"
            )
        ),
        rx.drawer.overlay(),
        rx.drawer.content(
            rx.drawer.header(
                rx.drawer.title("Grainchain Dashboard"),
                rx.drawer.close(
                    rx.button(
                        rx.icon("x", size=16),
                        variant="ghost",
                        size="2"
                    )
                )
            ),
            rx.drawer.body(
                rx.vstack(
                    nav_item("home", "Dashboard", "dashboard", DashboardState.current_page == "dashboard"),
                    nav_item("server", "Providers", "providers", DashboardState.current_page == "providers"),
                    nav_item("terminal", "Terminal", "terminal", DashboardState.current_page == "terminal"),
                    nav_item("folder", "Files", "files", DashboardState.current_page == "files"),
                    nav_item("camera", "Snapshots", "snapshots", DashboardState.current_page == "snapshots"),
                    nav_item("activity", "Monitoring", "monitoring", DashboardState.current_page == "monitoring"),
                    nav_item("settings", "Settings", "settings", DashboardState.current_page == "settings"),
                    spacing="2",
                    width="100%"
                )
            ),
            style={"width": "280px"}
        ),
        direction="left"
    )

def compact_sidebar() -> rx.Component:
    """Compact sidebar with icons only."""
    from ..state import DashboardState
    
    return rx.box(
        rx.vstack(
            # Header
            rx.button(
                rx.icon("layers", size=20, color="blue"),
                on_click=DashboardState.toggle_sidebar,
                variant="ghost",
                style={"padding": "1rem"}
            ),
            
            rx.divider(),
            
            # Navigation icons
            rx.vstack(
                rx.tooltip(
                    rx.button(
                        rx.icon("home", size=18),
                        on_click=lambda: DashboardState.set_page("dashboard"),
                        variant="ghost" if DashboardState.current_page != "dashboard" else "soft",
                        size="2"
                    ),
                    content="Dashboard"
                ),
                rx.tooltip(
                    rx.button(
                        rx.icon("server", size=18),
                        on_click=lambda: DashboardState.set_page("providers"),
                        variant="ghost" if DashboardState.current_page != "providers" else "soft",
                        size="2"
                    ),
                    content="Providers"
                ),
                rx.tooltip(
                    rx.button(
                        rx.icon("terminal", size=18),
                        on_click=lambda: DashboardState.set_page("terminal"),
                        variant="ghost" if DashboardState.current_page != "terminal" else "soft",
                        size="2"
                    ),
                    content="Terminal"
                ),
                rx.tooltip(
                    rx.button(
                        rx.icon("folder", size=18),
                        on_click=lambda: DashboardState.set_page("files"),
                        variant="ghost" if DashboardState.current_page != "files" else "soft",
                        size="2"
                    ),
                    content="Files"
                ),
                rx.tooltip(
                    rx.button(
                        rx.icon("camera", size=18),
                        on_click=lambda: DashboardState.set_page("snapshots"),
                        variant="ghost" if DashboardState.current_page != "snapshots" else "soft",
                        size="2"
                    ),
                    content="Snapshots"
                ),
                spacing="2",
                style={"padding": "0 0.5rem"}
            ),
            
            rx.spacer(),
            
            # Footer icons
            rx.vstack(
                rx.divider(),
                rx.tooltip(
                    rx.button(
                        rx.icon("settings", size=16),
                        on_click=DashboardState.open_settings,
                        variant="ghost",
                        size="2"
                    ),
                    content="Settings"
                ),
                style={"padding": "1rem 0.5rem"}
            ),
            
            spacing="0",
            height="100vh",
            width="100%",
            align="center"
        ),
        style={
            "width": "60px",
            "min_width": "60px",
            "background": "var(--gray-2)",
            "border_right": "1px solid var(--gray-6)"
        }
    )

