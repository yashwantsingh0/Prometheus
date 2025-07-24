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

from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QScrollArea, QGridLayout, QToolTip, QFileDialog, QDialog
)
from PyQt5.QtGui import QPixmap, QImage, QCursor
from PyQt5.QtCore import Qt, QSize, QEvent
import os
from utils.preview import generate_preview

class ImagePreviewDialog(QDialog):
    def __init__(self, image_path):
        super().__init__()
        self.setWindowTitle(os.path.basename(image_path))
        layout = QVBoxLayout()
        label = QLabel()
        pixmap = QPixmap(image_path)
        label.setPixmap(pixmap.scaledToWidth(800, Qt.SmoothTransformation))
        layout.addWidget(label)
        self.setLayout(layout)
        self.resize(pixmap.width(), pixmap.height())

class PreviewThumbnail(QWidget):
    def __init__(self, file_path, remove_callback):
        super().__init__()
        self.file_path = file_path
        self.remove_callback = remove_callback

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignHCenter)

        self.image_label = QLabel()
        self.image_label.setFixedSize(100, 100)
        self.image_label.setStyleSheet("border: 1px solid gray;")
        self.image_label.setScaledContents(True)

        preview = generate_preview(file_path, size=(100, 100))
        if preview:
            self.image_label.setPixmap(QPixmap.fromImage(preview))

        # Tooltip info
        self.image_label.setToolTip(self.get_file_info())

        # Hover zoom effect
        self.image_label.installEventFilter(self)

        # Click preview
        self.image_label.mousePressEvent = self.open_full_preview

        remove_button = QPushButton("🗑")
        remove_button.setFixedSize(24, 24)
        remove_button.clicked.connect(lambda: self.remove_callback(file_path))

        layout.addWidget(self.image_label)
        layout.addWidget(QLabel(os.path.basename(file_path)))
        layout.addWidget(remove_button)

        self.setLayout(layout)

    def get_file_info(self):
        size = os.path.getsize(self.file_path)
        return f"Size: {round(size / 1024, 2)} KB\nPath: {self.file_path}"

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Enter:
            self.image_label.setFixedSize(130, 130)
        elif event.type() == QEvent.Leave:
            self.image_label.setFixedSize(100, 100)
        return super().eventFilter(obj, event)

    def open_full_preview(self, event):
        dialog = ImagePreviewDialog(self.file_path)
        dialog.exec_()

class PreviewPanel(QWidget):
    def __init__(self, remove_callback):
        super().__init__()
        self.remove_callback = remove_callback
        self.layout = QVBoxLayout(self)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.inner_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.inner_widget.setLayout(self.grid_layout)
        self.scroll.setWidget(self.inner_widget)
        self.layout.addWidget(self.scroll)
        self.setLayout(self.layout)
        self.files = []

    def update_files(self, file_paths):
        self.files = file_paths
        self.refresh_thumbnails()

    def refresh_thumbnails(self):
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        for i, file_path in enumerate(self.files):
            thumb = PreviewThumbnail(file_path, self.remove_callback)
            row, col = divmod(i, 5)
            self.grid_layout.addWidget(thumb, row, col)
