import argparse
from fileflow.organizer import organize_files, reorganize_existing_files
from fileflow.watcher import start_watching

def main():
    parser = argparse.ArgumentParser(description="SELO FileFlow - Linux File Organizer with Content Classification")
    parser.add_argument('--watch', action='store_true', help='Start the file watcher daemon')
    parser.add_argument('--organize-once', action='store_true', help='Organize files once and exit')
    parser.add_argument('--reorganize', action='store_true', help='Reorganize existing files with NSFW/SFW content classification')
    parser.add_argument('--ui', action='store_true', help='Launch the graphical user interface')
    parser.add_argument('--web', action='store_true', help='Launch the web server interface')
    parser.add_argument('--target-dirs', nargs='*', help='Specific directories to reorganize (used with --reorganize)')
    parser.add_argument('--source', nargs='+', help='Source directory or directories to organize (overrides config)')
    parser.add_argument('--dest', help='Destination directory to organize into (overrides config, all categories will go here)')
    parser.add_argument('--host', default='127.0.0.1', help='Web server host (used with --web)')
    parser.add_argument('--port', type=int, default=9001, help='Web server port (used with --web)')
    args = parser.parse_args()

    if args.ui:
        from .ui.app import run_app
        run_app()
    elif args.web:
        try:
            import uvicorn
            from .web.api import app
            print(f"Starting FileFlow Web Server on http://{args.host}:{args.port}")
            print(f"API Documentation: http://{args.host}:{args.port}/docs")
            uvicorn.run(app, host=args.host, port=args.port)
        except ImportError:
            print("Error: Web dependencies not installed. Run: pip install fastapi uvicorn")
            return
    elif args.watch:
        start_watching()
    elif args.organize_once:
        organize_files(sources=args.source, dest=args.dest)
    elif args.reorganize:
        reorganize_existing_files(args.target_dirs)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
