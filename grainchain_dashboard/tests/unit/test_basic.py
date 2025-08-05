"""Basic tests for Grainchain Dashboard."""

import pytest
from unittest.mock import Mock, patch
import asyncio

def test_config_loading():
    """Test that configuration loads properly."""
    from grainchain_dashboard.config import config, get_enabled_providers
    
    assert config.app_name == "Grainchain Dashboard"
    assert config.default_provider == "local"
    
    # Test provider configs
    providers = get_enabled_providers()
    assert "local" in providers
    assert providers["local"].enabled is True

def test_grainchain_service_init():
    """Test that GrainchainService initializes properly."""
    from grainchain_dashboard.services.grainchain_service import GrainchainService
    
    service = GrainchainService()
    assert service.active_sandboxes == {}
    assert service.sandbox_info == {}
    assert service.snapshots == {}

@pytest.mark.asyncio
async def test_async_bridge():
    """Test the async-to-sync bridge functionality."""
    from grainchain_dashboard.services.grainchain_service import GrainchainService
    
    service = GrainchainService()
    
    # Test async coroutine execution
    async def test_coro():
        await asyncio.sleep(0.01)
        return "test_result"
    
    result = service._run_async(test_coro())
    assert result == "test_result"

def test_dashboard_state_init():
    """Test that DashboardState initializes with correct defaults."""
    from grainchain_dashboard.state import DashboardState
    
    state = DashboardState()
    assert state.current_page == "dashboard"
    assert state.sidebar_open is True
    assert state.loading is False
    assert state.selected_provider == "local"  # from config default

@patch('grainchain_dashboard.services.grainchain_service.get_providers_info')
def test_provider_status_mock(mock_get_providers):
    """Test provider status retrieval with mocked data."""
    from grainchain_dashboard.services.grainchain_service import GrainchainService
    
    # Mock provider info
    mock_get_providers.return_value = {
        "local": Mock(
            available=True,
            dependencies_installed=True,
            config_valid=True,
            missing_config=[],
            setup_instructions=""
        ),
        "e2b": Mock(
            available=False,
            dependencies_installed=False,
            config_valid=False,
            missing_config=["E2B_API_KEY"],
            setup_instructions="Install with: pip install grainchain[e2b]"
        )
    }
    
    service = GrainchainService()
    status = service.get_provider_status()
    
    assert "local" in status
    assert "e2b" in status
    assert status["local"]["available"] is True
    assert status["e2b"]["available"] is False

def test_file_size_formatting():
    """Test file size formatting utility."""
    from grainchain_dashboard.components.file_browser import format_file_size
    
    assert format_file_size(0) == "0 B"
    assert format_file_size(1024) == "1.0 KB"
    assert format_file_size(1024 * 1024) == "1.0 MB"
    assert format_file_size(1536) == "1.5 KB"

if __name__ == "__main__":
    pytest.main([__file__])

