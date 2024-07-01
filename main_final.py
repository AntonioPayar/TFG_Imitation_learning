import comun_file
from interfaces import interfaz_seleccion_ventana
from interfaces import interfaz_grabacion
from interfaces import interfaz_autonomo
from capturadoras import capturadora_autonoma , capturadora_grabacion

import pandas as pd
import os
import threading
import time
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 


modelo_mapa = "modelos/modelo_mapa_1.0_.h5"
csv_mini = None
csv_pov = None


"""
    Funcion encargada de ejecutar el bucle de grabacion
"""
def bucle_capturadora_grabacion():
    global csv_mini , csv_pov

    csv_mini = 'datos/grabacion/datos_bo3_minimapa.csv'
    csv_pov = 'datos/grabacion/datos_bo3_pov.csv'
    #Esperamos 5 segundos hasta que el usuario se prepara
    time.sleep(5)
    #Iniciar hilo para mantener las teclas presionadas
    comun_file.key_thread.start()

    capturadora = capturadora_grabacion.CapturadoraGrabacion(comun_file.cod_window,csv_mini,csv_pov)
    #Bucle hasta que la interfaz grafica da la orden de finalizacion
    while comun_file.get_Finalizacion == False:
        capturadora.run()
        capturadora.vaciar_memoria()


"""
    Funcion encargada de ejecutar el bucle del modo autonomo
"""
def bucle_capturadora_autonoma():
    global csv_mini , csv_pov
    global modelo_mapa

    csv_mini = 'datos/fine_tuning/datos_bo3_minimapa.csv'
    csv_pov = 'datos/fine_tuning/datos_bo3_pov.csv'

    #capturadora_autonoma.configuracion_gpu_keras(modelo_mapa)
    #Esperamos 5 segundos hasta que el usuario se prepara
    time.sleep(5)
    #Iniciar hilo para mantener las teclas presionadas
    #comun_file.key_thread.start()

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
        funcion_elegida = bucle_capturadora_grabacion
    else : 
        ineterfaz = interfaz_autonomo.interfaz_autonomo                  #Otro hilo para la interfaz
        funcion_elegida = bucle_capturadora_autonoma

    imagen_thread = threading.Thread(target=funcion_elegida)        #Un hilo para la capturadora
    imagen_thread.daemon = True 
    imagen_thread.start()
    
    ineterfaz()     #Llamamos a la funcion


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