# main.py
from gui.interface import PrometheusApp

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = PrometheusApp()
    window.show()
    sys.exit(app.exec_())