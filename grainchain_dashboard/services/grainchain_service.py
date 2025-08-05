"""Service layer for Grainchain operations with async-to-sync bridging."""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime

from grainchain import Sandbox, SandboxConfig, get_providers_info, check_provider
from grainchain.core.interfaces import ExecutionResult, FileInfo, SandboxStatus
from grainchain.core.exceptions import GrainchainError, ProviderError, TimeoutError

from grainchain_dashboard.config import config, get_provider_config, ProviderConfig

logger = logging.getLogger(__name__)

@dataclass
class SandboxInfo:
    """Information about an active sandbox."""
    sandbox_id: str
    provider: str
    status: SandboxStatus
    created_at: datetime
    config: SandboxConfig
    last_activity: datetime

@dataclass
class SnapshotInfo:
    """Information about a sandbox snapshot."""
    snapshot_id: str
    sandbox_id: str
    provider: str
    created_at: datetime
    description: str
    size_mb: Optional[float] = None

class GrainchainService:
    """Service layer that bridges async Grainchain operations with sync Reflex."""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.active_sandboxes: Dict[str, Sandbox] = {}
        self.sandbox_info: Dict[str, SandboxInfo] = {}
        self.snapshots: Dict[str, List[SnapshotInfo]] = {}  # sandbox_id -> snapshots
        
    def _run_async(self, coro):
        """Run async coroutine in thread pool to avoid blocking Reflex."""
        try:
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Error running async operation: {e}")
            raise
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers."""
        try:
            providers_info = self._run_async(self._get_providers_info_async())
            return providers_info
        except Exception as e:
            logger.error(f"Error getting provider status: {e}")
            return {}
    
    async def _get_providers_info_async(self) -> Dict[str, Dict[str, Any]]:
        """Async version of provider info retrieval."""
        providers_info = get_providers_info()
        result = {}
        
        for name, info in providers_info.items():
            result[name] = {
                "available": info.available,
                "dependencies_installed": info.dependencies_installed,
                "config_valid": info.config_valid,
                "missing_config": info.missing_config,
                "setup_instructions": info.setup_instructions
            }
        
        return result
    
    def create_sandbox(self, provider: str, sandbox_config: Optional[Dict[str, Any]] = None) -> Tuple[bool, str, Optional[str]]:
        """Create a new sandbox. Returns (success, message, sandbox_id)."""
        try:
            provider_config = get_provider_config(provider)
            if not provider_config or not provider_config.enabled:
                return False, f"Provider {provider} is not available", None
            
            # Create sandbox configuration
            config_dict = sandbox_config or {}
            if provider_config.config:
                config_dict.update(provider_config.config)
            
            grainchain_config = SandboxConfig(**config_dict)
            
            # Create sandbox asynchronously
            sandbox_id = self._run_async(self._create_sandbox_async(provider, grainchain_config))
            
            return True, f"Sandbox created successfully", sandbox_id
            
        except Exception as e:
            logger.error(f"Error creating sandbox: {e}")
            return False, f"Failed to create sandbox: {str(e)}", None
    
    async def _create_sandbox_async(self, provider: str, config: SandboxConfig) -> str:
        """Async sandbox creation."""
        sandbox = Sandbox(provider=provider, config=config)
        await sandbox.__aenter__()  # Initialize the sandbox
        
        sandbox_id = sandbox.sandbox_id
        self.active_sandboxes[sandbox_id] = sandbox
        
        # Store sandbox info
        self.sandbox_info[sandbox_id] = SandboxInfo(
            sandbox_id=sandbox_id,
            provider=provider,
            status=sandbox.status,
            created_at=datetime.now(),
            config=config,
            last_activity=datetime.now()
        )
        
        return sandbox_id
    
    def execute_command(self, sandbox_id: str, command: str, timeout: Optional[int] = None) -> Tuple[bool, str, Optional[ExecutionResult]]:
        """Execute a command in a sandbox. Returns (success, message, result)."""
        try:
            if sandbox_id not in self.active_sandboxes:
                return False, "Sandbox not found", None
            
            result = self._run_async(self._execute_command_async(sandbox_id, command, timeout))
            
            # Update last activity
            if sandbox_id in self.sandbox_info:
                self.sandbox_info[sandbox_id].last_activity = datetime.now()
            
            return True, "Command executed successfully", result
            
        except TimeoutError:
            return False, "Command timed out", None
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return False, f"Failed to execute command: {str(e)}", None
    
    async def _execute_command_async(self, sandbox_id: str, command: str, timeout: Optional[int]) -> ExecutionResult:
        """Async command execution."""
        sandbox = self.active_sandboxes[sandbox_id]
        return await sandbox.execute(command, timeout=timeout)
    
    def upload_file(self, sandbox_id: str, file_path: str, content: str) -> Tuple[bool, str]:
        """Upload a file to sandbox. Returns (success, message)."""
        try:
            if sandbox_id not in self.active_sandboxes:
                return False, "Sandbox not found"
            
            self._run_async(self._upload_file_async(sandbox_id, file_path, content))
            return True, "File uploaded successfully"
            
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return False, f"Failed to upload file: {str(e)}"
    
    async def _upload_file_async(self, sandbox_id: str, file_path: str, content: str):
        """Async file upload."""
        sandbox = self.active_sandboxes[sandbox_id]
        await sandbox.upload_file(file_path, content)
    
    def download_file(self, sandbox_id: str, file_path: str) -> Tuple[bool, str, Optional[bytes]]:
        """Download a file from sandbox. Returns (success, message, content)."""
        try:
            if sandbox_id not in self.active_sandboxes:
                return False, "Sandbox not found", None
            
            content = self._run_async(self._download_file_async(sandbox_id, file_path))
            return True, "File downloaded successfully", content
            
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return False, f"Failed to download file: {str(e)}", None
    
    async def _download_file_async(self, sandbox_id: str, file_path: str) -> bytes:
        """Async file download."""
        sandbox = self.active_sandboxes[sandbox_id]
        return await sandbox.download_file(file_path)
    
    def list_files(self, sandbox_id: str, path: str = "/") -> Tuple[bool, str, Optional[List[FileInfo]]]:
        """List files in sandbox directory. Returns (success, message, files)."""
        try:
            if sandbox_id not in self.active_sandboxes:
                return False, "Sandbox not found", None
            
            files = self._run_async(self._list_files_async(sandbox_id, path))
            return True, "Files listed successfully", files
            
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return False, f"Failed to list files: {str(e)}", None
    
    async def _list_files_async(self, sandbox_id: str, path: str) -> List[FileInfo]:
        """Async file listing."""
        sandbox = self.active_sandboxes[sandbox_id]
        return await sandbox.list_files(path)
    
    def create_snapshot(self, sandbox_id: str, description: str = "") -> Tuple[bool, str, Optional[str]]:
        """Create a snapshot of sandbox. Returns (success, message, snapshot_id)."""
        try:
            if sandbox_id not in self.active_sandboxes:
                return False, "Sandbox not found", None
            
            snapshot_id = self._run_async(self._create_snapshot_async(sandbox_id))
            
            # Store snapshot info
            if sandbox_id not in self.snapshots:
                self.snapshots[sandbox_id] = []
            
            snapshot_info = SnapshotInfo(
                snapshot_id=snapshot_id,
                sandbox_id=sandbox_id,
                provider=self.sandbox_info[sandbox_id].provider,
                created_at=datetime.now(),
                description=description or f"Snapshot created at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            self.snapshots[sandbox_id].append(snapshot_info)
            
            return True, "Snapshot created successfully", snapshot_id
            
        except NotImplementedError:
            return False, "Snapshots not supported by this provider", None
        except Exception as e:
            logger.error(f"Error creating snapshot: {e}")
            return False, f"Failed to create snapshot: {str(e)}", None
    
    async def _create_snapshot_async(self, sandbox_id: str) -> str:
        """Async snapshot creation."""
        sandbox = self.active_sandboxes[sandbox_id]
        return await sandbox.create_snapshot()
    
    def restore_snapshot(self, sandbox_id: str, snapshot_id: str) -> Tuple[bool, str]:
        """Restore sandbox from snapshot. Returns (success, message)."""
        try:
            if sandbox_id not in self.active_sandboxes:
                return False, "Sandbox not found"
            
            self._run_async(self._restore_snapshot_async(sandbox_id, snapshot_id))
            return True, "Snapshot restored successfully"
            
        except NotImplementedError:
            return False, "Snapshots not supported by this provider"
        except Exception as e:
            logger.error(f"Error restoring snapshot: {e}")
            return False, f"Failed to restore snapshot: {str(e)}"
    
    async def _restore_snapshot_async(self, sandbox_id: str, snapshot_id: str):
        """Async snapshot restoration."""
        sandbox = self.active_sandboxes[sandbox_id]
        await sandbox.restore_snapshot(snapshot_id)
    
    def delete_snapshot(self, sandbox_id: str, snapshot_id: str) -> Tuple[bool, str]:
        """Delete a snapshot. Returns (success, message)."""
        try:
            # Remove from local storage
            if sandbox_id in self.snapshots:
                self.snapshots[sandbox_id] = [
                    s for s in self.snapshots[sandbox_id] 
                    if s.snapshot_id != snapshot_id
                ]
            
            return True, "Snapshot deleted successfully"
            
        except Exception as e:
            logger.error(f"Error deleting snapshot: {e}")
            return False, f"Failed to delete snapshot: {str(e)}"
    
    def get_sandbox_list(self) -> List[SandboxInfo]:
        """Get list of active sandboxes."""
        return list(self.sandbox_info.values())
    
    def get_snapshots(self, sandbox_id: str) -> List[SnapshotInfo]:
        """Get snapshots for a sandbox."""
        return self.snapshots.get(sandbox_id, [])
    
    def close_sandbox(self, sandbox_id: str) -> Tuple[bool, str]:
        """Close and cleanup a sandbox. Returns (success, message)."""
        try:
            if sandbox_id not in self.active_sandboxes:
                return False, "Sandbox not found"
            
            self._run_async(self._close_sandbox_async(sandbox_id))
            
            # Remove from tracking
            del self.active_sandboxes[sandbox_id]
            if sandbox_id in self.sandbox_info:
                self.sandbox_info[sandbox_id].status = SandboxStatus.STOPPED
            
            return True, "Sandbox closed successfully"
            
        except Exception as e:
            logger.error(f"Error closing sandbox: {e}")
            return False, f"Failed to close sandbox: {str(e)}"
    
    async def _close_sandbox_async(self, sandbox_id: str):
        """Async sandbox closure."""
        sandbox = self.active_sandboxes[sandbox_id]
        await sandbox.__aexit__(None, None, None)
    
    def cleanup_all(self):
        """Cleanup all active sandboxes."""
        sandbox_ids = list(self.active_sandboxes.keys())
        for sandbox_id in sandbox_ids:
            try:
                self.close_sandbox(sandbox_id)
            except Exception as e:
                logger.error(f"Error cleaning up sandbox {sandbox_id}: {e}")

# Global service instance
grainchain_service = GrainchainService()
