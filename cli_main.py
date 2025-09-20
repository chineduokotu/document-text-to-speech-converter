#!/usr/bin/env python3
"""
Text-to-Speech Automation Tool - Main Entry Point

This script provides the main entry point for the TTS automation tool,
allowing users to choose between CLI and GUI interfaces.
"""

import sys
import argparse
from pathlib import Path

# Add src directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent / "src"))

from cli import main as cli_main
from gui import main as gui_main


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description='Text-to-Speech Automation Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Interface Options:
  --gui, -g                 Launch the graphical user interface
  --cli, -c                 Use the command-line interface (default)

Examples:
  python main.py --gui                          # Launch GUI
  python main.py --cli --file document.pdf     # Use CLI to read PDF
  python main.py --text "Hello world"          # Use CLI with text
        '''
    )
    
    # Interface selection
    interface_group = parser.add_mutually_exclusive_group()
    interface_group.add_argument(
        '--gui', '-g',
        action='store_true',
        help='Launch the graphical user interface'
    )
    interface_group.add_argument(
        '--cli', '-c',
        action='store_true',
        help='Use the command-line interface'
    )
    
    # Parse known args to separate interface choice from CLI args
    args, remaining_args = parser.parse_known_args()
    
    if args.gui:
        # Launch GUI
        print("Launching Text-to-Speech GUI...")
        try:
            gui_main()
        except KeyboardInterrupt:
            print("\nGUI application closed.")
            return 0
    else:
        # Use CLI (default)
        if not args.cli and not remaining_args:
            # No interface specified and no args - show help
            parser.print_help()
            print("\nTip: Use --gui to launch the graphical interface, or provide CLI arguments.")
            return 1
        
        # Pass remaining arguments to CLI
        try:
            return cli_main(remaining_args)
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return 1


if __name__ == "__main__":
    sys.exit(main())