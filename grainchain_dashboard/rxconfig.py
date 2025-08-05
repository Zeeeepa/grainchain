"""Simple Reflex configuration for Grainchain Dashboard."""

import reflex as rx

config = rx.Config(
    app_name="app",
    
    # Server configuration
    backend_host="0.0.0.0",
    backend_port=8001,
    
    # Frontend configuration
    frontend_port=3001,
    
    # Environment
    env=rx.Env.DEV,
    
    # Styling
    theme=rx.theme(
        appearance="dark",
        has_background=True,
        radius="medium",
        scaling="100%",
    ),
)
