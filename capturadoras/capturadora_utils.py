import numpy as np
import pandas as pd
import cv2
import mss
import threading
from datetime import datetime
import os
import time
from PIL import ImageGrab , Image ,UnidentifiedImageError
from pynput import mouse

import comun_file

def zoom_frame_minimapa(frame,zoom_factor):

    # Obtiene las dimensiones del fotograma
    height, width, _ = frame.shape

    # Calcula las dimensiones del área de zoom
    zoom_height, zoom_width = height // zoom_factor, width // zoom_factor

    # Calcula las coordenadas del área de zoom, incluyendo el desplazamiento horizontal
    x_start = 10
    x_end = (x_start + zoom_width) - 250
    y_start = 25
    y_end = (y_start + zoom_height) - 110

    # Recorta el área de zoom basado en la esquina seleccionada 
    cropped_frame = frame[y_start:y_end, x_start:x_end]

    return cropped_frame


def cargar_pantalla():
    global id_ventana, display_obj, root, window, geometry
    img_mini_mapa = None
    img_pov = None

    with mss.mss() as sct:
        try:
            # Captura el monitor donde esta el juego
            sct_img = sct.grab(sct.monitors[comun_file.cod_window])
            
            # Convertir la captura en una imagen de PIL
            screenshot = Image.frombytes("RGB", (sct_img.width, sct_img.height), sct_img.rgb)
            
            #Convertimos a np
            img_np = np.array(screenshot)
            img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

            img_mini_mapa = procesar_frames_minimapa(img_np)

            img_mini_mapa = cv2.resize(img_mini_mapa, (135, 93))
            img_pov = cv2.resize(img_np, (320, 180))

        except Exception as e:
            print(f"Error general en el intento : {e}")
            time.sleep(1)  # Esperar antes de volver a intentar
        finally:
            sct.close()  # Asegurarse de liberar la conexión al finalizar

        return img_mini_mapa, img_pov


def procesar_frames_minimapa(img_np):
    
    img_np = zoom_frame_minimapa(img_np,3)

    # Obtener las dimensiones de la imagen
    (h, w) = img_np.shape[:2]

    # Calcular el centro de la imagen
    center = (w // 2, h // 2)

    # Calcular la matriz de rotación
    M = cv2.getRotationMatrix2D(center, + 2, 1.0)

    # Aplicar la rotación
    img_np = cv2.warpAffine(img_np, M, (w, h))

    return img_np


def guardar_csv(row,row_pov):

    # Create a DataFrame from the row
    row_df = pd.DataFrame([row])
    row_df_pov = pd.DataFrame([row_pov])

    comun_file.DF_mini = pd.concat([comun_file.DF_mini, row_df], ignore_index=True)
    comun_file.DF_pov = pd.concat([comun_file.DF_pov, row_df_pov], ignore_index=True)

    csv_path = 'datos/datos_bo3_minimapa.csv'

    if not os.path.isfile(csv_path):
        # Si el archivo no existe, escribir el DataFrame con el encabezado
        comun_file.DF_mini.to_csv(csv_path, mode='w', header=True, index=False)
    else:
        # Si el archivo existe, escribir el DataFrame sin el encabezado
        comun_file.DF_mini.to_csv(csv_path, mode='a', header=False, index=False)
    
    csv_path = 'datos/datos_bo3_pov.csv'

    if not os.path.isfile(csv_path):
        # Si el archivo no existe, escribir el DataFrame con el encabezado
        comun_file.DF_pov.to_csv(csv_path, mode='w', header=True, index=False)
    else:
        # Si el archivo existe, escribir el DataFrame sin el encabezado
        comun_file.DF_pov.to_csv(csv_path, mode='a', header=False, index=False)



# Clase captura el movimineto del Raton instanciando un nuevo hilo
class MouseMoveDetector(threading.Thread):
    def __init__(self):
        super().__init__()
        self.current_position = (0, 0)
        self.total_displacement = (0, 0)
        self.lock = threading.Lock()
        self.listener = mouse.Listener(on_move=self.on_move)

    def on_move(self, x, y):
        with self.lock:
            # Calcular el desplazamiento
            dx = x - self.current_position[0]
            dy = y - self.current_position[1]
            # Actualizar la posición actual y el desplazamiento total
            self.current_position = (x, y)
            self.total_displacement = (self.total_displacement[0] + dx, self.total_displacement[1] + dy)

    def run(self):
        self.listener.start()
        self.listener.join()

    def capture_displacement(self, interval=1):
        time.sleep(interval)  # Espera durante el intervalo especificado
        movimiento = [None,None]
        with self.lock:
            dx, dy = self.total_displacement
            movimiento = [int(dx),int(dy)]
            # Resetear el desplazamiento para el próximo intervalo
            self.total_displacement = (0, 0)
        self.listener.stop()  # Detener el listener después de capturar el desplazamiento
        return movimiento





