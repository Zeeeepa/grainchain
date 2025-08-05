"""Provider settings and configuration components."""

import reflex as rx
from typing import Dict, Any

def provider_status_badge(status: str) -> rx.Component:
    """Create a status badge for provider health."""
    color_map = {
        "healthy": "green",
        "unhealthy": "red", 
        "unknown": "gray",
        "error": "red"
    }
    
    return rx.badge(
        status.title(),
        color_scheme=color_map.get(status, "gray"),
        variant="solid"
    )

def provider_card(name: str, info: Dict[str, Any], is_selected: bool = False) -> rx.Component:
    """Create a provider card with status and configuration."""
    
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading(name.title(), size="4"),
                provider_status_badge(info.get("status", "unknown")),
                justify="between",
                width="100%"
            ),
            rx.text(
                f"Available: {'Yes' if info.get('available', False) else 'No'}",
                size="2",
                color="gray"
            ),
            rx.text(
                f"Dependencies: {'Installed' if info.get('dependencies_installed', False) else 'Missing'}",
                size="2", 
                color="gray"
            ),
            rx.cond(
                info.get("missing_config"),
                rx.text(
                    f"Missing config: {', '.join(info.get('missing_config', []))}",
                    size="2",
                    color="red"
                )
            ),
            spacing="2",
            align="start"
        ),
        variant="surface" if not is_selected else "classic",
        style={
            "cursor": "pointer",
            "border": "2px solid var(--accent-9)" if is_selected else "1px solid var(--gray-6)",
            "min_height": "120px"
        },
        on_click=lambda: rx.call_script(f"window.selectProvider('{name}')")
    )

def provider_settings_form(provider: str, settings: Dict[str, Any]) -> rx.Component:
    """Create a settings form for a specific provider."""
    
    if provider == "local":
        return rx.vstack(
            rx.heading(f"{provider.title()} Settings", size="4"),
            rx.form_field(
                rx.form_label("Working Directory"),
                rx.input(
                    value=settings.get("working_directory", "./workspace"),
                    on_change=lambda v: rx.call_script(f"window.updateProviderSetting('{provider}', 'working_directory', '{v}')")
                ),
                name="working_directory"
            ),
            rx.form_field(
                rx.form_label("Timeout (seconds)"),
                rx.number_input(
                    value=settings.get("timeout", 60),
                    on_change=lambda v: rx.call_script(f"window.updateProviderSetting('{provider}', 'timeout', {v})")
                ),
                name="timeout"
            ),
            spacing="4"
        )
    
    elif provider == "e2b":
        return rx.vstack(
            rx.heading(f"{provider.upper()} Settings", size="4"),
            rx.form_field(
                rx.form_label("API Key"),
                rx.input(
                    type="password",
                    value=settings.get("api_key", ""),
                    placeholder="Enter E2B API key",
                    on_change=lambda v: rx.call_script(f"window.updateProviderSetting('{provider}', 'api_key', '{v}')")
                ),
                name="api_key"
            ),
            rx.form_field(
                rx.form_label("Template"),
                rx.input(
                    value=settings.get("template", "base"),
                    placeholder="E2B template name",
                    on_change=lambda v: rx.call_script(f"window.updateProviderSetting('{provider}', 'template', '{v}')")
                ),
                name="template"
            ),
            rx.form_field(
                rx.form_label("Timeout (seconds)"),
                rx.number_input(
                    value=settings.get("timeout", 300),
                    on_change=lambda v: rx.call_script(f"window.updateProviderSetting('{provider}', 'timeout', {v})")
                ),
                name="timeout"
            ),
            spacing="4"
        )
    
    elif provider == "daytona":
        return rx.vstack(
            rx.heading(f"{provider.title()} Settings", size="4"),
            rx.form_field(
                rx.form_label("API Key"),
                rx.input(
                    type="password",
                    value=settings.get("api_key", ""),
                    placeholder="Enter Daytona API key",
                    on_change=lambda v: rx.call_script(f"window.updateProviderSetting('{provider}', 'api_key', '{v}')")
                ),
                name="api_key"
            ),
            rx.form_field(
                rx.form_label("Workspace Template"),
                rx.input(
                    value=settings.get("workspace_template", "python-dev"),
                    placeholder="Workspace template name",
                    on_change=lambda v: rx.call_script(f"window.updateProviderSetting('{provider}', 'workspace_template', '{v}')")
                ),
                name="workspace_template"
            ),
            rx.form_field(
                rx.form_label("Timeout (seconds)"),
                rx.number_input(
                    value=settings.get("timeout", 300),
                    on_change=lambda v: rx.call_script(f"window.updateProviderSetting('{provider}', 'timeout', {v})")
                ),
                name="timeout"
            ),
            spacing="4"
        )
    
    elif provider == "morph":
        return rx.vstack(
            rx.heading(f"{provider.title()} Settings", size="4"),
            rx.form_field(
                rx.form_label("API Key"),
                rx.input(
                    type="password",
                    value=settings.get("api_key", ""),
                    placeholder="Enter Morph API key",
                    on_change=lambda v: rx.call_script(f"window.updateProviderSetting('{provider}', 'api_key', '{v}')")
                ),
                name="api_key"
            ),
            rx.form_field(
                rx.form_label("Image ID"),
                rx.input(
                    value=settings.get("image_id", "morphvm-minimal"),
                    placeholder="Morph image ID",
                    on_change=lambda v: rx.call_script(f"window.updateProviderSetting('{provider}', 'image_id', '{v}')")
                ),
                name="image_id"
            ),
            rx.hstack(
                rx.form_field(
                    rx.form_label("vCPUs"),
                    rx.number_input(
                        value=settings.get("vcpus", 2),
                        min=1,
                        max=16,
                        on_change=lambda v: rx.call_script(f"window.updateProviderSetting('{provider}', 'vcpus', {v})")
                    ),
                    name="vcpus"
                ),
                rx.form_field(
                    rx.form_label("Memory (MB)"),
                    rx.number_input(
                        value=settings.get("memory", 2048),
                        min=512,
                        max=32768,
                        step=512,
                        on_change=lambda v: rx.call_script(f"window.updateProviderSetting('{provider}', 'memory', {v})")
                    ),
                    name="memory"
                ),
                spacing="4"
            ),
            rx.form_field(
                rx.form_label("Disk Size (MB)"),
                rx.number_input(
                    value=settings.get("disk_size", 8192),
                    min=1024,
                    max=102400,
                    step=1024,
                    on_change=lambda v: rx.call_script(f"window.updateProviderSetting('{provider}', 'disk_size', {v})")
                ),
                name="disk_size"
            ),
            spacing="4"
        )
    
    elif provider == "modal":
        return rx.vstack(
            rx.heading(f"{provider.title()} Settings", size="4"),
            rx.form_field(
                rx.form_label("Token ID"),
                rx.input(
                    value=settings.get("token_id", ""),
                    placeholder="Enter Modal token ID",
                    on_change=lambda v: rx.call_script(f"window.updateProviderSetting('{provider}', 'token_id', '{v}')")
                ),
                name="token_id"
            ),
            rx.form_field(
                rx.form_label("Token Secret"),
                rx.input(
                    type="password",
                    value=settings.get("token_secret", ""),
                    placeholder="Enter Modal token secret",
                    on_change=lambda v: rx.call_script(f"window.updateProviderSetting('{provider}', 'token_secret', '{v}')")
                ),
                name="token_secret"
            ),
            rx.form_field(
                rx.form_label("Timeout (seconds)"),
                rx.number_input(
                    value=settings.get("timeout", 300),
                    on_change=lambda v: rx.call_script(f"window.updateProviderSetting('{provider}', 'timeout', {v})")
                ),
                name="timeout"
            ),
            spacing="4"
        )
    
    else:
        return rx.text(f"No settings available for {provider}")

