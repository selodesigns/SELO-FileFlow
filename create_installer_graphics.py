"""
Create placeholder graphics files for the SELO FileFlow installer.
"""

from pathlib import Path
import os

def create_empty_bitmap(filename, width, height):
    """Create an empty BMP file with the specified dimensions."""
    # BMP file header (14 bytes)
    file_header = bytearray([
        0x42, 0x4D,             # Signature 'BM'
        0x3E, 0x00, 0x00, 0x00, # File size in bytes (62 bytes for a minimal 1x1 BMP)
        0x00, 0x00,             # Reserved
        0x00, 0x00,             # Reserved
        0x36, 0x00, 0x00, 0x00  # Offset to pixel data (54 bytes)
    ])
    
    # DIB header (40 bytes)
    dib_header = bytearray([
        0x28, 0x00, 0x00, 0x00, # DIB header size (40 bytes)
        width & 0xFF, (width >> 8) & 0xFF, 0x00, 0x00,  # Width in pixels
        height & 0xFF, (height >> 8) & 0xFF, 0x00, 0x00, # Height in pixels
        0x01, 0x00,             # Number of color planes (1)
        0x18, 0x00,             # Bits per pixel (24 - RGB)
        0x00, 0x00, 0x00, 0x00, # Compression method (none)
        0x00, 0x00, 0x00, 0x00, # Image size (can be 0 for uncompressed)
        0xC4, 0x0E, 0x00, 0x00, # Horizontal resolution (3780 pixels per meter)
        0xC4, 0x0E, 0x00, 0x00, # Vertical resolution (3780 pixels per meter)
        0x00, 0x00, 0x00, 0x00, # Number of colors in palette (none)
        0x00, 0x00, 0x00, 0x00  # Number of important colors (all)
    ])
    
    # Pixel data (blue, green, red)
    # Create a simple color (light blue) for all pixels
    pixel_data = bytearray()
    
    # Ensure each row has a multiple of 4 bytes (BMP row padding)
    row_size = (width * 3)  # 3 bytes per pixel (RGB)
    padding_size = (4 - (row_size % 4)) % 4
    
    for y in range(height):
        for x in range(width):
            # Create a gradient from blue to white
            blue_value = min(255, 180 + int(75 * x / width))
            green_value = min(255, 180 + int(75 * y / height))
            red_value = min(200, 150 + int(50 * (x + y) / (width + height)))
            
            pixel_data.extend([blue_value, green_value, red_value])
        
        # Add padding to ensure each row is a multiple of 4 bytes
        pixel_data.extend([0] * padding_size)
    
    # Calculate the actual file size
    file_size = 14 + 40 + len(pixel_data)
    file_header[2] = file_size & 0xFF
    file_header[3] = (file_size >> 8) & 0xFF
    file_header[4] = (file_size >> 16) & 0xFF
    file_header[5] = (file_size >> 24) & 0xFF
    
    # Write the BMP file
    with open(filename, 'wb') as f:
        f.write(file_header)
        f.write(dib_header)
        f.write(pixel_data)

def main():
    # Create resources directory if it doesn't exist
    resources_dir = Path("resources")
    resources_dir.mkdir(exist_ok=True)
    
    # Create placeholder BMP files for the installer
    print("Creating placeholder installer graphics...")
    
    # Side image (shown on welcome/finish pages) - typical size is 164x314 pixels
    create_empty_bitmap(os.path.join(resources_dir, "installer-side.bmp"), 164, 314)
    
    # Header image - typical size is 150x57 pixels
    create_empty_bitmap(os.path.join(resources_dir, "installer-header.bmp"), 150, 57)
    
    print("Placeholder graphics created successfully.")

if __name__ == "__main__":
    main()
