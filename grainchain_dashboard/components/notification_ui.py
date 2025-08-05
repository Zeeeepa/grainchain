#!/usr/bin/env python3
"""Notification UI components."""

import reflex as rx
from typing import List, Dict, Any

def notification_toast(notification: Dict[str, Any]) -> rx.Component:
    """Individual notification toast component."""
    color_map = {
        "info": "blue",
        "success": "green", 
        "warning": "yellow",
        "error": "red",
        "system": "gray"
    }
    
    icon_map = {
        "info": "info",
        "success": "check-circle",
        "warning": "alert-triangle", 
        "error": "alert-circle",
        "system": "settings"
    }
    
    color = color_map.get(notification.get("type", "info"), "blue")
    icon = icon_map.get(notification.get("type", "info"), "info")
    
    return rx.toast(
        rx.hstack(
            rx.icon(icon, size=20, color=color),
            rx.vstack(
                rx.text(notification.get("title", ""), weight="medium"),
                rx.text(notification.get("message", ""), size="2", color="gray"),
                spacing="1",
                align="start"
            ),
            spacing="3",
            align="center"
        ),
        duration=5000 if notification.get("priority") != "urgent" else 10000
    )

def notification_bell() -> rx.Component:
    """Notification bell icon with unread count."""
    return rx.button(
        rx.hstack(
            rx.icon("bell", size=18),
            rx.cond(
                NotificationState.unread_count > 0,
                rx.badge(
                    NotificationState.unread_count,
                    color_scheme="red",
                    variant="solid",
                    size="1"
                ),
                rx.box()
            ),
            spacing="2"
        ),
        variant="ghost",
        on_click=NotificationState.toggle_panel
    )

def notification_panel() -> rx.Component:
    """Notification panel dropdown."""
    return rx.drawer.root(
        rx.drawer.trigger(rx.box()),  # Hidden trigger
        rx.drawer.content(
            rx.drawer.header(
                rx.hstack(
                    rx.drawer.title("Notifications"),
                    rx.spacer(),
                    rx.button(
                        rx.icon("check-check", size=16),
                        variant="ghost",
                        size="2",
                        on_click=NotificationState.mark_all_read
                    ),
                    rx.drawer.close(
                        rx.button(
                            rx.icon("x", size=16),
                            variant="ghost",
                            size="2"
                        )
                    ),
                    spacing="2",
                    align="center",
                    width="100%"
                )
            ),
            rx.drawer.body(
                rx.cond(
                    len(NotificationState.notifications) == 0,
                    rx.center(
                        rx.vstack(
                            rx.icon("bell-off", size=48, color="gray"),
                            rx.text("No notifications", color="gray"),
                            spacing="3"
                        ),
                        height="200px"
                    ),
                    rx.vstack(
                        rx.foreach(
                            NotificationState.notifications,
                            notification_item
                        ),
                        spacing="2",
                        width="100%"
                    )
                )
            ),
            side="right",
            size="md"
        ),
        open=NotificationState.show_panel
    )

