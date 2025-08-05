"""Test app to verify the complete implementation works."""

import reflex as rx
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from enhanced_state import EnhancedDashboardState
    from components.ui_components import status_badge
    
    def test_page() -> rx.Component:
        """Simple test page to verify components work."""
        return rx.vstack(
            rx.heading("🚀 Grainchain Dashboard Test", size="7"),
            rx.text("Testing complete implementation components", size="4", color="gray"),
            
            # Test status badges
            rx.hstack(
                status_badge("success"),
                status_badge("failed"),
                status_badge("unknown"),
                spacing="3"
            ),
            
            # Test basic state
            rx.text(f"Current page: {EnhancedDashboardState.current_page}"),
            rx.text(f"Providers count: {EnhancedDashboardState.providers_count}"),
            
            # Test navigation
            rx.hstack(
                rx.button(
                    "Dashboard",
                    on_click=lambda: EnhancedDashboardState.set_page("dashboard")
                ),
                rx.button(
                    "Providers", 
                    on_click=lambda: EnhancedDashboardState.set_page("providers")
                ),
                rx.button(
                    "Files",
                    on_click=lambda: EnhancedDashboardState.set_page("files")
                ),
                spacing="3"
            ),
            
            spacing="6",
            style={"padding": "2rem", "max_width": "800px", "margin": "0 auto"}
        )
    
    # Create test app
    app = rx.App()
    app.add_page(test_page, route="/", title="Grainchain Dashboard Test")
    
    print("✅ Test app created successfully!")
    print("✅ Enhanced state imported successfully!")
    print("✅ UI components imported successfully!")
    
except Exception as e:
    print(f"❌ Error creating test app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
