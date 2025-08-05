
import reflex as rx

config = rx.Config(
    app_name="simple_app",
    frontend_port=3001,
    backend_port=8001,
    db_url="sqlite:///temp.db",
)
