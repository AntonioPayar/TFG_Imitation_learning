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
from pynput.mouse import Controller

import comun_file

#Funcion Media de una lista de movimientos registrados
media = lambda lista: [round(sum(x[0] for x in lista) / len(lista)), round(sum(x[1] for x in lista) / len(lista))]

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
            img_pov = cv2.resize(img_np, (640, 360))

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

    csv_path = 'datos/grabacion/datos_bo3_minimapa.csv'

    if not os.path.isfile(csv_path):
        # Si el archivo no existe, escribir el DataFrame con el encabezado
        comun_file.DF_mini.to_csv(csv_path, mode='w', header=True, index=False)
    else:
        # Si el archivo existe, escribir el DataFrame sin el encabezado
        comun_file.DF_mini.to_csv(csv_path, mode='a', header=False, index=False)
    
    csv_path = 'datos/grabacion/datos_bo3_pov.csv'

    if not os.path.isfile(csv_path):
        # Si el archivo no existe, escribir el DataFrame con el encabezado
        comun_file.DF_pov.to_csv(csv_path, mode='w', header=True, index=False)
    else:
        # Si el archivo existe, escribir el DataFrame sin el encabezado
        comun_file.DF_pov.to_csv(csv_path, mode='a', header=False, index=False)


def captura_movimineto_raton():
    detector = MouseMoveDetector(comun_file.intervalo_captura)  #Clase en Captura_Utils
    detector.start()
    return detector.capture_displacement() #Retorna el movimiento realizado con el raton

def mover_raton_prediccion(delta_x, delta_y):
    # Creamos una instancia del controlador del ratón
    mouse = Controller()
    
    # Obtenemos la posición actual del ratón
    current_x, current_y = mouse.position
    
    # Calculamos las nuevas coordenadas sumando los deltas
    new_x = current_x + delta_x
    new_y = current_y + delta_y

    # Limitamos las coordenadas para asegurar que estén dentro del rango válido
    new_x = max(0, min(new_x, comun_file.resolucion_pantalla[0]))
    new_y = max(0, min(new_y, comun_file.resolucion_pantalla[1]))

    # Movemos el ratón a las nuevas coordenadas
    mouse.position = (int(new_x), int(new_y))

    print(f"Ratón movido a: {new_x}, {new_y}")

# Clase captura el movimineto del Raton instanciando un nuevo hilo
class MouseMoveDetector(threading.Thread):
    def __init__(self,intervalo_tiempo):
        super().__init__()
        self.current_position = (0, 0)
        self.total_displacement = (0, 0)
        self.intervalo = intervalo_tiempo
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

    def capture_displacement(self):
        time.sleep(self.intervalo)  # Espera durante el intervalo especificado
        movimiento = [None,None]
        with self.lock:
            dx, dy = self.total_displacement
            movimiento = [int(dx),int(dy)]
            # Resetear el desplazamiento para el próximo intervalo
            self.total_displacement = (0, 0)
        self.listener.stop()  # Detener el listener después de capturar el desplazamiento
        return movimiento





