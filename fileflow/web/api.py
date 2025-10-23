"""
FileFlow REST API

FastAPI-based web server providing endpoints for file organization,
configuration management, and watcher control.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
from typing import Dict, List, Optional
import logging

from .models import (
    ConfigResponse,
    ConfigUpdate,
    OrganizeRequest,
    OrganizeResponse,
    ReorganizeRequest,
    OrganizePathRequest,
    WatcherStatusResponse,
    HealthResponse
)
from .watcher_manager import WatcherManager
from ..config import load_config, save_config
from ..organizer import organize_files, reorganize_existing_files, organize_path

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="FileFlow API",
    description="REST API for FileFlow file organization system",
    version="1.0.0"
)

# Configure CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default + common React ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global watcher manager instance
watcher_manager = WatcherManager()


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="1.0.0")


@app.get("/api/config", response_model=ConfigResponse)
async def get_config():
    """Get current FileFlow configuration."""
    try:
        config = load_config()
        return ConfigResponse(config=config)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load configuration: {str(e)}")


@app.put("/api/config")
async def update_config(config_update: ConfigUpdate):
    """Update FileFlow configuration."""
    try:
        current_config = load_config()
        
        # Update provided fields
        if config_update.source_directories is not None:
            current_config['source_directories'] = config_update.source_directories
        
        if config_update.destination_directories is not None:
            current_config['destination_directories'] = config_update.destination_directories
        
        if config_update.file_types is not None:
            current_config['file_types'] = config_update.file_types
        
        if config_update.custom_mappings is not None:
            current_config['custom_mappings'] = config_update.custom_mappings
        
        if config_update.content_classification is not None:
            current_config['content_classification'] = config_update.content_classification
        
        if config_update.notify_on_move is not None:
            current_config['notify_on_move'] = config_update.notify_on_move
        
        if config_update.autostart is not None:
            current_config['autostart'] = config_update.autostart
        
        # Save updated config
        save_config(current_config)
        
        return {"status": "success", "message": "Configuration updated successfully"}
    
    except Exception as e:
        logger.error(f"Failed to update config: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update configuration: {str(e)}")


@app.post("/api/organize", response_model=OrganizeResponse)
async def organize(request: OrganizeRequest, background_tasks: BackgroundTasks):
    """
    Organize files from source directories.
    
    Can optionally override sources and destination via request body.
    """
    try:
        # Run organization in background to avoid blocking
        def run_organize():
            try:
                organize_files(sources=request.sources, dest=request.dest)
                logger.info("Organization completed successfully")
            except Exception as e:
                logger.error(f"Organization failed: {e}")
        
        background_tasks.add_task(run_organize)
        
        return OrganizeResponse(
            status="started",
            message="File organization started in background"
        )
    
    except Exception as e:
        logger.error(f"Failed to start organization: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start organization: {str(e)}")


@app.post("/api/reorganize", response_model=OrganizeResponse)
async def reorganize(request: ReorganizeRequest, background_tasks: BackgroundTasks):
    """
    Reorganize existing files with enhanced content classification.
    
    Applies NSFW/SFW classification to already organized files.
    """
    try:
        def run_reorganize():
            try:
                reorganize_existing_files(target_dirs=request.target_dirs)
                logger.info("Reorganization completed successfully")
            except Exception as e:
                logger.error(f"Reorganization failed: {e}")
        
        background_tasks.add_task(run_reorganize)
        
        return OrganizeResponse(
            status="started",
            message="File reorganization started in background"
        )
    
    except Exception as e:
        logger.error(f"Failed to start reorganization: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start reorganization: {str(e)}")


@app.post("/api/organize/path")
async def organize_single_path(request: OrganizePathRequest):
    """
    Organize a single file path.
    
    Immediately processes the specified file and returns the result.
    """
    try:
        file_path = Path(request.path)
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {request.path}")
        
        if not file_path.is_file():
            raise HTTPException(status_code=400, detail=f"Path is not a file: {request.path}")
        
        result = organize_path(file_path, dest=request.dest)
        
        return {
            "status": "success",
            "message": f"File organized successfully",
            "result": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to organize path: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to organize file: {str(e)}")


@app.post("/api/watch/start")
async def start_watcher():
    """Start the file watcher daemon."""
    try:
        if watcher_manager.is_running():
            return {"status": "already_running", "message": "Watcher is already running"}
        
        watcher_manager.start()
        return {"status": "started", "message": "File watcher started successfully"}
    
    except Exception as e:
        logger.error(f"Failed to start watcher: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start watcher: {str(e)}")


@app.post("/api/watch/stop")
async def stop_watcher():
    """Stop the file watcher daemon."""
    try:
        if not watcher_manager.is_running():
            return {"status": "not_running", "message": "Watcher is not running"}
        
        watcher_manager.stop()
        return {"status": "stopped", "message": "File watcher stopped successfully"}
    
    except Exception as e:
        logger.error(f"Failed to stop watcher: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop watcher: {str(e)}")


@app.get("/api/watch/status", response_model=WatcherStatusResponse)
async def get_watcher_status():
    """Get current watcher status."""
    return WatcherStatusResponse(
        running=watcher_manager.is_running(),
        uptime_seconds=watcher_manager.get_uptime()
    )


@app.get("/api/stats")
async def get_stats():
    """Get organization statistics (placeholder for future implementation)."""
    return {
        "total_organized": 0,
        "sfw_count": 0,
        "nsfw_count": 0,
        "last_run": None
    }


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
