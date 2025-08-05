#!/usr/bin/env python3
"""Authentication and user management system."""

import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import reflex as rx
from cryptography.fernet import Fernet
import sqlite3
import logging

logger = logging.getLogger(__name__)

class UserRole(Enum):
    """User roles for access control."""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"

@dataclass
class User:
    """User data model."""
    id: int
    username: str
    email: str
    role: UserRole
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    api_keys: List[str] = None

class AuthManager:
    """Manages authentication and user sessions."""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.fernet = Fernet(Fernet.generate_key())
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.init_database()
    
    def init_database(self):
        """Initialize user database tables."""
        try:
            conn = sqlite3.connect('grainchain.db')
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    api_keys TEXT
                )
            ''')
            
            # Sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    ip_address TEXT,
                    user_agent TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # API keys table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    key_name TEXT NOT NULL,
                    key_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    permissions TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            # Create default admin user if none exists
            self.create_default_admin()
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    def create_default_admin(self):
        """Create default admin user if none exists."""
        try:
            conn = sqlite3.connect('grainchain.db')
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM users WHERE role = ?', ('admin',))
            admin_count = cursor.fetchone()[0]
            
            if admin_count == 0:
                # Create default admin
                salt = secrets.token_hex(16)
                password_hash = self.hash_password('admin123', salt)
                
                cursor.execute('''
                    INSERT INTO users (username, email, password_hash, salt, role)
                    VALUES (?, ?, ?, ?, ?)
                ''', ('admin', 'admin@grainchain.local', password_hash, salt, 'admin'))
                
                conn.commit()
                logger.info("Default admin user created: admin/admin123")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error creating default admin: {e}")
    
    def hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt."""
        return hashlib.pbkdf2_hex(password.encode(), salt.encode(), 100000)
    
    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verify password against hash."""
        return self.hash_password(password, salt) == password_hash
    
    def create_user(self, username: str, email: str, password: str, role: UserRole = UserRole.USER) -> Optional[User]:
        """Create a new user."""
        try:
            conn = sqlite3.connect('grainchain.db')
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
            if cursor.fetchone():
                return None  # User already exists
            
            # Create new user
            salt = secrets.token_hex(16)
            password_hash = self.hash_password(password, salt)
            
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, salt, role)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password_hash, salt, role.value))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return User(
                id=user_id,
                username=username,
                email=email,
                role=role,
                created_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials."""
        try:
            conn = sqlite3.connect('grainchain.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, username, email, password_hash, salt, role, created_at, last_login, is_active
                FROM users WHERE username = ? AND is_active = 1
            ''', (username,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            user_id, username, email, password_hash, salt, role, created_at, last_login, is_active = row
            
            if not self.verify_password(password, password_hash, salt):
                return None
            
            # Update last login
            cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))
            conn.commit()
            conn.close()
            
            return User(
                id=user_id,
                username=username,
                email=email,
                role=UserRole(role),
                created_at=datetime.fromisoformat(created_at),
                last_login=datetime.fromisoformat(last_login) if last_login else None
            )
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    def create_session(self, user: User, ip_address: str = None, user_agent: str = None) -> str:
        """Create a new user session."""
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=24)  # 24 hour sessions
        
        try:
            conn = sqlite3.connect('grainchain.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO sessions (id, user_id, expires_at, ip_address, user_agent)
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, user.id, expires_at, ip_address, user_agent))
            
            conn.commit()
            conn.close()
            
            # Store in memory for quick access
            self.active_sessions[session_id] = {
                'user': user,
                'created_at': datetime.now(),
                'expires_at': expires_at,
                'ip_address': ip_address,
                'user_agent': user_agent
            }
            
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return None
    
    def validate_session(self, session_id: str) -> Optional[User]:
        """Validate session and return user if valid."""
        if not session_id:
            return None
        
        # Check memory first
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            if datetime.now() < session['expires_at']:
                return session['user']
            else:
                # Session expired, remove from memory
                del self.active_sessions[session_id]
        
        # Check database
        try:
            conn = sqlite3.connect('grainchain.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.user_id, s.expires_at, u.username, u.email, u.role, u.created_at, u.last_login
                FROM sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.id = ? AND s.is_active = 1 AND u.is_active = 1
            ''', (session_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            user_id, expires_at, username, email, role, created_at, last_login = row
            expires_at = datetime.fromisoformat(expires_at)
            
            if datetime.now() >= expires_at:
                # Session expired, deactivate
                cursor.execute('UPDATE sessions SET is_active = 0 WHERE id = ?', (session_id,))
                conn.commit()
                conn.close()
                return None
            
            conn.close()
            
            user = User(
                id=user_id,
                username=username,
                email=email,
                role=UserRole(role),
                created_at=datetime.fromisoformat(created_at),
                last_login=datetime.fromisoformat(last_login) if last_login else None
            )
            
            # Cache in memory
            self.active_sessions[session_id] = {
                'user': user,
                'created_at': datetime.now(),
                'expires_at': expires_at
            }
            
            return user
            
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return None
    
    def logout(self, session_id: str):
        """Logout user and invalidate session."""
        try:
            # Remove from memory
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            # Deactivate in database
            conn = sqlite3.connect('grainchain.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE sessions SET is_active = 0 WHERE id = ?', (session_id,))
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
    
    def create_api_key(self, user_id: int, key_name: str, permissions: List[str] = None) -> str:
        """Create API key for user."""
        api_key = f"gck_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        try:
            conn = sqlite3.connect('grainchain.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO api_keys (user_id, key_name, key_hash, permissions)
                VALUES (?, ?, ?, ?)
            ''', (user_id, key_name, key_hash, ','.join(permissions or [])))
            
            conn.commit()
            conn.close()
            
            return api_key
            
        except Exception as e:
            logger.error(f"Error creating API key: {e}")
            return None
    
    def validate_api_key(self, api_key: str) -> Optional[User]:
        """Validate API key and return associated user."""
        if not api_key or not api_key.startswith('gck_'):
            return None
        
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        try:
            conn = sqlite3.connect('grainchain.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT ak.user_id, u.username, u.email, u.role, u.created_at, u.last_login
                FROM api_keys ak
                JOIN users u ON ak.user_id = u.id
                WHERE ak.key_hash = ? AND ak.is_active = 1 AND u.is_active = 1
            ''', (key_hash,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            user_id, username, email, role, created_at, last_login = row
            
            # Update last used
            cursor.execute('UPDATE api_keys SET last_used = CURRENT_TIMESTAMP WHERE key_hash = ?', (key_hash,))
            conn.commit()
            conn.close()
            
            return User(
                id=user_id,
                username=username,
                email=email,
                role=UserRole(role),
                created_at=datetime.fromisoformat(created_at),
                last_login=datetime.fromisoformat(last_login) if last_login else None
            )
            
        except Exception as e:
            logger.error(f"API key validation error: {e}")
            return None

# Global auth manager instance
auth_manager = AuthManager()

class AuthState(rx.State):
    """Authentication state for Reflex app."""
    
    is_authenticated: bool = False
    current_user: Optional[Dict[str, Any]] = None
    session_id: str = ""
    login_error: str = ""
    
    def login(self, username: str, password: str):
        """Login user."""
        user = auth_manager.authenticate_user(username, password)
        if user:
            session_id = auth_manager.create_session(user)
            if session_id:
                self.is_authenticated = True
                self.current_user = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role.value
                }
                self.session_id = session_id
                self.login_error = ""
                return rx.redirect("/dashboard")
            else:
                self.login_error = "Failed to create session"
        else:
            self.login_error = "Invalid username or password"
    
    def logout(self):
        """Logout user."""
        if self.session_id:
            auth_manager.logout(self.session_id)
        
        self.is_authenticated = False
        self.current_user = None
        self.session_id = ""
        self.login_error = ""
        return rx.redirect("/login")
    
    def check_session(self):
        """Check if current session is valid."""
        if self.session_id:
            user = auth_manager.validate_session(self.session_id)
            if user:
                self.is_authenticated = True
                self.current_user = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role.value
                }
            else:
                self.logout()
    
    def require_auth(self):
        """Require authentication for protected routes."""
        if not self.is_authenticated:
            return rx.redirect("/login")
    
    def require_role(self, required_role: UserRole):
        """Require specific role for access."""
        if not self.is_authenticated:
            return rx.redirect("/login")
        
        if self.current_user and UserRole(self.current_user['role']) != required_role:
            return rx.redirect("/unauthorized")

# Export for use in main app
__all__ = ['AuthManager', 'AuthState', 'User', 'UserRole', 'auth_manager']
