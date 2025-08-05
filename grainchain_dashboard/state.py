"""Main state management for Grainchain Dashboard."""

import reflex as rx
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import asdict

from grainchain_dashboard.services.grainchain_service import grainchain_service, SandboxInfo, SnapshotInfo
from grainchain_dashboard.config import config, get_enabled_providers, get_provider_config, update_provider_config
from grainchain.core.interfaces import ExecutionResult, FileInfo

class DashboardState(rx.State):
    """Main state for the Grainchain Dashboard."""
    
    # UI State
    current_page: str = "dashboard"
    sidebar_open: bool = True
    loading: bool = False
    error_message: str = ""
    success_message: str = ""
    
    # Provider State
    providers: Dict[str, Dict[str, Any]] = {}
    selected_provider: str = config.default_provider
    provider_health_status: Dict[str, str] = {}
    
    # Sandbox State
    active_sandboxes: List[Dict[str, Any]] = []
    selected_sandbox_id: str = ""
    sandbox_status: Dict[str, str] = {}
    
    # Command Execution State
    command_input: str = ""
    command_history: List[str] = []
    command_output: str = ""
    command_running: bool = False
    
    # File Management State
    current_directory: str = "/"
    file_list: List[Dict[str, Any]] = []
    selected_files: List[str] = []
    upload_content: str = ""
    upload_filename: str = ""
    
    # Snapshot State
    snapshots: List[Dict[str, Any]] = []
    selected_snapshot_id: str = ""
    snapshot_description: str = ""
    
    # Settings State
    settings_open: bool = False
    provider_settings: Dict[str, Dict[str, Any]] = {}
    
    def __init__(self):
        super().__init__()
        self.refresh_providers()
        self.refresh_sandboxes()
    
    # Provider Management
    def refresh_providers(self):
        """Refresh provider status and information."""
        self.loading = True
        try:
            # Get provider status from service
            provider_status = grainchain_service.get_provider_status()
            self.providers = provider_status
            
            # Update health status
            for name, info in provider_status.items():
                self.provider_health_status[name] = "healthy" if info.get("available", False) else "unhealthy"
            
            # Load provider settings
            enabled_providers = get_enabled_providers()
            self.provider_settings = {
                name: {
                    "enabled": config.enabled,
                    "api_key": config.api_key or "",
                    **config.config
                }
                for name, config in enabled_providers.items()
            }
            
            self.success_message = "Providers refreshed successfully"
        except Exception as e:
            self.error_message = f"Failed to refresh providers: {str(e)}"
        finally:
            self.loading = False
    
    def select_provider(self, provider_name: str):
        """Select a provider for operations."""
        if provider_name in self.providers:
            self.selected_provider = provider_name
            self.success_message = f"Selected provider: {provider_name}"
        else:
            self.error_message = f"Provider {provider_name} not available"
    
    def update_provider_setting(self, provider: str, key: str, value: str):
        """Update a provider setting."""
        if provider not in self.provider_settings:
            self.provider_settings[provider] = {}
        
        self.provider_settings[provider][key] = value
        
        # Update the actual configuration
        update_provider_config(provider, {key: value})
    
    def save_provider_settings(self):
        """Save all provider settings."""
        try:
            for provider, settings in self.provider_settings.items():
                update_provider_config(provider, settings)
            
            self.success_message = "Provider settings saved successfully"
            self.settings_open = False
            self.refresh_providers()
        except Exception as e:
            self.error_message = f"Failed to save settings: {str(e)}"
    
    # Sandbox Management
    def refresh_sandboxes(self):
        """Refresh the list of active sandboxes."""
        try:
            sandbox_list = grainchain_service.get_sandbox_list()
            self.active_sandboxes = [
                {
                    "sandbox_id": info.sandbox_id,
                    "provider": info.provider,
                    "status": info.status.value,
                    "created_at": info.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "last_activity": info.last_activity.strftime("%Y-%m-%d %H:%M:%S")
                }
                for info in sandbox_list
            ]
        except Exception as e:
            self.error_message = f"Failed to refresh sandboxes: {str(e)}"
    
    def create_sandbox(self):
        """Create a new sandbox with the selected provider."""
        self.loading = True
        try:
            success, message, sandbox_id = grainchain_service.create_sandbox(self.selected_provider)
            
            if success and sandbox_id:
                self.selected_sandbox_id = sandbox_id
                self.success_message = message
                self.refresh_sandboxes()
                self.refresh_files()
            else:
                self.error_message = message
        except Exception as e:
            self.error_message = f"Failed to create sandbox: {str(e)}"
        finally:
            self.loading = False
    
    def select_sandbox(self, sandbox_id: str):
        """Select a sandbox for operations."""
        self.selected_sandbox_id = sandbox_id
        self.refresh_files()
        self.refresh_snapshots()
        self.success_message = f"Selected sandbox: {sandbox_id[:8]}..."
    
    def close_sandbox(self, sandbox_id: str):
        """Close a sandbox."""
        try:
            success, message = grainchain_service.close_sandbox(sandbox_id)
            
            if success:
                self.success_message = message
                if self.selected_sandbox_id == sandbox_id:
                    self.selected_sandbox_id = ""
                self.refresh_sandboxes()
            else:
                self.error_message = message
        except Exception as e:
            self.error_message = f"Failed to close sandbox: {str(e)}"
    
    # Command Execution
    def execute_command(self):
        """Execute a command in the selected sandbox."""
        if not self.selected_sandbox_id:
            self.error_message = "No sandbox selected"
            return
        
        if not self.command_input.strip():
            self.error_message = "Please enter a command"
            return
        
        self.command_running = True
        command = self.command_input.strip()
        
        try:
            success, message, result = grainchain_service.execute_command(
                self.selected_sandbox_id, 
                command
            )
            
            if success and result:
                # Add to history
                self.command_history.append(f"$ {command}")
                
                # Update output
                output_text = f"Command: {command}\n"
                output_text += f"Return Code: {result.return_code}\n"
                output_text += f"Execution Time: {result.execution_time:.2f}s\n\n"
                
                if result.stdout:
                    output_text += f"STDOUT:\n{result.stdout}\n\n"
                
                if result.stderr:
                    output_text += f"STDERR:\n{result.stderr}\n\n"
                
                self.command_output = output_text
                self.command_input = ""  # Clear input
                
                if result.success:
                    self.success_message = "Command executed successfully"
                else:
                    self.error_message = f"Command failed with return code {result.return_code}"
            else:
                self.error_message = message
                
        except Exception as e:
            self.error_message = f"Failed to execute command: {str(e)}"
        finally:
            self.command_running = False
    
    def clear_command_output(self):
        """Clear command output and history."""
        self.command_output = ""
        self.command_history = []
        self.success_message = "Command output cleared"
    
    # File Management
    def refresh_files(self):
        """Refresh file list for current directory."""
        if not self.selected_sandbox_id:
            self.file_list = []
            return
        
        try:
            success, message, files = grainchain_service.list_files(
                self.selected_sandbox_id, 
                self.current_directory
            )
            
            if success and files:
                self.file_list = [
                    {
                        "name": file.name,
                        "path": file.path,
                        "size": file.size,
                        "is_directory": file.is_directory,
                        "modified_time": datetime.fromtimestamp(file.modified_time).strftime("%Y-%m-%d %H:%M:%S"),
                        "permissions": file.permissions
                    }
                    for file in files
                ]
            else:
                self.file_list = []
                if not success:
                    self.error_message = message
                    
        except Exception as e:
            self.error_message = f"Failed to refresh files: {str(e)}"
            self.file_list = []
    
    def navigate_to_directory(self, path: str):
        """Navigate to a directory."""
        self.current_directory = path
        self.refresh_files()
    
    def upload_file(self):
        """Upload a file to the current directory."""
        if not self.selected_sandbox_id:
            self.error_message = "No sandbox selected"
            return
        
        if not self.upload_filename or not self.upload_content:
            self.error_message = "Please provide filename and content"
            return
        
        try:
            file_path = f"{self.current_directory.rstrip('/')}/{self.upload_filename}"
            success, message = grainchain_service.upload_file(
                self.selected_sandbox_id,
                file_path,
                self.upload_content
            )
            
            if success:
                self.success_message = message
                self.upload_filename = ""
                self.upload_content = ""
                self.refresh_files()
            else:
                self.error_message = message
                
        except Exception as e:
            self.error_message = f"Failed to upload file: {str(e)}"
    
    # Snapshot Management
    def refresh_snapshots(self):
        """Refresh snapshots for the selected sandbox."""
        if not self.selected_sandbox_id:
            self.snapshots = []
            return
        
        try:
            snapshot_list = grainchain_service.get_snapshots(self.selected_sandbox_id)
            self.snapshots = [
                {
                    "snapshot_id": info.snapshot_id,
                    "sandbox_id": info.sandbox_id,
                    "provider": info.provider,
                    "created_at": info.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "description": info.description,
                    "size_mb": info.size_mb
                }
                for info in snapshot_list
            ]
        except Exception as e:
            self.error_message = f"Failed to refresh snapshots: {str(e)}"
    
    def create_snapshot(self):
        """Create a snapshot of the selected sandbox."""
        if not self.selected_sandbox_id:
            self.error_message = "No sandbox selected"
            return
        
        self.loading = True
        try:
            success, message, snapshot_id = grainchain_service.create_snapshot(
                self.selected_sandbox_id,
                self.snapshot_description
            )
            
            if success and snapshot_id:
                self.success_message = message
                self.snapshot_description = ""
                self.refresh_snapshots()
            else:
                self.error_message = message
                
        except Exception as e:
            self.error_message = f"Failed to create snapshot: {str(e)}"
        finally:
            self.loading = False
    
    def restore_snapshot(self, snapshot_id: str):
        """Restore a snapshot."""
        if not self.selected_sandbox_id:
            self.error_message = "No sandbox selected"
            return
        
        self.loading = True
        try:
            success, message = grainchain_service.restore_snapshot(
                self.selected_sandbox_id,
                snapshot_id
            )
            
            if success:
                self.success_message = message
                self.refresh_files()  # Refresh files after restore
            else:
                self.error_message = message
                
        except Exception as e:
            self.error_message = f"Failed to restore snapshot: {str(e)}"
        finally:
            self.loading = False
    
    def delete_snapshot(self, snapshot_id: str):
        """Delete a snapshot."""
        try:
            success, message = grainchain_service.delete_snapshot(
                self.selected_sandbox_id,
                snapshot_id
            )
            
            if success:
                self.success_message = message
                self.refresh_snapshots()
            else:
                self.error_message = message
                
        except Exception as e:
            self.error_message = f"Failed to delete snapshot: {str(e)}"
    
    # UI State Management
    def toggle_sidebar(self):
        """Toggle sidebar visibility."""
        self.sidebar_open = not self.sidebar_open
    
    def set_page(self, page: str):
        """Set the current page."""
        self.current_page = page
    
    def open_settings(self):
        """Open settings dialog."""
        self.settings_open = True
    
    def close_settings(self):
        """Close settings dialog."""
        self.settings_open = False
    
    def clear_messages(self):
        """Clear error and success messages."""
        self.error_message = ""
        self.success_message = ""
