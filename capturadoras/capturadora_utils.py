import numpy as np
import pandas as pd
import cv2
import mss
import threading
from datetime import datetime
import os
import time
import sqlite3
from PIL import Image
from pynput import mouse
from pynput.mouse import Controller
from Xlib import display

import comun_file

lock = threading.Lock()

class Capturadora:
    def __init__(self,monitor,db):
        self.monito = monitor
        self.db = db
        self.ID = None
        self.df_pov = pd.DataFrame()
        self.df_mapa = pd.DataFrame()
        self.orden = 0
        self.ultimo_id()
        self.vaciar_memoria()
    
    def vaciar_memoria(self):
        self.lista_url_img_mini = [None, None,None, None,None]
        self.lista_img_mini = [None, None,None, None,None]
        self.lista_url_img_pov = [None, None,None, None,None]
        self.lista_img_pov = [None, None,None, None,None]
        self.lista_movimientos = [None,None,None]
    
    def ultimo_id(self):
        conexion = sqlite3.connect('datos/grabacion/base_datos_cod.db')
        # Crear un cursor para interactuar con la base de datos
        cursor = conexion.cursor()  
        cursor.execute("SELECT MAX(id) FROM series_de_tiempo")
    
        self.ID = cursor.fetchone()[0]
        conexion.close()

        if self.ID == None:
            self.ID = 0
        else :
            self.ID = self.ID + 1

    def zoom_frame_minimapa(self, frame,zoom_factor):

        # Obtiene las dimensiones del fotograma
        height, width, _ = frame.shape

        # Calcula las dimensiones del área de zoom
        zoom_height, zoom_width = height // zoom_factor, width // zoom_factor

        # Calcula las coordenadas del área de zoom, incluyendo el desplazamiento horizontal
        x_start = 0
        x_end = (x_start + zoom_width) - 200
        y_start = 20
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
        M = cv2.getRotationMatrix2D(center, + 2, 1.1)

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

                # Recortamos el mapa a img pov
                width, height = screenshot.size
                
                if comun_file.mapa_check == False:  # Si queremos mini_mapa cortamos la imagen para quitarlo del pov
                    img_pov = screenshot.crop((0, 280, width, height))
                else:
                    img_pov = screenshot.crop((0, 10, width, height))
                
                #Creamos la imagen mapa
                img_mini_mapa = np.array(screenshot)
                img_mini_mapa = cv2.cvtColor(img_mini_mapa, cv2.COLOR_RGB2BGR)
                img_mini_mapa = self.procesar_frames_minimapa(img_mini_mapa)

                #Creamos la imagen pov
                img_pov = np.array(img_pov)
                img_pov = cv2.cvtColor(img_pov, cv2.COLOR_RGB2BGR)

                img_mini_mapa = cv2.resize(img_mini_mapa, (300, 225))

                #Cambiamos el tamaño de la imagen pov si no queremos grabar cod
                if comun_file.mapa_check == False : 
                    img_pov = cv2.resize(img_pov, (300, 225))
                else : 
                    img_pov = cv2.resize(img_pov, (512, 288))

            except Exception as e:
                print(f"Error general en el intento : {e}")
                time.sleep(1)  # Esperar antes de volver a intentar
            finally:
                sct.close()

            return img_mini_mapa, img_pov
    
    def preparacion_datos_pandas(self):

        # Crear DataFrames para cada matriz
        row_mapa ={
                'id': self.ID,
                'orden': self.orden,
                'mapa_01': self.lista_url_img_mini[0],
                'mapa_02': self.lista_url_img_mini[1],
                'mapa_03': self.lista_url_img_mini[2],
                'mapa_04': self.lista_url_img_mini[3],
                'mapa_05': self.lista_url_img_mini[4],
                'etiqueta':str(self.lista_movimientos)
                }
        
        row_pov ={ 
                'id': self.ID,
                'orden': self.orden,
                'pov_01': self.lista_url_img_pov[0],
                'pov_02': self.lista_url_img_pov[1],
                'pov_03': self.lista_url_img_pov[2],
                'pov_04': self.lista_url_img_pov[3],
                'pov_05': self.lista_url_img_pov[4],
                'etiqueta':str(self.lista_movimientos)
                }

        # Crear y concatenar los DataFrames con un índice explícito
        self.df_mapa = pd.concat([self.df_mapa, pd.DataFrame(row_mapa, index=[0])], ignore_index=True)
        self.df_pov = pd.concat([self.df_pov, pd.DataFrame(row_pov, index=[0])], ignore_index=True)

    
    def guardar_sqlite(self):
        global lock

        data_02 ={
                'id': [self.ID],
                'nombre': ["muerte_"+str(self.ID)],
                }
        
        df_series = pd.DataFrame(data_02)

        with lock:  # Bloqueo al inicio de la escritura
            # Conectar a la base de datos
            conexion = sqlite3.connect(self.db)   
            self.df_pov.to_sql('videos_pov', conexion, if_exists='append', index=False)
            self.df_mapa.to_sql('videos_mapa', conexion, if_exists='append', index=False)
            df_series.to_sql('series_de_tiempo', conexion, if_exists='append', index=False)
            conexion.close()


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
        print(str(dx)+" , "+str(dy))

    def guardar_csv_final(self):
        #Archivo csv mini
        if not os.path.isfile(self.csv_mini):
            # Si el archivo no existe, escribir el DataFrame con el encabezado
            comun_file.DF_mini.to_csv(self.csv_mini, mode='w', header=True, index=False)
        else :
            # Si el archivo existe, escribir el DataFrame sin el encabezado
            comun_file.DF_mini.to_csv(self.csv_mini, mode='a', header=False, index=False)

        #Archivo cvs pov
        if not os.path.isfile(self.csv_pov):
            # Si el archivo no existe, escribir el DataFrame con el encabezado
            comun_file.DF_pov.to_csv(self.csv_pov, mode='w', header=True, index=False)
        else :
            # Si el archivo existe, escribir el DataFrame sin el encabezado
            comun_file.DF_pov.to_csv(self.csv_pov, mode='a', header=False, index=False)


