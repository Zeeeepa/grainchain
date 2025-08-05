"""Consolidated Dashboard State Management."""

import reflex as rx
from typing import Dict, List, Optional, Any
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database import get_db_session, log_activity, get_setting, set_setting
    from models import ProviderConfig, FileMetadata, Snapshot, CommandHistory, UserSettings
    from utils.encryption import encrypt_api_key, decrypt_api_key, secure_api_key_display, validate_api_key_format, sanitize_input
except ImportError as e:
    print(f"⚠️ Import warning: {e}")

class DashboardState(rx.State):
    """Consolidated dashboard state with all features."""
    
    # Navigation
    current_page: str = "dashboard"
    
    # Statistics
    active_sandboxes_count: int = 1
    providers_count: int = 5
    commands_run_count: int = 42
    
    # Provider management
    providers: Dict[str, Dict[str, Any]] = {
        "local": {"name": "Local", "status": "success", "has_api_key": True, "description": "Local development environment"},
        "e2b": {"name": "E2B", "status": "failed", "has_api_key": False, "description": "Cloud sandboxes with templates"},
        "daytona": {"name": "Daytona", "status": "unknown", "has_api_key": False, "description": "Development workspaces"},
        "morph": {"name": "Morph", "status": "unknown", "has_api_key": False, "description": "Custom VMs with fast snapshots"},
        "modal": {"name": "Modal", "status": "unknown", "has_api_key": False, "description": "Serverless compute platform"},
    }
    
    # File management
    current_directory: str = "/"
    files: List[Dict[str, Any]] = [
        {"name": "main.py", "size": 1024, "type": "file", "modified": "2025-01-05 10:30", "path": "/main.py"},
        {"name": "README.md", "size": 2048, "type": "file", "modified": "2025-01-05 10:25", "path": "/README.md"},
        {"name": "src", "size": 0, "type": "directory", "modified": "2025-01-05 10:20", "path": "/src"},
        {"name": "tests", "size": 0, "type": "directory", "modified": "2025-01-05 10:15", "path": "/tests"},
        {"name": "requirements.txt", "size": 512, "type": "file", "modified": "2025-01-05 10:10", "path": "/requirements.txt"},
    ]
    
    # Snapshot management
    snapshots: List[Dict[str, Any]] = [
        {"id": "snap_001", "name": "Initial Setup", "status": "ready", "size": "50MB", "created": "2025-01-05 09:00", "files_count": 15},
        {"id": "snap_002", "name": "After Dependencies", "status": "ready", "size": "120MB", "created": "2025-01-05 09:30", "files_count": 45},
        {"id": "snap_003", "name": "Working Implementation", "status": "creating", "size": "200MB", "created": "2025-01-05 10:00", "files_count": 78},
    ]
    
    # Terminal
    command_history: List[str] = ["ls -la", "python --version", "pip install -r requirements.txt", "python main.py"]
    command_output: str = """$ ls -la
total 24
drwxr-xr-x 5 user user 4096 Jan  5 10:30 .
drwxr-xr-x 3 root root 4096 Jan  5 10:00 ..
-rw-r--r-- 1 user user 1024 Jan  5 10:30 main.py
-rw-r--r-- 1 user user 2048 Jan  5 10:25 README.md
-rw-r--r-- 1 user user  512 Jan  5 10:10 requirements.txt
drwxr-xr-x 2 user user 4096 Jan  5 10:20 src
drwxr-xr-x 2 user user 4096 Jan  5 10:15 tests

$ python --version
Python 3.12.0

$ pip install -r requirements.txt
Collecting reflex>=0.8.0
  Downloading reflex-0.8.5-py3-none-any.whl
Installing collected packages: reflex, sqlalchemy, cryptography
Successfully installed reflex-0.8.5 sqlalchemy-2.0.42 cryptography-45.0.5

$ python main.py
🚀 Grainchain Dashboard starting...
✅ Database initialized
✅ All components loaded
🌐 Server running on http://localhost:3000

$ _"""
    current_command: str = ""
    
    # Settings
    theme: str = "dark"
    default_provider: str = "local"
    notifications_enabled: bool = True
    auto_save_enabled: bool = True
    command_history_limit: int = 100
    
    # UI State
    show_provider_modal: bool = False
    show_file_upload_modal: bool = False
    show_snapshot_modal: bool = False
    selected_provider: str = ""
    
    # Form states
    provider_api_key: str = ""
    snapshot_name: str = ""
    snapshot_description: str = ""
    
    def set_page(self, page: str):
        """Navigate to a different page."""
        self.current_page = page
    
    def open_provider_modal(self, provider: str):
        """Open provider configuration modal."""
        self.selected_provider = provider
        self.show_provider_modal = True
    
    def close_provider_modal(self):
        """Close provider configuration modal."""
        self.show_provider_modal = False
        self.provider_api_key = ""
    
    def save_provider_config(self):
        """Save provider configuration."""
        if self.provider_api_key.strip():
            if self.selected_provider in self.providers:
                self.providers[self.selected_provider]["has_api_key"] = True
                self.providers[self.selected_provider]["status"] = "success"
        self.close_provider_modal()
    
    def open_file_upload_modal(self):
        """Open file upload modal."""
        self.show_file_upload_modal = True
    
    def close_file_upload_modal(self):
        """Close file upload modal."""
        self.show_file_upload_modal = False
    
    def open_snapshot_modal(self):
        """Open create snapshot modal."""
        self.show_snapshot_modal = True
    
    def close_snapshot_modal(self):
        """Close create snapshot modal."""
        self.show_snapshot_modal = False
        self.snapshot_name = ""
        self.snapshot_description = ""
    
    def create_snapshot(self):
        """Create a new snapshot."""
        if self.snapshot_name.strip():
            new_snapshot = {
                "id": f"snap_{len(self.snapshots) + 1:03d}",
                "name": self.snapshot_name,
                "status": "creating",
                "size": "0MB",
                "created": "2025-01-05 10:35",
                "files_count": len(self.files)
            }
            self.snapshots.append(new_snapshot)
        self.close_snapshot_modal()
    
    def delete_snapshot(self, snapshot_id: str):
        """Delete a snapshot."""
        self.snapshots = [s for s in self.snapshots if s["id"] != snapshot_id]
    
    def execute_command(self):
        """Execute terminal command."""
        if self.current_command.strip():
            self.command_history.append(self.current_command)
            self.command_output += f"\n\n$ {self.current_command}\n"
            if self.current_command == "ls":
                self.command_output += "main.py  README.md  src  tests  requirements.txt"
            elif self.current_command.startswith("echo"):
                self.command_output += self.current_command[5:]
            else:
                self.command_output += f"Command executed: {self.current_command}"
            self.command_output += "\n\n$ _"
            self.current_command = ""
    
    def delete_file(self, file_path: str):
        """Delete a file."""
        self.files = [f for f in self.files if f["path"] != file_path]
    
    # Database integration methods
    async def load_providers_from_db(self):
        """Load provider configurations from database."""
        try:
            session = get_db_session()
            # Implementation would load from database
            pass
        except Exception as e:
            print(f"Error loading providers: {e}")
    
    async def save_provider_to_db(self, provider_name: str, config: dict):
        """Save provider configuration to database."""
        try:
            session = get_db_session()
            # Implementation would save to database
            pass
        except Exception as e:
            print(f"Error saving provider: {e}")
    
    async def log_user_activity(self, action: str, details: str = ""):
        """Log user activity to database."""
        try:
            log_activity("dashboard", action, details)
        except Exception as e:
            print(f"Error logging activity: {e}")
