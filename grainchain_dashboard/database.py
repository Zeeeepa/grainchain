"""Database initialization and management."""

import os
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from typing import Generator, Optional
import logging

from .models import Base, ProviderConfig, UserSettings, FileMetadata, Snapshot, CommandHistory, ActivityLog

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///grainchain_dashboard.db")

# Create engine
engine = sa.create_engine(
    DATABASE_URL,
    echo=os.getenv("DEBUG", "false").lower() == "true",
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Initialize database tables."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Initialize default settings
        with get_db_session() as db:
            init_default_settings(db)
            init_default_providers(db)
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

def init_default_settings(db: Session):
    """Initialize default user settings."""
    default_settings = [
        {
            "setting_key": "theme",
            "setting_value": "dark",
            "setting_type": "string",
            "description": "UI theme preference"
        },
        {
            "setting_key": "default_provider",
            "setting_value": "local",
            "setting_type": "string",
            "description": "Default sandbox provider"
        },
        {
            "setting_key": "auto_save_commands",
            "setting_value": "true",
            "setting_type": "boolean",
            "description": "Automatically save command history"
        },
        {
            "setting_key": "max_command_history",
            "setting_value": "1000",
            "setting_type": "integer",
            "description": "Maximum number of commands to keep in history"
        },
        {
            "setting_key": "file_upload_max_size",
            "setting_value": "104857600",  # 100MB
            "setting_type": "integer",
            "description": "Maximum file upload size in bytes"
        },
        {
            "setting_key": "notifications_enabled",
            "setting_value": "true",
            "setting_type": "boolean",
            "description": "Enable desktop notifications"
        },
        {
            "setting_key": "dashboard_refresh_interval",
            "setting_value": "30",
            "setting_type": "integer",
            "description": "Dashboard auto-refresh interval in seconds"
        }
    ]
    
    for setting_data in default_settings:
        existing = db.query(UserSettings).filter(
            UserSettings.setting_key == setting_data["setting_key"]
        ).first()
        
        if not existing:
            setting = UserSettings(**setting_data)
            db.add(setting)
    
    db.commit()
    logger.info("Default settings initialized")

def init_default_providers(db: Session):
    """Initialize default provider configurations."""
    default_providers = [
        {
            "provider_name": "local",
            "is_enabled": True,
            "test_status": "success"
        },
        {
            "provider_name": "e2b",
            "is_enabled": False,
            "test_status": "unknown"
        },
        {
            "provider_name": "daytona",
            "is_enabled": False,
            "test_status": "unknown"
        },
        {
            "provider_name": "morph",
            "is_enabled": False,
            "test_status": "unknown"
        },
        {
            "provider_name": "modal",
            "is_enabled": False,
            "test_status": "unknown"
        }
    ]
    
    for provider_data in default_providers:
        existing = db.query(ProviderConfig).filter(
            ProviderConfig.provider_name == provider_data["provider_name"]
        ).first()
        
        if not existing:
            provider = ProviderConfig(**provider_data)
            db.add(provider)
    
    db.commit()
    logger.info("Default providers initialized")

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Get database session with automatic cleanup."""
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        session.close()

def get_db() -> Session:
    """Get database session (for dependency injection)."""
    return SessionLocal()

# Database utility functions
def get_setting(key: str, default=None) -> Optional[str]:
    """Get a user setting value."""
    try:
        with get_db_session() as db:
            setting = db.query(UserSettings).filter(UserSettings.setting_key == key).first()
            if setting:
                return setting.get_typed_value()
            return default
    except Exception as e:
        logger.error(f"Failed to get setting {key}: {e}")
        return default

def set_setting(key: str, value, setting_type: str = "string", description: str = None):
    """Set a user setting value."""
    try:
        with get_db_session() as db:
            setting = db.query(UserSettings).filter(UserSettings.setting_key == key).first()
            
            if setting:
                if setting_type == "json":
                    import json
                    setting.setting_value = json.dumps(value)
                else:
                    setting.setting_value = str(value)
                setting.setting_type = setting_type
                if description:
                    setting.description = description
            else:
                if setting_type == "json":
                    import json
                    value_str = json.dumps(value)
                else:
                    value_str = str(value)
                    
                setting = UserSettings(
                    setting_key=key,
                    setting_value=value_str,
                    setting_type=setting_type,
                    description=description
                )
                db.add(setting)
            
            db.commit()
            logger.info(f"Setting {key} updated successfully")
            
    except Exception as e:
        logger.error(f"Failed to set setting {key}: {e}")
        raise

def log_activity(action: str, resource_type: str, resource_id: str = None, 
                details: dict = None, status: str = "success", error_message: str = None):
    """Log an activity for audit trail."""
    try:
        with get_db_session() as db:
            activity = ActivityLog(
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                status=status,
                error_message=error_message
            )
            
            if details:
                activity.set_details_dict(details)
            
            db.add(activity)
            db.commit()
            
    except Exception as e:
        logger.error(f"Failed to log activity: {e}")

def cleanup_old_data():
    """Clean up old data based on retention policies."""
    try:
        with get_db_session() as db:
            # Get retention settings
            max_commands = get_setting("max_command_history", 1000)
            
            # Clean up old command history
            command_count = db.query(CommandHistory).count()
            if command_count > max_commands:
                excess_count = command_count - max_commands
                old_commands = db.query(CommandHistory).order_by(
                    CommandHistory.executed_at.asc()
                ).limit(excess_count).all()
                
                for cmd in old_commands:
                    db.delete(cmd)
                
                db.commit()
                logger.info(f"Cleaned up {excess_count} old command history entries")
            
            # Clean up old activity logs (keep last 30 days)
            from datetime import datetime, timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            old_activities = db.query(ActivityLog).filter(
                ActivityLog.created_at < cutoff_date
            ).all()
            
            for activity in old_activities:
                db.delete(activity)
            
            if old_activities:
                db.commit()
                logger.info(f"Cleaned up {len(old_activities)} old activity log entries")
                
    except Exception as e:
        logger.error(f"Failed to cleanup old data: {e}")

# Initialize database on import
try:
    init_database()
except Exception as e:
    logger.warning(f"Database initialization failed: {e}")
