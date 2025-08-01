import argparse
from fileflow.organizer import organize_files, reorganize_existing_files
from fileflow.watcher import start_watching

def main():
    parser = argparse.ArgumentParser(description="SELO FileFlow - Linux File Organizer with Content Classification")
    parser.add_argument('--watch', action='store_true', help='Start the file watcher daemon')
    parser.add_argument('--organize-once', action='store_true', help='Organize files once and exit')
    parser.add_argument('--reorganize', action='store_true', help='Reorganize existing files with NSFW/SFW content classification')
    parser.add_argument('--ui', action='store_true', help='Launch the graphical user interface')
    parser.add_argument('--target-dirs', nargs='*', help='Specific directories to reorganize (used with --reorganize)')
    parser.add_argument('--source', nargs='+', help='Source directory or directories to organize (overrides config)')
    parser.add_argument('--dest', help='Destination directory to organize into (overrides config, all categories will go here)')
    args = parser.parse_args()

    if args.ui:
        from .ui.app import run_app
        run_app()
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
