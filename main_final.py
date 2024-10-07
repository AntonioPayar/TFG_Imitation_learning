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
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 


modelo_mapa = "modelos/modelos_entrenados/modelo_todo_0.68_.h5"

"""
    Funcion encargada de ejecutar el bucle de grabacion

"""

def bucle_capturadora_grabacion():
    global sqlite_db

    #Comprobamos si existen las carpetas
    if not os.path.exists('datos/grabacion/pov') and not os.path.exists('datos/grabacion/mini_mapa'):
        os.makedirs('datos/grabacion/pov')
        os.makedirs('datos/grabacion/mini_mapa')
        print("Carpetas creada ...")     

    #Esperamos 5 segundos hasta que el usuario se prepara
    time.sleep(5)

    teclas_direccion = threading.Thread(target=comun_file.teclas_direccion_movimiento_pantalla)
    
    if comun_file.move_check.get() == False:
        print("Move OFF")
        #Iniciar hilo para mantener las teclas presionadas
        comun_file.key_thread.start()

    if comun_file.sprint_check.get() == False:
        print("Sprint OFF")
        #Hilo que hace el movimiento de pantalla con las teclas de direccion
        teclas_direccion.start()
    
    try :
        capturadora = capturadora_grabacion_V2.CapturadoraGrabacion(comun_file.cod_window,"datos/grabacion/base_datos_cod.db")
        #Bucle hasta que la interfaz grafica da la orden de finalizacion
        while comun_file.get_Finalizacion == False:
            capturadora.run()
            #capturadora.vaciar_memoria()
        
        if comun_file.sprint_check.get() == False:
            #Finalizamos el proceso de las teclas
            teclas_direccion.join()
        
        if comun_file.move_check.get() == False:
            #Finalizamos el proceso del sprint
            comun_file.key_thread.join()

    finally:
        if comun_file.sprint_check.get() == False:
            #Finalizamos el proceso de las teclas
            teclas_direccion.join()
        
        if comun_file.move_check.get() == False:
            #Finalizamos el proceso del sprint
            comun_file.key_thread.join()




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
    #Hilo que hace el movimiento de pantalla con las teclas de direccion
    teclas_direccion = threading.Thread(target=comun_file.teclas_direccion_movimiento_pantalla)
    #Iniciar hilo para mantener las teclas presionadas
    comun_file.key_thread.start()
    teclas_direccion.start()

    capturadora = capturadora_autonoma.CapturadoraAutonoma(comun_file.cod_window,csv_mini,csv_pov)
    #Bucle hasta que la interfaz grafica da la orden de finalizacion
    while comun_file.get_Finalizacion == False:
        capturadora.run()
        capturadora.vaciar_memoria()

    #Finalizamos el proceso
    teclas_direccion.join()


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


"""
    #Eliminamos las ultimas filas del csv para que no aparezca ruido del menu al finalizar
    if os.path.isfile(csv_mini) and os.path.isfile(csv_pov):

        # Eliminar filas duplicadas
        comun_file.DF_mini.drop_duplicates(inplace=True)
        comun_file.DF_pov.drop_duplicates(inplace=True)

        # Eliminar las últimas 5 filas
        comun_file.DF_mini = comun_file.DF_mini[:-5]
        comun_file.DF_pov = comun_file.DF_pov[:-5]

        #Guardamos el archivo sobrescribiendo el anterior
        comun_file.DF_mini.to_csv(csv_mini, mode='a', header=False, index=False)
        comun_file.DF_pov.to_csv(csv_pov, mode='a', header=False, index=False)
        print("Archivos guardados...")
"""