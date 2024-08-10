import tkinter as tk
from tkinter import ttk
from PIL import ImageGrab , Image, ImageTk 
import queue
from Xlib import X, display
from Xlib.ext import xtest
import threading
import time
from datetime import datetime
import subprocess
from pynput import keyboard
import tkinter as tk

# Globales Ventana
cod_window = None
DF_mini = None
DF_pov = None

# Variable que almacenará el estado del Checkbutton
sprint_check = None
move_check = None
mapa_check = None

# Variable para control cerrar ventana
get_Finalizacion = False

# Cola para comunicación entre hilos
cola_imagenes_map = queue.Queue()
cola_imagenes_pov = queue.Queue()
cola_mov_raton = queue.Queue()  #Grabacion

# Evento para terminar hilo de presion letra (w)
stop_event = threading.Event()

#Intervalo de tiempo entre captura de imagenes
intervalo_captura = None
resolucion_pantalla = [None,None]

teclas_movimiento = 2
num_pulsaciones_01 = 0
num_pulsaciones_00 = 0

# Función para presionar teclas 'W' y 'Shift_L' usando Xlib
def press_keys_xlib():
    # Conectar al servidor X
    d = display.Display()
    root = d.screen().root

    # Obtener el código de tecla para 'W'
    keycode_w = d.keysym_to_keycode(ord('W'))  # 'W' may need to be uppercase

    # Código de tecla para Shift izquierda (Shift_L)
    keycode_shift_l = 50  # Este número puede variar según el layout del teclado

    try:
        while not stop_event.is_set():
            # Simular presión de teclas 'W' y 'Shift_L'
            xtest.fake_input(d, X.KeyPress, keycode_w)
            xtest.fake_input(d, X.KeyPress, keycode_shift_l)
            d.sync()
            time.sleep(0.1)  # Pequeño tiempo de espera para evitar uso excesivo de CPU

    finally:
        # Soltar las teclas 'W' y 'Shift_L' al interrumpir el script
        xtest.fake_input(d, X.KeyRelease, keycode_w)
        xtest.fake_input(d, X.KeyRelease, keycode_shift_l)
        d.sync()


class MovimientoTeclas():
        
    def move_mouse(self, x, y):
        subprocess.run(['xdotool', 'mousemove_relative', '--', str(x), str(y)])

    def on_press(self, key):
        global get_Finalizacion
        global key_thread , stop_event
        try:
            if key == keyboard.Key.up:
                pass
            elif key == keyboard.Key.down:
                subprocess.run(['xdotool', 'key', 'v']) 
            elif key == keyboard.Key.left:
                self.move_mouse(-500, 0)  # Mover a la izquierda
            elif key == keyboard.Key.right:
                self.move_mouse(500, 0)  # Mover a la derecha
            elif key.char == 'n' or key.char == 'f1':
                get_Finalizacion = True
                # Detener el hilo de presionar teclas
                stop_event.set()
                key_thread.join()
                print("Finalizando programa...")
                return False  # Esto detendrá el listener
        except AttributeError:
            pass

    def on_release(self, key):
        pass


def teclas_direccion_movimiento_pantalla():
    movimientos = MovimientoTeclas()
    # Start listening to the keyboard events
    with keyboard.Listener(on_press=movimientos.on_press, on_release=movimientos.on_release) as listener:
        listener.join()


#Hilo que presiona teclas (w+shift)
key_thread = threading.Thread(target=press_keys_xlib)
