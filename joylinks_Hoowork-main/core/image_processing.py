import os
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile

def convert_to_webp(image_field):
    """
    Converts a Django image field to WebP format.
    """
    if not image_field:
        return
    
    # Get image file name
    filename = os.path.splitext(image_field.name)[0]
    
    # Open image with PIL
    img = Image.open(image_field)
    
    # Convert to RGB if it's RGBA (WebP supports alpha, but sometimes we want consistency)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    
    # Save to BytesIO buffer
    output_buffer = BytesIO()
    img.save(output_buffer, format='WEBP', quality=85)
    output_buffer.seek(0)
    
    # Create a new Django File object
    webp_filename = f"{filename}.webp"
    
    return InMemoryUploadedFile(
        output_buffer, 
        'ImageField', 
        webp_filename, 
        'image/webp', 
        output_buffer.getbuffer().nbytes, 
        None
    )
