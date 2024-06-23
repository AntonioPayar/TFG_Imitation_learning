import tkinter as tk
from tkinter import ttk
import cv2
from pynput.mouse import Listener
import threading
from PIL import ImageGrab , Image, ImageTk 
import queue

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