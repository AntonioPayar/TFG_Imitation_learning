import numpy as np
import pandas as pd
import cv2
import mss
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener, Key
#import pyautogui
#from pynput.mouse import Listener
#from pynput.keyboard import Listener as KeyboardListener, Key
import threading
from datetime import datetime
import os
import time
from PIL import ImageGrab , Image ,UnidentifiedImageError
import queue

import comun_file

# Variable de control para salir del bucle
exit_event = threading.Event()
mouse_coords = {'x': None, 'y': None}
keys_pressed = set()
keys_number = 0


def on_move(x, y):
    global mouse_coords,exit_event
    mouse_coords['x'] = x
    mouse_coords['y'] = y
    # Establecer el evento para salir del bucle
    exit_event.set()

def on_key_press(key):
    global keys_pressed
    try:
        if key.char in ['w', 'a', 's', 'd']:
            keys_pressed.add(key.char)
            check_combinations()
    except AttributeError:
        pass

def on_key_release(key):
    global keys_pressed
    try:
        if key.char in ['w', 'a', 's', 'd']:
            keys_pressed.discard(key.char)
    except AttributeError:
        pass

def check_combinations():
    global keys_number

    if 'w' in keys_pressed:
        keys_number = 1
    elif 'a' in keys_pressed:
        keys_number = 2
    elif 's' in keys_pressed:
        keys_number = 3
    elif 'd' in keys_pressed:
        keys_number = 4 
    elif 'w' in keys_pressed and 'a' in keys_pressed:
        keys_number = 5
    elif 'w' in keys_pressed and 'd' in keys_pressed:
        keys_number = 6
    elif 's' in keys_pressed and 'a' in keys_pressed:
        keys_number = 7
    elif 's' in keys_pressed and 'd' in keys_pressed:
        keys_number = 8

def mouse_and_keyboard_listener():
    global exit_event
    # Listener para el movimiento del mouse y las pulsaciones de teclas
    with MouseListener(on_move=on_move) as mouse_listener, \
         KeyboardListener(on_press=on_key_press) as keyboard_listener:
        
        # Unificar los eventos de salida de ambos listeners
        while not exit_event.is_set():
            exit_event.wait(timeout=0.1)  # Esperar hasta que se establezca el evento para salir del bucle

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

'''
def cargar_pantalla():

    try :
        screenshot = pyautogui.screenshot()
        #Convertimos a np
        img_np = np.array(screenshot)
        img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        img_mini_mapa = procesar_frames_minimapa(img_np)

        img_mini_mapa = cv2.resize(img_mini_mapa, (268, 183))
        img_pov = cv2.resize(img_np, (1280, 720))

        return img_mini_mapa, img_pov
    
    except UnidentifiedImageError as e:
        print(f"Error al capturar la pantalla: {e}")
        img_mini_mapa = np.empty(shape=(268, 183,3), dtype=np.float64)
        img_pov = np.empty(shape=(1280, 720, 3), dtype=np.float64)
        return img_mini_mapa, img_pov
'''

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





