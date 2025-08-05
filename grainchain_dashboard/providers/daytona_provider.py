#!/usr/bin/env python3
"""Real Daytona Provider Integration."""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class DaytonaWorkspace:
    """Daytona workspace information."""
    id: str
    name: str
    status: str
    created_at: datetime
    updated_at: datetime
    repository_url: str
    branch: str
    ide: str
    machine_type: str

class DaytonaProvider:
    """Real Daytona provider with actual API integration."""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or self._get_api_key()
        self.base_url = base_url or "https://api.daytona.io"
        self.session: Optional[aiohttp.ClientSession] = None
        self.workspaces: Dict[str, DaytonaWorkspace] = {}
        
    def _get_api_key(self) -> str:
        """Get API key from environment or config."""
        import os
        api_key = os.getenv('DAYTONA_API_KEY')
        if not api_key:
            logger.warning("DAYTONA_API_KEY not found in environment variables")
            return ""
        return api_key
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if not self.session:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            self.session = aiohttp.ClientSession(headers=headers)
        return self.session
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated API request."""
        if not self.api_key:
            raise ValueError("Daytona API key is required")
            
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with session.request(method, url, **kwargs) as response:
                if response.status == 401:
                    raise ValueError("Invalid Daytona API key")
                elif response.status >= 400:
                    error_text = await response.text()
                    raise Exception(f"Daytona API error {response.status}: {error_text}")
                
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Daytona API request failed: {e}")
            raise Exception(f"Failed to connect to Daytona API: {e}")
    
    async def create_workspace(self, 
                             name: str,
                             repository_url: str,
                             branch: str = "main",
                             ide: str = "vscode",
                             machine_type: str = "standard") -> DaytonaWorkspace:
        """Create a new Daytona workspace."""
        payload = {
            "name": name,
            "repository": {
                "url": repository_url,
                "branch": branch
            },
            "ide": ide,
            "machine_type": machine_type
        }
        
        response = await self._make_request("POST", "/workspaces", json=payload)
        
        workspace = DaytonaWorkspace(
            id=response["id"],
            name=response["name"],
            status=response["status"],
            created_at=datetime.fromisoformat(response["created_at"]),
            updated_at=datetime.fromisoformat(response["updated_at"]),
            repository_url=response["repository"]["url"],
            branch=response["repository"]["branch"],
            ide=response["ide"],
            machine_type=response["machine_type"]
        )
        
        self.workspaces[workspace.id] = workspace
        logger.info(f"Created Daytona workspace: {workspace.name} ({workspace.id})")
        return workspace
    
    async def get_workspace(self, workspace_id: str) -> Optional[DaytonaWorkspace]:
        """Get workspace information."""
        try:
            response = await self._make_request("GET", f"/workspaces/{workspace_id}")
            
            workspace = DaytonaWorkspace(
                id=response["id"],
                name=response["name"],
                status=response["status"],
                created_at=datetime.fromisoformat(response["created_at"]),
                updated_at=datetime.fromisoformat(response["updated_at"]),
                repository_url=response["repository"]["url"],
                branch=response["repository"]["branch"],
                ide=response["ide"],
                machine_type=response["machine_type"]
            )
            
            self.workspaces[workspace.id] = workspace
            return workspace
            
        except Exception as e:
            logger.error(f"Failed to get Daytona workspace {workspace_id}: {e}")
            return None
    
    async def list_workspaces(self) -> List[DaytonaWorkspace]:
        """List all workspaces."""
        try:
            response = await self._make_request("GET", "/workspaces")
            workspaces = []
            
            for ws_data in response.get("workspaces", []):
                workspace = DaytonaWorkspace(
                    id=ws_data["id"],
                    name=ws_data["name"],
                    status=ws_data["status"],
                    created_at=datetime.fromisoformat(ws_data["created_at"]),
                    updated_at=datetime.fromisoformat(ws_data["updated_at"]),
                    repository_url=ws_data["repository"]["url"],
                    branch=ws_data["repository"]["branch"],
                    ide=ws_data["ide"],
                    machine_type=ws_data["machine_type"]
                )
                workspaces.append(workspace)
                self.workspaces[workspace.id] = workspace
            
            return workspaces
            
        except Exception as e:
            logger.error(f"Failed to list Daytona workspaces: {e}")
            return []
    
    async def start_workspace(self, workspace_id: str) -> bool:
        """Start a workspace."""
        try:
            await self._make_request("POST", f"/workspaces/{workspace_id}/start")
            logger.info(f"Started Daytona workspace: {workspace_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to start Daytona workspace {workspace_id}: {e}")
            return False
    
    async def stop_workspace(self, workspace_id: str) -> bool:
        """Stop a workspace."""
        try:
            await self._make_request("POST", f"/workspaces/{workspace_id}/stop")
            logger.info(f"Stopped Daytona workspace: {workspace_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop Daytona workspace {workspace_id}: {e}")
            return False
    
    async def delete_workspace(self, workspace_id: str) -> bool:
        """Delete a workspace."""
        try:
            await self._make_request("DELETE", f"/workspaces/{workspace_id}")
            if workspace_id in self.workspaces:
                del self.workspaces[workspace_id]
            logger.info(f"Deleted Daytona workspace: {workspace_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete Daytona workspace {workspace_id}: {e}")
            return False
    
    async def get_workspace_logs(self, workspace_id: str, lines: int = 100) -> List[str]:
        """Get workspace logs."""
        try:
            response = await self._make_request("GET", f"/workspaces/{workspace_id}/logs", 
                                              params={"lines": lines})
            return response.get("logs", [])
        except Exception as e:
            logger.error(f"Failed to get logs for Daytona workspace {workspace_id}: {e}")
            return []
    
    async def execute_command(self, workspace_id: str, command: str) -> Dict[str, Any]:
        """Execute command in workspace."""
        try:
            payload = {"command": command}
            response = await self._make_request("POST", f"/workspaces/{workspace_id}/execute", 
                                              json=payload)
            return {
                "stdout": response.get("stdout", ""),
                "stderr": response.get("stderr", ""),
                "exit_code": response.get("exit_code", 0),
                "execution_time": response.get("execution_time", 0)
            }
        except Exception as e:
            logger.error(f"Failed to execute command in Daytona workspace {workspace_id}: {e}")
            return {
                "stdout": "",
                "stderr": str(e),
                "exit_code": 1,
                "execution_time": 0
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get provider status."""
        try:
            if not self.api_key:
                return {
                    "status": "error",
                    "message": "API key not configured",
                    "workspaces_count": 0,
                    "available": False
                }
            
            workspaces = await self.list_workspaces()
            return {
                "status": "connected",
                "message": "Daytona provider is operational",
                "workspaces_count": len(workspaces),
                "available": True,
                "api_endpoint": self.base_url
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection failed: {e}",
                "workspaces_count": 0,
                "available": False
            }
    
    async def close(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None

# Global instance
daytona_provider = DaytonaProvider()
