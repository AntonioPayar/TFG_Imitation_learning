import comun_file
from interfaces import interfaz_seleccion_ventana
from interfaces import interfaz_grabacion
from interfaces import interfaz_autonomo
from capturadoras import capturadora_autonoma , capturadora_grabacion ,capturadora_grabacion_V2
import sqlite3
import pandas as pd
import os
import threading
import time
import subprocess
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 

modelo_mapa = "modelos/modelos_entrenados/modelo_todo_0.68_.h5"
DATA_LAKE = "datos/grabacion02"
BASE_SQLITE = DATA_LAKE + "/base_datos_cod.db"

"""
    Funcion encargada de ejecutar el bucle de grabacion

"""

def bucle_capturadora_grabacion():
    global sqlite_db

    #Comprobamos si existen las carpetas
    comun_file.comprobacion_ficheros(DATA_LAKE,BASE_SQLITE)   

    #Esperamos 5 segundos hasta que el usuario se prepara
    time.sleep(5)
    
    capturadora = capturadora_grabacion_V2.CapturadoraGrabacion(comun_file.cod_window,BASE_SQLITE,DATA_LAKE)
    #Bucle hasta que la interfaz grafica da la orden de finalizacion
    while not comun_file.get_Finalizacion:
        capturadora.run()

        
"""
    Funcion encargada de ejecutar el bucle del modo autonomo
"""
def bucle_capturadora_autonoma():
    global csv_mini , csv_pov
    global modelo_mapa

    csv_mini = 'datos/fine_tuning/datos_bo3_minimapa.csv'
    csv_pov = 'datos/fine_tuning/datos_bo3_pov.csv'

    capturadora_autonoma.configuracion_gpu_keras(modelo_mapa)
    #Esperamos 5 segundos hasta que el usuario se prepara
    time.sleep(5)

    capturadora = capturadora_autonoma.CapturadoraAutonoma(comun_file.cod_window,csv_mini,csv_pov)
    #Bucle hasta que la interfaz grafica da la orden de finalizacion
    while comun_file.get_Finalizacion == False:
        capturadora.run()
        capturadora.vaciar_memoria()



#Utilizar entorno
#source ../entorno_TFG/bin/activate

#---Reiniciar XServer
#sudo systemctl restart display-manager.service
#---Mostrar clientes XServer
#xlsclients
if __name__ == '__main__':

    comun_file.intervalo_captura = 0.01
    comun_file.resolucion_pantalla[0] = 1920
    comun_file.resolucion_pantalla[1] = 1080
        

    comun_file.DF_mini = pd.DataFrame(columns=['mini_01','mini_02','mini_03','mini_04','mini_05','mouse_final'])
    comun_file.DF_pov = pd.DataFrame(columns=['pov_01','pov_02','pov_03','pov_04','pov_05','mouse_final'])
    
    try:
        monitor , opcion_elegida = interfaz_seleccion_ventana.interfaz_selccion_ventana()
        comun_file.cod_window = monitor
    except IndexError:
        print(" 😡 Abra desde Steam Call of Duty® para poder empezar 😡")
        print(" 🥸 Corre el Juego en 1920x1080 🥸 ")
        print(" 🥸 Corre el Juego en Ventana (P.Completa) 🥸 ")
        print(" 🥸 Tener Juego en la pantalla de la derecha 🥸 ")
        print(" 🤖 El programa no para que correr hasta que des a la q en las ventanas emergentes 🤖 ")

    if opcion_elegida == 0:
        ineterfaz = interfaz_grabacion.interfaz_grabacion               #Otro hilo para la interfaz
        funcion_elegida = bucle_capturadora_grabacion
        funcion_elegida()
    else : 
        ineterfaz = interfaz_autonomo.interfaz_autonomo                  #Otro hilo para la interfaz
        funcion_elegida = bucle_capturadora_autonoma
        imagen_thread = threading.Thread(target=funcion_elegida)        #Un hilo para la capturadora
        imagen_thread.daemon = True 
        imagen_thread.start()
        ineterfaz()