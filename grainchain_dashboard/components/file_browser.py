"""File browser and management components."""

import reflex as rx
from typing import Dict, Any

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

def file_row(file_info: Dict[str, Any]) -> rx.Component:
    """Create a row for a file in the browser."""
    from ..state import DashboardState
    
    return rx.table.row(
        rx.table.cell(
            rx.hstack(
                file_icon(file_info),
                rx.text(
                    file_info["name"],
                    size="2",
                    weight="medium" if file_info.get("is_directory", False) else "normal"
                ),
                spacing="2",
                align="center"
            )
        ),
        rx.table.cell(
            rx.text(
                format_file_size(file_info.get("size", 0)),
                size="2",
                color="gray"
            )
        ),
        rx.table.cell(
            rx.text(
                file_info.get("modified_time", ""),
                size="2",
                color="gray"
            )
        ),
        rx.table.cell(
            rx.text(
                file_info.get("permissions", ""),
                size="2",
                color="gray",
                style={"font_family": "monospace"}
            )
        ),
        rx.table.cell(
            rx.menu.root(
                rx.menu.trigger(
                    rx.button(
                        rx.icon("more-horizontal", size=16),
                        variant="ghost",
                        size="1"
                    )
                ),
                rx.menu.content(
                    rx.cond(
                        file_info.get("is_directory", False),
                        rx.menu.item(
                            rx.icon("folder-open", size=16),
                            "Open",
                            on_click=lambda path=file_info["path"]: DashboardState.navigate_to_directory(path)
                        ),
                        rx.menu.item(
                            rx.icon("download", size=16),
                            "Download",
                            on_click=lambda path=file_info["path"]: rx.call_script(f"window.downloadFile('{path}')")
                        )
                    ),
                    rx.menu.separator(),
                    rx.menu.item(
                        rx.icon("trash-2", size=16),
                        "Delete",
                        color="red",
                        on_click=lambda path=file_info["path"]: rx.call_script(f"window.deleteFile('{path}')")
                    )
                )
            )
        ),
        style={
            "cursor": "pointer" if file_info.get("is_directory", False) else "default"
        },
        on_click=rx.cond(
            file_info.get("is_directory", False),
            lambda path=file_info["path"]: DashboardState.navigate_to_directory(path)
        )
    )

def breadcrumb_navigation() -> rx.Component:
    """Create breadcrumb navigation for current directory."""
    from ..state import DashboardState
    
    return rx.hstack(
        rx.button(
            rx.icon("home", size=16),
            on_click=lambda: DashboardState.navigate_to_directory("/"),
            variant="ghost",
            size="2"
        ),
        rx.text("/", color="gray"),
        # TODO: Split current_directory and create clickable breadcrumbs
        rx.text(
            DashboardState.current_directory,
            size="2",
            style={"font_family": "monospace"}
        ),
        spacing="1",
        align="center"
    )

def file_upload_form() -> rx.Component:
    """Form for uploading files."""
    from ..state import DashboardState
    
    return rx.card(
        rx.vstack(
            rx.heading("Upload File", size="4"),
            rx.form(
                rx.vstack(
                    rx.form_field(
                        rx.form_label("Filename"),
                        rx.input(
                            placeholder="Enter filename...",
                            value=DashboardState.upload_filename,
                            on_change=DashboardState.set_upload_filename
                        ),
                        name="filename"
                    ),
                    rx.form_field(
                        rx.form_label("Content"),
                        rx.text_area(
                            placeholder="Enter file content...",
                            value=DashboardState.upload_content,
                            on_change=DashboardState.set_upload_content,
                            rows=8
                        ),
                        name="content"
                    ),
                    rx.button(
                        rx.icon("upload", size=16),
                        "Upload File",
                        type="submit",
                        disabled=~DashboardState.selected_sandbox_id
                    ),
                    spacing="4",
                    width="100%"
                ),
                on_submit=DashboardState.upload_file,
                width="100%"
            ),
            spacing="4",
            width="100%"
        ),
        variant="surface"
    )

