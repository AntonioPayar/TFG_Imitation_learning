import comun_file
from interfaces import interfaz_seleccion_ventana
from interfaces import interfaz_grabacion
from interfaces import interfaz_autonomo
from capturadoras import capturadora_autonoma , capturadora_grabacion

import pandas as pd
import os
import threading
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 


#Utilizar entorno
#source ../entorno_TFG/bin/activate

#---Reiniciar XServer
#sudo systemctl restart display-manager.service
#---Mostrar clientes XServer
#xlsclients
if __name__ == '__main__':

    comun_file.intervalo_captura = 0.2
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
        funcion_elegida = capturadora_grabacion.modo_grabacion_movimientos
    else : 
        ineterfaz = interfaz_autonomo.interfaz_autonomo                  #Otro hilo para la interfaz
        funcion_elegida = capturadora_autonoma.modo_autonomo_moviminetos

    imagen_thread = threading.Thread(target=funcion_elegida)        #Un hilo para la capturadora
    imagen_thread.daemon = True 
    imagen_thread.start()
    
    ineterfaz()     #Llamamos a la funcion

    # Si selecciona grabacion limpiamos los ultimos datos donde aparece el menu
    if opcion_elegida == 0 :
        #Eliminanos las ultimas 3 filas del csv para evitar ruido del menu
        csv_mini = 'datos/grabacion/datos_bo3_minimapa.csv'
        csv_pov = 'datos/grabacion/datos_bo3_pov.csv'
        if os.path.isfile(csv_mini) and os.path.isfile(csv_pov):
            # Eliminar las últimas 3 filas
            comun_file.DF_mini = comun_file.DF_mini[:-3]
            comun_file.DF_pov = comun_file.DF_pov[:-3]

            #Guardamos el archivo sobrescribiendo el anterior
            comun_file.DF_mini.to_csv(csv_mini, mode='a', header=False, index=False)
            comun_file.DF_pov.to_csv(csv_pov, mode='a', header=False, index=False)
            print("Archivos guardados...")