# utils/image_compression_task.py

import time
import os

def simulate_image_compression(filepath):
    """
    Fake compression with progress for demonstration.
    Replace with real compression code and yield progress.
    """
    steps = 10
    for i in range(1, steps + 1):
        time.sleep(0.2)  # Simulate work
        yield int((i / steps) * 100)  # Yield progress %
    # Save file or modify here
    output_path = filepath.replace(".", "_compressed.")
    os.rename(filepath, output_path)
