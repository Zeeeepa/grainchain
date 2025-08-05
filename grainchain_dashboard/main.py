"""Main Grainchain Dashboard application."""

import reflex as rx
from grainchain_dashboard.state import DashboardState
from grainchain_dashboard.config import config

# Import all page components
from grainchain_dashboard.pages.dashboard import dashboard_page
from grainchain_dashboard.components.provider_settings import provider_selector, settings_dialog
from grainchain_dashboard.components.command_terminal import command_terminal
from grainchain_dashboard.components.file_browser import file_browser
from grainchain_dashboard.components.snapshot_manager import snapshot_manager
from grainchain_dashboard.components.sidebar import sidebar, compact_sidebar
from grainchain_dashboard.components.status_bar import status_bar, notification_toast, loading_overlay

def page_content() -> rx.Component:
    """Render the appropriate page content based on current page."""
    return rx.match(
        DashboardState.current_page,
        ("dashboard", dashboard_page()),
        ("providers", provider_selector()),
        ("terminal", command_terminal()),
        ("files", file_browser()),
        ("snapshots", snapshot_manager()),
        ("monitoring", rx.text("Monitoring page - Coming soon!")),
        ("settings", rx.text("Settings page - Coming soon!")),
        dashboard_page()  # Default fallback
    )

def main_layout() -> rx.Component:
    """Main application layout."""
    return rx.box(
        rx.hstack(
            # Sidebar
            rx.cond(
                DashboardState.sidebar_open,
                sidebar(),
                compact_sidebar()
            ),
            
            # Main content area
            rx.box(
                rx.vstack(
                    # Header
                    rx.box(
                        rx.hstack(
                            rx.heading(
                                rx.match(
                                    DashboardState.current_page,
                                    ("dashboard", "Dashboard"),
                                    ("providers", "Providers"),
                                    ("terminal", "Terminal"),
                                    ("files", "File Browser"),
                                    ("snapshots", "Snapshots"),
                                    ("monitoring", "Monitoring"),
                                    ("settings", "Settings"),
                                    "Dashboard"
                                ),
                                size="6"
                            ),
                            rx.spacer(),
                            rx.hstack(
                                rx.button(
                                    rx.icon("refresh-cw", size=16),
                                    "Refresh",
                                    on_click=DashboardState.refresh_providers,
                                    variant="outline",
                                    size="2"
                                ),
                                rx.button(
                                    rx.icon("settings", size=16),
                                    "Settings",
                                    on_click=DashboardState.open_settings,
                                    variant="outline",
                                    size="2"
                                ),
                                spacing="2"
                            ),
                            justify="between",
                            width="100%",
                            align="center"
                        ),
                        style={
                            "padding": "1.5rem 2rem",
                            "border_bottom": "1px solid var(--gray-6)",
                            "background": "var(--gray-1)"
                        }
                    ),
                    
                    # Page content
                    rx.box(
                        page_content(),
                        style={
                            "flex": "1",
                            "overflow_y": "auto",
                            "height": "calc(100vh - 80px - 32px)"  # Subtract header and status bar
                        }
                    ),
                    
                    spacing="0",
                    width="100%",
                    height="100vh"
                ),
                style={
                    "flex": "1",
                    "background": "var(--gray-1)"
                }
            ),
            
            spacing="0",
            width="100%",
            height="100vh"
        ),
        
        # Overlays
        notification_toast(),
        loading_overlay(),
        settings_dialog(),
        status_bar(),
        
        style={
            "font_family": "Inter, system-ui, sans-serif",
            "background": "var(--gray-1)",
            "color": "var(--gray-12)"
        }
    )

def index() -> rx.Component:
    """Main index page."""
    return main_layout()

# Custom CSS for animations and additional styling
custom_css = """
@keyframes slideInRight {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes fadeIn {
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
}

.fade-in {
    animation: fadeIn 0.3s ease-in;
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: var(--gray-3);
}

::-webkit-scrollbar-thumb {
    background: var(--gray-8);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--gray-9);
}

/* Terminal-like font for code blocks */
.terminal-font {
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

/* Responsive design helpers */
@media (max-width: 768px) {
    .desktop-only {
        display: none !important;
    }
}

@media (min-width: 769px) {
    .mobile-only {
        display: none !important;
    }
}
"""

# JavaScript for client-side interactions
custom_js = """
// Global functions for client-side interactions
window.selectProvider = function(provider) {
    // This would be handled by Reflex state management
    console.log('Selecting provider:', provider);
};

window.updateProviderSetting = function(provider, key, value) {
    // This would be handled by Reflex state management
    console.log('Updating provider setting:', provider, key, value);
};

window.restoreSnapshot = function(snapshotId) {
    // This would be handled by Reflex state management
    console.log('Restoring snapshot:', snapshotId);
};

window.deleteSnapshot = function(snapshotId) {
    if (confirm('Are you sure you want to delete this snapshot?')) {
        console.log('Deleting snapshot:', snapshotId);
    }
};

window.downloadFile = function(filePath) {
    // This would be handled by Reflex state management
    console.log('Downloading file:', filePath);
};

window.deleteFile = function(filePath) {
    if (confirm('Are you sure you want to delete this file?')) {
        console.log('Deleting file:', filePath);
    }
};

window.createDirectory = function() {
    const name = prompt('Enter directory name:');
    if (name) {
        console.log('Creating directory:', name);
    }
};

// Auto-hide notifications after 5 seconds
setTimeout(function() {
    const notifications = document.querySelectorAll('[data-notification]');
    notifications.forEach(function(notification) {
        notification.style.opacity = '0';
        setTimeout(function() {
            notification.remove();
        }, 300);
    });
}, 5000);

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K to focus command input
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const commandInput = document.querySelector('input[placeholder*="command"]');
        if (commandInput) {
            commandInput.focus();
        }
    }
    
    // Escape to clear messages
    if (e.key === 'Escape') {
        // This would trigger DashboardState.clear_messages
        console.log('Clearing messages');
    }
});
"""

# Create the Reflex app
app = rx.App(
    state=DashboardState,
    style={
        "font_family": "Inter, system-ui, sans-serif",
        "background_color": "var(--gray-1)",
    },
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ],
    head_components=[
        rx.script(custom_js),
        rx.el.style(custom_css),
    ]
)

# Add the main page
app.add_page(index, route="/", title="Grainchain Dashboard")

# Add additional routes for direct page access
app.add_page(
    lambda: main_layout(),
    route="/providers",
    title="Providers - Grainchain Dashboard",
    on_load=lambda: DashboardState.set_page("providers")
)

app.add_page(
    lambda: main_layout(),
    route="/terminal", 
    title="Terminal - Grainchain Dashboard",
    on_load=lambda: DashboardState.set_page("terminal")
)

app.add_page(
    lambda: main_layout(),
    route="/files",
    title="Files - Grainchain Dashboard", 
    on_load=lambda: DashboardState.set_page("files")
)

app.add_page(
    lambda: main_layout(),
    route="/snapshots",
    title="Snapshots - Grainchain Dashboard",
    on_load=lambda: DashboardState.set_page("snapshots")
)

if __name__ == "__main__":
    app.run(
        host=config.host,
        port=config.port,
        debug=config.debug
    )
