#!/usr/bin/env python3
"""Comprehensive notification and alert system."""

import asyncio
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import threading
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class NotificationType(Enum):
    """Types of notifications."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    SYSTEM = "system"

class NotificationPriority(Enum):
    """Notification priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class Notification:
    """Notification data model."""
    id: str
    title: str
    message: str
    type: NotificationType
    priority: NotificationPriority
    user_id: Optional[int] = None
    created_at: datetime = None
    read_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, str]]] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.expires_at is None:
            # Default expiry: 7 days for normal, 1 day for low priority
            days = 1 if self.priority == NotificationPriority.LOW else 7
            self.expires_at = self.created_at + timedelta(days=days)

class NotificationManager:
    """Manages notifications, alerts, and real-time delivery."""
    
    def __init__(self):
        self.subscribers: Dict[int, List[Callable]] = defaultdict(list)
        self.notification_buffer = deque(maxlen=1000)  # Recent notifications
        self.init_database()
        self.cleanup_thread = None
        self.start_cleanup_task()
    
    def init_database(self):
        """Initialize notification database tables."""
        try:
            conn = sqlite3.connect('grainchain_notifications.db')
            cursor = conn.cursor()
            
            # Notifications table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    type TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    user_id INTEGER,
                    created_at TIMESTAMP NOT NULL,
                    read_at TIMESTAMP,
                    expires_at TIMESTAMP,
                    metadata TEXT,
                    actions TEXT
                )
            ''')
            
            # Notification preferences table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notification_preferences (
                    user_id INTEGER PRIMARY KEY,
                    email_enabled BOOLEAN DEFAULT 1,
                    push_enabled BOOLEAN DEFAULT 1,
                    sound_enabled BOOLEAN DEFAULT 1,
                    types_enabled TEXT DEFAULT '["info","success","warning","error","system"]',
                    quiet_hours_start TIME,
                    quiet_hours_end TIME,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Activity feed table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activity_feed (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_id TEXT,
                    description TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_type ON notifications(type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_activity_feed_user_id ON activity_feed(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_activity_feed_timestamp ON activity_feed(timestamp)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error initializing notification database: {e}")
    
    def start_cleanup_task(self):
        """Start background cleanup task."""
        if not self.cleanup_thread or not self.cleanup_thread.is_alive():
            self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
            self.cleanup_thread.start()
    
    def _cleanup_loop(self):
        """Background cleanup of expired notifications."""
        while True:
            try:
                self.cleanup_expired_notifications()
                # Run cleanup every hour
                threading.Event().wait(3600)
            except Exception as e:
                logger.error(f"Error in notification cleanup: {e}")
                threading.Event().wait(300)  # Wait 5 minutes on error
    
    def create_notification(
        self,
        title: str,
        message: str,
        type: NotificationType = NotificationType.INFO,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        user_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        actions: Optional[List[Dict[str, str]]] = None,
        expires_in_hours: Optional[int] = None
    ) -> Notification:
        """Create and store a new notification."""
        
        notification_id = f"notif_{int(datetime.now().timestamp() * 1000)}"
        
        notification = Notification(
            id=notification_id,
            title=title,
            message=message,
            type=type,
            priority=priority,
            user_id=user_id,
            metadata=metadata,
            actions=actions
        )
        
        # Set custom expiry if provided
        if expires_in_hours:
            notification.expires_at = notification.created_at + timedelta(hours=expires_in_hours)
        
        # Store in database
        try:
            conn = sqlite3.connect('grainchain_notifications.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO notifications 
                (id, title, message, type, priority, user_id, created_at, expires_at, metadata, actions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                notification.id,
                notification.title,
                notification.message,
                notification.type.value,
                notification.priority.value,
                notification.user_id,
                notification.created_at,
                notification.expires_at,
                json.dumps(notification.metadata) if notification.metadata else None,
                json.dumps(notification.actions) if notification.actions else None
            ))
            
            conn.commit()
            conn.close()
            
            # Add to buffer for quick access
            self.notification_buffer.append(notification)
            
            # Deliver notification
            self._deliver_notification(notification)
            
            logger.info(f"Created notification: {notification.id}")
            return notification
            
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            return notification
    
    def _deliver_notification(self, notification: Notification):
        """Deliver notification to subscribers."""
        try:
            # Check user preferences
            if notification.user_id and not self._should_deliver(notification):
                return
            
            # Deliver to specific user or broadcast
            target_users = [notification.user_id] if notification.user_id else list(self.subscribers.keys())
            
            for user_id in target_users:
                if user_id in self.subscribers:
                    for callback in self.subscribers[user_id]:
                        try:
                            callback(notification)
                        except Exception as e:
                            logger.error(f"Error delivering notification to user {user_id}: {e}")
            
        except Exception as e:
            logger.error(f"Error in notification delivery: {e}")
    
    def _should_deliver(self, notification: Notification) -> bool:
        """Check if notification should be delivered based on user preferences."""
        try:
            conn = sqlite3.connect('grainchain_notifications.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT email_enabled, push_enabled, types_enabled, quiet_hours_start, quiet_hours_end
                FROM notification_preferences WHERE user_id = ?
            ''', (notification.user_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                return True  # Default to deliver if no preferences set
            
            email_enabled, push_enabled, types_enabled, quiet_start, quiet_end = row
            
            # Check if notification type is enabled
            enabled_types = json.loads(types_enabled)
            if notification.type.value not in enabled_types:
                return False
            
            # Check quiet hours
            if quiet_start and quiet_end:
                current_time = datetime.now().time()
                quiet_start_time = datetime.strptime(quiet_start, "%H:%M:%S").time()
                quiet_end_time = datetime.strptime(quiet_end, "%H:%M:%S").time()
                
                if quiet_start_time <= current_time <= quiet_end_time:
                    # Only deliver urgent notifications during quiet hours
                    return notification.priority == NotificationPriority.URGENT
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking delivery preferences: {e}")
            return True
    
    def subscribe(self, user_id: int, callback: Callable[[Notification], None]):
        """Subscribe to notifications for a user."""
        self.subscribers[user_id].append(callback)
        logger.info(f"User {user_id} subscribed to notifications")
    
    def unsubscribe(self, user_id: int, callback: Callable[[Notification], None]):
        """Unsubscribe from notifications."""
        if user_id in self.subscribers:
            try:
                self.subscribers[user_id].remove(callback)
                if not self.subscribers[user_id]:
                    del self.subscribers[user_id]
                logger.info(f"User {user_id} unsubscribed from notifications")
            except ValueError:
                pass
    
    def get_notifications(
        self,
        user_id: Optional[int] = None,
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        """Get notifications for a user."""
        try:
            conn = sqlite3.connect('grainchain_notifications.db')
            cursor = conn.cursor()
            
            query = '''
                SELECT id, title, message, type, priority, user_id, created_at, read_at, expires_at, metadata, actions
                FROM notifications
                WHERE (user_id = ? OR user_id IS NULL)
                AND expires_at > ?
            '''
            params = [user_id, datetime.now()]
            
            if unread_only:
                query += ' AND read_at IS NULL'
            
            query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            notifications = []
            for row in rows:
                notification = Notification(
                    id=row[0],
                    title=row[1],
                    message=row[2],
                    type=NotificationType(row[3]),
                    priority=NotificationPriority(row[4]),
                    user_id=row[5],
                    created_at=datetime.fromisoformat(row[6]),
                    read_at=datetime.fromisoformat(row[7]) if row[7] else None,
                    expires_at=datetime.fromisoformat(row[8]) if row[8] else None,
                    metadata=json.loads(row[9]) if row[9] else None,
                    actions=json.loads(row[10]) if row[10] else None
                )
                notifications.append(notification)
            
            return notifications
            
        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            return []
    
    def mark_as_read(self, notification_id: str, user_id: Optional[int] = None):
        """Mark notification as read."""
        try:
            conn = sqlite3.connect('grainchain_notifications.db')
            cursor = conn.cursor()
            
            query = 'UPDATE notifications SET read_at = ? WHERE id = ?'
            params = [datetime.now(), notification_id]
            
            if user_id:
                query += ' AND (user_id = ? OR user_id IS NULL)'
                params.append(user_id)
            
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            
            logger.info(f"Marked notification {notification_id} as read")
            
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
    
    def delete_notification(self, notification_id: str, user_id: Optional[int] = None):
        """Delete a notification."""
        try:
            conn = sqlite3.connect('grainchain_notifications.db')
            cursor = conn.cursor()
            
            query = 'DELETE FROM notifications WHERE id = ?'
            params = [notification_id]
            
            if user_id:
                query += ' AND (user_id = ? OR user_id IS NULL)'
                params.append(user_id)
            
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            
            logger.info(f"Deleted notification {notification_id}")
            
        except Exception as e:
            logger.error(f"Error deleting notification: {e}")
    
    def cleanup_expired_notifications(self):
        """Remove expired notifications."""
        try:
            conn = sqlite3.connect('grainchain_notifications.db')
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM notifications WHERE expires_at < ?', (datetime.now(),))
            deleted_count = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            if deleted_count > 0:
                logger.info(f"Cleaned up {deleted_count} expired notifications")
            
        except Exception as e:
            logger.error(f"Error cleaning up notifications: {e}")
    
    def log_activity(
        self,
        user_id: Optional[int],
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log user activity to the activity feed."""
        try:
            conn = sqlite3.connect('grainchain_notifications.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO activity_feed (user_id, action, resource_type, resource_id, description, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                action,
                resource_type,
                resource_id,
                description,
                json.dumps(metadata) if metadata else None
            ))
            
            conn.commit()
            conn.close()
            
            # Create notification for significant activities
            if action in ['created', 'deleted', 'error']:
                self.create_notification(
                    title=f"{resource_type.title()} {action}",
                    message=description,
                    type=NotificationType.ERROR if action == 'error' else NotificationType.INFO,
                    user_id=user_id,
                    metadata=metadata
                )
            
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
    
    def get_activity_feed(
        self,
        user_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get activity feed entries."""
        try:
            conn = sqlite3.connect('grainchain_notifications.db')
            cursor = conn.cursor()
            
            query = '''
                SELECT id, user_id, action, resource_type, resource_id, description, timestamp, metadata
                FROM activity_feed
            '''
            params = []
            
            if user_id:
                query += ' WHERE user_id = ?'
                params.append(user_id)
            
            query += ' ORDER BY timestamp DESC LIMIT ? OFFSET ?'
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            activities = []
            for row in rows:
                activity = {
                    'id': row[0],
                    'user_id': row[1],
                    'action': row[2],
                    'resource_type': row[3],
                    'resource_id': row[4],
                    'description': row[5],
                    'timestamp': row[6],
                    'metadata': json.loads(row[7]) if row[7] else None
                }
                activities.append(activity)
            
            return activities
            
        except Exception as e:
            logger.error(f"Error getting activity feed: {e}")
            return []
    
    def update_preferences(
        self,
        user_id: int,
        email_enabled: bool = True,
        push_enabled: bool = True,
        sound_enabled: bool = True,
        enabled_types: List[str] = None,
        quiet_hours_start: Optional[str] = None,
        quiet_hours_end: Optional[str] = None
    ):
        """Update notification preferences for a user."""
        try:
            if enabled_types is None:
                enabled_types = ["info", "success", "warning", "error", "system"]
            
            conn = sqlite3.connect('grainchain_notifications.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO notification_preferences 
                (user_id, email_enabled, push_enabled, sound_enabled, types_enabled, 
                 quiet_hours_start, quiet_hours_end, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                email_enabled,
                push_enabled,
                sound_enabled,
                json.dumps(enabled_types),
                quiet_hours_start,
                quiet_hours_end,
                datetime.now()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Updated notification preferences for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error updating notification preferences: {e}")

# Global notification manager instance
notification_manager = NotificationManager()

# Convenience functions for common notification types
def notify_success(title: str, message: str, user_id: Optional[int] = None, **kwargs):
    """Create a success notification."""
    return notification_manager.create_notification(
        title, message, NotificationType.SUCCESS, user_id=user_id, **kwargs
    )

def notify_error(title: str, message: str, user_id: Optional[int] = None, **kwargs):
    """Create an error notification."""
    return notification_manager.create_notification(
        title, message, NotificationType.ERROR, NotificationPriority.HIGH, user_id=user_id, **kwargs
    )

def notify_warning(title: str, message: str, user_id: Optional[int] = None, **kwargs):
    """Create a warning notification."""
    return notification_manager.create_notification(
        title, message, NotificationType.WARNING, user_id=user_id, **kwargs
    )

def notify_info(title: str, message: str, user_id: Optional[int] = None, **kwargs):
    """Create an info notification."""
    return notification_manager.create_notification(
        title, message, NotificationType.INFO, user_id=user_id, **kwargs
    )
