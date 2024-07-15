import time
import cv2
import numpy as np
from PIL import ImageGrab
from datetime import datetime
from pynput import keyboard
from collections import Counter
from capturadoras import capturadora_grabacion_V2

# Variable para controlar la finalización del bucle
finalizar = False
key_presses = []
capturadora = None

def on_press(key):
    global key_presses
    tecla = 2

    if key == keyboard.Key.left:
        tecla = 0
    elif key == keyboard.Key.right:
        tecla = 1
    
    key_presses.append(tecla)


def main():
    global finalizar, key_presses 

    # Limpiar key_presses para cada ciclo de main
    key_presses.clear()

    # Iniciar el listener del teclado
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    try:
        for i in range(5):
            # Tomar una foto de la pantalla
            screen = ImageGrab.grab()

            # Esperar 0.1 segundos antes de la siguiente foto
            time.sleep(0.1)

        
        print("----------------")
        if len(key_presses) == 0:
            print("[0,2,0]")


        counts = Counter(key_presses)

        if len(counts.items()) == 1 : 
            for number, count in counts.items():
                print("["+str(count)+","+str(number)+",0]")

    except KeyboardInterrupt:
        print("Deteniendo el script...")
        finalizar = True

    finally:
        listener.stop()  # Asegurar que el listener del teclado se detenga



if __name__ == "__main__":
    csv_mini = 'datos/grabacion/datos_bo3_minimapa_03.csv'
    csv_pov = 'datos/grabacion/datos_bo3_pov_03.csv'
    cod_window = "1"
    capturadora = capturadora_grabacion_V2.CapturadoraGrabacion(cod_window,csv_mini,csv_pov)
    
    while not finalizar:
        main()
