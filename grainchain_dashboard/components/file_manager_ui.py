#!/usr/bin/env python3
"""File Manager UI components."""

import reflex as rx
from typing import List, Dict, Any, Optional

def file_upload_zone() -> rx.Component:
    """Drag and drop file upload zone."""
    return rx.box(
        rx.vstack(
            rx.icon("upload-cloud", size=48, color="gray"),
            rx.heading("Drop files here or click to upload", size="4", color="gray"),
            rx.text("Supports all file types up to 100MB", color="gray"),
            rx.input(
                type="file",
                multiple=True,
                style={"display": "none"},
                id="file-input"
            ),
            spacing="3",
            align="center"
        ),
        border="2px dashed var(--gray-6)",
        border_radius="8px",
        padding="2rem",
        text_align="center",
        cursor="pointer",
        _hover={"border_color": "var(--blue-6)", "background": "var(--gray-2)"},
        on_click="document.getElementById('file-input').click()",
        width="100%",
        min_height="200px",
        display="flex",
        align_items="center",
        justify_content="center"
    )

def file_item(file_info: Dict[str, Any]) -> rx.Component:
    """Individual file item component."""
    return rx.card(
        rx.hstack(
            rx.icon(
                rx.cond(
                    file_info["type"] == "folder",
                    "folder",
                    rx.cond(
                        file_info["name"].endswith((".jpg", ".png", ".gif", ".svg")),
                        "image",
                        rx.cond(
                            file_info["name"].endswith((".py", ".js", ".html", ".css")),
                            "file-code",
                            "file"
                        )
                    )
                ),
                size=20,
                color=rx.cond(file_info["type"] == "folder", "blue", "gray")
            ),
            rx.vstack(
                rx.text(file_info["name"], weight="medium"),
                rx.text(
                    f"{file_info.get('size', 0)} bytes • {file_info.get('modified', 'Unknown')}",
                    size="2",
                    color="gray"
                ),
                spacing="1",
                align="start"
            ),
            rx.spacer(),
            rx.menu.root(
                rx.menu.trigger(
                    rx.button(
                        rx.icon("more-horizontal", size=16),
                        variant="ghost",
                        size="2"
                    )
                ),
                rx.menu.content(
                    rx.menu.item(
                        rx.hstack(rx.icon("eye", size=14), rx.text("Preview"), spacing="2"),
                        on_click=lambda: FileManagerState.preview_file(file_info["path"])
                    ),
                    rx.menu.item(
                        rx.hstack(rx.icon("download", size=14), rx.text("Download"), spacing="2"),
                        on_click=lambda: FileManagerState.download_file(file_info["path"])
                    ),
                    rx.menu.item(
                        rx.hstack(rx.icon("edit", size=14), rx.text("Rename"), spacing="2"),
                        on_click=lambda: FileManagerState.start_rename(file_info["path"])
                    ),
                    rx.menu.separator(),
                    rx.menu.item(
                        rx.hstack(rx.icon("trash-2", size=14), rx.text("Delete"), spacing="2"),
                        on_click=lambda: FileManagerState.delete_file(file_info["path"]),
                        color="red"
                    )
                )
            ),
            spacing="3",
            align="center",
            width="100%"
        ),
        padding="1rem",
        cursor="pointer",
        _hover={"background": "var(--gray-2)"},
        on_click=rx.cond(
            file_info["type"] == "folder",
            lambda: FileManagerState.navigate_to(file_info["path"]),
            lambda: FileManagerState.select_file(file_info["path"])
        )
    )

def file_preview_modal() -> rx.Component:
    """File preview modal."""
    return rx.dialog.root(
        rx.dialog.trigger(rx.box()),  # Hidden trigger
        rx.dialog.content(
            rx.dialog.title("File Preview"),
            rx.box(
                rx.cond(
                    FileManagerState.preview_type == "image",
                    rx.image(
                        src=FileManagerState.preview_url,
                        max_width="100%",
                        max_height="400px"
                    ),
                    rx.cond(
                        FileManagerState.preview_type == "text",
                        rx.code_block(
                            FileManagerState.preview_content,
                            language="python",
                            max_height="400px",
                            overflow="auto"
                        ),
                        rx.text("Preview not available for this file type")
                    )
                ),
                width="100%",
                max_width="600px"
            ),
            rx.dialog.close(
                rx.button("Close", variant="soft")
            ),
            max_width="80vw",
            max_height="80vh"
        ),
        open=FileManagerState.show_preview
    )

