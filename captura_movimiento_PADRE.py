from Xlib import display
import time
import threading
import mss
from PIL import Image
import numpy as np
import cv2
import pandas as pd
import os
from datetime import datetime
import csv

import comun_file


class Capturadora():
    def __init__(self,monitor):
        self.monito = monitor
        self.lock = threading.Lock()    # Añadir un lock para sincronización csv

        self.lista_url_img_mini = [None, None,None, None,None]
        self.lista_img_mini = [None, None,None, None,None]

        self.lista_url_img_pov = [None, None,None, None,None]
        self.lista_img_pov = [None, None,None, None,None]

        self.lista_movimientos = [None,None]

    def zoom_frame_minimapa(self, frame,zoom_factor):

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

    def procesar_frames_minimapa(self,img_np):
        
        img_np = self.zoom_frame_minimapa(img_np,3)

        # Obtener las dimensiones de la imagen
        (h, w) = img_np.shape[:2]

        # Calcular el centro de la imagen
        center = (w // 2, h // 2)

        # Calcular la matriz de rotación
        M = cv2.getRotationMatrix2D(center, + 2, 1.0)

        # Aplicar la rotación
        img_np = cv2.warpAffine(img_np, M, (w, h))

        return img_np

    def cargar_pantalla(self):
        img_mini_mapa = None
        img_pov = None

        with mss.mss() as sct:
            try:
                # Captura el monitor donde esta el juego
                sct_img = sct.grab(sct.monitors[self.monito])
                
                # Convertir la captura en una imagen de PIL
                screenshot = Image.frombytes("RGB", (sct_img.width, sct_img.height), sct_img.rgb)
                
                #Convertimos a np
                img_np = np.array(screenshot)
                img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

                img_mini_mapa = self.procesar_frames_minimapa(img_np)

                img_mini_mapa = cv2.resize(img_mini_mapa, (135, 93))
                img_pov = cv2.resize(img_np, (640, 360))

            except Exception as e:
                print(f"Error general en el intento : {e}")
                time.sleep(1)  # Esperar antes de volver a intentar
            finally:
                sct.close()  # Asegurarse de liberar la conexión al finalizar

            return img_mini_mapa, img_pov

    def guardar_csv(self,row,row_pov):

        # Create a DataFrame from the row
        row_df = pd.DataFrame([row])
        row_df_pov = pd.DataFrame([row_pov])

        print(row_df)

        with self.lock:  # Bloqueo al inicio de la escritura

            comun_file.DF_mini = pd.concat([comun_file.DF_mini, row_df], ignore_index=True)
            comun_file.DF_pov = pd.concat([comun_file.DF_pov, row_df_pov], ignore_index=True)

            csv_path = 'datos/grabacion/datos_bo3_minimapa.csv'

            if not os.path.isfile(csv_path):
                # Si el archivo no existe, escribir el DataFrame con el encabezado
                comun_file.DF_mini.to_csv(csv_path, mode='w', header=True, index=False)
            else :
                # Si el archivo existe, escribir el DataFrame sin el encabezado
                comun_file.DF_mini.to_csv(csv_path, mode='a', header=False, index=False)
            
            csv_path = 'datos/grabacion/datos_bo3_pov.csv'

            if not os.path.isfile(csv_path):
                # Si el archivo no existe, escribir el DataFrame con el encabezado
                comun_file.DF_pov.to_csv(csv_path, mode='w', header=True, index=False)
            else :
                # Si el archivo existe, escribir el DataFrame sin el encabezado
                comun_file.DF_pov.to_csv(csv_path, mode='a', header=False, index=False)

    def preparacion_datos_pandas(self):

        # Crear DataFrames para cada matriz
        row ={'mini_01': self.lista_url_img_mini[0], 'mini_02': self.lista_url_img_mini[1], 'mini_03': self.lista_url_img_mini[2], 'mini_04': self.lista_url_img_mini[3],'mini_05': self.lista_url_img_mini[4], 'mouse_final':self.lista_movimientos}
        row_pov = {'pov_01': self.lista_url_img_pov[0], 'pov_02': self.lista_url_img_pov[1], 'pov_03': self.lista_url_img_pov[2], 'pov_04': self.lista_url_img_pov[3],'pov_05': self.lista_url_img_pov[4], 'mouse_final':self.lista_movimientos}
        
        #Guardamos datos en csv
        self.guardar_csv(row,row_pov)

    # FUNONA PERFECTO
    def get_mouse_movement(self,interval=0.9):
        disp = display.Display()
        root = disp.screen().root

        last_pos = root.query_pointer()._data
        time.sleep(interval)
        current_pos = root.query_pointer()._data

        dx = current_pos['root_x'] - last_pos['root_x']
        dy = current_pos['root_y'] - last_pos['root_y']
        
        self.lista_movimientos[0] = int(dx)
        self.lista_movimientos[1] = int(dy)
        #print(str(dx)+" , "+str(dy))
        
    def get_screenshot(self):

        for i in range(5):
            self.posicion_i = i
            #print("Imagen..."+str(i))
            img_mini_mapa , img_np = self.cargar_pantalla()

            # Obtiene la fecha y hora actual
            now = datetime.now()
            timestamp = now.strftime("%d-%H-%M-%S-%f")

            #Creamos el nombre de las imgs
            mini_str = f"datos/grabacion/mini_mapa/mini_mapa_{timestamp}.jpg"
            pov_str = f"datos/grabacion/pov/pov_{timestamp}.jpg"

            #Guarda las imágenes JPG
            cv2.imwrite(mini_str, img_mini_mapa)
            cv2.imwrite(pov_str, img_np)

            #Almacenamos la localizacion de la img
            self.lista_url_img_mini[i] = mini_str
            self.lista_url_img_pov[i] = pov_str
            #Almacenamos la img
            self.lista_img_mini[i] = img_mini_mapa
            self.lista_img_pov[i] = img_np
            #Pausa entre capturas
            time.sleep(0.2)
        print("----------------------------")


    # Función principal para ejecutar en hilos
    def run(self):

        #Creamos dos hilos
        mouse_thread = threading.Thread(target=self.get_mouse_movement) #Capturamos movimiento
        capture_thread = threading.Thread(target=self.get_screenshot)   #Capturamos imagenes
        
        mouse_thread.start()
        capture_thread.start()

        mouse_thread.join()
        capture_thread.join()

        #Almacenamos las img y csv
        self.preparacion_datos_pandas()





if __name__ == '__main__':
    while True:
        capturadora = Capturadora(monitor = 1)
        capturadora.run()
