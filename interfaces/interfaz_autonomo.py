import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk ,ImageGrab
import pygetwindow as gw
import queue

from comun_file import  *

# Globales Interfaz
root = None
listbox = None
scrollbar = None
frame02 = None
frame03 = None
boton = None
label_texto = None
frame04 = None
boton02 = None
etiqueta_estado = None
progreso = None
listbox = None
scrollbar = None

texto_label_contador = None
cuenta_atras_label = None

anterior_movimiento_registrado = None

def iniciar_cuenta_atras(segundos):
    global texto_label_contador
    global cuenta_atras_label

    if segundos > 0:
        minutos, segundos_restantes = divmod(segundos, 60)
        cuenta_atras_label.config(text=f"{minutos:02}:{segundos_restantes:02}")
        root.after(1000, iniciar_cuenta_atras, segundos - 1)
    else:
        cuenta_atras_label.config(text="¡Grabando!")
        texto_label_contador.pack_forget()
        cuenta_atras_label.pack_forget()

def mostrar_imagenes_01(lista,frame,size):
    # Limpiar el frame antes de agregar nuevas imágenes
    for widget in frame.winfo_children():
        widget.destroy()

    referencias_imagenes = []  # Lista para mantener referencias de las imágenes
    for i in range(len(lista)):
        img_pil = Image.fromarray(lista[i])  # Convertir numpy array a PIL Image
        img_resized = img_pil.resize(size, Image.BICUBIC)  # Redimensionar la imagen
        img_tk = ImageTk.PhotoImage(img_resized)  # Convertir a PhotoImage
        referencias_imagenes.append(img_tk)  # Mantener una referencia a la imagen
        label = tk.Label(frame, image=img_tk)
        label.pack(side="left", padx=10)
    
    # Asignar referencias de imagen al frame para evitar recolección de basura
    frame.image_refs = referencias_imagenes

def pulsar_boton(bool):
    if bool == False:
        boton.config(bg="blue")
        boton.config(text="🤖 Automatico 🤖")
    else:
        boton.config(bg="red")
        boton.config(text="🤖 Manual 🤖")

def finalizar():
    get_Finalizacion = True
    # Deshabilitar el botón mientras se realiza el proceso
    boton02.config(state=tk.DISABLED)
    boton.config(state=tk.DISABLED)

    etiqueta_estado.pack()      # Mostrar la etiqueta de estado
    progreso.pack()
    
    progreso.start(50)  # Iniciar la barra de progreso con un intervalo de actualización de 50 ms
    etiqueta_estado.config(text="Re-Entrenando el modelo")   # Actualizar el texto de la etiqueta
    
    # Simular un proceso largo (ejemplo: esperar 5 segundos)
    root.after(5000, proceso_finalizado)  # Llamar a la función proceso_finalizado después de 5 segundos

# Función llamada cuando el proceso finaliza
def proceso_finalizado():
    
    progreso.stop()     # Detener la barra de progreso 
    etiqueta_estado.config(text="Proceso finalizado")   # Actualizar el texto de la etiqueta
    root.destroy()      # Cerrar la ventana principal

def actualizar_texto():
    texto_actualizado = "Texto actualizado"
    label_texto.config(text=texto_actualizado)


def check_queue():
    global cola_imagenes_map
    global cola_imagenes_pov
    global root
    global anterior_movimiento_registrado

    try:
        # Obtener una lista de imágenes de la cola y movimientos
        lista_imagenes_map = cola_imagenes_map.get_nowait()
        lista_imagenes_pov = cola_imagenes_pov.get_nowait()
        mov_raton = cola_mov_raton.get_nowait()

        #Para que guarde la primera posicion registrada
        if mov_raton == None:
            anterior_movimiento_registrado = mov_raton
            #Comprobamos si el usuario paso a manual y cambiamos el letrero
        elif mov_raton != anterior_movimiento_registrado:
            anterior_movimiento_registrado = mov_raton
            pulsar_boton(True)
        elif mov_raton == anterior_movimiento_registrado:
            pulsar_boton(False)            

     
        mostrar_imagenes_01(lista_imagenes_map,frame,(150,110))
        mostrar_imagenes_01(lista_imagenes_pov,frame02,(260,150))
    except queue.Empty:
        pass
    # Volver a comprobar la cola después de un corto intervalo
    root.after(1, check_queue)

def interfaz_autonomo():
    global root
    global frame
    global frame02
    global frame03
    global boton
    global label_texto
    global frame04
    global boton02
    global etiqueta_estado
    global progreso
    global texto_label_contador
    global cuenta_atras_label

    # Crear la ventana principal
    root = tk.Tk()
    root.title("Roberick")

    # Crear la etiqueta para el texto "Quedan:"
    texto_label_contador = tk.Label(root, text="Empiece ya a jugar:", font=("Arial", 48))
    texto_label_contador.pack(pady=20)

    # Crear la etiqueta para mostrar la cuenta atrás
    cuenta_atras_label = tk.Label(root, text="00:05", font=("Arial", 48))
    cuenta_atras_label.pack(pady=20)

    # Crear un fila con imagenes mini_mapa y list_box 
    frame = tk.Frame(root)
    frame.pack(pady=20)

    # Crear un fila con imagenes pov
    frame02 = tk.Frame(root)
    frame02.pack(pady=20)

    # Crear un fila con Estado  
    frame03 = tk.Frame(root)
    frame03.pack(pady=20)
    
    boton = tk.Button(frame03, text="" , font=("Arial", 16) ,width=120, height=7, bg="white" ,fg="white")
    boton.pack()

    # Label de Texto
    label_texto = tk.Label(frame03, text="0 Elementos Para Re-entrenar el modelos", font=("Arial", 14))
    label_texto.pack(side=tk.LEFT)

    # Crear un marco Finalizado  
    frame04 = tk.Frame(root)
    frame04.pack(pady=20)
    
    boton02 = tk.Button(frame04, text="Finalizar", command=finalizar , font=("Arial", 16) ,width=120, height=7, bg="grey", fg="white")
    boton02.pack()

    # Etiqueta para mostrar el estado del proceso 
    etiqueta_estado = tk.Label(root, text="", font=("Arial", 14))

    # Barra de progreso  
    progreso = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=200, mode='indeterminate')

    # Iniciar la cuenta atrás de 5 segundos al iniciar la aplicación
    root.after(1000, iniciar_cuenta_atras, 5)

    # Iniciar la comprobación de la cola
    check_queue()   #Tenemos que comprobar la cola de images constantemente
    root.mainloop()
    
