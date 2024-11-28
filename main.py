from procesos import proceso_botones
from procesos import proceso_shift 
from procesos import proceso_eliminar_procesos
import subprocess
import time

"""
NORMAS 
SI QUIERES PARAR PRESIONA ESC VARIAS VECES
"""

if __name__ == '__main__':

    #Proceso encargado de cerrar procesos antes de empezar
    proceso4 = subprocess.Popen(["python3", "procesos/proceso_eliminar_procesos.py"])
    proceso4.wait()

    # Proceso Principal
    proceso3 = subprocess.Popen(["python3", "proceso_captura.py"])

    time.sleep(20)
    
    # Ejecutar procesos de teclas
    proceso1 = subprocess.Popen(["python3", "procesos/proceso_botones.py"])
    proceso2 = subprocess.Popen(["python3", "procesos/proceso_shift.py"])

    proceso1.wait()
    proceso2.terminate()
    proceso3.wait()
    print("Eso es todo amigos..")
