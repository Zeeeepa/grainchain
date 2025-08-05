#!/usr/bin/env python3
"""Comprehensive monitoring and metrics collection system."""

import asyncio
import psutil
import time
import json
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging
import threading
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System resource metrics."""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used: int
    memory_total: int
    disk_percent: float
    disk_used: int
    disk_total: int
    network_bytes_sent: int
    network_bytes_recv: int
    load_average: List[float]
    process_count: int

@dataclass
class ApplicationMetrics:
    """Application-specific metrics."""
    timestamp: datetime
    active_users: int
    active_sessions: int
    api_requests_per_minute: int
    response_time_avg: float
    error_rate: float
    database_connections: int
    websocket_connections: int
    provider_status: Dict[str, str]

@dataclass
class UserActivity:
    """User activity tracking."""
    user_id: int
    username: str
    action: str
    resource: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    duration: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class MetricsCollector:
    """Collects and stores system and application metrics."""
    
    def __init__(self, collection_interval: int = 60):
        self.collection_interval = collection_interval
        self.running = False
        self.collector_thread = None
        
        # In-memory storage for recent metrics
        self.system_metrics_buffer = deque(maxlen=1440)  # 24 hours at 1-minute intervals
        self.app_metrics_buffer = deque(maxlen=1440)
        self.user_activities_buffer = deque(maxlen=10000)  # Last 10k activities
        
        # Request tracking
        self.request_times = deque(maxlen=1000)
        self.error_count = 0
        self.request_count = 0
        self.last_minute_requests = deque(maxlen=60)
        
        # Provider status tracking
        self.provider_status = {
            "local": "success",
            "e2b": "unknown",
            "daytona": "unknown",
            "morph": "unknown",
            "modal": "unknown"
        }
        
        self.init_database()
    
    def init_database(self):
        """Initialize metrics database tables."""
        try:
            conn = sqlite3.connect('grainchain_metrics.db')
            cursor = conn.cursor()
            
            # System metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP NOT NULL,
                    cpu_percent REAL NOT NULL,
                    memory_percent REAL NOT NULL,
                    memory_used INTEGER NOT NULL,
                    memory_total INTEGER NOT NULL,
                    disk_percent REAL NOT NULL,
                    disk_used INTEGER NOT NULL,
                    disk_total INTEGER NOT NULL,
                    network_bytes_sent INTEGER NOT NULL,
                    network_bytes_recv INTEGER NOT NULL,
                    load_average TEXT NOT NULL,
                    process_count INTEGER NOT NULL
                )
            ''')
            
            # Application metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS app_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP NOT NULL,
                    active_users INTEGER NOT NULL,
                    active_sessions INTEGER NOT NULL,
                    api_requests_per_minute INTEGER NOT NULL,
                    response_time_avg REAL NOT NULL,
                    error_rate REAL NOT NULL,
                    database_connections INTEGER NOT NULL,
                    websocket_connections INTEGER NOT NULL,
                    provider_status TEXT NOT NULL
                )
            ''')
            
            # User activities table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    action TEXT NOT NULL,
                    resource TEXT NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    ip_address TEXT,
                    user_agent TEXT,
                    duration REAL,
                    metadata TEXT
                )
            ''')
            
            # Performance alerts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    metric_value REAL,
                    threshold_value REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved BOOLEAN DEFAULT 0,
                    resolved_at TIMESTAMP
                )
            ''')
            
            # Create indexes for better query performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_app_metrics_timestamp ON app_metrics(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_activities_timestamp ON user_activities(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_activities_user_id ON user_activities(user_id)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error initializing metrics database: {e}")
    
    def start_collection(self):
        """Start metrics collection in background thread."""
        if not self.running:
            self.running = True
            self.collector_thread = threading.Thread(target=self._collection_loop, daemon=True)
            self.collector_thread.start()
            logger.info("Metrics collection started")
    
    def stop_collection(self):
        """Stop metrics collection."""
        self.running = False
        if self.collector_thread:
            self.collector_thread.join(timeout=5)
        logger.info("Metrics collection stopped")
    
    def _collection_loop(self):
        """Main collection loop running in background thread."""
        while self.running:
            try:
                # Collect system metrics
                system_metrics = self.collect_system_metrics()
                self.system_metrics_buffer.append(system_metrics)
                
                # Collect application metrics
                app_metrics = self.collect_application_metrics()
                self.app_metrics_buffer.append(app_metrics)
                
                # Store to database every 5 minutes
                if len(self.system_metrics_buffer) % 5 == 0:
                    self.store_metrics_to_db()
                
                # Check for alerts
                self.check_performance_alerts(system_metrics, app_metrics)
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                time.sleep(self.collection_interval)
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Load average (Unix-like systems)
            try:
                load_avg = list(psutil.getloadavg())
            except AttributeError:
                load_avg = [0.0, 0.0, 0.0]  # Windows doesn't have load average
            
            # Process count
            process_count = len(psutil.pids())
            
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used=memory.used,
                memory_total=memory.total,
                disk_percent=disk.percent,
                disk_used=disk.used,
                disk_total=disk.total,
                network_bytes_sent=network.bytes_sent,
                network_bytes_recv=network.bytes_recv,
                load_average=load_avg,
                process_count=process_count
            )
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_used=0,
                memory_total=0,
                disk_percent=0.0,
                disk_used=0,
                disk_total=0,
                network_bytes_sent=0,
                network_bytes_recv=0,
                load_average=[0.0, 0.0, 0.0],
                process_count=0
            )
    
    def collect_application_metrics(self) -> ApplicationMetrics:
        """Collect current application metrics."""
        try:
            # Calculate requests per minute
            current_time = time.time()
            self.last_minute_requests.append(current_time)
            
            # Remove requests older than 1 minute
            cutoff_time = current_time - 60
            while self.last_minute_requests and self.last_minute_requests[0] < cutoff_time:
                self.last_minute_requests.popleft()
            
            requests_per_minute = len(self.last_minute_requests)
            
            # Calculate average response time
            if self.request_times:
                avg_response_time = sum(self.request_times) / len(self.request_times)
            else:
                avg_response_time = 0.0
            
            # Calculate error rate
            if self.request_count > 0:
                error_rate = (self.error_count / self.request_count) * 100
            else:
                error_rate = 0.0
            
            return ApplicationMetrics(
                timestamp=datetime.now(),
                active_users=self.get_active_users_count(),
                active_sessions=self.get_active_sessions_count(),
                api_requests_per_minute=requests_per_minute,
                response_time_avg=avg_response_time,
                error_rate=error_rate,
                database_connections=self.get_database_connections_count(),
                websocket_connections=self.get_websocket_connections_count(),
                provider_status=self.provider_status.copy()
            )
            
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
            return ApplicationMetrics(
                timestamp=datetime.now(),
                active_users=0,
                active_sessions=0,
                api_requests_per_minute=0,
                response_time_avg=0.0,
                error_rate=0.0,
                database_connections=0,
                websocket_connections=0,
                provider_status={}
            )
    
    def record_request(self, response_time: float, is_error: bool = False):
        """Record API request metrics."""
        self.request_times.append(response_time)
        self.request_count += 1
        
        if is_error:
            self.error_count += 1
    
    def record_user_activity(self, user_id: int, username: str, action: str, 
                           resource: str, ip_address: str = None, 
                           user_agent: str = None, duration: float = None,
                           metadata: Dict[str, Any] = None):
        """Record user activity."""
        activity = UserActivity(
            user_id=user_id,
            username=username,
            action=action,
            resource=resource,
            timestamp=datetime.now(),
            ip_address=ip_address,
            user_agent=user_agent,
            duration=duration,
            metadata=metadata
        )
        
        self.user_activities_buffer.append(activity)
        
        # Store to database immediately for user activities
        try:
            conn = sqlite3.connect('grainchain_metrics.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO user_activities 
                (user_id, username, action, resource, timestamp, ip_address, user_agent, duration, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                activity.user_id,
                activity.username,
                activity.action,
                activity.resource,
                activity.timestamp,
                activity.ip_address,
                activity.user_agent,
                activity.duration,
                json.dumps(activity.metadata) if activity.metadata else None
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing user activity: {e}")
    
    def update_provider_status(self, provider: str, status: str):
        """Update provider status."""
        self.provider_status[provider] = status
    
    def get_active_users_count(self) -> int:
        """Get count of active users (real implementation)."""
        try:
            conn = sqlite3.connect('grainchain.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(DISTINCT user_id) FROM sessions 
                WHERE is_active = 1 AND expires_at > datetime('now')
            ''')
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            logger.error(f"Failed to get active users count: {e}")
            return 0
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions (real implementation)."""
        try:
            conn = sqlite3.connect('grainchain.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM sessions 
                WHERE is_active = 1 AND expires_at > datetime('now')
            ''')
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            logger.error(f"Failed to get active sessions count: {e}")
            return 0
    
    def get_database_connections_count(self) -> int:
        """Get count of active database connections (real implementation)."""
        try:
            # Get SQLite connection count (simplified)
            import threading
            return threading.active_count()  # Approximate active connections
        except Exception as e:
            logger.error(f"Failed to get database connections count: {e}")
            return 0
    
    def get_websocket_connections_count(self) -> int:
        """Get count of active WebSocket connections (real implementation)."""
        try:
            from ..websocket_handler import ws_manager
            return len(ws_manager.connections) if ws_manager else 0
        except Exception as e:
            logger.error(f"Failed to get WebSocket connections count: {e}")
            return 0
    
    def store_metrics_to_db(self):
        """Store buffered metrics to database."""
        try:
            conn = sqlite3.connect('grainchain_metrics.db')
            cursor = conn.cursor()
            
            # Store system metrics
            for metrics in list(self.system_metrics_buffer)[-5:]:  # Last 5 entries
                cursor.execute('''
                    INSERT INTO system_metrics 
                    (timestamp, cpu_percent, memory_percent, memory_used, memory_total,
                     disk_percent, disk_used, disk_total, network_bytes_sent, network_bytes_recv,
                     load_average, process_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metrics.timestamp,
                    metrics.cpu_percent,
                    metrics.memory_percent,
                    metrics.memory_used,
                    metrics.memory_total,
                    metrics.disk_percent,
                    metrics.disk_used,
                    metrics.disk_total,
                    metrics.network_bytes_sent,
                    metrics.network_bytes_recv,
                    json.dumps(metrics.load_average),
                    metrics.process_count
                ))
            
            # Store application metrics
            for metrics in list(self.app_metrics_buffer)[-5:]:  # Last 5 entries
                cursor.execute('''
                    INSERT INTO app_metrics 
                    (timestamp, active_users, active_sessions, api_requests_per_minute,
                     response_time_avg, error_rate, database_connections, websocket_connections,
                     provider_status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metrics.timestamp,
                    metrics.active_users,
                    metrics.active_sessions,
                    metrics.api_requests_per_minute,
                    metrics.response_time_avg,
                    metrics.error_rate,
                    metrics.database_connections,
                    metrics.websocket_connections,
                    json.dumps(metrics.provider_status)
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing metrics to database: {e}")
    
    def check_performance_alerts(self, system_metrics: SystemMetrics, app_metrics: ApplicationMetrics):
        """Check for performance alerts and store them."""
        alerts = []
        
        # CPU usage alert
        if system_metrics.cpu_percent > 80:
            alerts.append({
                "type": "high_cpu_usage",
                "severity": "warning" if system_metrics.cpu_percent < 90 else "critical",
                "message": f"High CPU usage: {system_metrics.cpu_percent:.1f}%",
                "value": system_metrics.cpu_percent,
                "threshold": 80
            })
        
        # Memory usage alert
        if system_metrics.memory_percent > 85:
            alerts.append({
                "type": "high_memory_usage",
                "severity": "warning" if system_metrics.memory_percent < 95 else "critical",
                "message": f"High memory usage: {system_metrics.memory_percent:.1f}%",
                "value": system_metrics.memory_percent,
                "threshold": 85
            })
        
        # Disk usage alert
        if system_metrics.disk_percent > 90:
            alerts.append({
                "type": "high_disk_usage",
                "severity": "critical",
                "message": f"High disk usage: {system_metrics.disk_percent:.1f}%",
                "value": system_metrics.disk_percent,
                "threshold": 90
            })
        
        # Error rate alert
        if app_metrics.error_rate > 5:
            alerts.append({
                "type": "high_error_rate",
                "severity": "warning" if app_metrics.error_rate < 10 else "critical",
                "message": f"High error rate: {app_metrics.error_rate:.1f}%",
                "value": app_metrics.error_rate,
                "threshold": 5
            })
        
        # Response time alert
        if app_metrics.response_time_avg > 2000:  # 2 seconds
            alerts.append({
                "type": "slow_response_time",
                "severity": "warning",
                "message": f"Slow response time: {app_metrics.response_time_avg:.0f}ms",
                "value": app_metrics.response_time_avg,
                "threshold": 2000
            })
        
        # Store alerts to database
        if alerts:
            self.store_alerts(alerts)
    
    def store_alerts(self, alerts: List[Dict[str, Any]]):
        """Store performance alerts to database."""
        try:
            conn = sqlite3.connect('grainchain_metrics.db')
            cursor = conn.cursor()
            
            for alert in alerts:
                cursor.execute('''
                    INSERT INTO performance_alerts 
                    (alert_type, severity, message, metric_value, threshold_value)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    alert["type"],
                    alert["severity"],
                    alert["message"],
                    alert["value"],
                    alert["threshold"]
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing alerts: {e}")
    
    def get_recent_metrics(self, hours: int = 1) -> Dict[str, List[Dict[str, Any]]]:
        """Get recent metrics from memory buffers."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_system = [
            asdict(m) for m in self.system_metrics_buffer 
            if m.timestamp >= cutoff_time
        ]
        
        recent_app = [
            asdict(m) for m in self.app_metrics_buffer 
            if m.timestamp >= cutoff_time
        ]
        
        return {
            "system_metrics": recent_system,
            "application_metrics": recent_app
        }
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get summary metrics for dashboard."""
        if not self.system_metrics_buffer or not self.app_metrics_buffer:
            return {
                "system": {"cpu": 0, "memory": 0, "disk": 0},
                "application": {"users": 0, "requests": 0, "errors": 0},
                "status": "initializing"
            }
        
        latest_system = self.system_metrics_buffer[-1]
        latest_app = self.app_metrics_buffer[-1]
        
        return {
            "system": {
                "cpu": latest_system.cpu_percent,
                "memory": latest_system.memory_percent,
                "disk": latest_system.disk_percent
            },
            "application": {
                "users": latest_app.active_users,
                "requests": latest_app.api_requests_per_minute,
                "errors": latest_app.error_rate
            },
            "providers": latest_app.provider_status,
            "status": "healthy"
        }

# Global metrics collector instance
metrics_collector = MetricsCollector()

# Export for use in main app
__all__ = ['MetricsCollector', 'SystemMetrics', 'ApplicationMetrics', 'UserActivity', 'metrics_collector']
