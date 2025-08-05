"""Reusable UI components for the dashboard."""

import reflex as rx
from typing import Dict, Any, Optional, List

def modal_dialog(
    is_open: bool,
    title: str,
    content: rx.Component,
    on_close,
    size: str = "md"
) -> rx.Component:
    """Reusable modal dialog component."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(title),
            rx.dialog.description(content),
            rx.dialog.close(
                rx.button("Close", on_click=on_close, variant="soft")
            ),
            size=size
        ),
        open=is_open
    )

def toast_notification(
    message: str,
    type: str = "info",
    show: bool = True
) -> rx.Component:
    """Toast notification component."""
    color_scheme = {
        "success": "green",
        "error": "red",
        "warning": "yellow",
        "info": "blue"
    }.get(type, "blue")
    
    return rx.cond(
        show,
        rx.box(
            rx.hstack(
                rx.icon(
                    "check-circle" if type == "success" else
                    "x-circle" if type == "error" else
                    "alert-triangle" if type == "warning" else
                    "info",
                    size=16,
                    color=color_scheme
                ),
                rx.text(message, size="2"),
                spacing="2"
            ),
            style={
                "position": "fixed",
                "top": "1rem",
                "right": "1rem",
                "background": f"var(--{color_scheme}-3)",
                "border": f"1px solid var(--{color_scheme}-6)",
                "border_radius": "6px",
                "padding": "0.75rem 1rem",
                "z_index": "1000",
                "box_shadow": "0 4px 12px rgba(0, 0, 0, 0.1)"
            }
        )
    )

def loading_spinner(show: bool = True, text: str = "Loading...") -> rx.Component:
    """Loading spinner component."""
    return rx.cond(
        show,
        rx.center(
            rx.vstack(
                rx.spinner(size="3"),
                rx.text(text, size="2", color="gray"),
                spacing="3"
            ),
            style={
                "position": "fixed",
                "top": "0",
                "left": "0",
                "width": "100vw",
                "height": "100vh",
                "background": "rgba(0, 0, 0, 0.5)",
                "z_index": "9999"
            }
        )
    )

def confirmation_dialog(
    is_open: bool,
    title: str,
    message: str,
    on_confirm,
    on_cancel,
    confirm_text: str = "Confirm",
    cancel_text: str = "Cancel"
) -> rx.Component:
    """Confirmation dialog component."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title(title),
            rx.dialog.description(message),
            rx.hstack(
                rx.dialog.close(
                    rx.button(cancel_text, on_click=on_cancel, variant="soft")
                ),
                rx.dialog.close(
                    rx.button(
                        confirm_text, 
                        on_click=on_confirm, 
                        color_scheme="red" if "delete" in title.lower() else "blue"
                    )
                ),
                spacing="3",
                justify="end"
            ),
            size="sm"
        ),
        open=is_open
    )

def file_icon(file_info: Dict[str, Any]) -> rx.Component:
    """Get appropriate icon for file type."""
    if file_info.get("is_directory", False):
        return rx.icon("folder", size=16, color="blue")
    
    name = file_info.get("name", "").lower()
    if name.endswith((".py", ".pyw")):
        return rx.icon("file-code", size=16, color="green")
    elif name.endswith((".js", ".ts", ".jsx", ".tsx")):
        return rx.icon("file-code", size=16, color="yellow")
    elif name.endswith((".html", ".htm", ".xml")):
        return rx.icon("file-code", size=16, color="orange")
    elif name.endswith((".css", ".scss", ".sass")):
        return rx.icon("file-code", size=16, color="purple")
    elif name.endswith((".json", ".yaml", ".yml", ".toml")):
        return rx.icon("file-text", size=16, color="blue")
    elif name.endswith((".md", ".txt", ".rst")):
        return rx.icon("file-text", size=16, color="gray")
    elif name.endswith((".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp")):
        return rx.icon("image", size=16, color="pink")
    elif name.endswith((".pdf", ".doc", ".docx")):
        return rx.icon("file-text", size=16, color="red")
    elif name.endswith((".zip", ".tar", ".gz", ".rar", ".7z")):
        return rx.icon("archive", size=16, color="brown")
    else:
        return rx.icon("file", size=16, color="gray")

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def status_badge(status: str) -> rx.Component:
    """Status badge component."""
    color_map = {
        "success": "green",
        "available": "green",
        "ready": "green",
        "connected": "green",
        "failed": "red",
        "error": "red",
        "unavailable": "red",
        "unknown": "gray",
        "pending": "yellow",
        "creating": "yellow",
        "restoring": "yellow",
        "loading": "blue"
    }
    
    color = color_map.get(status.lower(), "gray")
    
    return rx.badge(
        status.title(),
        color_scheme=color,
        variant="soft"
    )

