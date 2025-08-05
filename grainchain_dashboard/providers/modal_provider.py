#!/usr/bin/env python3
"""Real Modal Provider Integration."""

import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ModalFunction:
    """Modal function information."""
    id: str
    name: str
    status: str
    created_at: datetime
    updated_at: datetime
    image: str
    cpu: float
    memory: str
    gpu: Optional[str]
    environment: Dict[str, str]

class ModalProvider:
    """Real Modal provider with actual API integration."""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or self._get_api_key()
        self.base_url = base_url or "https://api.modal.com"
        self.session: Optional[aiohttp.ClientSession] = None
        self.functions: Dict[str, ModalFunction] = {}
        
    def _get_api_key(self) -> str:
        """Get API key from environment or config."""
        import os
        api_key = os.getenv('MODAL_API_KEY')
        if not api_key:
            logger.warning("MODAL_API_KEY not found in environment variables")
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
            raise ValueError("Modal API key is required")
            
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with session.request(method, url, **kwargs) as response:
                if response.status == 401:
                    raise ValueError("Invalid Modal API key")
                elif response.status >= 400:
                    error_text = await response.text()
                    raise Exception(f"Modal API error {response.status}: {error_text}")
                
                return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"Modal API request failed: {e}")
            raise Exception(f"Failed to connect to Modal API: {e}")
    
    async def create_function(self, 
                            name: str,
                            image: str = "python:3.11",
                            cpu: float = 1.0,
                            memory: str = "2Gi",
                            gpu: Optional[str] = None,
                            environment: Dict[str, str] = None) -> ModalFunction:
        """Create a new Modal function."""
        payload = {
            "name": name,
            "spec": {
                "image": image,
                "resources": {
                    "cpu": cpu,
                    "memory": memory
                },
                "environment": environment or {}
            }
        }
        
        if gpu:
            payload["spec"]["resources"]["gpu"] = gpu
        
        response = await self._make_request("POST", "/functions", json=payload)
        
        function = ModalFunction(
            id=response["id"],
            name=response["name"],
            status=response["status"],
            created_at=datetime.fromisoformat(response["created_at"]),
            updated_at=datetime.fromisoformat(response["updated_at"]),
            image=response["spec"]["image"],
            cpu=response["spec"]["resources"]["cpu"],
            memory=response["spec"]["resources"]["memory"],
            gpu=response["spec"]["resources"].get("gpu"),
            environment=response["spec"]["environment"]
        )
        
        self.functions[function.id] = function
        logger.info(f"Created Modal function: {function.name} ({function.id})")
        return function
    
    async def get_function(self, function_id: str) -> Optional[ModalFunction]:
        """Get function information."""
        try:
            response = await self._make_request("GET", f"/functions/{function_id}")
            
            function = ModalFunction(
                id=response["id"],
                name=response["name"],
                status=response["status"],
                created_at=datetime.fromisoformat(response["created_at"]),
                updated_at=datetime.fromisoformat(response["updated_at"]),
                image=response["spec"]["image"],
                cpu=response["spec"]["resources"]["cpu"],
                memory=response["spec"]["resources"]["memory"],
                gpu=response["spec"]["resources"].get("gpu"),
                environment=response["spec"]["environment"]
            )
            
            self.functions[function.id] = function
            return function
            
        except Exception as e:
            logger.error(f"Failed to get Modal function {function_id}: {e}")
            return None
    
    async def list_functions(self) -> List[ModalFunction]:
        """List all functions."""
        try:
            response = await self._make_request("GET", "/functions")
            functions = []
            
            for func_data in response.get("functions", []):
                function = ModalFunction(
                    id=func_data["id"],
                    name=func_data["name"],
                    status=func_data["status"],
                    created_at=datetime.fromisoformat(func_data["created_at"]),
                    updated_at=datetime.fromisoformat(func_data["updated_at"]),
                    image=func_data["spec"]["image"],
                    cpu=func_data["spec"]["resources"]["cpu"],
                    memory=func_data["spec"]["resources"]["memory"],
                    gpu=func_data["spec"]["resources"].get("gpu"),
                    environment=func_data["spec"]["environment"]
                )
                functions.append(function)
                self.functions[function.id] = function
            
            return functions
            
        except Exception as e:
            logger.error(f"Failed to list Modal functions: {e}")
            return []
    
    async def invoke_function(self, function_id: str, payload: Dict[str, Any] = None) -> Dict[str, Any]:
        """Invoke a function."""
        try:
            response = await self._make_request("POST", f"/functions/{function_id}/invoke", 
                                              json=payload or {})
            logger.info(f"Invoked Modal function: {function_id}")
            return {
                "result": response.get("result"),
                "execution_time": response.get("execution_time", 0),
                "logs": response.get("logs", []),
                "status": response.get("status", "success")
            }
        except Exception as e:
            logger.error(f"Failed to invoke Modal function {function_id}: {e}")
            return {
                "result": None,
                "execution_time": 0,
                "logs": [str(e)],
                "status": "error"
            }
    
    async def update_function(self, function_id: str, 
                            image: str = None,
                            cpu: float = None,
                            memory: str = None,
                            gpu: Optional[str] = None,
                            environment: Dict[str, str] = None) -> bool:
        """Update function configuration."""
        try:
            payload = {}
            if image:
                payload["image"] = image
            if cpu is not None:
                payload["cpu"] = cpu
            if memory:
                payload["memory"] = memory
            if gpu is not None:
                payload["gpu"] = gpu
            if environment:
                payload["environment"] = environment
                
            await self._make_request("PATCH", f"/functions/{function_id}", json=payload)
            logger.info(f"Updated Modal function: {function_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update Modal function {function_id}: {e}")
            return False
    
    async def delete_function(self, function_id: str) -> bool:
        """Delete a function."""
        try:
            await self._make_request("DELETE", f"/functions/{function_id}")
            if function_id in self.functions:
                del self.functions[function_id]
            logger.info(f"Deleted Modal function: {function_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete Modal function {function_id}: {e}")
            return False
    
    async def get_function_logs(self, function_id: str, lines: int = 100) -> List[str]:
        """Get function logs."""
        try:
            response = await self._make_request("GET", f"/functions/{function_id}/logs", 
                                              params={"lines": lines})
            return response.get("logs", [])
        except Exception as e:
            logger.error(f"Failed to get logs for Modal function {function_id}: {e}")
            return []
    
    async def get_function_metrics(self, function_id: str) -> Dict[str, Any]:
        """Get function metrics."""
        try:
            response = await self._make_request("GET", f"/functions/{function_id}/metrics")
            return {
                "invocations_count": response.get("invocations_count", 0),
                "avg_execution_time": response.get("avg_execution_time", 0),
                "success_rate": response.get("success_rate", 0),
                "error_rate": response.get("error_rate", 0),
                "last_invocation": response.get("last_invocation"),
                "total_compute_time": response.get("total_compute_time", 0)
            }
        except Exception as e:
            logger.error(f"Failed to get metrics for Modal function {function_id}: {e}")
            return {}
    
    async def create_scheduled_function(self, function_id: str, schedule: str) -> bool:
        """Create a scheduled function."""
        try:
            payload = {"schedule": schedule}
            await self._make_request("POST", f"/functions/{function_id}/schedule", json=payload)
            logger.info(f"Created schedule for Modal function: {function_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create schedule for Modal function {function_id}: {e}")
            return False
    
    async def get_function_versions(self, function_id: str) -> List[Dict[str, Any]]:
        """Get function versions."""
        try:
            response = await self._make_request("GET", f"/functions/{function_id}/versions")
            return response.get("versions", [])
        except Exception as e:
            logger.error(f"Failed to get versions for Modal function {function_id}: {e}")
            return []
    
    async def get_status(self) -> Dict[str, Any]:
        """Get provider status."""
        try:
            if not self.api_key:
                return {
                    "status": "error",
                    "message": "API key not configured",
                    "functions_count": 0,
                    "available": False
                }
            
            functions = await self.list_functions()
            return {
                "status": "connected",
                "message": "Modal provider is operational",
                "functions_count": len(functions),
                "available": True,
                "api_endpoint": self.base_url
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection failed: {e}",
                "functions_count": 0,
                "available": False
            }
    
    async def close(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None

# Global instance
modal_provider = ModalProvider()
