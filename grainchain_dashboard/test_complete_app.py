#!/usr/bin/env python3
"""Test script to verify the complete dashboard implementation."""

import sys
import os
import subprocess
import time
import requests
from pathlib import Path

def test_dependencies():
    """Test if all required dependencies are available."""
    print("🔍 Testing dependencies...")
    
    try:
        import reflex
        print(f"✅ Reflex: {reflex.__version__}")
    except ImportError:
        print("❌ Reflex not installed")
        return False
    
    try:
        import sqlalchemy
        print(f"✅ SQLAlchemy: {sqlalchemy.__version__}")
    except ImportError:
        print("❌ SQLAlchemy not installed")
        return False
    
    try:
        import cryptography
        print(f"✅ Cryptography: {cryptography.__version__}")
    except ImportError:
        print("❌ Cryptography not installed")
        return False
    
    return True

def test_imports():
    """Test if all our modules can be imported."""
    print("\n🔍 Testing module imports...")
    
    try:
        from models import Base, ProviderConfig
        print("✅ Database models")
    except ImportError as e:
        print(f"❌ Database models: {e}")
        return False
    
    try:
        from database import init_database
        print("✅ Database initialization")
    except ImportError as e:
        print(f"❌ Database initialization: {e}")
        return False
    
    try:
        from enhanced_state import EnhancedDashboardState
        print("✅ Enhanced state management")
    except ImportError as e:
        print(f"❌ Enhanced state management: {e}")
        return False
    
    try:
        from components.ui_components import modal_dialog
        print("✅ UI components")
    except ImportError as e:
        print(f"❌ UI components: {e}")
        return False
    
    try:
        from utils.encryption import encrypt_api_key
        print("✅ Encryption utilities")
    except ImportError as e:
        print(f"❌ Encryption utilities: {e}")
        return False
    
    return True

def test_database_init():
    """Test database initialization."""
    print("\n🔍 Testing database initialization...")
    
    try:
        from database import init_database, get_db_session
        from models import ProviderConfig
        
        # Initialize database
        init_database()
        print("✅ Database initialized")
        
        # Test database connection
        with get_db_session() as db:
            providers = db.query(ProviderConfig).all()
            print(f"✅ Database connection works, found {len(providers)} providers")
        
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def test_encryption():
    """Test encryption functionality."""
    print("\n🔍 Testing encryption...")
    
    try:
        from utils.encryption import encrypt_api_key, decrypt_api_key
        
        test_key = "test-api-key-12345"
        encrypted = encrypt_api_key(test_key)
        decrypted = decrypt_api_key(encrypted)
        
        if decrypted == test_key:
            print("✅ Encryption/decryption works")
            return True
        else:
            print("❌ Encryption/decryption failed")
            return False
    except Exception as e:
        print(f"❌ Encryption test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Complete Grainchain Dashboard Implementation\n")
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Module Imports", test_imports),
        ("Database Initialization", test_database_init),
        ("Encryption", test_encryption),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*50)
    print("📊 TEST RESULTS")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! The implementation is ready to run.")
        return True
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