def notification_item(notification: Dict[str, Any]) -> rx.Component:
    """Individual notification item in the panel."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon(
                    rx.cond(
                        notification["type"] == "success",
                        "check-circle",
                        rx.cond(
                            notification["type"] == "error",
                            "alert-circle",
                            rx.cond(
                                notification["type"] == "warning",
                                "alert-triangle",
                                "info"
                            )
                        )
                    ),
                    size=16,
                    color=rx.cond(
                        notification["type"] == "success",
                        "green",
                        rx.cond(
                            notification["type"] == "error",
                            "red",
                            rx.cond(
                                notification["type"] == "warning",
                                "yellow",
                                "blue"
                            )
                        )
                    )
                ),
                rx.text(notification["title"], weight="medium", size="2"),
                rx.spacer(),
                rx.cond(
                    notification.get("read_at") is None,
                    rx.badge("New", color_scheme="blue", size="1"),
                    rx.box()
                ),
                rx.button(
                    rx.icon("x", size=12),
                    variant="ghost",
                    size="1",
                    on_click=lambda: NotificationState.delete_notification(notification["id"])
                ),
                spacing="2",
                align="center",
                width="100%"
            ),
            rx.text(notification["message"], size="2", color="gray"),
            rx.text(
                notification.get("created_at", ""),
                size="1",
                color="gray"
            ),
            spacing="2",
            align="start",
            width="100%"
        ),
        padding="0.75rem",
        cursor="pointer",
        _hover={"background": "var(--gray-2)"},
        on_click=lambda: NotificationState.mark_as_read(notification["id"]),
        opacity=rx.cond(notification.get("read_at") is None, "1", "0.7")
    )

def activity_feed() -> rx.Component:
    """Activity feed component."""
    return rx.vstack(
        rx.heading("Recent Activity", size="4"),
        rx.cond(
            len(NotificationState.activities) == 0,
            rx.center(
                rx.vstack(
                    rx.icon("activity", size=48, color="gray"),
                    rx.text("No recent activity", color="gray"),
                    spacing="3"
                ),
                height="200px"
            ),
            rx.vstack(
                rx.foreach(
                    NotificationState.activities,
                    activity_item
                ),
                spacing="3",
                width="100%"
            )
        ),
        spacing="4",
        width="100%"
    )

def activity_item(activity: Dict[str, Any]) -> rx.Component:
    """Individual activity item."""
    return rx.hstack(
        rx.icon(
            rx.cond(
                activity["action"] == "created",
                "plus-circle",
                rx.cond(
                    activity["action"] == "deleted",
                    "trash-2",
                    rx.cond(
                        activity["action"] == "modified",
                        "edit",
                        "activity"
                    )
                )
            ),
            size=16,
            color="blue"
        ),
        rx.vstack(
            rx.text(activity["description"], size="2"),
            rx.text(
                activity.get("timestamp", ""),
                size="1",
                color="gray"
            ),
            spacing="1",
            align="start"
        ),
        spacing="3",
        align="center",
        width="100%"
    )

def notification_preferences() -> rx.Component:
    """Notification preferences panel."""
    return rx.vstack(
        rx.heading("Notification Preferences", size="4"),
        rx.vstack(
            rx.hstack(
                rx.switch(
                    checked=NotificationState.email_enabled,
                    on_change=NotificationState.set_email_enabled
                ),
                rx.text("Email notifications"),
                spacing="3",
                align="center"
            ),
            rx.hstack(
                rx.switch(
                    checked=NotificationState.push_enabled,
                    on_change=NotificationState.set_push_enabled
                ),
                rx.text("Push notifications"),
                spacing="3",
                align="center"
            ),
            rx.hstack(
                rx.switch(
                    checked=NotificationState.sound_enabled,
                    on_change=NotificationState.set_sound_enabled
                ),
                rx.text("Sound notifications"),
                spacing="3",
                align="center"
            ),
            spacing="4",
            align="start"
        ),
        rx.divider(),
        rx.text("Notification Types", weight="medium"),
        rx.vstack(
            rx.foreach(
                NotificationState.notification_types,
                lambda type_info: rx.hstack(
                    rx.checkbox(
                        checked=type_info["enabled"],
                        on_change=lambda checked: NotificationState.toggle_type(type_info["type"], checked)
                    ),
                    rx.text(type_info["label"]),
                    spacing="3",
                    align="center"
                )
            ),
            spacing="2",
            align="start"
        ),
        rx.button(
            "Save Preferences",
            on_click=NotificationState.save_preferences,
            color_scheme="blue"
        ),
        spacing="4",
        width="100%"
    )

# Import real NotificationState - no fallback to mock
try:
    from ..notifications.notification_manager import NotificationState
except ImportError as e:
    print(f"❌ Critical error: Notification module failed to import: {e}")
    print("🔧 Please ensure notification_manager.py is properly configured")
    raise ImportError("Notification system is required for the dashboard to function")
