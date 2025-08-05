#!/usr/bin/env python3
"""
Simple test to check if basic Reflex app works
"""

import reflex as rx

class SimpleState(rx.State):
    """Simple test state."""
    message: str = "Hello World"

def index() -> rx.Component:
    """Simple index page."""
    return rx.vstack(
        rx.heading("Simple Test", size="6"),
        rx.text(SimpleState.message),
        padding="2rem",
    )

app = rx.App()
app.add_page(index)

if __name__ == "__main__":
    app.run()
