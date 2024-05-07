import argparse
from pathlib import Path
from . import show_folder
import sys


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='View a folder of images as image sequence.')
    parser.add_argument(
        'folder', type=Path, help='Path to the folder containing the images.')
    parser.add_argument(
        '--title', type=str, default='Image Folder Viewer',
        help='Title of the application window.')
    args = parser.parse_args()
    
    sys.exit(show_folder(folder=args.folder, window_title=args.title))
