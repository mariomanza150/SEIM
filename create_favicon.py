from PIL import Image, ImageDraw, ImageFont
import os

# Create a simple 16x16 favicon with "SE" text
size = (16, 16)
img = Image.new('RGBA', size, (0, 123, 255, 255))  # Bootstrap primary blue
draw = ImageDraw.Draw(img)

# Try to use a simple font
try:
    font = ImageFont.truetype("arial.ttf", 10)
except:
    font = ImageFont.load_default()

# Draw "SE" text
draw.text((2, 2), "SE", fill=(255, 255, 255), font=font)

# Save as ICO format
output_path = r"E:\mario\Documents\SGII\SEIM\exchange\static\images\favicon.ico"
img.save(output_path, format='ICO', sizes=[size])
print(f"Favicon created at: {output_path}")
