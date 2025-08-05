"""Reflex configuration file for Grainchain Dashboard."""

import reflex as rx

# Reflex configuration
config = rx.Config(
    app_name="simple_main",
    
    # Server configuration
    backend_host="localhost",
    backend_port=8000,
    
    # Frontend configuration
    frontend_port=3001,
    
    # Database configuration (using SQLite for simplicity)
    db_url="sqlite:///grainchain_dashboard.db",
    
    # Environment
    env=rx.Env.DEV,
    
    # API configuration
    api_url="http://localhost:8000",
    
    # Styling
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="medium",
        scaling="100%",
    ),
)
