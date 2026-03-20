import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5 import uic
from datetime import datetime

from core.processor import procesar_imagenes

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Carga de la grafica
        uic.loadUi("main.ui", self)

        self.carpeta = None

        # Eventos
        self.btnSeleccionar.clicked.connect(self.seleccionar_carpeta)
        self.btnProcesar.clicked.connect(self.procesar)

    def seleccionar_carpeta(self):
        '''Obtiene la ruta de la carpeta que contiene las imagenes a procesar'''
        carpeta = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta")
        # Si existe la carpeta, muestra su ubicacion
        if carpeta: 
            self.carpeta = carpeta
            self.lblRuta.setText(carpeta)
            self.txtLog.append(f"\n 📂 Carpeta seleccionada:\n{carpeta}")

    def procesar(self):
        '''Realiza el cambio de parametros informando tanto en log como en la progress bar'''
        # Si no hay carpeta definida, da aviso
        if not self.carpeta:
            self.txtLog.append("⚠️ Seleccioná una carpeta primero")
            return
        # Crea una carpeta donde se colocaran las imagenes procesadas
        carpeta_salida = os.path.join(self.carpeta, "output")

        def log(msg):
            '''log de eventos con timestamp'''
            ahora = datetime.now().strftime("%H:%M:%S")
            self.txtLog.append(f"[{ahora}] {msg}")
            self.txtLog.ensureCursorVisible()
            QApplication.processEvents()

        def progress(val):
            '''progreso de la barra de progreso'''
            self.progressBar.setValue(val)
            QApplication.processEvents()

        log("🚀 Iniciando procesamiento...")
        self.progressBar.setValue(0)

        procesar_imagenes(
            self.carpeta,
            carpeta_salida,
            log_callback=log,
            progress_callback=progress
        )

        log("🎉 Proceso finalizado")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())