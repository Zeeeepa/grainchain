#!/usr/bin/env python3
"""Advanced terminal session management with multi-session support."""

import asyncio
import subprocess
import threading
import uuid
import time
import json
import os
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from collections import deque
import logging

logger = logging.getLogger(__name__)

@dataclass
class TerminalSession:
    """Terminal session data model."""
    id: str
    name: str
    created_at: datetime
    last_activity: datetime
    current_directory: str
    environment: Dict[str, str]
    history: List[Dict[str, Any]]
    is_active: bool = True
    process: Optional[subprocess.Popen] = None

@dataclass
class CommandExecution:
    """Command execution result."""
    command: str
    output: str
    error: str
    exit_code: int
    execution_time: float
    timestamp: datetime

class TerminalSessionManager:
    """Manages multiple terminal sessions with advanced features."""
    
    def __init__(self):
        self.sessions: Dict[str, TerminalSession] = {}
        self.active_processes: Dict[str, subprocess.Popen] = {}
        self.command_history: deque = deque(maxlen=1000)  # Global command history
        self.completion_cache: Dict[str, List[str]] = {}
        self.environment_templates: Dict[str, Dict[str, str]] = {
            "default": {"TERM": "xterm-256color", "SHELL": "/bin/bash"},
            "python": {"PYTHONPATH": ".", "VIRTUAL_ENV": "venv"},
            "node": {"NODE_ENV": "development", "NPM_CONFIG_PREFIX": "~/.npm-global"}
        }
        
        # Initialize default session
        self.create_session("default", "Default Terminal")
    
    def create_session(self, name: str = None, description: str = None, 
                      environment_template: str = "default") -> str:
        """Create a new terminal session."""
        session_id = str(uuid.uuid4())[:8]
        
        if not name:
            name = f"Terminal {len(self.sessions) + 1}"
        
        # Get environment template
        env = self.environment_templates.get(environment_template, {}).copy()
        env.update(os.environ.copy())  # Include system environment
        
        session = TerminalSession(
            id=session_id,
            name=name,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            current_directory=os.getcwd(),
            environment=env,
            history=[]
        )
        
        self.sessions[session_id] = session
        logger.info(f"Created terminal session: {session_id} ({name})")
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[TerminalSession]:
        """Get terminal session by ID."""
        return self.sessions.get(session_id)
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all terminal sessions."""
        return [
            {
                "id": session.id,
                "name": session.name,
                "created_at": session.created_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "current_directory": session.current_directory,
                "is_active": session.is_active,
                "command_count": len(session.history)
            }
            for session in self.sessions.values()
        ]
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a terminal session."""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            
            # Kill any active process
            if session_id in self.active_processes:
                try:
                    self.active_processes[session_id].terminate()
                    del self.active_processes[session_id]
                except Exception as e:
                    logger.error(f"Error terminating process for session {session_id}: {e}")
            
            del self.sessions[session_id]
            logger.info(f"Deleted terminal session: {session_id}")
            return True
        
        return False
    
    async def execute_command(self, session_id: str, command: str, 
                            timeout: int = 30) -> CommandExecution:
        """Execute command in terminal session."""
        session = self.get_session(session_id)
        if not session:
            return CommandExecution(
                command=command,
                output="",
                error="Session not found",
                exit_code=1,
                execution_time=0.0,
                timestamp=datetime.now()
            )
        
        start_time = time.time()
        
        try:
            # Handle built-in commands
            if command.strip().startswith('cd '):
                return await self._handle_cd_command(session, command)
            elif command.strip() == 'pwd':
                return CommandExecution(
                    command=command,
                    output=session.current_directory,
                    error="",
                    exit_code=0,
                    execution_time=time.time() - start_time,
                    timestamp=datetime.now()
                )
            elif command.strip() == 'history':
                return await self._handle_history_command(session)
            elif command.strip().startswith('export '):
                return await self._handle_export_command(session, command)
            
            # Execute external command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=session.current_directory,
                env=session.environment
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=timeout
                )
                
                output = stdout.decode('utf-8', errors='replace')
                error = stderr.decode('utf-8', errors='replace')
                exit_code = process.returncode
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                output = ""
                error = f"Command timed out after {timeout} seconds"
                exit_code = 124  # Timeout exit code
            
            execution_time = time.time() - start_time
            
            # Create command execution result
            result = CommandExecution(
                command=command,
                output=output,
                error=error,
                exit_code=exit_code,
                execution_time=execution_time,
                timestamp=datetime.now()
            )
            
            # Update session
            session.last_activity = datetime.now()
            session.history.append(asdict(result))
            self.command_history.append({
                "session_id": session_id,
                "command": command,
                "timestamp": result.timestamp.isoformat()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing command in session {session_id}: {e}")
            return CommandExecution(
                command=command,
                output="",
                error=str(e),
                exit_code=1,
                execution_time=time.time() - start_time,
                timestamp=datetime.now()
            )
    
    async def _handle_cd_command(self, session: TerminalSession, command: str) -> CommandExecution:
        """Handle cd command to change directory."""
        start_time = time.time()
        
        try:
            # Parse directory from command
            parts = command.strip().split(' ', 1)
            if len(parts) < 2:
                target_dir = os.path.expanduser('~')  # Default to home
            else:
                target_dir = parts[1].strip()
            
            # Handle relative paths
            if not os.path.isabs(target_dir):
                target_dir = os.path.join(session.current_directory, target_dir)
            
            # Normalize path
            target_dir = os.path.normpath(target_dir)
            
            # Check if directory exists
            if os.path.isdir(target_dir):
                session.current_directory = target_dir
                return CommandExecution(
                    command=command,
                    output=f"Changed directory to {target_dir}",
                    error="",
                    exit_code=0,
                    execution_time=time.time() - start_time,
                    timestamp=datetime.now()
                )
            else:
                return CommandExecution(
                    command=command,
                    output="",
                    error=f"Directory not found: {target_dir}",
                    exit_code=1,
                    execution_time=time.time() - start_time,
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            return CommandExecution(
                command=command,
                output="",
                error=str(e),
                exit_code=1,
                execution_time=time.time() - start_time,
                timestamp=datetime.now()
            )
    
    async def _handle_history_command(self, session: TerminalSession) -> CommandExecution:
        """Handle history command."""
        start_time = time.time()
        
        history_lines = []
        for i, cmd in enumerate(session.history[-50:], 1):  # Last 50 commands
            history_lines.append(f"{i:4d}  {cmd['command']}")
        
        output = "\n".join(history_lines) if history_lines else "No command history"
        
        return CommandExecution(
            command="history",
            output=output,
            error="",
            exit_code=0,
            execution_time=time.time() - start_time,
            timestamp=datetime.now()
        )
    
    async def _handle_export_command(self, session: TerminalSession, command: str) -> CommandExecution:
        """Handle export command to set environment variables."""
        start_time = time.time()
        
        try:
            # Parse export command: export VAR=value
            parts = command.strip().split(' ', 1)
            if len(parts) < 2:
                return CommandExecution(
                    command=command,
                    output="",
                    error="Usage: export VAR=value",
                    exit_code=1,
                    execution_time=time.time() - start_time,
                    timestamp=datetime.now()
                )
            
            assignment = parts[1]
            if '=' not in assignment:
                return CommandExecution(
                    command=command,
                    output="",
                    error="Usage: export VAR=value",
                    exit_code=1,
                    execution_time=time.time() - start_time,
                    timestamp=datetime.now()
                )
            
            var_name, var_value = assignment.split('=', 1)
            session.environment[var_name] = var_value
            
            return CommandExecution(
                command=command,
                output=f"Exported {var_name}={var_value}",
                error="",
                exit_code=0,
                execution_time=time.time() - start_time,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return CommandExecution(
                command=command,
                output="",
                error=str(e),
                exit_code=1,
                execution_time=time.time() - start_time,
                timestamp=datetime.now()
            )
    
    def get_command_completions(self, session_id: str, partial_command: str) -> List[str]:
        """Get command completions for partial command."""
        session = self.get_session(session_id)
        if not session:
            return []
        
        # Cache key for completions
        cache_key = f"{session.current_directory}:{partial_command}"
        if cache_key in self.completion_cache:
            return self.completion_cache[cache_key]
        
        completions = []
        
        try:
            # File/directory completions
            if '/' in partial_command or partial_command.startswith('.'):
                # Path completion
                if partial_command.endswith('/') or partial_command == '':
                    search_dir = session.current_directory
                    prefix = ''
                else:
                    path_parts = partial_command.rsplit('/', 1)
                    if len(path_parts) == 2:
                        dir_part, file_part = path_parts
                        search_dir = os.path.join(session.current_directory, dir_part)
                        prefix = file_part
                    else:
                        search_dir = session.current_directory
                        prefix = partial_command
                
                if os.path.isdir(search_dir):
                    for item in os.listdir(search_dir):
                        if item.startswith(prefix):
                            completions.append(item)
            
            else:
                # Command completions from history
                for cmd_entry in reversed(list(self.command_history)):
                    cmd = cmd_entry['command'].split()[0]
                    if cmd.startswith(partial_command) and cmd not in completions:
                        completions.append(cmd)
                        if len(completions) >= 10:  # Limit completions
                            break
                
                # Common commands
                common_commands = [
                    'ls', 'cd', 'pwd', 'mkdir', 'rmdir', 'rm', 'cp', 'mv',
                    'cat', 'less', 'head', 'tail', 'grep', 'find', 'which',
                    'ps', 'top', 'kill', 'jobs', 'bg', 'fg', 'history',
                    'export', 'env', 'echo', 'date', 'whoami', 'id'
                ]
                
                for cmd in common_commands:
                    if cmd.startswith(partial_command) and cmd not in completions:
                        completions.append(cmd)
        
        except Exception as e:
            logger.error(f"Error getting completions: {e}")
        
        # Cache results
        self.completion_cache[cache_key] = completions[:20]  # Limit and cache
        
        return completions[:20]
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed session information."""
        session = self.get_session(session_id)
        if not session:
            return None
        
        return {
            "id": session.id,
            "name": session.name,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "current_directory": session.current_directory,
            "environment_count": len(session.environment),
            "command_count": len(session.history),
            "is_active": session.is_active,
            "recent_commands": [
                cmd['command'] for cmd in session.history[-5:]
            ]
        }
    
    def search_history(self, session_id: str, query: str) -> List[Dict[str, Any]]:
        """Search command history."""
        session = self.get_session(session_id)
        if not session:
            return []
        
        results = []
        for cmd in session.history:
            if query.lower() in cmd['command'].lower():
                results.append({
                    "command": cmd['command'],
                    "timestamp": cmd['timestamp'],
                    "exit_code": cmd['exit_code']
                })
        
        return results[-20:]  # Return last 20 matches
    
    def export_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export session data for backup/sharing."""
        session = self.get_session(session_id)
        if not session:
            return None
        
        return {
            "session": asdict(session),
            "exported_at": datetime.now().isoformat(),
            "version": "1.0"
        }
    
    def import_session(self, session_data: Dict[str, Any]) -> Optional[str]:
        """Import session from exported data."""
        try:
            session_info = session_data['session']
            
            # Create new session ID to avoid conflicts
            new_session_id = str(uuid.uuid4())[:8]
            
            session = TerminalSession(
                id=new_session_id,
                name=f"Imported: {session_info['name']}",
                created_at=datetime.now(),
                last_activity=datetime.now(),
                current_directory=session_info['current_directory'],
                environment=session_info['environment'],
                history=session_info['history']
            )
            
            self.sessions[new_session_id] = session
            return new_session_id
            
        except Exception as e:
            logger.error(f"Error importing session: {e}")
            return None

# Global session manager instance
session_manager = TerminalSessionManager()

# Export for use in main app
__all__ = ['TerminalSessionManager', 'TerminalSession', 'CommandExecution', 'session_manager']
