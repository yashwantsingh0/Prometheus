# ──────────────────────────────────────────────────────────────
#  Prometheus File Compressor
#  Version: 0.2.0
#  License: MIT (see LICENSE file for details)
#
#  Author: Yashwant Singh
#  GitHub: https://github.com/yashwantsingh0/Prometheus
#
#  Description:
#      Compress JPG, PNG, and PDF files with full user control.
#      Features drag & drop, save-as, image quality tuning, DPI reduction.
#
#  ⚠️ This file is part of the Prometheus Project.
#     Do not remove or modify attribution headers in redistributed versions.
# ──────────────────────────────────────────────────────────────
# gui/interface.py

import os
import traceback
from PIL import Image

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QMenuBar, QAction, QMessageBox, QStyleFactory, QScrollArea,
    QGridLayout, QHBoxLayout, QSpinBox, QComboBox, QGroupBox, QFormLayout,
    QDialog, QListWidget, QListWidgetItem, QProgressBar, QLineEdit
)
from PyQt5.QtGui import QIcon, QPalette, QColor, QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QThreadPool

from compression.image_compressor import compress_image
from compression.pdf_compressor import compress_pdf
from compression.ghostscript_compressor import compress_pdf_ghostscript
from compression.pikepdf_optimizer import optimize_pdf_pikepdf
from gui.preview_panel import PreviewPanel  # For future expansion
from utils.compression_worker import CompressionWorker  # Reserved for async compression
from utils.image_compression_task import simulate_image_compression  # Placeholder logic

SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".pdf")


# ─────────────────────────────
# ConvertWorker for format dialog
# ─────────────────────────────
class ConvertWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, source_path, target_ext, output_path):
        super().__init__()
        self.source_path = source_path
        self.target_ext = target_ext
        self.output_path = output_path

    def run(self):
        try:
            img = Image.open(self.source_path)
            if self.target_ext == ".ico":
                if img.size[0] < 256 or img.size[1] < 256:
                    img = img.resize((256, 256))
                img.save(self.output_path, format="ICO", sizes=[(256, 256)])
            else:
                img.save(self.output_path)
            self.progress.emit(100)
            self.finished.emit(self.output_path)
        except Exception as e:
            self.finished.emit(f"Error: {str(e)}")


# ─────────────────────────────
# Format Converter Dialog (Tools > Convert)
# ─────────────────────────────
class ImageFormatConverterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Convert Image Format")
        self.setMinimumSize(600, 400)
        self.setStyleSheet("background-color: #2e2e2e; color: #e0e0e0;")
        self.threads = []

        layout = QVBoxLayout(self)

        self.image_list = QListWidget()
        self.image_list.setAcceptDrops(True)
        self.image_list.setDragDropMode(QListWidget.DropOnly)
        self.image_list.viewport().setAcceptDrops(True)
        self.image_list.setSpacing(5)
        self.image_list.setStyleSheet("background-color: #3a3a3a; border: 1px solid #444;")

        self.select_button = QPushButton("Add Images")
        self.select_button.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        self.select_button.clicked.connect(self.select_files)

        self.output_format = QComboBox()
        self.output_format.addItems([".jpg", ".png", ".jpeg", ".bmp", ".ico", ".webp"])
        self.output_format.setStyleSheet("background-color: #3a3a3a; color: #e0e0e0; border: 1px solid #444; padding: 5px;")

        self.convert_btn = QPushButton("Convert All")
        self.convert_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        self.convert_btn.clicked.connect(self.start_conversion)

        layout.addWidget(self.select_button)
        layout.addWidget(QLabel("Target Format:"))
        layout.addWidget(self.output_format)
        layout.addWidget(self.image_list)
        layout.addWidget(self.convert_btn, alignment=Qt.AlignCenter)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Images", "", "Images (*.jpg *.jpeg *.png *.bmp *.ico *.webp *.tiff)"
        )
        for f in files:
            self.add_image_item(f)

    def add_image_item(self, path):
        item = QListWidgetItem(os.path.basename(path))
        item.setData(Qt.UserRole, path)
        progress = QProgressBar()
        progress.setStyleSheet("background-color: #2e2e2e; border: 1px solid #444; color: #e0e0e0;")
        progress.setValue(0)
        self.image_list.addItem(item)
        self.image_list.setItemWidget(item, progress)

    def start_conversion(self):
        target_ext = self.output_format.currentText()
        for i in range(self.image_list.count()):
            item = self.image_list.item(i)
            source_path = item.data(Qt.UserRole)
            base, _ = os.path.splitext(source_path)
            output_path = base + target_ext
            bar = self.image_list.itemWidget(item)

            thread = ConvertWorker(source_path, target_ext, output_path)
            thread.progress.connect(bar.setValue)
            thread.finished.connect(lambda msg, b=bar: b.setFormat(msg))
            thread.start()
            self.threads.append(thread)


