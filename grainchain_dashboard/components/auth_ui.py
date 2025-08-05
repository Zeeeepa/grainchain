#!/usr/bin/env python3
"""Authentication UI components."""

import reflex as rx
from typing import Optional

def login_form() -> rx.Component:
    """Login form component."""
    return rx.card(
        rx.vstack(
            rx.heading("Login to Grainchain", size="6", text_align="center"),
            rx.form(
                rx.vstack(
                    rx.input(
                        placeholder="Username",
                        name="username",
                        required=True,
                        width="100%"
                    ),
                    rx.input(
                        placeholder="Password",
                        name="password",
                        type="password",
                        required=True,
                        width="100%"
                    ),
                    rx.button(
                        "Login",
                        type="submit",
                        width="100%",
                        color_scheme="blue"
                    ),
                    spacing="4",
                    width="100%"
                ),
                on_submit=lambda form_data: AuthState.login(
                    form_data["username"], 
                    form_data["password"]
                ),
                width="100%"
            ),
            rx.cond(
                AuthState.login_error != "",
                rx.callout(
                    AuthState.login_error,
                    icon="alert-circle",
                    color_scheme="red",
                    width="100%"
                )
            ),
            spacing="4",
            width="100%"
        ),
        max_width="400px",
        margin="auto",
        padding="2rem"
    )

def user_menu() -> rx.Component:
    """User menu dropdown component."""
    return rx.menu.root(
        rx.menu.trigger(
            rx.button(
                rx.hstack(
                    rx.avatar(
                        fallback=rx.cond(
                            AuthState.current_user,
                            AuthState.current_user["username"][0].upper(),
                            "?"
                        ),
                        size="2"
                    ),
                    rx.text(
                        rx.cond(
                            AuthState.current_user,
                            AuthState.current_user["username"],
                            "Guest"
                        )
                    ),
                    rx.icon("chevron-down", size=16),
                    spacing="2"
                ),
                variant="ghost"
            )
        ),
        rx.menu.content(
            rx.menu.item(
                rx.hstack(
                    rx.icon("user", size=16),
                    rx.text("Profile"),
                    spacing="2"
                ),
                on_click=lambda: rx.redirect("/profile")
            ),
            rx.menu.item(
                rx.hstack(
                    rx.icon("settings", size=16),
                    rx.text("Settings"),
                    spacing="2"
                ),
                on_click=lambda: rx.redirect("/settings")
            ),
            rx.menu.separator(),
            rx.menu.item(
                rx.hstack(
                    rx.icon("log-out", size=16),
                    rx.text("Logout"),
                    spacing="2"
                ),
                on_click=AuthState.logout,
                color="red"
            )
        )
    )

def auth_guard(component: rx.Component) -> rx.Component:
    """Protect component with authentication."""
    return rx.cond(
        AuthState.is_authenticated,
        component,
        rx.center(
            rx.card(
                rx.vstack(
                    rx.icon("lock", size=48, color="gray"),
                    rx.heading("Authentication Required", size="5"),
                    rx.text("Please log in to access this page."),
                    rx.button(
                        "Go to Login",
                        on_click=lambda: rx.redirect("/login"),
                        color_scheme="blue"
                    ),
                    spacing="4",
                    text_align="center"
                ),
                padding="2rem"
            ),
            height="100vh"
        )
    )

def role_guard(component: rx.Component, required_role: str) -> rx.Component:
    """Protect component with role-based access."""
    return rx.cond(
        AuthState.is_authenticated & (AuthState.current_user["role"] == required_role),
        component,
        rx.center(
            rx.card(
                rx.vstack(
                    rx.icon("shield-x", size=48, color="red"),
                    rx.heading("Access Denied", size="5"),
                    rx.text(f"You need {required_role} role to access this page."),
                    rx.button(
                        "Go Back",
                        on_click=lambda: rx.redirect("/dashboard"),
                        color_scheme="gray"
                    ),
                    spacing="4",
                    text_align="center"
                ),
                padding="2rem"
            ),
            height="100vh"
        )
    )

# Import AuthState for use in components
try:
    from ..auth import AuthState
except ImportError as e:
    print(f"❌ Critical error: Authentication module failed to import: {e}")
    print("🔧 Please ensure auth.py is properly configured")
    raise ImportError("Authentication system is required for the dashboard to function")
