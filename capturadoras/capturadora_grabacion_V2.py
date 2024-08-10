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
from pynput import keyboard
from collections import Counter


listener = None


class CapturadoraGrabacion(Capturadora):
    def __init__(self,monitor,csv_mini,csv_pov):
        super().__init__(monitor,csv_mini,csv_pov)
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
        elif key == keyboard.Key.f1:
            comun_file.get_Finalizacion = True
            return 
        
        self.key_presses.append(tecla)


    def get_screenshot(self):

        if comun_file.get_Finalizacion == True :
            return

        # Limpiar key_presses para cada ciclo de main
        self.key_presses.clear()

        try:
            for i in range(5):
                self.posicion_i = i
                
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

                # Esperar 0.1 segundos antes de la siguiente foto
                time.sleep(0.1)
                
            print("----------------------------")

            # Iniciar el listener del teclado después de capturar las imágenes
            listener = keyboard.Listener(on_press=self.on_press)
            listener.start()

            # Usar un temporizador para detener el listener después de un tiempo
            def stop_listener():
                listener.stop()

            # Por ejemplo, escuchamos las teclas por 2 segundos
            timer = threading.Timer(0.45, stop_listener)
            timer.start()

            # Esperar a que el listener se detenga
            timer.join()


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
                    if number != 2:
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

        finally:
            if listener.running:
                listener.stop()


    def run(self):
        self.get_screenshot()
       
    
    def preparar_cola_interfaz(self):
        #Almacenamos las img y csv
        self.preparacion_datos_pandas()

        #Enviamos las imagenes a la interfaz grafica
        comun_file.cola_imagenes_map.put(self.lista_img_mini)
        comun_file.cola_imagenes_pov.put(self.lista_img_pov)
        comun_file.cola_mov_raton.put(self.lista_movimientos)

    
    '''
    def set_movimiento(self,tecla_pulsada):
        self.lista_movimientos[0] = int(tecla_pulsada)
        self.lista_movimientos[1] = int(0)
        #print(str(dx)+" , "+str(dy))

        print("Tecla -> "+str(tecla_pulsada))
    '''
    '''
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
            time.sleep(0.1)
        print("----------------------------")
        self.preparar_cola_interfaz()
    '''
        
        # FUNONA PERFECTO
    def get_mouse_movement(self,interval=0.9):
        '''
        disp = display.Display()
        root = disp.screen().root

        last_pos = root.query_pointer()._data
        time.sleep(interval)
        current_pos = root.query_pointer()._data

        dx = current_pos['root_x'] - last_pos['root_x']
        dy = current_pos['root_y'] - last_pos['root_y']
        '''
        
        detectar_teclas()
        
        self.lista_movimientos[0] = int(comun_file.teclas_movimiento)
        self.lista_movimientos[1] = int(0)

        if comun_file.teclas_movimiento == 1:
            print("Tecla "+str(comun_file.teclas_movimiento)+" pulsaciones "+str(comun_file.num_pulsaciones_00))
        elif comun_file.teclas_movimiento == 0:
            print("Tecla "+str(comun_file.teclas_movimiento)+" pulsaciones "+str(comun_file.num_pulsaciones_01))
        
        recargar_tecla()


'''
def on_press(key):
    try:
        if key == keyboard.Key.up:
            comun_file.teclas_movimiento = 3
        elif key == keyboard.Key.down:
            print(" ")
        elif key == keyboard.Key.left:
            comun_file.teclas_movimiento = 0
            comun_file.num_pulsaciones_00 = comun_file.num_pulsaciones_00 + 1
        elif key == keyboard.Key.right:
            comun_file.teclas_movimiento = 1
            comun_file.num_pulsaciones_01 = comun_file.num_pulsaciones_01 + 1
    except AttributeError:
        # Ignorar teclas que no son de dirección
        pass
'''
def recargar_tecla() :
    comun_file.num_pulsaciones_01 = 0
    comun_file.num_pulsaciones_00 = 0
    comun_file.teclas_movimiento = 2



def detectar_teclas():
    global listener
    with keyboard.Listener(on_press=on_press) as listener:
        # Esperar 1 segundo y luego detener el listener
        time.sleep(0.2)
        listener.stop()


