import sys
import os
import resources_rc

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5.QtGui import QIcon
from PyQt5 import uic
from datetime import datetime

from core.processor import procesar_imagenes

'''
para compilar iconos: python -m PyQt5.pyrcc_main resources.qrc -o resources_rc.py
'''

class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    log = pyqtSignal(str)

    def __init__(self, carpeta_origen, carpeta_destino):
        super().__init__()
        self.carpeta_origen = carpeta_origen
        self.carpeta_destino = carpeta_destino

    def run(self):
        procesar_imagenes(
            self.carpeta_origen,
            self.carpeta_destino,
            log_callback=self.log.emit,
            progress_callback=self.progress.emit
        )
        self.finished.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Carga de la grafica
        uic.loadUi("main.ui", self)
        self.btnSeleccionar.setIcon(QIcon(":/icons/folder.png"))
        self.btnProcesar.setIcon(QIcon(":/icons/play.png"))
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
        if not self.carpeta:
            self.txtLog.append("⚠️ Seleccioná una carpeta primero")
            return

        carpeta_salida = os.path.join(self.carpeta, "output")
        self.progressBar.setValue(0)
        # Crear thread y worker
        self.thread = QThread()
        self.worker = Worker(self.carpeta, carpeta_salida)
        self.worker.moveToThread(self.thread)
        # Conexiones
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.actualizar_progreso)
        self.worker.log.connect(self.agregar_log)
        self.worker.finished.connect(self.proceso_terminado)
        # UI estado
        self.btnProcesar.setEnabled(False)
        self.agregar_log("🚀 Iniciando procesamiento...")
        self.thread.start()

    def actualizar_progreso(self, valor):
        self.progressBar.setValue(valor)

    def agregar_log(self, msg):
        ahora = datetime.now().strftime("%H:%M:%S")
        self.txtLog.append(f"[{ahora}] {msg}")
        self.txtLog.ensureCursorVisible()

    def proceso_terminado(self):
        self.agregar_log("🎉 Proceso finalizado")
        self.btnProcesar.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())