#!/usr/bin/env python3
"""
Optional script to fix PNG color profile warnings.
This removes the problematic iCCP chunk from PNG files.
"""

import os
import sys
from pathlib import Path

def fix_png_profile(png_path):
    """Remove iCCP chunk from PNG file to fix color profile warnings."""
    try:
        # Try using PIL/Pillow if available
        from PIL import Image
        
        # Open and re-save the image without the color profile
        with Image.open(png_path) as img:
            # Convert to RGB if necessary and save without profile
            if img.mode in ('RGBA', 'LA', 'P'):
                # Keep transparency for RGBA images
                img.save(png_path, 'PNG', optimize=True)
            else:
                # Convert to RGB and save
                rgb_img = img.convert('RGB')
                rgb_img.save(png_path, 'PNG', optimize=True)
        
        print(f"✓ Fixed color profile for: {png_path}")
        return True
        
    except ImportError:
        print("PIL/Pillow not available. Install with: pip install Pillow")
        return False
    except Exception as e:
        print(f"Error fixing {png_path}: {e}")
        return False

def main():
    """Fix PNG color profiles in the resources directory."""
    resources_dir = Path(__file__).parent / 'resources'
    
    if not resources_dir.exists():
        print("Resources directory not found.")
        return
    
    png_files = list(resources_dir.glob('*.png'))
    
    if not png_files:
        print("No PNG files found in resources directory.")
        return
    
    print(f"Found {len(png_files)} PNG file(s) to process...")
    
    fixed_count = 0
    for png_file in png_files:
        if fix_png_profile(png_file):
            fixed_count += 1
    
    print(f"\nProcessed {len(png_files)} files, fixed {fixed_count} files.")
    print("PNG color profile warnings should now be reduced.")

if __name__ == "__main__":
    main()