def data_table(
    headers: List[str],
    rows: List[List[Any]],
    actions: Optional[List[rx.Component]] = None
) -> rx.Component:
    """Reusable data table component."""
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                *[rx.table.column_header_cell(header) for header in headers],
                rx.table.column_header_cell("Actions") if actions else None
            )
        ),
        rx.table.body(
            *[
                rx.table.row(
                    *[rx.table.cell(str(cell)) for cell in row],
                    rx.table.cell(
                        rx.hstack(*actions, spacing="2") if actions else None
                    ) if actions else None
                )
                for row in rows
            ]
        ),
        variant="surface",
        size="2"
    )

def search_input(
    placeholder: str,
    value: str,
    on_change,
    on_search=None
) -> rx.Component:
    """Search input component."""
    return rx.hstack(
        rx.input(
            placeholder=placeholder,
            value=value,
            on_change=on_change,
            style={"flex": "1"}
        ),
        rx.button(
            rx.icon("search", size=16),
            on_click=on_search if on_search else lambda: None,
            variant="soft"
        ),
        spacing="2",
        width="100%"
    )

def progress_bar(
    value: float,
    max_value: float = 100,
    show_percentage: bool = True
) -> rx.Component:
    """Progress bar component."""
    percentage = (value / max_value) * 100 if max_value > 0 else 0
    
    return rx.vstack(
        rx.progress(value=percentage, max=100),
        rx.text(f"{percentage:.1f}%", size="2", color="gray") if show_percentage else None,
        spacing="1",
        width="100%"
    )

def empty_state(
    icon: str,
    title: str,
    description: str,
    action_button: Optional[rx.Component] = None
) -> rx.Component:
    """Empty state component."""
    return rx.center(
        rx.vstack(
            rx.icon(icon, size=48, color="gray"),
            rx.heading(title, size="5", color="gray"),
            rx.text(description, size="3", color="gray", text_align="center"),
            action_button if action_button else None,
            spacing="4",
            align="center",
            style={"padding": "4rem"}
        ),
        width="100%",
        min_height="300px"
    )

def card_with_header(
    title: str,
    content: rx.Component,
    actions: Optional[List[rx.Component]] = None
) -> rx.Component:
    """Card with header and optional actions."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading(title, size="4"),
                rx.spacer(),
                rx.hstack(*actions, spacing="2") if actions else None,
                width="100%"
            ),
            rx.divider(),
            content,
            spacing="3",
            width="100%"
        ),
        style={"padding": "1.5rem"}
    )

def form_field(
    label: str,
    input_component: rx.Component,
    error_message: Optional[str] = None,
    required: bool = False
) -> rx.Component:
    """Form field with label and error handling."""
    return rx.vstack(
        rx.hstack(
            rx.text(label, size="2", weight="medium"),
            rx.text("*", color="red") if required else None,
            spacing="1"
        ),
        input_component,
        rx.text(error_message, size="1", color="red") if error_message else None,
        spacing="2",
        width="100%"
    )
