#!/usr/bin/env python3
"""
FileFlow Web Server Launcher

Starts the FastAPI web server for FileFlow, enabling web-based
control and configuration.

Usage:
    python scripts/run_web_server.py [--host HOST] [--port PORT] [--reload]
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main():
    parser = argparse.ArgumentParser(description="FileFlow Web Server")
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        help='Host to bind to (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=9001,
        help='Port to bind to (default: 9001)'
    )
    parser.add_argument(
        '--reload',
        action='store_true',
        help='Enable auto-reload on code changes (development)'
    )
    parser.add_argument(
        '--public',
        action='store_true',
        help='Bind to all interfaces (0.0.0.0) - use with caution'
    )
    
    args = parser.parse_args()
    
    # Override host if --public flag is set
    host = '0.0.0.0' if args.public else args.host
    
    print(f"Starting FileFlow Web Server...")
    print(f"  Host: {host}")
    print(f"  Port: {args.port}")
    print(f"  Reload: {args.reload}")
    print(f"\nAPI Documentation: http://{host if host != '0.0.0.0' else 'localhost'}:{args.port}/docs")
    print(f"Health Check: http://{host if host != '0.0.0.0' else 'localhost'}:{args.port}/health")
    print("\nPress CTRL+C to stop\n")
    
    try:
        import uvicorn
        from fileflow.web.api import app
        
        uvicorn.run(
            app,
            host=host,
            port=args.port,
            reload=args.reload,
            log_level="info"
        )
    
    except KeyboardInterrupt:
        print("\nShutting down FileFlow Web Server...")
        sys.exit(0)
    
    except ImportError as e:
        print(f"Error: Missing dependencies. Please install FastAPI and Uvicorn:")
        print(f"  pip install fastapi uvicorn")
        print(f"\nDetails: {e}")
        sys.exit(1)
    
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
