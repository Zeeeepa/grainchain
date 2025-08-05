#!/usr/bin/env python3
"""Real Morph Provider Integration."""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MorphEnvironment:
    """Morph environment information."""
    id: str
    name: str
    status: str
    created_at: datetime
    updated_at: datetime
    image: str
    cpu: str
    memory: str
    storage: str
    port_mappings: Dict[str, int]

class MorphProvider:
    """Real Morph provider with actual API integration."""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or self._get_api_key()
        self.base_url = base_url or "https://api.morph.sh"
        self.session: Optional[aiohttp.ClientSession] = None
        self.environments: Dict[str, MorphEnvironment] = {}
        
    def _get_api_key(self) -> str:
        """Get API key from environment or config."""
        import os
        api_key = os.getenv('MORPH_API_KEY')
        if not api_key:
            logger.warning("MORPH_API_KEY not found in environment variables")
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
            raise ValueError("Morph API key is required")
            
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with session.request(method, url, **kwargs) as response:
                if response.status == 401:
                    raise ValueError("Invalid Morph API key")
                elif response.status >= 400:
                    error_text = await response.text()
                    raise Exception(f"Morph API error {response.status}: {error_text}")
                
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Morph API request failed: {e}")
            raise Exception(f"Failed to connect to Morph API: {e}")
    
    async def create_environment(self, 
                               name: str,
                               image: str = "ubuntu:22.04",
                               cpu: str = "1",
                               memory: str = "2Gi",
                               storage: str = "10Gi",
                               port_mappings: Dict[str, int] = None) -> MorphEnvironment:
        """Create a new Morph environment."""
        payload = {
            "name": name,
            "spec": {
                "image": image,
                "resources": {
                    "cpu": cpu,
                    "memory": memory,
                    "storage": storage
                },
                "ports": port_mappings or {"http": 8080}
            }
        }
        
        response = await self._make_request("POST", "/environments", json=payload)
        
        environment = MorphEnvironment(
            id=response["id"],
            name=response["name"],
            status=response["status"],
            created_at=datetime.fromisoformat(response["created_at"]),
            updated_at=datetime.fromisoformat(response["updated_at"]),
            image=response["spec"]["image"],
            cpu=response["spec"]["resources"]["cpu"],
            memory=response["spec"]["resources"]["memory"],
            storage=response["spec"]["resources"]["storage"],
            port_mappings=response["spec"]["ports"]
        )
        
        self.environments[environment.id] = environment
        logger.info(f"Created Morph environment: {environment.name} ({environment.id})")
        return environment
    
    async def get_environment(self, environment_id: str) -> Optional[MorphEnvironment]:
        """Get environment information."""
        try:
            response = await self._make_request("GET", f"/environments/{environment_id}")
            
            environment = MorphEnvironment(
                id=response["id"],
                name=response["name"],
                status=response["status"],
                created_at=datetime.fromisoformat(response["created_at"]),
                updated_at=datetime.fromisoformat(response["updated_at"]),
                image=response["spec"]["image"],
                cpu=response["spec"]["resources"]["cpu"],
                memory=response["spec"]["resources"]["memory"],
                storage=response["spec"]["resources"]["storage"],
                port_mappings=response["spec"]["ports"]
            )
            
            self.environments[environment.id] = environment
            return environment
            
        except Exception as e:
            logger.error(f"Failed to get Morph environment {environment_id}: {e}")
            return None
    
    async def list_environments(self) -> List[MorphEnvironment]:
        """List all environments."""
        try:
            response = await self._make_request("GET", "/environments")
            environments = []
            
            for env_data in response.get("environments", []):
                environment = MorphEnvironment(
                    id=env_data["id"],
                    name=env_data["name"],
                    status=env_data["status"],
                    created_at=datetime.fromisoformat(env_data["created_at"]),
                    updated_at=datetime.fromisoformat(env_data["updated_at"]),
                    image=env_data["spec"]["image"],
                    cpu=env_data["spec"]["resources"]["cpu"],
                    memory=env_data["spec"]["resources"]["memory"],
                    storage=env_data["spec"]["resources"]["storage"],
                    port_mappings=env_data["spec"]["ports"]
                )
                environments.append(environment)
                self.environments[environment.id] = environment
            
            return environments
            
        except Exception as e:
            logger.error(f"Failed to list Morph environments: {e}")
            return []
    
    async def start_environment(self, environment_id: str) -> bool:
        """Start an environment."""
        try:
            await self._make_request("POST", f"/environments/{environment_id}/start")
            logger.info(f"Started Morph environment: {environment_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to start Morph environment {environment_id}: {e}")
            return False
    
    async def stop_environment(self, environment_id: str) -> bool:
        """Stop an environment."""
        try:
            await self._make_request("POST", f"/environments/{environment_id}/stop")
            logger.info(f"Stopped Morph environment: {environment_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to stop Morph environment {environment_id}: {e}")
            return False
    
    async def delete_environment(self, environment_id: str) -> bool:
        """Delete an environment."""
        try:
            await self._make_request("DELETE", f"/environments/{environment_id}")
            if environment_id in self.environments:
                del self.environments[environment_id]
            logger.info(f"Deleted Morph environment: {environment_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete Morph environment {environment_id}: {e}")
            return False
    
    async def get_environment_logs(self, environment_id: str, lines: int = 100) -> List[str]:
        """Get environment logs."""
        try:
            response = await self._make_request("GET", f"/environments/{environment_id}/logs", 
                                              params={"lines": lines})
            return response.get("logs", [])
        except Exception as e:
            logger.error(f"Failed to get logs for Morph environment {environment_id}: {e}")
            return []
    
    async def execute_command(self, environment_id: str, command: str) -> Dict[str, Any]:
        """Execute command in environment."""
        try:
            payload = {"command": command}
            response = await self._make_request("POST", f"/environments/{environment_id}/exec", 
                                              json=payload)
            return {
                "stdout": response.get("stdout", ""),
                "stderr": response.get("stderr", ""),
                "exit_code": response.get("exit_code", 0),
                "execution_time": response.get("execution_time", 0)
            }
        except Exception as e:
            logger.error(f"Failed to execute command in Morph environment {environment_id}: {e}")
            return {
                "stdout": "",
                "stderr": str(e),
                "exit_code": 1,
                "execution_time": 0
            }
    
    async def scale_environment(self, environment_id: str, cpu: str = None, memory: str = None) -> bool:
        """Scale environment resources."""
        try:
            payload = {}
            if cpu:
                payload["cpu"] = cpu
            if memory:
                payload["memory"] = memory
                
            await self._make_request("PATCH", f"/environments/{environment_id}/scale", json=payload)
            logger.info(f"Scaled Morph environment: {environment_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to scale Morph environment {environment_id}: {e}")
            return False
    
    async def get_environment_metrics(self, environment_id: str) -> Dict[str, Any]:
        """Get environment metrics."""
        try:
            response = await self._make_request("GET", f"/environments/{environment_id}/metrics")
            return {
                "cpu_usage": response.get("cpu_usage", 0),
                "memory_usage": response.get("memory_usage", 0),
                "storage_usage": response.get("storage_usage", 0),
                "network_in": response.get("network_in", 0),
                "network_out": response.get("network_out", 0),
                "uptime": response.get("uptime", 0)
            }
        except Exception as e:
            logger.error(f"Failed to get metrics for Morph environment {environment_id}: {e}")
            return {}
    
    async def get_status(self) -> Dict[str, Any]:
        """Get provider status."""
        try:
            if not self.api_key:
                return {
                    "status": "error",
                    "message": "API key not configured",
                    "environments_count": 0,
                    "available": False
                }
            
            environments = await self.list_environments()
            return {
                "status": "connected",
                "message": "Morph provider is operational",
                "environments_count": len(environments),
                "available": True,
                "api_endpoint": self.base_url
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection failed: {e}",
                "environments_count": 0,
                "available": False
            }
    
    async def close(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None

# Global instance
morph_provider = MorphProvider()
