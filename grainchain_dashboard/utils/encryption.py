"""Encryption utilities for secure API key storage."""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)

class EncryptionManager:
    """Manages encryption and decryption of sensitive data."""
    
    def __init__(self):
        self._fernet = None
        self._initialize_encryption()
    
    def _initialize_encryption(self):
        """Initialize encryption with key derivation."""
        try:
            # Get or generate encryption key
            encryption_key = self._get_or_create_key()
            self._fernet = Fernet(encryption_key)
            logger.info("Encryption initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            raise
    
    def _get_or_create_key(self) -> bytes:
        """Get existing encryption key or create a new one."""
        key_file = os.path.join(os.path.dirname(__file__), "..", ".encryption_key")
        
        if os.path.exists(key_file):
            # Load existing key
            try:
                with open(key_file, "rb") as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Failed to load existing key: {e}")
        
        # Generate new key
        password = os.getenv("ENCRYPTION_PASSWORD", "grainchain-dashboard-default-key").encode()
        salt = os.getenv("ENCRYPTION_SALT", "grainchain-salt").encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        
        # Save key for future use
        try:
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            with open(key_file, "wb") as f:
                f.write(key)
            # Set restrictive permissions
            os.chmod(key_file, 0o600)
            logger.info("New encryption key generated and saved")
        except Exception as e:
            logger.warning(f"Failed to save encryption key: {e}")
        
        return key
    
    def encrypt(self, data: str) -> str:
        """Encrypt a string and return base64 encoded result."""
        if not data:
            return ""
        
        try:
            encrypted_data = self._fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt base64 encoded data and return original string."""
        if not encrypted_data:
            return ""
        
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self._fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise
    
    def is_encrypted(self, data: str) -> bool:
        """Check if data appears to be encrypted."""
        if not data:
            return False
        
        try:
            # Try to decode as base64 and decrypt
            decoded_data = base64.urlsafe_b64decode(data.encode())
            self._fernet.decrypt(decoded_data)
            return True
        except:
            return False

# Global encryption manager instance
encryption_manager = EncryptionManager()

def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key for secure storage."""
    return encryption_manager.encrypt(api_key)

def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an API key for use."""
    return encryption_manager.decrypt(encrypted_key)

def is_api_key_encrypted(api_key: str) -> bool:
    """Check if an API key is encrypted."""
    return encryption_manager.is_encrypted(api_key)

def secure_api_key_display(api_key: str) -> str:
    """Display API key in a secure format (masked)."""
    if not api_key:
        return ""
    
    # Decrypt if encrypted
    if is_api_key_encrypted(api_key):
        try:
            api_key = decrypt_api_key(api_key)
        except:
            return "***INVALID***"
    
    # Mask the key
    if len(api_key) <= 8:
        return "*" * len(api_key)
    else:
        return api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]

def validate_api_key_format(provider: str, api_key: str) -> tuple[bool, str]:
    """Validate API key format for different providers."""
    if not api_key:
        return False, "API key cannot be empty"
    
    # Decrypt if encrypted
    if is_api_key_encrypted(api_key):
        try:
            api_key = decrypt_api_key(api_key)
        except:
            return False, "Invalid encrypted API key"
    
    # Provider-specific validation
    if provider == "e2b":
        if not api_key.startswith("e2b_"):
            return False, "E2B API key must start with 'e2b_'"
        if len(api_key) < 20:
            return False, "E2B API key appears to be too short"
    
    elif provider == "daytona":
        if len(api_key) < 16:
            return False, "Daytona API key appears to be too short"
    
    elif provider == "morph":
        if len(api_key) < 16:
            return False, "Morph API key appears to be too short"
    
    elif provider == "modal":
        if not (api_key.startswith("ak-") or api_key.startswith("as-")):
            return False, "Modal API key must start with 'ak-' or 'as-'"
    
    # General validation
    if len(api_key) < 8:
        return False, "API key appears to be too short"
    
    if len(api_key) > 200:
        return False, "API key appears to be too long"
    
    # Check for suspicious characters
    if any(char in api_key for char in [" ", "\n", "\t", "\r"]):
        return False, "API key contains invalid whitespace characters"
    
    return True, "API key format is valid"

def sanitize_input(input_str: str, max_length: int = 1000) -> str:
    """Sanitize user input to prevent injection attacks."""
    if not input_str:
        return ""
    
    # Truncate if too long
    if len(input_str) > max_length:
        input_str = input_str[:max_length]
    
    # Remove null bytes and control characters
    sanitized = "".join(char for char in input_str if ord(char) >= 32 or char in ["\n", "\t"])
    
    return sanitized.strip()

def hash_sensitive_data(data: str) -> str:
    """Create a hash of sensitive data for logging/comparison without storing the actual data."""
    import hashlib
    return hashlib.sha256(data.encode()).hexdigest()[:16]  # First 16 chars for brevity
