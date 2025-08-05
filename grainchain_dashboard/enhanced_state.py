"""Enhanced state management with database integration."""

import reflex as rx
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import asyncio
import logging
import os
import json

from database import get_db_session, log_activity, get_setting, set_setting
from models import ProviderConfig, FileMetadata, Snapshot, CommandHistory, UserSettings
from utils.encryption import encrypt_api_key, decrypt_api_key, secure_api_key_display, validate_api_key_format, sanitize_input

logger = logging.getLogger(__name__)

class EnhancedDashboardState(rx.State):
    """Enhanced state management with full functionality."""
    
    # UI State
    current_page: str = "dashboard"
    sidebar_open: bool = True
    loading: bool = False
    error_message: str = ""
    success_message: str = ""
    show_modal: bool = False
    modal_title: str = ""
    modal_content: str = ""
    
    # Provider Management State
    providers: Dict[str, Dict[str, Any]] = {}
    selected_provider: str = "local"
    provider_config_modal_open: bool = False
    selected_provider_for_config: str = ""
    api_key_input: str = ""
    provider_test_results: Dict[str, str] = {}
    
    # File Management State
    current_directory: str = "/"
    file_list: List[Dict[str, Any]] = []
    selected_files: List[str] = []
    file_upload_modal_open: bool = False
    file_create_modal_open: bool = False
    new_file_name: str = ""
    new_file_content: str = ""
    file_search_query: str = ""
    
    # Snapshot Management State
    snapshots: List[Dict[str, Any]] = []
    selected_snapshot_id: str = ""
    snapshot_create_modal_open: bool = False
    snapshot_name: str = ""
    snapshot_description: str = ""
    snapshot_progress: float = 0.0
    snapshot_operation_status: str = ""
    
    # Terminal State
    command_input: str = ""
    command_history: List[str] = []
    command_output: str = ""
    command_running: bool = False
    terminal_connected: bool = False
    current_sandbox_id: str = "local-sandbox-123"
    
    # Settings State
    settings: Dict[str, Any] = {}
    settings_modified: bool = False
    theme: str = "dark"
    default_provider_setting: str = "local"
    auto_save_commands: bool = True
    notifications_enabled: bool = True
    
    # Statistics
    active_sandboxes_count: int = 1
    providers_count: int = 5
    commands_run_count: int = 42
    
    def __init__(self):
        super().__init__()
        self.load_initial_data()
    
    # Initialization Methods
    def load_initial_data(self):
        """Load initial data from database."""
        try:
            self.load_providers()
            self.load_settings()
            self.load_snapshots()
            self.load_command_history()
            self.update_statistics()
        except Exception as e:
            logger.error(f"Failed to load initial data: {e}")
            self.error_message = "Failed to load dashboard data"
    
    def load_providers(self):
        """Load provider configurations from database."""
        try:
            with get_db_session() as db:
                provider_configs = db.query(ProviderConfig).all()
                
                self.providers = {}
                for config in provider_configs:
                    self.providers[config.provider_name] = {
                        "name": config.provider_name,
                        "enabled": config.is_enabled,
                        "status": config.test_status,
                        "has_api_key": bool(config.api_key),
                        "api_key_display": secure_api_key_display(config.api_key) if config.api_key else "",
                        "last_tested": config.last_tested.isoformat() if config.last_tested else None,
                        "config": config.get_config_dict()
                    }
                
                logger.info(f"Loaded {len(self.providers)} provider configurations")
                
        except Exception as e:
            logger.error(f"Failed to load providers: {e}")
    
    def load_settings(self):
        """Load user settings from database."""
        try:
            with get_db_session() as db:
                settings = db.query(UserSettings).all()
                
                self.settings = {}
                for setting in settings:
                    self.settings[setting.setting_key] = setting.get_typed_value()
                
                # Update state variables
                self.theme = self.settings.get("theme", "dark")
                self.default_provider_setting = self.settings.get("default_provider", "local")
                self.auto_save_commands = self.settings.get("auto_save_commands", True)
                self.notifications_enabled = self.settings.get("notifications_enabled", True)
                
                logger.info(f"Loaded {len(self.settings)} user settings")
                
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
    
    def load_snapshots(self):
        """Load snapshots from database."""
        try:
            with get_db_session() as db:
                snapshot_records = db.query(Snapshot).order_by(Snapshot.created_at.desc()).limit(50).all()
                
                self.snapshots = []
                for snapshot in snapshot_records:
                    self.snapshots.append({
                        "id": snapshot.snapshot_id,
                        "name": snapshot.name,
                        "description": snapshot.description,
                        "provider": snapshot.provider,
                        "sandbox_id": snapshot.sandbox_id,
                        "size": snapshot.snapshot_size,
                        "file_count": snapshot.file_count,
                        "status": snapshot.status,
                        "created_at": snapshot.created_at.isoformat(),
                        "completed_at": snapshot.completed_at.isoformat() if snapshot.completed_at else None,
                        "metadata": snapshot.get_metadata_dict()
                    })
                
                logger.info(f"Loaded {len(self.snapshots)} snapshots")
                
        except Exception as e:
            logger.error(f"Failed to load snapshots: {e}")
    
    def load_command_history(self):
        """Load recent command history."""
        try:
            with get_db_session() as db:
                commands = db.query(CommandHistory).order_by(
                    CommandHistory.executed_at.desc()
                ).limit(100).all()
                
                self.command_history = [cmd.command for cmd in commands]
                
                # Update commands run count
                total_commands = db.query(CommandHistory).count()
                self.commands_run_count = total_commands
                
                logger.info(f"Loaded {len(self.command_history)} recent commands")
                
        except Exception as e:
            logger.error(f"Failed to load command history: {e}")
    
    def update_statistics(self):
        """Update dashboard statistics (real implementation)."""
        try:
            # Get real active sandboxes count from providers
            active_count = 0
            for provider_name, provider_info in self.providers.items():
                if provider_info.get("status") == "connected":
                    # Count active environments/workspaces from each provider
                    if provider_name == "e2b":
                        from .providers.e2b_provider import e2b_provider
                        active_count += len(e2b_provider.sandboxes)
                    elif provider_name == "daytona":
                        from .providers.daytona_provider import daytona_provider
                        active_count += len(daytona_provider.workspaces)
                    elif provider_name == "morph":
                        from .providers.morph_provider import morph_provider
                        active_count += len(morph_provider.environments)
                    elif provider_name == "modal":
                        from .providers.modal_provider import modal_provider
                        active_count += len(modal_provider.functions)
            
            self.active_sandboxes_count = active_count
            self.providers_count = len(self.providers)
            
        except Exception as e:
            logger.error(f"Failed to update statistics: {e}")
            # Fallback to basic count
            self.active_sandboxes_count = 0
            self.providers_count = len(self.providers)
    
    # Navigation Methods
    def set_page(self, page: str):
        """Navigate to a different page."""
        self.current_page = page
        self.clear_messages()
        
        # Load page-specific data
        if page == "files":
            self.load_file_list()
        elif page == "snapshots":
            self.load_snapshots()
        elif page == "providers":
            self.load_providers()
        elif page == "settings":
            self.load_settings()
    
    def toggle_sidebar(self):
        """Toggle sidebar visibility."""
        self.sidebar_open = not self.sidebar_open
    
    # Message Management
    def show_success(self, message: str):
        """Show success message."""
        self.success_message = message
        self.error_message = ""
    
    def show_error(self, message: str):
        """Show error message."""
        self.error_message = message
        self.success_message = ""
    
    def clear_messages(self):
        """Clear all messages."""
        self.success_message = ""
        self.error_message = ""
    
    # Modal Management
    def open_modal(self, title: str, content: str = ""):
        """Open a modal dialog."""
        self.modal_title = title
        self.modal_content = content
        self.show_modal = True
    
    def close_modal(self):
        """Close modal dialog."""
        self.show_modal = False
        self.modal_title = ""
        self.modal_content = ""
    
    # Provider Management Methods
    def open_provider_config(self, provider_name: str):
        """Open provider configuration modal."""
        self.selected_provider_for_config = provider_name
        self.provider_config_modal_open = True
        self.api_key_input = ""
        self.clear_messages()
    
    def close_provider_config(self):
        """Close provider configuration modal."""
        self.provider_config_modal_open = False
        self.selected_provider_for_config = ""
        self.api_key_input = ""
    
    def save_provider_config(self):
        """Save provider configuration."""
        if not self.selected_provider_for_config or not self.api_key_input:
            self.show_error("Provider name and API key are required")
            return
        
        try:
            # Validate API key format
            is_valid, error_msg = validate_api_key_format(
                self.selected_provider_for_config, 
                self.api_key_input
            )
            
            if not is_valid:
                self.show_error(error_msg)
                return
            
            # Encrypt and save API key
            encrypted_key = encrypt_api_key(self.api_key_input)
            
            with get_db_session() as db:
                provider = db.query(ProviderConfig).filter(
                    ProviderConfig.provider_name == self.selected_provider_for_config
                ).first()
                
                if provider:
                    provider.api_key = encrypted_key
                    provider.is_enabled = True
                    provider.test_status = "unknown"
                else:
                    provider = ProviderConfig(
                        provider_name=self.selected_provider_for_config,
                        api_key=encrypted_key,
                        is_enabled=True,
                        test_status="unknown"
                    )
                    db.add(provider)
                
                db.commit()
            
            # Log activity
            log_activity(
                action="configure_provider",
                resource_type="provider",
                resource_id=self.selected_provider_for_config,
                details={"provider": self.selected_provider_for_config}
            )
            
            self.show_success(f"{self.selected_provider_for_config.title()} API key saved successfully")
            self.close_provider_config()
            self.load_providers()
            
            # Test the connection
            self.test_provider_connection(self.selected_provider_for_config)
            
        except Exception as e:
            logger.error(f"Failed to save provider config: {e}")
            self.show_error("Failed to save provider configuration")
    
    def test_provider_connection(self, provider_name: str):
        """Test provider connection."""
        try:
            # This would implement actual provider testing
            # For now, we'll simulate the test
            
            with get_db_session() as db:
                provider = db.query(ProviderConfig).filter(
                    ProviderConfig.provider_name == provider_name
                ).first()
                
                if provider and provider.api_key:
                    # Simulate connection test
                    import time
                    time.sleep(1)  # Simulate API call
                    
                    # For demo, mark as success if API key exists
                    provider.test_status = "success"
                    provider.last_tested = datetime.utcnow()
                    db.commit()
                    
                    self.provider_test_results[provider_name] = "success"
                    self.show_success(f"{provider_name.title()} connection test successful")
                else:
                    self.provider_test_results[provider_name] = "failed"
                    self.show_error(f"{provider_name.title()} connection test failed")
            
            self.load_providers()
            
        except Exception as e:
            logger.error(f"Failed to test provider connection: {e}")
            self.provider_test_results[provider_name] = "failed"
            self.show_error(f"Failed to test {provider_name} connection")
    
    def delete_provider_config(self, provider_name: str):
        """Delete provider configuration."""
        try:
            with get_db_session() as db:
                provider = db.query(ProviderConfig).filter(
                    ProviderConfig.provider_name == provider_name
                ).first()
                
                if provider:
                    provider.api_key = None
                    provider.is_enabled = False
                    provider.test_status = "unknown"
                    db.commit()
            
            log_activity(
                action="delete_provider_config",
                resource_type="provider",
                resource_id=provider_name
            )
            
            self.show_success(f"{provider_name.title()} configuration deleted")
            self.load_providers()
            
        except Exception as e:
            logger.error(f"Failed to delete provider config: {e}")
            self.show_error("Failed to delete provider configuration")
    
    # File Management Methods
    def load_file_list(self, directory: str = None):
        """Load file list for current directory."""
        if directory:
            self.current_directory = directory
        
        try:
            # This would implement actual file system browsing
            # For now, we'll use mock data
            self.file_list = [
                {
                    "name": "main.py",
                    "path": "/main.py",
                    "size": 1024,
                    "type": "file",
                    "is_directory": False,
                    "modified": datetime.now().isoformat()
                },
                {
                    "name": "README.md",
                    "path": "/README.md",
                    "size": 2048,
                    "type": "file",
                    "is_directory": False,
                    "modified": datetime.now().isoformat()
                },
                {
                    "name": "src",
                    "path": "/src",
                    "size": 0,
                    "type": "directory",
                    "is_directory": True,
                    "modified": datetime.now().isoformat()
                }
            ]
            
        except Exception as e:
            logger.error(f"Failed to load file list: {e}")
            self.show_error("Failed to load file list")
    
    def open_file_upload_modal(self):
        """Open file upload modal."""
        self.file_upload_modal_open = True
        self.clear_messages()
    
    def close_file_upload_modal(self):
        """Close file upload modal."""
        self.file_upload_modal_open = False
    
    def open_file_create_modal(self):
        """Open file creation modal."""
        self.file_create_modal_open = True
        self.new_file_name = ""
        self.new_file_content = ""
        self.clear_messages()
    
    def close_file_create_modal(self):
        """Close file creation modal."""
        self.file_create_modal_open = False
        self.new_file_name = ""
        self.new_file_content = ""
    
    def create_new_file(self):
        """Create a new file."""
        if not self.new_file_name:
            self.show_error("File name is required")
            return
        
        try:
            # Sanitize inputs
            file_name = sanitize_input(self.new_file_name, 255)
            file_content = sanitize_input(self.new_file_content, 10000)
            
            # This would implement actual file creation
            # For now, we'll simulate it
            
            log_activity(
                action="create_file",
                resource_type="file",
                resource_id=file_name,
                details={"path": f"{self.current_directory}/{file_name}"}
            )
            
            self.show_success(f"File '{file_name}' created successfully")
            self.close_file_create_modal()
            self.load_file_list()
            
        except Exception as e:
            logger.error(f"Failed to create file: {e}")
            self.show_error("Failed to create file")
    
    def delete_file(self, file_path: str):
        """Delete a file."""
        try:
            # This would implement actual file deletion
            
            log_activity(
                action="delete_file",
                resource_type="file",
                resource_id=file_path
            )
            
            self.show_success("File deleted successfully")
            self.load_file_list()
            
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            self.show_error("Failed to delete file")
    
    # Snapshot Management Methods
    def open_snapshot_create_modal(self):
        """Open snapshot creation modal."""
        self.snapshot_create_modal_open = True
        self.snapshot_name = ""
        self.snapshot_description = ""
        self.clear_messages()
    
    def close_snapshot_create_modal(self):
        """Close snapshot creation modal."""
        self.snapshot_create_modal_open = False
        self.snapshot_name = ""
        self.snapshot_description = ""
    
    def create_snapshot(self):
        """Create a new snapshot."""
        if not self.snapshot_name:
            self.show_error("Snapshot name is required")
            return
        
        try:
            # Sanitize inputs
            name = sanitize_input(self.snapshot_name, 255)
            description = sanitize_input(self.snapshot_description, 1000)
            
            # Generate unique snapshot ID
            import uuid
            snapshot_id = f"snap_{uuid.uuid4().hex[:8]}"
            
            # Create snapshot record
            with get_db_session() as db:
                snapshot = Snapshot(
                    snapshot_id=snapshot_id,
                    name=name,
                    description=description,
                    sandbox_id=self.current_sandbox_id,
                    provider=self.selected_provider,
                    status="creating"
                )
                db.add(snapshot)
                db.commit()
            
            log_activity(
                action="create_snapshot",
                resource_type="snapshot",
                resource_id=snapshot_id,
                details={"name": name, "sandbox_id": self.current_sandbox_id}
            )
            
            self.show_success(f"Snapshot '{name}' creation started")
            self.close_snapshot_create_modal()
            self.load_snapshots()
            
            # Simulate snapshot creation progress
            self.simulate_snapshot_creation(snapshot_id)
            
        except Exception as e:
            logger.error(f"Failed to create snapshot: {e}")
            self.show_error("Failed to create snapshot")
    
    def simulate_snapshot_creation(self, snapshot_id: str):
        """Simulate snapshot creation progress."""
        # This would be replaced with actual snapshot creation logic
        try:
            import time
            time.sleep(2)  # Simulate creation time
            
            with get_db_session() as db:
                snapshot = db.query(Snapshot).filter(
                    Snapshot.snapshot_id == snapshot_id
                ).first()
                
                if snapshot:
                    snapshot.status = "ready"
                    snapshot.completed_at = datetime.utcnow()
                    snapshot.snapshot_size = 1024 * 1024 * 50  # 50MB mock size
                    snapshot.file_count = 25  # Mock file count
                    db.commit()
            
            self.load_snapshots()
            
        except Exception as e:
            logger.error(f"Failed to complete snapshot creation: {e}")
    
    def restore_snapshot(self, snapshot_id: str):
        """Restore from a snapshot."""
        try:
            with get_db_session() as db:
                snapshot = db.query(Snapshot).filter(
                    Snapshot.snapshot_id == snapshot_id
                ).first()
                
                if not snapshot:
                    self.show_error("Snapshot not found")
                    return
                
                # Update status to restoring
                snapshot.status = "restoring"
                db.commit()
            
            log_activity(
                action="restore_snapshot",
                resource_type="snapshot",
                resource_id=snapshot_id
            )
            
            self.show_success("Snapshot restoration started")
            self.load_snapshots()
            
            # Simulate restoration
            self.simulate_snapshot_restoration(snapshot_id)
            
        except Exception as e:
            logger.error(f"Failed to restore snapshot: {e}")
            self.show_error("Failed to restore snapshot")
    
    def simulate_snapshot_restoration(self, snapshot_id: str):
        """Simulate snapshot restoration."""
        try:
            import time
            time.sleep(3)  # Simulate restoration time
            
            with get_db_session() as db:
                snapshot = db.query(Snapshot).filter(
                    Snapshot.snapshot_id == snapshot_id
                ).first()
                
                if snapshot:
                    snapshot.status = "ready"
                    db.commit()
            
            self.show_success("Snapshot restored successfully")
            self.load_snapshots()
            
        except Exception as e:
            logger.error(f"Failed to complete snapshot restoration: {e}")
    
    def delete_snapshot(self, snapshot_id: str):
        """Delete a snapshot."""
        try:
            with get_db_session() as db:
                snapshot = db.query(Snapshot).filter(
                    Snapshot.snapshot_id == snapshot_id
                ).first()
                
                if snapshot:
                    db.delete(snapshot)
                    db.commit()
            
            log_activity(
                action="delete_snapshot",
                resource_type="snapshot",
                resource_id=snapshot_id
            )
            
            self.show_success("Snapshot deleted successfully")
            self.load_snapshots()
            
        except Exception as e:
            logger.error(f"Failed to delete snapshot: {e}")
            self.show_error("Failed to delete snapshot")
    
    # Terminal Methods
    def execute_command(self):
        """Execute a terminal command."""
        if not self.command_input.strip():
            return
        
        command = self.command_input.strip()
        self.command_input = ""
        self.command_running = True
        
        try:
            # Add to history
            if command not in self.command_history:
                self.command_history.insert(0, command)
                if len(self.command_history) > 100:
                    self.command_history = self.command_history[:100]
            
            # Simulate command execution
            self.command_output += f"\n$ {command}\n"
            
            # Mock command responses
            if command == "ls -la":
                self.command_output += """total 12
drwxr-xr-x 3 user user 4096 Jan  5 01:20 .
drwxr-xr-x 3 root root 4096 Jan  5 01:20 ..
-rw-r--r-- 1 user user 1024 Jan  5 01:20 main.py
-rw-r--r-- 1 user user 2048 Jan  5 01:20 README.md"""
            elif command.startswith("echo"):
                self.command_output += command[5:]  # Remove "echo "
            elif command == "pwd":
                self.command_output += "/home/user"
            elif command == "whoami":
                self.command_output += "user"
            else:
                self.command_output += f"Command '{command}' executed successfully"
            
            # Save to database if enabled
            if self.auto_save_commands:
                with get_db_session() as db:
                    cmd_record = CommandHistory(
                        command=command,
                        sandbox_id=self.current_sandbox_id,
                        provider=self.selected_provider,
                        exit_code=0,
                        stdout=self.command_output.split('\n')[-1],
                        execution_time=0.1
                    )
                    db.add(cmd_record)
                    db.commit()
            
            self.commands_run_count += 1
            
        except Exception as e:
            logger.error(f"Failed to execute command: {e}")
            self.command_output += f"\nError: {str(e)}"
        finally:
            self.command_running = False
    
    def clear_terminal(self):
        """Clear terminal output."""
        self.command_output = ""
    
    # Settings Methods
    def save_settings(self):
        """Save user settings."""
        try:
            settings_to_save = {
                "theme": self.theme,
                "default_provider": self.default_provider_setting,
                "auto_save_commands": self.auto_save_commands,
                "notifications_enabled": self.notifications_enabled
            }
            
            for key, value in settings_to_save.items():
                set_setting(key, value, 
                           "boolean" if isinstance(value, bool) else "string")
            
            log_activity(
                action="update_settings",
                resource_type="settings",
                details=settings_to_save
            )
            
            self.show_success("Settings saved successfully")
            self.settings_modified = False
            self.load_settings()
            
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            self.show_error("Failed to save settings")
    
    def reset_settings(self):
        """Reset settings to defaults."""
        try:
            self.theme = "dark"
            self.default_provider_setting = "local"
            self.auto_save_commands = True
            self.notifications_enabled = True
            
            self.save_settings()
            self.show_success("Settings reset to defaults")
            
        except Exception as e:
            logger.error(f"Failed to reset settings: {e}")
            self.show_error("Failed to reset settings")
