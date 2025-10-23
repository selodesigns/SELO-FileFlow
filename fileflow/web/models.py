"""
Pydantic models for FileFlow API request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str


class ConfigResponse(BaseModel):
    """Configuration response."""
    config: Dict[str, Any]


class ConfigUpdate(BaseModel):
    """Configuration update request."""
    source_directories: Optional[List[str]] = None
    destination_directories: Optional[Dict[str, str]] = None
    file_types: Optional[Dict[str, List[str]]] = None
    custom_mappings: Optional[List[Dict[str, str]]] = None
    content_classification: Optional[Dict[str, Any]] = None
    notify_on_move: Optional[bool] = None
    autostart: Optional[bool] = None


class OrganizeRequest(BaseModel):
    """File organization request."""
    sources: Optional[List[str]] = Field(None, description="Override source directories")
    dest: Optional[str] = Field(None, description="Override destination directory")


class ReorganizeRequest(BaseModel):
    """File reorganization request."""
    target_dirs: Optional[List[str]] = Field(None, description="Specific directories to reorganize")


class OrganizePathRequest(BaseModel):
    """Single path organization request."""
    path: str = Field(..., description="File path to organize")
    dest: Optional[str] = Field(None, description="Override destination directory")


class OrganizeResponse(BaseModel):
    """Organization operation response."""
    status: str
    message: str


class WatcherStatusResponse(BaseModel):
    """Watcher status response."""
    running: bool
    uptime_seconds: Optional[float] = None
