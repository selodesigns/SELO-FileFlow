"""
Create a simple icon file for SELO FileFlow.
"""
from PIL import Image
import os

def create_icon():
    # Create a blue gradient icon
    width, height = 256, 256
    
    # Create a new image with a blue gradient
    image = Image.new('RGBA', (width, height))
    
    # Generate a blue gradient
    for y in range(height):
        for x in range(width):
            # Create a blue gradient from top to bottom
            r = int(73 * (1 - y/height))  # Darker at the bottom
            g = int(109 + (146-109) * (1 - y/height))
            b = int(137 + (220-137) * (1 - y/height))
            image.putpixel((x, y), (r, g, b, 255))
    
    # Draw 'SF' text (simplified)
    for y in range(75, 200):
        for x in range(75, 105):
            # Draw vertical line for 'S'
            image.putpixel((x, y), (255, 255, 255, 255))
        for x in range(150, 180):
            # Draw vertical line for 'F'
            image.putpixel((x, y), (255, 255, 255, 255))
            
    # Draw horizontal lines for 'S'
    for x in range(75, 180):
        for y in range(75, 95):
            image.putpixel((x, y), (255, 255, 255, 255))
        for y in range(130, 150):
            image.putpixel((x, y), (255, 255, 255, 255))
        for y in range(180, 200):
            image.putpixel((x, y), (255, 255, 255, 255))
    
    # Draw horizontal line for 'F'
    for x in range(150, 200):
        for y in range(75, 95):
            image.putpixel((x, y), (255, 255, 255, 255))
        for y in range(130, 150):
            image.putpixel((x, y), (255, 255, 255, 255))
    
    # Save as PNG first
    png_path = os.path.join('resources', 'icon.png')
    image.save(png_path)
    print(f"PNG icon saved to {png_path}")
    
    # Save as ICO with multiple sizes
    ico_path = os.path.join('resources', 'icon.ico')
    # Create multi-resolution icon
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    resized_images = [image.resize(size) for size in sizes]
    
    # The first image will be used as the base for the .ico file
    resized_images[0].save(ico_path, format='ICO', sizes=[(img.width, img.height) for img in resized_images])
    print(f"ICO icon saved to {ico_path}")

if __name__ == "__main__":
    create_icon()
