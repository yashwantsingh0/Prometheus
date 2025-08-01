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
# compression/pdf_compressor.py

import fitz  # PyMuPDF
import os

def compress_pdf(input_path, output_path=None, dpi=100, remove_metadata=True):
    try:
        if not output_path:
            base, _ = os.path.splitext(input_path)
            output_path = f"{base}_compressed.pdf"

        input_doc = fitz.open(input_path)
        output_doc = fitz.open()

        for page in input_doc:
            pix = page.get_pixmap(dpi=dpi)
            img_pdf = fitz.open()
            img_page = img_pdf.new_page(width=pix.width, height=pix.height)
            img_page.insert_image(img_page.rect, pixmap=pix)
            output_doc.insert_pdf(img_pdf)

        if remove_metadata:
            output_doc.set_metadata({})  # Clear metadata

        output_doc.save(output_path, garbage=4, deflate=True)
        return output_path

    except Exception as e:
        print(f"Error during PDF compression: {e}")
        return None
