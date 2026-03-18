import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5 import uic

from core.processor import procesar_imagenes


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi("main.ui", self)

        self.carpeta = None

        # Eventos
        self.btnSeleccionar.clicked.connect(self.seleccionar_carpeta)
        self.btnProcesar.clicked.connect(self.procesar)

    def seleccionar_carpeta(self):
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta")

        if carpeta:
            self.carpeta = carpeta
            self.lblRuta.setText(carpeta)
            self.txtLog.append(f"📂 Carpeta seleccionada:\n{carpeta}")

    def procesar(self):
        if not self.carpeta:
            self.txtLog.append("⚠️ Seleccioná una carpeta primero")
            return

        carpeta_salida = os.path.join(self.carpeta, "output")

        self.txtLog.append("🚀 Iniciando procesamiento...\n")
        self.progressBar.setValue(0)

        def log(msg):
            self.txtLog.append(msg)
            QApplication.processEvents()

        def progress(val):
            self.progressBar.setValue(val)
            QApplication.processEvents()

        procesar_imagenes(
            self.carpeta,
            carpeta_salida,
            log_callback=log,
            progress_callback=progress
        )

        self.txtLog.append("\n🎉 Proceso finalizado")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())