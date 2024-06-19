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
        # print("Key w pressed")
    elif 'a' in keys_pressed:
        keys_number = 2
        # print("Key a pressed")
    elif 's' in keys_pressed:
        keys_number = 3
        # print("Key s pressed")
    elif 'd' in keys_pressed:
        keys_number = 4
        # print("Key d pressed")  
    elif 'w' in keys_pressed and 'a' in keys_pressed:
        keys_number = 5
        # print("Combination wa pressed")
    elif 'w' in keys_pressed and 'd' in keys_pressed:
        keys_number = 6
        # print("Combination wd pressed")
    elif 's' in keys_pressed and 'a' in keys_pressed:
        keys_number = 7
        # print("Combination sa pressed")
    elif 's' in keys_pressed and 'd' in keys_pressed:
        keys_number = 8
        # print("Combination sd pressed")

def mouse_listener():
    # Listener para el movimiento del mouse
    with Listener(on_move=on_move) as listener:
        listener.join()

def keyboard_listener():
    with KeyboardListener(on_press=on_key_press, on_release=on_key_release) as listener:
        listener.join()


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


def modo_grabacion_movimientos():

    time.sleep(5)       #Esperamos unos segundos hasta que empiece la partida

    # Asegúrate de que la ventana esté visible
    if comun_file.cod_window.isMinimized:
        comun_file.cod_window.restore()

    # Trae la ventana al frente
    comun_file.cod_window.activate()

    lista_url_img_mini = [None, None,None, None,None]
    lista_img_mini = [None, None,None, None,None]
    lista_url_img_pov = [None, None,None, None,None]
    lista_img_pov = [None, None,None, None,None]

    i = 0

    while True:
        
        img_mini_mapa , img_np = cargar_pantalla()

        # Obtiene la fecha y hora actual
        now = datetime.now()
        timestamp = now.strftime("%d-%H-%M-%S")

        mini_str = f"datos/mini_mapa/mini_mapa_{timestamp}.jpg"
        pov_str = f"datos/pov/pov_{timestamp}.jpg"

        # -------------------------------------------------Guarda las imágenes redimensionadas en formato JPG
        # cv2.imwrite(mini_str, img_mini_mapa)
        # cv2.imwrite(pov_str, img_np)

        #Almacenamos la localizacion y la propia img
        lista_url_img_mini[i] = mini_str
        lista_url_img_pov[i] = pov_str
        lista_img_mini[i] = img_mini_mapa
        lista_img_pov[i] = img_np

        if i < 4:
            i = i + 1
        else:
            #-----------Almacenamos las img y csv
            mouse_final= almacenar_informacion(lista_url_img_mini,lista_url_img_pov)

            #Enviamos las imagenes a la interfaz grafica
            comun_file.cola_imagenes_map.put(lista_img_mini)
            comun_file.cola_imagenes_pov.put(lista_img_pov)
            comun_file.cola_mov_raton.put(mouse_final)

            i = 0
            lista_img_mini = [None, None,None, None,None]
            lista_img_pov = [None, None,None, None,None]
        
        # Esperar 0.5 segundos antes de la próxima captura
        time.sleep(0.2)

        # Salir del bucle si se presiona el boton finalizar
        if comun_file.get_Finalizacion == True:
            break

def modo_autonomo_moviminetos():

    time.sleep(5)       #Esperamos unos segundos hasta que empiece la partida

    # Asegúrate de que la ventana esté visible
    if comun_file.cod_window.isMinimized:
        comun_file.cod_window.restore()

    # Trae la ventana al frente
    comun_file.cod_window.activate()

    lista_url_img_mini = [None, None,None, None,None]
    lista_img_mini = [None, None,None, None,None]
    lista_url_img_pov = [None, None,None, None,None]
    lista_img_pov = [None, None,None, None,None]

    i = 0

    while True:
        
        img_mini_mapa , img_np = cargar_pantalla()

        # Obtiene la fecha y hora actual
        now = datetime.now()
        timestamp = now.strftime("%d-%H-%M-%S")

        mini_str = f"datos/mini_mapa/mini_mapa_{timestamp}.jpg"
        pov_str = f"datos/pov/pov_{timestamp}.jpg"

        #Almacenamos la localizacion y la propia img
        lista_url_img_mini[i] = mini_str
        lista_url_img_pov[i] = pov_str
        lista_img_mini[i] = img_mini_mapa
        lista_img_pov[i] = img_np

        if i < 4:
            i = i + 1
        else:
            comun_file.cola_imagenes_map.put(lista_img_mini)
            comun_file.cola_imagenes_pov.put(lista_img_pov)
            i = 0
            lista_img_mini = [None, None,None, None,None]
            lista_img_pov = [None, None,None, None,None]
        
        # Esperar 0.5 segundos antes de la próxima captura
        time.sleep(0.2)

        # Salir del bucle si se presiona el boton finalizar
        if comun_file.get_Finalizacion == True:
            break


def almacenar_informacion(img_mini,img_pov):
    global exit_event
    global keys_number

    # Crear y comenzar un nuevo hilo para el listener
    mouse_thread = threading.Thread(target=mouse_listener)
    keyboard_thread  = threading.Thread(target=keyboard_listener)

    mouse_thread.start()
    keyboard_thread.start()
    # Esperar hasta que se establezca el evento para salir del bucle
    exit_event.wait()
    

    # print(f'Las coordenadas finales del mouse son ({mouse_coords["x"]}, {mouse_coords["y"]})')

    mouse_final = [int(keys_number),int(mouse_coords["x"]),int(mouse_coords["y"])]

    keys_number = 0

    # Crear DataFrames para cada matriz
    row ={'mini_01': img_mini[0], 'mini_02': img_mini[1], 'mini_03': img_mini[2], 'mini_04': img_mini[3],'mini_05': img_mini[4], 'mouse_final':mouse_final}
    row_pov = {'pov_01': img_pov[0], 'pov_02': img_pov[1], 'pov_03': img_pov[2], 'pov_04': img_pov[3],'pov_05': img_pov[4], 'mouse_final':mouse_final}

    # guardar_csv(row,row_pov)
    
    return mouse_final


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



