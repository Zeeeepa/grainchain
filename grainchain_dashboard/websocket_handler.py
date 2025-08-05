#!/usr/bin/env python3
"""WebSocket handler for real-time communication."""

import asyncio
import json
import logging
from typing import Dict, Set, Any, Optional
from datetime import datetime
import reflex as rx

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections for real-time features."""
    
    def __init__(self):
        self.connections: Dict[str, Set[rx.WebSocket]] = {
            'terminal': set(),
            'files': set(),
            'dashboard': set(),
            'collaboration': set()
        }
        self.terminal_sessions: Dict[str, Dict[str, Any]] = {}
        
    async def connect(self, websocket: rx.WebSocket, channel: str = 'dashboard'):
        """Add a new WebSocket connection."""
        if channel not in self.connections:
            self.connections[channel] = set()
        
        self.connections[channel].add(websocket)
        logger.info(f"WebSocket connected to {channel}. Total connections: {len(self.connections[channel])}")
        
        # Send initial data
        await self.send_initial_data(websocket, channel)
    
    async def disconnect(self, websocket: rx.WebSocket, channel: str = 'dashboard'):
        """Remove a WebSocket connection."""
        if channel in self.connections:
            self.connections[channel].discard(websocket)
            logger.info(f"WebSocket disconnected from {channel}. Remaining: {len(self.connections[channel])}")
    
    async def broadcast(self, message: Dict[str, Any], channel: str = 'dashboard'):
        """Broadcast message to all connections in a channel."""
        if channel not in self.connections:
            return
            
        message['timestamp'] = datetime.now().isoformat()
        message_str = json.dumps(message)
        
        # Remove dead connections
        dead_connections = set()
        
        for websocket in self.connections[channel]:
            try:
                await websocket.send_text(message_str)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                dead_connections.add(websocket)
        
        # Clean up dead connections
        for dead_ws in dead_connections:
            self.connections[channel].discard(dead_ws)
    
    async def send_initial_data(self, websocket: rx.WebSocket, channel: str):
        """Send initial data when client connects."""
        initial_data = {
            'type': 'initial_data',
            'channel': channel,
            'data': {}
        }
        
        if channel == 'dashboard':
            initial_data['data'] = {
                'active_sandboxes': 1,
                'providers_count': 5,
                'commands_run': 42,
                'system_status': 'healthy'
            }
        elif channel == 'terminal':
            initial_data['data'] = {
                'sessions': list(self.terminal_sessions.keys()),
                'current_session': None
            }
        elif channel == 'files':
            initial_data['data'] = {
                'current_directory': '/',
                'watch_enabled': True
            }
        
        try:
            await websocket.send_text(json.dumps(initial_data))
        except Exception as e:
            logger.error(f"Error sending initial data: {e}")
    
    async def handle_terminal_command(self, session_id: str, command: str):
        """Handle terminal command execution with real-time output."""
        if session_id not in self.terminal_sessions:
            self.terminal_sessions[session_id] = {
                'history': [],
                'current_directory': '/',
                'environment': {}
            }
        
        # Add command to history
        self.terminal_sessions[session_id]['history'].append({
            'command': command,
            'timestamp': datetime.now().isoformat(),
            'output': '',
            'exit_code': 0
        })
        
        # Broadcast command start
        await self.broadcast({
            'type': 'terminal_command_start',
            'session_id': session_id,
            'command': command
        }, 'terminal')
        
        # Simulate command execution (replace with actual execution)
        output = await self.execute_command(command)
        
        # Update history with output
        self.terminal_sessions[session_id]['history'][-1]['output'] = output
        
        # Broadcast command completion
        await self.broadcast({
            'type': 'terminal_command_complete',
            'session_id': session_id,
            'command': command,
            'output': output,
            'exit_code': 0
        }, 'terminal')
    
    async def execute_command(self, command: str) -> str:
        """Execute command and return output (real implementation)."""
        import subprocess
        import asyncio
        
        try:
            # Execute command in a subprocess with timeout
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd="/tmp"  # Safe working directory
            )
            
            # Wait for completion with timeout
            stdout, _ = await asyncio.wait_for(
                process.communicate(), 
                timeout=30.0  # 30 second timeout
            )
            
            output = stdout.decode('utf-8', errors='replace')
            return output.strip() if output else f"Command completed: {command}"
            
        except asyncio.TimeoutError:
            return f"Command timed out: {command}"
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return f"Command failed: {command}\nError: {str(e)}"
    
    async def handle_file_change(self, file_path: str, change_type: str):
        """Handle file system changes."""
        await self.broadcast({
            'type': 'file_change',
            'file_path': file_path,
            'change_type': change_type,  # 'created', 'modified', 'deleted'
            'timestamp': datetime.now().isoformat()
        }, 'files')
    
    async def handle_dashboard_update(self, metric: str, value: Any):
        """Handle dashboard metric updates."""
        await self.broadcast({
            'type': 'dashboard_update',
            'metric': metric,
            'value': value
        }, 'dashboard')

# Global WebSocket manager instance
ws_manager = WebSocketManager()

class WebSocketState(rx.State):
    """State for WebSocket connections."""
    
    connected: bool = False
    terminal_output: str = ""
    current_terminal_session: str = "default"
    
    async def connect_websocket(self):
        """Connect to WebSocket."""
        self.connected = True
    
    async def disconnect_websocket(self):
        """Disconnect from WebSocket."""
        self.connected = False
    
    async def send_terminal_command(self, command: str):
        """Send command to terminal via WebSocket."""
        await ws_manager.handle_terminal_command(self.current_terminal_session, command)
    
    async def handle_websocket_message(self, message: str):
        """Handle incoming WebSocket message."""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'terminal_command_complete':
                self.terminal_output += f"\n$ {data['command']}\n{data['output']}"
            elif message_type == 'dashboard_update':
                # Handle dashboard updates
                pass
            elif message_type == 'file_change':
                # Handle file changes
                pass
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message: {message}")

# Export for use in main app
__all__ = ['WebSocketManager', 'WebSocketState', 'ws_manager']
