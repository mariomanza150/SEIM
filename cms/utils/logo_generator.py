"""
Partner Institution Logo Generator

Creates placeholder logos for partner institutions using PIL/Pillow.
"""

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os


def create_placeholder_logo(institution_name, output_path=None, return_buffer=False):
    """
    Create a simple text-based logo for an institution.
    
    Args:
        institution_name: Name of the institution
        output_path: Path to save the logo (optional)
        return_buffer: If True, return BytesIO buffer instead of saving
        
    Returns:
        BytesIO buffer if return_buffer=True, otherwise None
    """
    # Image size
    width, height = 400, 200
    
    # UAdeC color scheme
    bg_color = (255, 255, 255)  # White background
    primary_color = (0, 51, 102)  # UAdeC blue
    accent_color = (204, 204, 204)  # Light gray
    
    # Create image
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw border
    border_width = 3
    draw.rectangle(
        [(border_width, border_width), (width - border_width, height - border_width)],
        outline=primary_color,
        width=border_width
    )
    
    # Draw decorative line
    draw.line([(20, height // 2), (width - 20, height // 2)], fill=accent_color, width=2)
    
    # Try to load font, fallback to default if not available
    try:
        # Try to use a nice font
        font_large = ImageFont.truetype("arial.ttf", 24)
        font_small = ImageFont.truetype("arial.ttf", 14)
    except:
        # Fallback to default font
        try:
            font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
    
    # Wrap text if too long
    max_width = width - 40
    if len(institution_name) > 30:
        # Split into two lines
        words = institution_name.split()
        mid = len(words) // 2
        line1 = ' '.join(words[:mid])
        line2 = ' '.join(words[mid:])
        
        # Calculate text positions
        bbox1 = draw.textbbox((0, 0), line1, font=font_large)
        bbox2 = draw.textbbox((0, 0), line2, font=font_large)
        text_width1 = bbox1[2] - bbox1[0]
        text_width2 = bbox2[2] - bbox2[0]
        
        x1 = (width - text_width1) // 2
        x2 = (width - text_width2) // 2
        y1 = height // 2 - 30
        y2 = height // 2 + 10
        
        draw.text((x1, y1), line1, fill=primary_color, font=font_large)
        draw.text((x2, y2), line2, fill=primary_color, font=font_large)
    else:
        # Single line
        bbox = draw.textbbox((0, 0), institution_name, font=font_large)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), institution_name, fill=primary_color, font=font_large)
    
    # Add "Partner Institution" label at bottom
    label = "Partner Institution"
    bbox = draw.textbbox((0, 0), label, font=font_small)
    label_width = bbox[2] - bbox[0]
    label_x = (width - label_width) // 2
    label_y = height - 30
    draw.text((label_x, label_y), label, fill=accent_color, font=font_small)
    
    if return_buffer:
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return buffer
    elif output_path:
        img.save(output_path, 'PNG')
        return None
    else:
        # Return the image object
        return img


# Predefined partner institutions
PARTNER_INSTITUTIONS = {
    'universidad-salamanca': {
        'name': 'Universidad de Salamanca',
        'country': 'España',
        'city': 'Salamanca',
        'agreement_type': 'bilateral',
    },
    'texas-am': {
        'name': 'Texas A&M University',
        'country': 'Estados Unidos',
        'city': 'College Station',
        'agreement_type': 'bilateral',
    },
    'bologna': {
        'name': 'Università di Bologna',
        'country': 'Italia',
        'city': 'Bologna',
        'agreement_type': 'bilateral',
    },
    'unam': {
        'name': 'UNAM',
        'country': 'México',
        'city': 'Ciudad de México',
        'agreement_type': 'bilateral',
    },
    'guadalajara': {
        'name': 'Universidad de Guadalajara',
        'country': 'México',
        'city': 'Guadalajara',
        'agreement_type': 'bilateral',
    },
    'tec-monterrey': {
        'name': 'Tecnológico de Monterrey',
        'country': 'México',
        'city': 'Monterrey',
        'agreement_type': 'bilateral',
    },
    'ut-system': {
        'name': 'University of Texas System',
        'country': 'Estados Unidos',
        'city': 'Austin',
        'agreement_type': 'bilateral',
    },
    'mcgill': {
        'name': 'McGill University',
        'country': 'Canadá',
        'city': 'Montreal',
        'agreement_type': 'bilateral',
    },
    'sorbonne': {
        'name': 'Sorbonne Université',
        'country': 'Francia',
        'city': 'París',
        'agreement_type': 'bilateral',
    },
    'fu-berlin': {
        'name': 'Freie Universität Berlin',
        'country': 'Alemania',
        'city': 'Berlín',
        'agreement_type': 'erasmus',
    },
}

