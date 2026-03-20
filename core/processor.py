import os
import re
from datetime import datetime
from PIL import Image
import piexif
import shutil


def procesar_imagenes(carpeta_origen, carpeta_destino, log_callback=None, progress_callback=None):
    patron = re.compile(r"(IMG)-(\d{8})-WA\d+", re.IGNORECASE)

    archivos = [
    f for f in os.listdir(carpeta_origen) if os.path.isfile(os.path.join(carpeta_origen, f))]

    total = len(archivos)

    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)

    procesados = 0

    for i, archivo in enumerate(archivos):
        ruta_origen = os.path.join(carpeta_origen, archivo)
        ruta_destino = os.path.join(carpeta_destino, archivo)

        try:
            if archivo.lower().endswith((".jpg", ".jpeg")):
                with Image.open(ruta_origen) as imagen:
                    exif_bytes = imagen.info.get("exif", None)
                    # 1. Si ya tiene fecha → copiar y seguir
                    if exif_bytes:
                        exif_dict = piexif.load(exif_bytes)
                        if piexif.ExifIFD.DateTimeOriginal in exif_dict["Exif"]:
                            shutil.copy2(ruta_origen, ruta_destino)
                            if log_callback:
                                log_callback(f"⏭️ {archivo} (ya tiene fecha)")
                            continue
                    # 2. Intentar extraer fecha del nombre
                    match = patron.search(archivo)
                    if match:
                        fecha_str = match.group(2)
                        fecha = datetime.strptime(fecha_str, "%Y%m%d")
                        fecha_exif = fecha.strftime("%Y:%m:%d 12:00:00")
                        exif_dict = {
                            "0th": {},
                            "Exif": {
                                piexif.ExifIFD.DateTimeOriginal: fecha_exif,
                                piexif.ExifIFD.DateTimeDigitized: fecha_exif,
                            },
                            "1st": {},
                            "thumbnail": None,
                        }
                        exif_bytes = piexif.dump(exif_dict)
                        imagen.save(ruta_destino, exif=exif_bytes)
                        if log_callback:
                            log_callback(f"✅ {archivo}")
                    else:
                        shutil.copy2(ruta_origen, ruta_destino)
                        if log_callback:
                            log_callback(f"⚠️ {archivo} (sin patrón)")
            else:
                # Otros archivos → copiar directo
                shutil.copy2(ruta_origen, ruta_destino)
        except Exception as e:
            if log_callback:
                log_callback(f"❌ {archivo} → {e}")
        finally:
            # progreso SIEMPRE se ejecuta
            procesados += 1
            if progress_callback:
                progreso = int((procesados / total) * 100)
                progress_callback(progreso)

