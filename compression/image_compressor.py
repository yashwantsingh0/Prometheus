# ──────────────────────────────────────────────────────────────
#  Prometheus File Compressor
#  Version: 0.1.0
#  License: MIT (see LICENSE file for details)
#
#  Author: Yashwant Singh
#  GitHub: https://github.com/yashwantsingh0/Prometheus
#
#  Description:
#      Compress JPG, PNG, and PDF files with full user control.
#      Features drag & drop, save-as, image quality tuning, and PDF DPI reduction.
#
#  ⚠️ This file is part of the Prometheus Project.
#     Do not remove or modify attribution headers in redistributed versions.
# ──────────────────────────────────────────────────────────────
# compression/image_compressor.py

from PIL import Image
import os

def compress_image(
    input_path,
    output_path=None,
    quality=85,
    resize_percent=None,
    dpi=None,
    background_color="white"
):
    try:
        img = Image.open(input_path)
        img_format = img.format or "JPEG"

        # Resize image
        if resize_percent and 0 < resize_percent < 100:
            new_size = (
                int(img.width * resize_percent / 100),
                int(img.height * resize_percent / 100)
            )
            img = img.resize(new_size, Image.ANTIALIAS)

        # Handle transparency
        if img.mode in ("RGBA", "LA"):
            background = Image.new("RGB", img.size, background_color)
            background.paste(img, mask=img.split()[3])  # Alpha channel
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

        # Output path
        if not output_path:
            base, ext = os.path.splitext(input_path)
            output_path = f"{base}_compressed{ext}"

        # Save image
        save_kwargs = {"quality": quality, "optimize": True}
        if dpi:
            save_kwargs["dpi"] = (dpi, dpi)
        img.save(output_path, format=img_format, **save_kwargs)

        return output_path
    except Exception as e:
        print(f"Image compression failed: {e}")
        return None



from PIL import Image
import os

def compress_webp(input_path, output_path=None, quality=80, lossless=False):
    """
    Compress a WebP image.
    
    Parameters:
        input_path (str): Path to the input .webp image
        output_path (str): Optional; path to save the compressed image
        quality (int): Quality level (0-100)
        lossless (bool): Use lossless compression if True
        
    Returns:
        output_path (str): Path to the saved compressed image
    """
    try:
        with Image.open(input_path) as img:
            # Ensure RGB or RGBA
            img = img.convert("RGBA") if img.mode in ("RGBA", "P") else img.convert("RGB")
            
            if not output_path:
                filename = os.path.splitext(os.path.basename(input_path))[0]
                output_path = os.path.join(os.path.dirname(input_path), f"{filename}_compressed.webp")
            
            img.save(output_path, format="WEBP", quality=quality, lossless=lossless)
            print(f"Compressed: {input_path} -> {output_path} ({quality}%)")
            return output_path
    except Exception as e:
        print(f"Error compressing {input_path}: {e}")
        return None