def file_search_bar() -> rx.Component:
    """File search and filter bar."""
    return rx.hstack(
        rx.input(
            placeholder="Search files...",
            value=FileManagerState.search_query,
            on_change=FileManagerState.set_search_query,
            width="300px"
        ),
        rx.select.root(
            rx.select.trigger(
                rx.select.value(placeholder="File Type"),
                width="150px"
            ),
            rx.select.content(
                rx.select.item("All Files", value="all"),
                rx.select.item("Images", value="image"),
                rx.select.item("Documents", value="document"),
                rx.select.item("Code", value="code"),
                rx.select.item("Archives", value="archive")
            ),
            value=FileManagerState.filter_type,
            on_value_change=FileManagerState.set_filter_type
        ),
        rx.button(
            rx.icon("refresh-cw", size=16),
            on_click=FileManagerState.refresh_files,
            variant="outline"
        ),
        spacing="3",
        align="center"
    )

def breadcrumb_navigation() -> rx.Component:
    """Breadcrumb navigation for current path."""
    return rx.hstack(
        rx.foreach(
            FileManagerState.path_parts,
            lambda part, index: rx.hstack(
                rx.button(
                    part,
                    variant="ghost",
                    size="2",
                    on_click=lambda: FileManagerState.navigate_to_index(index)
                ),
                rx.cond(
                    index < len(FileManagerState.path_parts) - 1,
                    rx.icon("chevron-right", size=14, color="gray"),
                    rx.box()
                ),
                spacing="1"
            )
        ),
        spacing="1",
        align="center"
    )

def file_manager_toolbar() -> rx.Component:
    """File manager toolbar with actions."""
    return rx.hstack(
        rx.button(
            rx.hstack(rx.icon("folder-plus", size=16), rx.text("New Folder"), spacing="2"),
            on_click=FileManagerState.create_folder,
            variant="outline"
        ),
        rx.button(
            rx.hstack(rx.icon("upload", size=16), rx.text("Upload"), spacing="2"),
            on_click=FileManagerState.show_upload_dialog,
            color_scheme="blue"
        ),
        rx.spacer(),
        rx.button_group(
            rx.button(
                rx.icon("grid-3x3", size=16),
                variant=rx.cond(FileManagerState.view_mode == "grid", "solid", "outline"),
                on_click=lambda: FileManagerState.set_view_mode("grid")
            ),
            rx.button(
                rx.icon("list", size=16),
                variant=rx.cond(FileManagerState.view_mode == "list", "solid", "outline"),
                on_click=lambda: FileManagerState.set_view_mode("list")
            )
        ),
        spacing="3",
        align="center",
        width="100%"
    )

def file_manager_main() -> rx.Component:
    """Main file manager component."""
    return rx.vstack(
        file_manager_toolbar(),
        breadcrumb_navigation(),
        file_search_bar(),
        rx.divider(),
        rx.cond(
            FileManagerState.loading,
            rx.center(
                rx.spinner(size="3"),
                height="200px"
            ),
            rx.cond(
                len(FileManagerState.files) == 0,
                rx.center(
                    rx.vstack(
                        rx.icon("folder-open", size=48, color="gray"),
                        rx.text("No files found", color="gray"),
                        spacing="3"
                    ),
                    height="200px"
                ),
                rx.cond(
                    FileManagerState.view_mode == "grid",
                    rx.grid(
                        rx.foreach(
                            FileManagerState.filtered_files,
                            file_item
                        ),
                        columns="repeat(auto-fill, minmax(300px, 1fr))",
                        gap="1rem",
                        width="100%"
                    ),
                    rx.vstack(
                        rx.foreach(
                            FileManagerState.filtered_files,
                            file_item
                        ),
                        spacing="2",
                        width="100%"
                    )
                )
            )
        ),
        file_preview_modal(),
        spacing="4",
        width="100%",
        height="100%"
    )

# Mock FileManagerState for development
class MockFileManagerState:
    files = []
    filtered_files = []
    current_path = "/"
    path_parts = ["/"]
    search_query = ""
    filter_type = "all"
    view_mode = "list"
    loading = False
    show_preview = False
    preview_type = "text"
    preview_content = ""
    preview_url = ""
    
    @staticmethod
    def navigate_to(path: str):
        pass
    
    @staticmethod
    def select_file(path: str):
        pass
    
    @staticmethod
    def preview_file(path: str):
        pass
    
    @staticmethod
    def download_file(path: str):
        pass
    
    @staticmethod
    def delete_file(path: str):
        pass
    
    @staticmethod
    def start_rename(path: str):
        pass
    
    @staticmethod
    def set_search_query(query: str):
        pass
    
    @staticmethod
    def set_filter_type(filter_type: str):
        pass
    
    @staticmethod
    def set_view_mode(mode: str):
        pass
    
    @staticmethod
    def refresh_files():
        pass
    
    @staticmethod
    def create_folder():
        pass
    
    @staticmethod
    def show_upload_dialog():
        pass
    
    @staticmethod
    def navigate_to_index(index: int):
        pass

# Try to import real state, fall back to mock
try:
    from ..file_manager.file_manager_state import FileManagerState
except ImportError:
    FileManagerState = MockFileManagerState
