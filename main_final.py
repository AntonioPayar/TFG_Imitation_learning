import comun_file
from interfaces import interfaz_seleccion_ventana
from interfaces import interfaz_grabacion
from interfaces import interfaz_autonomo
from capturadoras import capturadora_completa

import pandas as pd
import pygetwindow as gw
import threading


if __name__ == '__main__':

    comun_file.DF_mini = pd.DataFrame(columns=['mini_01','mini_02','mini_03','mini_04','mini_05','mouse_final'])
    comun_file.DF_pov = pd.DataFrame(columns=['pov_01','pov_02','pov_03','pov_04','pov_05','mouse_final'])


    try:
        ventana , opcion_elegida = interfaz_seleccion_ventana.interfaz_selccion_ventana()
        comun_file.cod_window = gw.getWindowsWithTitle(ventana)[0]
    except IndexError:
        print(" 😡 Abra desde Steam Call of Duty® para poder empezar 😡")
        print(" 🥸 Corre el Juego en 1920x1080 🥸 ")
        print(" 🥸 Corre el Juego en Ventana (P.Completa) 🥸 ")
        print(" 🤖 El programa no para que correr hasta que des a la q en las ventanas emergentes 🤖 ")

    if opcion_elegida == 0:
        ineterfaz = interfaz_grabacion.interfaz_grabacion               #Otro hilo para la interfaz
        funcion_elegida = capturadora_completa.modo_grabacion_movimientos
    else : 
        ineterfaz = interfaz_autonomo.interfaz_autonomo                  #Otro hilo para la interfaz
        funcion_elegida = capturadora_completa.modo_autonomo_moviminetos

    imagen_thread = threading.Thread(target=funcion_elegida)        #Un hilo para la capturadora
    imagen_thread.daemon = True 
    imagen_thread.start()

    ineterfaz()     #Llamamos a la funcion