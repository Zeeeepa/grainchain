#!/usr/bin/env python3
"""File Manager State and Backend Logic."""

import os
import shutil
import mimetypes
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import reflex as rx
import asyncio
import logging

logger = logging.getLogger(__name__)

class FileManagerState(rx.State):
    """File manager state with comprehensive file operations."""
    
    # Current state
    files: List[Dict[str, Any]] = []
    filtered_files: List[Dict[str, Any]] = []
    current_path: str = "/"
    path_parts: List[str] = ["/"]
    
    # UI state
    search_query: str = ""
    filter_type: str = "all"
    view_mode: str = "list"  # "list" or "grid"
    loading: bool = False
    
    # Preview state
    show_preview: bool = False
    preview_type: str = "text"
    preview_content: str = ""
    preview_url: str = ""
    
    # Selection state
    selected_files: List[str] = []
    
    # Upload state
    show_upload_dialog: bool = False
    upload_progress: Dict[str, float] = {}
    
    def __init__(self):
        super().__init__()
        self.base_path = Path.cwd() / "workspace"
        self.base_path.mkdir(exist_ok=True)
        self.refresh_files()
    
    def get_full_path(self, relative_path: str = None) -> Path:
        """Get full filesystem path from relative path."""
        if relative_path is None:
            relative_path = self.current_path
        
        # Ensure path is within workspace
        full_path = self.base_path / relative_path.lstrip("/")
        try:
            full_path = full_path.resolve()
            if not str(full_path).startswith(str(self.base_path.resolve())):
                return self.base_path
        except Exception:
            return self.base_path
        
        return full_path
    
    def refresh_files(self):
        """Refresh file list for current directory."""
        self.loading = True
        try:
            current_dir = self.get_full_path()
            files = []
            
            if not current_dir.exists():
                current_dir.mkdir(parents=True, exist_ok=True)
            
            # Add parent directory link if not at root
            if self.current_path != "/":
                files.append({
                    "name": "..",
                    "path": str(Path(self.current_path).parent),
                    "type": "folder",
                    "size": 0,
                    "modified": "",
                    "is_parent": True
                })
            
            # List directory contents
            for item in current_dir.iterdir():
                try:
                    stat = item.stat()
                    relative_path = str(item.relative_to(self.base_path))
                    
                    file_info = {
                        "name": item.name,
                        "path": "/" + relative_path.replace("\\", "/"),
                        "type": "folder" if item.is_dir() else "file",
                        "size": stat.st_size if item.is_file() else 0,
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                        "is_parent": False
                    }
                    
                    # Add MIME type for files
                    if item.is_file():
                        mime_type, _ = mimetypes.guess_type(str(item))
                        file_info["mime_type"] = mime_type or "application/octet-stream"
                    
                    files.append(file_info)
                    
                except (OSError, PermissionError) as e:
                    logger.warning(f"Cannot access {item}: {e}")
                    continue
            
            # Sort: folders first, then files, alphabetically
            files.sort(key=lambda x: (x["type"] != "folder", x["name"].lower()))
            
            self.files = files
            self.filter_files()
            self.update_path_parts()
            
        except Exception as e:
            logger.error(f"Error refreshing files: {e}")
            self.files = []
            self.filtered_files = []
        finally:
            self.loading = False
    
    def filter_files(self):
        """Filter files based on search query and type filter."""
        filtered = self.files.copy()
        
        # Apply search filter
        if self.search_query:
            query = self.search_query.lower()
            filtered = [f for f in filtered if query in f["name"].lower()]
        
        # Apply type filter
        if self.filter_type != "all":
            if self.filter_type == "image":
                filtered = [f for f in filtered if f["type"] == "folder" or 
                           (f.get("mime_type", "").startswith("image/"))]
            elif self.filter_type == "document":
                doc_types = ["application/pdf", "text/", "application/msword", 
                            "application/vnd.openxmlformats-officedocument"]
                filtered = [f for f in filtered if f["type"] == "folder" or 
                           any(f.get("mime_type", "").startswith(t) for t in doc_types)]
            elif self.filter_type == "code":
                code_extensions = [".py", ".js", ".html", ".css", ".json", ".xml", ".yaml", ".yml"]
                filtered = [f for f in filtered if f["type"] == "folder" or 
                           any(f["name"].endswith(ext) for ext in code_extensions)]
            elif self.filter_type == "archive":
                archive_types = ["application/zip", "application/x-tar", "application/gzip"]
                filtered = [f for f in filtered if f["type"] == "folder" or 
                           any(f.get("mime_type", "").startswith(t) for t in archive_types)]
        
        self.filtered_files = filtered
    
    def update_path_parts(self):
        """Update breadcrumb path parts."""
        if self.current_path == "/":
            self.path_parts = ["/"]
        else:
            parts = [""] + self.current_path.strip("/").split("/")
            self.path_parts = ["/"] + parts[1:]
    
    def navigate_to(self, path: str):
        """Navigate to a specific path."""
        if path == "..":
            path = str(Path(self.current_path).parent)
        
        # Normalize path
        if not path.startswith("/"):
            path = "/" + path
        
        self.current_path = path
        self.refresh_files()
    
    def navigate_to_index(self, index: int):
        """Navigate to path at breadcrumb index."""
        if index == 0:
            self.navigate_to("/")
        else:
            path_parts = self.current_path.strip("/").split("/")
            new_path = "/" + "/".join(path_parts[:index])
            self.navigate_to(new_path)
    
    def select_file(self, path: str):
        """Select/deselect a file."""
        if path in self.selected_files:
            self.selected_files.remove(path)
        else:
            self.selected_files.append(path)
    
    def preview_file(self, path: str):
        """Preview a file."""
        try:
            full_path = self.get_full_path(path)
            
            if not full_path.exists() or full_path.is_dir():
                return
            
            # Determine preview type
            mime_type, _ = mimetypes.guess_type(str(full_path))
            
            if mime_type and mime_type.startswith("image/"):
                self.preview_type = "image"
                self.preview_url = f"/api/files/preview/{path.lstrip('/')}"
                self.preview_content = ""
            elif mime_type and (mime_type.startswith("text/") or 
                               full_path.suffix in [".py", ".js", ".html", ".css", ".json", ".yaml", ".yml"]):
                self.preview_type = "text"
                self.preview_url = ""
                
                # Read text content (limit to 10KB for performance)
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read(10240)  # 10KB limit
                        if len(content) == 10240:
                            content += "\n... (file truncated)"
                        self.preview_content = content
                except UnicodeDecodeError:
                    self.preview_content = "Binary file - cannot preview as text"
            else:
                self.preview_type = "unsupported"
                self.preview_url = ""
                self.preview_content = ""
            
            self.show_preview = True
            
        except Exception as e:
            logger.error(f"Error previewing file {path}: {e}")
    
    def download_file(self, path: str):
        """Initiate file download."""
        # This would typically trigger a download via the API
        logger.info(f"Download requested for: {path}")
        return rx.download(url=f"/api/files/download/{path.lstrip('/')}")
    
    def delete_file(self, path: str):
        """Delete a file or folder."""
        try:
            full_path = self.get_full_path(path)
            
            if full_path.is_dir():
                shutil.rmtree(full_path)
            else:
                full_path.unlink()
            
            self.refresh_files()
            logger.info(f"Deleted: {path}")
            
        except Exception as e:
            logger.error(f"Error deleting {path}: {e}")
    
    def create_folder(self):
        """Create a new folder."""
        try:
            base_name = "New Folder"
            counter = 1
            
            while True:
                folder_name = f"{base_name} {counter}" if counter > 1 else base_name
                folder_path = self.get_full_path() / folder_name
                
                if not folder_path.exists():
                    folder_path.mkdir()
                    self.refresh_files()
                    logger.info(f"Created folder: {folder_name}")
                    break
                
                counter += 1
                if counter > 100:  # Prevent infinite loop
                    break
                    
        except Exception as e:
            logger.error(f"Error creating folder: {e}")
    
    def start_rename(self, path: str):
        """Start renaming a file/folder."""
        # This would typically open a rename dialog
        logger.info(f"Rename requested for: {path}")
    
    def set_search_query(self, query: str):
        """Set search query and filter files."""
        self.search_query = query
        self.filter_files()
    
    def set_filter_type(self, filter_type: str):
        """Set file type filter."""
        self.filter_type = filter_type
        self.filter_files()
    
    def set_view_mode(self, mode: str):
        """Set view mode (list or grid)."""
        self.view_mode = mode
    
    def show_upload_dialog(self):
        """Show upload dialog."""
        self.show_upload_dialog = True
    
    async def upload_files(self, files: List[Any]):
        """Upload multiple files."""
        try:
            current_dir = self.get_full_path()
            
            for file in files:
                file_path = current_dir / file.filename
                
                # Avoid overwriting existing files
                counter = 1
                original_path = file_path
                while file_path.exists():
                    stem = original_path.stem
                    suffix = original_path.suffix
                    file_path = current_dir / f"{stem}_{counter}{suffix}"
                    counter += 1
                
                # Save file
                with open(file_path, 'wb') as f:
                    content = await file.read()
                    f.write(content)
                
                logger.info(f"Uploaded: {file.filename} -> {file_path.name}")
            
            self.refresh_files()
            
        except Exception as e:
            logger.error(f"Error uploading files: {e}")
    
    def get_file_stats(self) -> Dict[str, Any]:
        """Get file statistics for current directory."""
        try:
            total_files = len([f for f in self.files if f["type"] == "file"])
            total_folders = len([f for f in self.files if f["type"] == "folder"])
            total_size = sum(f["size"] for f in self.files if f["type"] == "file")
            
            return {
                "total_files": total_files,
                "total_folders": total_folders,
                "total_size": total_size,
                "total_size_formatted": self.format_file_size(total_size)
            }
        except Exception:
            return {
                "total_files": 0,
                "total_folders": 0,
                "total_size": 0,
                "total_size_formatted": "0 B"
            }
    
    @staticmethod
    def format_file_size(size: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
