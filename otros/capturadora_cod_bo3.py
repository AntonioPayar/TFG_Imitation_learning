import pygetwindow as gw
import numpy as np
import pandas as pd
from PIL import ImageGrab
import cv2
from pynput.mouse import Listener
import threading
from datetime import datetime
import os
import time


# Variable de control para salir del bucle
exit_event = threading.Event()
mouse_coords = {'x': None, 'y': None}

def on_move(x, y):
    mouse_coords['x'] = x
    mouse_coords['y'] = y
    # Establecer el evento para salir del bucle
    exit_event.set()

def mouse_listener():
    # Listener para el movimiento del mouse
    with Listener(on_move=on_move) as listener:
        # Esperar hasta que se establezca el evento para salir del bucle
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

def capturar_pantalla(cod_window,DF_mini,DF_pov):

    # Asegúrate de que la ventana esté visible
    if cod_window.isMinimized:
        cod_window.restore()

    # Trae la ventana al frente
    cod_window.activate()

    ventanas_mini = ["mini_01","mini_02","mini_03","mini_04","mini_05"]
    ventanas_pov = ["pov_01","pov_02","pov_03","pov_04","pov_05"]

    img_mini = [None, None,None, None,None]
    img_pov = [None, None,None, None,None]

    i = 0

    while True:
        # Obtiene las coordenadas de la ventana
        left, top, right, bottom = cod_window.left, cod_window.top, cod_window.right, cod_window.bottom
        
        # Ajustar las coordenadas
        top = top + 24
        bottom = bottom - 100

        # Captura la pantalla en las coordenadas de la ventana
        screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))

        # Convierte la imagen a un array de numpy
        img_np = np.array(screenshot)
        img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        img_mini_mapa = procesar_frames_minimapa(img_np)

        # Crea ventana minimapa
        cv2.namedWindow(ventanas_mini[i], cv2.WINDOW_NORMAL)
        cv2.resizeWindow(ventanas_mini[i], 268, 183)  # Ajusta el tamaño de la ventana

        # Crea una ventana pov
        cv2.namedWindow(ventanas_pov[i], cv2.WINDOW_NORMAL)
        cv2.resizeWindow(ventanas_pov[i], 360, 240)

        # Redimensiona la ventana minimapa
        img_mini_mapa = cv2.resize(img_mini_mapa, (268, 183))
        # Redimensiona la ventana pov
        img_np = cv2.resize(img_np, (1280, 720))

        # Obtiene la fecha y hora actual
        now = datetime.now()
        timestamp = now.strftime("%d-%H-%M-%S")

        mini_str = f"datos/mini_mapa/mini_mapa_{timestamp}.jpg"
        pov_str = f"datos/pov/pov_{timestamp}.jpg"

        # Guarda las imágenes redimensionadas en formato JPG
        cv2.imwrite(mini_str, img_mini_mapa)
        cv2.imwrite(pov_str, img_np)

        #Almacenamos la localizacion de la img
        img_mini[i] = mini_str
        img_pov[i] = pov_str
        

        # Muestra la ventana minimapa
        cv2.imshow(ventanas_mini[i], img_mini_mapa)
        # Muestra la ventana pov
        cv2.imshow(ventanas_pov[i], img_np)

        if i < 4:
            i = i + 1
        else:
            almacenar_informacion(img_mini,img_pov,DF_mini,DF_pov)
            i = 0
        
        # Esperar 0.5 segundos antes de la próxima captura
        time.sleep(0.5)

        # Salir del bucle si se presiona la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()


def almacenar_informacion(img_mini,img_pov,DF_mini,DF_pov):
    # Crear y comenzar un nuevo hilo para el listener
    listener_thread = threading.Thread(target=mouse_listener)
    listener_thread.start()
    # Esperar hasta que se establezca el evento para salir del bucle
    exit_event.wait()

    print(f'Las coordenadas finales del mouse son ({mouse_coords["x"]}, {mouse_coords["y"]})')

    mouse_final = [int(mouse_coords["x"]),int(mouse_coords["y"])]

    # Crear DataFrames para cada matriz
    row ={'mini_01': img_mini[0], 'mini_02': img_mini[1], 'mini_03': img_mini[2], 'mini_04': img_mini[3],'mini_05': img_mini[4], 'mouse_final':mouse_final}
    row_pov = {'pov_01': img_pov[0], 'pov_02': img_pov[1], 'pov_03': img_pov[2], 'pov_04': img_pov[3],'pov_05': img_pov[4], 'mouse_final':mouse_final}
    
    # Create a DataFrame from the row
    row_df = pd.DataFrame([row])
    row_df_pov = pd.DataFrame([row_pov])

    DF_mini = pd.concat([DF_mini, row_df], ignore_index=True)
    DF_pov = pd.concat([DF_pov, row_df_pov], ignore_index=True)

    csv_path = 'datos/datos_bo3_minimapa.csv'

    if not os.path.isfile(csv_path):
        # Si el archivo no existe, escribir el DataFrame con el encabezado
        DF_mini.to_csv(csv_path, mode='w', header=True, index=False)
    else:
        # Si el archivo existe, escribir el DataFrame sin el encabezado
        DF_mini.to_csv(csv_path, mode='a', header=False, index=False)
    
    csv_path = 'datos/datos_bo3_pov.csv'

    if not os.path.isfile(csv_path):
        # Si el archivo no existe, escribir el DataFrame con el encabezado
        DF_pov.to_csv(csv_path, mode='w', header=True, index=False)
    else:
        # Si el archivo existe, escribir el DataFrame sin el encabezado
        DF_pov.to_csv(csv_path, mode='a', header=False, index=False)



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


if __name__ == '__main__':

    DF_mini = pd.DataFrame(columns=['mini_01','mini_02','mini_03','mini_04','mini_05','mouse_final'])
    DF_pov = pd.DataFrame(columns=['pov_01','pov_02','pov_03','pov_04','pov_05','mouse_final'])

    try:
        cod_window = gw.getWindowsWithTitle("Call of Duty®  - ship - Son_of_Odin")[0]
    except IndexError:
        print(" 😡 Abra desde Steam Call of Duty® para poder empezar 😡")
        print(" 🥸 Corre el Juego en 1920x1080 🥸 ")
        print(" 🥸 Corre el Juego en Ventana (P.Completa) 🥸 ")
        print(" 🤖 El programa no para que correr hasta que des a la q en las ventanas emergentes 🤖 ")

    capturar_pantalla(cod_window,DF_mini,DF_pov)