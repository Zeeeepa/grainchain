"""Unified configuration settings for Grainchain Dashboard."""

import os
from typing import Dict, Any

class BaseConfig:
    """Base configuration with common settings."""
    
    # Application settings
    APP_NAME = "grainchain_dashboard"
    VERSION = "1.0.0"
    DEBUG = False
    
    # Database settings
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///grainchain.db")
    
    # Security settings
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ENCRYPTION_KEY_FILE = ".encryption_key"
    
    # Server settings
    HOST = "0.0.0.0"
    FRONTEND_PORT = 3000
    BACKEND_PORT = 8000
    
    # Provider settings
    SUPPORTED_PROVIDERS = ["local", "e2b", "daytona", "morph", "modal"]
    DEFAULT_PROVIDER = "local"
    
    # File management
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    ALLOWED_FILE_TYPES = [".py", ".js", ".ts", ".json", ".md", ".txt", ".yml", ".yaml"]
    
    # Terminal settings
    COMMAND_HISTORY_LIMIT = 100
    TERMINAL_TIMEOUT = 30
    
    # UI settings
    DEFAULT_THEME = "dark"
    ITEMS_PER_PAGE = 10

class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    
    DEBUG = True
    FRONTEND_PORT = 3000
    BACKEND_PORT = 8000

class ProductionConfig(BaseConfig):
    """Production configuration."""
    
    DEBUG = False
    FRONTEND_PORT = int(os.getenv("FRONTEND_PORT", 3000))
    BACKEND_PORT = int(os.getenv("BACKEND_PORT", 8000))
    
    # Production security
    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is required in production")

class TestingConfig(BaseConfig):
    """Testing configuration."""
    
    DEBUG = True
    DATABASE_URL = "sqlite:///:memory:"
    COMMAND_HISTORY_LIMIT = 10

# Configuration mapping
config_map: Dict[str, Any] = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}

def get_config(env: str = None) -> BaseConfig:
    """Get configuration based on environment."""
    if env is None:
        env = os.getenv("ENVIRONMENT", "default")
    
    config_class = config_map.get(env, DevelopmentConfig)
    return config_class()
