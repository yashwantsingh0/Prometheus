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

# converters/image_converter.py

from PIL import Image, UnidentifiedImageError
import os

def convert_image(input_path, output_path, target_ext):
    """
    Converts a single image to the target format, prioritizing lossless quality.
    
    Special handling:
    - ICO output resizes to 256x256 if smaller.
    - ICO input uses largest embedded size.
    - Transparency and metadata preserved where supported.
    - No quality degradation for lossless formats.
    """
    try:
        with Image.open(input_path) as img:
            # Ensure consistent extension
            target_ext = target_ext.lower()

            # Convert ICO input: extract largest embedded image
            if input_path.lower().endswith(".ico"):
                if hasattr(img, "n_frames"):
                    max_size = 0
                    for frame in range(img.n_frames):
                        img.seek(frame)
                        if img.size[0] * img.size[1] > max_size:
                            max_size = img.size[0] * img.size[1]
                            best_img = img.copy()
                    img = best_img

            # Handle alpha (transparency)
            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                img = img.convert("RGBA")
            else:
                img = img.convert("RGB")

            # ICO output: ensure 256x256 size
            if target_ext == ".ico":
                if img.width != 256 or img.height != 256:
                    img = img.resize((256, 256), Image.LANCZOS)
                img.save(output_path, format="ICO", sizes=[(256, 256)])

            # PNG, TIFF, WebP → prioritize lossless
            elif target_ext in [".png", ".tiff", ".tif", ".webp"]:
                img.save(output_path, format=target_ext.strip("."), lossless=True)

            # JPEG → force RGB, avoid subsampling
            elif target_ext in [".jpg", ".jpeg"]:
                img = img.convert("RGB")
                img.save(output_path, format="JPEG", quality=100, subsampling=0, optimize=True)

            # Other formats (BMP, GIF, etc.)
            else:
                img.save(output_path, format=target_ext.strip("."))

            return True, output_path

    except UnidentifiedImageError:
        return False, "Unsupported or corrupted image file."
    except Exception as e:
        return False, str(e)
