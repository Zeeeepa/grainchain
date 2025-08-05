"""Configuration management for Grainchain Dashboard."""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DashboardConfig(BaseModel):
    """Main configuration for the dashboard."""
    
    # App settings
    app_name: str = "Grainchain Dashboard"
    debug: bool = Field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    host: str = Field(default_factory=lambda: os.getenv("HOST", "localhost"))
    port: int = Field(default_factory=lambda: int(os.getenv("PORT", "3000")))
    
    # Security settings
    secret_key: str = Field(default_factory=lambda: os.getenv("SECRET_KEY", "dev-secret-key-change-in-production"))
    encryption_key: Optional[str] = Field(default_factory=lambda: os.getenv("ENCRYPTION_KEY"))
    
    # Storage settings
    data_dir: Path = Field(default_factory=lambda: Path(os.getenv("DATA_DIR", "./data")))
    config_file: Path = Field(default_factory=lambda: Path(os.getenv("CONFIG_FILE", "./data/dashboard_config.json")))
    
    # Provider settings
    default_provider: str = Field(default_factory=lambda: os.getenv("DEFAULT_PROVIDER", "local"))
    provider_timeout: int = Field(default_factory=lambda: int(os.getenv("PROVIDER_TIMEOUT", "300")))
    
    # Dashboard features
    enable_monitoring: bool = Field(default_factory=lambda: os.getenv("ENABLE_MONITORING", "true").lower() == "true")
    enable_analytics: bool = Field(default_factory=lambda: os.getenv("ENABLE_ANALYTICS", "true").lower() == "true")
    enable_collaboration: bool = Field(default_factory=lambda: os.getenv("ENABLE_COLLABORATION", "false").lower() == "true")
    
    def __post_init__(self):
        """Ensure data directory exists."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

class ProviderConfig(BaseModel):
    """Configuration for individual providers."""
    
    name: str
    enabled: bool = True
    api_key: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    last_health_check: Optional[str] = None
    health_status: str = "unknown"  # unknown, healthy, unhealthy, error

# Global configuration instance
config = DashboardConfig()

# Provider configurations
PROVIDER_CONFIGS = {
    "local": ProviderConfig(
        name="Local",
        enabled=True,
        config={
            "working_directory": os.getenv("LOCAL_WORKING_DIR", "./workspace"),
            "timeout": int(os.getenv("LOCAL_TIMEOUT", "60"))
        }
    ),
    "e2b": ProviderConfig(
        name="E2B",
        enabled=bool(os.getenv("E2B_API_KEY")),
        api_key=os.getenv("E2B_API_KEY"),
        config={
            "template": os.getenv("E2B_TEMPLATE", "base"),
            "timeout": int(os.getenv("E2B_TIMEOUT", "300"))
        }
    ),
    "daytona": ProviderConfig(
        name="Daytona",
        enabled=bool(os.getenv("DAYTONA_API_KEY")),
        api_key=os.getenv("DAYTONA_API_KEY"),
        config={
            "workspace_template": os.getenv("DAYTONA_WORKSPACE_TEMPLATE", "python-dev"),
            "timeout": int(os.getenv("DAYTONA_TIMEOUT", "300"))
        }
    ),
    "morph": ProviderConfig(
        name="Morph",
        enabled=bool(os.getenv("MORPH_API_KEY")),
        api_key=os.getenv("MORPH_API_KEY"),
        config={
            "image_id": os.getenv("MORPH_IMAGE_ID", "morphvm-minimal"),
            "vcpus": int(os.getenv("MORPH_VCPUS", "2")),
            "memory": int(os.getenv("MORPH_MEMORY", "2048")),
            "disk_size": int(os.getenv("MORPH_DISK_SIZE", "8192"))
        }
    ),
    "modal": ProviderConfig(
        name="Modal",
        enabled=bool(os.getenv("MODAL_TOKEN_ID") and os.getenv("MODAL_TOKEN_SECRET")),
        config={
            "token_id": os.getenv("MODAL_TOKEN_ID"),
            "token_secret": os.getenv("MODAL_TOKEN_SECRET"),
            "timeout": int(os.getenv("MODAL_TIMEOUT", "300"))
        }
    )
}

def get_enabled_providers() -> Dict[str, ProviderConfig]:
    """Get all enabled provider configurations."""
    return {name: config for name, config in PROVIDER_CONFIGS.items() if config.enabled}

def get_provider_config(provider_name: str) -> Optional[ProviderConfig]:
    """Get configuration for a specific provider."""
    return PROVIDER_CONFIGS.get(provider_name)

def update_provider_config(provider_name: str, updates: Dict[str, Any]) -> bool:
    """Update provider configuration."""
    if provider_name not in PROVIDER_CONFIGS:
        return False
    
    provider_config = PROVIDER_CONFIGS[provider_name]
    for key, value in updates.items():
        if hasattr(provider_config, key):
            setattr(provider_config, key, value)
        else:
            provider_config.config[key] = value
    
    return True

