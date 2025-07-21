"""
Convert PNG to ICO format for FileFlow application.
"""
from PIL import Image
import os
from pathlib import Path

def convert_png_to_ico():
    """Convert PNG to ICO format with multiple sizes for Windows."""
    png_path = Path("resources/icon.png")
    ico_path = Path("resources/icon.ico")
    
    if not png_path.exists():
        print(f"Error: {png_path} not found!")
        return False
    
    try:
        # Open the PNG image
        img = Image.open(png_path)
        
        # Create a set of images with different sizes
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # The first image will be used as the base for the .ico file
        # Generate all sizes and save as ICO
        print(f"Converting {png_path} to {ico_path} with sizes: {sizes}")
        img.save(ico_path, format='ICO', sizes=[(x, y) for x, y in sizes])
        
        print(f"Successfully created {ico_path}")
        return True
    
    except Exception as e:
        print(f"Error converting PNG to ICO: {e}")
        return False

if __name__ == "__main__":
    convert_png_to_ico()
