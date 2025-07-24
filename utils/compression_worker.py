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

# utils/compression_worker.py

from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot
import traceback

class CompressionSignals(QObject):
    progress = pyqtSignal(int, str)  # progress %, filename
    finished = pyqtSignal(str)       # filename
    error = pyqtSignal(str, str)     # filename, error

class CompressionWorker(QRunnable):
    def __init__(self, filepath, compress_fn):
        super().__init__()
        self.filepath = filepath
        self.compress_fn = compress_fn
        self.signals = CompressionSignals()

    @pyqtSlot()
    def run(self):
        try:
            for progress in self.compress_fn(self.filepath):
                self.signals.progress.emit(progress, self.filepath)
            self.signals.finished.emit(self.filepath)
        except Exception as e:
            self.signals.error.emit(self.filepath, str(e))
