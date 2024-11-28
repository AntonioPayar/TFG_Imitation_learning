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
from pynput import keyboard
from collections import Counter


listener = None


class CapturadoraGrabacion(Capturadora):
    def __init__(self,monitor,db,data_lake):
        super().__init__(monitor,db,data_lake)
        self.key_presses = []
    
    def on_press(self,key):
        tecla = 2

        if key == keyboard.Key.left:
            tecla = 0
        elif key == keyboard.Key.right:
            tecla = 1
        elif key == keyboard.Key.up:
            tecla = 3
        elif key == keyboard.Key.down:
            tecla = 4
            print("----------FIN SERIE----------")
            self.guardar_sqlite()
            
            self.ID = self.ID + 1
            self.orden = 0
            self.df_pov = pd.DataFrame()
            self.df_mapa = pd.DataFrame()
        elif key == keyboard.Key.esc:
            comun_file.get_Finalizacion = True
            print("Saliendo 01")          
            return True
        
        self.key_presses.append(tecla)
        return False


    def get_screenshot(self):

        if comun_file.get_Finalizacion == True :
            print("Saliendo...")
            return

        # Limpiar key_presses para cada ciclo de main
        self.key_presses.clear()

        try:
            self.orden = self.orden + 1

            for i in range(5):

                if comun_file.get_Finalizacion == True :
                    print("Saliendo...")
                    return
                
                self.posicion_i = i
                img_mini_mapa , img_np = self.cargar_pantalla()
                
                # Obtiene la fecha y hora actual
                now = datetime.now()
                timestamp = now.strftime("%d-%H-%M-%S-%f")
                
                #Creamos el nombre de las imgs
                mini_str = f"{self.data_lake}/mini_mapa/mini_mapa_{timestamp}.jpg"
                pov_str = f"{self.data_lake}/pov/pov_{timestamp}.jpg"

                #Guarda las imágenes JPG
                if comun_file.save_check.get() == False:
                    cv2.imwrite(mini_str, img_mini_mapa)
                    cv2.imwrite(pov_str, img_np)
                           
                #Almacenamos la localizacion de la img
                self.lista_url_img_mini[i] = mini_str
                self.lista_url_img_pov[i] = pov_str
                #Almacenamos la img
                self.lista_img_mini[i] = img_mini_mapa
                self.lista_img_pov[i] = img_np

                # Esperar 0.1 segundos antes de la siguiente foto
                time.sleep(0.1)
                
            print("----------------------------")

            #Capturamos teclas 0.45 secs
            if not self.capture_keys():
                return  # Salir si `ESC` fue presionado

            counts = Counter(self.key_presses)
            array_movimiento = []

            if len(counts.items()) == 1 : 
                for number, count in counts.items():
                    if number != 2:
                        array_movimiento.append([int(count),int(number),int(0)])
                    else:
                        count = 0
                        array_movimiento.append([int(count),int(number),int(0)])

            elif len(counts.items()) == 2 :
                for number, count in counts.items():
                    if number != 2 :
                        array_movimiento.append([int(count),int(number),int(0)])
                             
            if len(array_movimiento) == 1:
                print(array_movimiento[0])

                self.lista_movimientos[0] = int(array_movimiento[0][0])
                self.lista_movimientos[1] = int(array_movimiento[0][1])
                self.lista_movimientos[2] = int(0)

                # Guardamos label en csv
                self.preparar_cola_interfaz()
                self.vaciar_memoria()
            elif len(array_movimiento) == 0:
                print("Forward")

                self.lista_movimientos[0] = int(1)
                self.lista_movimientos[1] = int(2)
                self.lista_movimientos[2] = int(0)

                # Guardamos label en csv
                self.preparar_cola_interfaz()
                self.vaciar_memoria()

        except KeyboardInterrupt:
            comun_file.get_Finalizacion = True
            print("Deteniendo el script...")
    


    def capture_keys(self):
        #Captura teclas inmediatamente después de las 5 fotos.
        start_time = time.time()

        while time.time() - start_time < 0.45:  # Limitar el tiempo de escucha a 0.45 segundos
            with keyboard.Events() as events:  # Crear un manejador de eventos de teclado
                event = events.get(0.45)  # Esperar un evento de teclado por un máximo de 0.45 segundos
                if event is None:
                    continue  # Si no hay eventos, seguir iterando

                if isinstance(event, keyboard.Events.Press):  # Si se detecta una pulsación de tecla
                    if self.on_press(event.key):  # Procesar la tecla presionada
                        return False  # Si `ESC` es presionado, detener el programa

        return True  # Si no se presiona `ESC`, continuar con el programa




    def run(self):
        self.get_screenshot()
       
    
    def preparar_cola_interfaz(self):
        #Almacenamos las img y csv
        self.preparacion_datos_pandas()

        #Enviamos las imagenes a la interfaz grafica
        comun_file.cola_imagenes_map.put(self.lista_img_mini)
        comun_file.cola_imagenes_pov.put(self.lista_img_pov)
        comun_file.cola_mov_raton.put(self.lista_movimientos)

