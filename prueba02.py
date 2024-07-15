import threading
import time
from pynput import keyboard

num_pulsaciones_01 = 0
num_pulsaciones_0 = 0
tecla_direccion = 2
listener = None

def recargar_tecla() :
    global tecla_direccion
    global num_pulsaciones_01 , num_pulsaciones_0
    num_pulsaciones_01 = 0
    num_pulsaciones_0 = 0
    tecla_direccion = 2

def print_tecla():
    global tecla_direccion
    global num_pulsaciones_01 , num_pulsaciones_0

    if tecla_direccion == 1:
        print("Tecla "+str(tecla_direccion)+" pulsaciones "+str(num_pulsaciones_01))
    elif tecla_direccion == 0:
        print("Tecla "+str(tecla_direccion)+" pulsaciones "+str(num_pulsaciones_0))

def on_press(key):
    global tecla_direccion ,num_pulsaciones_01 , num_pulsaciones_0
    try:
        if key == keyboard.Key.up:
            tecla_direccion = 2
        elif key == keyboard.Key.down:
            tecla_direccion = 2
        elif key == keyboard.Key.left:
            tecla_direccion = 0
            num_pulsaciones_0 = num_pulsaciones_0 + 1
        elif key == keyboard.Key.right:
            tecla_direccion = 1
            num_pulsaciones_01 = num_pulsaciones_01 + 1
    except AttributeError:
        # Ignorar teclas que no son de dirección
        pass

def detectar_teclas():
    global listener
    # Crear un hilo para la detección de teclas
    def thread_func():
        with keyboard.Listener(on_press=on_press) as listener:
            # Esperar 1 segundo y luego detener el listener
            time.sleep(0.2)
            listener.stop()

    listener = threading.Thread(target=thread_func)
    listener.start()
    listener.join()



def run():
    global tecla_direccion
    while True:
        detectar_teclas()
        print_tecla()
        recargar_tecla()


if __name__ == "__main__":
    run()