def provider_selector() -> rx.Component:
    """Create a provider selector component."""
    from grainchain_dashboard.state import DashboardState
    
    return rx.vstack(
        rx.heading("Select Provider", size="5"),
        rx.grid(
            rx.foreach(
                DashboardState.providers,
                lambda provider_item: provider_card(
                    provider_item[0],  # provider name
                    provider_item[1],  # provider info
                    DashboardState.selected_provider == provider_item[0]
                )
            ),
            columns="3",
            spacing="4",
            width="100%"
        ),
        rx.hstack(
            rx.button(
                "Refresh Providers",
                on_click=DashboardState.refresh_providers,
                loading=DashboardState.loading,
                variant="outline"
            ),
            rx.button(
                "Settings",
                on_click=DashboardState.open_settings,
                variant="outline"
            ),
            spacing="2"
        ),
        spacing="4",
        width="100%"
    )

def settings_dialog() -> rx.Component:
    """Create the settings dialog."""
    from grainchain_dashboard.state import DashboardState
    
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Provider Settings"),
            rx.dialog.description("Configure your sandbox providers"),
            
            rx.tabs.root(
                rx.tabs.list(
                    rx.foreach(
                        DashboardState.provider_settings,
                        lambda provider_item: rx.tabs.trigger(
                            provider_item[0].title(),
                            value=provider_item[0]
                        )
                    )
                ),
                rx.foreach(
                    DashboardState.provider_settings,
                    lambda provider_item: rx.tabs.content(
                        provider_settings_form(
                            provider_item[0],  # provider name
                            provider_item[1]   # provider settings
                        ),
                        value=provider_item[0]
                    )
                ),
                default_value="local"
            ),
            
            rx.flex(
                rx.dialog.close(
                    rx.button("Cancel", variant="soft", color_scheme="gray")
                ),
                rx.button(
                    "Save Settings",
                    on_click=DashboardState.save_provider_settings,
                    loading=DashboardState.loading
                ),
                spacing="3",
                margin_top="16px",
                justify="end"
            ),
            
            style={"max_width": "600px", "width": "90vw"}
        ),
        open=DashboardState.settings_open,
        on_open_change=DashboardState.close_settings
    )
