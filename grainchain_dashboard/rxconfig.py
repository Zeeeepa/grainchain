"""Reflex configuration file for Grainchain Dashboard."""

import reflex as rx
from .config import config

# Reflex configuration
config_reflex = rx.Config(
    app_name="grainchain_dashboard",
    
    # Server configuration
    backend_host=config.host,
    backend_port=config.port,
    
    # Frontend configuration
    frontend_port=3000,
    
    # Database configuration (using SQLite for simplicity)
    db_url="sqlite:///grainchain_dashboard.db",
    
    # Environment
    env=rx.Env.DEV if config.debug else rx.Env.PROD,
    
    # API configuration
    api_url=f"http://{config.host}:{config.port}",
    
    # Styling
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="medium",
        scaling="100%",
    ),
    
    # Performance
    compile=not config.debug,
    
    # Tailwind CSS (optional)
    tailwind={
        "theme": {
            "extend": {
                "colors": {
                    "primary": {
                        "50": "#eff6ff",
                        "500": "#3b82f6",
                        "900": "#1e3a8a",
                    }
                }
            }
        }
    }
)

