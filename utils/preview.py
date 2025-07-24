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

from PIL import Image
from PyQt5.QtGui import QPixmap
from pdf2image import convert_from_path
import os
import io

def generate_preview(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    try:
        if ext in [".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"]:
            img = Image.open(file_path)
        elif ext == ".pdf":
            images = convert_from_path(file_path, first_page=1, last_page=1, dpi=100)
            img = images[0] if images else None
        else:
            return None

        if img is None:
            return None

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return QPixmap.fromImage(Image.open(buf).toqimage())
    except Exception as e:
        print(f"Preview generation failed for {file_path}: {e}")
        return None
