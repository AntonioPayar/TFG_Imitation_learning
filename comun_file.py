import tkinter as tk
from tkinter import ttk
import cv2
from pynput import mouse
import threading
from PIL import ImageGrab , Image, ImageTk 
import queue
from Xlib import X, display
from Xlib.ext import xtest
import threading
import time

# Globales Ventana
cod_window = None
DF_mini = None
DF_pov = None

# Variable para control cerrar ventana
get_Finalizacion = False

# Cola para comunicación entre hilos
cola_imagenes_map = queue.Queue()
cola_imagenes_pov = queue.Queue()
cola_mov_raton = queue.Queue()  #Grabacion

mouse_coords = {'x': None, 'y': None}
keys_pressed = set()
keys_number = 0

# Clase captura el movimineto del Raton instanciando un nuevo hilo
class MouseMoveDetector(threading.Thread):
    def __init__(self):
        super().__init__()
        self.running = True
        self.mouse_coords = {'x': None, 'y': None}
        self.keys_number = 0
        self.listener = mouse.Listener(on_move=self.on_move)

    def on_move(self, x, y):
        self.mouse_coords['x'] = x
        self.mouse_coords['y'] = y
        self.running = False
        self.listener.stop()  # Detener el listener

    def run(self):
        self.listener.start()
        while self.running:
            pass  # Mantener el hilo vivo mientras `self.running` sea True




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
        while True:
            # Simular presión de teclas 'W' y 'Shift_L'
            xtest.fake_input(d, X.KeyPress, keycode_w)
            xtest.fake_input(d, X.KeyPress, keycode_shift_l)
            d.sync()
            time.sleep(0.1)  # Pequeño tiempo de espera para evitar uso excesivo de CPU

    except KeyboardInterrupt:
        # Soltar las teclas 'W' y 'Shift_L' al interrumpir el script
        xtest.fake_input(d, X.KeyRelease, keycode_w)
        xtest.fake_input(d, X.KeyRelease, keycode_shift_l)
        d.sync()