def file_browser_table() -> rx.Component:
    """Main file browser table."""
    from ..state import DashboardState
    
    return rx.card(
        rx.vstack(
            rx.hstack(
                breadcrumb_navigation(),
                rx.button(
                    rx.icon("refresh-cw", size=16),
                    "Refresh",
                    on_click=DashboardState.refresh_files,
                    variant="outline",
                    size="2"
                ),
                justify="between",
                width="100%"
            ),
            rx.divider(),
            rx.cond(
                DashboardState.file_list,
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Name"),
                            rx.table.column_header_cell("Size"),
                            rx.table.column_header_cell("Modified"),
                            rx.table.column_header_cell("Permissions"),
                            rx.table.column_header_cell("Actions")
                        )
                    ),
                    rx.table.body(
                        rx.foreach(
                            DashboardState.file_list,
                            file_row
                        )
                    ),
                    variant="surface",
                    width="100%"
                ),
                rx.text(
                    "No files in current directory",
                    size="2",
                    color="gray",
                    style={"text_align": "center", "padding": "2rem"}
                )
            ),
            spacing="3",
            width="100%"
        ),
        variant="surface"
    )

def file_browser() -> rx.Component:
    """Main file browser component."""
    from ..state import DashboardState
    
    return rx.vstack(
        rx.cond(
            DashboardState.selected_sandbox_id,
            rx.vstack(
                file_browser_table(),
                file_upload_form(),
                spacing="6",
                width="100%"
            ),
            rx.card(
                rx.vstack(
                    rx.icon("folder", size=48, color="gray"),
                    rx.heading("No Sandbox Selected", size="4"),
                    rx.text(
                        "Select a sandbox to browse its files",
                        size="2",
                        color="gray"
                    ),
                    spacing="3",
                    align="center"
                ),
                variant="surface",
                style={"text_align": "center", "padding": "3rem"}
            )
        ),
        spacing="4",
        width="100%"
    )

def file_quick_actions() -> rx.Component:
    """Quick actions for file management."""
    from ..state import DashboardState
    
    return rx.card(
        rx.vstack(
            rx.text("Quick Actions", weight="bold", size="2"),
            rx.vstack(
                rx.button(
                    rx.icon("upload", size=16),
                    "Upload File",
                    on_click=lambda: rx.call_script("document.querySelector('input[name=\"filename\"]').focus()"),
                    width="100%",
                    variant="soft",
                    disabled=~DashboardState.selected_sandbox_id
                ),
                rx.button(
                    rx.icon("folder-plus", size=16),
                    "Create Directory",
                    on_click=lambda: rx.call_script("window.createDirectory()"),
                    width="100%",
                    variant="outline",
                    size="2",
                    disabled=~DashboardState.selected_sandbox_id
                ),
                rx.button(
                    rx.icon("refresh-cw", size=16),
                    "Refresh Files",
                    on_click=DashboardState.refresh_files,
                    width="100%",
                    variant="outline",
                    size="2"
                ),
                spacing="2",
                width="100%"
            ),
            spacing="3",
            width="100%"
        ),
        variant="surface"
    )

def directory_tree() -> rx.Component:
    """Directory tree navigation (simplified version)."""
    from ..state import DashboardState
    
    common_dirs = [
        ("/", "Root"),
        ("/home", "Home"),
        ("/tmp", "Temporary"),
        ("/var", "Variable"),
        ("/etc", "Configuration"),
        ("/usr", "User Programs")
    ]
    
    return rx.card(
        rx.vstack(
            rx.text("Quick Navigation", weight="bold", size="2"),
            rx.divider(),
            rx.vstack(
                *[
                    rx.button(
                        rx.hstack(
                            rx.icon("folder", size=14),
                            rx.text(name, size="2"),
                            spacing="2"
                        ),
                        on_click=lambda p=path: DashboardState.navigate_to_directory(p),
                        variant="ghost",
                        size="2",
                        style={"justify_content": "flex_start", "width": "100%"}
                    )
                    for path, name in common_dirs
                ],
                spacing="1",
                width="100%"
            ),
            spacing="3",
            width="100%"
        ),
        variant="surface"
    )

