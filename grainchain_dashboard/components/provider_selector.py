"""Provider selection component."""

import reflex as rx
from typing import Dict, Any

def provider_option(name: str, info: Dict[str, Any], is_selected: bool = False) -> rx.Component:
    """Create a provider option in the selector."""
    
    status_color = "green" if info.get("available", False) else "red"
    
    return rx.card(
        rx.hstack(
            rx.vstack(
                rx.hstack(
                    rx.text(name.title(), weight="bold", size="3"),
                    rx.badge(
                        "Available" if info.get("available", False) else "Unavailable",
                        color_scheme=status_color,
                        variant="soft"
                    ),
                    spacing="2"
                ),
                rx.text(
                    f"Dependencies: {'✓' if info.get('dependencies_installed', False) else '✗'}",
                    size="2",
                    color="gray"
                ),
                rx.cond(
                    info.get("missing_config"),
                    rx.text(
                        f"Missing: {', '.join(info.get('missing_config', []))}",
                        size="1",
                        color="red"
                    )
                ),
                align="start",
                spacing="1"
            ),
            rx.cond(
                is_selected,
                rx.icon("check-circle", size=20, color="green")
            ),
            justify="between",
            width="100%"
        ),
        variant="surface" if not is_selected else "classic",
        style={
            "cursor": "pointer" if info.get("available", False) else "not-allowed",
            "opacity": "1" if info.get("available", False) else "0.6",
            "border": "2px solid var(--accent-9)" if is_selected else "1px solid var(--gray-6)"
        },
        on_click=rx.cond(
            info.get("available", False),
            lambda: rx.call_script(f"window.selectProvider('{name}')")
        )
    )

def quick_provider_selector() -> rx.Component:
    """Create a compact provider selector for the sidebar."""
    from ..state import DashboardState
    
    return rx.vstack(
        rx.text("Active Provider", size="2", weight="bold"),
        rx.select.root(
            rx.select.trigger(
                rx.select.value(placeholder="Select provider...")
            ),
            rx.select.content(
                rx.foreach(
                    DashboardState.providers,
                    lambda provider_item: rx.cond(
                        provider_item[1].get("available", False),
                        rx.select.item(
                            provider_item[0].title(),
                            value=provider_item[0]
                        )
                    )
                )
            ),
            value=DashboardState.selected_provider,
            on_value_change=DashboardState.select_provider
        ),
        spacing="2",
        width="100%"
    )

def provider_health_indicator(provider: str, status: str) -> rx.Component:
    """Create a health indicator for a provider."""
    
    color_map = {
        "healthy": "green",
        "unhealthy": "red",
        "unknown": "gray",
        "error": "red"
    }
    
    icon_map = {
        "healthy": "check-circle",
        "unhealthy": "x-circle", 
        "unknown": "help-circle",
        "error": "alert-circle"
    }
    
    return rx.hstack(
        rx.icon(
            icon_map.get(status, "help-circle"),
            size=16,
            color=color_map.get(status, "gray")
        ),
        rx.text(
            provider.title(),
            size="2"
        ),
        rx.badge(
            status.title(),
            color_scheme=color_map.get(status, "gray"),
            variant="soft",
            size="1"
        ),
        spacing="2",
        align="center"
    )

def provider_grid() -> rx.Component:
    """Create a grid of provider options."""
    from ..state import DashboardState
    
    return rx.vstack(
        rx.heading("Available Providers", size="4"),
        rx.text(
            "Select a provider to create and manage sandboxes",
            size="2",
            color="gray"
        ),
        rx.grid(
            rx.foreach(
                DashboardState.providers,
                lambda provider_item: provider_option(
                    provider_item[0],  # provider name
                    provider_item[1],  # provider info
                    DashboardState.selected_provider == provider_item[0]
                )
            ),
            columns="2",
            spacing="3",
            width="100%"
        ),
        spacing="4",
        width="100%"
    )

def provider_status_panel() -> rx.Component:
    """Create a status panel showing all provider health."""
    from ..state import DashboardState
    
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading("Provider Status", size="4"),
                rx.button(
                    rx.icon("refresh-cw", size=16),
                    "Refresh",
                    on_click=DashboardState.refresh_providers,
                    loading=DashboardState.loading,
                    variant="ghost",
                    size="2"
                ),
                justify="between",
                width="100%"
            ),
            rx.divider(),
            rx.vstack(
                rx.foreach(
                    DashboardState.provider_health_status,
                    lambda status_item: provider_health_indicator(
                        status_item[0],  # provider name
                        status_item[1]   # status
                    )
                ),
                spacing="2",
                width="100%"
            ),
            spacing="3",
            width="100%"
        ),
        variant="surface"
    )

