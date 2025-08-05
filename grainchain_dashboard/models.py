"""Database models for Grainchain Dashboard."""

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import Optional
import json

Base = declarative_base()

class ProviderConfig(Base):
    """Store provider API keys and configuration."""
    __tablename__ = "provider_configs"
    
    id = sa.Column(sa.Integer, primary_key=True)
    provider_name = sa.Column(sa.String(50), unique=True, nullable=False)
    api_key = sa.Column(sa.Text, nullable=True)  # Encrypted
    config_data = sa.Column(sa.Text, nullable=True)  # JSON config
    is_enabled = sa.Column(sa.Boolean, default=True)
    last_tested = sa.Column(sa.DateTime, nullable=True)
    test_status = sa.Column(sa.String(20), default="unknown")  # success, failed, unknown
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_config_dict(self) -> dict:
        """Get configuration as dictionary."""
        if self.config_data:
            return json.loads(self.config_data)
        return {}
    
    def set_config_dict(self, config: dict):
        """Set configuration from dictionary."""
        self.config_data = json.dumps(config)

class FileMetadata(Base):
    """Store file metadata and information."""
    __tablename__ = "file_metadata"
    
    id = sa.Column(sa.Integer, primary_key=True)
    file_path = sa.Column(sa.String(500), nullable=False)
    file_name = sa.Column(sa.String(255), nullable=False)
    file_size = sa.Column(sa.BigInteger, nullable=False)
    file_type = sa.Column(sa.String(50), nullable=True)
    mime_type = sa.Column(sa.String(100), nullable=True)
    is_directory = sa.Column(sa.Boolean, default=False)
    parent_directory = sa.Column(sa.String(500), nullable=True)
    sandbox_id = sa.Column(sa.String(100), nullable=True)
    provider = sa.Column(sa.String(50), nullable=True)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    modified_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    accessed_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    
    # Relationships
    snapshots = relationship("SnapshotFile", back_populates="file")

class Snapshot(Base):
    """Store snapshot information."""
    __tablename__ = "snapshots"
    
    id = sa.Column(sa.Integer, primary_key=True)
    snapshot_id = sa.Column(sa.String(100), unique=True, nullable=False)
    name = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    sandbox_id = sa.Column(sa.String(100), nullable=False)
    provider = sa.Column(sa.String(50), nullable=False)
    snapshot_size = sa.Column(sa.BigInteger, nullable=True)
    file_count = sa.Column(sa.Integer, default=0)
    status = sa.Column(sa.String(20), default="creating")  # creating, ready, failed, restoring
    storage_path = sa.Column(sa.String(500), nullable=True)
    metadata = sa.Column(sa.Text, nullable=True)  # JSON metadata
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    completed_at = sa.Column(sa.DateTime, nullable=True)
    
    # Relationships
    files = relationship("SnapshotFile", back_populates="snapshot")
    
    def get_metadata_dict(self) -> dict:
        """Get metadata as dictionary."""
        if self.metadata:
            return json.loads(self.metadata)
        return {}
    
    def set_metadata_dict(self, metadata: dict):
        """Set metadata from dictionary."""
        self.metadata = json.dumps(metadata)

class SnapshotFile(Base):
    """Association table for snapshots and files."""
    __tablename__ = "snapshot_files"
    
    id = sa.Column(sa.Integer, primary_key=True)
    snapshot_id = sa.Column(sa.Integer, sa.ForeignKey("snapshots.id"), nullable=False)
    file_id = sa.Column(sa.Integer, sa.ForeignKey("file_metadata.id"), nullable=False)
    relative_path = sa.Column(sa.String(500), nullable=False)
    file_hash = sa.Column(sa.String(64), nullable=True)  # SHA256 hash
    
    # Relationships
    snapshot = relationship("Snapshot", back_populates="files")
    file = relationship("FileMetadata", back_populates="snapshots")

class UserSettings(Base):
    """Store user preferences and settings."""
    __tablename__ = "user_settings"
    
    id = sa.Column(sa.Integer, primary_key=True)
    setting_key = sa.Column(sa.String(100), unique=True, nullable=False)
    setting_value = sa.Column(sa.Text, nullable=True)
    setting_type = sa.Column(sa.String(20), default="string")  # string, json, boolean, integer
    description = sa.Column(sa.Text, nullable=True)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_typed_value(self):
        """Get value with proper type conversion."""
        if self.setting_type == "json":
            return json.loads(self.setting_value) if self.setting_value else {}
        elif self.setting_type == "boolean":
            return self.setting_value.lower() == "true" if self.setting_value else False
        elif self.setting_type == "integer":
            return int(self.setting_value) if self.setting_value else 0
        else:
            return self.setting_value

class CommandHistory(Base):
    """Store command execution history."""
    __tablename__ = "command_history"
    
    id = sa.Column(sa.Integer, primary_key=True)
    command = sa.Column(sa.Text, nullable=False)
    sandbox_id = sa.Column(sa.String(100), nullable=False)
    provider = sa.Column(sa.String(50), nullable=False)
    exit_code = sa.Column(sa.Integer, nullable=True)
    stdout = sa.Column(sa.Text, nullable=True)
    stderr = sa.Column(sa.Text, nullable=True)
    execution_time = sa.Column(sa.Float, nullable=True)  # seconds
    executed_at = sa.Column(sa.DateTime, default=datetime.utcnow)

class ActivityLog(Base):
    """Store activity logs for audit trail."""
    __tablename__ = "activity_logs"
    
    id = sa.Column(sa.Integer, primary_key=True)
    action = sa.Column(sa.String(100), nullable=False)
    resource_type = sa.Column(sa.String(50), nullable=False)  # provider, file, snapshot, etc.
    resource_id = sa.Column(sa.String(100), nullable=True)
    details = sa.Column(sa.Text, nullable=True)  # JSON details
    status = sa.Column(sa.String(20), nullable=False)  # success, failed, pending
    error_message = sa.Column(sa.Text, nullable=True)
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    
    def get_details_dict(self) -> dict:
        """Get details as dictionary."""
        if self.details:
            return json.loads(self.details)
        return {}
    
    def set_details_dict(self, details: dict):
        """Set details from dictionary."""
        self.details = json.dumps(details)
