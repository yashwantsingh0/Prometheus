import pikepdf
import os

def optimize_pdf(input_path, output_path=None, remove_metadata=True):
    """
    Optimize a PDF by compressing object streams and optionally removing metadata.

    Parameters:
        input_path (str): Path to the input PDF file
        output_path (str): Optional; path to save the optimized PDF
        remove_metadata (bool): If True, removes PDF metadata

    Returns:
        str: Path to the optimized PDF, or None on failure
    """
    try:
        if not output_path:
            filename = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(
                os.path.dirname(input_path),
                f"{filename}_optimized.pdf"
            )

        with pikepdf.open(input_path) as pdf:
            # Remove metadata if enabled
            if remove_metadata:
                keys = list(pdf.docinfo.keys())
                for key in keys:
                    del pdf.docinfo[key]

            # Save with stream/object optimization
            pdf.save(
                output_path,
                object_stream_mode=pikepdf.ObjectStreamMode.generate
            )

        print(f"Optimized: {input_path} -> {output_path}")
        return output_path

    except Exception as e:
        print(f"Failed to optimize {input_path}: {e}")
        return None


# compression/pikepdf_optimizer.py

import pikepdf
import os

def optimize_pdf_pikepdf(input_path, output_path):
    """
    Optimize a PDF using pikepdf by removing duplicates and unused objects.
    """
    try:
        with pikepdf.open(input_path) as pdf:
            pdf.save(output_path, optimize_version=True, linearize=True)
        return output_path if os.path.exists(output_path) else None
    except Exception as e:
        print(f"[pikepdf] Optimization failed: {e}")
        return None
