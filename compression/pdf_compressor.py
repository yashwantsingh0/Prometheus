# compression/pdf_compressor.py

import fitz  # PyMuPDF
import os

def compress_pdf(input_path, output_path=None, remove_metadata=True, dpi=120):
    try:
        if not output_path:
            base, _ = os.path.splitext(input_path)
            output_path = f"{base}_compressed.pdf"

        doc = fitz.open(input_path)

        # Remove metadata
        if remove_metadata:
            doc.set_metadata({})

        # Iterate pages and redraw with lower resolution
        for i in range(len(doc)):
            page = doc.load_page(i)
            pix = page.get_pixmap(dpi=dpi)
            img_pdf = fitz.open()  # temporary PDF
            img_pdf.new_page(width=pix.width, height=pix.height)
            img_page = img_pdf[-1]
            img_page.insert_image(img_page.rect, pixmap=pix)
            doc[i] = img_pdf[-1]  # replace original page with image version

        doc.save(output_path, garbage=4, deflate=True, clean=True)
        return output_path
    except Exception as e:
        print(f"PDF compression failed: {e}")
        return None