# ─────────────────────────────
# Main Application Window
# ─────────────────────────────
class PrometheusApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prometheus - File Compressor")
        self.setMinimumSize(900, 700)
        self.setAcceptDrops(True)

        self.theme = "dark"
        self.preview_files = []
        self.preview_widgets = {}
        self.progress_bars = {}
        self.threadpool = QThreadPool()

        self.init_ui()

    def init_ui(self):
        self.create_menu()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout(central_widget)
        self.layout.setAlignment(Qt.AlignTop)

        self.drop_label = QLabel("\n\n⬇️  Drag & Drop files here  ⬇️\n\n")
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #4a90e2;
                padding: 50px;
                font-size: 28px;
                color: #4a90e2;
                background-color: #2e2e2e;
                border-radius: 10px;
            }
        """)

        btn_style = """
            QPushButton {
                background-color: #4a90e2;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:pressed {
                background-color: #2e6da4;
            }
        """

        self.button = QPushButton("📁 Choose Files...")
        self.button.setStyleSheet(btn_style)
        self.button.clicked.connect(self.open_file_dialog)

        self.compress_button = QPushButton("🔧 Compress All")
        self.compress_button.setStyleSheet(btn_style)
        self.compress_button.clicked.connect(self.compress_all_files)

        # Compression Options
        self.options_group = QGroupBox("Compression Settings")
        self.options_group.setStyleSheet("background-color: #3a3a3a; border: 1px solid #444; padding: 10px; color: #e0e0e0;")
        options_layout = QFormLayout()

        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(10, 100)
        self.quality_spin.setValue(85)
        self.quality_spin.setStyleSheet("background-color: #2e2e2e; color: #e0e0e0; border: 1px solid #444; padding: 5px;")

        self.resize_spin = QSpinBox()
        self.resize_spin.setRange(10, 100)
        self.resize_spin.setValue(100)
        self.resize_spin.setStyleSheet("background-color: #2e2e2e; color: #e0e0e0; border: 1px solid #444; padding: 5px;")

        self.dpi_spin = QSpinBox()
        self.dpi_spin.setRange(50, 300)
        self.dpi_spin.setValue(120)
        self.dpi_spin.setStyleSheet("background-color: #2e2e2e; color: #e0e0e0; border: 1px solid #444; padding: 5px;")

        self.pdf_engine = QComboBox()
        self.pdf_engine.addItems(["PyMuPDF", "Ghostscript", "pikepdf"])
        self.pdf_engine.setStyleSheet("background-color: #2e2e2e; color: #e0e0e0; border: 1px solid #444; padding: 5px;")

        options_layout.addRow("Image Quality (%)", self.quality_spin)
        options_layout.addRow("Resize Percent (IMGs/PDFs)", self.resize_spin)
        options_layout.addRow("DPI (for PDF only)", self.dpi_spin)
        options_layout.addRow("PDF Engine", self.pdf_engine)

        self.options_group.setLayout(options_layout)

        # Scroll area for preview thumbnails
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background-color: #2e2e2e; border: 1px solid #444;")
        self.preview_container = QWidget()
        self.preview_layout = QGridLayout(self.preview_container)
        self.scroll_area.setWidget(self.preview_container)

        self.layout.addWidget(self.drop_label)
        self.layout.addWidget(self.button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.options_group)
        self.layout.addWidget(self.compress_button, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.scroll_area)

        self.apply_theme()

    def create_menu(self):
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)

        menubar.setStyleSheet("""
            QMenuBar {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2e2e2e,
                    stop:1 #3a3a3a
                );
                color: #e0e0e0;
                font-size: 14px;
            }
            QMenuBar::item {
                background: transparent;
                padding: 8px 15px;
                margin: 0px 2px;
            }
            QMenuBar::item:selected {
                background: #4a90e2;
                color: white;
            }
            QMenu {
                background-color: #2e2e2e;
                color: #e0e0e0;
                font-size: 14px;
            }
            QMenu::item:selected {
                background-color: #4a90e2;
                color: white;
            }
        """)

        file_menu = menubar.addMenu("File")
        file_menu.addAction(QAction("Open Files", self, triggered=self.open_file_dialog))
        file_menu.addSeparator()
        file_menu.addAction(QAction("Exit", self, triggered=self.close))

        theme_menu = menubar.addMenu("Theme")
        theme_menu.addAction(QAction("Dark/Light", self, triggered=self.toggle_theme))

        tools_menu = menubar.addMenu("Tools")
        tools_menu.addAction(QAction("Convert Image Format", self, triggered=self.open_converter_dialog))

        help_menu = menubar.addMenu("Help")
        help_menu.addAction(QAction("About", self, triggered=self.show_about))


    def open_converter_dialog(self):
        dialog = ImageFormatConverterDialog(self)
        dialog.exec()

    # Add, Remove, Drag, Preview logic
    def open_file_dialog(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select files", "", "Images and PDFs (*.jpg *.jpeg *.png *.pdf)")
        if files:
            self.handle_files(files)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self.handle_files(files)

    def handle_files(self, files):
        valid_files = [f for f in files if f.lower().endswith(SUPPORTED_FORMATS)]
        if not valid_files:
            QMessageBox.warning(self, "Unsupported", "No supported files selected.")
            return

        for file_path in valid_files:
            if file_path not in self.preview_files:
                self.preview_files.append(file_path)
                self.add_preview(file_path)

        self.refresh_preview_grid()

    def add_preview(self, file_path):
        base_name = os.path.basename(file_path)
        container = QWidget()
        layout = QVBoxLayout(container)

        if file_path.lower().endswith((".jpg", ".jpeg", ".png")):
            pixmap = QPixmap(file_path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            pixmap = QPixmap(100, 100)
            pixmap.fill(Qt.gray)

        thumb = QLabel()
        thumb.setPixmap(pixmap)
        thumb.setAlignment(Qt.AlignCenter)
        thumb.setStyleSheet("border: 1px solid #444; border-radius: 5px;")

        name = QLabel(base_name)
        name.setAlignment(Qt.AlignCenter)
        name.setWordWrap(True)
        name.setStyleSheet("color: #e0e0e0;")

        remove_btn = QPushButton("🗑️")
        remove_btn.setFixedSize(28, 28)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        remove_btn.clicked.connect(lambda: self.remove_preview(file_path))

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(remove_btn)

        layout.addLayout(btn_layout)
        layout.addWidget(thumb)
        layout.addWidget(name)

        container.setLayout(layout)
        self.preview_widgets[file_path] = container

    def refresh_preview_grid(self):
        for i in reversed(range(self.preview_layout.count())):
            widget = self.preview_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        for i, file_path in enumerate(self.preview_files):
            widget = self.preview_widgets[file_path]
            self.preview_layout.addWidget(widget, i // 4, i % 4)

    def remove_preview(self, file_path):
        if file_path in self.preview_files:
            self.preview_files.remove(file_path)
        widget = self.preview_widgets.pop(file_path, None)
        if widget:
            widget.setParent(None)
        self.refresh_preview_grid()

    def compress_all_files(self):
        if not self.preview_files:
            QMessageBox.information(self, "No files", "Please add files to compress.")
            return

        quality = self.quality_spin.value()
        resize = self.resize_spin.value()
        dpi = self.dpi_spin.value()
        engine = self.pdf_engine.currentText()

        for path in self.preview_files:
            base = os.path.splitext(os.path.basename(path))[0]
            ext = os.path.splitext(path)[1]
            suggested = base + "_compressed" + ext

            save_path, _ = QFileDialog.getSaveFileName(self, "Save Compressed File As", suggested, f"*{ext}")
            if not save_path:
                continue

            try:
                if path.lower().endswith((".jpg", ".jpeg", ".png")):
                    compressed = compress_image(path, output_path=save_path, quality=quality, resize_percent=resize)
                elif path.lower().endswith(".pdf"):
                    if engine == "PyMuPDF":
                        compressed = compress_pdf(path, output_path=save_path, dpi=dpi)
                    elif engine == "Ghostscript":
                        compressed = compress_pdf_ghostscript(path, output_path=save_path)
                    elif engine == "pikepdf":
                        compressed = optimize_pdf_pikepdf(path, output_path=save_path)

                if compressed:
                    print(f"Compressed and saved: {compressed}")
                else:
                    raise Exception("Compression returned None")

            except Exception as e:
                print(f"Compression failed: {e}")
                traceback.print_exc()
                QMessageBox.critical(self, "Compression Error", f"Failed to compress file:\n{path}\n\n{str(e)}")

        QMessageBox.information(self, "Done", "Compression completed.")

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        self.apply_theme()

    def apply_theme(self):
        if self.theme == "dark":
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(46, 46, 46))
            palette.setColor(QPalette.WindowText, Qt.white)
            palette.setColor(QPalette.Base, QColor(58, 58, 58))
            palette.setColor(QPalette.Text, Qt.white)
            palette.setColor(QPalette.Button, QColor(74, 144, 226))
            palette.setColor(QPalette.ButtonText, Qt.white)
            palette.setColor(QPalette.Highlight, QColor(74, 144, 226))
            palette.setColor(QPalette.HighlightedText, Qt.black)
            self.setPalette(palette)
            self.setStyle(QStyleFactory.create("Fusion"))
        else:
            self.setPalette(QApplication.style().standardPalette())
            self.setStyle(QStyleFactory.create("Fusion"))

    def show_about(self):
        text = (
            "<b>Prometheus File Compressor</b><br>"
            "User-driven file size optimization for Linux desktops.<br>"
            "Built with Python 3.13, PyQt5, and the following technologies:<br><br>"
            "<ul>"
            "<li><b>Image Compression:</b> Pillow (resize, quality)</li>"
            "<li><b>PDF Compression:</b> PyMuPDF, Ghostscript, pikepdf</li>"
            "<li><b>GUI Framework:</b> PyQt5 (cross-platform native look)</li>"
            "<li><b>File I/O:</b> Drag & drop, batch handling</li>"
            "<li><b>Theming:</b> Dark/Light switch with Fusion palette</li>"
            "</ul><br><br>"
            "<center>Crafted with ❤️ by <a href='https://yashwantsingh0.github.io'>Yashwant Singh</a></center>"
        )
        msg = QMessageBox(self)
        msg.setWindowTitle("About Prometheus")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()