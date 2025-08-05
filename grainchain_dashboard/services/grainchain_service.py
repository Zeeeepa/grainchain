"""Production Grainchain Service - Real Implementation."""

import asyncio
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor
import logging

from grainchain import Grainchain
from grainchain.core.interfaces import SandboxStatus, ExecutionResult, FileInfo, SandboxConfig

logger = logging.getLogger(__name__)

class GrainchainService:
    """Production service for Grainchain operations."""
    
    def __init__(self):
        self.grainchain: Optional[Grainchain] = None
        self.active_sessions: Dict[str, Any] = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def initialize(self) -> bool:
        """Initialize Grainchain instance."""
        try:
            self.grainchain = Grainchain()
            logger.info("Grainchain service initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Grainchain: {e}")
            return False
    
    async def get_providers(self) -> List[Dict[str, Any]]:
        """Get available providers with status."""
        if not self.grainchain:
            await self.initialize()
        
        providers = []
        provider_names = ["local", "e2b", "daytona", "morph", "modal"]
        
        for name in provider_names:
            try:
                provider = await self.grainchain.get_provider(name)
                status = "available" if provider else "unavailable"
                
                providers.append({
                    "name": name,
                    "status": status,
                    "description": self._get_provider_description(name),
                    "capabilities": self._get_provider_capabilities(name)
                })
            except Exception as e:
                logger.warning(f"Error checking provider {name}: {e}")
                providers.append({
                    "name": name,
                    "status": "error",
                    "description": self._get_provider_description(name),
                    "capabilities": []
                })
        
        return providers
    
    def _get_provider_description(self, name: str) -> str:
        """Get provider description."""
        descriptions = {
            "local": "Local development environment with direct system access",
            "e2b": "Cloud sandboxes with pre-configured templates and scaling",
            "daytona": "Development workspaces with collaboration features",
            "morph": "Custom VMs with fast snapshots and resource control",
            "modal": "Serverless compute platform with automatic scaling"
        }
        return descriptions.get(name, "Unknown provider")
    
    def _get_provider_capabilities(self, name: str) -> List[str]:
        """Get provider capabilities."""
        capabilities = {
            "local": ["snapshots", "file_operations", "command_execution"],
            "e2b": ["snapshots", "templates", "scaling", "file_operations", "command_execution"],
            "daytona": ["workspaces", "collaboration", "file_operations", "command_execution"],
            "morph": ["custom_vms", "fast_snapshots", "resource_control", "file_operations", "command_execution"],
            "modal": ["serverless", "auto_scaling", "file_operations", "command_execution"]
        }
        return capabilities.get(name, [])
    
    async def create_sandbox(self, provider_name: str, config: Optional[SandboxConfig] = None) -> Dict[str, Any]:
        """Create a new sandbox."""
        if not self.grainchain:
            await self.initialize()
        
        if not config:
            config = SandboxConfig(
                timeout=300,
                working_directory="~",
                auto_cleanup=False,
                keep_alive=True
            )
        
        try:
            sandbox = await self.grainchain.create_sandbox(
                provider=provider_name,
                config=config
            )
            
            # Store session for later use
            self.active_sessions[sandbox.sandbox_id] = sandbox
            
            return {
                "id": sandbox.sandbox_id,
                "provider": provider_name,
                "status": sandbox.status.value,
                "config": config.__dict__
            }
        except Exception as e:
            logger.error(f"Failed to create sandbox with {provider_name}: {e}")
            raise
    
    async def list_sandboxes(self) -> List[Dict[str, Any]]:
        """List all active sandboxes."""
        if not self.grainchain:
            return []
        
        all_sandboxes = []
        provider_names = ["local", "e2b", "daytona", "morph", "modal"]
        
        for provider_name in provider_names:
            try:
                provider = await self.grainchain.get_provider(provider_name)
                if not provider:
                    continue
                
                sandbox_ids = await provider.list_sandboxes()
                for sandbox_id in sandbox_ids:
                    try:
                        status = await provider.get_sandbox_status(sandbox_id)
                        all_sandboxes.append({
                            "id": sandbox_id,
                            "provider": provider_name,
                            "status": status.value,
                            "active": sandbox_id in self.active_sessions
                        })
                    except Exception as e:
                        logger.warning(f"Error getting status for sandbox {sandbox_id}: {e}")
            except Exception as e:
                logger.warning(f"Error listing sandboxes for {provider_name}: {e}")
        
        return all_sandboxes
    
    async def execute_command(self, sandbox_id: str, command: str, **kwargs) -> ExecutionResult:
        """Execute command in sandbox."""
        if sandbox_id not in self.active_sessions:
            raise ValueError(f"No active session for sandbox {sandbox_id}")
        
        session = self.active_sessions[sandbox_id]
        return await session.execute(command, **kwargs)
    
    async def create_snapshot(self, sandbox_id: str) -> str:
        """Create snapshot of sandbox."""
        if sandbox_id not in self.active_sessions:
            raise ValueError(f"No active session for sandbox {sandbox_id}")
        
        session = self.active_sessions[sandbox_id]
        return await session.create_snapshot()
    
    async def restore_snapshot(self, sandbox_id: str, snapshot_id: str) -> None:
        """Restore sandbox from snapshot."""
        if sandbox_id not in self.active_sessions:
            raise ValueError(f"No active session for sandbox {sandbox_id}")
        
        session = self.active_sessions[sandbox_id]
        await session.restore_snapshot(snapshot_id)
    
    async def list_files(self, sandbox_id: str, path: str = "/") -> List[FileInfo]:
        """List files in sandbox."""
        if sandbox_id not in self.active_sessions:
            raise ValueError(f"No active session for sandbox {sandbox_id}")
        
        session = self.active_sessions[sandbox_id]
        return await session.list_files(path)
    
    async def upload_file(self, sandbox_id: str, path: str, content: str | bytes, mode: str = "w") -> None:
        """Upload file to sandbox."""
        if sandbox_id not in self.active_sessions:
            raise ValueError(f"No active session for sandbox {sandbox_id}")
        
        session = self.active_sessions[sandbox_id]
        await session.upload_file(path, content, mode)
    
    async def download_file(self, sandbox_id: str, path: str) -> bytes:
        """Download file from sandbox."""
        if sandbox_id not in self.active_sessions:
            raise ValueError(f"No active session for sandbox {sandbox_id}")
        
        session = self.active_sessions[sandbox_id]
        return await session.download_file(path)
    
    async def terminate_sandbox(self, sandbox_id: str) -> None:
        """Terminate sandbox."""
        if sandbox_id in self.active_sessions:
            session = self.active_sessions[sandbox_id]
            await session.terminate()
            del self.active_sessions[sandbox_id]
    
    async def wake_up_sandbox(self, sandbox_id: str, snapshot_id: Optional[str] = None) -> None:
        """Wake up terminated sandbox."""
        # This would need to be implemented based on provider capabilities
        raise NotImplementedError("Wake up functionality not yet implemented")
    
    async def cleanup(self) -> None:
        """Cleanup all resources."""
        for session in self.active_sessions.values():
            try:
                await session.close()
            except Exception as e:
                logger.warning(f"Error closing session: {e}")
        
        self.active_sessions.clear()
        
        if self.grainchain:
            # Cleanup providers if they support it
            provider_names = ["local", "e2b", "daytona", "morph", "modal"]
            for name in provider_names:
                try:
                    provider = await self.grainchain.get_provider(name)
                    if provider and hasattr(provider, 'cleanup'):
                        await provider.cleanup()
                except Exception as e:
                    logger.warning(f"Error cleaning up provider {name}: {e}")
    
    def get_session(self, sandbox_id: str):
        """Get active session for sandbox."""
        return self.active_sessions.get(sandbox_id)
    
    def has_active_session(self, sandbox_id: str) -> bool:
        """Check if sandbox has active session."""
        return sandbox_id in self.active_sessions

# Global service instance
grainchain_service = GrainchainService()
