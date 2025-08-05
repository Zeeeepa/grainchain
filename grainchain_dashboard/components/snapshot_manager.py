"""Snapshot management components."""

import reflex as rx
from typing import Dict, Any, List

def snapshot_card(snapshot: Dict[str, Any]) -> rx.Component:
    """Create a card for a single snapshot."""
    
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.text(
                        f"Snapshot {snapshot['snapshot_id'][:8]}...",
                        weight="bold",
                        size="3"
                    ),
                    rx.text(
                        snapshot.get("description", "No description"),
                        size="2",
                        color="gray"
                    ),
                    align="start",
                    spacing="1"
                ),
                rx.menu.root(
                    rx.menu.trigger(
                        rx.button(
                            rx.icon("more-vertical", size=16),
                            variant="ghost",
                            size="2"
                        )
                    ),
                    rx.menu.content(
                        rx.menu.item(
                            rx.icon("play", size=16),
                            "Restore",
                            on_click=lambda: rx.call_script(f"window.restoreSnapshot('{snapshot['snapshot_id']}')")
                        ),
                        rx.menu.separator(),
                        rx.menu.item(
                            rx.icon("trash-2", size=16),
                            "Delete",
                            color="red",
                            on_click=lambda: rx.call_script(f"window.deleteSnapshot('{snapshot['snapshot_id']}')")
                        )
                    )
                ),
                justify="between",
                width="100%"
            ),
            rx.hstack(
                rx.text(
                    f"Created: {snapshot['created_at']}",
                    size="1",
                    color="gray"
                ),
                rx.cond(
                    snapshot.get("size_mb"),
                    rx.text(
                        f"Size: {snapshot['size_mb']:.1f} MB",
                        size="1",
                        color="gray"
                    )
                ),
                spacing="4"
            ),
            rx.badge(
                snapshot["provider"].title(),
                variant="soft",
                size="1"
            ),
            spacing="3",
            align="start",
            width="100%"
        ),
        variant="surface",
        style={"min_height": "120px"}
    )

def create_snapshot_form() -> rx.Component:
    """Create form for creating new snapshots."""
    from ..state import DashboardState
    
    return rx.card(
        rx.vstack(
            rx.heading("Create Snapshot", size="4"),
            rx.text(
                "Create a snapshot of the current sandbox state",
                size="2",
                color="gray"
            ),
            rx.form_field(
                rx.form_label("Description (optional)"),
                rx.text_area(
                    placeholder="Enter a description for this snapshot...",
                    value=DashboardState.snapshot_description,
                    on_change=DashboardState.set_snapshot_description,
                    rows=3
                ),
                name="description"
            ),
            rx.hstack(
                rx.button(
                    rx.icon("camera", size=16),
                    "Create Snapshot",
                    on_click=DashboardState.create_snapshot,
                    loading=DashboardState.loading,
                    disabled=~DashboardState.selected_sandbox_id
                ),
                rx.button(
                    rx.icon("refresh-cw", size=16),
                    "Refresh",
                    on_click=DashboardState.refresh_snapshots,
                    variant="outline",
                    size="2"
                ),
                spacing="2"
            ),
            spacing="4",
            width="100%"
        ),
        variant="surface"
    )

