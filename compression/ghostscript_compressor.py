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

# ghostscript_compressor.py

import subprocess
import os

def compress_pdf_with_ghostscript(input_path, output_path=None, quality='screen'):
    """
    Compress a PDF using Ghostscript.
    
    Parameters:
        input_path (str): Path to input PDF
        output_path (str): Optional output file (default adds '_compressed')
        quality (str): One of ['screen', 'ebook', 'printer', 'prepress', 'default']
        
    Returns:
        output_path (str): Compressed PDF path or None if failed
    """
    if not output_path:
        filename = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(os.path.dirname(input_path), f"{filename}_compressed.pdf")
    
    # Ghostscript command
    gs_cmd = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS=/{quality}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        input_path
    ]

    try:
        subprocess.run(gs_cmd, check=True)
        print(f"Compressed: {input_path} -> {output_path} ({quality})")
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"Ghostscript compression failed: {e}")
        return None




import shutil

def compress_pdf_to_target_size(input_path, output_path=None, target_kb=500):
    """
    Try multiple Ghostscript quality settings to get as close as possible to a target size.
    
    Parameters:
        input_path (str): Path to input PDF
        output_path (str): Final output path (optional)
        target_kb (int): Desired output size in kilobytes
        
    Returns:
        output_path (str): Final compressed file or None if no setting matched
    """
    quality_levels = ['screen', 'ebook', 'printer', 'prepress', 'default']
    temp_files = []

    if not output_path:
        filename = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(os.path.dirname(input_path), f"{filename}_compressed_target.pdf")

    for quality in quality_levels:
        temp_path = output_path.replace(".pdf", f"_{quality}.pdf")
        result = compress_pdf_with_ghostscript(input_path, temp_path, quality)
        if result and os.path.exists(result):
            size_kb = os.path.getsize(result) // 1024
            print(f"[{quality}] Size: {size_kb} KB")
            temp_files.append((result, size_kb))

            if size_kb <= target_kb:
                shutil.move(result, output_path)
                _cleanup_temp_files(temp_files, keep=output_path)
                return output_path

    # Fallback: pick closest if none under target
    if temp_files:
        best_file = min(temp_files, key=lambda x: abs(x[1] - target_kb))[0]
        shutil.move(best_file, output_path)
        _cleanup_temp_files(temp_files, keep=output_path)
        return output_path

    return None

def _cleanup_temp_files(files, keep=None):
    for f, _ in files:
        if f != keep and os.path.exists(f):
            os.remove(f)



import subprocess
import shutil
import os

def compress_pdf_ghostscript(input_path, output_path=None):
    """
    Compress a PDF using Ghostscript.

    Args:
        input_path (str): Path to input PDF
        output_path (str, optional): Path to save compressed PDF

    Returns:
        str: Path to the compressed PDF
    """
    if not shutil.which("gs"):
        raise RuntimeError("Ghostscript not installed or not in PATH")

    if output_path is None:
        base, _ = os.path.splitext(input_path)
        output_path = base + "_compressed_gs.pdf"

    cmd = [
        "gs",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        "-dPDFSETTINGS=/screen",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        input_path
    ]

    subprocess.run(cmd, check=True)

    if not os.path.exists(output_path):
        raise RuntimeError("Compression failed, output file not found")

    return output_path

# compression/ghostscript_compressor.py

import subprocess
import os

def compress_pdf_ghostscript(input_path, output_path, quality="screen"):
    """
    Compress PDF using Ghostscript.

    quality options:
        - screen (lowest)
        - ebook
        - printer
        - prepress
        - default
    """
    try:
        command = [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS=/{quality}",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={output_path}",
            input_path
        ]
        subprocess.run(command, check=True)
        return output_path if os.path.exists(output_path) else None
    except Exception as e:
        print(f"[Ghostscript] Compression failed: {e}")
        return None
