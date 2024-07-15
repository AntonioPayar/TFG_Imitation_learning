from capturadoras.capturadora_utils import *
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


class CapturadoraGrabacion(Capturadora):
    def __init__(self,monitor,csv_mini,csv_pov):
        super().__init__(monitor,csv_mini,csv_pov)

    # Función principal para ejecutar en hilos
    def run(self):
        mouse_thread = threading.Thread(target=self.get_mouse_movement)
        capture_thread = threading.Thread(target=self.get_screenshot)
        
        mouse_thread.start()
        capture_thread.start()

        mouse_thread.join()
        capture_thread.join()

        #Almacenamos las img y csv
        self.preparacion_datos_pandas()

        #Enviamos las imagenes a la interfaz grafica
        comun_file.cola_imagenes_map.put(self.lista_img_mini)
        comun_file.cola_imagenes_pov.put(self.lista_img_pov)
        comun_file.cola_mov_raton.put(self.lista_movimientos)

   
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
            #cv2.imwrite(mini_str, img_mini_mapa)
            #cv2.imwrite(pov_str, img_np)

            #Almacenamos la localizacion de la img
            self.lista_url_img_mini[i] = mini_str
            self.lista_url_img_pov[i] = pov_str
            #Almacenamos la img
            self.lista_img_mini[i] = img_mini_mapa
            self.lista_img_pov[i] = img_np
            #Pausa entre capturas
            time.sleep(0.2)
        print("----------------------------")
