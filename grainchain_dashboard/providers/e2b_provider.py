#!/usr/bin/env python3
"""E2B Cloud Sandboxes provider integration."""

import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class E2BProvider:
    """E2B Cloud Sandboxes provider."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://api.e2b.dev"
        self.session = None
        self.sandboxes: Dict[str, Dict[str, Any]] = {}
    
    async def init_session(self):
        """Initialize HTTP session."""
        if not self.session:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
    
    async def close_session(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test API connection."""
        if not self.api_key:
            return {"status": "error", "message": "API key not configured"}
        
        try:
            await self.init_session()
            async with self.session.get(f"{self.base_url}/sandboxes") as response:
                if response.status == 200:
                    return {"status": "success", "message": "Connection successful"}
                elif response.status == 401:
                    return {"status": "error", "message": "Invalid API key"}
                else:
                    return {"status": "error", "message": f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"E2B connection test failed: {e}")
            return {"status": "error", "message": str(e)}
    
    async def list_templates(self) -> List[Dict[str, Any]]:
        """List available sandbox templates."""
        try:
            await self.init_session()
            async with self.session.get(f"{self.base_url}/templates") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("templates", [])
                else:
                    logger.error(f"Failed to list templates: HTTP {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error listing templates: {e}")
            return []
    
    async def create_sandbox(self, template_id: str = "base", metadata: Dict[str, Any] = None) -> Optional[str]:
        """Create a new sandbox."""
        try:
            await self.init_session()
            
            payload = {
                "templateID": template_id,
                "metadata": metadata or {}
            }
            
            async with self.session.post(f"{self.base_url}/sandboxes", json=payload) as response:
                if response.status == 201:
                    data = await response.json()
                    sandbox_id = data.get("sandboxID")
                    
                    # Store sandbox info
                    self.sandboxes[sandbox_id] = {
                        "id": sandbox_id,
                        "template_id": template_id,
                        "status": "running",
                        "created_at": datetime.now().isoformat(),
                        "metadata": metadata or {}
                    }
                    
                    return sandbox_id
                else:
                    logger.error(f"Failed to create sandbox: HTTP {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error creating sandbox: {e}")
            return None
    
    async def get_sandbox(self, sandbox_id: str) -> Optional[Dict[str, Any]]:
        """Get sandbox information."""
        try:
            await self.init_session()
            async with self.session.get(f"{self.base_url}/sandboxes/{sandbox_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.error(f"Failed to get sandbox: HTTP {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error getting sandbox: {e}")
            return None
    
    async def list_sandboxes(self) -> List[Dict[str, Any]]:
        """List all sandboxes."""
        try:
            await self.init_session()
            async with self.session.get(f"{self.base_url}/sandboxes") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("sandboxes", [])
                else:
                    logger.error(f"Failed to list sandboxes: HTTP {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error listing sandboxes: {e}")
            return []
    
    async def delete_sandbox(self, sandbox_id: str) -> bool:
        """Delete a sandbox."""
        try:
            await self.init_session()
            async with self.session.delete(f"{self.base_url}/sandboxes/{sandbox_id}") as response:
                if response.status == 204:
                    # Remove from local storage
                    if sandbox_id in self.sandboxes:
                        del self.sandboxes[sandbox_id]
                    return True
                else:
                    logger.error(f"Failed to delete sandbox: HTTP {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error deleting sandbox: {e}")
            return False
    
    async def execute_command(self, sandbox_id: str, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute command in sandbox."""
        try:
            await self.init_session()
            
            payload = {
                "command": command,
                "timeout": timeout
            }
            
            async with self.session.post(f"{self.base_url}/sandboxes/{sandbox_id}/commands", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "stdout": data.get("stdout", ""),
                        "stderr": data.get("stderr", ""),
                        "exit_code": data.get("exitCode", 0),
                        "execution_time": data.get("executionTime", 0)
                    }
                else:
                    logger.error(f"Failed to execute command: HTTP {response.status}")
                    return {"stdout": "", "stderr": "Command execution failed", "exit_code": 1}
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return {"stdout": "", "stderr": str(e), "exit_code": 1}
    
    async def upload_file(self, sandbox_id: str, file_path: str, content: bytes) -> bool:
        """Upload file to sandbox."""
        try:
            await self.init_session()
            
            data = aiohttp.FormData()
            data.add_field('file', content, filename=file_path.split('/')[-1])
            data.add_field('path', file_path)
            
            async with self.session.post(f"{self.base_url}/sandboxes/{sandbox_id}/files", data=data) as response:
                return response.status == 201
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return False
    
    async def download_file(self, sandbox_id: str, file_path: str) -> Optional[bytes]:
        """Download file from sandbox."""
        try:
            await self.init_session()
            async with self.session.get(f"{self.base_url}/sandboxes/{sandbox_id}/files", params={"path": file_path}) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    logger.error(f"Failed to download file: HTTP {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return None
    
    async def list_files(self, sandbox_id: str, directory: str = "/") -> List[Dict[str, Any]]:
        """List files in sandbox directory."""
        try:
            await self.init_session()
            async with self.session.get(f"{self.base_url}/sandboxes/{sandbox_id}/files/list", params={"path": directory}) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("files", [])
                else:
                    logger.error(f"Failed to list files: HTTP {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []
    
    async def get_resource_usage(self, sandbox_id: str) -> Dict[str, Any]:
        """Get sandbox resource usage."""
        try:
            await self.init_session()
            async with self.session.get(f"{self.base_url}/sandboxes/{sandbox_id}/metrics") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "cpu_usage": data.get("cpuUsage", 0),
                        "memory_usage": data.get("memoryUsage", 0),
                        "disk_usage": data.get("diskUsage", 0),
                        "network_in": data.get("networkIn", 0),
                        "network_out": data.get("networkOut", 0)
                    }
                else:
                    return {"cpu_usage": 0, "memory_usage": 0, "disk_usage": 0}
        except Exception as e:
            logger.error(f"Error getting resource usage: {e}")
            return {"cpu_usage": 0, "memory_usage": 0, "disk_usage": 0}
    
    async def create_snapshot(self, sandbox_id: str, name: str) -> Optional[str]:
        """Create sandbox snapshot."""
        try:
            await self.init_session()
            
            payload = {
                "name": name,
                "description": f"Snapshot created at {datetime.now().isoformat()}"
            }
            
            async with self.session.post(f"{self.base_url}/sandboxes/{sandbox_id}/snapshots", json=payload) as response:
                if response.status == 201:
                    data = await response.json()
                    return data.get("snapshotID")
                else:
                    logger.error(f"Failed to create snapshot: HTTP {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error creating snapshot: {e}")
            return None
    
    async def restore_snapshot(self, snapshot_id: str) -> Optional[str]:
        """Restore sandbox from snapshot."""
        try:
            await self.init_session()
            
            payload = {"snapshotID": snapshot_id}
            
            async with self.session.post(f"{self.base_url}/sandboxes/restore", json=payload) as response:
                if response.status == 201:
                    data = await response.json()
                    return data.get("sandboxID")
                else:
                    logger.error(f"Failed to restore snapshot: HTTP {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error restoring snapshot: {e}")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get provider status."""
        return {
            "name": "E2B Cloud Sandboxes",
            "status": "success" if self.api_key else "failed",
            "has_api_key": bool(self.api_key),
            "description": "Cloud sandboxes with templates",
            "features": [
                "Template-based sandboxes",
                "Command execution",
                "File operations",
                "Resource monitoring",
                "Snapshots"
            ],
            "active_sandboxes": len(self.sandboxes)
        }

# Export for use in main app
__all__ = ['E2BProvider']
