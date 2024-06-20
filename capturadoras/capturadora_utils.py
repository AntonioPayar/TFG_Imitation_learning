import numpy as np
import pandas as pd
import cv2
from pynput.mouse import Listener
from pynput.keyboard import Listener as KeyboardListener, Key
import threading
from datetime import datetime
import os
import time
from PIL import ImageGrab
import queue

import comun_file

# Variable de control para salir del bucle
exit_event = threading.Event()
mouse_coords = {'x': None, 'y': None}
keys_pressed = set()
keys_number = 0

def zoom_frame_minimapa(frame,zoom_factor):

    # Obtiene las dimensiones del fotograma
    height, width, _ = frame.shape

    # Calcula las dimensiones del área de zoom
    zoom_height, zoom_width = height // zoom_factor, width // zoom_factor

    # Calcula las coordenadas del área de zoom, incluyendo el desplazamiento horizontal
    x_start = 10
    x_end = (x_start + zoom_width) - 250
    y_start = 5
    y_end = (y_start + zoom_height) - 80

    # Recorta el área de zoom basado en la esquina seleccionada 
    cropped_frame = frame[y_start:y_end, x_start:x_end]

    return cropped_frame

def cargar_pantalla():
    # Obtiene las coordenadas de la ventana
    left, top, right, bottom = comun_file.cod_window.left, comun_file.cod_window.top, comun_file.cod_window.right, comun_file.cod_window.bottom
    
    # Ajustar las coordenadas
    top = top + 24
    bottom = bottom - 100

    # Captura la pantalla en las coordenadas de la ventana
    screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))

    # Convierte la imagen a un array de numpy
    img_np = np.array(screenshot)
    img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

    img_mini_mapa = procesar_frames_minimapa(img_np)

    # Redimensiona la ventana minimapa
    img_mini_mapa = cv2.resize(img_mini_mapa, (268, 183))
    # Redimensiona la ventana pov
    img_pov = cv2.resize(img_np, (1280, 720))

    return img_mini_mapa , img_pov

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





