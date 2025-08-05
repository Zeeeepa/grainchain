"""Mock Grainchain interfaces for dashboard demonstration."""

import asyncio
import time
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime

class SandboxStatus(Enum):
    """Sandbox status enumeration."""
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"

@dataclass
class ExecutionResult:
    """Result of command execution."""
    stdout: str
    stderr: str
    return_code: int
    success: bool
    execution_time: float

@dataclass
class FileInfo:
    """File information."""
    name: str
    path: str
    size: int
    is_directory: bool
    modified_time: float
    permissions: str

@dataclass
class SandboxConfig:
    """Sandbox configuration."""
    timeout: int = 300
    working_directory: str = "/tmp"
    environment: Dict[str, str] = None
    
    def __post_init__(self):
        if self.environment is None:
            self.environment = {}

@dataclass
class ProviderInfo:
    """Provider information."""
    available: bool
    dependencies_installed: bool
    config_valid: bool
    missing_config: List[str]
    setup_instructions: str

class MockSandbox:
    """Mock sandbox for demonstration."""
    
    def __init__(self, provider: str, config: SandboxConfig):
        self.provider = provider
        self.config = config
        self.sandbox_id = f"{provider}-{int(time.time())}"
        self.status = SandboxStatus.STARTING
        self._files = {
            "/": [
                FileInfo("home", "/home", 4096, True, time.time(), "drwxr-xr-x"),
                FileInfo("tmp", "/tmp", 4096, True, time.time(), "drwxrwxrwt"),
                FileInfo("usr", "/usr", 4096, True, time.time(), "drwxr-xr-x"),
                FileInfo("var", "/var", 4096, True, time.time(), "drwxr-xr-x"),
            ],
            "/home": [
                FileInfo("user", "/home/user", 4096, True, time.time(), "drwxr-xr-x"),
            ],
            "/home/user": [
                FileInfo("main.py", "/home/user/main.py", 1024, False, time.time(), "-rw-r--r--"),
                FileInfo("README.md", "/home/user/README.md", 2048, False, time.time(), "-rw-r--r--"),
            ]
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        await asyncio.sleep(0.1)  # Simulate startup time
        self.status = SandboxStatus.RUNNING
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        self.status = SandboxStatus.STOPPED
    
    async def execute(self, command: str, timeout: Optional[int] = None) -> ExecutionResult:
        """Execute a command in the sandbox."""
        await asyncio.sleep(0.2)  # Simulate execution time
        
        # Mock different command responses
        if command.startswith("ls"):
            if "-la" in command:
                stdout = """total 12
drwxr-xr-x 3 user user 4096 Jan  1 12:00 .
drwxr-xr-x 3 root root 4096 Jan  1 12:00 ..
-rw-r--r-- 1 user user 1024 Jan  1 12:00 main.py
-rw-r--r-- 1 user user 2048 Jan  1 12:00 README.md"""
            else:
                stdout = "main.py  README.md"
            return ExecutionResult(stdout, "", 0, True, 0.2)
        
        elif command == "pwd":
            return ExecutionResult("/home/user", "", 0, True, 0.1)
        
        elif command == "whoami":
            return ExecutionResult("user", "", 0, True, 0.1)
        
        elif command.startswith("python"):
            if "--version" in command:
                return ExecutionResult("Python 3.12.0", "", 0, True, 0.1)
            else:
                return ExecutionResult("Hello from Python!", "", 0, True, 0.5)
        
        elif command == "pip list":
            stdout = """Package    Version
---------- -------
pip        23.3.1
setuptools 69.0.2
wheel      0.42.0"""
            return ExecutionResult(stdout, "", 0, True, 1.0)
        
        elif command.startswith("echo"):
            text = command.replace("echo ", "")
            return ExecutionResult(text, "", 0, True, 0.1)
        
        elif command == "env":
            stdout = """PATH=/usr/local/bin:/usr/bin:/bin
HOME=/home/user
USER=user
SHELL=/bin/bash"""
            return ExecutionResult(stdout, "", 0, True, 0.2)
        
        elif command == "df -h":
            stdout = """Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        20G  5.2G   14G  28% /
tmpfs           2.0G     0  2.0G   0% /tmp"""
            return ExecutionResult(stdout, "", 0, True, 0.3)
        
        elif command == "ps aux":
            stdout = """USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root         1  0.0  0.1   1234   567 ?        Ss   12:00   0:00 /sbin/init
user       123  0.0  0.2   2345  1234 pts/0    S    12:01   0:00 bash"""
            return ExecutionResult(stdout, "", 0, True, 0.4)
        
        else:
            # Unknown command
            return ExecutionResult("", f"bash: {command}: command not found", 127, False, 0.1)
    
    async def upload_file(self, file_path: str, content: str):
        """Upload a file to the sandbox."""
        await asyncio.sleep(0.1)
        # Mock file upload - just add to our mock file system
        directory = "/".join(file_path.split("/")[:-1]) or "/"
        filename = file_path.split("/")[-1]
        
        if directory not in self._files:
            self._files[directory] = []
        
        # Remove existing file if it exists
        self._files[directory] = [f for f in self._files[directory] if f.name != filename]
        
        # Add new file
        self._files[directory].append(
            FileInfo(filename, file_path, len(content), False, time.time(), "-rw-r--r--")
        )
    
    async def download_file(self, file_path: str) -> bytes:
        """Download a file from the sandbox."""
        await asyncio.sleep(0.1)
        
        # Mock file content based on file type
        if file_path.endswith(".py"):
            content = f"""#!/usr/bin/env python3
# Mock Python file: {file_path}

def main():
    print("Hello from {file_path}!")

if __name__ == "__main__":
    main()
"""
        elif file_path.endswith(".md"):
            content = f"""# {file_path.split('/')[-1]}

This is a mock README file for demonstration purposes.

## Features
- Mock file system
- Simulated content
- Dashboard integration

Generated at: {datetime.now().isoformat()}
"""
        else:
            content = f"Mock content for {file_path}\nGenerated at: {datetime.now().isoformat()}\n"
        
        return content.encode('utf-8')
    
    async def list_files(self, path: str = "/") -> List[FileInfo]:
        """List files in a directory."""
        await asyncio.sleep(0.1)
        return self._files.get(path, [])
    
    async def create_snapshot(self) -> str:
        """Create a snapshot of the sandbox."""
        await asyncio.sleep(1.0)  # Simulate snapshot creation time
        snapshot_id = f"snap-{int(time.time())}"
        return snapshot_id
    
    async def restore_snapshot(self, snapshot_id: str):
        """Restore from a snapshot."""
        await asyncio.sleep(1.5)  # Simulate restore time

def get_providers_info() -> Dict[str, ProviderInfo]:
    """Get information about available providers."""
    return {
        "local": ProviderInfo(
            available=True,
            dependencies_installed=True,
            config_valid=True,
            missing_config=[],
            setup_instructions=""
        ),
        "e2b": ProviderInfo(
            available=False,
            dependencies_installed=False,
            config_valid=False,
            missing_config=["E2B_API_KEY"],
            setup_instructions="Install with: pip install grainchain[e2b]"
        ),
        "daytona": ProviderInfo(
            available=False,
            dependencies_installed=False,
            config_valid=False,
            missing_config=["DAYTONA_API_KEY"],
            setup_instructions="Install with: pip install grainchain[daytona]"
        ),
        "morph": ProviderInfo(
            available=False,
            dependencies_installed=False,
            config_valid=False,
            missing_config=["MORPH_API_KEY"],
            setup_instructions="Install with: pip install grainchain[morph]"
        ),
        "modal": ProviderInfo(
            available=False,
            dependencies_installed=False,
            config_valid=False,
            missing_config=["MODAL_TOKEN_ID", "MODAL_TOKEN_SECRET"],
            setup_instructions="Install with: pip install grainchain[modal]"
        )
    }

async def check_provider(provider: str) -> bool:
    """Check if a provider is available."""
    providers = get_providers_info()
    return providers.get(provider, ProviderInfo(False, False, False, [], "")).available

# Mock the Sandbox class to use our MockSandbox
class Sandbox:
    """Mock Sandbox class that creates MockSandbox instances."""
    
    def __init__(self, provider: str, config: SandboxConfig):
        self._mock = MockSandbox(provider, config)
    
    async def __aenter__(self):
        await self._mock.__aenter__()
        return self._mock
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._mock.__aexit__(exc_type, exc_val, exc_tb)

# Mock exceptions
class GrainchainError(Exception):
    """Base Grainchain exception."""
    pass

class ProviderError(GrainchainError):
    """Provider-specific error."""
    pass

class TimeoutError(GrainchainError):
    """Timeout error."""
    pass

