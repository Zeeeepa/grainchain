"""Reflex configuration for Grainchain Dashboard."""

import reflex as rx
from config.settings import get_config

# Get configuration
config_settings = get_config()

# Reflex configuration
config = rx.Config(
    app_name=config_settings.APP_NAME,
    
    # Server configuration
    backend_host=config_settings.HOST,
    backend_port=config_settings.BACKEND_PORT,
    
    # Frontend configuration
    frontend_port=config_settings.FRONTEND_PORT,
    
    # Database configuration
    db_url=config_settings.DATABASE_URL,
    
    # Environment
    env=rx.Env.DEV if config_settings.DEBUG else rx.Env.PROD,
    
    # Disable sitemap plugin warnings
    disable_plugins=["reflex.plugins.sitemap.SitemapPlugin"],
    
    # Styling
    theme=rx.theme(
        appearance=config_settings.DEFAULT_THEME,
        has_background=True,
        radius="medium",
        scaling="100%",
    ),
)