def snapshot_timeline() -> rx.Component:
    """Create a timeline view of snapshots."""
    from ..state import DashboardState
    
    return rx.vstack(
        rx.heading("Snapshot Timeline", size="4"),
        rx.cond(
            DashboardState.snapshots,
            rx.vstack(
                rx.foreach(
                    DashboardState.snapshots,
                    lambda snapshot: rx.hstack(
                        rx.vstack(
                            rx.circle(
                                rx.icon("camera", size=12),
                                size="6",
                                color_scheme="blue"
                            ),
                            rx.box(
                                height="20px",
                                width="2px",
                                bg="var(--gray-6)"
                            ),
                            spacing="0"
                        ),
                        rx.vstack(
                            rx.hstack(
                                rx.text(
                                    f"Snapshot {snapshot['snapshot_id'][:8]}...",
                                    weight="bold",
                                    size="2"
                                ),
                                rx.badge(
                                    snapshot["provider"].title(),
                                    variant="soft",
                                    size="1"
                                ),
                                spacing="2"
                            ),
                            rx.text(
                                snapshot.get("description", "No description"),
                                size="2",
                                color="gray"
                            ),
                            rx.text(
                                snapshot["created_at"],
                                size="1",
                                color="gray"
                            ),
                            rx.hstack(
                                rx.button(
                                    "Restore",
                                    size="1",
                                    variant="soft",
                                    on_click=lambda sid=snapshot['snapshot_id']: rx.call_script(f"window.restoreSnapshot('{sid}')")
                                ),
                                rx.button(
                                    "Delete",
                                    size="1",
                                    variant="soft",
                                    color_scheme="red",
                                    on_click=lambda sid=snapshot['snapshot_id']: rx.call_script(f"window.deleteSnapshot('{sid}')")
                                ),
                                spacing="2"
                            ),
                            align="start",
                            spacing="1"
                        ),
                        align="start",
                        spacing="3",
                        width="100%"
                    )
                ),
                spacing="2",
                width="100%"
            ),
            rx.text(
                "No snapshots available",
                size="2",
                color="gray",
                style={"text_align": "center", "padding": "2rem"}
            )
        ),
        spacing="4",
        width="100%"
    )

def snapshot_grid() -> rx.Component:
    """Create a grid view of snapshots."""
    from ..state import DashboardState
    
    return rx.vstack(
        rx.hstack(
            rx.heading("Snapshots", size="4"),
            rx.text(
                f"{len(DashboardState.snapshots)} snapshots",
                size="2",
                color="gray"
            ),
            justify="between",
            width="100%"
        ),
        rx.cond(
            DashboardState.snapshots,
            rx.grid(
                rx.foreach(
                    DashboardState.snapshots,
                    snapshot_card
                ),
                columns="3",
                spacing="4",
                width="100%"
            ),
            rx.text(
                "No snapshots available for this sandbox",
                size="2",
                color="gray",
                style={"text_align": "center", "padding": "2rem"}
            )
        ),
        spacing="4",
        width="100%"
    )

def snapshot_manager() -> rx.Component:
    """Main snapshot management component."""
    from ..state import DashboardState
    
    return rx.vstack(
        rx.cond(
            DashboardState.selected_sandbox_id,
            rx.vstack(
                create_snapshot_form(),
                rx.tabs.root(
                    rx.tabs.list(
                        rx.tabs.trigger("Grid View", value="grid"),
                        rx.tabs.trigger("Timeline", value="timeline")
                    ),
                    rx.tabs.content(
                        snapshot_grid(),
                        value="grid"
                    ),
                    rx.tabs.content(
                        snapshot_timeline(),
                        value="timeline"
                    ),
                    default_value="grid"
                ),
                spacing="6",
                width="100%"
            ),
            rx.card(
                rx.vstack(
                    rx.icon("camera", size=48, color="gray"),
                    rx.heading("No Sandbox Selected", size="4"),
                    rx.text(
                        "Select a sandbox to manage its snapshots",
                        size="2",
                        color="gray"
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

def snapshot_quick_actions() -> rx.Component:
    """Quick actions for snapshot management."""
    from ..state import DashboardState
    
    return rx.card(
        rx.vstack(
            rx.text("Quick Actions", weight="bold", size="2"),
            rx.vstack(
                rx.button(
                    rx.icon("camera", size=16),
                    "Create Snapshot",
                    on_click=DashboardState.create_snapshot,
                    loading=DashboardState.loading,
                    disabled=~DashboardState.selected_sandbox_id,
                    width="100%",
                    variant="soft"
                ),
                rx.button(
                    rx.icon("refresh-cw", size=16),
                    "Refresh Snapshots",
                    on_click=DashboardState.refresh_snapshots,
                    width="100%",
                    variant="outline",
                    size="2"
                ),
                spacing="2",
                width="100%"
            ),
            spacing="3",
            width="100%"
        ),
        variant="surface"
    )

