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
    def __init__(self,monitor):
        super().__init__(monitor)

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
